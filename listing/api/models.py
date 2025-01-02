from django.db import models
from django.utils.text import slugify

# for resize images
from django_resized import ResizedImageField

# for mptt category
from mptt.models import MPTTModel, TreeForeignKey

# for user management
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import hashlib
from phonenumber_field.modelfields import PhoneNumberField

# for listings
from django_resized import ResizedImageField
from django_bleach.models import BleachField
from .constants import FLOOR_CHOICES

# for validation
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
class County(models.Model):
    # Câmpuri de bază
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    # Câmpuri pentru SEO și descriere
    meta_title = models.CharField(max_length=140, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # Câmp pentru data creării
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug din name, dacă slug-ul nu este specificat
        if not self.slug:
            self.slug = slugify(self.name)
        super(County, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"
        ordering = ['name']

class City(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # Relația One-to-Many cu County
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name="cities")
    
    meta_title = models.CharField(max_length=140, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.county.name}"

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ['name']
        
class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    # Relația One-to-Many cu City
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="neighborhoods")
    
    meta_title = models.CharField(max_length=140, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Neighborhood, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.city.name}"

    class Meta:
        verbose_name = "Neighborhood"
        verbose_name_plural = "Neighborhoods"
        ordering = ['name']   
        
class Category(MPTTModel):
    CATEGORY_GROUP_CHOICES = [
        (0, 'Apartamente'),
        (1, 'Birouri și Spații Comerciale'),
        (2, 'Case și Vile'),
        (3, 'Terenuri'),
        (4, 'Alte proprietăți'),
    ]    
    name = models.CharField(max_length=60, blank=True)   
    parent = TreeForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name='children')
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    short_name = models.CharField(max_length=80, blank=True)
    meta_title = models.CharField(max_length=90, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    custom_text = models.TextField(blank=True, null=True) 
    image = ResizedImageField(size=[160, 160], crop=['middle', 'center'], quality=80, upload_to='category_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    group = models.SmallIntegerField(
        choices=CATEGORY_GROUP_CHOICES,
        null=True,
        blank=True,
        db_index=True
    )    
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ('name',)

    class MPTTMeta:
        order_insertion_by = ['name']
        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)      
        
        
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Nu ati completat adresa de email")
        email = self.normalize_email(email)
        extra_fields['is_active'] = True  # Setăm explicit is_active
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class UserType(models.Model):
    type_name = models.CharField(max_length=20, unique=True)  # Ex: 'bronze', 'silver', 'gold'
    max_ads = models.PositiveIntegerField(default=0)  # Număr maxim de anunțuri permis
    background_color = models.CharField(max_length=7, default='#FFFFFF')  # Cod HEX pentru culoarea de fundal
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)  # Preț pe zi 

    def __str__(self):
        return self.type_name
    

class User(AbstractUser):
    ACCOUNT_TYPE_CHOICES = [
        ('person', 'Persoană Fizică'),
        ('company', 'Companie'),
        ('agent', 'Agent Imobiliar'),
    ] 
    email = models.EmailField(unique=True)    
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False) 
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='person')  
    username_hash = models.CharField(max_length=8, unique=True, blank=True, null=True)  
    profile_picture = ResizedImageField(size=[200, 200], force_format="WEBP", quality=80, upload_to='profile_pictures', null=True, blank=True)
    profile_picture_hash = models.CharField(max_length=64, blank=True, null=True, unique=True)
    company_logo = ResizedImageField(size=[240, 60], force_format="WEBP", quality=80, upload_to='company_logos', null=True, blank=True)
    company_logo_hash = models.CharField(max_length=64, blank=True, null=True, unique=True)    
    company = models.ForeignKey(
        'CompanyProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agents',
        help_text="Compania la care este asociat acest agent imobiliar (opțional)."
    )    
    email_verified = models.BooleanField(default=False)  
    receive_email = models.BooleanField(default=False)      
    first_name = models.CharField(max_length=60, blank=False, null=False)
    last_name = models.CharField(max_length=90, blank=False, null=False) 
    phone_number = PhoneNumberField(region="RO", unique=True)    
    phone_verified = models.BooleanField(default=False)  
    phone_verified_at = models.DateTimeField(null=True, blank=True)             
    hashed_ip_address = models.CharField(max_length=64, blank=True, null=True)
    has_accepted_tos = models.BooleanField(null=False, default=False)
    tos_accepted_timestamp = models.DateTimeField(null=True, blank=True)
    tos_accepted_ip = models.GenericIPAddressField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)         
    
    objects = UserManager()
    
    def verify_email(self):
        self.email_verified = True
        self.save()
        
    # Verifică numărul maxim de anunțuri permise
    def get_user_limit(self):
        if self.user_type:
            return self.user_type.max_ads
        return 0  # Dacă nu există UserType asociat
    
    def is_email_verified(self):
        return self.email_verified        
        
    def claim_company(self, company):
        if self.account_type != 'agent':
            raise ValidationError("Doar utilizatorii de tip 'Agent Imobiliar' pot face claim pentru o companie.")
        if company is None:
            raise ValidationError("Compania specificată nu este validă.")
        self.company = company  # Asociază agentul cu compania
        self.save()  # Salvează modificările              

    def save(self, *args, **kwargs):
        # Validare companie
        if self.company and self.account_type != 'agent':
            raise ValidationError("Doar utilizatorii de tip 'Agent Imobiliar' pot fi asociați cu o companie.")

        # Actualizarea timestamp-ului pentru acceptarea termenilor
        self.tos_accepted_timestamp = timezone.now()

        # Hash-ul adresei IP, dacă este prezentă
        if self.hashed_ip_address:
            hashed_ip = hashlib.sha256(self.hashed_ip_address.encode('utf-8')).hexdigest()
            self.hashed_ip_address = hashed_ip
            
        # Generare hash din username, doar dacă nu există deja
        if not self.username_hash:
            self.username_hash = hashlib.md5(self.username.encode()).hexdigest()[:8]            

        # Apelul metodei `save` a clasei părinte
        super().save(*args, **kwargs)  

    @classmethod
    def authenticate(cls, request, username=None, password=None, **kwargs):
        user = authenticate(request, username=username, password=password, **kwargs)
        if user and user.is_email_verified():
            return user
        elif user:
            # Handle unverified email
            raise ValidationError("Adresa de email nu a fost validata")
        return None


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, related_name="subscriptions")
    start_date = models.DateTimeField(default=now)  # Data începerii abonamentului
    end_date = models.DateTimeField(null=True, blank=True)  # Data expirării abonamentului, poate fi None pentru nelimitat
    
    # Câmp boolean care reflectă statusul activității abonamentului
    is_active_field = models.BooleanField(default=False, editable=False)

    def clean(self):
        # Verifică dacă end_date este înaintea sau egal cu start_date
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError("Data de expirare nu poate fi înainte sau egală cu data de început.")

    def save(self, *args, **kwargs):
        # Rulează validările personalizate
        self.full_clean()

        # Actualizează câmpul is_active_field în funcție de data expirării
        if self.end_date is None:
            self.is_active_field = True  # Abonamentul este activ dacă end_date este None
        else:
            self.is_active_field = self.end_date >= now()  # Compară cu data curentă dacă end_date nu este None

        # Salvează obiectul
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.user_type.type_name} (expiră la {self.end_date})"

    def remaining_days(self):
        """Returnează numărul de zile rămase din abonament."""
        if self.end_date:
            delta = self.end_date - now()
            return max(delta.days, 0)
        return None

class EmailConfirmationToken(models.Model):
        id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False)
        created_at = models.DateTimeField(auto_now_add=True)
        user = models.ForeignKey(User, on_delete=models.CASCADE)

        def __str__(self):
            return str(self.id)  # Convert UUID to string               

class CompanyProfile(models.Model):
    COMPANY_TYPE_CHOICES = (
        (0, 'Dezvoltator / Constructor'),
        (1, 'Agenție Imobiliară'),
        (2, 'Broker Ipotecar'),
        (3, 'Instituție Financiară'),
        (4, 'Alt Tip'),        
    )    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    registration_number = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    company_type = models.IntegerField(
        choices=COMPANY_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="Tipul companiei. Poate fi lăsat necompletat."
    )    
    
    def clean(self):
        # Validare: verifică dacă utilizatorul este de tip 'company'
        if self.user.account_type != 'company':
            raise ValidationError({"user": "Profilul de companie poate fi asociat doar unui utilizator de tip 'companie'."})

    def save(self, *args, **kwargs):
        # Apelăm `clean` pentru a efectua validarea
        self.clean()
        # Apelul metodei `save` a clasei părinte
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name
    
class ClaimRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'În așteptare'),
        ('approved', 'Aprobat'),
        ('rejected', 'Respins'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='claim_requests')
    company = models.ForeignKey('CompanyProfile', on_delete=models.CASCADE, related_name='claim_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self):
        """Aprobă cererea și asociază compania cu utilizatorul."""
        self.status = 'approved'
        self.company.user = self.user
        self.company.save()
        self.save()

    def reject(self):
        """Respinge cererea."""
        self.status = 'rejected'
        self.save()

class Address(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)   
    strada = models.CharField(max_length=255, null=False, blank=False)
    strada_numar = models.CharField(
        max_length=10, 
        null=False, 
        blank=False,
        validators=[RegexValidator(r'^\d+$', 'Numărul străzii trebuie să fie un număr.')]  # Validare pentru numărul străzii
    )    
    oras = models.CharField(max_length=255, null=False, blank=False)
    judet = models.CharField(max_length=255, null=False, blank=False)
    cod_postal = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        validators=[RegexValidator(r'^\d{6}$', 'Codul poștal trebuie să fie format din 6 cifre.')]  # Validare pentru codul poștal
    )
    tara = models.CharField(max_length=255, null=False, blank=False)
    
    def __str__(self):
        return f"Adresa {self.user.username} - {self.strada} {self.strada_numar}, {self.oras}, {self.judet}, {self.tara}"  
    
      
class Tag(models.Model):
    STATUS = (
        (0, 'Dezaprobat'),
        (1, 'Activ'),
        (2, 'Așteptare'),
    ) 
    name = models.CharField(max_length=30, blank=False, unique=True)
    icon_name = models.CharField(max_length=50, blank=True, null=True)    
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    status = models.SmallIntegerField(default=2, db_index=True, choices=STATUS)
    meta_title = models.CharField(max_length=90, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)  
    categories = models.ManyToManyField(Category, related_name="tags")      
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)  
        
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')  # Un utilizator poate da like o singură dată la un anunț            

class Listing(models.Model):
    STATUS_CHOICES = [
        (0, 'Inactive'),
        (1, 'Active'),
        (2, 'Rejected'),
    ]
    CURRENCY_CHOICES = [
        (0, 'Lei'),
        (1, 'EUR'),
    ]
    COMPARTIMENTARE_CHOICES = [
        (0, 'Decomandat'),
        (1, 'Semidecomandat'),
        (2, 'Nedecomandat'),
        (3, 'Circular'),
    ]
    ZONARE_CHOICES = [
        (0, 'intravilan'),
        (1, 'extravilan'),
    ] 
    NUMAR_CAMERE_CHOICES = [
        (1, '1 Cameră'),
        (2, '2 Camere'),
        (3, '3 Camere'),
        (4, '4 Camere'),
        (5, '5+ Camere'),
    ]  
    STRUCTURA_CHOICES = [
        (0, 'Caramida'),
        (1, 'Beton'),
        (2, 'BCA'),
        (3, 'Placi'),
        (4, 'Lemn'),
        (5, 'Metal'),
        (6, 'Altele'),
    ]        
    
    # Câmpuri de bază
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False)       
    title = models.CharField(max_length=200, db_index=True)
    description = BleachField()
    price = models.PositiveIntegerField(
        help_text="Prețul trebuie să fie un număr întreg și pozitiv."
    )
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=1)
    negociabil = models.BooleanField(default=False)    
    suprafata_utila = models.FloatField(
        "Suprafață utilă",
        null=True,
        blank=True
    )     
    is_owner = models.BooleanField(
        default=False,
        help_text="Indică dacă utilizatorul a fost validat ca fiind proprietar al anunțului."
    )      
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0, db_index=True) 
    is_active_by_user = models.BooleanField(default=True)  # Default activ   
    buyer_commission = models.DecimalField(
        max_digits=4,  # 2 cifre pentru partea întreagă și 2 pentru partea zecimală
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('50.00'))  # Maxim 50.00%
        ],
        null=True,
        blank=True,
        help_text="Introduceți procentul comisionului pentru cumpărător (maxim 50%)."
    )
    
    # Relații
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_listings')
    tag = models.ManyToManyField('Tag', related_name='listings', blank=True)    
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE,
        related_name='county_listings',
        null=False,  # Câmp obligatoriu
        blank=False  # Împiedică formularele să accepte valori goale
    )
    neighborhood = models.ForeignKey(
        Neighborhood,
        on_delete=models.SET_NULL,
        related_name='neighborhood_listings',     
        null=True,
        blank=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='city_listings',
        null=False,
        blank=False
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='category_listings',
        null=False,
        blank=False
    )    

    # Imagini
    photo1 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings')   
    photo2 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True) 
    photo3 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)    
    photo4 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)    
    photo5 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)    
    photo6 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)   
    photo7 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)  
    photo8 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)   
    photo9 = ResizedImageField(size=[800, 600], force_format="WEBP", quality=80, upload_to='listings', blank=True, null=True)     
    # Thumbnail-ul
    thumbnail = ResizedImageField(
        size=[300, 240],  # Dimensiuni pentru thumbnail
        force_format="WEBP", 
        quality=80, 
        upload_to='thumbs',  # Directorul pentru thumbnail-uri
        blank=True, 
        null=True
    )        

    # Link pentru videoclip
    video_url = models.URLField(max_length=500, blank=True, null=True)

    # Locație
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Date și statistici
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    valability_end_date = models.DateField(
        blank=True,
        null=True,
        help_text="Data până la care anunțul este valid."
    )
    views_count = models.BigIntegerField(default=0)
    like_count = models.IntegerField(default=0)
    
    # Machine learning statistics
    is_good_deal = models.BooleanField(null=True)  # Etichetă (pont/norm)
    is_manual_label = models.BooleanField(default=False)  # Etichetare manuală    
    
    # Campuri aditionale
    year_of_construction = models.IntegerField(null=True, blank=True, help_text="Year of construction")    
    compartimentare = models.SmallIntegerField(
        choices=COMPARTIMENTARE_CHOICES,
        null=True,
        blank=True,
        db_index=True
    )
    zonare = models.SmallIntegerField(
        choices=ZONARE_CHOICES, 
        null=True, 
        blank=True,
        db_index=True,        
        help_text="Zonarea poate fi intravilan, extravilan sau necompletată."
    )  
    numar_camere = models.IntegerField(
        choices=NUMAR_CAMERE_CHOICES, 
        default=1,
        null=True, 
        blank=True,
        db_index=True,  
        help_text="Se aplica doar pentru apartamente, case, vile, spatii comerciale."                
        )   
    structura = models.IntegerField(
        choices=STRUCTURA_CHOICES,
        null=True,
        blank=True,
        db_index=True
    )     
    floor = models.SmallIntegerField(choices=FLOOR_CHOICES, db_index=True, null=True, blank=True)    
    
    # SEO
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    meta_title = models.CharField(max_length=140, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.valability_end_date:
            # Extrage doar data, fără ora
            self.valability_end_date = (timezone.now() + timedelta(days=30)).date()
            
        if not self.slug:  # Dacă slug-ul nu este deja setat
            # Generează un hash unic pe baza utilizatorului
            user_hash = hashlib.md5(str(self.user.id).encode()).hexdigest()[:6]
            # Creează baza slug-ului
            slug_base = slugify(f"{self.title} {self.county.name} {self.city.name} {user_hash}")
            self.slug = slug_base                         
                        
        super(Listing, self).save(*args, **kwargs)  
        
    # Metodă pentru gestionarea like-urilor
    def toggle_like(self, user):
        # Verifică dacă utilizatorul a dat deja like
        like, created = Like.objects.get_or_create(user=user, listing=self)

        if not created:
            # Dacă like-ul există deja, îl eliminăm
            like.delete()
            self.like_count -= 1  # Scădem 1 din like_count
        else:
            # Dacă like-ul nu există, îl adăugăm
            self.like_count += 1  # Adăugăm 1 la like_count

        # Salvează actualizarea în baza de date
        self.save(update_fields=['like_count'])
        
        return created  # Returnează True dacă like-ul a fost adăugat, False dacă a fost eliminat     
      
    def __str__(self):
        return f"{self.title} - {self.price} {dict(self.CURRENCY_CHOICES).get(self.currency)}"

    class Meta:
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        ordering = ['-created_date']
        
class ImageHash(models.Model):
    hash_value = models.CharField(max_length=64, unique=True)
    listing_uuid = models.UUIDField(null=True, blank=True)  # Folosind UUID-ul pentru asocierea cu listing
    photo_name = models.CharField(max_length=20, null=True, blank=True)     
    created_at = models.DateTimeField(auto_now_add=True)         
        
class Report(models.Model):
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    DISMISSED = 'dismissed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REVIEWED, 'Reviewed'),
        (DISMISSED, 'Dismissed'),
    ]

    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='reports')
    reporter_name = models.CharField(max_length=255)
    reporter_email = models.EmailField()
    reason = BleachField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Adaugă câmp pentru IP
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)  # Câmp pentru status
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.listing.title} by {self.reporter_name}"    
    
class Suggestion(models.Model):
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='suggestions', 
        null=True,  # Permite valoarea NULL în baza de date
        blank=True  # Permite câmpul să fie lăsat gol în formulare
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = BleachField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        listing_title = self.listing.title if self.listing else 'No Listing'
        user_name = self.user.username if self.user else 'Admin'
        return f"Suggestion for {listing_title} by {user_name}"   
    
class ManagementCommand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name       
    
