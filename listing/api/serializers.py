from rest_framework import serializers

# for user validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'meta_title', 'meta_description', 'custom_text', 'parent', 'children')

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

    def get_parent(self, obj):
        if obj.parent:
            return {"id": obj.parent.id, "name": obj.parent.name, "slug": obj.parent.slug}
        return None
    
# for user
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password', 'user_type',
            'first_name', 'last_name', 'hashed_ip_address', 'created_at', 'full_name', 'has_accepted_tos'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'hashed_ip_address': {'read_only': True},
            'created_at': {'read_only': True},
            'email': {'required': True},  # Email este obligatoriu
            'username': {'required': True},  # Username este obligatoriu
           'has_accepted_tos': {'required': True}            
        }
        
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("Parolele nu se potrivesc.")
        
        # Dacă parolele se potrivesc, elimină confirm_password din attrs, pentru că nu trebuie salvat în bază de date
        attrs.pop('confirm_password')

        return attrs        

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def validate_email(self, value):
        # Check if email is unique
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Adresa de email deja exista.")
        
        # Validate email format
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        
        return value      

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Numele de utilizator este deja folosit.")
        return value

    def validate_user_type(self, value):
        valid_types = ['bronze', 'silver', 'gold']
        if value not in valid_types:
            raise serializers.ValidationError("Tipul utilizatorului este invalid.")
        return value
    
    def create(self, validated_data):
        # Set default value for user_type if not provided
        validated_data.setdefault('user_type', 0)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user   

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance  
    
class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'user_type', 'has_accepted_tos']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
      

class AccountDeletionSerializer(serializers.Serializer):
    password = serializers.CharField() 
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, min_length=8, max_length=100)
    new_password = serializers.CharField(required=True, min_length=8, max_length=100)     

    
# for email confirmations
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()     
