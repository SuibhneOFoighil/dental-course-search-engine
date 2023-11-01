import time
import streamlit as st
from ai import RagAgent
from message import Message
from utils import extract_reference_numbers

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "agent" not in st.session_state:
    st.session_state.agent = RagAgent()

def display_message(message: Message):
    with st.chat_message(message.role):
        st.write(message.content)
        if message.citations:
            display_citations(message.citations)

def display_citations(citations: dict):
    """
    Displays the citations under the current message.
    Args:
        citations (dict): A dictionary containing the citations to be displayed. Where the key is the citation number and the value is a string containing the citation link.
    """

    if len(citations) == 0:
        return

    def extract_video_link_and_start_time(url):
        result = url.split('&t=')
        video_link = result[0]
        start_time = int(result[1]) if len(result) > 1 else 0
        return video_link, start_time

    #Unpack citations
    references = list(citations.keys())
    links = list(citations.values())

    with st.expander("References🔗"):
        tabs = st.tabs(references)
        for tab, reference, link in zip(tabs, references, links):
            video_link, start_time = extract_video_link_and_start_time(link)
            with tab:
                st.video(video_link, start_time=start_time)

def main():
    st.title("Dental Course Search Engine")
    st.write("Welcome to the Dental Course Search Engine!")
    
    # Display chat history
    for message in st.session_state.chat_history:
        display_message(message)

    # Get user input
    if prompt := st.chat_input("Ask a question..."):

        #Add user input to chat history
        st.session_state.chat_history.append(Message("user", prompt))
        
        with st.chat_message("user"):
            st.write(prompt)

        #Add assistant response
        with st.chat_message("assistant"):

            chat_holder = st.empty()

            #Get response stream from agent
            reponse_stream = st.session_state.agent.get_response_stream(prompt)

            #output streamed response
            full_response = ""
            for response in reponse_stream:
                if response.choices[0]['finish_reason'] == "stop":
                    break
                full_response += response.choices[0]['delta']['content']
                #add blinking cursor to indicate typing
                chat_holder.write(full_response + "▊")

            chat_holder.write(full_response)

            all_citations = st.session_state.agent.get_recent_citations()
            used_citations = extract_reference_numbers(full_response)
            citations = {ref: all_citations[ref] for ref in used_citations if ref in all_citations}
            display_citations(citations)

        #Add assistant response to chat history
        assistant_message = Message("assistant", full_response, citations)
        st.session_state.chat_history.append(assistant_message)

if __name__ == "__main__":
    main()