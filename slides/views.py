from calendar import c
import os
from cmd import PROMPT
from dotenv import load_dotenv


from django.shortcuts import render
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# client = genai.Client()

def generate_slide_content(topic):
    PROMPT = f"""
    you generate a slide titles for presentation.
    Return exactly five slide titles for a beginner friendly talk about "{topic}".
    Must return only valid JSON in this exact structure:
    {{
        "slides": [
        {{"title": "..."}},
        {{"title": "..."}},
        {{"title": "..."}},
        {{"title": "..."}},
        {{"title": "..."}}

        ]
    }}

"""
    try:
        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            contents = [{"text": PROMPT}],
            config=types.GenerateContentConfig(response_mime_type = "application/json"),
        )
        raw = ""
        for part in response.parts:
            if part.text:
                raw += part.text.strip()
        
        print("Raw title generation response:", raw)

        data = json.loads(raw)
        titles = [s["title"] for s in data.get("slides", []) if "title" in s]

        if len(titles) == 5:
            return titles
    
    except Exception as e:
        print("Error generating slide titles:", str(e))
    
    return [
        f"Introduction to {topic}",
        f"Core Concepts of {topic}",
        f"How {topic} Works",
        f"Use Cases of {topic}",
        f"Future of {topic}"
    ]

# Create your views here.
def slide_builder(request):
    
    return render(request, 'slide_builder.html')

@csrf_exempt
def generate_slides(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    topic = (body.get('topic',) or '').strip()
    if not topic:
        topic = "Random topic"

    print(f"Topic from client: '{topic}'")

    titles = generate_slide_content(topic)
    print(f"Titles from Ai: {titles}")

    slides = []

    for idx, title in enumerate(titles):
        slides.append({
            "id": idx,
            "title": title,
            "image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80"


        })
    return JsonResponse({'slides': slides})