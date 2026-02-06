from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class Media(models.Model):
    """Classe mère abstraite pour tous les médias empruntables"""
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=200, blank=True, default='')
    nombre_exemplaires = models.PositiveIntegerField(default=1)
    date_ajout = models.DateField(auto_now_add=True)
    disponible = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.titre} - {self.auteur}"


class Livre(Media):
    """Livre héritant de Media"""

    class Meta:
        verbose_name = "Livre"
        verbose_name_plural = "Livres"

    def emprunts_en_cours(self):
        """Retourne le nombre d'emprunts en cours pour ce livre"""
        return self.emprunt_set.filter(date_retour_effective__isnull=True).count()

    def exemplaires_disponibles(self):
        """Retourne le nombre d'exemplaires disponibles"""
        return self.nombre_exemplaires - self.emprunts_en_cours()

    def est_disponible(self):
        """Vérifie si au moins un exemplaire est disponible"""
        return self.exemplaires_disponibles() > 0


class DVD(Media):
    """DVD héritant de Media"""
    duree = models.PositiveIntegerField(help_text="Durée en minutes")

    class Meta:
        verbose_name = "DVD"
        verbose_name_plural = "DVDs"

    def emprunts_en_cours(self):
        """Retourne le nombre d'emprunts en cours pour ce DVD"""
        return self.emprunt_set.filter(date_retour_effective__isnull=True).count()

    def exemplaires_disponibles(self):
        """Retourne le nombre d'exemplaires disponibles"""
        return self.nombre_exemplaires - self.emprunts_en_cours()

    def est_disponible(self):
        """Vérifie si au moins un exemplaire est disponible"""
        return self.exemplaires_disponibles() > 0


class CD(Media):
    """CD héritant de Media"""
    nombre_pistes = models.PositiveIntegerField()
    artiste = models.CharField(max_length=200)

    class Meta:
        verbose_name = "CD"
        verbose_name_plural = "CDs"

    def emprunts_en_cours(self):
        """Retourne le nombre d'emprunts en cours pour ce CD"""
        return self.emprunt_set.filter(date_retour_effective__isnull=True).count()

    def exemplaires_disponibles(self):
        """Retourne le nombre d'exemplaires disponibles"""
        return self.nombre_exemplaires - self.emprunts_en_cours()

    def est_disponible(self):
        """Vérifie si au moins un exemplaire est disponible"""
        return self.exemplaires_disponibles() > 0


class JeuPlateau(models.Model):
    """Jeu de plateau - consultation uniquement, non empruntable"""
    titre = models.CharField(max_length=200)
    editeur = models.CharField(max_length=200)
    nombre_joueurs_min = models.PositiveIntegerField(default=2)
    nombre_joueurs_max = models.PositiveIntegerField(default=4)
    date_ajout = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Jeu de plateau"
        verbose_name_plural = "Jeux de plateau"

    def __str__(self):
        return f"{self.titre} ({self.nombre_joueurs_min}-{self.nombre_joueurs_max} joueurs)"


class Membre(models.Model):
    """Membre emprunteur de la médiathèque"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_inscription = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def nombre_emprunts_en_cours(self):
        """Retourne le nombre d'emprunts en cours"""
        return self.emprunt_set.filter(date_retour_effective__isnull=True).count()

    def a_emprunt_en_retard(self):
        """Vérifie si le membre a un emprunt en retard"""
        return self.emprunt_set.filter(
            date_retour_effective__isnull=True,
            date_retour_prevue__lt=timezone.now().date()
        ).exists()

    def peut_emprunter(self):
        """Vérifie si le membre peut emprunter (max 3 emprunts, pas de retard)"""
        if self.nombre_emprunts_en_cours() >= 3:
            return False
        if self.a_emprunt_en_retard():
            return False
        return True


class Emprunt(models.Model):
    """Emprunt d'un média par un membre"""
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE)

    # Relations avec les différents types de médias
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, null=True, blank=True)
    dvd = models.ForeignKey(DVD, on_delete=models.CASCADE, null=True, blank=True)
    cd = models.ForeignKey(CD, on_delete=models.CASCADE, null=True, blank=True)

    date_emprunt = models.DateField(auto_now_add=True)
    date_retour_prevue = models.DateField()
    date_retour_effective = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"

    def save(self, *args, **kwargs):
        # Calcul automatique de la date de retour prévue (7 jours)
        if not self.date_retour_prevue:
            self.date_retour_prevue = timezone.now().date() + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        media = self.get_media()
        return f"Emprunt de {media} par {self.membre}"

    def get_media(self):
        """Retourne le média emprunté"""
        if self.livre:
            return self.livre
        elif self.dvd:
            return self.dvd
        elif self.cd:
            return self.cd
        return None

    def est_en_retard(self):
        """Vérifie si l'emprunt est en retard"""
        if self.date_retour_effective:
            return False
        return timezone.now().date() > self.date_retour_prevue
