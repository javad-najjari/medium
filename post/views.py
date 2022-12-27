from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import PostSerializer
from .models import Post, File




class GetPostView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.data._mutable = True
        request.data['user'] = request.user.id
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        files = request.FILES.getlist('files')
        post = Post.objects.last()
        for file in files:
            File.objects.create(file=file, post=post)
        return Response(status=status.HTTP_200_OK)


class DeletePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        if post.user == user:
            post.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdatePostView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




