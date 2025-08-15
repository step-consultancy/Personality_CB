from django.urls import path
from . import views
from analysis.views import chat_page, chat_api

urlpatterns = [
    # path('/', views.analysis, name='analysis'),
    path('/', chat_page, name='chat_page'),
    path('api/chat/', chat_api, name='chat_api'),
]
