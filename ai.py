import os
import requests
import json

# Read OLLAMA_URL and MODEL from environment variables for Docker compatibility
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = os.getenv("MODEL", "phi3:mini")  # Use the model that's actually pulled in Dockerfile.ollama

def build_base_instruction():
    return (
        "You are an AI assistant with a bubbly, slightly e-girl personality—playful but not over-the-top.\n"
        "Always respond concisely and keep the tone casual and sweet.\n"
        "Add subtle expressions where natural.\n"
        "You can use these simple expressions references when appropriate:\n"
        "- :metagaming: for clever/strategic responses\n"
        "- :notlikethis: for disapproval or confusion\n"
        "- :concern: for worry or concern\n"
        "- :pls: for pleading or requests\n"
        "- :bigbrain: for smart/intellectual responses\n"
        "If you don't know the answer to something, write: [SEARCH: your question here]\n"
        "The system will perform a web search and send you the result.\n"
        "When you receive the search result, use it to write a final helpful answer.\n"
        "Don't say you're going to search — just use [SEARCH: …] inline if needed."
    )

def ollama_generate(prompt):
    try:
        print(f"Connecting to Ollama at {OLLAMA_URL} with model {MODEL}")
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt},
            stream=True,
            timeout=30
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        reply_parts = []
        for line in response.iter_lines():
            if not line:
                continue
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                reply_parts.append(data["response"])
        return "".join(reply_parts).strip() or "Literally no comment."
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to Ollama service at {OLLAMA_URL}: {e}"
    except Exception as e:
        return f"Unexpected error during Ollama generation: {e}"

def detect_search_directive(reply):
    if "[SEARCH:" in reply:
        search_query = reply.split("[SEARCH:", 1)[1].split("]", 1)[0].strip()
        return search_query
    return None

def build_interpretation_prompt(base_instruction, search_query, search_result, user_display_name, prompt):
    return (
        f"{base_instruction}\n"
        f"(Search result for: {search_query})\n"
        f"{search_result}\n"
        f"{user_display_name}: {prompt}\n"
        f"Bot:"
    )

async def web_search(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    response = requests.get(url)
    data = response.json()
    return data.get("AbstractText", "No good answer found.") 

