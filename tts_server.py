from flask import Flask, request, send_file, jsonify
import edge_tts
import asyncio
import os
import tempfile

app = Flask(__name__)

async def generate_audio(text, voice, output_file):
    """Generate audio using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

@app.route('/health', methods=['GET'])
def health():
    """Check if server is running"""
    return jsonify({"status": "ok", "service": "Edge TTS Server"})

@app.route('/generate', methods=['POST'])
def generate():
    """Generate audio from text"""
    try:
        data = request.json
        text = data.get('text', '')
        voice = data.get('voice', 'en-US-GuyNeural')
        video_number = data.get('video_number', '1')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Create file in same directory as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, f'audio_{video_number}.mp3')
        
        # Generate audio
        asyncio.run(generate_audio(text, voice, output_file))
        
        # Send file back
        return send_file(output_file, mimetype='audio/mpeg', as_attachment=True, download_name=f'audio_{video_number}.mp3')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/voices', methods=['GET'])
def list_voices():
    """List available voices"""
    voices = [
        "en-US-GuyNeural",
        "en-US-JennyNeural",
        "en-US-AriaNeural",
        "en-US-ChristopherNeural",
        "en-US-EricNeural"
    ]
    return jsonify({"voices": voices})

if __name__ == '__main__':
    print("🎤 Edge TTS Server Starting...")
    print("📡 Server will run on http://localhost:5000")
    print("✅ Ready to generate audio!")
    app.run(host='0.0.0.0', port=5000, debug=False)