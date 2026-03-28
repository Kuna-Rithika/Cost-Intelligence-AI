<<<<<<< HEAD
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_claude(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2000
    )
    return response.choices[0].message.content

def format_inr(amount: float) -> str:
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.2f} Cr"
    elif amount >= 100_000:
        return f"₹{amount/100_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

def confidence_gate(confidence: float, threshold: float = 0.85) -> str:
    if confidence >= threshold:
        return "AUTO_EXECUTE"
    else:
        return "NEEDS_APPROVAL"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
=======
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_claude(prompt: str, system: str = None) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=2000
    )
    return response.choices[0].message.content

def format_inr(amount: float) -> str:
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.2f} Cr"
    elif amount >= 100_000:
        return f"₹{amount/100_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

def confidence_gate(confidence: float, threshold: float = 0.85) -> str:
    if confidence >= threshold:
        return "AUTO_EXECUTE"
    else:
        return "NEEDS_APPROVAL"

def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
>>>>>>> d3f3a69b20c5cc97bedaa85d0090b1f4905adf78
    print(f"{'='*60}")