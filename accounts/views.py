import random
from utils import reset_password, send_otp_code, OTP_CODE_VALID_SECONDS
from django.utils import timezone
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
from .paginations import DefaultPagination, UserPostsPagination, UserFollowPagination, BookMarkListPagination
from .serializers import (
        CreateUserSerializer, UserDetailSerializer, UserEditSerializer, BookMarkDetailSerializer, UserSerializer,
        CustomTokenObtainPairSerializer, BookMarkSerializer
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
            try:
                del request.session['user_registration_info']
            except KeyError:
                pass
            return Response({'detail': 'The code has expired.'}, status=status.HTTP_404_NOT_FOUND)

        user = User.objects.create_user(
            username=data['username'], email=data['email'], password=data['password']
        )

        try:
            del request.session['user_registration_info']
        except KeyError:
            pass
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
    """
    Get the user id and follow that user.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, user_id):
        follow = Follow.objects.filter(from_user=request.user, to_user__id=user_id)
        if follow.exists():
            follow.delete()
            return Response({'detail': 'Unfollowed.'}, status=status.HTTP_200_OK)
        
        if request.user.id == user_id:
            return Response({'detail': 'You can not follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this id.'}, status=status.HTTP_404_NOT_FOUND)

        Follow.objects.create(from_user=request.user, to_user=user)
        return Response({'detail': 'Followed.'}, status=status.HTTP_200_OK)


class FollowingsView(generics.ListAPIView):
    """
    User followings list.
    """
    serializer_class = UserSerializer
    pagination_class = UserFollowPagination

    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this username.'}, status=status.HTTP_404_NOT_FOUND)

        followings = user.user_followings.all()
        users = [follow.to_user for follow in followings]
        return users


class FollowersView(generics.ListAPIView):
    """
    User followers list.
    """
    serializer_class = UserSerializer
    pagination_class = UserFollowPagination

    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this username.'}, status=status.HTTP_404_NOT_FOUND)

        followers = user.user_followers.all()
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
    """
    Get the title and create a bookmark.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            book_mark = BookMark.objects.create(
                title = request.data['title'],
                user = request.user
            )
            return Response(BookMarkSerializer(book_mark).data, status=status.HTTP_200_OK)
        except KeyError:
            return Response({'detail': '`title` field is required.'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateBookMarkView(APIView):
    """
    Get the title and edit the bookmark.
    """
    permission_classes = (IsAuthenticated,)

    def put(self, request, bookmark_id):
        try:
            book_mark = BookMark.objects.get(id=bookmark_id)
        except BookMark.DoesNotExist:
            return Response({'detail': 'There is no Bookmark with this id.'}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user != book_mark.user:
            return Response(
                {'detail': 'You are not the creator of this bookmark.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            book_mark.title = request.data['title']
        except KeyError:
            return Response({'detail': '`title` field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        book_mark.save()
        return Response(BookMarkSerializer(book_mark).data, status=status.HTTP_200_OK)


class DeleteBookMarkView(APIView):
    """
    Get the id and delete the bookmark.
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, bookmark_id):
        try:
            book_mark = BookMark.objects.get(id=bookmark_id)
        except BookMark.DoesNotExist:
            return Response({'detail': 'There is no Bookmark with this id '})

        if book_mark.user != request.user:
            return Response(
                {'detail': 'You are not the creator of this bookmark.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        book_mark.delete()
        return Response(BookMarkSerializer(book_mark).data, status=status.HTTP_204_NO_CONTENT)


class CreateBookMarkUserView(APIView):
    """
    Get the `bookmark id` and `post id`, then add the post to the bookmark.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, bookmark_id, post_id):
        try:
            book_mark = BookMark.objects.get(id=bookmark_id)
        except BookMark.DoesNotExist:
            return Response({'detail': f'There is no bookmark with this id : {bookmark_id}.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': f'There is no post with this id : {post_id}.'}, status=status.HTTP_404_NOT_FOUND)

        if not BookMarkUser.objects.filter(book_mark=book_mark, post=post).exists():
            if book_mark.user != request.user:
                return Response({'detail': 'You are not the creator of this bookmark.'}, status=status.HTTP_401_UNAUTHORIZED)
                
            BookMarkUser.objects.create(book_mark=book_mark, post=post)
            return Response({'detail': f'post `{post.title}` added to bookmark `{book_mark.title}` successfully.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'The post already exists in this bookmark.'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteBookMarkUserView(APIView):
    """
    Get the bookmarkuser id and delete it (remove post from bookmark).
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, bookmark_id, post_id):
        try:
            book_mark_user = BookMarkUser.objects.get(book_mark__id=bookmark_id, post__id=post_id)
        except BookMarkUser.DoesNotExist:
            return Response({'detail': 'The post does not already exist in the bookmark.'}, status=status.HTTP_404_NOT_FOUND)

        if book_mark_user.book_mark.user != request.user:
            return Response({'detail': 'You are not the creator of this bookmark.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        book_mark_user.delete()
        return Response({'detail': 'The post has been successfully removed from the bookmark.'}, status=status.HTTP_204_NO_CONTENT)


class BookMarkUserExists(APIView):
    """
    Getting `bookmark id` and `post id` and checking if there is a post in that bookmark or not.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, bookmark_id, post_id):
        if BookMarkUser.objects.filter(book_mark__id=bookmark_id, post__id=post_id).exists():
            return Response(True)
        return Response(False)


class GetBookMarkView(APIView):
    """
    Get id and show bookmark.
    """
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, bookmark_id):
        try:
            book_mark = BookMark.objects.get(id=bookmark_id)
        except BookMark.DoesNotExist:
            return Response({'detail': 'There is no bookmark with this id.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookMarkDetailSerializer(book_mark)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetBookMarkListView(generics.ListAPIView):
    """
    Get the list of user bookmarks.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = BookMarkSerializer
    pagination_class = BookMarkListPagination

    def get_queryset(self):
        user = self.request.user
        book_marks = BookMark.objects.filter(user=user)
        return book_marks


class GetPostListView(generics.ListAPIView):
    """
    Get the list of user post.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    pagination_class = UserPostsPagination

    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            return Response({'detail': 'There is no user with this id.'}, status=status.HTTP_404_NOT_FOUND)
        
        if user != request.user:
            page = self.paginate_queryset(user.posts.filter(status=True))
        else:
            page = self.paginate_queryset(user.posts.all())

        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)




# tomprary view
class AllUsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

