from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
        )
        read_only_fields = fields  # Make all fields read-only for the profile serializer
        

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True,validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone_number",
        )

    def validate_email(self, value):

        email = value.strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):

        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data 
        return data  # Include user profile data in the response
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True,trim_whitespace=False)
    

#for API documentation
class AuthTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField(required=False)
    user = UserProfileSerializer(required=False)

#for API documentation
class LogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = self.context['request'].user
        
        # Check current password
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        
        # Check password confirmation
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        
         # Prevent using the same password
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})
        
        # Validate new password using Django validators
        try:
            validate_password(attrs['new_password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return attrs
    

class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()

        