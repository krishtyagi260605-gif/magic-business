import os
import google.generativeai as genai
from groq import Groq
from config import GROQ_API_KEY, GEMINI_API_KEY

def generate_business_copy(business_name: str, services_list: list[str]) -> tuple[str, str, list[str]]:
    """
    Generate tagline, about description, and 4 USPs using Groq or Gemini API.
    Returns (tagline, about, list_of_usps).
    """
    services_str = ", ".join(services_list) if services_list else "general services"
    prompt = f"""
    You are an expert branding copywriter. Generate professional branding copy for:
    Business Name: {business_name}
    Services Offered: {services_str}
    
    Respond in EXACTLY the following format:
    TAGLINE: <catchy tagline (1 sentence, max 10 words)>
    ABOUT: <professional description of the business, its vision and values (3-4 sentences, max 80 words)>
    USP1: <first short unique selling point, e.g. Premium Quality (max 4 words)>: <description (max 10 words)>
    USP2: <second USP, e.g. Customer First>: <description>
    USP3: <third USP>: <description>
    USP4: <fourth USP>: <description>
    """
    
    # 1. Try Groq (Llama 3.3)
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=250
            )
            response_text = chat_completion.choices[0].message.content
            return parse_llm_response(response_text, business_name)
        except Exception as e:
            print(f"Groq API call failed: {e}. Trying Gemini.")
            
    # 2. Try Gemini
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return parse_llm_response(response.text, business_name)
        except Exception as e:
            print(f"Gemini API call failed: {e}. Falling back to rule-based.")
            
    # 3. Rule-based Fallback
    return get_fallback_copy(business_name, services_list)

def parse_llm_response(text: str, business_name: str) -> tuple[str, str, list[str]]:
    """Parse text output from LLM to fetch tagline, about, and USPs."""
    tagline = ""
    about = ""
    usps = []
    
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith("TAGLINE:"):
            tagline = line.replace("TAGLINE:", "").strip()
        elif line.startswith("ABOUT:"):
            about = line.replace("ABOUT:", "").strip()
        elif any(line.startswith(f"USP{i}:") for i in range(1, 5)):
            usp_val = line.split(":", 1)[1].strip()
            usps.append(usp_val)
            
    # Clean quotes
    tagline = tagline.replace('"', '').replace("'", "")
    
    # Validation checks
    if not tagline:
        tagline = f"Quality & Reliability at {business_name}."
    if not about:
        about = f"Welcome to {business_name}. We are dedicated to providing the highest quality services to our customers. Our professional team is committed to excellence and ensuring absolute client satisfaction."
        
    return tagline, about, usps

def get_fallback_copy(business_name: str, services_list: list[str]) -> tuple[str, str, list[str]]:
    """Return static fallback copywriting materials if API keys are missing or failed."""
    tagline = f"Aapki Har Zaroorat Ka Samadhan" if "sharma" in business_name.lower() else f"Empowering Excellence in Services"
    about = f"At {business_name}, we are dedicated to offering exceptional products and services. Under our expert leadership, we strive to exceed customer expectations, establish standard community guidelines, and deliver reliable value across our offerings."
    
    usps = [
        "Premium Quality: We maintain the highest service delivery standards.",
        "Experienced Team: Work with industry experts who understand your needs.",
        "Affordable Rates: Professional solutions priced for business value.",
        "Customer Centric: Custom solutions built to support your workflow."
    ]
    return tagline, about, usps
