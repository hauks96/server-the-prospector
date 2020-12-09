from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import registration, get_average_per_level, level_stats, guest_user, user_progress, get_best_time, \
    level_stars, update_all, single_level_stars, all_best_time

urlpatterns = [
    path('login/', obtain_auth_token, name="login"),
    path('guest-login/', guest_user, name="guest-login"),
    path('register/', registration, name="register"),
    path('save-playstats/', level_stats, name="save-stats"),
    path('average-stats/', get_average_per_level, name="avg-stats"),
    path('unlocked-level/', user_progress, name="player-progress"),
    path('best-time/', all_best_time, name="best-time"),
    path('best-time/<int:level>/', get_best_time, name="single-best-time"),
    path('level-stars/', level_stars, name="level-stars"),
    path('level-stars/<int:level>/', single_level_stars, name="level-stars"),
    path('update-post-game/', update_all, name="update-all"),
]
