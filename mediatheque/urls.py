from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('login/membre/', views.login_membre, name='login_membre'),
    path('login/bibliothecaire/', views.login_bibliothecaire, name='login_bibliothecaire'),
    path('logout/', views.logout_view, name='logout'),
    path('espace/membre/', views.espace_membre, name='espace_membre'),
    path('espace/bibliothecaire/', views.espace_bibliothecaire, name='espace_bibliothecaire'),

    # Médias
    path('medias/', views.liste_medias, name='liste_medias'),
    path('medias/ajouter/', views.ajouter_media, name='ajouter_media'),
    path('medias/ajouter/livre/', views.ajouter_livre, name='ajouter_livre'),
    path('medias/ajouter/dvd/', views.ajouter_dvd, name='ajouter_dvd'),
    path('medias/ajouter/cd/', views.ajouter_cd, name='ajouter_cd'),
    path('medias/ajouter/jeu/', views.ajouter_jeu, name='ajouter_jeu'),
    # Modifier médias
    path('medias/modifier/livre/<int:pk>/', views.modifier_livre, name='modifier_livre'),
    path('medias/modifier/dvd/<int:pk>/', views.modifier_dvd, name='modifier_dvd'),
    path('medias/modifier/cd/<int:pk>/', views.modifier_cd, name='modifier_cd'),
    path('medias/modifier/jeu/<int:pk>/', views.modifier_jeu, name='modifier_jeu'),
    # Supprimer médias
    path('medias/supprimer/livre/<int:pk>/', views.supprimer_livre, name='supprimer_livre'),
    path('medias/supprimer/dvd/<int:pk>/', views.supprimer_dvd, name='supprimer_dvd'),
    path('medias/supprimer/cd/<int:pk>/', views.supprimer_cd, name='supprimer_cd'),
    path('medias/supprimer/jeu/<int:pk>/', views.supprimer_jeu, name='supprimer_jeu'),

    # Membres
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/ajouter/', views.ajouter_membre, name='ajouter_membre'),
    path('membres/modifier/<int:pk>/', views.modifier_membre, name='modifier_membre'),
    path('membres/supprimer/<int:pk>/', views.supprimer_membre, name='supprimer_membre'),

    # Emprunts
    path('emprunts/', views.liste_emprunts, name='liste_emprunts'),
    path('emprunts/creer/', views.creer_emprunt, name='creer_emprunt'),
    path('emprunts/retourner/<int:pk>/', views.retourner_emprunt, name='retourner_emprunt'),
]
