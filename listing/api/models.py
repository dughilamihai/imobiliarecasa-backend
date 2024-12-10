from django.db import models
from django.utils.text import slugify

# for resize images
from django_resized import ResizedImageField

# for mptt category
from mptt.models import MPTTModel, TreeForeignKey

# for user management
from django.contrib.auth.models import AbstractUser, BaseUserManager
from uuid import uuid4
from django.core.validators import MinLengthValidator
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
import phonenumbers
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta
import hashlib

# for listings
from django_resized import ResizedImageField
from django_bleach.models import BleachField

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
            raise ValueError(_('Nu ati completat adresa de email'))
        email = self.normalize_email(email)
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
    ACCOUNT_TYPE_CHOICES = [ ('person', 'Persoană Fizică'), ('company', 'Companie'), ]    
    email = models.EmailField(unique=True)    
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='person')    
    email_verified = models.BooleanField(default=False)  
    receive_email = models.BooleanField(default=False)      
    first_name = models.CharField(max_length=60, blank=False, null=False)
    last_name = models.CharField(max_length=90, blank=False, null=False) 
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    phone_verified = models.BooleanField(default=False)  
    phone_verified_at = models.DateTimeField(null=True, blank=True)             
    hashed_ip_address = models.CharField(max_length=64, blank=True, null=True)
    has_accepted_tos = models.BooleanField(null=False, default=False)
    tos_accepted_timestamp = models.DateTimeField(null=True, blank=True)
    tos_accepted_ip = models.GenericIPAddressField(null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True)         
    
    def verify_email(self):
        self.email_verified = True
        self.save()
        
    def get_user_limit(self):
        return self.USER_LIMITS.get(self.user_type, 0)    

    def is_email_verified(self):
        return self.email_verified
    
    def clean_phone_number(self):
            if self.phone_number:
                try:
                    parsed_number = phonenumbers.parse(self.phone_number, "RO")  # RO pentru România
                    if not phonenumbers.is_valid_number(parsed_number):
                        raise ValidationError("Numărul de telefon nu este valid.")
                    # Salvează numărul în format internațional
                    self.phone_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                except phonenumbers.NumberParseException:
                    raise ValidationError("Numărul de telefon nu poate fi procesat.")

    def save(self, *args, **kwargs):
        # 1. Validarea și normalizarea numărului de telefon
        self.clean_phone_number()

        # 2. Actualizarea timestamp-ului pentru acceptarea termenilor
        self.tos_accepted_timestamp = timezone.now()

        # 3. Hash-ul adresei IP, dacă este prezentă
        if self.hashed_ip_address:
            hashed_ip = hashlib.sha256(self.hashed_ip_address.encode('utf-8')).hexdigest()
            self.hashed_ip_address = hashed_ip

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    registration_number = models.CharField(max_length=255, unique=True)
    company_name = models.CharField(max_length=255)
    website = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    facebook_url = models.URLField(null=True, blank=True)
    
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
    
from django.core.validators import RegexValidator

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
    
    # Câmpuri de bază
    title = models.CharField(max_length=200, db_index=True)
    description = BleachField()
    price = models.PositiveIntegerField(
        help_text="Prețul trebuie să fie un număr întreg și pozitiv."
    )
    currency = models.SmallIntegerField(choices=CURRENCY_CHOICES, default=0)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0, db_index=True)
    
    # Relații
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_listings')
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
    
    # SEO
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    meta_title = models.CharField(max_length=140, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.valability_end_date:
            # Extrage doar data, fără ora
            self.valability_end_date = (timezone.now() + timedelta(days=30)).date()
        super(Listing, self).save(*args, **kwargs)    
    
    def __str__(self):
        return f"{self.title} - {self.price} {dict(self.CURRENCY_CHOICES).get(self.currency)}"

    class Meta:
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        ordering = ['-created_date']
        
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
    reason = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Adaugă câmp pentru IP
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)  # Câmp pentru status
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report for {self.listing.title} by {self.reporter_name}"        
    
