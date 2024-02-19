from django.urls import path
from . import views
from .views import LabelAPI

my_viewset = LabelAPI.as_view({
    'get': 'get',
    'post': 'post',
    'put': 'put',
    'delete': 'delete'
})

urlpatterns = [
    path('notes/', views.NotesAPI.as_view(), name='NotesApi'),
    path('label/', my_viewset, name = 'LabelApi'),
]