from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('listings/', views.listing_list, name='listing_list'),
    path('listings/<int:id>/', views.listing_detail, name='listing_detail'),
]