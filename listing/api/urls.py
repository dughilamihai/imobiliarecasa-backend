from django.urls import path
from . import views
from .views import APIRootView, CategoryListAllAV, CategoryListAV

app_name = 'api'

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('categorii-toate/', CategoryListAllAV.as_view(), name='category-list-all'),
    path('categorii/', CategoryListAV.as_view(), name='category-parent-list'),    
    # path('listings/', views.listing_list, name='listing_list'),
    # path('listings/<int:id>/', views.listing_detail, name='listing_detail'),
]