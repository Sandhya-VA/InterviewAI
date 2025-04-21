from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import whisper
import subprocess
import pdfplumber
import spacy
import json
import re
import tempfile

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Load Whisper large model
whisper_model = whisper.load_model("medium")

# Load custom NER model
NER_MODEL_PATH = "/Users/sandhyavenkataramaiah/Resume_Parsing/ner_model"
try:
    ner_model = spacy.load(NER_MODEL_PATH)
    print("NER model loaded successfully.")
except Exception as e:
    print(f"Failed to load NER model: {e}")
    ner_model = None

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not ner_model:
        return jsonify({"error": "NER model not loaded"}), 500

    try:
        with pdfplumber.open(file.stream) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500

    doc = ner_model(text)
    raw_skills = list(set(ent.text.strip() for ent in doc.ents if ent.label_.lower() == "skill"))

    prompt = f"""
You are a highly accurate technical skills extraction engine.

Your task is to extract only valid, specific technical skills from the list below:
{raw_skills}

Include only the following categories:
- Programming languages (e.g., Python, JavaScript)
- Frameworks and libraries (e.g., React, Django, NumPy)
- Databases (e.g., MySQL, MongoDB, PostgreSQL)
- DevOps and CI/CD tools (e.g., Docker, Jenkins, GitHub Actions)
- Cloud platforms and services (e.g., AWS, Azure, GCP, Firebase)
- Data technologies (e.g., Hadoop, Spark, Pandas, Kafka)
- Testing tools (e.g., Jest, Cypress, Selenium)
- Frontend/Backend technologies (e.g., REST API, GraphQL, TypeScript)
- ML/NLP libraries (e.g., TensorFlow, PyTorch, spaCy)

Strictly exclude:
- Soft skills (e.g., communication, leadership)
- Job roles or domains (e.g., software engineer, web development)
- Vague or generic terms (e.g., database, system design, web app)
- Business terms (e.g., KPIs, OKRs, management, BI)

Be thorough. Do not miss any valid technical skills.
Remove duplicates and keep the formatting clean.

Return the result as a JSON array of strings, like:
["React", "Node.js", "MongoDB", "AWS", "Docker"]
"""

    try:
        result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True, timeout=60)
        output = result.stdout.strip()

        # Safely extract JSON array from model output
        match = re.search(r"\[.*?\]", output, re.DOTALL)
        if not match:
            return jsonify({"error": "Failed to extract JSON array from model response", "raw_output": output}), 500

        try:
            parsed_skills = json.loads(match.group())
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Skill JSON parsing failed: {str(e)}", "raw_output": output}), 500

        # Filter out blacklisted or invalid items
        blacklist = {
    "software", "database", "web app", "scalability", "design", "architecture", "business intelligence",
    "data analysis", "team work", "communication", "collaboration", "leadership", "ui", "ux",
    "responsive", "frontend", "backend", "application", "development", "system", "integration",
    "debugging", "testing", "optimization", "performance", "management", "agile", "scrum",
    "devops"  # (only remove if listed generically, not as a tool like "DevOps Tools: Jenkins")
        }

        filtered_skills = list(dict.fromkeys(
            skill for skill in parsed_skills if skill in raw_skills and skill not in blacklist
        ))

    except Exception as e:
        return jsonify({"error": f"Skill filtering failed: {str(e)}"}), 500

    # Question generation
    questions = {}
    for skill in filtered_skills:
        q_prompt = f"""
You are a senior technical interviewer.

Generate exactly 5 concise and diverse technical interview questions for the skill: {skill}.

Guidelines:
- Ask clear, practical questions that test core understanding and application
- Mix difficulty levels: easy, moderate, and hard
- Focus on concepts, use cases, best practices, and common pitfalls
- Do NOT ask the candidate to write code or implement programs
- Do NOT include explanations, commentary, or answers

Return only a valid JSON array of the 5 questions.

"""
        try:
            result = subprocess.run(["ollama", "run", "mistral", q_prompt], capture_output=True, text=True, timeout=60)
            output = result.stdout.strip()
            match = re.search(r"\[.*?\]", output, re.DOTALL)
            questions[skill] = json.loads(match.group()) if match else [output]
        except Exception as e:
            questions[skill] = [f"Error generating questions: {str(e)}"]

    return jsonify({"skills": filtered_skills, "questions": questions}), 200


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    print(f"📥 Received file: {file.filename}, type: {file.content_type}")

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save input audio as temp .webm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
            file.save(temp_input.name)
            input_path = temp_input.name

        # ✅ Reject very short/silent files
        if os.path.getsize(input_path) < 2048:
            os.unlink(input_path)
            return jsonify({"error": "Audio file too short or silent"}), 400

        # Convert to mono WAV
        processed_path = input_path.replace(".webm", "_mono.wav")
        ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_path, "-ac", "1", processed_path]
        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        # Transcribe
        result = whisper_model.transcribe(processed_path)
        transcription = result.get("text", "").strip()

        # Cleanup temp files
        os.unlink(input_path)
        os.unlink(processed_path)

        if not transcription:
            return jsonify({"error": "No transcription generated (empty audio?)"}), 400

        return jsonify({
            "message": "Transcription successful",
            "transcription": transcription
        }), 200

    except subprocess.CalledProcessError as ffmpeg_err:
        return jsonify({"error": f"FFmpeg conversion failed: {str(ffmpeg_err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route('/evaluate_answers', methods=['POST'])
def evaluate_answers():
    data = request.get_json()
    responses = data.get("responses", [])
    if not responses:
        return jsonify({"error": "No responses provided."}), 400

    evaluations = []
    score_sum = 0

    for item in responses:
        question = item["question"]
        answer = item["answer"]

        prompt = f"""
You are a strict technical interviewer.

Evaluate the candidate's answer below based on:
- Technical correctness
- Depth of explanation
- Relevance to the question
- Use of terminology and examples

Question: {question}
Answer: {answer}

Respond in strict JSON format only:
{{
  "score": <score out of 10>,
  "feedback": "<clear, constructive, technical feedback>"
}}

🟡 Feedback should explain what was missing, what was correct, and how the answer could be improved.
"""

        try:
            result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True, timeout=60)
            raw_output = result.stdout.strip()

            try:
                eval_result = json.loads(raw_output)
            except json.JSONDecodeError:
                eval_result = {"score": 0, "feedback": "Invalid JSON from model."}

            score = eval_result.get("score", 0)
            if isinstance(score, str):
                try:
                    score = int(score)
                except ValueError:
                    score = 0

            score_sum += score
            evaluations.append({
                "question": question,
                "answer": answer,
                "score": score,
                "feedback": eval_result.get("feedback", "No feedback available.")
            })

        except Exception as e:
            evaluations.append({
                "question": question,
                "answer": answer,
                "score": 0,
                "feedback": f"Error: {str(e)}"
            })

    overall_score = round(score_sum / len(evaluations), 2) if evaluations else 0

    # 👇 Summarize feedback in one final model call
    feedback_prompt = "You are a senior technical interviewer. Based on the evaluations, summarize the candidate's overall technical performance in 2-3 sentences.\n\n"
    for e in evaluations:
        feedback_prompt += f"Q: {e['question']}\nA: {e['answer']}\nScore: {e['score']}/10\nFeedback: {e['feedback']}\n\n"
    feedback_prompt += """
Write a summary that:
- Highlights technical strengths and weaknesses
- Mentions any repeated mistakes or patterns
- Suggests areas for improvement
"""

    try:
        result = subprocess.run(["ollama", "run", "mistral", feedback_prompt], capture_output=True, text=True, timeout=60)
        overall_feedback = result.stdout.strip()
    except Exception as e:
        overall_feedback = f"Failed to generate summary: {str(e)}"

    return jsonify({
        "evaluations": evaluations,
        "overall_score": overall_score,
        "overall_feedback": overall_feedback
    }), 200


if __name__ == '__main__':
    app.run(debug=True)