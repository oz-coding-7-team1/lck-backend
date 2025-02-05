from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/player/', views.subscribe_player, name='subscribe_player'),
    path('unsubscribe/player/', views.unsubscribe_player, name='unsubscribe_player'),
    path('subscribe/team/', views.subscribe_team, name='subscribe_team'),
    path('unsubscribe/team/', views.unsubscribe_team, name='unsubscribe_team'),
    path('count/players/', views.subscribed_players_count, name='subscribed_players_count'),
    path('count/teams/', views.subscribed_teams_count, name='subscribed_teams_count'),
]