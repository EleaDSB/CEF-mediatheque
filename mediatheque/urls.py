from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/membre/', views.login_membre, name='login_membre'),
    path('login/bibliothecaire/', views.login_bibliothecaire, name='login_bibliothecaire'),
    path('logout/', views.logout_view, name='logout'),
    path('espace/membre/', views.espace_membre, name='espace_membre'),
    path('espace/bibliothecaire/', views.espace_bibliothecaire, name='espace_bibliothecaire'),
    path('medias/', views.liste_medias, name='liste_medias'),
]
