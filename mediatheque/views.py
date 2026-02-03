from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Livre, DVD, CD, JeuPlateau
import logging

logger = logging.getLogger('mediatheque')


def home(request):
    """Page d'accueil avec choix Membre/Bibliothécaire"""
    logger.info("Accès à la page d'accueil")
    return render(request, 'mediatheque/home.html')


def login_membre(request):
    """Connexion pour les membres"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Vérifier que c'est bien un membre (pas staff)
            if not user.is_staff:
                login(request, user)
                logger.info(f"Connexion membre: {username}")
                messages.success(request, f"Bienvenue {username} !")
                return redirect('espace_membre')
            else:
                logger.warning(f"Tentative connexion membre avec compte staff: {username}")
                return render(request, 'mediatheque/login.html', {
                    'user_type': 'Membre',
                    'error': "Ce compte n'est pas un compte membre."
                })
        else:
            logger.warning(f"Échec connexion membre: {username}")
            return render(request, 'mediatheque/login.html', {
                'user_type': 'Membre',
                'error': "Nom d'utilisateur ou mot de passe incorrect."
            })

    return render(request, 'mediatheque/login.html', {'user_type': 'Membre'})


def login_bibliothecaire(request):
    """Connexion pour les bibliothécaires"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Vérifier que c'est bien un bibliothécaire (staff)
            if user.is_staff:
                login(request, user)
                logger.info(f"Connexion bibliothécaire: {username}")
                messages.success(request, f"Bienvenue {username} !")
                return redirect('espace_bibliothecaire')
            else:
                logger.warning(f"Tentative connexion biblio avec compte membre: {username}")
                return render(request, 'mediatheque/login.html', {
                    'user_type': 'Bibliothécaire',
                    'error': "Ce compte n'est pas un compte bibliothécaire."
                })
        else:
            logger.warning(f"Échec connexion bibliothécaire: {username}")
            return render(request, 'mediatheque/login.html', {
                'user_type': 'Bibliothécaire',
                'error': "Nom d'utilisateur ou mot de passe incorrect."
            })

    return render(request, 'mediatheque/login.html', {'user_type': 'Bibliothécaire'})


def logout_view(request):
    """Déconnexion"""
    username = request.user.username
    logout(request)
    logger.info(f"Déconnexion: {username}")
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')


@login_required
def espace_membre(request):
    """Espace membre - consultation des médias"""
    if request.user.is_staff:
        return redirect('espace_bibliothecaire')
    return render(request, 'mediatheque/espace_membre.html')


@login_required
def espace_bibliothecaire(request):
    """Espace bibliothécaire - gestion complète"""
    if not request.user.is_staff:
        return redirect('espace_membre')
    return render(request, 'mediatheque/espace_bibliothecaire.html')


def liste_medias(request):
    """Liste de tous les médias - accessible à tous"""
    livres = Livre.objects.all()
    dvds = DVD.objects.all()
    cds = CD.objects.all()
    jeux = JeuPlateau.objects.all()

    username = request.user.username if request.user.is_authenticated else "visiteur"
    logger.info(f"Consultation liste médias par {username}")

    return render(request, 'mediatheque/liste_medias.html', {
        'livres': livres,
        'dvds': dvds,
        'cds': cds,
        'jeux': jeux,
    })
