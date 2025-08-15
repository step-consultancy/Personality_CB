from django.shortcuts import render
from .gpt_helper import get_openai_astrology
from django.views.decorators.csrf import csrf_exempt
from .models import astroResponse

@csrf_exempt
def astro(request):
    response = None
    formatted = None

    if request.method == "POST":
        dob = request.POST.get("dob")
        tob = request.POST.get("tob")
        place = request.POST.get("place")

        prompt = f"""
You are a professional astrologer. Based on the following details:
- Date of Birth: {dob}
- Time of Birth: {tob}
- Place of Birth: {place}

Generate a full astrological report with the following sections:
Please format your output with clear **numbered bullet points**.  
Use a **double line break after each point and add <br> tag** for clarity.  
Keep the language simple, insightful, and concise.

1. 🌙 **Vedic Astrology Overview**
2. 🌕 **Moon Sign Meaning**
3. ✨ **Nakshatra and Traits**
4. 🪐 **Planetary Positions**
5. 🏠 **House-wise Analysis (1st to 12th)**
6. 👤 **Who You Are – Personality Description**
7. 🔮 **Yogas (Special Planetary Combinations)**
8. ♈ **Western Astrology Overview**
9. 📊 **Life Predictions by Category**  
   - Career  
   - Marriage  
   - Finance  
   - Spirituality  
   - Health  
10. 🧭 **Life Path Summary**
        """

        # Call your OpenAI function
        response = get_openai_astrology(prompt)

        # Optional: Add <br><br> after each line break or numbered point
        formatted = format_paragraph(response)

        # ✅ Proper usage of update_or_create
        astroResponse.objects.update_or_create(
            user=request.user,
            defaults={'response': formatted}
        )

    return render(request, "astro.html", {"response": formatted})

def format_paragraph(paragraph):
    # Try splitting by <br><br> first (or fallback to \n\n)
    if "<br><br>" in paragraph:
        points = paragraph.split("<br><br>")
    else:
        points = paragraph.split("\n\n")

    # Strip each point of leading/trailing spaces or <br>
    cleaned_points = [point.strip().strip("<br>").strip() for point in points if point.strip()]

    return cleaned_points




