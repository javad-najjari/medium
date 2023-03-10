from django.urls import path
from . import views



urlpatterns = [
    path('<int:post_id>/', views.GetPostView.as_view()),
    path('create/', views.CreatePostView.as_view()),
    path('delete/<int:post_id>/', views.DeletePostView.as_view()),
    path('update/<int:post_id>/', views.UpdatePostView.as_view()),
    path('tag/<str:tag>/', views.GetPostsByTagView.as_view()),
]
