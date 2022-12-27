from rest_framework import serializers
from .models import Post
from accounts.serializers import UserSerializer



class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Post
        fields = (
            'user', 'title', 'body', 'tags', 'description', 'seo_title', 'seo_description', 'created'
        )


