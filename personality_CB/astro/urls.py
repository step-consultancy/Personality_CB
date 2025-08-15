from django.urls import path
from . import views

urlpatterns = [
    path('/', views.astro, name='astro'),
]
