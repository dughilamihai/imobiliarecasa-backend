from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
# need to send confirmation email after user sign up
from api.utils import send_confirmation_email
from .models import *
from .serializers import *

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

