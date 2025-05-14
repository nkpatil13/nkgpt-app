from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session

# Configure your Gemini API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
model = genai.GenerativeModel("gemini-2.0-flash")
@app.route("/")
def index():
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("index.html", history=session["chat_history"])

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "Please enter a message."})

    try:
        response = model.generate_content(user_input)
        reply = response.text

        # Append to session history
        if "chat_history" not in session:
            session["chat_history"] = []
        session["chat_history"].append({"role": "user", "text": user_input})
        session["chat_history"].append({"role": "bot", "text": reply})
        session.modified = True

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
