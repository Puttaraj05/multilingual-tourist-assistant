import os
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

# Create Gemini client using the API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Show the Gemini models available for this API key
print("Available models:\n")

for model in client.models.list():
    print(model.name)