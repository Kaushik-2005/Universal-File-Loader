from flask import Flask, render_template, request, jsonify
from loader.pdf import PDFLoader
import os

app = Flask(__name__)


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')


# Route for handling normal chatbot conversations
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = handle_chat(user_input)  # Function from main.py
    return jsonify({'response': response})


# Route for handling file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    file_type = file.filename.split('.')[-1]

    # Process the file based on its type
    if file_type == 'pdf':
        # Save the file temporarily
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        # Initialize PDFLoader with the file path
        processor = PDFLoader(file_path)
        text = processor.extract_text()  # Make this synchronous for simplicity
        processor.process()  # Process the file and get vectors for the knowledge base
        response = update_knowledge_base(text)  # Update the knowledge base
        return jsonify({'response': 'File processed successfully'})
    # Uncomment below when CSVLoader is available
    # elif file_type == 'csv':
    #     processor = CSVLoader()

    return jsonify({'error': 'Unsupported file type'}), 400


if __name__ == '__main__':
    app.run(debug=True)
