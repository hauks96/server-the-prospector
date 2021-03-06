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
from user.models import UnlockedLevel, LevelCompletionStat, LevelStar


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

        # If something is missing from request body
        if username is None or password1 is None or password2 is None:
            if data is not None:
                try:
                    username = data['username']
                    password1 = data['password1']
                    password2 = data['password2']
                except KeyError:
                    response = JsonResponse({"message": "Missing username or password in request."},
                                            status=status.HTTP_400_BAD_REQUEST)
                    return setHeaders(response)

            response = JsonResponse({"message": "Missing username or password in request."},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        # Check if the user with these credentials exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        # If user exists
        if user is not None:
            response = JsonResponse({"message": "Account with this username already exists."},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        if len(username) < 3:
            response = JsonResponse({"message": "Username must be at least of length 3"},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        if password1 != password2:
            response = JsonResponse({"message": "Password checks didn't match"},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        if len(password1) < 5:
            response = JsonResponse({"message": "Password must be at least of length 5"},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        fake_email = username + "_the_prospector@fake_email.com"
        user = User.objects.create_user(username=username, password=password1, email=fake_email)

        token = Token.objects.get(user=user).key
        level_progress = UnlockedLevel.objects.create(user=user)
        level_progress.save()
        response = JsonResponse({"message": "Successfully registered", "token": token}, status=status.HTTP_200_OK)
        return setHeaders(response)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_progress(request):
    user_level_progress = UnlockedLevel.objects.get_or_create(user=request.user)[0]
    if request.method == "GET":
        response = JsonResponse({"unlocked_level": user_level_progress.current_level})
        return setHeaders(response)

    if request.method == "POST":
        if request.user.username == "GuestUser":
            response = JsonResponse({'message': "GuestUser level progression is not saved."}, status=status.HTTP_200_OK)
            return setHeaders(response)

        try:
            data = json.loads(request.body)
        except ValueError:
            data = None

        new_level = request.POST.get("unlocked_level")

        if new_level is None and data is None:
            response = JsonResponse({"message": "Missing 'unlocked_level' from request."},
                                    status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        if new_level is None:
            try:
                new_level = data['unlocked_level']
            except KeyError:
                response = JsonResponse({"message": "Key name must be 'level'."},
                                        status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        if type(new_level) != int:
            try:
                new_level = int(new_level)
            except ValueError:
                response = JsonResponse({"message": "Invalid level for update. Must be integer."},
                                        status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        if user_level_progress.current_level < new_level:
            user_level_progress.current_level = new_level
            user_level_progress.save()
        response = JsonResponse({"unlocked_level": user_level_progress.current_level}, status=status.HTTP_200_OK)
        return setHeaders(response)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def all_best_time(request):
    user_best_level_data = LevelCompletionStat.objects.filter(user=request.user).order_by('time')
    best_time = []
    dict_levels = {}
    if user_best_level_data is None:
        response = JsonResponse({"message": "No best time yet"}, status=status.HTTP_400_BAD_REQUEST)
        return setHeaders(response)

    for level in user_best_level_data:
        try:
            time = dict_levels[level.level]
            if level.time < time:
                dict_levels[level.level] = level.time
        except KeyError:
            dict_levels[level.level] = level.time

    levels = list(dict_levels.keys())
    for i in range(len(levels)):
        best_time.append(dict_levels[levels[i]])

    response = JsonResponse({'level': levels, 'time': best_time}, status=status.HTTP_200_OK)
    return setHeaders(response)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_best_time(request, level):
    user_best_level_data = LevelCompletionStat.objects.filter(user=request.user, level=level).order_by('time').first()

    if user_best_level_data is None:
        response = JsonResponse({"message": "No best time yet"}, status=status.HTTP_400_BAD_REQUEST)
        return setHeaders(response)

    response = JsonResponse({"time": user_best_level_data.time}, status=status.HTTP_200_OK)
    return setHeaders(response)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def level_stars(request):
    if request.method == "GET":
        # Get all level stars in json list
        levels = LevelStar.objects.filter(user=request.user).order_by('level')
        list_stars = []
        list_levels = []
        for i in range(len(levels)):
            list_stars.append(levels[i].stars)
            list_levels.append(levels[i].level)

        response = JsonResponse({'levels': list_levels, 'stars': list_stars}, status=status.HTTP_200_OK)
        return setHeaders(response)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def single_level_stars(request, level):
    if request.method == "GET":
        try:
            level_stars_obj = LevelStar.objects.get(level=level)
        except LevelStar.DoesNotExist:
            response = JsonResponse({"message": "No data found on this level."}, status=status.HTTP_404_NOT_FOUND)
            return setHeaders(response)

        response = JsonResponse({'level': level_stars_obj.level, 'stars': level_stars_obj.stars}, status=status.HTTP_200_OK)
        return setHeaders(response)

    if request.method == "POST":
        # Get the data from request
        keys = ['stars']
        types = {'stars': int}

        try:
            data = json.loads(request.body)
        except ValueError:
            data = None

        if data is not None:
            try:
                data = get_body(keys=keys, req_body=data)
            except KeyError as error:
                response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        else:
            try:
                data = get_form_data(keys=keys, request=request)
            except KeyError as error:
                response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        try:
            data = type_check(data=data, types=types)
        except ValueError as error:
            response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        level_stars_obj = LevelStar.objects.filter(user=request.user, level=level).first()
        # if the level rating doesn't exist yet create a new one
        if level_stars_obj is None:
            level_stars_obj = LevelStar.objects.create(user=request.user, level=level, stars=data['stars'])
            level_stars_obj.save()
            response = JsonResponse({"message": "Updated level stars!", 'level': level, 'stars': data['stars']},
                                    status=status.HTTP_200_OK)
            return setHeaders(response)
        # if it already exists first check if we really need to update
        else:
            data_stars = data['stars']
            if data_stars > level_stars_obj.stars:
                if data_stars > 3:
                    response=  JsonResponse({"message": "Cannot update with more than 3 stars."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    return setHeaders(response)
                level_stars_obj.stars = data_stars
                level_stars_obj.save()

        response = JsonResponse({"message": "Updated level stars!", 'level': level, 'stars': data_stars},
                            status=status.HTTP_200_OK)
        return setHeaders(response)


@api_view(['GET'])
def get_world_record(request, level):
    world_record = LevelCompletionStat.objects.filter(level=level, stars=3).order_by('time').first()
    if world_record is None:
        response = JsonResponse({"time": 0}, status=status.HTTP_200_OK)
        return setHeaders(response)
    response = JsonResponse({"time": world_record.time}, status=status.HTTP_200_OK)
    return setHeaders(response)


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
                response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        else:
            try:
                data = get_form_data(keys=keys, request=request)
            except KeyError as error:
                response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)

        try:
            data = type_check(data=data, types=types)
        except ValueError as error:
            response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

        # Add to level stats
        stats = LevelCompletionStat.objects.create(user=request.user, restarts=data['restarts'],
                                                   time=data['time'], level=data['level'])
        stats.save()
        response = JsonResponse({"message": "Level data saved", "data": data}, status=status.HTTP_200_OK)
        return setHeaders(response)


@api_view(['GET'])
def get_average_per_level(request):
    if request.user.is_superuser or request.user.is_staff:
        all_stats = LevelCompletionStat.objects.all()
        data = StatsRep.get_average_per_level(all_stats)
        response = JsonResponse({"message": "Data successfully fetched.", "data": data}, status=status.HTTP_200_OK)
        return setHeaders(response)
    response = JsonResponse({'message': "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    return setHeaders(response)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_all(request):
    keys = ['level', 'stars', 'restarts', 'time']
    types = {'level': int, 'stars': int, 'restarts': int, 'time': float}

    try:
        data = json.loads(request.body)
    except ValueError:
        data = None

    if data is not None:
        try:
            data = get_body(keys=keys, req_body=data)
        except KeyError as error:
            response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

    else:
        try:
            data = get_form_data(keys=keys, request=request)
        except KeyError as error:
            response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return setHeaders(response)

    try:
        data = type_check(data=data, types=types)
    except ValueError as error:
        response = JsonResponse({"message": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return setHeaders(response)

    # Add game data to level stats
    stats = LevelCompletionStat.objects.create(user=request.user, restarts=data['restarts'],
                                               time=data['time'], level=data['level'], stars=data['stars'])
    stats.save()

    if request.user.username != "GuestUser":
        # Update level stars if needed
        level_stars_obj = LevelStar.objects.get_or_create(user=request.user, level=data['level'])[0]
        data_stars = data['stars']

        if data_stars > level_stars_obj.stars:
            if data_stars > 3:
                response = JsonResponse({"message": "Cannot update with more than 3 stars."},
                                        status=status.HTTP_400_BAD_REQUEST)
                return setHeaders(response)
            level_stars_obj.stars = data_stars
            level_stars_obj.save()

        # Update users unlocked level if needed
        user_level_progress = UnlockedLevel.objects.get(user=request.user)
        if user_level_progress.current_level < data['level']:
            user_level_progress.current_level = data['level']
            user_level_progress.save()

    response = JsonResponse({'message': 'Game data stored. Level stars updated. User level unlocks updated.'})
    return setHeaders(response)


def type_check(data: dict, types: dict) -> dict:
    keys = list(data.keys())
    for i in range(len(keys)):
        if type(data[keys[i]]) != types[keys[i]]:
            try:
                data[keys[i]] = types[keys[i]](data[keys[i]])
            except ValueError:
                error_str = "Incorrect type received for key '" + keys[i] + "': " + str(data[keys[i]]) + "."
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


def setHeaders(response, set_auth=True):

    #response["Access-Control-Allow-Credentials"] = "true"
    #response["Access-Control-Allow-Headers"] = "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time"
    #response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    #response["Access-Control-Allow-Origin"] = "*"

    return response
