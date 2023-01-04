from rest_framework import serializers
from .models import Post, File



class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ('file',)


class PostSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

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

