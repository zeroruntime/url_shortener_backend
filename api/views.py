from datetime import timezone
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import string, random, math, secrets

from api.models import Clicks, Links
from api.serializers import ClickSerializer, LinkSerializer

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

# Old method, insecure and open to bruteforcing
# def generate_short_url():
#     BASE62_ALPHABET = string.digits + string.ascii_letters
#     # BASENUM = len(BASE62_ALPHABET)

#     short_url = ''

#     for i in range(6):
#         # short_url += BASE62_ALPHABET[math.floor(random.random() * BASENUM)]
#         short_url += random.choice(BASE62_ALPHABET)

#     return short_url

# New method, using secrets to generate the short url
def generate_short_url():
    BASE62_ALPHABET = string.digits + string.ascii_letters
    return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(6))

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

    existing_link = Links.objects.filter(original_url=longUrl, user_id=user).first()
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getlink(request, pk):
    user = request.user
    try:
        link = Links.objects.filter(user=user).get(pk=pk)
        serializer = LinkSerializer(link)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Links.DoesNotExist:
        return Response({'error':'Link not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletelink(request, pk):
    user = request.user
    link = get_object_or_404(Links, pk=pk, user=user)
    link.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def redirect_url(request, short_code):
    try:
        link = Links.objects.get(short_code=short_code, is_active=True)

        if link.expires_at and link.expires_at > timezone.now():
            return Response({"error":"Link has expired"}, status=status.HTTP_410_GONE)

        Clicks.objects.create(
            link=link,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )

        return Response({'redirect_to': link.original_url}, status=status.HTTP_302_FOUND)
    except Links.DoesNotExist:
        return Response({'error': 'Link not found'}, status=status.HTTP_404_NOT_FOUND)
