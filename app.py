from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os
import uuid
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from dotenv import load_dotenv
import google.generativeai as genai
#Apply rate limiting here. I have missed it....

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Create model
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)
CORS(app)

def query_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini Error:", e)
        return "Sorry, I couldn't generate a reply."

@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files['audio']
    filename = f"temp_{uuid.uuid4()}.mp3"
    audio_file.save(filename)
    print("Succes loaded audio file")

    try:
        audio = AudioSegment.from_file(filename)
        wav_filename = f"temp_{uuid.uuid4()}.wav"
        audio.export(wav_filename, format="wav")
        print("converted to wav")
    except Exception as e:
        return jsonify({"error": "Audio conversion failed", "details": str(e)}), 400

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_filename) as source:
        audio_data = recognizer.record(source)
        print(audio_data)

    try:
        user_text = recognizer.recognize_google(audio_data)
        print("user text")
        print(user_text)
    except sr.UnknownValueError:
        return jsonify({"error": "Speech not recognized"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech service unavailable"}), 400
    finally:
        os.remove(filename)
        os.remove(wav_filename)

    # Get response from Gemini
    reply = query_gemini(user_text)
    print("reply_from_model:")
    print(reply)

    # Text-to-speech
    tts_audio = gTTS(text=reply, lang="en")
    reply_filename = f"response_{uuid.uuid4()}.mp3"
    tts_audio.save(reply_filename)

    return send_file(reply_filename, mimetype="audio/mpeg", as_attachment=True, download_name="response.mp3")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
