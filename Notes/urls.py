from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotesAPI.as_view(), name='NotesApi'),
    path('create/', views.NotesAPI.as_view()),
    path('update/', views.NotesAPI.as_view()),
    path('delete/', views.NotesAPI.as_view())
]