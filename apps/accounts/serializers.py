from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )
        
        def validate_email(self,value):
            email = value.strip().lower()
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError("A user with this email already exists.")
            
            return email
        
        def validate(self, attrs):
            if attrs["password"] != attrs["password_confirm"]:
                raise serializers.ValidationError({
                    "password_confirm": "Password fields didn't match."})
                
            return attrs
        
        def create(self, validated_data):
            validated_data.pop("password_confirm")  # Remove the confirm password field
            password = validated_data.pop("password")
            user = CustomUser.objects.create_user(password=password, **validated_data)
            return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data 
        return data  # Include user profile data in the response