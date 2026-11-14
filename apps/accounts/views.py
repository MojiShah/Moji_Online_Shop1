from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from drf_spectacular.utils import extend_schema
from .serializers import (RegisterSerializer,UserProfileSerializer,EmailTokenObtainPairSerializer)

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
    @extend_schema(request=EmailTokenObtainPairSerializer)
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
    @extend_schema(request=TokenRefreshSerializer)
    def post(self,request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data,status=status.HTTP_200_OK)