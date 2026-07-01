import os
from litellm import completion

response = completion(
    model="groq/llama-3.3-70b-versatile",  # DASH not dot
    messages=[{"role": "user", "content": "Say hello in one word"}],
    api_key=os.getenv("GROQ_API_KEY")
)
print("Groq response:", response.choices[0].message.content)