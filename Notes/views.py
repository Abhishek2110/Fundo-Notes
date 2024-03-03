from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import NotesSerializer, LabelSerializer, CollaboratorSerializer
from .models import Notes, Label, Collaborator
from user.models import User
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .utils import RedisClient
import json
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='fundo.log')

logger = logging.getLogger(__name__)

# Create your views here.
class NotesAPI(APIView):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = "fundoo_api"

    """
    This resource handles the fetching of notes.

    Methods:
        - GET: Fetch notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the notes are successfully retrieved. Returns a success message, status code 200, and the fetched notes data.
        - 400: If there is an error during notes retrieval. Returns an error message and status code 400.
    """

    @swagger_auto_schema(responses={200: openapi.Response(description="Successfully Fetched Data from Cache/Successfully Fetched Data", examples={
                             "application/json": {'message': 'Successfully Fetched Data from Cache/Successfully Fetched Data', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})  
    def get(self, request):
        try:
            cache_notes = RedisClient.get(f'user_{request.user.id}')
            if cache_notes:
                cache_notes_dict = [json.loads(x) for x in cache_notes.values()]  # Parse JSON string to dictionary
                return Response({'message': 'Successfully Fetched Data from Cache', 'status': 200, 'data': cache_notes_dict}, status=200)
            # If cache_notes is empty or None, proceed with fetching data from database
            lookup = Q(user_id=request.user.id) | Q(collaborators__id=request.user.id)
            notes = Notes.objects.filter(lookup, is_archive = False, is_trash = False)
            serializer = NotesSerializer(notes, many=True)
            return Response({'message': 'Successfully Fetched Data', 'status': 200, 'data': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while fetching notes: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)

    """
    This resource handles the creation of notes.

    Methods:
        - POST: Create notes.

    Request Body:
        - name - str, required. The details of the note to create.

    Responses:
        - 201: If the note is successfully created. Returns a success message, status code 201, and the created notes data.
        - 400: If there is an error during notes creation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'color': openapi.Schema(type=openapi.TYPE_STRING),
            'reminder': openapi.Schema(
                type=openapi.TYPE_STRING,
                example="YYYY-MM-DDTHH:MM:SSZ", # Example of the format "YYYY-MM-DDTHH:MM:SSZ"
            ),
        },
        required=['title', 'description', 'color', 'reminder']
    ),
    responses={
        201: openapi.Response(
            description="Note Created",
            examples={"application/json": {'message': 'Note Created', 'status': 201, 'data': {}}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
)
    def post(self,request):
        try:
            request.data['user'] = request.user.id
            serializer = NotesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            note_id = serializer.instance.id
            RedisClient.save(f'user_{request.user.id}', f'note_{note_id}', serializer.data)
            return Response({'message': 'Note Created', 'status': 201, 
                            'data': serializer.data}, status=201)
        except Exception as e:
            logger.error(f"An error occurred while creating note: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
    
    """
    This resource handles the updation of notes.

    Methods:
        - PUT: Update notes.

    Request Body:
        - name - str, required. The details of the note to update.

    Responses:
        - 200: If the note is successfully updated. Returns a success message, status code 200, and the updated notes data.
        - 400: If there is an error during notes updation. Returns an error message and status code 400.
        - 404: If note is not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'description': openapi.Schema(type=openapi.TYPE_STRING),
            'color': openapi.Schema(type=openapi.TYPE_STRING),
            'reminder': openapi.Schema(
                type=openapi.TYPE_STRING,
                example="YYYY-MM-DDTHH:MM:SSZ", # Example of the format "yyyy-mm-ddTHH:MM:SSZ"
            ),
        },
        required=['id', 'title', 'description', 'color', 'reminder']
    ), responses={200: openapi.Response(description="Data Updated", examples={
                             "application/json": {'message': 'Data Updated', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad request", 401: "Unauthorized", 404: "Note not found"})
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            note_id = request.data.get('id')
            note = Notes.objects.get(id = note_id, user_id=request.data.get('user'))
            serializer = NotesSerializer(instance = note, data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            data_json = serializer.data
            RedisClient.save(f'user_{request.user.id}',f'note_{note_id}', data_json)
            return Response({'message': 'Data Updated', 'status': 200, 'data': serializer.data}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while updating note: {str(e)}")
            return Response({'message': 'Note not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while updating note: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
    
    """
    This resource handles the deletion of notes.

    Methods:
        - DELETE: Delete notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the note is successfully deleted. Returns a success message, status code 200.
        - 400: If there is an error during notes deletion. Returns an error message and status code 400.
        - 404: If note is not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ],responses={200: openapi.Response(description="Note Deleted", examples={
                             "application/json": {'message': 'Note Deleted', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})       
    def delete(self, request):
        try:
            note_id = request.query_params.get('id')
            note = Notes.objects.get(id = note_id)
            user_id = request.user.id
            RedisClient.delete(f'user_{user_id}', f'note_{note_id}')
            note.delete()
            return Response({'message': 'Note Deleted', 'status': 200}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while deleting note: {str(e)}")
            return Response({'msg': 'Notes not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while deleting note: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)

class ArchiveTrashAPI(viewsets.ViewSet):
        
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = "fundoo_api"

    """
    This resource handles the updation of archived notes.

    Methods:
        - PATCH: Update archive notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the archived note is successfully updated. Returns a success message, status code 200.
        - 400: If there is an error during updation of archived notes. Returns an error message and status code 400.
        - 404: Notes not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('note_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ], responses={200: openapi.Response(description="Note moved to Archive/Note moved out of Archive", examples={
                             "application/json": {'message': 'Note moved to Archive/Note moved out of Archive', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized", 404: "Note not found"})  
    def update_archive(self, request):
        try:
            note_id = request.query_params.get('note_id')
            if not note_id:
                return Response({"msg": "Note ID not found", "status": 404}, status=404)
            note = Notes.objects.get(id=note_id, user=request.user)
            note.is_archive = True if not note.is_archive else False
            note.save()
            if note.is_archive:
                return Response({'message': 'Note moved to Archive', 'status':200}, status=200)
            return Response({'message': 'Note moved out of Archive', 'status': 200}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while updating note archive: {str(e)}")
            return Response({'message': 'Note does not Exist', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while updating note archive: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
     
    """
    This resource handles the retrieval of archived notes.

    Methods:
        - GET: Get archive notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the archived note is successfully retrieved. Returns a success message, status code 200.
        - 400: If there is an error during retrival of archived notes. Returns an error message and status code 400.
        - 404: Archived Notes not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(responses={200: openapi.Response(description="Archived Notes", examples={
                             "application/json": {'message': 'Archived Notes', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})     
    def get_archived_notes(self, request):
        try:
            notes = Notes.objects.filter(user=request.user, is_archive=True, is_trash=False)
            serializer = NotesSerializer(notes, many=True)
            return Response({'message': 'Archived Notes', 'status': 200, 'Data': serializer.data}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while fetching archived notes: {str(e)}") 
            return Response({'message': 'Note does not Exist', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while fetching archived notes: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status=400)

    """
    This resource handles the updation of trashed notes.

    Methods:
        - PATCH: Update trash notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the trashed note is successfully updated. Returns a success message, status code 200.
        - 400: If there is an error during updation of trashed notes. Returns an error message and status code 400.
        - 404: Notes not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('note_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ], responses={200: openapi.Response(description="Note moved to Trash/Note moved out of Trash", examples={
                             "application/json": {'message': 'Note moved to Trash/Note moved out of Trash', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized", 404: "Note not found"})  
    def update_trash(self, request):
        try:
            note_id = request.query_params.get('note_id')
            if not note_id:
                return Response({"msg": "Note ID not found", "status": 404}, status=404)
            note = Notes.objects.get(id=note_id, user=request.user)
            note.is_trash = True if not note.is_trash else False
            note.save()
            if note.is_trash:
                return Response({'message': 'Note moved to Trash', 'status':200}, status=200)
            return Response({'message': 'Note moved out of Trash', 'status': 200}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while updating note trash: {str(e)}")
            return Response({'message': 'Note does not Exist', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while updating note trash: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
   
    """
    This resource handles the retrieval of trashed notes.

    Methods:
        - GET: Get trash notes.

    Request Body:
        - Not required.

    Responses:
        - 200: If the trashed note is successfully retrieved. Returns a success message, status code 200.
        - 400: If there is an error during retrival of Trashed notes. Returns an error message and status code 400.
        - 404: Trashed Notes not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(responses={200: openapi.Response(description="Trashed Notes", examples={
                             "application/json": {'message': 'Trashed Notes', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized", 404: "Note not found"})          
    def get_trash_notes(self, request):
        try:
            notes = Notes.objects.filter(user=request.user, is_trash=True)
            serializer = NotesSerializer(notes, many=True)
            return Response({'message': 'Trashed Notes', 'status': 200, 'Data': serializer.data}, status=200)
        except Notes.DoesNotExist as e:
            logger.error(f"An error occurred while fetching trashed notes: {str(e)}") 
            return Response({'message': 'Note does not Exist', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while fetching trashed notes: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status=400)

class GetOneApi(APIView):

    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = "fundoo_api"

    """
    This resource handles retrieval of single note.

    Methods:
        - GET: Get Note.

    Request Body:
        - Not required.

    Responses:
        - 200: If the note is successfully fetched. Returns a success message, status code 200 and note data.
        - 400: If there is an error during note retrieval. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ],responses={200: openapi.Response(description="Successfully Fetched Data from Cache/Successfully Fetched Data", examples={
                             "application/json": {'message': 'Successfully Fetched Data from Cache/Successfully Fetched Data', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})  
    def get(self, request):
        try:
            user_id = request.user.id
            note_id = request.query_params.get('id')
            cache_notes = RedisClient.get_one(f'user_{user_id}', f'note_{note_id}')
            if cache_notes:
                cache_notes_dict = json.loads(cache_notes)
                return Response({'message': 'Successfully Fetched Data from cache', 'status': 200, 'data': cache_notes_dict}, status=200)
            note = Notes.objects.get(id = note_id, user_id = user_id)
            serializer = NotesSerializer(note, many=False)
            return Response({'message': 'Successfully Fetched Data', 'status': 200, 'data': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while fetching note: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status=400)

class LabelAPI(viewsets.ViewSet):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = "fundoo_api"

    """
    This resource handles the fetching of labels.

    Methods:
        - GET: Fetch labels.

    Request Body:
        - Not required.

    Responses:
        - 200: If the labels are successfully retrieved. Returns a success message, status code 200, and the fetched labels data.
        - 400: If there is an error during labels retrieval. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(responses={200: openapi.Response(description="Successfully Fetched Data", examples={
                             "application/json": {'message': 'Successfully Fetched Data', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})  
    def get(self, request):
        try:
            # labels = Label.objects.filter(user_id = request.user.id)
            labels = Label.objects.raw("SELECT * FROM label WHERE user_id = %s", (request.user.id,))
            serializer = LabelSerializer(labels, many=True)
            return Response({'message': 'Successfully Fetched Data', 'status': 200,
                             'data': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while fetching labels: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status = 400)

    """
    This resource handles the creation of labels.

    Methods:
        - POST: Create labels.

    Request Body:
        - name - str, required. The details of the label to create.

    Responses:
        - 201: If the label is successfully created. Returns a success message, status code 201, and the created label data.
        - 400: If there is an error during labels creation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name']
    ), responses={201: openapi.Response(description="Label Created Successfully!", examples={
                             "application/json": {'message': 'Label Created Successfully!', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})
    def post(self, request):
        try:
            request.data['user'] = request.user.id
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO label (name, user_id) values (%s, %s)", (request.data['name'], request.data['user']))
                cursor.execute("select * from label order by id desc fetch first row only")
                columns = [col[0] for col in cursor.description]
                data = cursor.fetchone()
                data = dict(zip(columns, data))
            return Response({'message': 'Label Created Successfully!', 'status': 201, 
                             'data': data}, status = 201)
        except Exception as e:
            logger.error(f"An error occurred while creating labels: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status = 400)
    
    """
    This resource handles the updation of labels.

    Methods:
        - PUT: Update labels.

    Request Body:
        - name - str, required. The details of the label to update.

    Responses:
        - 200: If the label is successfully updated. Returns a success message, status code 200, and the updated labels data.
        - 400: If there is an error during labels updation. Returns an error message and status code 400.
        - 404: If label is not found. Returns an error message and status code 404.
    """
     
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['id', 'name']
    ), responses={200: openapi.Response(description="Data Updated", examples={
                             "application/json": {'message': 'Data Updated', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad request", 401: "Unauthorized", 404: "label not found"})   
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            with connection.cursor() as cursor:
                cursor.execute("UPDATE label SET name = %s WHERE id = %s and user_id = %s", (request.data['name'], request.data['id'], request.user.id))
                cursor.execute("SELECT * FROM label WHERE user_id = %s and id=%s", (request.user.id, request.data['id']))
                data = cursor.fetchone()
                if data:  # Check if data is not None
                    columns = [col[0] for col in cursor.description]
                    data = dict(zip(columns, data))
                    return Response({'message': 'Data Updated', 'status': 200, 'data': data}, status=200)
                else:
                    return Response({'message': 'Label not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while updating labels: {str(e)}") 
            return Response({'message': str(e), 'status': 400}, status=400)

    """
    This resource handles the deletion of labels.

    Methods:
        - DELETE: Delete labels.

    Request Body:
        - Not required.

    Responses:
        - 200: If the label is successfully deleted. Returns a success message, status code 200.
        - 400: If there is an error during labels deletion. Returns an error message and status code 400.
        - 404: If label is not found. Returns an error message and status code 404.
    """
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ],responses={200: openapi.Response(description="Label Deleted", examples={
                             "application/json": {'message': 'Label Deleted', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized", 404: "Label not found"})             
    def delete(self, request):
        try:
            label_id = request.query_params.get('id')
            if label_id is None:
                return Response({'message': 'Label ID not provided', 'status': 400}, status=400)
            if Label.objects.get(id = label_id):
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM label WHERE id = %s AND user_id = %s", (label_id, request.user.id))
                    cursor.execute("SELECT * FROM label WHERE id = %s AND user_id = %s", (label_id, request.user.id))
                    data = cursor.fetchone()
                    if data is None:
                        return Response({'message': 'Label Deleted', 'status': 200}, status=200)
                    else:
                        return Response({'message': 'Label not found', 'status': 404}, status=404)
        except Label.DoesNotExist as e:
            logger.error(f"An error occurred while deleting labels: {str(e)}") 
            return Response({'message': 'Label does not exist', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while deleting label: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)           
                      
class CollaboratorApi(APIView):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    throttle_scope = "fundoo_api"

    """
    This resource handles the creation of collaborators for notes.

    Methods:
        - POST: Create collaborators.

    Request Body:
        - name - str, required. The details of the collaborator to create.

    Responses:
        - 201: If the collaborator is successfully created. Returns a success message, status code 201.
        - 400: If there is an error during collaborator creation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(request_body=CollaboratorSerializer, responses={201: openapi.Response(description="Note Shared to user [User ID]", examples={
                             "application/json": {'message': 'Note Shared to user [User ID]', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})
    def post(self, request):
        try:    
            for user_id in request.data["collaborator"]:
                if user_id == request.user.id:
                    return Response({'message': "Note can't be shared to yourself.", 'status': 400}, status=400)
            if not request.data["collaborator"]:
                return Response({'message': 'Collaborator ID is not provided.', 'status': 400}, status=400)
            serializer = CollaboratorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            return Response({'message': f'Note Shared to user {request.data["collaborator"]}.', 'status': 201}, status=201)
        except Exception as e:
            logger.error(f"An error occurred while creating collaborators: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
    
    """
    This resource handles the deletion of collaborators for notes.

    Methods:
        - DELETE: Delete collaborators.

    Request Body:
        - name - str, required. The details of the collaborator to delete.

    Responses:
        - 200: If the collaborator is successfully deleted. Returns a success message, status code 200.
        - 400: If there is an error during collaborator deletion. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(request_body=CollaboratorSerializer, responses={200: openapi.Response(description="Access to user [User ID] removed.", examples={
                             "application/json": {'message': 'Access to user [User ID] removed.', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})                
    def delete(self, request):
        try:
            note = Notes.objects.get(id=request.data['note'], user_id=request.user.id)
            [note.collaborators.remove(user) for user in request.data['collaborator']]
            return Response({'message': f'Access to user {request.data["collaborator"]} removed.', 'status': 200}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while deleting collaborators: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
            
