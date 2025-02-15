from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
# send confirmation email after user sign up
from .utils import send_confirmation_email, get_similar_listings

from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# for login
from rest_framework_simplejwt.views import TokenObtainPairView
# for change password
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

# for filtering
from django_filters import rest_framework as filters
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .constants import FLOOR_CHOICES

# for pagination
from rest_framework.pagination import PageNumberPagination

# for caching
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# for listing
# every user will be able to see all the listings, but only logged-in users will be able to add, change, or delete objects.
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# for sending emails
from django.core.mail import send_mail

# for user reset password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import get_template
from django.urls import reverse

# for throttling
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

import logging
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)

# Extrage valoarea TIMEOUT din configurația de cache
CACHE_TIMEOUT = settings.CACHES['default']['TIMEOUT']


class APIRootView(APIView):
    """
    Root view for the API
    """
    permission_classes = [AllowAny]  # Permite accesul fără autentificare

    def get(self, request):
        return Response({
            "message": "Bine ați venit la API-ul site-ului de imobiliare. Utilizați rutele disponibile pentru a accesa funcționalitățile."
        })

class CategoryListAllAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Obține toate categoriile care nu sunt incluse ca subcategorii
        categories = Category.objects.filter(parent__isnull=True)
        
        # Serializare cu includerea relației parent-children
        serializer = NestedCategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryListAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        parent_categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(parent_categories, many=True)
        return Response(serializer.data)
    
class CategoryDetailAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug=None, *args, **kwargs):
        try:
            # Obține categoria pe baza slug-ului
            category = Category.objects.prefetch_related('tags', 'children').get(slug=slug)
            serializer = CategoryDetailSerializer(category)
            return Response(serializer.data, status=200)
        except Category.DoesNotExist:
            return Response({"detail": "Categoria nu a fost găsită."}, status=404)
 
class CountyListAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        counties = County.objects.all()
        serializer = CountySerializer(counties, many=True)
        return Response(serializer.data)    
    
class CountyDetailAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug=None, *args, **kwargs):
        try:
            # Obține județul pe baza slug-ului
            county = County.objects.get(slug=slug)
            serializer = CountySerializer(county)
            return Response(serializer.data, status=200)
        except County.DoesNotExist:
            # Răspuns personalizat pentru 404
            return Response({"detail": "Județul nu a fost găsit."}, status=404)   
        
class CityListByCountyAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            # Găsește județul după slug
            county = County.objects.get(slug=slug)
            
            # Obține toate localitățile asociate cu județul
            cities = county.cities.all()

            # Serializare date
            serializer = CitySerializer(cities, many=True)
            return Response(serializer.data)
        except County.DoesNotExist:
            return Response({"detail": "Orașul nu a fost găsit."}, status=404)   

class CityDetailAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request, city_slug=None, county_slug=None, *args, **kwargs):
        try:
            # Obține orașul pe baza slug-urilor
            city = City.objects.get(slug=city_slug, county__slug=county_slug)
            serializer = CitySerializer(city)
            return Response(serializer.data, status=200)
        except City.DoesNotExist:
            # Răspuns personalizat pentru 404
            return Response({"detail": "Orașul nu a fost găsit."}, status=404)

          
    
# register user        
class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated requests
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
      
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Create an email confirmation token for the newly registered user
            token = EmailConfirmationToken.objects.create(user=user)

            # Send the confirmation email with the token to the user
            send_confirmation_email(email=user.email, token_id=token.pk, user_id=user.pk)

            # Return success response
            return Response({'message': 'Utilizatorul s-a înregistrat cu succes. Vă rugăm să vă verificați e-mailul pentru a vă confirma contul.'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      
    
# confirm email address for unlogged users
class SendEmailConfirmationToken(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated requests

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # Find the user based on the provided email address
        user = User.objects.filter(email=email).first()

        # Check if the user exists and proceed accordingly
        if user:
            # Check if the user's email is already verified
            if user.email_verified:
                # Return an error message in Romanian
                return Response({'error': 'Adresa de email este deja verificată'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the number of existing confirmation emails for the user
            existing_confirmations = EmailConfirmationToken.objects.filter(user=user).count()       

            # Check if the user has reached the maximum number of confirmation emails
            if existing_confirmations >= settings.MAX_CONFIRMATION_EMAILS:
                return Response({'error': 'Numărul maxim de emailuri de confirmare a fost atins'}, status=status.HTTP_400_BAD_REQUEST)

            # Create an email confirmation token for the user
            token = EmailConfirmationToken.objects.create(user=user)

            # Send the confirmation email with the token to the user
            send_confirmation_email(email=user.email, token_id=token.pk, user_id=user.pk)

        # Return a generic success message in Romanian
        return Response({'message': 'Veti primi un email de confirmare pentru a valida contul'}, status=status.HTTP_200_OK) 
    
# for confirmation email send to user after registration    
def confirm_email_view(request):
    token_id = request.GET.get('token_id', None)
    try:
        token = EmailConfirmationToken.objects.get(pk = token_id)
        user = token.user
        user.is_email_confirmed = True
        user.save()
        data = {'is_email_confirmed': True}
        return render(request, template_name='confirm_email_view.html', context=data)  
    except EmailConfirmationToken.DoesNotExist:
        data = {'is_email_confirmed': False}
        return render(request, template_name='confirm_email_view.html', context=data)        
    
 
# for logging
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# user delete account
class AccountDeletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AccountDeletionSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            # Check if the provided password is correct
            if not authenticate(username=user.username, password=serializer.validated_data['password']):
                return Response({'message': 'Parola nu este corectă'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Perform account deletion logic here
                user.delete()
                logger.info(f'User {user.username} ({user.email}) deleted their account.')
                return Response({'message': 'Contul a fost șters cu succes.'}, status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                logger.error(f"Error deleting account for user {user.username}: {str(e)}")
                return Response({'message': 'A apărut o eroare la ștergerea contului.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
        
class UserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)              
    
class UserUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Detaliile utilizatorului au fost actualizate cu succes.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        # Validare date
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # Verifică dacă refresh token-ul este valid înainte de a continua cu schimbarea parolei
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                # Validare refresh token
                token = RefreshToken(refresh_token)
                # Dacă token-ul este valid, îl putem lăsa să continue și schimbăm parola
            except Exception as e:
                return Response({
                    'message': 'Token-ul refresh nu este valid sau a expirat.',
                    'error': str(e)
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'message': 'Token-ul refresh este necesar.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifică dacă parola veche este corectă
        if not check_password(old_password, user.password):
            return Response({'message': 'Parola veche este incorectă.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifică dacă parola nouă este diferită de parola veche
        if old_password == new_password:
            return Response({'message': 'Parola nouă trebuie să fie diferită de parola actuală.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validează parola nouă utilizând regulile Django
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({'message': 'Parola nouă nu este validă.', 'errors': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Setează parola nouă
        user.set_password(new_password)
        user.save()

        # După schimbarea parolei, adăugăm token-ul la lista neagră (blacklist)
        if refresh_token:
            try:
                token.blacklist()  # Blacklist token-ul vechi
            except Exception as e:
                return Response({'message': 'Nu am reușit să blacklistez token-ul refresh.', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Parola a fost schimbată cu succes.'}, status=status.HTTP_200_OK)
    
# Token generator pentru resetarea parolei
token_generator = PasswordResetTokenGenerator()

def send_reset_email(email, user):
    """
    Trimite email pentru resetarea parolei cu un token unic.
    """
    # Crează un token de resetare pentru utilizator
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.id).encode())
    
    # Crează link-ul pentru resetarea parolei folosind FRONTEND_URL
    reset_link = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
    full_url = f'{settings.FRONTEND_URL}{reset_link}'  # Folosește URL-ul frontend-ului din settings.py
    
    # Date pentru template-ul de email
    data = {
        'reset_link': full_url,
        'user_id': user.id,
        'token': token
    }
    
    # Încărcăm template-ul de email
    message = get_template('reset_password_email.txt').render(data)
    
    # Trimite email-ul
    send_mail(
        subject="Resetare parolă",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]    
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        logger.info("Post method reached")
        print("Post method reached")
        email = request.data.get("email", "").strip()

        if not email:
            return Response({"detail": "Adresa de email este necesară."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifică dacă utilizatorul există
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Răspuns generalizat (evită dezvăluirea existenței email-ului)
            return Response(
                {"detail": "Dacă adresa de email există în baza noastră de date, vei primi un mesaj cu instrucțiuni."},
                status=status.HTTP_200_OK
            )

        # Verifică dacă utilizatorul a depășit numărul maxim de încercări de resetare
        password_reset_attempt, created = PasswordResetAttempt.objects.get_or_create(email=email)

        # Dacă sunt prea multe încercări, nu permite resetarea
        if not password_reset_attempt.can_attempt_reset():
            return Response(
                {"detail": "Ai atins numărul maxim de încercări de resetare a parolei. Încearcă din nou mai târziu."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Trimite email pentru resetare
        send_reset_email(email, user)

        # Actualizează numărul de încercări
        password_reset_attempt.attempts += 1
        password_reset_attempt.last_attempt = now()
        password_reset_attempt.save()

        return Response(
            {"detail": "Dacă adresa de email există în baza noastră de date, vei primi un mesaj cu instrucțiuni."},
            status=status.HTTP_200_OK
        )

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]      
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Linkul este invalid sau a expirat."}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"detail": "Token invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Dacă tokenul este valid, resetează parola
        new_password = request.data.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Parola a fost resetată cu succes."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Parola nu a fost furnizată."}, status=status.HTTP_400_BAD_REQUEST)
    
class UserAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            address = Address.objects.get(user=request.user)
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({"detail": "Adresa nu există pentru acest utilizator."}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        """
        Creează o adresă nouă pentru utilizatorul autentificat.
        """
        try:
            if Address.objects.filter(user=request.user).exists():
                return Response({"detail": "Adresa există deja pentru acest utilizator."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AddressSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:  # Tratare erori de validare
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # Erori neprevăzute
            return Response({"detail": "Eroare internă."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    def patch(self, request):
        try:
            address, created = Address.objects.get_or_create(user=request.user)
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:  # Tratare erori de validare
            return Response({"detail": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Address.DoesNotExist:  # Dacă adresa nu este găsită
            return Response({"detail": "Adresa nu există."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:  # Erori neprevăzute
            return Response({"detail": "Eroare internă."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

class CompanyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = CompanyProfile.objects.get(user=request.user)
            serializer = CompanyProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CompanyProfile.DoesNotExist:
            return Response({"detail": "Profilul companiei nu există."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = CompanyProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            profile = CompanyProfile.objects.get(user=request.user)
            serializer = CompanyProfileSerializer(
                profile, 
                data=request.data, 
                partial=True, 
                context={'request': request}  # Adăugare context
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CompanyProfile.DoesNotExist:
            return Response({"detail": "Profilul companiei nu există."}, status=status.HTTP_404_NOT_FOUND)
        
class TagListView(APIView):
    permission_classes = [AllowAny]    
    def get(self, request):
        # Filtrăm tag-urile pentru a obține doar cele active (status = 1)
        tags = Tag.objects.filter(status=1)
        
        # Serializăm datele
        serializer = TagSerializer(tags, many=True)
        
        # Returnăm răspunsul cu tag-urile active
        return Response(serializer.data)        

class ListingPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

class ListingFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = filters.NumberFilter(field_name="category_id", lookup_expr="exact")
    county = filters.NumberFilter(field_name="county__id", lookup_expr="exact")    
    city = filters.NumberFilter(field_name="city__id", lookup_expr="exact")
    year_of_construction_min = filters.NumberFilter(field_name='year_of_construction', lookup_expr='gte', label='An minim Construcție')
    year_of_construction_max = filters.NumberFilter(field_name='year_of_construction', lookup_expr='lte', label='An maxim Construcție') 
    username_hash = filters.CharFilter(field_name="user__username_hash", lookup_expr="exact")   
    is_promoted = filters.BooleanFilter(field_name="is_promoted", lookup_expr="exact", label="Anunț promovat")
    
    # Filtre pentru suprafață utilă
    suprafata_utila_min = filters.NumberFilter(field_name="suprafata_utila", lookup_expr="gte", label="Suprafață utilă minimă")
    suprafata_utila_max = filters.NumberFilter(field_name="suprafata_utila", lookup_expr="lte", label="Suprafață utilă maximă")      
    
    # Filtrul pentru etaj
    floor = filters.ChoiceFilter(field_name="floor", choices=FLOOR_CHOICES)
    
    # Filtrul pentru ordonare    
    ordering = OrderingFilter(
    fields=['created_date', 'like_count', 'views_count']
)
    class Meta:
        model = Listing
        fields = [
            'category', 'price_min', 'price_max', 'city__id', 'county__id',
            'year_of_construction_min', 'year_of_construction_max', 
            'username_hash', 'suprafata_utila_min', 'suprafata_utila_max', 'floor', 'is_promoted'
        ]

class ListingAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter
    pagination_class = ListingPagination

    def get(self, request):
        # Filtrare de bază
        queryset = Listing.objects.filter(
            status=1,
            valability_end_date__gte=now().date(),
            is_active_by_user=True  # Exclude anunțurile inactive by user
        )

        # Aplicare filtre
        filterset = self.filterset_class(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs  # Aplică filtrarea definită dacă este validă

        # Aplicare ordonare
        ordering = request.GET.get('ordering')  # Preia parametru 'ordering' din query string
        if ordering:
            queryset = queryset.order_by(ordering)  # Aplică criteriul de ordonare

        # Aplicare paginare
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serializare
        serializer = ListingMinimalSerializer(paginated_queryset, context={'request': request}, many=True)
        return paginator.get_paginated_response(serializer.data)

class promotedListingWidgetAPIView(APIView):
    permission_classes = [AllowAny]   
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter

    # @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request):
        # Filtrare de bază
        queryset = Listing.objects.filter(
            status=1,
            is_promoted=True,
            valability_end_date__gte=now().date(),
            is_active_by_user=True  # Exclude anunțurile inactive by user
        )

        # Aplicare filtre
        filterset = self.filterset_class(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs  # Aplică filtrarea definită dacă este validă
            
        # Selectarea aleatorie a 4 anunțuri promovate
        promoted_listings = queryset.order_by('?')[:4]

        serializer = ListingMinimalSerializer(promoted_listings, context={'request': request}, many=True)
        return Response(serializer.data)
           
class HomeListingAPIView(APIView):
    permission_classes = [AllowAny]    
    
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request):
        # Obține cele 8 cele mai noi anunțuri
        latest_listings = Listing.objects.filter(
            status=1,
            valability_end_date__gte=now().date()
        ).order_by('-created_date')[:8]
        
        # Obține cele 8 cele mai noi anunțuri promovate
        promoted_listings = Listing.objects.filter(
            status=1,
            is_promoted=True,
            valability_end_date__gte=now().date()
        ).order_by('-created_date')[:8]
                

        # Obține cele 8 cele mai apreciate anunțuri
        most_liked_listings = Listing.objects.filter(
            status=1,
            valability_end_date__gte=now().date()
        ).order_by('-like_count')[:8]
        
        # Obține cele 8 cele mai vizualizate anunțuri
        most_viewed_listings = Listing.objects.filter(
            status=1,
            valability_end_date__gte=now().date()
        ).order_by('-views_count')[:8]        

        # Obține 8 anunțuri random
        random_listings = Listing.objects.filter(
            status=1,
            valability_end_date__gte=now().date()
        ).order_by('?')[:8]

        # Serializăm datele
        latest_serializer = ListingMinimalSerializer(latest_listings, context={'request': request}, many=True)
        promoted_serializer = ListingMinimalSerializer(promoted_listings, context={'request': request}, many=True)        
        liked_serializer = ListingMinimalSerializer(most_liked_listings, context={'request': request}, many=True)
        most_viewed = ListingMinimalSerializer(most_viewed_listings, context={'request': request}, many=True)        
        random_serializer = ListingMinimalSerializer(random_listings, context={'request': request}, many=True)

        # Returnăm datele într-un răspuns structurat
        return Response({
            'latest': latest_serializer.data,      # Cele mai noi anunțuri
            'promoted': promoted_serializer.data,  # Anunțuri promovate
            'most_liked': liked_serializer.data,   # Cele mai apreciate anunțuri
            'most_viewed': most_viewed.data,       # Cele mai vizualizate anunțuri            
            'random': random_serializer.data,      # Anunțuri random
        }, status=status.HTTP_200_OK)
    
# Clasă pentru vizualizare detaliată
class ListingDetailAPIView(APIView):
    permission_classes = [AllowAny]  
    
    def get(self, request, slug, *args, **kwargs):
        try:
            listing = Listing.objects.get(slug=slug)
        except Listing.DoesNotExist:
            return Response(
                {"detail": "Anunțul nu a fost găsit."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verifică dacă anunțul este activ sau dacă utilizatorul este proprietar
        if listing.status != 1 and listing.user != request.user:
            return Response(
                {"detail": "Nu aveți permisiunea să accesați acest anunț."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verifică dacă anunțul este dezactivat de utilizator
        if not listing.is_active_by_user and listing.user != request.user:
            return Response(
                {"detail": "Nu aveți permisiunea să accesați acest anunț."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verifică dacă anunțul a expirat
        if listing.valability_end_date and listing.valability_end_date < timezone.now().date():
            # Dacă utilizatorul nu este proprietarul, întoarce mesaj de expirare
            if listing.user != request.user:
                return Response(
                    {"detail": "Anunțul a expirat și nu este accesibil."},
                    status=status.HTTP_403_FORBIDDEN,
                )
                
        # Incrementare views_count dacă utilizatorul nu este proprietarul
        if listing.user != request.user:
            listing.views_count += 1
            listing.save(update_fields=['views_count'])  # Optimizează salvarea doar pentru acest câmp

        # Serializare și răspuns
        serializer = ListingDetailSerializer(listing, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# Clasă pentru ștergere
class ListingDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, uuid, *args, **kwargs):
        try:
            # Căutăm listingul folosind uuid în loc de pk
            listing = Listing.objects.get(pk=uuid)
            if listing.user != request.user:
                return Response(
                    {"detail": "Nu aveți permisiunea să ștergeți acest anunț."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            listing.delete()
            return Response(
                {"detail": "Anunțul a fost șters cu succes."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Listing.DoesNotExist:
            return Response(
                {"detail": "Anunțul nu a fost găsit."},
                status=status.HTTP_404_NOT_FOUND,
            )

class ListingUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, uuid):
        try:
            # Căutăm listingul folosind uuid în loc de pk
            listing = Listing.objects.get(pk=uuid, user=request.user)
        except Listing.DoesNotExist:
            return Response({"detail": "Resursa nu a fost găsită."}, status=status.HTTP_404_NOT_FOUND)

        # Dacă anunțul este găsit
        listing.status = 0  # Setăm statusul ca 'inactive'
        
        # Serializăm datele
        serializer = ListingUpdateSerializer(instance=listing, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            # Salvăm anunțul cu statusul actualizat
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikedListingsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ListingPagination

    def get(self, request):
        # Obține anunțurile pe care utilizatorul autentificat le-a likat
        liked_listings = Listing.objects.filter(likes__user=request.user, status=1).distinct()
        
        # Aplicare paginare directă
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(liked_listings, request)

        # Serializare
        serializer = ListingMinimalSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class PromoteListingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        listing_id = request.data.get("id")
        days = request.data.get("days")  # Numărul de zile pentru promovare

        if not listing_id or not days:
            return Response({"error": "ID-ul anunțului și numărul de zile sunt necesare."}, status=status.HTTP_400_BAD_REQUEST)

        # Convertim în întreg și verificăm limita
        try:
            days = int(days)
            if days <= 0 or days > settings.MAX_PROMOTION_DAYS:
                return Response({"error": f"Numărul maxim de zile permise este {settings.MAX_PROMOTION_DAYS}."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Numărul de zile trebuie să fie un număr valid."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            listing = Listing.objects.get(id=listing_id, user=user)
        except Listing.DoesNotExist:
            return Response({"error": "Anunțul nu există sau nu îți aparține."}, status=status.HTTP_403_FORBIDDEN)

        if listing.status != 1:
            return Response({"error": "Nu poți promova un anunț care nu a fost aprobat de administrator."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Verificăm dacă anunțul este deja promovat
        if listing.is_promoted and listing.valability_promote_date and listing.valability_promote_date > now().date():
            return Response({
                "error": f"Anunțul este deja promovat până pe {listing.valability_promote_date}. Trebuie să aștepți expirarea promovării."
            }, status=status.HTTP_400_BAD_REQUEST)

        today = now().date()
        new_promote_date = (datetime.combine(today, datetime.min.time()) + timedelta(days=int(days))).replace(hour=23, minute=59, second=59)

        # Preluăm valorile din settings.py
        price_per_day_ex_vat = getattr(settings, "PROMOTION_PRICE_PER_DAY_EX_VAT", 5)
        vat_rate = getattr(settings, "VAT_RATE", 19.00)

        # Calculăm costurile
        amount_without_vat = price_per_day_ex_vat * int(days)
        vat_amount = (amount_without_vat * vat_rate) / 100
        amount_with_vat = amount_without_vat + vat_amount

        # Creăm un obiect Payment
        payment = Payment.objects.create(
            user=user,
            listing=listing,
            amount_without_vat=amount_without_vat,
            vat_amount=vat_amount,
            amount_with_vat=amount_with_vat,
            promoted_days=int(days),            
            currency="RON",
            status="pending"
        )

        return Response({
            "success": "Plata inițiată.",
            "payment_id": payment.id,
            "amount_without_vat": float(amount_without_vat),
            "vat_amount": float(vat_amount),
            "amount_with_vat": float(amount_with_vat),
            "new_valability_date": new_promote_date  # Doar informativ, nu se salvează încă
        }, status=status.HTTP_200_OK)


class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get("payment_id")
        # external_payment_id = request.data.get("external_payment_id")  # ID-ul de la procesatorul de plăți
        external_payment_id = 272727  # ID-ul simulat de la procesatorul de plăți
        verification_code = request.data.get("verification_code")  # Codul introdus de utilizator

        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"error": "Plata nu există."}, status=status.HTTP_404_NOT_FOUND)

        if payment.status == "paid":
            return Response({"message": "Plata a fost deja confirmată."}, status=status.HTTP_200_OK)

        # 📌 Simulare verificare cod random pentru confirmare
        if not verification_code:
            return Response({"error": "Codul de verificare este necesar."}, status=status.HTTP_400_BAD_REQUEST)
        
        if str(external_payment_id) != verification_code:
            return Response({"error": "Cod de verificare incorect."}, status=status.HTTP_400_BAD_REQUEST)

        """
        # 🔹 Dacă folosim Stripe, putem activa verificarea reală:
        try:
            stripe_payment = stripe.PaymentIntent.retrieve(external_payment_id)
        except stripe.error.StripeError:
            return Response({"error": "Plata nu a fost găsită în Stripe."}, status=status.HTTP_400_BAD_REQUEST)

        if stripe_payment.status != "succeeded":
            return Response({"error": "Plata nu este confirmată încă."}, status=status.HTTP_400_BAD_REQUEST)
        """

        # Confirmăm plata și promovăm anunțul
        payment.status = "paid"
        payment.save()

        listing = payment.listing
        today = now().date()

        # Setăm perioada de promovare
        end_date = today + timedelta(days=int(payment.promoted_days))
        listing.valability_promote_date = end_date
        listing.is_promoted = True
        listing.save()

        # Salvăm istoricul promovării
        PromotionHistory.objects.create(
            user=payment.user,
            listing=listing,
            title=listing.title,
            total_days=int(payment.promoted_days),
            payment=payment,  # Legăm direct la plată
            start_date=today,
            end_date=end_date
        )

        return Response({"success": "Plata confirmată și anunț promovat."}, status=status.HTTP_200_OK)
        
class ToggleLikeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
       # Filtrăm anunțul pe baza UUID-ului și statusului activ
        listing = Listing.objects.filter(pk=uuid, status=1).first()

        if not listing:
            # Returnăm un răspuns personalizat cu statusul 404
            return Response({"error": "Anunțul nu a fost găsit sau nu este activ."}, status=404)

        # Verificăm dacă utilizatorul încearcă să dea like propriului anunț
        if listing.user == request.user:
            return Response({"error": "Nu poți aprecia propriile anunțuri."}, status=403)

        # Folosim metoda din model pentru gestionarea like-urilor
        liked = listing.toggle_like(request.user)

        # Returnăm răspunsul JSON cu starea curentă
        return Response({'liked': liked, 'like_count': listing.like_count})
    
class ToggleListingActivationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uuid):
        listing = Listing.objects.filter(pk=uuid, user=request.user, status=1).first()
        if not listing:
            return Response({"error": "Anunțul nu poate fi modificat."}, status=400)

        listing.is_active_by_user = not listing.is_active_by_user
        listing.save()
        return Response({"is_active_by_user": listing.is_active_by_user})

class SimilarListingsAPIView(APIView):
    permission_classes = [AllowAny]


    @method_decorator(cache_page(CACHE_TIMEOUT))
    def get(self, request, uuid, *args, **kwargs):
        try:
            # Verifică dacă anunțul există
            listing = Listing.objects.get(id=uuid)
        except Listing.DoesNotExist:
            return Response(
                {"detail": "Anunțul nu a fost găsit."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verifică dacă anunțul este activ
        if listing.status != 1:
            return Response(
                {"detail": "Anunțul nu este activ."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verifică dacă anunțul este dezactivat de utilizator
        if not listing.is_active_by_user:
            return Response(
                {"detail": "Anunțul este dezactivat."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Găsește anunțuri similare
        similar_listings = get_similar_listings(uuid)

        # Dacă nu sunt găsite anunțuri similare, returnăm un array gol
        if not similar_listings:
            return Response([], status=status.HTTP_200_OK)

        # Serializăm anunțurile similare
        serializer = ListingMinimalSerializer(similar_listings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReportCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uuid, *args, **kwargs):
        # Validare UUID
        try:
            listing = Listing.objects.get(pk=uuid)
        except Listing.DoesNotExist:
            return Response({"detail": "Anunțul nu a fost găsit."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:  # Dacă UUID-ul are un format incorect
            return Response({"detail": "UUID invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificăm dacă anunțul este activ
        if listing.status != 1:  # Folosim valoarea din `STATUS_CHOICES` pentru 'Active'
            return Response({"detail": "Anunțul nu este activ."}, status=status.HTTP_400_BAD_REQUEST)

        # Preluăm datele din request
        ip_address = request.META.get('REMOTE_ADDR')
        data = request.data
        data['listing'] = listing.id  # Mapăm listing-ul la ID
        data['ip_address'] = ip_address
        data['status'] = 'pending'  # Status implicit

        # Validăm și salvăm raportul
        serializer = ReportSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Raportul a fost trimis cu succes."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SuggestionCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Doar utilizatori autentificați pot adăuga sugestii

    def post(self, request, *args, **kwargs):
        serializer = SuggestionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # Adăugăm user-ul curent
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   
    
class ClaimCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ClaimRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            claim_request = serializer.save()
            return Response(
                {"detail": "Cererea de revendicare a fost trimisă."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveClaimRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            claim_request = ClaimRequest.objects.get(pk=pk, status='pending')
        except ClaimRequest.DoesNotExist:
            return Response(
                {"detail": "Cererea nu există sau nu este în așteptare."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verifică dacă utilizatorul autentificat este proprietarul companiei
        if claim_request.company.user != request.user:
            return Response(
                {"detail": "Nu aveți permisiunea de a aproba această cerere."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Aprobare cerere
        claim_request.status = 'approved'
        claim_request.save()

        return Response(
            {"detail": "Cererea a fost aprobată."},
            status=status.HTTP_200_OK
        )


class DeclineClaimRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            claim_request = ClaimRequest.objects.get(pk=pk, status='pending')
        except ClaimRequest.DoesNotExist:
            return Response(
                {"detail": "Cererea nu există sau nu este în așteptare."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verifică dacă utilizatorul autentificat este proprietarul companiei
        if claim_request.company.user != request.user:
            return Response(
                {"detail": "Nu aveți permisiunea de a respinge această cerere."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Respinge cererea
        claim_request.status = 'rejected'
        claim_request.save()

        return Response(
            {"detail": "Cererea a fost respinsă."},
            status=status.HTTP_200_OK
        )

class PrivacyPolicySectionAPIView(APIView):
    """API pentru a obține toate secțiunile politicii de confidențialitate"""
    permission_classes = [AllowAny]

    def get(self, request):
        sections = PrivacyPolicySection.objects.all().order_by('section_number')
        serializer = PrivacyPolicySectionSerializer(sections, many=True)
        return Response(serializer.data)


class PrivacyPolicyHistoryAPIView(APIView):
    """API pentru a obține istoricul modificărilor politicii"""

    permission_classes = [AllowAny]
    def get(self, request):
        history = PrivacyPolicyHistory.objects.all().order_by('-modified_at')
        serializer = PrivacyPolicyHistorySerializer(history, many=True)
        return Response(serializer.data)

            
            