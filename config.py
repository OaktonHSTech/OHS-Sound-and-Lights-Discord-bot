import os

DB_FILE = "tags.db"
OLLAMA_URL = "http://ollama:11434"
MODEL = "phi3:mini"

with open("discord_token.txt", "r") as f:
    DISCORD_TOKEN = f.read().strip() 