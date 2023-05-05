from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chat import get_response

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_text = request.form['text']
    bot_response = get_response(user_text)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
