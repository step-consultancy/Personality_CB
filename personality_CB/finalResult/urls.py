from django.urls import path
from . import views

urlpatterns = [
    path('/', views.finalResult, name='finalResult'),
]
