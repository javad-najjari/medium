import random
from utils import reset_password, send_otp_code, OTP_CODE_VALID_SECONDS
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from post.models import Post
from post.serializers import PostSerializer
from .models import User, OtpCode, Follow, BookMark, BookMarkUser
from .paginations import DefaultPagination, UserPostsPagination, UserFollowPagination
from .serializers import (
        CreateUserSerializer, UserDetailSerializer, UserEditSerializer, BookMarkSerializer, UserSerializer,
        CustomTokenObtainPairSerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Using the custom serializer to login. We access user here.
    """
    serializer_class = CustomTokenObtainPairSerializer


class HomeView(generics.ListAPIView):
    """
    Display the posts of those you follow.
    """
    serializer_class = PostSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        auth_user = self.request.user

        try:
            my_objects = [user.to_user.posts.all() for user in auth_user.user_followings.all()]
            final_posts = []
            for posts in my_objects:
                for post in posts:
                    final_posts.append(post)
            final_posts = sorted(final_posts, key=lambda x:x.created, reverse=True)
            return final_posts
        except AttributeError:
            return Post.objects.all()


class GetUserView(APIView):
    """
    Get user information and send confirmation code.
    """
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)

        if serializer.is_valid():
            random_code = random.randint(100000, 999999)
            OtpCode.objects.create(email=serializer.validated_data['email'], code=random_code)
            send_otp_code(serializer.validated_data['email'], random_code)

            # To request with postman
            request.session['user_registration_info'] = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password': serializer.validated_data['password']
            }
            return Response({'detail': 'We have sent you a code.'}, status=status.HTTP_200_OK)

        try:
            value = serializer.data
            username_exists = User.objects.filter(username=value['username']).exists()
            email_exists = User.objects.filter(email=value['email']).exists()

            if username_exists or email_exists:
                return Response({'detail': 'Username or email already exists.'}, status=status.HTTP_409_CONFLICT)

            if value['password'] != value['password2']:
                return Response({'detail': 'Passwords does not match.'}, status=status.HTTP_401_UNAUTHORIZED)
                
        except KeyError:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterView(APIView):
    """
    Receive verification code and register the user.
    """
    def post(self, request):
        try:
            data = request.session['user_registration_info']
            code = request.data['code']
        except KeyError:
            try:
                data = request.data['data']
                code = request.data['data']['code']
            except KeyError:
                return Response(
                    {'detail': 'Sessions and body are destroyed.'}, status=status.HTTP_400_BAD_REQUEST
                )
        
        if OtpCode.objects.filter(email=data['email'], code=code).exists():
            otp_code = OtpCode.objects.get(email=data['email'], code=code)
        else:
            return Response({'detail': 'The code is wrong.'}, status=status.HTTP_404_NOT_FOUND)
        
        if (timezone.now() - otp_code.created).seconds > OTP_CODE_VALID_SECONDS:
            otp_code.delete()
            del request.session['user_registration_info']
            return Response({'detail': 'The code has expired.'}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.create_user(
            username=data['username'], email=data['email'], password=data['password']
        )

        del request.session['user_registration_info']
        otp_code.delete()

        tokens = {
            'refresh': str(TokenObtainPairSerializer().get_token(user)),
            'access': str(AccessToken().for_user(user))
        }
        return Response({'tokens': tokens}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    """
    Receive an email to recover the user's password.
    """
    def post(self, request):
        try:
            email = request.data['email']
        except KeyError:
            return Response({'detail': '`email` field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(email=email).exists():
            return Response({'detail': 'There is no user with this email.'}, status=status.HTTP_404_NOT_FOUND)
        
        random_code = random.randint(100000, 999999)
        OtpCode.objects.create(email=email, code=random_code)
        reset_password(email, random_code)

        request.session['user_reset_password'] = {'email': email}
        return Response({'detail': f'The code was sent to this email: {email}'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Receive confirmation code and new user password to change his(her) password.
    """
    def post(self, request):
        try:
            email = request.session['user_reset_password']['email']
        except:
            try:
                email = request.data['email']
            except KeyError:
                return Response(
                    {'detail': 'Sessions and body are destroyed.'}, status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            code = request.data['code']
            password = request.data['password']
            password2 = request.data['password2']
        except KeyError:
            return Response(
                {'detail': 'These fields are required: {code, password, password2}'}, status=status.HTTP_404_NOT_FOUND
            )
        
        if OtpCode.objects.filter(email=email, code=code).exists():
            otp_code = OtpCode.objects.get(email=email, code=code)
        else:
            return Response({'detail': 'The code is wrong.'}, status=status.HTTP_404_NOT_FOUND)

        elapsed_time = timezone.now() - otp_code.created

        if elapsed_time.seconds > OTP_CODE_VALID_SECONDS:
            try:
                del request.session['user_reset_password']
            except:
                pass
            otp_code.delete()
            return Response({'detail': 'The code has expired.'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this email.'}, status=status.HTTP_404_NOT_FOUND)

        if password != password2:
            return Response({'detail': 'Passwords does not match.'}, status=status.HTTP_401_UNAUTHORIZED)
        if not 8 <= len(password) <= 32:
            return  Response(
                {'detail': 'The length of the password must be between 8 and 32 characters.'}, status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password)
        user.save()

        try:
            del request.session['user_reset_password']
        except:
            pass

        otp_code.delete()
        return Response({'detail': 'password changed successfully.'}, status=status.HTTP_200_OK)


class UserFollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        if Follow.objects.filter(from_user=request.user, to_user=user).exists():
            Follow.objects.get(from_user=request.user, to_user=user).delete()
            return Response({'message': 'follow removed'}, status=status.HTTP_200_OK)
        else:
            if user == request.user:
                return Response({'message': 'you can not follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(from_user=request.user, to_user=user)
            return Response({'message': 'follow created'}, status=status.HTTP_200_OK)


class FollowingsView(generics.ListAPIView):
    """
    User followings list.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    pagination_class = UserFollowPagination

    def get_queryset(self):
        followings = self.request.user.user_followings.all()
        users = [follow.to_user for follow in followings]
        return users


class FollowersView(generics.ListAPIView):
    """
    User followers list.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    pagination_class = UserFollowPagination

    def get_queryset(self):
        followers = self.request.user.user_followers.all()
        users = [follow.from_user for follow in followers]
        return users


class UserProfileView(APIView):
    """
    Get the username and view the desired user's profile.
    """
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this username.'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEditView(APIView):
    """
    Edit user information.
    """
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = UserEditSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateBookMarkView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        BookMark.objects.create(
            title = data['title'], user = request.user
        )
        return Response(status=status.HTTP_200_OK)


class UpdateBookMarkView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, bookmark_id):
        book_mark = get_object_or_404(BookMark, id=bookmark_id)
        if request.user != book_mark.user:
            return Response(
                {'detail': 'you are not the creator of this bookmark'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        title = request.data['title']
        book_mark.title = title
        book_mark.save()
        return Response(status=status.HTTP_200_OK)


class DeleteBookMarkView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, bookmark_id):
        book_mark = get_object_or_404(BookMark, pk=bookmark_id)
        if book_mark.user != request.user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        book_mark.delete()
        return Response(status=status.HTTP_200_OK)


class CreateBookMarkUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, bookmark_id, post_id):
        book_mark = get_object_or_404(BookMark, pk=bookmark_id)
        post = get_object_or_404(Post, pk=post_id)
        if not BookMarkUser.objects.filter(book_mark=book_mark, post=post).exists():
            if book_mark.user != request.user:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            BookMarkUser.objects.create(book_mark=book_mark, post=post)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeleteBookMarkUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, bookmarkuser_id):
        book_mark_user = get_object_or_404(BookMarkUser, pk=bookmarkuser_id)
        if book_mark_user.book_mark.user != request.user:
            return Response(status.status.HTTP_401_UNAUTHORIZED)
        book_mark_user.delete()
        return Response(status=status.HTTP_200_OK)


class GetBookMarkView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, bookmark_id):
        book_mark = get_object_or_404(BookMark, pk=bookmark_id)
        serializer = BookMarkSerializer(book_mark)
        return Response(serializer.data)


class GetBookMarkListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        book_marks = BookMark.objects.filter(user=user)
        serializer = BookMarkSerializer(book_marks, many=True)
        return Response(serializer.data)


class GetPostListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    pagination_class = UserPostsPagination

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        if user != self.request.user:
            return user.posts.filter(status=True)
        return user.posts.all()



# tomprary view
class AllUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

