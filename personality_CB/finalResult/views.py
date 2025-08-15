from django.shortcuts import render
import openai
from astro.models import astroResponse
from Home.models import personalityResponse

# Create your views here.
def finalResult(request):
    astroRes = astroResponse.objects.filter(user=request.user).values_list('response', flat=True).first()
    personalityRes = personalityResponse.objects.filter(user=request.user).values_list('response', flat=True).first()

    prompt = f"""
        You are a helpful assistant. The following two texts are:

        1. An **astrological report**:
        {astroRes}

        2. A **personality profile**:
        {personalityRes}

        Summarize both reports into a **single coherent paragraph**, highlighting the user's key personality traits and life guidance. Keep it simple, insightful, and 100–150 words long.
        """
    
    final_response = get_openai_summary(prompt)  

    return render(request, 'finalResult.html', {'final_response': final_response})

def get_openai_summary(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are an expert summarizer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()