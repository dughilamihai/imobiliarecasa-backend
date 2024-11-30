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
    list_display = ['email', 'username', 'is_staff', 'is_superuser', 'get_user_type_display', 'last_login', 'first_name', 'last_name', 'email_verified', 'receive_email_status','created_at']
    search_fields = ("username", "email")
    list_filter = [('user_type', admin.ChoicesFieldListFilter)]    
    
    def get_user_type_display(self, obj):
        return dict(User.USER_TYPES)[obj.user_type]
    get_user_type_display.short_description = 'User Type' 
    
    @admin.display(description="Primește email")
    def receive_email_status(self, obj):
        return "DA" if obj.receive_email else "NU"       

    class Meta:
        model = User
        fields = '__all__' 

class EmailConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'user')

admin.site.register(EmailConfirmationToken, EmailConfirmationTokenAdmin)


