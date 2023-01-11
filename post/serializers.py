from rest_framework import serializers
from .models import Post, File
from datetime import datetime



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
            'id', 'user', 'title', 'body', 'tags', 'description', 'seo_title', 'seo_description',
            'created', 'files'
        )
    
    def get_files(self, obj):
        files = obj.files
        serializer = FileSerializer(files, many=True)
        return serializer.data

    def get_created(self, obj):
        elapsed_time = datetime.utcnow() - obj.created.replace(tzinfo=None)
        t = int(elapsed_time.total_seconds())
        if t < 60:
            return f'{t} seconds'
        elif t < 3600:
            if t // 60 == 1:
                return '1 minute'
            return f'{t // 60} minutes'
        elif t < 86400:
            if t // 3600 == 1:
                return '1 hour'
            return f'{t // 3600} hours'
        elif t < 604800:
            if t // 86400 == 1:
                return '1 day'
            return f'{t // 86400} days'
        elif t // 604800 == 1:
            return '1 week'
        return f'{t // 604800} weeks'

