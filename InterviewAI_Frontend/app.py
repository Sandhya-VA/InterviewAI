from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import whisper
import subprocess
import pdfplumber
import spacy
import json
import re
import tempfile
import chromadb
from chromadb.utils import embedding_functions

app = Flask(__name__)
CORS(app, supports_credentials=True)

whisper_model = whisper.load_model("medium")

# NER_MODEL_PATH set via .env — no hardcoded local paths
NER_MODEL_PATH = os.environ.get("NER_MODEL_PATH", "./ner_model")
try:
    ner_model = spacy.load(NER_MODEL_PATH)
    print(f"NER model loaded from {NER_MODEL_PATH}")
except Exception as e:
    print(f"Failed to load NER model: {e}")
    ner_model = None

# ChromaDB with sentence-transformers embedding function for real RAG.
# Each Q&A exchange is embedded as a vector. On retrieval, we do
# semantic similarity search — so the model gets the most relevant
# past context, not just a raw dump of everything said.
chroma_client = chromadb.Client()
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_session_collection(session_id: str):
    """Get or create a ChromaDB collection for this session."""
    return chroma_client.get_or_create_collection(
        name=f"session_{session_id}",
        embedding_function=embedding_fn
    )

def store_exchange(session_id: str, question: str, answer: str, score: int):
    """Embed and store a Q&A exchange in the session vector store."""
    collection = get_session_collection(session_id)
    collection.add(
        documents=[f"Q: {question}\nA: {answer}"],
        metadatas=[{"score": score, "question": question}],
        ids=[str(uuid.uuid4())]
    )

def retrieve_relevant_context(session_id: str, query: str, n_results: int = 3) -> str:
    """
    RAG retrieval: embed the query and return the top-k most semantically
    similar past exchanges from this session. This is what makes it RAG —
    we're not just fetching everything, we're finding the most relevant
    prior context based on vector similarity.
    """
    try:
        collection = get_session_collection(session_id)
        count = collection.count()
        if count == 0:
            return ""
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs)
    except Exception:
        return ""


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
            text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500

    doc = ner_model(text)
    raw_skills = list(set(ent.text.strip() for ent in doc.ents if ent.label_.lower() == "skill"))

    prompt = f"""You are a technical skills extraction engine. Extract only valid technical skills from:
{raw_skills}

Include: programming languages, frameworks, databases, DevOps tools, cloud platforms, ML/NLP libraries.
Exclude: soft skills, job roles, vague terms, business terms.

Return a JSON array only: ["React", "Node.js", "AWS"]"""

    try:
        result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True, timeout=60)
        output = result.stdout.strip()
        match = re.search(r"\[.*?\]", output, re.DOTALL)
        if not match:
            return jsonify({"error": "No JSON in model response", "raw": output}), 500
        parsed_skills = json.loads(match.group())

        blacklist = {
            "software", "database", "web app", "scalability", "design", "architecture",
            "data analysis", "communication", "collaboration", "leadership", "ui", "ux",
            "application", "development", "system", "debugging", "testing", "management",
            "agile", "scrum", "frontend", "backend"
        }
        filtered_skills = list(dict.fromkeys(
            s for s in parsed_skills if s in raw_skills and s not in blacklist
        ))
    except Exception as e:
        return jsonify({"error": f"Skill extraction failed: {str(e)}"}), 500

    questions = {}
    for skill in filtered_skills:
        q_prompt = f"""You are a senior technical interviewer.
Generate exactly 5 interview questions for: {skill}
Mix difficulty levels. No code questions. No explanations.
Return a JSON array only."""
        try:
            result = subprocess.run(["ollama", "run", "mistral", q_prompt], capture_output=True, text=True, timeout=60)
            match = re.search(r"\[.*?\]", result.stdout.strip(), re.DOTALL)
            questions[skill] = json.loads(match.group()) if match else [result.stdout.strip()]
        except Exception as e:
            questions[skill] = [f"Error: {str(e)}"]

    session_id = str(uuid.uuid4())
    return jsonify({"skills": filtered_skills, "questions": questions, "session_id": session_id}), 200


@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            file.save(tmp.name)
            input_path = tmp.name

        if os.path.getsize(input_path) < 2048:
            os.unlink(input_path)
            return jsonify({"error": "Audio too short or silent"}), 400

        processed_path = input_path.replace(".webm", "_mono.wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, "-ac", "1", processed_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )

        result = whisper_model.transcribe(processed_path)
        transcription = result.get("text", "").strip()

        os.unlink(input_path)
        os.unlink(processed_path)

        if not transcription:
            return jsonify({"error": "Empty transcription"}), 400

        return jsonify({"transcription": transcription}), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"FFmpeg failed: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@app.route('/evaluate_answers', methods=['POST'])
def evaluate_answers():
    data = request.get_json()
    responses = data.get("responses", [])
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not responses:
        return jsonify({"error": "No responses provided."}), 400

    evaluations = []
    score_sum = 0

    for item in responses:
        question = item["question"]
        answer = item["answer"]

        # RAG: retrieve the most relevant past exchanges before evaluating
        # this answer — gives the model context about how the candidate
        # has been performing on related topics earlier in the session
        relevant_context = retrieve_relevant_context(
            session_id,
            query=question,
            n_results=3
        )

        context_block = ""
        if relevant_context:
            context_block = f"\nRelevant prior answers from this session:\n{relevant_context}\n"

        prompt = f"""You are a strict technical interviewer.{context_block}
Evaluate this answer on: technical correctness, depth, relevance, terminology.

Question: {question}
Answer: {answer}

Respond in JSON only:
{{"score": <0-10>, "feedback": "<constructive feedback>"}}"""

        try:
            result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True, timeout=60)
            try:
                eval_result = json.loads(result.stdout.strip())
            except json.JSONDecodeError:
                eval_result = {"score": 0, "feedback": "Could not parse response."}

            score = eval_result.get("score", 0)
            if isinstance(score, str):
                try:
                    score = int(score)
                except ValueError:
                    score = 0

            score_sum += score

            # Store this exchange as a vector in ChromaDB
            store_exchange(session_id, question, answer, score)

            evaluations.append({
                "question": question,
                "answer": answer,
                "score": score,
                "feedback": eval_result.get("feedback", "No feedback.")
            })
        except Exception as e:
            evaluations.append({"question": question, "answer": answer, "score": 0, "feedback": str(e)})

    overall_score = round(score_sum / len(evaluations), 2) if evaluations else 0

    # RAG retrieval for the final summary: query with a broad prompt
    # so we pull the most representative exchanges from the session
    summary_context = retrieve_relevant_context(
        session_id,
        query="technical skills performance strengths weaknesses",
        n_results=5
    )

    summary_prompt = f"""You are a senior technical interviewer.
Based on the candidate's interview session:

{summary_context}

Write a 2-3 sentence summary of their overall technical performance.
Highlight strengths, weaknesses, and specific areas to improve."""

    try:
        result = subprocess.run(["ollama", "run", "mistral", summary_prompt], capture_output=True, text=True, timeout=60)
        overall_feedback = result.stdout.strip()
    except Exception as e:
        overall_feedback = f"Summary failed: {str(e)}"

    return jsonify({
        "evaluations": evaluations,
        "overall_score": overall_score,
        "overall_feedback": overall_feedback,
        "session_id": session_id
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
