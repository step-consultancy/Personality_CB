from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .gpt_helper import (
    INTRO_QUESTION,
    select_best_questions,
    generate_personality_profile,
    generate_feedback
)
from .models import personalityResponse

def index(request):
    initial_questions = [INTRO_QUESTION]
    initial_options = [[]]
    return render(request, 'index.html', {
        'questions': initial_questions,
        'options': initial_options
    })

@csrf_exempt
def submit(request):
    if request.method == 'POST':
        user_intro = request.POST.get('intro', '')

        qa_pairs = []
        i = 0
        while True:
            question_key = f'question_{i}'
            answer_key = f'answer_{i}'
            if question_key in request.POST and answer_key in request.POST:
                qa_pairs.append((request.POST[question_key], request.POST[answer_key]))
                i += 1
            else:
                break
        
        if qa_pairs:
            qa_pairs.pop(0)

        profile = generate_personality_profile(user_intro, qa_pairs)

        if request.user.is_authenticated:
            personalityResponse.objects.update_or_create(
                user=request.user,
                defaults={'response': profile}
            )

        return render(request, 'index.html', {'profile': profile})

    return render(request, 'index.html')

@csrf_exempt
def feedback_view(request):
    if request.method == 'POST':
        question = request.POST.get('question', '')
        answer = request.POST.get('answer', '')
        current_index = int(request.POST.get('currentIndex', '0'))
        
        try:
            if current_index == 0:
                feedback = generate_feedback(question, answer)
                next_qa_data = select_best_questions(answer)
                return JsonResponse({
                    'feedback': feedback,
                    'next_questions': next_qa_data
                })
            else:
                feedback = generate_feedback(question, answer)
                return JsonResponse({'feedback': feedback})

        except Exception as e:
            print(f"❌ OpenAI Feedback/Question Generation Error: {str(e)}")
            return JsonResponse({'feedback': "That's interesting! Let's continue."})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
