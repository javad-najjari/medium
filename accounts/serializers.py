from rest_framework import serializers
from .models import User, BookMark, BookMarkUser
from post.models import Post
from post.serializers import PostSerializer



class CreateUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password2'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        del validated_data['password2']
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('passwords must match')
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'profile')


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('name', 'family', 'username', 'skills', 'email', 'profile', 'about', 'followers')


class UserEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('name', 'family', 'skills', 'profile', 'about')


class BookMarkSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = BookMark
        fields = ('title', 'posts')
    
    def get_users(self, obj):
        bookmark_users = BookMarkUser.objects.filter(book_mark=obj)
        users = []
        for bookmark_user in bookmark_users:
            users.append(bookmark_user.user)
        serializer = UserSerializer(users, many=True)
        return serializer.data
    
    def get_posts(self, obj):
        bookmark_posts = BookMarkUser.objects.filter(book_mark=obj)
        posts = []
        for bookmark_post in bookmark_posts:
            posts.append(bookmark_post.post)
        serializer = PostSerializer(posts, many=True)
        return serializer.data

