from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import NotesSerializer
from .models import Notes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class NotesAPI(APIView):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            notes = Notes.objects.filter(user_id = request.user.id)
            serializer = NotesSerializer(notes, many=True)
            return Response({'message': 'Successfully Fetched Data', 'status': 200,
                             'data': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)

    def post(self, request):
        try:
            request.data['user'] = request.user.id
            serializer = NotesSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Note Created Successfully!', 'status': 201, 
                             'data': serializer.data}, status = 201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)
     
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            note = Notes.objects.get(id = request.data.get('id'), user_id=request.data.get('user'))
            serializer = NotesSerializer(instance = note, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Data Updated', 'status': 200, 'data': serializer.data}, status=200)
        except Notes.DoesNotExist:
            return Response({'message': 'Note not found', 'status': 404}, status=404)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
            
    def delete(self, request):
        try:
            notes = Notes.objects.get(id = request.data.get('id'), user_id=request.user.id)
            notes.delete()
            return Response({'message': 'Note Deleted', 'status': 200}, status=200)
        except Notes.DoesNotExist:
            return Response({'msg': 'Notes not found', 'status': 404}, status=404)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)