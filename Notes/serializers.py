from rest_framework import serializers
from .models import Notes, Label, Collaborator

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ('id', 'title', 'description', 'color', 'reminder', 'is_archive', 'is_trash', 'user')
        read_only_fields = ['is_archive', 'is_trash']
        
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('id', 'name', 'user')
        
class CollaboratorSerializer(serializers.ModelSerializer):
    collaborator = serializers.ListField(child=serializers.IntegerField()) 
    class Meta:
        model = Collaborator
        fields = ('id', 'access_type', 'note', 'collaborator')
        
    def create(self, validated_data):
        # for collab in validated_data['collaborator']:
        #     collab_user = Collaborator(note_id=note.id, user_id=collab, access_type=validated_data['access_type'])
        existing_collab = [obj.user_id for obj in Collaborator.objects.filter(user_id__in=validated_data['collaborator'], note=validated_data['note'])]
        existing_user_ids = []
        for user_id in validated_data['collaborator']:
            if user_id in existing_collab:
                existing_user_ids.append(user_id)
        if existing_user_ids:
            raise Exception(f"Note is already shared to {''.join(str(existing_user_ids))}")
        collab_user = [Collaborator(note=validated_data['note'], user_id=collab, access_type=validated_data['access_type']) for collab in validated_data['collaborator']]
        Collaborator.objects.bulk_create(collab_user)
        return Collaborator
        
        