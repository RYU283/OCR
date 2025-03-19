from flask import Flask, request, jsonify, render_template_string
import requests

API_KEY = ''
class GeminiAPI:
    def __init__(self, api_key=API_KEY):
        self.api_key = api_key
        self.endpoint = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.api_key}'

    def generate_text(self, prompt):
        headers = {
            'Content-Type': 'application/json',
        }

        data = {
            'contents': [
                {
                    'parts': [
                        {
                            'text': f"{prompt}"
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()

            if 'candidates' in result:
                candidates = result['candidates']
                if len(candidates) > 0 and 'content' in candidates[0] and 'parts' in candidates[0]['content'] and len(candidates[0]['content']['parts']) > 0:
                    return candidates[0]['content']['parts'][0].get('text', 'No text found')
            return "Gemini API did not return expected data."

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return "Error: Failed to connect to Gemini API."

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def chat_with_gemini():
    if request.method == 'GET':
        return render_template_string('''
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Gemini Chatbot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f7f7f7;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
                .container {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    width: 400px;
                    max-width: 100%;
                    display: flex;
                    flex-direction: column;
                    height: 600px;
                    overflow: hidden;
                }
                .messages {
                    flex: 1;
                    padding: 10px;
                    overflow-y: auto;
                    border-bottom: 1px solid #ddd;
                }
                .input-area {
                    display: flex;
                    padding: 10px;
                    background-color: #f1f1f1;
                }
                #questionInput {
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    outline: none;
                    font-size: 14px;
                }
                #sendButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    margin-left: 10px;
                    cursor: pointer;
                    font-size: 14px;
                    transition: background-color 0.3s ease;
                }
                #sendButton:hover {
                    background-color: #0056b3;
                }
                .message {
                    margin-bottom: 15px;
                    display: flex;
                }
                .message.user {
                    justify-content: flex-end;
                }
                .message.bot {
                    justify-content: flex-start;
                }
                .message .text {
                    max-width: 70%;
                    padding: 10px;
                    border-radius: 10px;
                    font-size: 14px;
                }
                .message.user .text {
                    background-color: #007bff;
                    color: white;
                }
                .message.bot .text {
                    background-color: #f1f1f1;
                    color: black;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="messages" id="messages"></div>
                <div class="input-area">
                    <input type="text" id="questionInput" placeholder="내용 입력">
                    <button id="sendButton">전송</button>
                </div>
            </div>

            <script>
                document.getElementById('sendButton').addEventListener('click', sendMessage);
                document.getElementById('questionInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });

                function sendMessage() {
                    const input = document.getElementById('questionInput');
                    const message = input.value;
                    if (message.trim() !== '') {
                        displayMessage(message, 'user');
                        fetch('/', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ question: message })
                        })
                        .then(response => response.json())
                        .then(data => {
                            displayMessage(data.answer, 'bot');
                        })
                        .catch(error => {
                            console.error('Error:', error);
                        });
                        input.value = '';
                    }
                }

                function displayMessage(text, sender) {
                    const messages = document.getElementById('messages');
                    const messageElement = document.createElement('div');
                    messageElement.className = 'message ' + sender;
                    
                    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                    
                    const textElement = document.createElement('div');
                    textElement.className = 'text';
                    textElement.innerHTML = formattedText;  // 
                    messageElement.appendChild(textElement);
                    messages.appendChild(messageElement);
                    messages.scrollTop = messages.scrollHeight;
                }
            </script>
        </body>
        </html>
        ''')
    
    elif request.method == 'POST':
        data = request.get_json()
        user_question = data.get('question', '')

        gemini = GeminiAPI(api_key=API_KEY)
        response_text = gemini.generate_text(user_question)

        return jsonify({'answer': response_text})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
