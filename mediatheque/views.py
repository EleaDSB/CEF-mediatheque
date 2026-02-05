from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Livre, DVD, CD, JeuPlateau, Membre, Emprunt
from .forms import MembreForm, LivreForm, DVDForm, CDForm, JeuPlateauForm, EmpruntForm
from django.utils import timezone
import logging

logger = logging.getLogger('mediatheque')


def is_bibliothecaire(user):
    """Vérifie si l'utilisateur est bibliothécaire"""
    return user.is_staff


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


# ============== GESTION DES MEMBRES ==============

@login_required
@user_passes_test(is_bibliothecaire)
def liste_membres(request):
    """Liste de tous les membres"""
    membres = Membre.objects.all()
    logger.info(f"Consultation liste membres par {request.user.username}")
    return render(request, 'mediatheque/liste_membres.html', {'membres': membres})


@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_membre(request):
    """Ajouter un nouveau membre"""
    if request.method == 'POST':
        form = MembreForm(request.POST)
        if form.is_valid():
            membre = form.save()
            logger.info(f"Membre créé: {membre.nom} {membre.prenom} par {request.user.username}")
            messages.success(request, f"Membre {membre.prenom} {membre.nom} créé avec succès.")
            return redirect('liste_membres')
    else:
        form = MembreForm()
    return render(request, 'mediatheque/form_membre.html', {'form': form, 'action': 'Ajouter'})


@login_required
@user_passes_test(is_bibliothecaire)
def modifier_membre(request, pk):
    """Modifier un membre existant"""
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == 'POST':
        form = MembreForm(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            logger.info(f"Membre modifié: {membre.nom} {membre.prenom} par {request.user.username}")
            messages.success(request, f"Membre {membre.prenom} {membre.nom} modifié avec succès.")
            return redirect('liste_membres')
    else:
        form = MembreForm(instance=membre)
    return render(request, 'mediatheque/form_membre.html', {'form': form, 'action': 'Modifier', 'membre': membre})


@login_required
@user_passes_test(is_bibliothecaire)
def supprimer_membre(request, pk):
    """Supprimer un membre"""
    membre = get_object_or_404(Membre, pk=pk)
    if request.method == 'POST':
        nom_complet = f"{membre.prenom} {membre.nom}"
        logger.info(f"Membre supprimé: {nom_complet} par {request.user.username}")
        membre.delete()
        messages.success(request, f"Membre {nom_complet} supprimé avec succès.")
        return redirect('liste_membres')
    return render(request, 'mediatheque/confirmer_suppression.html', {'objet': membre, 'type': 'membre'})


# ============== GESTION DES MÉDIAS ==============

@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_media(request):
    """Page de choix du type de média à ajouter"""
    return render(request, 'mediatheque/choix_media.html')


@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_livre(request):
    """Ajouter un livre"""
    if request.method == 'POST':
        form = LivreForm(request.POST)
        if form.is_valid():
            livre = form.save()
            logger.info(f"Livre ajouté: {livre.titre} par {request.user.username}")
            messages.success(request, f"Livre '{livre.titre}' ajouté avec succès.")
            return redirect('liste_medias')
    else:
        form = LivreForm()
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'Livre'})


@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_dvd(request):
    """Ajouter un DVD"""
    if request.method == 'POST':
        form = DVDForm(request.POST)
        if form.is_valid():
            dvd = form.save()
            logger.info(f"DVD ajouté: {dvd.titre} par {request.user.username}")
            messages.success(request, f"DVD '{dvd.titre}' ajouté avec succès.")
            return redirect('liste_medias')
    else:
        form = DVDForm()
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'DVD'})


@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_cd(request):
    """Ajouter un CD"""
    if request.method == 'POST':
        form = CDForm(request.POST)
        if form.is_valid():
            cd = form.save()
            logger.info(f"CD ajouté: {cd.titre} par {request.user.username}")
            messages.success(request, f"CD '{cd.titre}' ajouté avec succès.")
            return redirect('liste_medias')
    else:
        form = CDForm()
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'CD'})


@login_required
@user_passes_test(is_bibliothecaire)
def ajouter_jeu(request):
    """Ajouter un jeu de plateau"""
    if request.method == 'POST':
        form = JeuPlateauForm(request.POST)
        if form.is_valid():
            jeu = form.save()
            logger.info(f"Jeu ajouté: {jeu.titre} par {request.user.username}")
            messages.success(request, f"Jeu '{jeu.titre}' ajouté avec succès.")
            return redirect('liste_medias')
    else:
        form = JeuPlateauForm()
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'Jeu de plateau'})


# ============== MODIFIER LES MÉDIAS ==============

@login_required
@user_passes_test(is_bibliothecaire)
def modifier_livre(request, pk):
    """Modifier un livre"""
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        form = LivreForm(request.POST, instance=livre)
        if form.is_valid():
            form.save()
            logger.info(f"Livre modifié: {livre.titre} par {request.user.username}")
            messages.success(request, f"Livre '{livre.titre}' modifié avec succès.")
            return redirect('liste_medias')
    else:
        form = LivreForm(instance=livre)
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'Livre', 'action': 'Modifier'})


@login_required
@user_passes_test(is_bibliothecaire)
def modifier_dvd(request, pk):
    """Modifier un DVD"""
    dvd = get_object_or_404(DVD, pk=pk)
    if request.method == 'POST':
        form = DVDForm(request.POST, instance=dvd)
        if form.is_valid():
            form.save()
            logger.info(f"DVD modifié: {dvd.titre} par {request.user.username}")
            messages.success(request, f"DVD '{dvd.titre}' modifié avec succès.")
            return redirect('liste_medias')
    else:
        form = DVDForm(instance=dvd)
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'DVD', 'action': 'Modifier'})


@login_required
@user_passes_test(is_bibliothecaire)
def modifier_cd(request, pk):
    """Modifier un CD"""
    cd = get_object_or_404(CD, pk=pk)
    if request.method == 'POST':
        form = CDForm(request.POST, instance=cd)
        if form.is_valid():
            form.save()
            logger.info(f"CD modifié: {cd.titre} par {request.user.username}")
            messages.success(request, f"CD '{cd.titre}' modifié avec succès.")
            return redirect('liste_medias')
    else:
        form = CDForm(instance=cd)
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'CD', 'action': 'Modifier'})


@login_required
@user_passes_test(is_bibliothecaire)
def modifier_jeu(request, pk):
    """Modifier un jeu de plateau"""
    jeu = get_object_or_404(JeuPlateau, pk=pk)
    if request.method == 'POST':
        form = JeuPlateauForm(request.POST, instance=jeu)
        if form.is_valid():
            form.save()
            logger.info(f"Jeu modifié: {jeu.titre} par {request.user.username}")
            messages.success(request, f"Jeu '{jeu.titre}' modifié avec succès.")
            return redirect('liste_medias')
    else:
        form = JeuPlateauForm(instance=jeu)
    return render(request, 'mediatheque/form_media.html', {'form': form, 'type_media': 'Jeu de plateau', 'action': 'Modifier'})


# ============== SUPPRIMER LES MÉDIAS ==============

@login_required
@user_passes_test(is_bibliothecaire)
def supprimer_livre(request, pk):
    """Supprimer un livre"""
    livre = get_object_or_404(Livre, pk=pk)
    if request.method == 'POST':
        titre = livre.titre
        logger.info(f"Livre supprimé: {titre} par {request.user.username}")
        livre.delete()
        messages.success(request, f"Livre '{titre}' supprimé avec succès.")
        return redirect('liste_medias')
    return render(request, 'mediatheque/confirmer_suppression.html', {'objet': livre, 'type': 'livre'})


@login_required
@user_passes_test(is_bibliothecaire)
def supprimer_dvd(request, pk):
    """Supprimer un DVD"""
    dvd = get_object_or_404(DVD, pk=pk)
    if request.method == 'POST':
        titre = dvd.titre
        logger.info(f"DVD supprimé: {titre} par {request.user.username}")
        dvd.delete()
        messages.success(request, f"DVD '{titre}' supprimé avec succès.")
        return redirect('liste_medias')
    return render(request, 'mediatheque/confirmer_suppression.html', {'objet': dvd, 'type': 'DVD'})


@login_required
@user_passes_test(is_bibliothecaire)
def supprimer_cd(request, pk):
    """Supprimer un CD"""
    cd = get_object_or_404(CD, pk=pk)
    if request.method == 'POST':
        titre = cd.titre
        logger.info(f"CD supprimé: {titre} par {request.user.username}")
        cd.delete()
        messages.success(request, f"CD '{titre}' supprimé avec succès.")
        return redirect('liste_medias')
    return render(request, 'mediatheque/confirmer_suppression.html', {'objet': cd, 'type': 'CD'})


@login_required
@user_passes_test(is_bibliothecaire)
def supprimer_jeu(request, pk):
    """Supprimer un jeu de plateau"""
    jeu = get_object_or_404(JeuPlateau, pk=pk)
    if request.method == 'POST':
        titre = jeu.titre
        logger.info(f"Jeu supprimé: {titre} par {request.user.username}")
        jeu.delete()
        messages.success(request, f"Jeu '{titre}' supprimé avec succès.")
        return redirect('liste_medias')
    return render(request, 'mediatheque/confirmer_suppression.html', {'objet': jeu, 'type': 'jeu de plateau'})


# ============== GESTION DES EMPRUNTS ==============

@login_required
@user_passes_test(is_bibliothecaire)
def liste_emprunts(request):
    """Liste de tous les emprunts"""
    emprunts_en_cours = Emprunt.objects.filter(date_retour_effective__isnull=True)
    emprunts_termines = Emprunt.objects.filter(date_retour_effective__isnull=False)
    logger.info(f"Consultation liste emprunts par {request.user.username}")
    return render(request, 'mediatheque/liste_emprunts.html', {
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_termines': emprunts_termines,
    })


@login_required
@user_passes_test(is_bibliothecaire)
def creer_emprunt(request):
    """Créer un nouvel emprunt"""
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            membre = form.cleaned_data['membre']
            type_media = form.cleaned_data['type_media']

            # Vérifier si le membre peut emprunter
            if not membre.peut_emprunter():
                if membre.a_emprunt_en_retard():
                    messages.error(request, f"{membre} a un emprunt en retard et ne peut pas emprunter.")
                else:
                    messages.error(request, f"{membre} a déjà 3 emprunts en cours.")
                return render(request, 'mediatheque/form_emprunt.html', {'form': form})

            # Récupérer le média sélectionné
            media = None
            if type_media == 'livre':
                media = form.cleaned_data.get('livre')
            elif type_media == 'dvd':
                media = form.cleaned_data.get('dvd')
            elif type_media == 'cd':
                media = form.cleaned_data.get('cd')

            if not media:
                messages.error(request, "Veuillez sélectionner un média.")
                return render(request, 'mediatheque/form_emprunt.html', {'form': form})

            # Vérifier si le média a des exemplaires disponibles
            if not media.est_disponible():
                messages.error(request, f"Aucun exemplaire de '{media.titre}' n'est disponible.")
                return render(request, 'mediatheque/form_emprunt.html', {'form': form})

            # Créer l'emprunt
            emprunt = Emprunt(membre=membre)
            if type_media == 'livre':
                emprunt.livre = media
            elif type_media == 'dvd':
                emprunt.dvd = media
            elif type_media == 'cd':
                emprunt.cd = media

            emprunt.save()

            logger.info(f"Emprunt créé: {media.titre} pour {membre} par {request.user.username}")
            messages.success(request, f"Emprunt de '{media.titre}' créé pour {membre}.")
            return redirect('liste_emprunts')
    else:
        form = EmpruntForm()
    return render(request, 'mediatheque/form_emprunt.html', {'form': form})


@login_required
@user_passes_test(is_bibliothecaire)
def retourner_emprunt(request, pk):
    """Enregistrer le retour d'un emprunt"""
    emprunt = get_object_or_404(Emprunt, pk=pk)

    if emprunt.date_retour_effective:
        messages.warning(request, "Cet emprunt a déjà été retourné.")
        return redirect('liste_emprunts')

    if request.method == 'POST':
        emprunt.date_retour_effective = timezone.now().date()
        emprunt.save()

        media = emprunt.get_media()
        logger.info(f"Emprunt retourné: {media.titre} par {emprunt.membre} - {request.user.username}")
        messages.success(request, f"Retour de '{media.titre}' enregistré.")
        return redirect('liste_emprunts')

    return render(request, 'mediatheque/confirmer_retour.html', {'emprunt': emprunt})


@login_required
@user_passes_test(is_bibliothecaire)
def creer_emprunt_livre(request, pk):
    """Créer un emprunt pour un livre spécifique"""
    livre = get_object_or_404(Livre, pk=pk)
    membres = Membre.objects.filter(actif=True)

    if not livre.est_disponible():
        messages.error(request, f"Aucun exemplaire de '{livre.titre}' n'est disponible.")
        return redirect('liste_medias')

    if request.method == 'POST':
        membre_id = request.POST.get('membre')
        membre = get_object_or_404(Membre, pk=membre_id)

        if not membre.peut_emprunter():
            if membre.a_emprunt_en_retard():
                messages.error(request, f"{membre} a un emprunt en retard.")
            else:
                messages.error(request, f"{membre} a déjà 3 emprunts en cours.")
            return render(request, 'mediatheque/form_emprunt_direct.html', {'media': livre, 'type_media': 'livre', 'membres': membres})

        emprunt = Emprunt(membre=membre, livre=livre)
        emprunt.save()

        logger.info(f"Emprunt créé: {livre.titre} pour {membre} par {request.user.username}")
        messages.success(request, f"Emprunt de '{livre.titre}' créé pour {membre}.")
        return redirect('liste_medias')

    return render(request, 'mediatheque/form_emprunt_direct.html', {'media': livre, 'type_media': 'livre', 'membres': membres})


@login_required
@user_passes_test(is_bibliothecaire)
def creer_emprunt_dvd(request, pk):
    """Créer un emprunt pour un DVD spécifique"""
    dvd = get_object_or_404(DVD, pk=pk)
    membres = Membre.objects.filter(actif=True)

    if not dvd.est_disponible():
        messages.error(request, f"Aucun exemplaire de '{dvd.titre}' n'est disponible.")
        return redirect('liste_medias')

    if request.method == 'POST':
        membre_id = request.POST.get('membre')
        membre = get_object_or_404(Membre, pk=membre_id)

        if not membre.peut_emprunter():
            if membre.a_emprunt_en_retard():
                messages.error(request, f"{membre} a un emprunt en retard.")
            else:
                messages.error(request, f"{membre} a déjà 3 emprunts en cours.")
            return render(request, 'mediatheque/form_emprunt_direct.html', {'media': dvd, 'type_media': 'dvd', 'membres': membres})

        emprunt = Emprunt(membre=membre, dvd=dvd)
        emprunt.save()

        logger.info(f"Emprunt créé: {dvd.titre} pour {membre} par {request.user.username}")
        messages.success(request, f"Emprunt de '{dvd.titre}' créé pour {membre}.")
        return redirect('liste_medias')

    return render(request, 'mediatheque/form_emprunt_direct.html', {'media': dvd, 'type_media': 'dvd', 'membres': membres})


@login_required
@user_passes_test(is_bibliothecaire)
def creer_emprunt_cd(request, pk):
    """Créer un emprunt pour un CD spécifique"""
    cd = get_object_or_404(CD, pk=pk)
    membres = Membre.objects.filter(actif=True)

    if not cd.est_disponible():
        messages.error(request, f"Aucun exemplaire de '{cd.titre}' n'est disponible.")
        return redirect('liste_medias')

    if request.method == 'POST':
        membre_id = request.POST.get('membre')
        membre = get_object_or_404(Membre, pk=membre_id)

        if not membre.peut_emprunter():
            if membre.a_emprunt_en_retard():
                messages.error(request, f"{membre} a un emprunt en retard.")
            else:
                messages.error(request, f"{membre} a déjà 3 emprunts en cours.")
            return render(request, 'mediatheque/form_emprunt_direct.html', {'media': cd, 'type_media': 'cd', 'membres': membres})

        emprunt = Emprunt(membre=membre, cd=cd)
        emprunt.save()

        logger.info(f"Emprunt créé: {cd.titre} pour {membre} par {request.user.username}")
        messages.success(request, f"Emprunt de '{cd.titre}' créé pour {membre}.")
        return redirect('liste_medias')

    return render(request, 'mediatheque/form_emprunt_direct.html', {'media': cd, 'type_media': 'cd', 'membres': membres})
