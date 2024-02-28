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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserAPI(APIView):

    @swagger_auto_schema(request_body=RegisterSerializer, responses={201: openapi.Response(description="User registered", examples={
                             "application/json": {'message': 'User registered', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request"})
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token = RefreshToken.for_user(serializer.instance).access_token
            url = f'{settings.BASE_URL}{reverse("userApi")}?token={token}'
            email = request.data['email']
            subject = 'Verification mail Fundo Notes'
            message = f"""Dear {request.data["username"]},\n\nWelcome to Fundo Notes! We're excited to have you as part of our community. \n\nTo begin, please verify your email address by clicking the following link:\n\nVerification Link:{url}\n\nVerifying your email ensures the security of your account and helps us maintain a safe community. If you did not sign up for a Fundo Notes account, please disregard this email.\n\nThank you for choosing Fundo Notes! If you have any questions or require assistance, don't hesitate to contact our support team at abhishekrajpal819@gmail.com.\n\nBest regards,\n\nFundo Notes Team"""
            from_mail = settings.EMAIL_HOST_USER
            recipient_list = [email]
            celery_send_mail.delay(subject, message, from_mail, recipient_list)
            return Response({'message': 'User registered', 'status': 201, 
                                'data': serializer.data}, status=201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
    ], responses={200: openapi.Response(description="User verified successfully", examples={
                             "application/json": {'message': 'User verified successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})  
    def get(self, request):
        try:
            token = request.query_params.get('token')
            if not token:
                return Response({'message': 'Invalid Token', 'status': 400}, status=400)
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
    
    @swagger_auto_schema(request_body=LoginSerializer, 
                         responses={200: openapi.Response(description="Login successful", examples={
                             "application/json": {'message': 'Login successful', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad Request"})
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
