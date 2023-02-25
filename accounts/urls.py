from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views



urlpatterns = [
    path('home/', views.HomeView.as_view()),

    path('login/', views.CustomTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('get-user/', views.GetUserView.as_view()),
    path('register/', views.UserRegisterView.as_view()),
    path('forgot-password/', views.ForgotPasswordView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
    path('followings/<str:username>/', views.FollowingsView.as_view()),
    path('followers/<str:username>/', views.FollowersView.as_view()),
    path('follow/<int:user_id>/', views.UserFollowView.as_view()),

    path('user-profile/<str:username>/', views.UserProfileView.as_view()),
    path('user-edit/', views.UserEditView.as_view()),

    path('create-bookmark/', views.CreateBookMarkView.as_view()),
    path('update-bookmark/<int:bookmark_id>/', views.UpdateBookMarkView.as_view()),
    path('delete-bookmark/<int:bookmark_id>/', views.DeleteBookMarkView.as_view()),
    path('create-bookmarkuser/<int:bookmark_id>/<int:post_id>/', views.CreateBookMarkUserView.as_view()),
    path('delete-bookmark-user/<int:bookmark_id>/<int:post_id>/', views.DeleteBookMarkUserView.as_view()),
    path('<int:bookmark_id>/<int:post_id>/', views.BookMarkUserExists.as_view()),

    path('get-bookmark/<int:bookmark_id>/', views.GetBookMarkView.as_view()),
    path('get-bookmark-list/', views.GetBookMarkListView.as_view()),

    path('user-posts/<str:username>/', views.GetPostListView.as_view()),

    path('all-users/', views.AllUsersView.as_view()),
]
