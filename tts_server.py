from flask import Flask, request, jsonify
import edge_tts
import asyncio
import os
import uuid
import boto3

app = Flask(__name__)

# ---------- AWS S3 CONFIG ----------
BUCKET_NAME = "my-tts-audio-bucket-123"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client("s3", region_name=AWS_REGION)

# ---------- TTS ----------
async def generate_audio(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# ---------- HEALTH ----------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "Edge TTS Server"})

# ---------- GENERATE ----------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)

        text = data.get("text", "")
        voice = data.get("voice", "en-US-GuyNeural")
        video_number = data.get("video_number", "1")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Temp file (safe for cloud)
        file_name = f"audio_video_{video_number}_{uuid.uuid4()}.mp3"
        local_path = os.path.join("/tmp", file_name)

        # Generate audio
        asyncio.run(generate_audio(text, voice, local_path))

        # Upload to S3
        s3.upload_file(
            local_path,
            BUCKET_NAME,
            file_name,
            ExtraArgs={"ContentType": "audio/mpeg"}
        )

        # Public S3 URL (works if bucket/object is public)
        s3_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"

        return jsonify({
            "message": "Audio generated and uploaded",
            "s3_url": s3_url,
            "file_name": file_name
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- VOICES ----------
@app.route("/voices", methods=["GET"])
def list_voices():
    return jsonify({
        "voices": [
            "en-US-GuyNeural",
            "en-US-JennyNeural",
            "en-US-AriaNeural",
            "en-US-ChristopherNeural",
            "en-US-EricNeural"
        ]
    })

# ---------- START ----------
if __name__ == "__main__":
    print("🎤 Edge TTS Server Starting...")
    app.run(host="0.0.0.0", port=5000, debug=False)
