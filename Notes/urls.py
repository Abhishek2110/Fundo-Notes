from django.urls import path
from . import views

my_viewset = views.LabelAPI.as_view({
    'get': 'get',
    'post': 'post',
    'put': 'put',
    'delete': 'delete',
})

archive = views.ArchiveTrashAPI.as_view({
    'patch': 'update_archive',
    'get': 'get_archived_notes'    
})

trash = views.ArchiveTrashAPI.as_view({
    'patch': 'update_trash',    
    'get': 'get_trash_notes'
})

urlpatterns = [
    path('notes/', views.NotesAPI.as_view(), name='NotesApi'),
    path('notes/one/', views.GetOneApi.as_view(), name='NotesGetOneApi'),
    path('label/', my_viewset, name = 'LabelApi'),
    path('archive/', archive, name='ArchiveApi'),
    path('trash/', trash, name='TrashApi'),
]