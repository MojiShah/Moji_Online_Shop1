from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError

from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings

from drf_spectacular.utils import extend_schema
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    EmailTokenObtainPairSerializer,
    LogoutSerializer,
    AuthTokenResponseSerializer,
    LogoutResponseSerializer,
)
# Create your views here.
class RegisterAPIView(APIView):
    permission_classes=[AllowAny]
    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserProfileSerializer},
    )
    
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)
        # if serializer.is_valid():
        #     user = serializer.save()
        #     return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserProfileSerializer(user)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
        
class LoginAPIView(APIView):
    permission_classes=[AllowAny]
    @extend_schema(
    request=EmailTokenObtainPairSerializer,
    responses={200: AuthTokenResponseSerializer}
    )   
    def post(self,request):
        serializer = EmailTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data,
                        status=status.HTTP_200_OK)
        
class ProfileAPIView(APIView):
    permission_classes=[IsAuthenticated]
    @extend_schema(responses=UserProfileSerializer)
    def get(self,request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class TokenRefreshAPIView(APIView):
    permission_classes=[AllowAny]
    @extend_schema(
    request=TokenRefreshSerializer,
    responses={200: AuthTokenResponseSerializer}
    )
    def post(self,request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data,status=status.HTTP_200_OK)
    
class LogoutAPIView(APIView):
    permission_classes=[IsAuthenticated]
    @extend_schema(
    request=LogoutSerializer,
    responses={200: LogoutResponseSerializer}
    )
    def post(self,request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        # در این فرآیند میا  آیدی کاربر رو از رفرش توکن در خود رکویست استخراج میکنه و با آیدی استخراج شده از خود رکوییست مقایسه می کنه.
        try:
            token = RefreshToken(refresh_token)
            token_user_id = token.get(api_settings.USER_ID_CLAIM)
            if str(token_user_id) != str(request.user.pk):
                raise PermissionDenied("You can not revoke another user's token.")
            
            token.blacklist()
        except TokenError:
            raise ValidationError({"refresh": "Invalid, expired or blacklisted refresh token."})
        
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)