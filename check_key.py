from backend.config import GEMINI_API_KEY

print("Key loaded:", bool(GEMINI_API_KEY))
print("Key length:", len(GEMINI_API_KEY))
print("First 6 characters:", GEMINI_API_KEY[:6])