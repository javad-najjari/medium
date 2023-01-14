from rest_framework import serializers
from .models import Post, File
from datetime import datetime
from utils import get_time



class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('file',)


class PostSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

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

