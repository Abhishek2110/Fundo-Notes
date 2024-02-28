from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework import exceptions
import re
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(max_length=50, required=True, write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'date_joined')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('date_joined', 'first_name', 'last_name',)

    def validate_username(self, value):
        pattern = r'^[a-zA-Z0-9_]+$'
        if re.match(pattern, value):
            return value
        raise serializers.ValidationError("Invalid Username! Please make sure you do not have space in the username.")
    
    def validate_password(self, password):
        pattern = r'^(?=.*[A-Z])(?=.*\d)([a-zA-Z\d!@#$%^&*()]{8,})$'
        if re.match(pattern, password):
            return password
        raise serializers.ValidationError("Invalid Password! Please make sure your password contains minimum 8 characters, atleast 1 uppercase, atleast 1 numeric number and exactly one special character")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True, write_only=True)
    password = serializers.CharField(max_length=50, required=True, write_only=True)
    
    def create(self, validate_data):
        user = authenticate(**validate_data)
        if not user:
            raise exceptions.AuthenticationFailed('Invalid username or password')
        return user

    

