from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os

MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = """
You're an expert text extractor. You extract information from webpage content.
Always extract data without changing it and any other output.
"""


def create_scrape_prompt(page_content: str) -> str:
    return f"""
Extract the information from the following web page:
```

{page_content}

```
""".strip()


def getllm():
    llm = ChatGroq(temperature=0, model_name=MODEL, api_key=os.getenv("GROK"))
    # llm = ChatOpenAI(
    #     model="gpt-4o",
    #     temperature=0,
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
    #
    #
    #     api_key=os.getenv("OPEN_AI")  # if you prefer to pass api key in directly instaed of using env vars
    #     # base_url="...",
    #     # organization="...",
    #     # other params...
    # )
    return llm