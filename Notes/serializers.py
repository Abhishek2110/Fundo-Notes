from rest_framework import serializers
from .models import Notes

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ('id', 'title', 'description', 'color', 'user')
    
    # def create(self, validated_data):
    #     return Notes.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     pass
