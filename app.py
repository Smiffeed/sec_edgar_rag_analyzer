import streamlit as st
from generate import ask_question

# Titile of Web Page
st.title("📈 SEC Edgar RAG Analyzer")
st.markdown("Ask questions about Apple's latest 10-K filing!")

# Chat input box
user_input = st.chat_input("E.g., What are the main risk factors?")

# If user hits enter
if user_input:
    # Display question on the screen
    with st.chat_message("user"):
        st.write(user_input)

    # Loading Spineer while LLM thinks
    with st.spinner("Analyzing SEC filings..."):
        answer = ask_question(user_input)

        # Display AI answer
        with st.chat_message("assistant"):
            st.write(answer)
