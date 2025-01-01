# Register your models here.
from django.contrib import admin
from .models import *

# for running commands
from django.core.management import call_command
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.contrib.admin import SimpleListFilter

class CompanyTypeFilter(SimpleListFilter):
    title = 'Tip companie'
    parameter_name = 'company_type'

    def lookups(self, request, model_admin):
        return CompanyProfile.COMPANY_TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(company_profile__company_type=self.value())
        return queryset

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_created')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'date_created')
    search_fields = ('name', 'county__name')
    list_filter = ('county',)
    prepopulated_fields = {"slug": ("name",)} 
    
@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'date_created')
    search_fields = ('name', 'city__name')
    list_filter = ('city',)
    prepopulated_fields = {"slug": ("name",)}    

from django.contrib import admin
from .models import Category

# Filtru personalizat pentru câmpul group
class GroupFilter(admin.SimpleListFilter):
    title = 'Grup'  # Nume afișat în interfață
    parameter_name = 'group'  # Parametru în URL

    def lookups(self, request, model_admin):
        # Returnează opțiunile de filtrare din CATEGORY_GROUP_CHOICES
        return Category.CATEGORY_GROUP_CHOICES

    def queryset(self, request, queryset):
        # Filtrează categoriile pe baza valorii selectate
        if self.value():
            return queryset.filter(group=self.value())
        return queryset

# Admin pentru Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'get_group_name', 'date_created')  # Afișează numele grupului
    search_fields = ('name', 'parent__name')
    list_filter = ('parent', GroupFilter)  # Adaugă filtrul personalizat
    prepopulated_fields = {"slug": ("name",)}

    def get_group_name(self, obj):
        # Returnează numele grupului
        return dict(Category.CATEGORY_GROUP_CHOICES).get(obj.group, 'Nedefinit')
    get_group_name.short_description = "Grup"  # Nume afișat în admin

    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_staff', 'is_superuser', 'get_user_type_display', 'last_login', 'first_name', 'last_name', 'email_verified', 'receive_email_status', 'is_active', 'get_account_type', 'get_company_name', 'created_at']
    search_fields = ("username", "email")
    list_filter = ['subscription__user_type', 'is_staff', CompanyTypeFilter, 'account_type']   
      
    # Afișează user_type
    def get_user_type_display(self, obj):
        return obj.subscription.user_type.type_name if hasattr(obj, 'subscription') else 'No Subscription'
    get_user_type_display.short_description = 'User Type'

    # Afișează detalii despre subscription
    def get_subscription_details(self, obj):
        if hasattr(obj, 'subscription'):
            return f"Start: {obj.subscription.start_date} - Expire: {obj.subscription.end_date} - Active: {obj.subscription.is_active()}"
        return 'No Subscription'
    get_subscription_details.short_description = 'Subscription Details'
    
    @admin.display(description="Primește email")
    def receive_email_status(self, obj):
        return "DA" if obj.receive_email else "NU"   
    
    def get_account_type(self, obj):
        """
        Returnează tipul utilizacontuluitorului: Persoană Fizică sau Companie.
        """
        return dict(User.ACCOUNT_TYPE_CHOICES).get(obj.account_type, "N/A")

    get_account_type.short_description = "Tipul contului"

    def get_company_name(self, obj):
        """
        Returnează numele companiei dacă utilizatorul este de tip companie.
        """
        if obj.account_type == 'company' and hasattr(obj, 'company_profile'):          
            return obj.company_profile.company_name
        return "-"
    
    get_company_name.short_description = "Nume Companie"        

    class Meta:
        model = User
        fields = '__all__' 
        
@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'max_ads', 'background_color', 'price_per_day')
    search_fields = ('type_name',)   
    
@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'start_date', 'end_date', 'is_active_field')
    search_fields = ('user__username', 'user__email')
    list_filter = ('user_type', 'is_active_field')  # Folosește câmpul calculat pentru filtrare   
    
@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'registration_number', 'website', 'get_company_type']
    search_fields = ['company_name', 'registration_number'] 
    list_filter = ['company_type']     
    
    # Metodă pentru a afișa numele tipului de companie
    def get_company_type(self, obj):
        return obj.get_company_type_display()

    get_company_type.short_description = 'Tip Companie'       
    
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'strada', 'strada_numar', 'oras', 'judet', 'cod_postal', 'tara')
    search_fields = ('user__email', 'oras', 'judet', 'tara')     

class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'user')

admin.site.register(EmailConfirmationToken, EmailConfirmationTokenAdmin)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'slug', 'date_created')
    list_filter = ('status',)
    search_fields = ('name', 'slug')
    
@admin.register(ImageHash)
class ImageHashAdmin(admin.ModelAdmin):
    list_display = ('hash_value', 'listing_id', 'photo_name', 'created_at')  # Afișează Listing ID în loc de Listing Name
    search_fields = ('hash_value', 'photo_name', 'listing_uuid')  # Permite căutarea și după UUID-ul listingului
    
    # Metodă pentru afișarea ID-ului listingului
    def listing_id(self, obj):
        if obj.listing_uuid:
            listing = get_object_or_404(Listing, id=obj.listing_uuid)
            return listing.id  # Returnează ID-ul Listing-ului
        return 'N/A'  # Dacă nu există listing_uuid
    listing_id.short_description = 'Listing ID'  # Eticheta pentru coloana

    # Metodă pentru afișarea numelui pozei
    def photo_name(self, obj):
        return obj.photo_name if obj.photo_name else 'N/A'
    photo_name.short_description = 'Photo Name'
    
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    # Afișează UUID-ul, alături de alte câmpuri
    list_display = ('id', 'title', 'status', 'county', 'city', 'neighborhood', 'category__name', 'expired', 'username', 'thumbnail_preview')  # Afișează UUID-ul
    list_filter = ('city', 'county', 'tag__name', 'category__name')  # Permite filtrarea după city, county și tags
    search_fields = ('title', 'county__name', 'city__name', 'id')  # Permite căutarea după UUID (id)
    filter_horizontal = ('tag',)  # Permite selecția etichetelor într-un mod intuitiv    

    def expired(self, obj):
        return obj.valability_end_date and obj.valability_end_date < timezone.now().date()

    expired.boolean = True  # Afișează un semn de bifare sau un X în loc de True/False
    
    # Metodă pentru a afișa username-ul utilizatorului
    def username(self, obj):
        return obj.user.username  # Afișează username-ul utilizatorului

    username.short_description = 'Username'  # Etichetă pentru coloană    
    
        # Metodă pentru a afișa category_name
    def category_name(self, obj):
        return obj.category.name  # Afișează numele categoriei

    category_name.short_description = 'Category Name'  # Etichetă pentru coloană 
    
   # Funcție pentru a afișa thumbnail-ul redimensionat
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="100" height="80" style="object-fit: cover;" />', 
                obj.thumbnail.url
            )
        return "No Image"
    thumbnail_preview.short_description = 'Thumbnail'    

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    # Afișează UUID-ul asociat raportului
    list_display = ('listing', 'listing_id', 'reporter_name', 'reporter_email', 'status', 'ip_address', 'created_at')  # Afișează listingul și UUID-ul
    list_filter = ('status', 'created_at')  # Permite filtrarea după status și dată
    search_fields = ('reporter_name', 'reporter_email', 'reason', 'listing__title', 'listing__id')  # Permite căutarea după UUID-ul anunțului
    readonly_fields = ('ip_address', 'created_at')  # Câmpuri doar pentru citire
    list_editable = ('status',)  # Permite editarea statusului direct din listă
    ordering = ('-created_at',)  # Ordonează după cele mai recente rapoarte

    def has_add_permission(self, request):  # Dezactivează adăugarea manuală a rapoartelor
        return False

    # Metodă pentru a adăuga UUID-ul anunțului în lista de Admin
    def listing_id(self, obj):
        return obj.listing.id  # Afișează UUID-ul asociat raportului

    listing_id.short_description = 'Listing UUID'  # Etichetă pentru UUID
    
@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('listing', 'user', 'text', 'created_at')
    list_filter = ('created_at', 'user')

    def save_model(self, request, obj, form, change):
        if not obj.user:
            obj.user = request.user  # Setează utilizatorul curent, dacă nu este setat
        super().save_model(request, obj, form, change)
        
@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'status', 'created_at', 'updated_at')  # Afișează câmpurile dorite în listă
    list_filter = ('company', 'status')  # Filtrează după companie și status
    search_fields = ('user__email', 'company__company_name')  # Permite căutarea după email și numele companiei
    ordering = ('-created_at',)  # Ordine descrescătoare după data creării        
        
class ManagementCommandAdmin(admin.ModelAdmin):
    list_display = ['name', 'run_command']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clear-cache/', self.admin_site.admin_view(self.clear_cache), name='clear-cache'),
        ]
        return custom_urls + urls

    def run_command(self, obj):
        if obj.name == 'clear_cache':
            return format_html('<a class="button" href="{}">Clear Cache</a>', reverse('admin:clear-cache'))
        else:
            return "No command linked"

    def clear_cache(self, request):
        call_command('clear_cache')
        self.message_user(request, "Cache cleared successfully.")
        return HttpResponseRedirect(reverse('admin:api_managementcommand_changelist'))

    run_command.short_description = 'Actions'
    run_command.allow_tags = True

admin.site.register(ManagementCommand, ManagementCommandAdmin)        
    


