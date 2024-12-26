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
from django.utils.timezone import localtime

# generating meta tags for listings
from datetime import datetime

# for custom variables
from django.conf import settings

# for hashing
from .utils import generate_hash, MONTHS_RO

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
            'first_name', 'last_name', 'phone_number', 'hashed_ip_address', 'created_at', 'full_name', 'has_accepted_tos', 'is_active', 'account_type', 'profile_picture', 'company_logo'
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
        account_type = attrs.get('account_type')  
        profile_picture = attrs.get('profile_picture')
        company_logo = attrs.get('company_logo')      

        if password != confirm_password:
            raise serializers.ValidationError("Parolele nu se potrivesc.")
        
        # Elimină `confirm_password` din `attrs`, deoarece nu trebuie salvat în baza de date
        attrs.pop('confirm_password')
        
        # Verificări pentru tipul de cont și imaginile permise
        if account_type in ['person', 'agent'] and 'company_logo' in attrs:
            raise serializers.ValidationError("Logo-ul nu este permis pentru acest tip de utilizator.")
        if account_type == 'company' and 'profile_picture' in attrs:
            raise serializers.ValidationError("Imaginea de profil nu este permisă pentru companie.")  
        
        # Verificare și generare hash pentru profile_picture
        if profile_picture:
            hash_value = generate_hash(profile_picture)
            # Verificare dacă există un alt utilizator cu același hash
            if User.objects.filter(profile_picture_hash=hash_value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError({"profile_picture": "Această imagine de profil există deja în sistem."})
            # Adăugare hash la attrs
            attrs['profile_picture_hash'] = hash_value

        # Verificare și generare hash pentru company_logo
        if company_logo:
            hash_value = generate_hash(company_logo)
            # Verificare dacă există un alt utilizator cu același hash
            if User.objects.filter(company_logo_hash=hash_value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError({"company_logo": "Acest logo există deja în sistem."})
            # Adăugare hash la attrs
            attrs['company_logo_hash'] = hash_value    
            
        # Verificăm dacă utilizatorul a acceptat TOS
        has_accepted_tos = attrs.get('has_accepted_tos')
        if not has_accepted_tos:
            raise serializers.ValidationError({"has_accepted_tos": "Trebuie să accepți Termenii și Condițiile pentru a te înregistra."})                      

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
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'has_accepted_tos', 'user_type', 'account_type_display', 'profile_picture', 'company_logo']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()   
    
    def get_user_type(self, obj):
        # Obținem user_type din UserSubscription
        subscription = obj.subscription 
        if subscription and subscription.user_type:
            return subscription.user_type.type_name  # Returnează tipul de abonament
        return None  # În caz că nu există un abonament asociat    
    

class UserInfoSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()   
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)    
    last_active = serializers.SerializerMethodField()    
    joined_on = serializers.SerializerMethodField()     

    class Meta:
        model = User
        fields = ['first_name', 'phone_number', 'user_type', 'account_type_display', 'last_active', 'joined_on', 'username_hash']

    
    def get_user_type(self, obj):
        # Obținem user_type din UserSubscription
        subscription = obj.subscription 
        if subscription and subscription.user_type:
            return subscription.user_type.type_name  # Returnează tipul de abonament
        return None  # În caz că nu există un abonament asociat     
    

    def get_last_active(self, obj):
        if obj.last_login:
            date = localtime(obj.last_login)
            day = date.strftime('%d')
            month = MONTHS_RO[date.strftime('%B')] 
            year = date.strftime('%Y')  # Anul
            return f"Activ pe {day} {month} {year}"
        return "Inactiv"  # Mesaj de fallback dacă nu există `last_login`
    
    def get_joined_on(self, obj):
        if obj.date_joined:
            site_name = getattr(settings, 'SITE_NAME', 'site-ul nostru')
            date = localtime(obj.date_joined)
            month = MONTHS_RO[date.strftime('%B')]
            year = date.strftime('%Y')
            return f"Pe {site_name} din {month} {year}"
        return "Data necunoscută"
      
      
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
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'account_type_display', 'profile_picture', 'company_logo' ]

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
        # Obține tipul de cont și imaginile
        account_type = attrs.get('account_type', self.instance.account_type if self.instance else None)
        profile_picture = attrs.get('profile_picture', self.instance.profile_picture if self.instance else None)
        company_logo = attrs.get('company_logo', self.instance.company_logo if self.instance else None)
          
        """
        Validează dacă `account_type` este trimis și aruncă eroare.
        """
        if 'account_type' in self.initial_data:
            raise serializers.ValidationError(
                {"account_type": "Tipul contului nu poate fi modificat după crearea utilizatorului."}
            )

        # Validare pentru tipul de cont și imagini
        if account_type in ['person', 'agent'] and company_logo:
            raise serializers.ValidationError(
                {"company_logo": "Logo-ul nu este permis pentru acest tip de utilizator."}
            )
        if account_type == 'company' and profile_picture:
            raise serializers.ValidationError(
                {"profile_picture": "Imaginea de profil nu este permisă pentru companii."}
            )

        # Validare pentru unicitate folosind hash-uri
        if profile_picture:
            hash_value = generate_hash(profile_picture)
            if User.objects.filter(profile_picture_hash=hash_value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError({"profile_picture": "Această imagine de profil există deja în sistem."})
            attrs['profile_picture_hash'] = hash_value

        if company_logo:
            hash_value = generate_hash(company_logo)
            if User.objects.filter(company_logo_hash=hash_value).exclude(id=self.instance.id if self.instance else None).exists():
                raise serializers.ValidationError({"company_logo": "Acest logo există deja în sistem."})
            attrs['company_logo_hash'] = hash_value 
                            
        return attrs    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['strada', 'strada_numar', 'oras', 'judet', 'cod_postal', 'tara']

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['registration_number', 'company_name', 'website', 'linkedin_url', 'facebook_url', 'company_type']

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
    
class TagSerializer(serializers.ModelSerializer):
    # Serializare pentru câmpul 'categories' care este o relație ManyToMany
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'icon_name', 'slug', 'status', 'meta_title', 'meta_description', 'description', 'categories']  
        
class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']    
        
class CategoryDetailSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    tags = TagSimpleSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'meta_title', 'meta_description', 'custom_text', 'description', 'parent', 'children', 'tags']

    def get_parent(self, obj):
        if obj.parent:
            return {
                "id": obj.parent.id,
                "name": obj.parent.name,
                "slug": obj.parent.slug
            }
        return None

    def get_children(self, obj):
        children = obj.children.all()
        return CategoryDetailSerializer(children, many=True).data                
    
class ListingSerializer(serializers.ModelSerializer):
    county_id = serializers.IntegerField(write_only=True, required=True)  # Acceptă doar ID-ul pentru județ la POST/PUT 
    city_id = serializers.IntegerField(write_only=True, required=True)    # Acceptă doar ID-ul pentru oraș
    neighborhood_id = serializers.IntegerField(write_only=True, required=False) # Acceptă doar ID-ul cartierului    
    category_id = serializers.IntegerField(write_only=True, required=True) # Acceptă doar ID-ul categoriei
    
    county_name = serializers.CharField(source='county.name', read_only=True)  # Afișează numele județului
    city_name = serializers.CharField(source='city.name', read_only=True)      # Afișează numele orașului
    neighborhood_name = serializers.CharField(source='neighborhood.name', read_only=True)  # Afișează numele cartierului    
    category_name = serializers.CharField(source='category.name', read_only=True)  # Afișează numele categoriei    
    
    # get list of tags
    tag = TagSimpleSerializer(read_only=True, many=True)    
    
    meta_title = serializers.CharField(read_only=True)
    meta_description = serializers.CharField(read_only=True)
    
    # Câmp pentru tag-uri, acceptă lista de ID-uri
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'price',
            'negociabil',            
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
            'tag',    
            'tag_ids',                
            'meta_title', 
            'meta_description', 
            'compartimentare', 
            'zonare',
            'suprafata_utila',
            'numar_camere',
            'year_of_construction',
            'structura',
        ]    

    def validate(self, data):
        # Obține ID-urile transmise
        county_id = data.get('county_id')
        city_id = data.get('city_id')
        neighborhood_id = data.get('neighborhood_id')  
        compartimentare = data.get('compartimentare')
        zonare = data.get('zonare')    
        numar_camere = data.get('numar_camere')   
        year_of_construction = data.get('year_of_construction')    
        structura = data.get('structura')                           
        
        # Obține categoria
        category = Category.objects.get(id=data['category_id']) 

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

        # Verificăm regula pentru "compartimentare"
        if compartimentare is not None and category.group != 0:
            raise serializers.ValidationError({
                'compartimentare': 'Câmpul "Compartimentare" nu este permis pentru această categorie.'
            })    
            
        # Verificăm regula pentru "zonare"
        if zonare is not None and category.group != 3:
            raise serializers.ValidationError({
                'zonare': 'Câmpul "Zonare terenuri" nu este permis pentru această categorie.'
            })
            
        # Verificăm regula pentru "numar_camere"
        if numar_camere is not None and category.group not in [0, 1, 2]:
            raise serializers.ValidationError({
                'numar_camere': 'Câmpul "Număr camere" nu este permis pentru această categorie.'
            })    

        # Verificăm regula pentru "year_of_construction"
        if year_of_construction is not None and category.group == 3:
            raise serializers.ValidationError({
                'year_of_construction': 'Câmpul "An construcție" nu este permis pentru această categorie.'
            })    
            
        # Verificăm regula pentru "structura"
        if structura is not None and category.group == 3:
            raise serializers.ValidationError({
                'structura': 'Câmpul "Structura" nu este permis pentru această categorie.'
            })                          
            
        # Verificare imagini duplicate
        for i in range(1, 10):  # Iterează prin câmpurile foto
            photo_field = data.get(f"photo{i}")
            if photo_field:
                # Generează hash-ul imaginii
                hash_value = generate_hash(photo_field)
                hash_field = f"photo{i}_hash"

                # Verifică dacă există un alt obiect cu același hash
                filters = {hash_field: hash_value}
                if Listing.objects.filter(**filters).exclude(id=self.instance.id if self.instance else None).exists():
                    raise serializers.ValidationError({
                        f"photo{i}": f"Imaginea {i} există deja în sistem."
                    })                       

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
    
    def validate_suprafata_utila(self, value):
        # Verificăm dacă valoarea este pozitivă
        if value is not None and value <= 0:
            raise serializers.ValidationError("Suprafața utilă trebuie să fie mai mare decât 0.")
        
        # Adaugă alte validări dacă este cazul
        if value is not None and value > 10000000:  # Limita maximă teoretică (10 milioane de m²)
            raise serializers.ValidationError("Suprafața utilă este prea mare.")
        return value    
    
    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitudinea trebuie să fie între -90 și 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitudinea trebuie să fie între -180 și 180.")
        return value    
    
    def validate_year_of_construction(self, value):
        anul_curent = datetime.now().year

        # Verificare pentru exact 4 cifre
        if not (1000 <= value <= 9999):
            raise serializers.ValidationError("Anul construcției trebuie să aibă exact 4 cifre.")
        
        # Verificare pentru a nu depăși anul curent
        if value > anul_curent:
            raise serializers.ValidationError(f"Anul construcției nu poate fi mai mare decât anul curent ({anul_curent}).")
        
        return value    
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])  # Extragem tag_ids din datele validate
        
        # Rotunjim la 2 zecimale suprafata utila
        suprafata_utila = validated_data.get('suprafata_utila')
        if suprafata_utila is not None:
            validated_data['suprafata_utila'] = round(suprafata_utila, 2)          
        
        # Creăm instanța fără tag-uri, fără să setăm meta_title și meta_description
        instance = super().create(validated_data)
        
        # Legăm tag-urile la Listing dacă există ID-uri
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)  # Obținem tag-urile din DB
            instance.tag.set(tags)  # Legăm tag-urile la Listing folosind set()        

        # Obținem valorile necesare din instanțele asociate
        city_name = instance.city.name if instance.city else ""
        category_name = instance.category.name if instance.category else ""

        # Obținem lista de tag-uri asociate instanței de anunț
        tags = instance.tag.all()  # Obținem tag-urile din baza de date    
        tag_list = ", ".join(tag.name for tag in tags)  # Le convertim într-un string

        # Construim meta_description
        description_parts = [
            instance.title,
            f"➤ {category_name}",
        ]

        # Verificăm dacă există caracteristici (compartimentare, zonare, tag-uri)
        features_added = False
        features = []

        # Adăugare compartimentare dacă există
        if instance.compartimentare is not None:
            compartimentare_text = instance.get_compartimentare_display()
            features.append(compartimentare_text.capitalize())
            features_added = True

        # Adăugare zonare dacă există
        if instance.zonare is not None:
            zonare_text = instance.get_zonare_display()
            features.append(zonare_text.capitalize())
            features_added = True
            
        # Adăugare număr camere, dacă există
        if instance.numar_camere is not None:
            numar_camere_text = instance.get_numar_camere_display()
            features.append(numar_camere_text)
            features_added = True
            
        # Adăugare tag_list dacă există tag-uri
        if tag_list:
            features.append(tag_list)
            features_added = True

        # Adăugăm "➤ Caracteristici:" doar dacă există vreo caracteristică
        if features_added:
            description_parts.append(f"➤ Caracteristici: {', '.join(features)}")

        description_parts.append(f"➤ Anunț Imobiliar {city_name} {datetime.now().year}")

        # Generăm meta_title și meta_description
        instance.meta_title = f"{instance.title} ➤ Anunț Imobiliar {city_name}"
        instance.meta_description = " ".join(description_parts)

        # Salvăm modificările
        instance.save()

        return instance
    
class ListingUpdateSerializer(serializers.ModelSerializer):
    county_id = serializers.IntegerField(write_only=True, required=False)
    city_id = serializers.IntegerField(write_only=True, required=False)
    neighborhood_id = serializers.IntegerField(write_only=True, required=False)
    category_id = serializers.IntegerField(write_only=True, required=False)
    
    county_name = serializers.CharField(source='county.name', read_only=True)  # Afișează numele județului
    city_name = serializers.CharField(source='city.name', read_only=True)      # Afișează numele orașului
    neighborhood_name = serializers.CharField(source='neighborhood.name', read_only=True)  # Afișează numele cartierului    
    category_name = serializers.CharField(source='category.name', read_only=True)  # Afișează numele categoriei       
    
    # get list of tags
    tag = TagSimpleSerializer(read_only=True, many=True)       
    
    meta_title = serializers.CharField(read_only=True)
    meta_description = serializers.CharField(read_only=True)
    
    # Câmp pentru tag-uri, acceptă lista de ID-uri
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )    

    class Meta:
        model = Listing
        fields = [
            'title',
            'description',
            'price',
            'negociabil',
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
            'valability_end_date',
            'county_id',
            'city_id',
            'neighborhood_id',
            'category_id',
            'county_name',      # Returnează numele județului
            'city_name',        # Returnează numele orașului
            'neighborhood_name',# Returnează numele cartierului            
            'category_name',    # Returnează numele categoriei            
            'slug',  # Pentru validare și recalculare
            'tag',              
            'tag_ids',                
            'meta_title', 
            'meta_description',    
            'compartimentare',
            'zonare', 
            'suprafata_utila',   
            'numar_camere',          
            'year_of_construction',   
            'structura',                                        
        ]

    # Validări individuale
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

    def validate(self, data):
        category_id = data.get('category_id')
        compartimentare = data.get('compartimentare')
        zonare = data.get('zonare')       
        numar_camere = data.get('numar_camere')   
        year_of_construction = data.get('year_of_construction')    
        structura = data.get('structura')   
    
        if 'county_id' in data:
            county = County.objects.filter(id=data['county_id']).first()
            if not county:
                raise serializers.ValidationError({'county_id': 'Județul selectat nu există.'})

        if 'city_id' in data:
            city = City.objects.filter(id=data['city_id']).first()
            if not city:
                raise serializers.ValidationError({'city_id': 'Orașul selectat nu există.'})
            if 'county_id' in data and city.county_id != data['county_id']:
                raise serializers.ValidationError({'city_id': 'Orașul trebuie să aparțină județului selectat.'})

        if 'neighborhood_id' in data:
            neighborhood = Neighborhood.objects.filter(id=data['neighborhood_id']).first()
            if not neighborhood:
                raise serializers.ValidationError({'neighborhood_id': 'Cartierul selectat nu există.'})
            if 'city_id' in data and neighborhood.city_id != data['city_id']:
                raise serializers.ValidationError({'neighborhood_id': 'Cartierul trebuie să aparțină orașului selectat.'})
            
        # Verificăm categoria doar dacă este furnizată
        if category_id:
            category = Category.objects.filter(id=category_id).first()
            if not category:
                raise serializers.ValidationError({'category_id': 'Categoria selectată nu există.'})

            # Verificăm regula pentru "compartimentare"
            if compartimentare is not None and category.group != 0:
                raise serializers.ValidationError({
                    'compartimentare': 'Câmpul "Compartimentare" nu este permis pentru această categorie.'
                })    
                
            # Verificăm regula pentru "zonare"
            if zonare is not None and category.group != 3:
                raise serializers.ValidationError({
                    'zonare': 'Câmpul "Zonare terenuri" nu este permis pentru această categorie.'
                })   
                
            # Verificăm regula pentru "numar_camere"
            if numar_camere is not None and category.group not in [0, 1, 2]:
                raise serializers.ValidationError({
                    'numar_camere': 'Câmpul "Număr camere" nu este permis pentru această categorie.'
                })  
                
            # Verificăm regula pentru "year_of_construction"
            if year_of_construction is not None and category.group == 3:
                raise serializers.ValidationError({
                    'year_of_construction': 'Câmpul "An construcție" nu este permis pentru această categorie.'
                })                
                
            # Verificăm regula pentru "structura"
            if structura is not None and category.group == 3:
                raise serializers.ValidationError({
                    'structura': 'Câmpul "Structura" nu este permis pentru această categorie.'
                })                   
                
        # Verificare imagini duplicate
        for i in range(1, 10):  # Iterează prin câmpurile foto
            photo_field = data.get(f"photo{i}")
            if photo_field:
                # Generează hash-ul imaginii
                hash_value = generate_hash(photo_field)
                hash_field = f"photo{i}_hash"

                # Verifică dacă există un alt obiect cu același hash
                filters = {hash_field: hash_value}
                if Listing.objects.filter(**filters).exclude(id=self.instance.id if self.instance else None).exists():
                    raise serializers.ValidationError({
                        f"photo{i}": f"Imaginea {i} există deja în sistem."
                    })                                                       

        return data
    
    def validate_suprafata_utila(self, value):
        # Verificăm dacă valoarea este pozitivă
        if value is not None and value <= 0:
            raise serializers.ValidationError("Suprafața utilă trebuie să fie mai mare decât 0.")
        
        # Adaugă alte validări dacă este cazul
        if value is not None and value > 10000000:  # Limita maximă teoretică (10 milioane de m²)
            raise serializers.ValidationError("Suprafața utilă este prea mare.")
        return value  
    
    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitudinea trebuie să fie între -90 și 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitudinea trebuie să fie între -180 și 180.")
        return value         
    
    def validate_year_of_construction(self, value):
        anul_curent = datetime.now().year

        # Verificare pentru exact 4 cifre
        if not (1000 <= value <= 9999):
            raise serializers.ValidationError("Anul construcției trebuie să aibă exact 4 cifre.")
        
        # Verificare pentru a nu depăși anul curent
        if value > anul_curent:
            raise serializers.ValidationError(f"Anul construcției nu poate fi mai mare decât anul curent ({anul_curent}).")
        
        return value         
    
    def update(self, instance, validated_data):
        title = validated_data.get('title', instance.title)
        county_id = validated_data.get('county_id', instance.county_id)
        city_id = validated_data.get('city_id', instance.city_id)
        
        # Rotunjim la 2 zecimale suprafata utila
        suprafata_utila = validated_data.get('suprafata_utila')
        if suprafata_utila is not None:
            validated_data['suprafata_utila'] = round(suprafata_utila, 2)           

        # Obține valori pentru county și city
        county = County.objects.filter(id=county_id).first() if county_id else instance.county
        city = City.objects.filter(id=city_id).first() if city_id else instance.city

        # Gestionare recalculare slug
        if 'title' in validated_data or 'county_id' in validated_data or 'city_id' in validated_data:
            if not county or not city:
                raise serializers.ValidationError("Județul și orașul trebuie să fie valide pentru recalcularea slug-ului.")
            
            user_hash = hashlib.md5(str(self.context['request'].user.id).encode()).hexdigest()[:6]
            slug_base = slugify(f"{title} {county.name} {city.name} {user_hash}")

            if Listing.objects.filter(slug=slug_base).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("Slug-ul recalculat există deja. Modificați titlul sau alte date.")
            validated_data['slug'] = slug_base

        # Gestionare tag-uri
        tag_ids = validated_data.pop('tag_ids', None)
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tag.set(tags)
            tag_list = ", ".join(tag.name for tag in tags)
        else:
            tag_list = ", ".join(tag.name for tag in instance.tag.all())

        # Obține valori pentru categoria și orașul curent
        category_id = validated_data.get('category_id', instance.category_id)
        category = Category.objects.filter(id=category_id).first() if category_id else instance.category

        category_name = category.name if category else instance.category.name
        city_name = city.name if city else instance.city.name

        # Construim meta_description cu compartimentare și zonare
        description_parts = [
            title,
            f"➤ {category_name}",
        ]

        # Verificăm dacă există caracteristici (compartimentare, zonare, tag-uri)
        features_added = False
        features = []

        # Adăugare compartimentare dacă există
        if instance.compartimentare is not None:
            compartimentare_text = instance.get_compartimentare_display()
            features.append(compartimentare_text.capitalize())
            features_added = True

        # Adăugare zonare dacă există
        if instance.zonare is not None:
            zonare_text = instance.get_zonare_display()
            features.append(zonare_text.capitalize())
            features_added = True
            
        # Adăugare număr camere, dacă există
        if instance.numar_camere is not None:
            numar_camere_text = instance.get_numar_camere_display()
            features.append(numar_camere_text)
            features_added = True            

        # Adăugare tag_list dacă există tag-uri
        if tag_list:
            features.append(tag_list)
            features_added = True

        # Adăugăm "➤ Caracteristici:" doar dacă există vreo caracteristică
        if features_added:
            description_parts.append(f"➤ Caracteristici: {', '.join(features)}")

        description_parts.append(f"➤ Anunț Imobiliar {city_name} {datetime.now().year}")

        # Setăm meta_title și meta_description
        instance.meta_title = f"{title} ➤ Anunț Imobiliar {city_name}"
        instance.meta_description = " ".join(description_parts)

        # Actualizăm câmpurile instanței
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance
    
class ListingDetailSerializer(serializers.ModelSerializer):
    county_name = serializers.CharField(source='county.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    neighborhood_name = serializers.CharField(source='neighborhood.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tag = TagSimpleSerializer(read_only=True, many=True)
    user = UserInfoSerializer(read_only=True)  # Include datele despre utilizatorul care a adăugat anunțul    
    
    class Meta:
        model = Listing
        fields = [
            'id',
            'title',
            'description',
            'price',
            'negociabil',
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
            'county_name',
            'city_name',
            'neighborhood_name',
            'category_name',
            'tag',
            'user',
        ]
    
 
class ReportSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all())

    class Meta:
        model = Report
        fields = [
            'id',
            'listing',
            'reporter_name',
            'reporter_email',
            'reason',
            'ip_address',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'status', 'ip_address']

    def validate_listing(self, value):
        # Verificăm dacă anunțul este activ
        if value.status != 1:  # 1 = "Active"
            raise serializers.ValidationError("Anunțul nu este activ.")
        return value

    def validate(self, data):
        # Validare: același IP nu poate raporta același anunț în ultimele 24 de ore
        ip_address = data.get('ip_address')
        listing = self.initial_data.get('listing')  # Folosim ID-ul setat în view

        if Report.objects.filter(listing=listing, ip_address=ip_address, created_at__gte=now() - timedelta(hours=24)).exists():
            raise serializers.ValidationError({'ip_address': 'Ai raportat deja acest anunț în ultimele 24 de ore.'})

        if not data.get('reason'):
            raise serializers.ValidationError({"reason": "Motivul raportului este obligatoriu."})

        return data

class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ['listing', 'text']

    def validate_listing(self, value):
        """
        Verificăm dacă anunțul (listing) aparține utilizatorului.
        """
        request = self.context['request']
        user = request.user

        if value.user != user: 
            raise serializers.ValidationError("Nu poți adăuga sugestii la un anunț care nu îți aparține.")
        
        return value
    
    def validate(self, attrs):
        """
        Verificăm dacă utilizatorul a trimis deja un număr limitat de sugestii în general.
        """
        user = self.context['request'].user

        # Verificăm câte sugestii a trimis utilizatorul
        if Suggestion.objects.filter(user=user).count() >= settings.SUGGESTION_LIMIT:
            raise serializers.ValidationError(f"Nu poți trimite mai mult de {settings.SUGGESTION_LIMIT} sugestii în general.")

        return attrs    
    
class ClaimRequestSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(write_only=True)

    class Meta:
        model = ClaimRequest
        fields = ['registration_number']

    def validate(self, attrs):
        user = self.context['request'].user
        registration_number = attrs.pop('registration_number')

        # Găsește compania pe baza numărului de înregistrare
        try:
            company = CompanyProfile.objects.get(registration_number=registration_number)
        except CompanyProfile.DoesNotExist:
            raise serializers.ValidationError("Nu există nicio companie cu acest număr de înregistrare.")

        # Verifică dacă utilizatorul este de tip 'agent'
        if user.account_type != 'agent':
            raise serializers.ValidationError("Doar agenții imobiliari pot revendica o companie.")

        # Verifică dacă există deja o cerere aprobată sau respinsă pentru această companie
        existing_request = ClaimRequest.objects.filter(user=user, company=company).exclude(status='pending').first()
        if existing_request:
            raise serializers.ValidationError(
                f"Nu poți face o nouă cerere pentru această companie. Statusul ultimei cereri: {existing_request.get_status_display()}."
            )

        # Verifică dacă există deja o cerere în așteptare pentru această companie
        if ClaimRequest.objects.filter(user=user, company=company, status='pending').exists():
            raise serializers.ValidationError("Există deja o cerere în așteptare pentru această companie.")

        attrs['company'] = company
        return attrs

    def create(self, validated_data):
        """Creează cererea de revendicare."""
        user = self.context['request'].user
        company = validated_data['company']
        return ClaimRequest.objects.create(user=user, company=company)
 



