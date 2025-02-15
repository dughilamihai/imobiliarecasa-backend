"""
URL configuration for listing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import CustomTokenObtainPairView, PasswordResetRequestView, PasswordResetConfirmView

# for static files
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)
# from rest_framework_simplejwt.token_blacklist.views import TokenBlacklistView

urlpatterns = [
    path('mikeadmin/', admin.site.urls),  # Custom admin URL     
    path('api/', include('api.urls')),
    # Rute pentru autentificare JWT
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login și obținere tokenuri
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token
    path('api/logout/', TokenBlacklistView.as_view(), name='token_blacklist'),  # Logout (blacklist token)
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Verificare token (opțional)    
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/password-reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)