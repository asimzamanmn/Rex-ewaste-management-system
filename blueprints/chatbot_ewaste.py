from flask import Blueprint, render_template, request, jsonify
import ollama

# Define the blueprint
chatbot_ewaste_bp = Blueprint('chatbot_ewaste', __name__, template_folder='templates')

# Awareness chatbot homepage (optional)
@chatbot_ewaste_bp.route('/')
def home():
    return render_template('ewaste_chat.html')  # Create this template

# Chat endpoint
@chatbot_ewaste_bp.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')

    # Sending message to Ollama
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': (
                'You are an expert in e-waste management and sustainability. Provide responses in a clearly formatted '
                'point-wise list using HTML <ul> and <li> tags. Ensure each response includes numbered points and bold headings. '
                'Example: <li><strong>1. Recycling Process:</strong> E-waste should be taken to authorized recyclers...</li>.'
            )},
            {'role': 'user', 'content': user_message}
        ]
    )

    formatted_response = f"<ul>{response['message']['content']}</ul>"
    return jsonify({'content': formatted_response})
