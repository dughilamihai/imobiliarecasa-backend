from django.db import models
from django.utils.text import slugify

# for resize images
from django_resized import ResizedImageField

# for mptt category
from mptt.models import MPTTModel, TreeForeignKey

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
