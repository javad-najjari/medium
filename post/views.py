from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics
from .serializers import PostDetailSerializer, PostSerializer
from .models import Post, File
from accounts.paginations import DefaultPagination




class GetPostView(APIView):
    """
    Getting the id and displaying the complete information of the post.
    """
    # permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'There is no post with this id.'}, status=status.HTTP_404_NOT_FOUND)
        
        # if post.user != request.user and not post.status == True:
        #     return Response({'detail': 'You are not the owner and the post cannot be displayed.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePostView(APIView):
    """
    Create a post by taking some fields.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PostDetailSerializer(data=request.data, context={'user': request.user})

        files = request.FILES.getlist('files')
        if len(files) == 0:
            return Response({'detail': 'You must add at least one file.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        
        for file in files:
            File.objects.create(file=file, post=post)
        return Response({'detail': 'Post created successfully.'}, status=status.HTTP_200_OK)


class DeletePostView(APIView):
    """
    Get id and delete post.
    """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'There is no post with this id.'}, status=status.HTTP_404_NOT_FOUND)

        if post.user == request.user:
            post.delete()
            return Response({'detail': 'Post deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'You are not the creator of this post.'}, status=status.HTTP_401_UNAUTHORIZED)


class UpdatePostView(APIView):
    """
    Get the new values and update the post.
    """
    permission_classes = (IsAuthenticated,)

    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'There is no post with this id.'}, status=status.HTTP_404_NOT_FOUND)

        if post.user != request.user:
            return Response({'detail': 'You are not the creator of this post.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = PostDetailSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Changes applied successfully.'}, status=status.HTTP_200_OK)


class GetPostsByTagView(generics.ListAPIView):
    """
    Getting a tag and displaying posts that contain that tag.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    pagination_class = DefaultPagination

    def list(self, request, *args, **kwargs):
        posts = Post.objects.filter(tags__contains=kwargs['tag'], status=True)
        page = self.paginate_queryset(posts)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

