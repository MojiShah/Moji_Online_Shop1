from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError, APIException
from rest_framework.throttling import ScopedRateThrottle


from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

from drf_spectacular.utils import extend_schema

from .services.email_service import send_password_reset_email
from .services.verification_service import send_verification_email
import logging
logger = logging.getLogger(__name__)

from .models import CustomUser

from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    EmailTokenObtainPairSerializer,
    LogoutSerializer,
    AuthTokenResponseSerializer,
    LogoutResponseSerializer,
    ChangePasswordSerializer,
    MessageResponseSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationConfirmSerializer
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
    
class ChangePasswordAPIView(APIView):
    permission_classes=[IsAuthenticated]
    @extend_schema(
    request=ChangePasswordSerializer,
    responses={200: MessageResponseSerializer}
    )
    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Set new password securely
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=["password"])
        
        # Revoke all user's refresh tokens
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
        
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
    

class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_request"

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={200: MessageResponseSerializer}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = CustomUser.objects.filter(
            email__iexact=email,
            is_active=True
        ).first()

        # Send email only if an active account exists
        if user:
            try:
                send_password_reset_email(user)
            except Exception:
                # Do not expose account or SMTP details
                raise APIException("Unable to process your request right now.")
        return Response(
            {
                "detail": (
                    "If an active account exists for this email, "
                    "a password reset link will be sent."
                )
            },
            status=status.HTTP_200_OK
        )

            
class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"
    
    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={200:MessageResponseSerializer}
    )
    
    def post(self,request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]
        
        #Set new password securely
        user.set_password(new_password)
        user.save(update_fields=["password"])
        
        # Revoke all existing refresh tokens
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token = outstanding_token)
        
        return Response({"detail": "Password has been reset successfully."},status=status.HTTP_200_OK)
    
class EmailVerificationAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "email_verification"
    
    @extend_schema(
        request=EmailVerificationConfirmSerializer,
        responses={
            200: MessageResponseSerializer
        }
    )
    
    def post(self,request):
        serializer = EmailVerificationConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.is_email_verified = True
        user.save(update_field=['is_email_verified'])
        return Response({"detail": "Email verified successfully."},status=status.HTTP_200_OK)
