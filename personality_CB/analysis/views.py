# mysite/chatbot/views.py
import os
import re
from typing import List, Tuple
import urllib.request as urllib_request  # ✅ Safe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from astro.models import astroResponse 
from Home.models import personalityResponse  # <— keep your actual model names

# OpenAI 0.28.x
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---- Config ----
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # change if you want
TEMPERATURE = 0.3
STRICT_GROUNDING = False  # True => only answer from DB context (say you don’t know otherwise)

# Common zodiac aliases (helps catch more queries)
ZODIAC = [
    "aries","taurus","gemini","cancer","leo","virgo","libra",
    "scorpio","sagittarius","capricorn","aquarius","pisces"
]

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def _word_in_text(word: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE) is not None

def _collect_grounding(username, user_msg: str) -> Tuple[List[astroResponse], List[personalityResponse]]:
    """Return matches from astroResponse + personalityResponse for this message."""
    lm = user_msg.lower()
    # print(username)
    # Load all (small tables are fine to scan in memory; switch to icontains if large)
    astro_matches = list(astroResponse.objects.filter(user=username).values_list('response', flat=True))
    pers_matches = list(personalityResponse.objects.filter(user=username).values_list('response', flat=True))

    return astro_matches, pers_matches

def _format_section(title: str, rows: List[object], key_name: str) -> str:
    if not rows:
        return f"{title}: (none)"
    lines = []
    for r in rows:
        key = _normalize(getattr(r, key_name, ""))
        val = _normalize(getattr(r, "response", ""))
        if key and val:
            lines.append(f"- {key}: {val}")
    return f"{title}:\n" + ("\n".join(lines) if lines else "(none)")

@ensure_csrf_cookie
def chat_page(request):
    # your combined HTML already calls {% url 'chat_api' %}; keep the same template
    return render(request, 'analysis.html')

@require_POST
def chat_api(request):
    user_message = _normalize(request.POST.get('message', ''))
    if not user_message:
        return JsonResponse({'ok': False, 'reply': "Please type a message."}, status=400)

    # 1) Gather context from both tables
    astro_matches, pers_matches = _collect_grounding(request.user, user_message)

    # 2) Exact override if only one perfect hit (optional but useful)
    #    If there’s a single, clear astro OR personality match and the user asked about it,
    #    reply exactly with the stored text without calling OpenAI.
    
    # 3) Build grounded context for the model
    astro_ctx = _format_section("ASTRO_CONTEXT", astro_matches, "astro")
    astro_ctx = astro_matches
    pers_ctx  = _format_section("PERSONALITY_CONTEXT", pers_matches, "trait")
    pers_ctx = pers_matches
    

    if astro_matches or pers_matches:
        guidance = (
            "Use ASTRO_CONTEXT and PERSONALITY_CONTEXT as the primary source of truth. "
            "If both apply, blend them coherently without contradiction. "
            "Prefer ASTRO_CONTEXT for zodiac-specific guidance, and PERSONALITY_CONTEXT for tone/advice personalization. "
            "Be concise and practical."
        )
    else:
        if STRICT_GROUNDING:
            return JsonResponse({
                'ok': True,
                'reply': "I couldn’t find any matching entries in my astro or personality data for that. "
                         "Please mention your zodiac sign or a personality keyword (e.g., 'introvert', 'leader')."
            })
        guidance = (
            "No admin context matched. Give a brief, helpful answer anyway. "
            "Do NOT invent admin facts. If relevant, mention that no specific admin data was found."
        )

    # 4) Call OpenAI 0.28.x
    try:
        completion = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Ground your answer in the provided admin data when available. "
                        + guidance
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"USER_QUESTION:\n{user_message}\n\n"
                        f"{astro_ctx}\n\n{pers_ctx}"
                    ),
                },
            ],
        )
        reply = completion.choices[0].message["content"].strip()
        return JsonResponse({'ok': True, 'reply': reply})
    except Exception as e:
        return JsonResponse({'ok': False, 'reply': f"OpenAI error: {e}"}, status=500)
