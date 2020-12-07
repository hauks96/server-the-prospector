import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.authtoken.models import Token


# Create your views here.

@api_view(['POST'])
def registration(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # Get request body username and password
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # If something is missing from request body
        if username is None or password1 is None or password2 is None:
            try:
                username = data['username']
                password1 = data['password1']
                password2 = data['password2']
            except KeyError:
                return JsonResponse({"message": "Missing username or password in request."},
                                    status=status.HTTP_400_BAD_REQUEST)

        # Check if the user with these credentials exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        # If user exists
        if user is not None:
            return JsonResponse({"message": "Account with this username already exists."},
                                status=status.HTTP_400_BAD_REQUEST)

        if len(username) < 3:
            return JsonResponse({"message": "Username must be at least of length 3"},
                                status=status.HTTP_400_BAD_REQUEST)

        if password1 != password2:
            return JsonResponse({"message": "Password checks didn't match"},
                                status=status.HTTP_400_BAD_REQUEST)

        if len(password1) < 5:
            return JsonResponse({"message": "Password must be at least of length 5"},
                                status=status.HTTP_400_BAD_REQUEST)

        fake_email = username+"_the_prospector@fake_email.com"
        user = User.objects.create_user(username=username, password=password1, email=fake_email)

        token = Token.objects.get(user=user).key
        return JsonResponse({"message": "Successfully logged in", "token": token}, status=status.HTTP_200_OK)
