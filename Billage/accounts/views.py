from ast import Expression
import email
from re import T
from django.shortcuts import render
from .serializers import UserSerializer
from .models import User
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import views, response, permissions, authentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):
    def enforce_csrf(self, request):
        return

# 회원가입
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token
        
        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')

        url = f"http://{current_site}{relativeLink}{token}"
        absurl = f'<a href={url}>클릭하여 회원가입을 완료 합니다!</a>'
        email_body = 'Hi' +user.name + 'Use link below to verify your email \n '+ absurl
        data={'email_body':email_body, 'to_email': user.email, 'email_subject': 'Verify your email'}
        Util.send_email(data)
        return Response(user_data, status = status.HTTP_201_CREATED)

class VerifyEmail(generics.GenericAPIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload['user_id'])
            print(user)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'},status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'},status=status.HTTP_400_BAD_REQUEST)

class UserListAPI(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#로그인
class LoginView(views.APIView):
    # permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return response.Response(UserSerializer(user).data)


class LogoutView(views.APIView):
    def post(self, request):
        logout(request)
        return response.Response()


class UserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def get_object(self, *args, **kwargs):
        return self.request.user