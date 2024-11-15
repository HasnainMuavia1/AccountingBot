"""accountingBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
import uuid
urlpatterns = [
    path('', views.index, name='index'),  # Homepage at root URL
    path('chat/<uuid:session_id>/', views.index, name='chat_session'),
    path('chat/<uuid:session_id>/history/', views.chat_history_all_objects, name='chat_history'),
    path('newsession/', views.new_session, name='new_session'),
    path('upload/',views.upload,name='upload'),
    path('Dashboard/',views.Dashboard,name='Dashboard'),
    path('chat/<str:session_id>/rename/', views.Rename, name='rename'),
    path('chat/<str:session_id>/delete/', views.delete, name='delete'),
    path('params_save/',views.params_save,name='params_save'),
    path('assistant/',views.Assistant_bot,name='assistant'),

]
