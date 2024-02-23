from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.reverse import reverse
import jwt
from .models import User
from jwt import PyJWTError
from .tasks import celery_send_mail


class UserAPI(APIView):

    # Create your views here.
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            url = f'{settings.BASE_URL}{reverse("userApi")}?token={token}'
            email = request.data['email']
            subject = 'This is mail from django server'
            message = f'Hello from Backend developer!\nPlease Verify: {url}'
            from_mail = settings.EMAIL_HOST_USER
            recipient_list = [email]
            celery_send_mail.delay(subject, message, from_mail, recipient_list)
            return Response({'message': 'User registered', 'status': 201, 
                                'data': "serializer.data"}, status=201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
    def get(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                return Response({'message': 'Invalid Token'})
            payload = jwt.decode(token, key=settings.SIMPLE_JWT.get('SIGNING_KEY'), algorithms=[settings.SIMPLE_JWT.get('ALGORITHM')])
            user = User.objects.get(id=payload['user_id'])
            user.is_verified = True
            user.save()
            return Response({'message': 'User verified successfully', 'status': 200}, status=200)
        except PyJWTError:
            return Response({'message': 'Invalid token', 'status': 400}, status=400)
        except User.DoesNotExist:
            return Response({'message': 'User does not exitst', 'status': 400}, status=400)
        
class UserApi(APIView):

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            return Response({'message': 'Login successful', 'status': 200, 'token': str(token)}, status=200)
        # User authentication failed
        except Exception as e:
            print(type(e))
            return Response({'message': str(e), 'status': 400}, status=400)
