from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CustomUser, ClientProfile, ProviderProfile, Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'receiver_name', 'receiver_phone', 'state', 
                 'city', 'postal_code', 'full_address', 'is_default']
        
    def create(self, validated_data):
        user = self.context['request'].user
        address = Address.objects.create(user=user, **validated_data)
        return address

class CustomUserSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'birth_date', 'is_client', 'is_provider', 
                 'is_admin', 'addresses', 'roles']
        read_only_fields = ['is_client', 'is_provider', 'is_admin']

    def get_roles(self, obj):
        roles = []
        if obj.is_client:
            roles.append('client')
        if obj.is_provider:
            roles.append('provider')
        if obj.is_admin:
            roles.append('admin')
        return roles

class ClientProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    default_address = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientProfile
        fields = ['id', 'user', 'phone', 'birth_date', 'national_code', 
                 'is_client', 'default_address']
        read_only_fields = ['is_client']

    def get_default_address(self, obj):
        default_address = obj.get_default_address()
        if default_address:
            return AddressSerializer(default_address).data
        return None

class ProviderProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = ProviderProfile
        fields = ['id', 'user', 'phone', 'birth_date', 'national_code', 
                 'is_provider']
        read_only_fields = ['is_provider']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=['client', 'provider'])
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'user_type']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("رمز عبور و تکرار آن باید یکسان باشند")
        return data

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        confirm_password = validated_data.pop('confirm_password')
        
        # ایجاد کاربر اصلی
        user = User.objects.create_user(**validated_data)
        
        # ایجاد CustomUser
        custom_user = CustomUser.objects.create(
            user=user,
            is_client=(user_type == 'client'),
            is_provider=(user_type == 'provider')
        )
        
        # ایجاد پروفایل مناسب
        if user_type == 'client':
            ClientProfile.objects.create(user=custom_user)
        else:
            ProviderProfile.objects.create(user=custom_user)
            
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("رمز عبور جدید و تکرار آن باید یکسان باشند")
        return data
