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

