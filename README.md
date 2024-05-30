# Internet-Access-to-LLM


This repository provides a framework to integrate internet search capabilities with a Language Learning Model (LLM), specifically using Gemini 1.5 API. This allows the LLM to fetch and use real-time data from the internet to enhance its responses to user queries.

## Features

- **Keyword Extraction**: Uses KeyBERT to extract relevant keywords from the user's prompt.
- **Internet Search**: Utilizes DuckDuckGo Search API to gather articles, videos, and images based on extracted keywords.
- **Zero-Shot Classification**: Employs a zero-shot classifier to decide whether a query needs internet search or can be answered using the LLM's knowledge.
- **Integration with Gemini 1.5**: Connects with Gemini 1.5 API for generating responses.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/LikithMeruvu/Internet-Access-to-LLM.git
   cd Internet-Access-to-LLM
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up your API keys:
   - Replace `GEMINI_API_KEY` in the code with your Gemini API key.

## Usage

To run the program, execute the following command:
```sh
python main.py
```

## Code Overview

### Keyword Extraction

The `keyword_extractor` function uses KeyBERT to extract top keywords from the user's prompt. These keywords are then used for internet search.

```python
def keyword_extractor(prompts):
    ...
```

### Internet Search

The `DuckDuckGoSearcher` class handles searching for articles, videos, and images using DuckDuckGo's API.

```python
class DuckDuckGoSearcher:
    ...
```

### Zero-Shot Classification

This classifier decides whether a query requires internet search based on the prompt.

```python
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
...
```

### Generating Responses

Depending on the classification result, the program either uses the LLM's knowledge or performs an internet search to gather additional information before generating a response.

```python
def get_response(prompt):
    ...
```

## Example

Here's how the process works:

1. **User Input**: The user provides a query.
2. **Classification**: The query is classified to determine if internet search is needed.
3. **Keyword Extraction**: Relevant keywords are extracted from the query.
4. **Internet Search**: If required, the program performs an internet search and gathers data.
5. **Response Generation**: The LLM generates a response, optionally using the gathered data.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any feature requests or bug reports.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue or contact the repository owner.
```
