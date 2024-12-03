from rest_framework import serializers

# for user validation
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# for logging in
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

import logging
from rest_framework import serializers
from .models import *

logger = logging.getLogger(__name__)

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
            'id', 'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'hashed_ip_address', 'created_at', 'full_name', 'has_accepted_tos', 'is_active'
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
    
    def create(self, validated_data):
        # Obține sau creează tipul de utilizator 'bronze'
        user_type = UserType.objects.get_or_create(type_name='bronze')[0]

        # Extrage parola și creează utilizatorul
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)

        # Creează abonamentul pentru utilizatorul nou creat
        UserSubscription.objects.create(
            user=user,
            user_type=user_type,
            start_date=now(),  # Data începerii abonamentului
            end_date=None,  # Abonament nelimitat
            is_active_field=True  # Activ automat
        )

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
    user_type = serializers.SerializerMethodField()    

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'has_accepted_tos', 'user_type']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()   
    
    def get_user_type(self, obj):
        # Obținem user_type din UserSubscription
        subscription = obj.subscription 
        if subscription and subscription.user_type:
            return subscription.user_type.type_name  # Returnează tipul de abonament
        return None  # În caz că nu există un abonament asociat    
      
      
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Obține utilizatorul pe baza datelor de autentificare
        user = self.get_user(attrs)
        
        # Verifică dacă utilizatorul este activ
        if not user.is_active:
            raise AuthenticationFailed({
                'detail': 'Contul este dezactivat. Contactați administratorul pentru detalii.',
                'code': 'user_inactive'
            })        

        # Verifică dacă email-ul este confirmat
        if not user.email_verified:
            logger.warning(f"User {user.email} attempted to log in without verifying email.")
            raise AuthenticationFailed({
                'detail': 'Contul nu este activ! Nu ați confirmat link-ul primit pe email.',
                'code': 'email_not_verified'
            })

        # Dacă utilizatorul este valid, continuă cu validarea de bază
        data = super().validate(attrs)
        return data

    def get_user(self, attrs):
        """
        Obține utilizatorul pe baza datelor de autentificare.
        """
        username = attrs.get('username') or attrs.get('email')
        password = attrs.get('password')

        # Încearcă să autentifici utilizatorul
        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed('Date de autentificare incorecte')

        return user  

class AccountDeletionSerializer(serializers.Serializer):
    password = serializers.CharField() 
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, min_length=8, max_length=100)
    new_password = serializers.CharField(required=True, min_length=8, max_length=100)     

    
# for email confirmations
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()     
