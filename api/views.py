from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema

from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Links, Clicks
from api.serializers import LinkSerializer, RegisterSerializer, LogoutSerializer

from functools import wraps
from django.core.cache import cache
from django.db.models import Count

import string, secrets

# AUTHENTICATION
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: None})
    def get(self, request):
        return Response({
            "message": f"Hello, {request.user.username}, you are authenticated!"
        })

class RegisterView(APIView):

    @extend_schema(
        request=RegisterSerializer,
        responses={201: None}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if User.objects.filter(username=serializer.validated_data["username"]).exists():
            return Response(
                {"error": "Username exists already"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response({"message": "User created successfully"}, status=201)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LogoutSerializer,
        responses={205: None}
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
            return Response({"message": "Logout successful"}, status=205)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

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
# def generate_short_url():
#     BASE62_ALPHABET = string.digits + string.ascii_letters
#     return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(6))

def rate_limit(max_requests, time_window_seconds):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            if request.user.is_authenticated:
                key = f"rate_limit:user:{request.user.id}"
            else:
                key = f"rate_limit:ip:{request.META.get('REMOTE_ADDR')}"

            current = cache.get(key)

            if current is None:
                cache.add(key, 1, timeout=time_window_seconds)
                return view_func(request, *args, **kwargs)

            if current >= max_requests:
                return Response(
                    {"error": "Rate limit exceeded"},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            cache.incr(key)
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator

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
def generate_short_url():
    BASE62 = string.digits + string.ascii_letters
    return ''.join(secrets.choice(BASE62) for _ in range(6))

@method_decorator(rate_limit(100, 3600), name='post')
class ShortenURLView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=LinkSerializer,
        responses={201: LinkSerializer}
    )
    def post(self, request):
        serializer = LinkSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        long_url = serializer.validated_data["original_url"]
        custom_alias = serializer.validated_data.get("custom_alias")

        existing = Links.objects.filter(original_url=long_url, user=user).first()
        if existing:
            return Response({
                "shortUrl": existing.short_code,
                "customAlias": existing.custom_alias,
                "longUrl": existing.original_url,
                "message": "URL already exists"
            })

        if custom_alias and Links.objects.filter(custom_alias=custom_alias).exists():
            return Response({"error": "Custom alias taken"}, status=400)

        for _ in range(10):
            short_code = custom_alias or generate_short_url()
            try:
                link = serializer.save(user=user, short_code=short_code)
                return Response({
                    "shortUrl": link.short_code,
                    "customAlias": link.custom_alias,
                    "longUrl": link.original_url
                }, status=201)
            except IntegrityError:
                if custom_alias:
                    break

        return Response({"error": "Could not generate unique short URL"}, status=500)

class LinkListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LinkSerializer(many=True)})
    def get(self, request):
        limit = min(int(request.query_params.get("limit", 10)), 100)
        offset = max(int(request.query_params.get("offset", 0)), 0)

        queryset = Links.objects.filter(user=request.user).order_by("-created_at")
        total = queryset.count()
        links = queryset[offset:offset + limit]

        serializer = LinkSerializer(links, many=True)

        return Response({
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": serializer.data
        })

class LinkDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: LinkSerializer})
    def get(self, request, pk):
        link = get_object_or_404(Links, pk=pk, user=request.user)
        return Response(LinkSerializer(link).data)

class DeleteLinkView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        link = get_object_or_404(Links, pk=pk, user=request.user)
        link.delete()
        return Response(status=204)

@method_decorator(rate_limit(1000, 3600), name='get')
class RedirectView(APIView):

    @extend_schema(exclude=True)
    def get(self, request, short_code):
        try:
            link = Links.objects.get(short_code=short_code, is_active=True)

            if link.expires_at and link.expires_at < timezone.now():
                return Response({"error": "Link expired"}, status=410)

            Clicks.objects.create(
                link=link,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return HttpResponseRedirect(link.original_url)

        except Links.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

class LinkAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: None})
    def get(self, request, pk):
        link = get_object_or_404(Links, pk=pk, user=request.user)
        clicks = Clicks.objects.filter(link=link)

        data = {
            'link_info': {
                'short_url': f"{request.build_absolute_uri('/')[:-1]}/{link.short_code}",
                'original_url': link.original_url,
                'created_at': link.created_at,
                'is_active': link.is_active,
                'expires_at': link.expires_at,
            },
            'total_clicks': clicks.count(),
            'clicks_by_country': list(
                clicks.values('country')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
        }

        return Response(data)
