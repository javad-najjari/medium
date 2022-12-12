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
]
