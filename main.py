import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-2.5-flash-preview-04-17")

st.title("💬 Insights by Nandkishor")

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    chat_history = st.session_state.messages.copy()
    response = model.generate_content(chat_history).text
    st.session_state.messages.append({"role": "model", "parts": [response]})
    st.session_state.last_streamed_idx = len(st.session_state.messages) - 1

# Display the conversation
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    msg = message["parts"][0]

    if role == "user":
        st.chat_message("user").write(msg)
    else:
        if idx == getattr(st.session_state, "last_streamed_idx", -1):
            # --- FIX: Avatar and message in ONE block ---
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in msg.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        else:
            st.chat_message("assistant").write(msg)




