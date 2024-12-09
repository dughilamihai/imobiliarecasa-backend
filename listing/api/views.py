from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
# send confirmation email after user sign up
from api.utils import send_confirmation_email

from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
# for login
from rest_framework_simplejwt.views import TokenObtainPairView
# for change password
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

# for filtering
from django_filters import rest_framework as filters
from  django_filters.rest_framework import DjangoFilterBackend

# for pagination
from rest_framework.pagination import PageNumberPagination

# for listing
# every user will be able to see all the listings, but only logged-in users will be able to add, change, or delete objects.
from rest_framework.permissions import IsAuthenticatedOrReadOnly

import logging
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)

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
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class CategoryListAV(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        parent_categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(parent_categories, many=True)
        return Response(serializer.data)
    
# register user        
class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated requests
      
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

class ListingPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

class ListingFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = filters.CharFilter(field_name="category", lookup_expr="exact")
    city_id = filters.NumberFilter(field_name="city__id", lookup_expr="exact")

    class Meta:
        model = Listing
        fields = ['category', 'price_min', 'price_max', 'city__id']
        
class ListingAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    pagination_class = ListingPagination

    def get(self, request):
        """
        Listare și filtrare Listings.
        """
        today = now().date()
        queryset = Listing.objects.filter(
            status=1,
            valability_end_date__gte=today
        ).order_by('-created_date')

        # Aplicare filtre Django Filter
        filterset = ListingFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        # Paginare
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(filterset.qs, request)

        # Serializare
        serializer = ListingSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)  
    
    def post(self, request):
        """
        Creare Listing nou.
        """
        serializer = ListingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    
class ListingDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            listing = Listing.objects.get(pk=pk)
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
            