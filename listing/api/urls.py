from django.urls import path
from . import views
from .views import *

app_name = 'api'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('categorii-toate/', CategoryListAllAV.as_view(), name='category-list-all'),
    path('categorii/', CategoryListAV.as_view(), name='category-parent-list'), 
    path('categorii/<slug:slug>/', CategoryDetailAV.as_view(), name='category-detail'),    
    path('creaza-cont/', UserRegistrationAPIView.as_view(), name='user-registration'),          
    path('user-info/', UserDetailsAPIView.as_view(), name='user-details'), 
    path('user-address/', UserAddressAPIView.as_view(), name='user-address'),
    path('company-profile/', CompanyProfileAPIView.as_view(), name='company-profile'),        
    path('sterge-cont/', AccountDeletionView.as_view(), name='delete-account'),  
    path('send-confirmation-email/', SendEmailConfirmationToken.as_view(), name='send_email_confirmation_api_view'),  
    path('confirm-email/', confirm_email_view, name='confirm_email_view'),  
    path('schimba-parola/', ChangePasswordView.as_view(), name='change-password'),
    path('user-update/', UserUpdateAPIView.as_view(), name='user-update'),  
    path('tags/', TagListView.as_view(), name='tag-list'),             
    path('listings/', ListingAPIView.as_view(), name='listing-list'),
    path('listings/<slug:slug>/', ListingDetailAPIView.as_view(), name='listing-detail'), # Pentru VIEW
    path('listings/<uuid:uuid>/delete/', ListingDeleteAPIView.as_view(), name='listing-delete'),  # Pentru DELETE
    path('listings/<uuid:uuid>/update/', ListingUpdateAPIView.as_view(), name='listing-update'), # Pentru UPDATE  
    path('reports/<uuid:uuid>/', ReportCreateAPIView.as_view(), name='report-create'), # Ruta pentru a crea un raport
    path('suggestions/', SuggestionCreateAPIView.as_view(), name='create-suggestion'),    
]