from rest_framework import serializers
from .models import User, BookMark, BookMarkUser, Follow
from post.serializers import PostSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CreateUserSerializer(serializers.ModelSerializer):
    """
    A serializer to create a new user.
    """
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
            raise serializers.ValidationError('Passwords must match')
        if not 8 <= len(data['password']) <= 32:
            raise serializers.ValidationError('The length of the password must be between 8 and 32 characters')
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    A serializer to show `username` and user `profile`.
    """

    class Meta:
        model = User
        fields = ('username', 'profile')


class UserNameProfileSerializer(serializers.ModelSerializer):
    """
    A serializer to show `name` (or `username` if there is no name) and user `profile`.
    """
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('name', 'profile')
    
    def get_name(self, obj):
        return obj.name or obj.username


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer related to getting all user information.
    """
    followers = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('is_following', 'id', 'name', 'username', 'skills', 'profile', 'about', 'followers')
    
    def get_followers(self, obj):
        return obj.user_followers.count()
    
    def get_is_following(self, obj):
        try:
            auth_user = self.context['request'].user
            if Follow.objects.filter(from_user=auth_user, to_user=obj).exists():
                return True
            elif auth_user == obj:
                return None
            return False
        except:
            return None


class UserEditSerializer(serializers.ModelSerializer):
    """
    Serializer related to user editing.
    """

    class Meta:
        model = User
        fields = ('name', 'family', 'username', 'skills', 'profile', 'about')


class BookMarkDetailSerializer(serializers.ModelSerializer):
    """
    Serializer related to getting all bookmark information.
    """
    posts = serializers.SerializerMethodField()

    class Meta:
        model = BookMark
        fields = ('id', 'title', 'posts')
    
    def get_posts(self, obj):
        bookmark_posts = BookMarkUser.objects.filter(book_mark=obj)
        posts = []
        for bookmark_post in bookmark_posts:
            posts.append(bookmark_post.post)
        serializer = PostSerializer(posts, many=True)
        return serializer.data


class BookMarkSerializer(serializers.ModelSerializer):
    """
    Serializer related to getting `id` and `title` of a bookmark.
    """

    class Meta:
        model = BookMark
        fields = ('id', 'title')
    

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizing the serializer class to get my custom data after login. We have access to the 'user' here.
    """
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data['user'] = UserDetailSerializer(self.user).data
        return validated_data

