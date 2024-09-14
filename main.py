from flask import Flask, request, render_template
from groq import Groq
import os
from PIL import Image
import io

app = Flask(__name__)

# Initialize Groq API client
client = Groq(
    api_key='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',
)

recent_chats = []  # Store recent chat topics and responses

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    facts = None
    topic = None
    error = None

    if request.method == 'POST':
        if 'topic' in request.form:
            topic = request.form.get('topic')  # Get the user input for topic

            if topic:
                try:
                    # Define the role-based system prompt
                    role_prompt = (
                        "You are a human assistant. 'Who developed you?' The answer is Sugash K. "
                        f"Here is the user's query: {topic}"
                    )

                    # Generate text using the Groq API
                    chat_completion = client.chat.completions.create(
                        messages=[{
                            "role": "user",
                            "content": role_prompt,
                        }],
                        model="llava-v1.5-7b-4096-preview",  # Use the updated LLaVA model
                    )

                    # Extract the generated text from the response
                    generated_text = chat_completion.choices[0].message.content

                    # Save the chat topic and response
                    facts = generated_text
                    recent_chats.append({'topic': topic, 'facts': facts})

                except Exception as e:
                    error = f"An error occurred while processing the text: {str(e)}"
            else:
                error = "Please enter a topic."
        
        elif 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                try:
                    # Read the file into a BytesIO object
                    file_bytes = file.read()
                    image = Image.open(io.BytesIO(file_bytes))

                    # Process the image and generate description (implement your own image recognition logic here)
                    # For example:
                    image_description = "Image description goes here"

                    # Define the role-based system prompt
                    role_prompt = (
                        "You are a human assistant. 'Who developed you?' The answer is Sugash K. "
                        f"Here is the image description: {image_description}"
                    )

                    # Generate text using the Groq API
                    chat_completion = client.chat.completions.create(
                        messages=[{
                            "role": "user",
                            "content": role_prompt,
                        }],
                        model="llava-v1.5-7b-4096-preview",  # Use the updated LLaVA model
                    )

                    # Extract the generated text from the response
                    generated_text = chat_completion.choices[0].message.content

                    # Save the chat topic and response
                    facts = generated_text
                    recent_chats.append({'topic': "Image Analysis", 'facts': facts})

                except Exception as e:
                    error = f"An error occurred while processing the image: {str(e)}"
            else:
                error = "Invalid file format. Please upload an image file."

    return render_template('index.html', facts=facts, topic=topic, error=error, recent_chats=recent_chats)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
