from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from main import handle_query, update_knowledge_base

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
current_file_type = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global current_file_type
    if not current_file_type:
        return jsonify({'response': "No file uploaded. Please upload a file first."})

    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': "Please enter a valid question."})

    try:
        response = handle_query(user_input, current_file_type)
        if not response:
            return jsonify({'response': "Sorry, I couldn't find an answer to your question."})
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f"Error processing query: {str(e)}")
        return jsonify({'response': "An error occurred while processing your query. Please try again."}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_file_type

    try:
        if 'file' not in request.files:
            app.logger.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            app.logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        file_type = file.filename.split('.')[-1].lower()

        if file_type not in ['csv', 'pdf', 'xlsx', 'docx']:
            app.logger.error(f'Unsupported file type: {file_type}')
            return jsonify({'error': 'Unsupported file type'}), 400

        # Ensure the uploads directory exists
        upload_dir = os.path.join(app.root_path, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        current_file_type = file_type
        update_knowledge_base(file_path, file_type)
        return jsonify({'response': f'{file_type.upper()} file processed and knowledge base updated successfully.'})
    except Exception as e:
        app.logger.error(f'Error in upload_file: {str(e)}')
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)