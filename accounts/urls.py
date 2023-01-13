from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views



urlpatterns = [
    path('home/', views.HomeView.as_view()),
    path('all-users/', views.GetAllUsersView.as_view()),

    path('login/', views.CustomTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('get_user/', views.GetUserView.as_view()),
    path('register/', views.UserRegisterView.as_view()),
    path('forgot-password/', views.ForgotPasswordView.as_view()),
    path('check-code/', views.CheckCodeView.as_view()),
    path('reset-password/', views.ResetPasswordView.as_view()),
    path('followings/', views.FollowingsView.as_view()),
    path('followers/', views.FollowersView.as_view()),

    path('user_profile/<str:username>/', views.UserProfileView.as_view()),
    path('user_edit/<str:username>/', views.UserEditView.as_view()),

    path('create-bookmark/', views.CreateBookMarkView.as_view()),
    path('update-bookmark/<int:bookmark_id>/', views.UpdateBookMarkView.as_view()),
    path('delete-bookmark/<int:bookmark_id>/', views.DeleteBookMarkView.as_view()),
    path('create-bookmarkuser/<int:bookmark_id>/<int:post_id>/', views.CreateBookMarkUserView.as_view()),
    path('delete-bookmark-user/<int:bookmarkuser_id>/', views.DeleteBookMarkUserView.as_view()),

    path('get-bookmark/<int:bookmark_id>/', views.GetBookMarkView.as_view()),
    path('get-bookmark-list/', views.GetBookMarkListView.as_view()),

    path('user-posts/<int:user_id>/', views.GetPostListView.as_view()),
    # path('get-user-by-token/', views.GetUserByTokenView.as_view()),
]
