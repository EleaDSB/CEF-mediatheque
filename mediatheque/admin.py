from django.contrib import admin
from .models import Livre, DVD, CD, JeuPlateau, Membre, Emprunt


@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'disponible')
    search_fields = ('titre', 'auteur')
    list_filter = ('disponible',)


@admin.register(DVD)
class DVDAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'duree', 'disponible')
    search_fields = ('titre', 'auteur')
    list_filter = ('disponible',)


@admin.register(CD)
class CDAdmin(admin.ModelAdmin):
    list_display = ('titre', 'artiste', 'nombre_pistes', 'disponible')
    search_fields = ('titre', 'artiste')
    list_filter = ('disponible',)


@admin.register(JeuPlateau)
class JeuPlateauAdmin(admin.ModelAdmin):
    list_display = ('titre', 'editeur', 'nombre_joueurs_min', 'nombre_joueurs_max')
    search_fields = ('titre', 'editeur')


@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'date_inscription', 'actif')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('actif',)


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ('membre', 'get_media', 'date_emprunt', 'date_retour_prevue', 'date_retour_effective')
    list_filter = ('date_emprunt', 'date_retour_effective')
    search_fields = ('membre__nom', 'membre__prenom')
