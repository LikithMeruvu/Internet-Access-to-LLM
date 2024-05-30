# from langchain_groq import ChatGroq

import google.generativeai as genai
from src.Searcher import DuckDuckGoSearcher
from transformers import pipeline
from keybert import KeyBERT

classifier = pipeline("zero-shot-classification",model="facebook/bart-large-mnli")

USE_INTERNET = True
m = KeyBERT()

def keyword_extractor(prompts):
    all_keywords = []
    if prompts:
        text = prompts
        keywords = m.extract_keywords(text, keyphrase_ngram_range=(1, 4), stop_words='english')
        filtered_keywords = [(kw,score) for kw, score in keywords if score > 0.25]
        top_keywords = [kw for kw, score in sorted(filtered_keywords, key=lambda x: x[1], reverse=True)[:10]]
        all_keywords.append(', '.join(top_keywords))

    print(all_keywords)
    
    return all_keywords

genai.configure(api_key="GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash-latest')

SYSTEM_PROMPT = "Your name is Kambala AI. Your task is to Respond to the Queries you get."

chat = model.start_chat(history=[{"role": "model", "parts": [SYSTEM_PROMPT]}])

def get_response(prompt):
    candidate_labels = ['Need to search Internet for LLM to respond','Doesnt Require any Internet Search for LLM to Respond ']
    result = classifier(prompt, candidate_labels)

    if result["scores"][1] > 0.38: # type: ignore
        USE_INTERNET = False
        print(result["scores"]) # type: ignore
    else:
        USE_INTERNET = True
        print(result["scores"]) # type: ignore




    if USE_INTERNET:
        searcher = DuckDuckGoSearcher()
        max_results = 5
        key = keyword_extractor(prompt)
        articles = searcher.search_articles(f"{key}", max_results)
        context = ""
        for article in articles:
            context += f"Title: {article['title']}\nText: {article['text']}\n\n"
            print(article['title'])

        # print(context)
        print("\n\n👇👇👇👇\n\n")

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
And do not mention that I gathered data from intenet Like that It should Abstracted !
""", stream=True)
        # response.resolve()

        for chunk in response:
            print(chunk.text)
    else:
        response = chat.send_message([prompt], stream=True)
        # response.resolve()

        for chunk in response:
            print(chunk.text)

while True:
    prompt = input("Enter your query: ")
    get_response(prompt)