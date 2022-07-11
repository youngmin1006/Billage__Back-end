from django.urls import path, include
from . import views
from .views import UserListAPI, VerifyEmail
from rest_framework import urls

urlpatterns =[
    path('signup/', views.UserCreate.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('userlist/', UserListAPI.as_view()),
    path('login/', views.LoginView.as_view()),
    path('logout/',views.LogoutView.as_view()),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify")
 ]