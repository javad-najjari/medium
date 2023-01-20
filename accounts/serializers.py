from rest_framework import serializers
from .models import User, BookMark, BookMarkUser, Follow
from post.serializers import PostSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



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
            raise serializers.ValidationError('Passwords must match')
        if not 8 <= len(data['password']) <= 32:
            raise serializers.ValidationError('The length of the password must be between 8 and 32 characters')
        return data


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'profile')


class UserDetailSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = User
        fields = ('name', 'family', 'username', 'skills', 'profile', 'about')


class BookMarkSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta:
        model = BookMark
        fields = ('id', 'title', 'posts')
    
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ customizing the serializer class to get my custom data after login. we have access to the 'user' here """
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data['user'] = UserDetailSerializer(self.user).data
        return validated_data



