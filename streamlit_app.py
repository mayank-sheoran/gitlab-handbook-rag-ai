import os
import hashlib
import hmac
from datetime import datetime, timedelta

import streamlit as st
import requests
from typing import List, Dict, Any

class GitLabChatApp:
    def __init__(self):
        self.api_base_url = os.getenv("BACKEND_URL", "http://localhost:9999")
        self.chat_endpoint = f"{self.api_base_url}/chat"

    def initialize_session_state(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def add_message_to_history(self, role: str, content: str):
        message = {"role": role, "content": content}
        st.session_state.chat_history.append(message)
        st.session_state.messages.append(message)

    def send_chat_request(self, query: str, k: int = 10) -> Dict[str, Any]:
        try:
            user_messages_only = [
                msg for msg in st.session_state.chat_history
                if msg["role"] == "user"
            ]

            payload = {
                "query": query,
                "k": k,
                "chat_history": user_messages_only
            }

            response = requests.post(
                self.chat_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "answer": f"Error: Unable to get response from server (Status: {response.status_code})",
                    "citations": [],
                    "rewritten_query": query
                }

        except requests.exceptions.ConnectionError:
            return {
                "answer": "Error: Unable to connect to the chat service. Please ensure the backend is running.",
                "citations": [],
                "rewritten_query": query
            }
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "citations": [],
                "rewritten_query": query
            }

    def render_chat_message(self, role: str, content: str):
        with st.chat_message(role):
            st.markdown(content)

    def render_citations(self, citations: List[Dict[str, Any]]):
        if not citations:
            return

        st.subheader("📚 Sources")

        for citation in citations:
            with st.expander(f"[{citation['index']}] {citation['title'][:100]}..."):
                st.write(f"**URL:** {citation['url']}")
                st.write(f"**Snippet:**")
                st.write(citation['snippet'][:500] + "..." if len(citation['snippet']) > 500 else citation['snippet'])

    def clear_chat_history(self):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

    def run(self):
        st.set_page_config(
            page_title="GitLab Handbook Chat",
            page_icon="🦊",
            layout="wide"
        )

        st.title("🦊 GitLab Handbook Chat Assistant")
        st.markdown("Ask questions about GitLab's handbook and direction documents")

        self.initialize_session_state()

        col1, col2 = st.columns([3, 1])

        with col2:
            st.subheader("📝 Chat History")

            if st.session_state.chat_history:
                st.write(f"**Messages:** {len(st.session_state.chat_history)}")

                with st.expander("View History"):
                    for i, msg in enumerate(st.session_state.chat_history):
                        role_emoji = "👤" if msg["role"] == "user" else "🤖"
                        st.write(f"{role_emoji} **{msg['role'].title()}:** {msg['content'][:100]}...")

                if st.button("Clear History", type="secondary"):
                    self.clear_chat_history()
            else:
                st.write("No chat history yet")

            st.subheader("ℹ️ About")
            st.write("""
            This chat assistant helps you find information from GitLab's handbook and direction documents.
            
            **Features:**
            - Context-aware responses using chat history
            - Citation tracking
            - Semantic search
            - Real-time conversation flow
            - 🔒 Secure access control
            """)

        with col1:
            st.subheader("💬 Chat")
            for message in st.session_state.messages:
                self.render_chat_message(message["role"], message["content"])

            if prompt := st.chat_input("Ask a question about GitLab's handbook..."):
                self.render_chat_message("user", prompt)
                self.add_message_to_history("user", prompt)

                with st.spinner("Searching GitLab handbook..."):
                    response = self.send_chat_request(prompt)

                assistant_response = response["answer"]
                self.render_chat_message("assistant", assistant_response)
                self.add_message_to_history("assistant", assistant_response)

                if response.get("citations"):
                    self.render_citations(response["citations"])

if __name__ == "__main__":
    app = GitLabChatApp()
    app.run()
