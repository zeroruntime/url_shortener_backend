from django.db import IntegrityError
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import string, random, math

from api.models import Links
from api.serializers import LinkSerializer

# AUTHENTICATION
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    user = request.user
    return Response({
        'message': f'Hello, {user.username}, you are authenticated!'
    })

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password:
        return Response({'error': 'Username and password are required'})

    if User.objects.filter(username=username).exists():
        return Response({'error':'Username exists already'})

    user = User.objects.create_user(username=username, password=password, email=email)
    user.save()

    return Response({'message':'User created successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message':'Logout successful'}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# URL SHORTENING LOGIC
def generate_short_url():
    BASE62_ALPHABET = string.digits + string.ascii_letters
    # BASENUM = len(BASE62_ALPHABET)

    short_url = ''

    for i in range(6):
        # short_url += BASE62_ALPHABET[math.floor(random.random() * BASENUM)]
        short_url += random.choice(BASE62_ALPHABET)

    return short_url

# OUTDATED POST REUEST (DOESNT USE SERIALIZATION)
# @api_view(['POST'])
# def shorten_url(request):
#     longUrl = request.data.get('longUrl')

#     if not longUrl:
#         return Response({'error':'Long URL is required'}, status=status.HTTP_400_BAD_REQUEST)

#     # if Links.objects.filter(original_url=longUrl).exists():
#     #     return Response({"error":"Original Url already exists"})

#     existing_link = Links.objects.filter(original_url=longUrl).first()
#     if existing_link:
#         return Response({
#             'shortUrl': existing_link.short_code,
#             'longUrl': existing_link.original_url,
#             'message': 'URL already has a short code'
#         }, status=status.HTTP_200_OK)

#     max_tries = 10
#     tries = 0

#     while True:
#         tries += 1
#         short_code = generate_short_url()

#         try:
#             link = Links.objects.create(short_code=short_code, original_url=longUrl)
#             newlinks = {
#                 "shortUrl":short_code,
#                 "longUrl":longUrl
#             }
#             return Response(newlinks, status=status.HTTP_201_CREATED)

#         except IntegrityError:
#             if tries > max_tries:
#                 break
#             continue
#     return Response({"error": "Could not generate unique short URL after multiple attempts"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# NEW POST REQUEST TO CREATE SHORT URL
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def shorten_url(request):
    serializer = LinkSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    longUrl = serializer.validated_data['original_url']
    user = request.user

    existing_link = Links.objects.filter(original_url=longUrl, user=user).first()
    if existing_link:
        return Response({
            'shortUrl': existing_link.short_code,
            'longUrl': existing_link.original_url,
            'message': 'URL already has a short code'
        }, status=status.HTTP_200_OK)

    max_tries = 10
    tries = 0
    while tries < max_tries:
        tries += 1
        short_code = generate_short_url()
        try:
            link = serializer.save(short_code=short_code)
            return Response({
                'shortUrl': link.short_code,
                'longUrl': link.original_url
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            continue

    return Response(
        {"error": "Could not generate unique short URL"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getlinks(request):
    user = request.user
    allshortlinks = Links.objects.filter(user=user)
    serializer = LinkSerializer(allshortlinks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
