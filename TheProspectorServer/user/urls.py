from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import registration, get_average_per_level, level_stats, guest_user

urlpatterns = [
    path('login/', obtain_auth_token, name="login"),
    path('guest-login/', guest_user, name="guest-login"),
    path('register/', registration, name="register"),
    path('save-playstats/', level_stats, name="save-stats"),
    path('average-stats/', get_average_per_level, name="avg-stats"),
]
