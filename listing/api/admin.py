# Register your models here.
from django.contrib import admin
from .models import *

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'date_created')
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)
    prepopulated_fields = {"slug": ("name",)}
    
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'is_staff', 'is_superuser', 'get_user_type_display', 'last_login', 'first_name', 'last_name', 'email_verified', 'receive_email_status', 'is_active', 'get_account_type', 'get_company_name', 'created_at']
    search_fields = ("username", "email")
    list_filter = ['subscription__user_type', 'is_staff']   
      
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
    list_display = ['user', 'company_name', 'registration_number', 'website']
    search_fields = ['company_name', 'registration_number']    
    
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

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    # Afișează UUID-ul, alături de alte câmpuri
    list_display = ('id', 'title', 'status', 'county', 'city', 'neighborhood', 'expired', 'username')  # Afișează UUID-ul
    list_filter = ('city', 'county', 'tag__name')  # Permite filtrarea după city, county și tags
    search_fields = ('title', 'county__name', 'city__name', 'id')  # Permite căutarea după UUID (id)
    filter_horizontal = ('tag',)  # Permite selecția etichetelor într-un mod intuitiv    

    def expired(self, obj):
        return obj.valability_end_date and obj.valability_end_date < timezone.now().date()

    expired.boolean = True  # Afișează un semn de bifare sau un X în loc de True/False
    
    # Metodă pentru a afișa username-ul utilizatorului
    def username(self, obj):
        return obj.user.username  # Afișează username-ul utilizatorului

    username.short_description = 'Username'  # Etichetă pentru coloană     

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


