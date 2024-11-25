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
import hashlib

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

class User(AbstractUser):
    USER_TYPES = {
        'bronze': 3,
        'silver': 20,
        'gold': 50,
    }
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPES,
        default='bronze'
    ) 
    email = models.EmailField(unique=True)    
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False)
    email_verified = models.BooleanField(default=False)  
    receive_email = models.BooleanField(default=False)      
    first_name = models.CharField(max_length=60, blank=False, null=False, validators=[MinLengthValidator(3)])
    last_name = models.CharField(max_length=90, blank=False, null=False, validators=[MinLengthValidator(3)]) 
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    phone_verified = models.BooleanField(default=False)       
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


class EmailConfirmationToken(models.Model):
        id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4, editable=False)
        created_at = models.DateTimeField(auto_now_add=True)
        user = models.ForeignKey(User, on_delete=models.CASCADE)

        def __str__(self):
            return str(self.id)  # Convert UUID to string               

