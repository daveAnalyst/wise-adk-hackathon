from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat(): 
    data = request.get_json() 

    if not data or 'message' not in data: 
        return jsonify({'error' : 'Missing message field'})
    
    user_message = data['message']
    reply = f"You said: {user_message}"
    return jsonify({'reply': reply})

if __name__ == '__main__':
    app.run(debug=True)