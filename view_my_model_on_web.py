from flask import Flask, render_template, request, jsonify, send_from_directory
import subprocess
import json
import os
import sys

app = Flask(__name__, template_folder='.')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['prompt']
        # Run the character pipeline script
        result = subprocess.run(
            [sys.executable, 'character_pipeline_viewer.py', prompt],
            capture_output=True, text=True
        )
        # Read the generated character JSON to get the export path
        with open('generated_characters/character1.json') as f:
            data = json.load(f)
        export_path = data.get('export_path')
        if not export_path:
            return "Error: No export path found", 500
        base_name = os.path.splitext(os.path.basename(export_path))[0]
        # Render the viewer with the new model name
        return render_template('viewer.html', model_base=base_name)
    # Default: show viewer (with or without a model)
    return render_template('viewer.html', model_base=None)

@app.route('/list_textures')
def list_textures():
    texture_dir = 'textures'  
    try:
        files = os.listdir(texture_dir)
        #  filter for image files only:
        files = [f for f in files if os.path.isfile(os.path.join(texture_dir, f))]
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(debug=True)
    