


import streamlit as st
import google.generativeai as genai
from src.Searcher import DuckDuckGoSearcher
from transformers import pipeline
import time
import threading
import datetime
import asyncio
# Cache the Pipeline of transformers
@st.cache_resource
def get_classifier():
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    return classifier

classifier = get_classifier()

USE_INTERNET = True

genai.configure(api_key="AIzaSyADB7iNeNiMITsGckS8UYLw-u6t03qr9Qk")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

SYSTEM_PROMPT = "Your name is Kambala AI. Your task is to Respond to the Queries you get."

chat = model.start_chat(history=[{"role": "model", "parts": [SYSTEM_PROMPT]}])

from keybert import KeyBERT
def keyword_extractor(prompts):
    m = KeyBERT()
    all_keywords = []
    if prompts:
        text = prompts
        keywords = m.extract_keywords(text, keyphrase_ngram_range=(1, 4), stop_words='english')
        filtered_keywords = [(kw,score) for kw, score in keywords if score > 0.25]
        top_keywords = [kw for kw, score in sorted(filtered_keywords, key=lambda x: x[1], reverse=True)[:10]]
        all_keywords.append(','.join(top_keywords))
    print(all_keywords)
    return all_keywords

async def get_response(prompt, classifier):
    try:
        candidate_labels = ['Need to search Internet for LLM model to respond to query', 'Doesnt Require any Internet Search for LLM model to Respond query']
        result = classifier(prompt, candidate_labels)

        if result["scores"][1] > 0.4:  
            USE_INTERNET = False
            print(result["scores"])  
        else:
            USE_INTERNET = True
            print(result["scores"])  

        if USE_INTERNET:
            searcher = DuckDuckGoSearcher()
            max_results = 5
            Keywords = keyword_extractor(prompt)
            today_date = datetime.date.today().strftime("%d-%m-%Y")
            search_query = f"{Keywords} today's Date :- {today_date}"
            result = await searcher.search_all(search_query, max_results, f"{Keywords}")
            articles, videos, images = result
            context = ""
            for article in articles:
                context += f"Title: {article['title']}\nText: {article['text']}\n\n"

            response = chat.send_message(f"""
            User Prompt: {prompt}
            \n\n
            Here is the Gathered Data :- {context}
            \n\n
            Instruction:
            Analyze the user prompt to determine the type of query.
            If the query is a general greeting, introduction, or simple question that does not require external information, then:
            Do not use any gathered data from the internet.
            Respond based solely on your own knowledge and conversational abilities.
            If the query is a factual or informational request that would benefit from external data, then:
            Use the gathered data from the internet to supplement your response.
            Combine the user prompt and the gathered data to provide a comprehensive and informative answer.
            For any other type of query, assess whether the gathered data is relevant and useful for the response. Use the data if it is relevant, or respond based on your own knowledge if the data is not useful.
            And do not mention that I gathered data from the internet. It should be abstracted!
            """)

            st.write(response.text)
        else:
            response = chat.send_message([prompt])
            st.write(response.text)

        if USE_INTERNET:
            st.subheader("Gathered Data:")
            st.write("Articles:")
            for article in articles:
                st.write(f"**{article['title']}**")
                # st.write(article['text'])
                st.write(f"[Read more]({article['url']})")
                st.write("---")

            st.write("Videos:")
            for video in videos:
                st.write(f"**{video['title']}**")
                # st.write(video['description'])
                st.video(video['url'])
                st.write("---")

            st.write("Images:")
            num_cols = 3
            for i in range(0, len(images), num_cols):
                cols = st.columns(num_cols)
                for j, image in enumerate(images[i:i+num_cols]):
                    with cols[j]:
                        st.image(image['image'], caption=image['title'], use_column_width=True)
                st.write("---")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def app():
    st.title("Kambala AI")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything you want, I can answer you!"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg.get("role")):
            st.write(msg.get("content"))

    prompt = st.text_input("Enter your query:")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        classifier = get_classifier()
        asyncio.run(get_response(prompt, classifier))

        for msg in st.session_state.messages[-1:]:
            with st.chat_message(msg.get("role")):
                st.write(msg.get("content"))

if __name__ == "__main__":
    app()