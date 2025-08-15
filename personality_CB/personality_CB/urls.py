from django.urls import path, include
from .views import auth_view, logout
from django.contrib.auth.views import LogoutView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_view, name='auth'),
    path('logout/', logout, name='logout'),
    path('home', include('Home.urls')),
    path('astro', include('astro.urls')),
    path('finalResult', include('finalResult.urls')),
    path('analysis', include('analysis.urls')),
]