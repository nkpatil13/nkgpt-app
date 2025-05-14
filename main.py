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
    st.session_state.editing = False
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "editing" not in st.session_state:
    st.session_state.editing = False

user_input = st.chat_input("Say something...")

# Handle new user input
if user_input:
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    chat_history = st.session_state.messages.copy()
    response = model.generate_content(chat_history).text
    st.session_state.messages.append({"role": "model", "parts": [response]})
    st.session_state.last_streamed_idx = len(st.session_state.messages) - 1
    st.session_state.editing = False

# Display messages
for idx, message in enumerate(st.session_state.messages):
    role = message["role"]
    msg = message["parts"][0]

    if role == "user":
        is_last_user_msg = (
            idx == len(st.session_state.messages) - 2 and
            st.session_state.messages[idx + 1]["role"] == "model"
        )

        if is_last_user_msg and st.session_state.editing:
            with st.chat_message("user"):
                edited_msg = st.text_area("Edit message", value=msg, key="edit_text")
                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.button("✅ Save", key="save_btn"):
                        st.session_state.messages[idx]["parts"][0] = edited_msg
                        st.session_state.messages = st.session_state.messages[:idx + 1]  # remove old response
                        response = model.generate_content(st.session_state.messages.copy()).text
                        st.session_state.messages.append({"role": "model", "parts": [response]})
                        st.session_state.last_streamed_idx = len(st.session_state.messages) - 1
                        st.session_state.editing = False
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key="cancel_btn"):
                        st.session_state.editing = False
                        st.rerun()
        else:
            with st.chat_message("user"):
                col1, col2 = st.columns([10, 1])
                with col1:
                    st.write(msg)
                if is_last_user_msg:
                    with col2:
                        if st.button("✏️", key="edit_btn"):
                            st.session_state.editing = True
                            st.rerun()

    elif role == "model":
        if idx == getattr(st.session_state, "last_streamed_idx", -1):
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

# Autofocus chat input using JS
st.components.v1.html(
    """
    <script>
    window.addEventListener('load', function() {
        const chatInput = parent.document.querySelector('textarea[placeholder="Say something..."]');
        if (chatInput) {
            chatInput.focus();
        }
    });
    </script>
    """,
    height=0,
)
