import random, string
from utils import reset_password, send_otp_code
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from post.models import Post
from post.serializers import PostSerializer
from .models import User, Reset, OtpCode, Follow, BookMark, BookMarkUser
from .serializers import (
        CreateUserSerializer, UserDetailSerializer, UserEditSerializer, BookMarkSerializer, UserSerializer
)



class HomeView(APIView):
    def get(self, request):
        posts = Post.objects.all()[:10]
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetAllUsersView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class GetUserView(APIView):
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

            return Response(status=status.HTTP_200_OK)

        value = serializer.data

        username_exists = User.objects.filter(username=value['username']).exists()
        email_exists = User.objects.filter(email=value['email']).exists()

        if username_exists or email_exists:
            return Response(status=status.HTTP_409_CONFLICT)

        if value['password'] != value['password2']:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterView(APIView):
    def post(self, request):

        try:
            # if it is requested through postman
            # user information is stored in sessions
            data = request.session['user_registration_info']
            code = request.data['code']
            del request.session['user_registration_info']
        except:
            # if it is requested through frontend
            # The frontend should send the user information (in body) that it got from the previous endpoint
            data = request.data['data']
            code = request.data['data']['code']
        
        otp_code = OtpCode.objects.filter(email=data['email'], code=code).first()
        if otp_code is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        elapsed_time = timezone.now() - otp_code.created
        if elapsed_time.seconds > 180:
            otp_code.delete()
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = User.objects.create_user(
            username=data['username'], email=data['email'], password=data['password']
        )
        
        otp_code.delete()
        tokens = {
            'refresh': str(TokenObtainPairSerializer().get_token(user)),
            'access': str(AccessToken().for_user(user))
        }
        return Response({'tokens': tokens}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    def post(self, request):

        email = request.data['email']

        if not User.objects.filter(email=email).exists():
            return Response({'detail': 'there is no user with this email'}, status=status.HTTP_404_NOT_FOUND)
        
        random_code = random.randint(100000, 999999)
        OtpCode.objects.create(email=email, code=random_code)
        reset_password(email, random_code)

        request.session['user_reset_password'] = {
            'email': email,
        }
        return Response({'detail': f'the code was sent to this email: {email}'}, status=status.HTTP_200_OK)


class CheckCodeView(APIView):
    def post(self, request):
        code = request.data['code']

        try:
            email = request.session['user_reset_password']['email']
        except:
            email = request.data['email']
        
        otp_code = OtpCode.objects.filter(email=email, code=code).first()
        if otp_code is None:
            return Response({'detail': 'the code is wrong'}, status=status.HTTP_404_NOT_FOUND)
        
        elapsed_time = timezone.now() - otp_code.created
        if elapsed_time.seconds > 180:
            otp_code.delete()
            return Response({'detail': 'the code has expired'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'detail': 'ok. now you can change your password'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request):
        try:
            email = request.session['user_reset_password']['email']
        except:
            email = request.data['email']
        
        user = get_object_or_404(User, email=email)

        password = request.data['password']
        password2 = request.data['password2']

        if password != password2:
            return Response({'detail': 'passwords does not match'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user.set_password(password)
        user.save()
        try:
            del request.session['user_reset_password']
        except:
            pass
        return Response({'detail': 'password changed successfully'}, status=status.HTTP_200_OK)


class FollowView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        from_user = request.user
        to_user = get_object_or_404(User, pk=id)
        Follow.objects.create(from_user=from_user, to_user=to_user)
        return Response(status=status.HTTP_200_OK)


class FollowingsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        users = []
        followings = user.user_followings.all()
        for follow in followings:
            users.append(follow.to_user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowersView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        users = []
        followings = user.user_followers.all()
        for follow in followings:
            users.append(follow.from_user)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserEditView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if request.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserEditSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


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


class GetPostListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        posts = user.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

