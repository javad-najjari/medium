from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views



urlpatterns = [
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('get_user/', views.GetUserView.as_view()),
    path('register/', views.UserRegisterView.as_view()),
    path('forgot-password/', views.ForgotPasswordView.as_view()),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view()),

    path('user_profile/<int:user_id>/', views.UserProfileView.as_view()),
    path('user_edit/<int:user_id>/', views.UserEditView.as_view()),

    path('create-bookmark/', views.CreateBookMarkView.as_view()),
    path('delete-bookmark/<int:bookmark_id>/', views.DeleteBookMarkView.as_view()),
    path('create-bookmarkuser/<int:bookmark_id>/<int:user_id>/', views.CreateBookMarkUserView.as_view()),
    path('delete-bookmark-user/<int:bookmarkuser_id>/', views.DeleteBookMarkUserView.as_view()),

    path('get-bookmark/<int:bookmark_id>/', views.GetBookMarkView.as_view()),
]
