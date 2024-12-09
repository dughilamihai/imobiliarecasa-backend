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

# for time operations
from datetime import timedelta

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
    account_type = serializers.ChoiceField(choices=User.ACCOUNT_TYPE_CHOICES)  # Adaugă câmpul ACCOUNT_TYPE_CHOICES    

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'confirm_password',
            'first_name', 'last_name', 'hashed_ip_address', 'created_at', 'full_name', 'has_accepted_tos', 'is_active', 'account_type'
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
    
    def validate_first_name(self, value):
        """
        Validează prenumele: minim 3 caractere și maxim 59 caractere.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Prenumele trebuie să conțină cel puțin 3 caractere.")
        if len(value) > 59:  # 59 în loc de 60 pentru personalizare
            raise serializers.ValidationError("Prenumele nu poate depăși 59 de caractere.")
        return value

    def validate_last_name(self, value):
        """
        Validează numele: minim 3 caractere și maxim 89 caractere.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Numele trebuie să conțină cel puțin 3 caractere.")
        if len(value) > 89:  # 89 în loc de 90 pentru personalizare
            raise serializers.ValidationError("Numele nu poate depăși 89 de caractere.")
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
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)     

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'has_accepted_tos', 'user_type', 'account_type_display']

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
    

class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # Exclude validarea automată `unique=True`    
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'account_type_display']

    def validate_first_name(self, value):
        """
        Validează prenumele: minim 3 caractere și maxim 59 caractere.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Prenumele trebuie să conțină cel puțin 3 caractere.")
        if len(value) > 59:  # 59 în loc de 60 pentru personalizare
            raise serializers.ValidationError("Prenumele nu poate depăși 59 de caractere.")
        return value

    def validate_last_name(self, value):
        """
        Validează numele: minim 3 caractere și maxim 89 caractere.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Numele trebuie să conțină cel puțin 3 caractere.")
        if len(value) > 89:  # 89 în loc de 90 pentru personalizare
            raise serializers.ValidationError("Numele nu poate depăși 89 de caractere.")
        return value 
    
    def validate(self, attrs):
            """
            Validează dacă `account_type` este trimis și aruncă eroare.
            """
            if 'account_type' in self.initial_data:
                raise serializers.ValidationError(
                    {"account_type": "Tipul contului nu poate fi modificat după crearea utilizatorului."}
                )
            return attrs    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['strada', 'strada_numar', 'oras', 'judet', 'cod_postal', 'tara']

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['registration_number', 'company_name', 'website', 'linkedin_url', 'facebook_url']

    def validate_company_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Numele companiei este obligatoriu.")
        return value
    
    def validate(self, data):
        # Validare: Utilizatorul trebuie să fie de tip 'companie'
        request_user = self.context['request'].user
        if request_user.account_type != 'company':
            raise serializers.ValidationError({"user": "Profilul de companie poate fi asociat doar unui utilizator de tip 'companie'."})
        return data

    def create(self, validated_data):
        # Asigură-te că profilul este creat doar pentru utilizatorul curent
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)    
    
# for email confirmations
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()    
    
class ListingSerializer(serializers.ModelSerializer):
    county_id = serializers.IntegerField(write_only=True, required=True)  # Acceptă doar ID-ul pentru județ la POST/PUT 
    city_id = serializers.IntegerField(write_only=True, required=True)    # Acceptă doar ID-ul pentru oraș
    neighborhood_id = serializers.IntegerField(write_only=True, required=False) # Acceptă doar ID-ul cartierului    
    category_id = serializers.IntegerField(write_only=True, required=True) # Acceptă doar ID-ul categoriei
    
    county_name = serializers.CharField(source='county.name', read_only=True)  # Afișează numele județului
    city_name = serializers.CharField(source='city.name', read_only=True)      # Afișează numele orașului
    neighborhood_name = serializers.CharField(source='neighborhood.name', read_only=True)  # Afișează numele cartierului    
    category_name = serializers.CharField(source='category.name', read_only=True)  # Afișează numele categoriei    

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'price',
            'currency',
            'status',
            'photo1',
            'photo2',
            'photo3',
            'photo4',
            'photo5',
            'photo6',
            'photo7',
            'photo8',
            'photo9',
            'video_url',
            'latitude',
            'longitude',
            'created_date',
            'valability_end_date',            
            'views_count',
            'like_count',
            'slug',
            'county_id',        # Acceptă ID-ul județului
            'city_id',          # Acceptă ID-ul orașului
            'neighborhood_id',  # Acceptă ID-ul cartierului            
            'category_id',      # Acceptă ID-ul categoriei
            'county_name',      # Returnează numele județului
            'city_name',        # Returnează numele orașului
            'neighborhood_name',# Returnează numele cartierului            
            'category_name',    # Returnează numele categoriei
        ]     

    def validate(self, data):
        # Obține ID-urile transmise
        county_id = data.get('county_id')
        city_id = data.get('city_id')
        neighborhood_id = data.get('neighborhood_id')
        user = self.context['request'].user        

        # Verifică dacă ID-urile obligatorii sunt furnizate
        if not county_id:
            raise serializers.ValidationError({'county_id': 'Județul este obligatoriu.'})
        if not city_id:
            raise serializers.ValidationError({'city_id': 'Orașul este obligatoriu.'})
        if not data.get('category_id'):
            raise serializers.ValidationError({'category_id': 'Categoria este obligatorie.'})

        # Obține obiectele din baza de date
        county = County.objects.filter(id=county_id).first()
        city = City.objects.filter(id=city_id).first()
        neighborhood = Neighborhood.objects.filter(id=neighborhood_id).first() if neighborhood_id else None

        # Validare existență
        if not county:
            raise serializers.ValidationError({'county_id': 'Județul selectat nu există.'})
        if not city:
            raise serializers.ValidationError({'city_id': 'Orașul selectat nu există.'})
        
        if neighborhood_id:
        # Verifică dacă cartierul există în baza de date
            exists = Neighborhood.objects.filter(id=neighborhood_id).exists()
            if not exists:
                raise serializers.ValidationError({
                    'neighborhood_id': "Cartierul selectat nu există în baza de date."
                })

        # Verifică dacă orașul aparține județului
        if city.county != county:
            raise serializers.ValidationError({
                'city_id': "Orașul trebuie să aparțină județului selectat."
            })

        # Verifică dacă cartierul aparține orașului
        if neighborhood and neighborhood.city != city:
            raise serializers.ValidationError({
                'neighborhood_id': "Cartierul trebuie să aparțină orașului selectat."
            })
          
        # Verifica slug sa fie unic
        user_hash = hashlib.md5(str(self.context['request'].user.id).encode()).hexdigest()[:6]
        slug_base = slugify(f"{data['title']} {county.name} {city.name} {user_hash}")
        
        if Listing.objects.filter(slug=slug_base).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"slug": "Slug-ul generat există deja. Vă rugăm să modificați titlul sau alte date pentru a genera un slug unic."})

        # Returnează datele cu slug-ul validat
        data['slug'] = slug_base
                    
        return data

    def validate_valability_end_date(self, value):
        """
        Validează că `valability_end_date` este cu cel puțin o zi mai mare decât `created_date`
        și nu este în trecut.
        """
        today = now().date()

        # Verificare dată în trecut
        if value < today:
            raise serializers.ValidationError("Data de valabilitate nu poate fi în trecut.")

        # Verificare că este cel puțin cu o zi mai mare decât data curentă
        min_valid_date = today + timedelta(days=1)
        if value < min_valid_date:
            raise serializers.ValidationError("Data de valabilitate trebuie să fie cu cel puțin 1 zi mai mare decât data curentă.")
        return value
    
    def validate_county_id(self, value):
        if not County.objects.filter(id=value).exists():
            raise serializers.ValidationError("Județul selectat nu există.")
        return value

    def validate_city_id(self, value):
        if not City.objects.filter(id=value).exists():
            raise serializers.ValidationError("Orașul selectat nu există.")
        return value

    def validate_category_id(self, value):
        if not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Categoria selectată nu există.")
        return value  
    
    def validate_slug(self, value):
        if Listing.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Slug-ul trebuie să fie unic. Slug-ul specificat există deja.")
        return value      