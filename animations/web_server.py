#!/usr/bin/env python3
"""
HUGMAN Web Server - Updated with real-time file monitoring
"""

from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import sys
import time
import glob
import threading
from pathlib import Path

app = Flask(__name__)

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ACTION_GLB_PATH = os.path.join(SCRIPT_DIR, 'action.glb')
CHARACTER_PIPELINE = "character_pipeline_viewer.py"

# Track file generation status
file_generation_in_progress = False
last_generation_time = 0

def file_is_ready(path):
    """Check if file exists and is fully written"""
    try:
        if not os.path.exists(path):
            return False
        
        # Check file size stability
        size1 = os.path.getsize(path)
        time.sleep(0.1)
        size2 = os.path.getsize(path)
        
        return size1 > 1024 and size1 == size2  # At least 1KB and stable
    except:
        return False

def generate_character_task(prompt):
    """Background task for character generation"""
    global file_generation_in_progress, last_generation_time
    
    try:
        file_generation_in_progress = True
        last_generation_time = time.time()
        
        # Remove existing file
        if os.path.exists(ACTION_GLB_PATH):
            os.remove(ACTION_GLB_PATH)
        
        # Run generation
        subprocess.run(
            [sys.executable, CHARACTER_PIPELINE, prompt],
            check=True
        )
        
        # Wait for file to stabilize
        max_wait = 30
        start_time = time.time()
        
        while not file_is_ready(ACTION_GLB_PATH):
            if time.time() - start_time > max_wait:
                raise TimeoutError("File didn't stabilize in time")
            time.sleep(0.5)
            
    finally:
        file_generation_in_progress = False

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory(SCRIPT_DIR, 'animation_viewer.html')

@app.route('/generate-character', methods=['POST'])
def generate_character_endpoint():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_character_task,
            args=(prompt,)
        )
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Generation started"
        })
        
    except Exception as e:
        return jsonify({"error": f"Error starting generation: {str(e)}"}), 500

@app.route('/check-file-update', methods=['GET'])
def check_file_update():
    """Check file status with more detailed info"""
    try:
        exists = os.path.exists(ACTION_GLB_PATH)
        file_time = os.path.getmtime(ACTION_GLB_PATH) if exists else 0
        file_size = os.path.getsize(ACTION_GLB_PATH) if exists else 0
        
        return jsonify({
            "exists": exists,
            "fileTime": file_time,
            "fileSize": file_size,
            "generationInProgress": file_generation_in_progress,
            "lastGenerationTime": last_generation_time
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check-file-exists', methods=['GET'])
def check_file_exists():
    """Check if action.glb file exists"""
    try:
        exists = os.path.exists(ACTION_GLB_PATH)
        print(f"File exists check: action.glb exists = {exists}")
        return jsonify({"exists": exists})
    except Exception as e:
        print(f"File exists check error: {str(e)}")
        return jsonify({"error": f"Error checking file existence: {str(e)}"}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (GLB files, etc.)"""
    return send_from_directory(SCRIPT_DIR, filename)

if __name__ == '__main__':
    print("=" * 50)
    print("HUGMAN Character Generation System")
    print("=" * 50)
    
    # Check if running as command line tool
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        generate_character_task(prompt)
        sys.exit(0)
    
    print("\nStarting HUGMAN web server...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    # Open browser automatically after a short delay
    def open_browser():
        time.sleep(2)
        import webbrowser
        webbrowser.open('http://localhost:5001')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)