from flask import Flask, render_template, request, jsonify
import os
from main import handle_query, update_knowledge_base

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods = ['POST'])
def chat():
    user_input = request.json.get('message')
    response = handle_query(user_input)
    return jsonify({'response': response})

@app.route('/upload', methods = ['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    file_type = file.filename.split('.')[-1]

    if file_type == 'pdf':
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        update_knowledge_base(file_path)
        return jsonify({'response': 'File processed and knowledge base updated successfully'})
    return jsonify({'error': 'Unsupported file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)