import copy
import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.
from user.models import LevelProgress, LevelCompletionStats


@api_view(['GET'])
def guest_user(request):
    guest = User.objects.get(username='GuestUser')
    token = Token.objects.get(user=guest)
    return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)


@api_view(['POST'])
def registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except ValueError:
            data = None
        # Get request body username and password
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        print(username, password1, password2)

        # If something is missing from request body
        if username is None or password1 is None or password2 is None:
            if data is not None:
                try:
                    username = data['username']
                    password1 = data['password1']
                    password2 = data['password2']
                except KeyError:
                    return JsonResponse({"message": "Missing username or password in request."},
                                        status=status.HTTP_400_BAD_REQUEST)

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

        fake_email = username + "_the_prospector@fake_email.com"
        user = User.objects.create_user(username=username, password=password1, email=fake_email)

        token = Token.objects.get(user=user).key
        level_progress = LevelProgress.objects.create(user=user)
        level_progress.save()
        return JsonResponse({"message": "Successfully registered", "token": token}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_progress(request):
    user_level_progress = LevelProgress.objects.get(user=request.user)
    if request.method == "GET":
        return JsonResponse({"current_level": user_level_progress.current_level})

    if request.method == "POST":
        if request.user.username == "GuestUser":
            return JsonResponse({'message': "GuestUser level progression is not saved."}, status=status.HTTP_200_OK)
        try:
            data = json.loads(request.body)
        except ValueError:
            data = None

        new_level = request.POST.get("level")

        if new_level is None and data is None:
            return JsonResponse({"message": "Missing 'level' from request."}, status=status.HTTP_400_BAD_REQUEST)

        if new_level is None:
            try:
                new_level = data['level']
            except KeyError:
                return JsonResponse({"message": "Key name must be 'level'."},
                                    status=status.HTTP_400_BAD_REQUEST)

        if type(new_level) != int:
            try:
                new_level = int(new_level)
            except ValueError:
                return JsonResponse({"message": "Invalid level for update. Must be integer."},
                                    status=status.HTTP_400_BAD_REQUEST)

        user_level_progress.current_level = new_level
        user_level_progress.save()
        return JsonResponse({"current_level": user_level_progress.current_level}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def level_stats(request):
    keys = ['restarts', 'time', 'level']
    types = {'restarts': int, 'time': float, 'level': int}
    if request.method == "POST":
        # Get the data from request
        try:
            data = json.loads(request.body)
        except ValueError:
            data = None

        if data is not None:
            try:
                data = get_body(keys=keys, req_body=data)
            except KeyError as error:
                return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                data = get_form_data(keys=keys, request=request)
            except KeyError as error:
                return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = type_check(data=data, types=types)
        except ValueError as error:
            return JsonResponse({"message": error}, status=status.HTTP_400_BAD_REQUEST)

        # Add to level stats
        stats = LevelCompletionStats.objects.create(user=request.user, restarts=data['restarts'],
                                                    time=data['time'], level=data['level'])
        stats.save()
        return JsonResponse({"message": "Level data saved", "data": data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_average_per_level(request):
    all_stats = LevelCompletionStats.objects.all()
    data = StatsRep.get_average_per_level(all_stats)
    return JsonResponse({"message": "Data successfully fetched.", "data": data}, status=status.HTTP_200_OK)


def type_check(data: dict, types: dict) -> dict:
    keys = list(data.keys())
    for i in range(len(keys)):
        if type(data[keys[i]]) != types[keys[i]]:
            try:
                data[keys[i]] = types[keys[i]](data[keys[i]])
            except ValueError:
                error_str = "Incorrect type received for key '" + data[keys[i]] + "'."
                raise ValueError(error_str)
    return data


def get_body(keys: list, req_body: dict) -> dict:
    ret_data = {}
    for i in range(len(keys)):
        try:
            ret_data[keys[i]] = req_body[keys[i]]
        except KeyError:
            raise KeyError("Missing key value pair '" + keys[i] + "'.")

    return ret_data


def get_form_data(keys: list, request) -> dict:
    ret_data = {}
    for i in range(len(keys)):
        curr_val = request.POST.get(keys[i])
        if curr_val is None:
            raise KeyError("Missing key value pair '" + keys[i] + "'.")
        ret_data[keys[i]] = curr_val

    return ret_data


class StatsRep:
    @staticmethod
    def get_average_per_level(django_query) -> dict:
        levels_total = {}
        level_total_preset = {"time": 0.0, "plays": 0, "restarts": 0}
        for stat in django_query:
            try:
                levels_total[stat.level]
            except KeyError:
                levels_total[stat.level] = copy.deepcopy(level_total_preset)

            curr_level_stats = levels_total[stat.level]
            curr_level_stats["time"] += stat.time
            curr_level_stats["plays"] += 1
            curr_level_stats["restarts"] += stat.restarts

        levels = levels_total.keys()
        for level in levels:
            plays = levels_total[level]["plays"]
            levels_total[level]["time"] = levels_total[level]["time"] / plays
            levels_total[level]["restarts"] = levels_total[level]["restarts"] / plays

        return levels_total
