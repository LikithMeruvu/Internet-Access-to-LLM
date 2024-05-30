
import json
from groq import Groq
from search_api import DuckDuckGoSearcher
from keybert import KeyBERT
import asyncio

# Set up the Groq API client
client = Groq(api_key="GROQ_API_KEY")
MODEL = 'llama3-70b-8192'

# Initialize the searcher
searcher = DuckDuckGoSearcher()

# Define the function for getting articles
def get_articles(keywords: str, max_results: int = 5):
    return json.dumps(searcher.search_articles(keywords, max_results))

def keyword_extractor(prompts: str):
    m = KeyBERT()
    all_keywords = []
    if prompts:
        text = prompts
        keywords = m.extract_keywords(text, keyphrase_ngram_range=(1, 4), stop_words='english')
        filtered_keywords = [(kw, score) for kw, score in keywords if score > 0.25]
        top_keywords = [kw for kw, score in sorted(filtered_keywords, key=lambda x: x, reverse=True)[:10]]
        all_keywords.append(','.join(top_keywords))
        print(all_keywords)
    return all_keywords

def run_conversation(user_prompt: str):
    # Define the initial messages and tools for the Groq model
    messages = [
        {
            "role": "system",
            "content": """You are an LLM that uses the data extracted from the get_articles function to answer questions about articles and media."""
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_articles",
                "description": "Get articles for a given keyword",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "The keywords to search articles for (e.g. 'technology news')",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "The maximum number of results to return",
                            "default": 5,
                        }
                    },
                    "required": ["keywords"],
                },
            },
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096
    )
    response_message = response.choices[0].message
    print(f"Initial Response: {response_message} \n")
    tool_calls = response_message.tool_calls

    print(f"{tool_calls} \n")
    # Step 2: check if the model wanted to call a function
    print("Final Response:")
    if tool_calls:
        available_functions = {
            "get_articles": get_articles,
        }  # only one function in this example, but you can have multiple

        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 3: call the function
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                keywords=function_args.get("keywords"),
                max_results=function_args.get("max_results", 5)
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model=MODEL,
            messages=messages
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content

    else:
        keywords = keyword_extractor(user_prompt)
        if keywords:
            articles, videos, images = asyncio.run(searcher.search_all(keywords[0], max_results=5, imgkey=keywords[0]))
            return {
                "articles": articles,
                "videos": videos,
                "images": images
            }
        else:
            return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    user_prompt = "Tell me the latest news about AI advancements."
    result = run_conversation(user_prompt)
    print(result)
