from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserRegistrationSerializer, CustomAuthTokenSerializer, UserLoginResponseSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.serializers import AuthTokenSerializer


#Register API
@api_view(['POST'])
@permission_classes([AllowAny])
def userRegistration(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#Login API
@api_view(['POST'])
@permission_classes([AllowAny])
def userAuthTokenLogin(request):
    serializer = CustomAuthTokenSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Get or create the token for the user
    token, created = Token.objects.get_or_create(user=user)
    
    # Determine the role based on user attributes
    if user.is_superuser:
        role = 'admin'
    elif user.is_staff:
        role = 'staff'
    else:
        role = 'customer'
    
    # Customize the response data
    response_data = {
        'access_token': token.key,
        'token_type': 'bearer',
        'expires_in': 36000,  # token expiration time (in seconds)
        'user': {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined, 
            'role': role
        }
    }

    serializer = UserLoginResponseSerializer(data=response_data)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)



