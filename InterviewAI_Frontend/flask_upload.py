from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend
import os
import whisper


UPLOAD_FOLDER_RESUME = os.path.expanduser("~/Documents/Resume")  # Save files in the Documents/Resume folder
app.config['UPLOAD_FOLDER_RESUME'] = UPLOAD_FOLDER_RESUME

UPLOAD_FOLDER_AUDIO = os.path.expanduser("~/Documents/Audio")  # Save files in the Documents/Audio folder
app.config['UPLOAD_FOLDER_AUDIO'] = UPLOAD_FOLDER_AUDIO

os.makedirs(UPLOAD_FOLDER_RESUME, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_AUDIO, exist_ok=True)
model = whisper.load_model("small")
@app.route('/upload_resume', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER_RESUME'], file.filename)
    file.save(file_path)
    
    return jsonify({"message": f"File '{file.filename}' uploaded successfully!"}), 200

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], file.filename)
    file.save(file_path)

    # Transcribe audio using Whisper
    try:
        result = model.transcribe(file_path)
        transcription = result["text"]  
        # return jsonify({"message": "File uploaded and transcribed successfully!", "transcription": transcription}), 200
        transcription_path = os.path.join(app.config['UPLOAD_FOLDER_AUDIO'], file.filename + ".txt")
        with open(transcription_path, "w") as f:
            f.write(transcription)

        return jsonify({
            "message": "File uploaded and transcribed successfully!",
         "transcription": transcription,
            "transcription_file": transcription_path
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

