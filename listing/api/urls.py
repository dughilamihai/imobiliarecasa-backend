from django.urls import path
from . import views
from .views import *

app_name = 'api'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('categorii-toate/', CategoryListAllAV.as_view(), name='category-list-all'),
    path('categorii/', CategoryListAV.as_view(), name='category-parent-list'), 
    path('categorie/<slug:slug>/', CategoryDetailAV.as_view(), name='category-detail'),    
    path('judete/', CountyListAV.as_view(), name='county-list'),  
    path('judet/<slug:slug>/', CountyDetailAV.as_view(), name='county-detail'),        
    path('creaza-cont/', UserRegistrationAPIView.as_view(), name='user-registration'), 
    path('user-details/', UserDetailsAPIView.as_view(), name='user-details'),              
    path('user-address/', UserAddressAPIView.as_view(), name='user-address'),
    path('company-profile/', CompanyProfileAPIView.as_view(), name='company-profile'), 
    path('claim-company/', ClaimCompanyView.as_view(), name='claim-company'), 
    path('claim-request/approve/<int:pk>/', ApproveClaimRequestView.as_view(), name='approve-claim'),
    path('claim-request/decline/<int:pk>/', DeclineClaimRequestView.as_view(), name='decline-claim'),             
    path('sterge-cont/', AccountDeletionView.as_view(), name='delete-account'),  
    path('send-confirmation-email/', SendEmailConfirmationToken.as_view(), name='send_email_confirmation_api_view'),  
    path('confirm-email/', confirm_email_view, name='confirm_email_view'),  
    path('schimba-parola/', ChangePasswordView.as_view(), name='change-password'),
    path('user-update/', UserUpdateAPIView.as_view(), name='user-update'),  
    path('tags/', TagListView.as_view(), name='tag-list'),             
    path('listings/', ListingAPIView.as_view(), name='listing-list'),
    path('listings/home/', HomeListingAPIView.as_view(), name='home-listings'),      
    path('listings/liked-listings/', LikedListingsAPIView.as_view(), name='liked_listings'),        
    path('listings/<slug:slug>/', ListingDetailAPIView.as_view(), name='listing-detail'), # Pentru VIEW
    path('listings/<uuid:uuid>/delete/', ListingDeleteAPIView.as_view(), name='listing-delete'),  # Pentru DELETE
    path('listings/<uuid:uuid>/update/', ListingUpdateAPIView.as_view(), name='listing-update'), # Pentru UPDATE 
    path('listings/<uuid:uuid>/toggle-activation/', ToggleListingActivationView.as_view(), name='toggle-listing-activation'), # user can toggle their listing 
    path('listings/<uuid:uuid>/similar/', SimilarListingsAPIView.as_view(), name='listing-similar'),     
    path('listings/<uuid:uuid>/toggle-like/', ToggleLikeAPIView.as_view(), name='toggle_like'), 
    path('reports/<uuid:uuid>/', ReportCreateAPIView.as_view(), name='report-create'), # Ruta pentru a crea un raport
    path('suggestions/', SuggestionCreateAPIView.as_view(), name='create-suggestion'),    
]