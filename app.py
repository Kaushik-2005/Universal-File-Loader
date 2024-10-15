from flask import Flask, render_template, request, jsonify
import os
from main import handle_query, update_knowledge_base

app = Flask(__name__)
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

    if 'file' not in request.files:
        app.logger.error('No file provided')
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error('No file selected')
        return jsonify({'error': 'No file selected'}), 400

    file_type = file.filename.split('.')[-1].lower()

    if file_type not in ['csv', 'pdf', 'xlsx', 'docx']:
        app.logger.error(f'Unsupported file type: {file_type}')
        return jsonify({'error': 'Unsupported file type'}), 400

    # Ensure the uploads directory exists
    upload_dir = os.path.join(app.root_path, "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    try:
        file.save(file_path)
    except Exception as e:
        app.logger.error(f'File upload failed: {str(e)}')
        return jsonify({'error': f'File upload failed: {str(e)}'}), 500

    try:
        current_file_type = file_type
        update_knowledge_base(file_path, file_type)
        return jsonify({'response': f'{file_type.upper()} file processed and knowledge base updated successfully.'})
    except Exception as e:
        app.logger.error(f'Error updating knowledge base: {str(e)}')
        return jsonify({'error': f'Error updating knowledge base: {str(e)}'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error('Server Error: %s', (error))
    return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)