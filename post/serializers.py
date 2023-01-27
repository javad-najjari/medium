from rest_framework import serializers
from .models import Post, File
from datetime import datetime
from utils import get_time



class FileSerializer(serializers.ModelSerializer):
    """
    Post file serializer.
    """

    class Meta:
        model = File
        fields = ('file',)


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer related to getting all post information.
    And post validation before `creating` or `editing`.
    """
    files = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'title', 'tags', 'description', 'seo_title', 'seo_description',
            'created', 'files'
        )
    
    def get_files(self, obj):
        files = obj.files
        serializer = FileSerializer(files, many=True)
        return serializer.data

    def get_created(self, obj):
        elapsed_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        seconds = int(elapsed_time.total_seconds())
        return get_time(seconds)
    
    def get_user(self, obj):
        return UserNameProfileSerializer(obj.user).data
    
    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super().create(validated_data)
    
    def validate(self, attrs):
        if 'description' in attrs and len(attrs['description']) > 350:
            raise serializers.ValidationError({'description': 'The length of the description should not be more than 350 characters.'})
        if 'tags' in attrs and ' ' in attrs['tags']:
            raise serializers.ValidationError({'tags': 'Tags must not contain spaces.'})
        # if 'seo_title' in attrs and ' ' in attrs['seo_title']:
        #     raise serializers.ValidationError({'seo_title': 'seo_title must not contain spaces.'})
        # if 'seo_description' in attrs and ' ' in attrs['seo_description']:
        #     raise serializers.ValidationError({'seo_description': 'seo_description must not contain spaces.'})
        
        return super().validate(attrs)


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer related to getting some information of a post.
    It is mostly used for listing posts.
    """
    files = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            'id', 'user', 'title', 'description', 'tags', 'created', 'files'
        )
    
    def get_files(self, obj):
        files = obj.files.first()
        serializer = FileSerializer(files)
        return serializer.data

    def get_created(self, obj):
        elapsed_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        seconds = int(elapsed_time.total_seconds())
        return get_time(seconds)
    
    def get_user(self, obj):
        return UserNameProfileSerializer(obj.user).data
    
    def get_description(self, obj):
        if obj.description:
            if len(obj.description) > 30:
                return obj.description[:30] + ' ...'
            return obj.description
        return None



from accounts.serializers import UserNameProfileSerializer
