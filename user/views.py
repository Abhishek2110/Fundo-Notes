from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
import json
from .models import User
from django.forms import model_to_dict

# Create your views here.
def register_user(request):
    if request.method != 'POST':
         return JsonResponse({'msg': 'Method not allowed'})
    try:
        data = json.loads(request.body)
        user = User.objects.create(**data)
        return JsonResponse({'message': 'User registered', 'status': 201, 
                             'data': model_to_dict(user)})
    except Exception as e:
        return JsonResponse({'message': str(e), 'status': 400})
    
def login(request):
    if request.method != 'POST':
        return JsonResponse({'msg': 'Method not allowed'})
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        if User.objects.filter(email = email, password=password).first():
            # authenticate(email = email, password = password)
            return JsonResponse({'message': 'Login successful', 'status': 200})
        # User authentication failed
        return JsonResponse({'message': 'Invalid credentials', 'status': 401})
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON data in request body', 'status': 400})
    except Exception as e:
        return JsonResponse({'message': str(e), 'status': 400})

