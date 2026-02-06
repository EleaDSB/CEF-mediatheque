from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Livre, DVD, CD, JeuPlateau, Membre, Emprunt


# ============== TESTS DES MODÈLES ==============

class LivreModelTest(TestCase):
    """Tests pour le modèle Livre"""

    def setUp(self):
        self.livre = Livre.objects.create(
            titre="Le Petit Prince",
            auteur="Antoine de Saint-Exupéry",
            nombre_exemplaires=2
        )
        self.membre = Membre.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@test.com"
        )

    def test_creation_livre(self):
        """Test de création d'un livre"""
        self.assertEqual(self.livre.titre, "Le Petit Prince")
        self.assertEqual(self.livre.auteur, "Antoine de Saint-Exupéry")
        self.assertEqual(self.livre.nombre_exemplaires, 2)

    def test_livre_str(self):
        """Test de la représentation string du livre"""
        self.assertEqual(str(self.livre), "Le Petit Prince - Antoine de Saint-Exupéry")

    def test_exemplaires_disponibles_sans_emprunt(self):
        """Test du nombre d'exemplaires disponibles sans emprunt"""
        self.assertEqual(self.livre.exemplaires_disponibles(), 2)

    def test_exemplaires_disponibles_avec_emprunt(self):
        """Test du nombre d'exemplaires disponibles avec un emprunt"""
        Emprunt.objects.create(membre=self.membre, livre=self.livre)
        self.assertEqual(self.livre.exemplaires_disponibles(), 1)

    def test_est_disponible(self):
        """Test de la disponibilité du livre"""
        self.assertTrue(self.livre.est_disponible())

    def test_livre_non_disponible(self):
        """Test livre non disponible quand tous les exemplaires sont empruntés"""
        Emprunt.objects.create(membre=self.membre, livre=self.livre)
        membre2 = Membre.objects.create(nom="Martin", prenom="Paul", email="paul@test.com")
        Emprunt.objects.create(membre=membre2, livre=self.livre)
        self.assertFalse(self.livre.est_disponible())


class DVDModelTest(TestCase):
    """Tests pour le modèle DVD"""

    def setUp(self):
        self.dvd = DVD.objects.create(
            titre="Inception",
            auteur="Christopher Nolan",
            duree=148,
            nombre_exemplaires=1
        )

    def test_creation_dvd(self):
        """Test de création d'un DVD"""
        self.assertEqual(self.dvd.titre, "Inception")
        self.assertEqual(self.dvd.duree, 148)

    def test_dvd_disponibilite(self):
        """Test de la disponibilité du DVD"""
        self.assertTrue(self.dvd.est_disponible())
        self.assertEqual(self.dvd.exemplaires_disponibles(), 1)


class CDModelTest(TestCase):
    """Tests pour le modèle CD"""

    def setUp(self):
        self.cd = CD.objects.create(
            titre="Abbey Road",
            auteur="The Beatles",
            artiste="The Beatles",
            nombre_pistes=17,
            nombre_exemplaires=3
        )

    def test_creation_cd(self):
        """Test de création d'un CD"""
        self.assertEqual(self.cd.titre, "Abbey Road")
        self.assertEqual(self.cd.artiste, "The Beatles")
        self.assertEqual(self.cd.nombre_pistes, 17)

    def test_cd_disponibilite(self):
        """Test de la disponibilité du CD"""
        self.assertTrue(self.cd.est_disponible())
        self.assertEqual(self.cd.exemplaires_disponibles(), 3)


class JeuPlateauModelTest(TestCase):
    """Tests pour le modèle JeuPlateau"""

    def setUp(self):
        self.jeu = JeuPlateau.objects.create(
            titre="Catan",
            editeur="Kosmos",
            nombre_joueurs_min=3,
            nombre_joueurs_max=4
        )

    def test_creation_jeu(self):
        """Test de création d'un jeu de plateau"""
        self.assertEqual(self.jeu.titre, "Catan")
        self.assertEqual(self.jeu.editeur, "Kosmos")
        self.assertEqual(self.jeu.nombre_joueurs_min, 3)
        self.assertEqual(self.jeu.nombre_joueurs_max, 4)

    def test_jeu_str(self):
        """Test de la représentation string du jeu"""
        self.assertEqual(str(self.jeu), "Catan (3-4 joueurs)")


class MembreModelTest(TestCase):
    """Tests pour le modèle Membre"""

    def setUp(self):
        self.membre = Membre.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@test.com"
        )
        self.livre = Livre.objects.create(
            titre="Test Livre",
            nombre_exemplaires=5
        )

    def test_creation_membre(self):
        """Test de création d'un membre"""
        self.assertEqual(self.membre.nom, "Dupont")
        self.assertEqual(self.membre.prenom, "Jean")

    def test_membre_str(self):
        """Test de la représentation string du membre"""
        self.assertEqual(str(self.membre), "Jean Dupont")

    def test_nombre_emprunts_en_cours(self):
        """Test du comptage des emprunts en cours"""
        self.assertEqual(self.membre.nombre_emprunts_en_cours(), 0)
        Emprunt.objects.create(membre=self.membre, livre=self.livre)
        self.assertEqual(self.membre.nombre_emprunts_en_cours(), 1)

    def test_peut_emprunter_nouveau_membre(self):
        """Test qu'un nouveau membre peut emprunter"""
        self.assertTrue(self.membre.peut_emprunter())


class EmpruntModelTest(TestCase):
    """Tests pour le modèle Emprunt"""

    def setUp(self):
        self.membre = Membre.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@test.com"
        )
        self.livre = Livre.objects.create(
            titre="Test Livre",
            nombre_exemplaires=1
        )

    def test_creation_emprunt(self):
        """Test de création d'un emprunt"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre)
        self.assertEqual(emprunt.membre, self.membre)
        self.assertEqual(emprunt.livre, self.livre)

    def test_date_retour_prevue_auto(self):
        """Test que la date de retour prévue est calculée automatiquement (7 jours)"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre)
        date_attendue = timezone.now().date() + timedelta(days=7)
        self.assertEqual(emprunt.date_retour_prevue, date_attendue)

    def test_get_media_livre(self):
        """Test de récupération du média emprunté (livre)"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre)
        self.assertEqual(emprunt.get_media(), self.livre)

    def test_emprunt_non_en_retard(self):
        """Test qu'un nouvel emprunt n'est pas en retard"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre)
        self.assertFalse(emprunt.est_en_retard())


# ============== TESTS DES RÈGLES MÉTIER ==============

class ReglesMetierTest(TestCase):
    """Tests pour les règles métier de la médiathèque"""

    def setUp(self):
        self.membre = Membre.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@test.com"
        )
        self.livre1 = Livre.objects.create(titre="Livre 1", nombre_exemplaires=5)
        self.livre2 = Livre.objects.create(titre="Livre 2", nombre_exemplaires=5)
        self.livre3 = Livre.objects.create(titre="Livre 3", nombre_exemplaires=5)
        self.livre4 = Livre.objects.create(titre="Livre 4", nombre_exemplaires=5)

    def test_max_trois_emprunts(self):
        """Test qu'un membre ne peut pas avoir plus de 3 emprunts"""
        Emprunt.objects.create(membre=self.membre, livre=self.livre1)
        Emprunt.objects.create(membre=self.membre, livre=self.livre2)
        Emprunt.objects.create(membre=self.membre, livre=self.livre3)

        self.assertEqual(self.membre.nombre_emprunts_en_cours(), 3)
        self.assertFalse(self.membre.peut_emprunter())

    def test_membre_avec_retard_bloque(self):
        """Test qu'un membre avec un emprunt en retard est bloqué"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre1)
        # Forcer la date de retour prévue dans le passé
        emprunt.date_retour_prevue = timezone.now().date() - timedelta(days=1)
        emprunt.save()

        self.assertTrue(self.membre.a_emprunt_en_retard())
        self.assertFalse(self.membre.peut_emprunter())

    def test_emprunt_en_retard_detection(self):
        """Test de la détection d'un emprunt en retard"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre1)
        emprunt.date_retour_prevue = timezone.now().date() - timedelta(days=1)
        emprunt.save()

        self.assertTrue(emprunt.est_en_retard())

    def test_emprunt_retourne_pas_en_retard(self):
        """Test qu'un emprunt retourné n'est plus considéré en retard"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre1)
        emprunt.date_retour_prevue = timezone.now().date() - timedelta(days=1)
        emprunt.date_retour_effective = timezone.now().date()
        emprunt.save()

        self.assertFalse(emprunt.est_en_retard())
        self.assertFalse(self.membre.a_emprunt_en_retard())

    def test_exemplaires_multiples(self):
        """Test de la gestion des exemplaires multiples"""
        livre = Livre.objects.create(titre="Livre Multi", nombre_exemplaires=2)
        membre1 = Membre.objects.create(nom="Un", prenom="Membre", email="un@test.com")
        membre2 = Membre.objects.create(nom="Deux", prenom="Membre", email="deux@test.com")

        # Premier emprunt
        Emprunt.objects.create(membre=membre1, livre=livre)
        self.assertEqual(livre.exemplaires_disponibles(), 1)
        self.assertTrue(livre.est_disponible())

        # Deuxième emprunt
        Emprunt.objects.create(membre=membre2, livre=livre)
        self.assertEqual(livre.exemplaires_disponibles(), 0)
        self.assertFalse(livre.est_disponible())


# ============== TESTS DES VUES ==============

class VuesPubliquesTest(TestCase):
    """Tests pour les vues accessibles au public"""

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        """Test d'accès à la page d'accueil"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_liste_medias_accessible(self):
        """Test que la liste des médias est accessible sans connexion"""
        response = self.client.get(reverse('liste_medias'))
        self.assertEqual(response.status_code, 200)


class AuthentificationTest(TestCase):
    """Tests pour l'authentification"""

    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(
            username='biblio',
            password='test1234',
            is_staff=True
        )
        self.membre_user = User.objects.create_user(
            username='membre',
            password='test1234',
            is_staff=False
        )

    def test_login_bibliothecaire_succes(self):
        """Test de connexion réussie pour un bibliothécaire"""
        response = self.client.post(reverse('login_bibliothecaire'), {
            'username': 'biblio',
            'password': 'test1234'
        })
        self.assertRedirects(response, reverse('espace_bibliothecaire'))

    def test_login_bibliothecaire_echec(self):
        """Test de connexion échouée pour un bibliothécaire"""
        response = self.client.post(reverse('login_bibliothecaire'), {
            'username': 'biblio',
            'password': 'mauvais'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "incorrect")

    def test_logout(self):
        """Test de déconnexion"""
        self.client.login(username='biblio', password='test1234')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))


class VuesBibliothecaireTest(TestCase):
    """Tests pour les vues réservées au bibliothécaire"""

    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(
            username='biblio',
            password='test1234',
            is_staff=True
        )
        self.client.login(username='biblio', password='test1234')

    def test_espace_bibliothecaire(self):
        """Test d'accès à l'espace bibliothécaire"""
        response = self.client.get(reverse('espace_bibliothecaire'))
        self.assertEqual(response.status_code, 200)

    def test_liste_membres(self):
        """Test d'accès à la liste des membres"""
        response = self.client.get(reverse('liste_membres'))
        self.assertEqual(response.status_code, 200)

    def test_liste_emprunts(self):
        """Test d'accès à la liste des emprunts"""
        response = self.client.get(reverse('liste_emprunts'))
        self.assertEqual(response.status_code, 200)

    def test_ajouter_membre(self):
        """Test d'ajout d'un membre"""
        response = self.client.post(reverse('ajouter_membre'), {
            'nom': 'Test',
            'prenom': 'User',
            'email': 'test@test.com'
        })
        self.assertEqual(Membre.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_membres'))

    def test_ajouter_livre(self):
        """Test d'ajout d'un livre"""
        response = self.client.post(reverse('ajouter_livre'), {
            'titre': 'Nouveau Livre',
            'auteur': 'Auteur Test',
            'nombre_exemplaires': 2,
            'disponible': True
        })
        self.assertEqual(Livre.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_medias'))

    def test_ajouter_dvd(self):
        """Test d'ajout d'un DVD"""
        response = self.client.post(reverse('ajouter_dvd'), {
            'titre': 'Nouveau DVD',
            'auteur': 'Réalisateur Test',
            'duree': 120,
            'nombre_exemplaires': 1,
            'disponible': True
        })
        self.assertEqual(DVD.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_medias'))

    def test_ajouter_cd(self):
        """Test d'ajout d'un CD"""
        response = self.client.post(reverse('ajouter_cd'), {
            'titre': 'Nouveau CD',
            'auteur': 'Auteur Test',
            'artiste': 'Artiste Test',
            'nombre_pistes': 12,
            'nombre_exemplaires': 1,
            'disponible': True
        })
        self.assertEqual(CD.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_medias'))

    def test_ajouter_jeu(self):
        """Test d'ajout d'un jeu de plateau"""
        response = self.client.post(reverse('ajouter_jeu'), {
            'titre': 'Nouveau Jeu',
            'editeur': 'Editeur Test',
            'nombre_joueurs_min': 2,
            'nombre_joueurs_max': 6
        })
        self.assertEqual(JeuPlateau.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_medias'))


class AccesNonAutoriseTest(TestCase):
    """Tests pour vérifier que les pages protégées sont bien protégées"""

    def setUp(self):
        self.client = Client()
        # Créer un utilisateur non-staff pour tester
        self.membre_user = User.objects.create_user(
            username='membre',
            password='test1234',
            is_staff=False
        )

    def test_liste_membres_non_staff(self):
        """Test que la liste des membres est interdite aux non-staff"""
        self.client.login(username='membre', password='test1234')
        response = self.client.get(reverse('liste_membres'))
        # Redirection vers login car user_passes_test échoue
        self.assertNotEqual(response.status_code, 200)

    def test_ajouter_media_non_staff(self):
        """Test que l'ajout de média est interdit aux non-staff"""
        self.client.login(username='membre', password='test1234')
        response = self.client.get(reverse('ajouter_livre'))
        self.assertNotEqual(response.status_code, 200)

    def test_liste_emprunts_non_staff(self):
        """Test que la liste des emprunts est interdite aux non-staff"""
        self.client.login(username='membre', password='test1234')
        response = self.client.get(reverse('liste_emprunts'))
        self.assertNotEqual(response.status_code, 200)


class GestionEmpruntTest(TestCase):
    """Tests pour la gestion des emprunts"""

    def setUp(self):
        self.client = Client()
        self.bibliothecaire = User.objects.create_user(
            username='biblio',
            password='test1234',
            is_staff=True
        )
        self.client.login(username='biblio', password='test1234')

        self.membre = Membre.objects.create(
            nom="Dupont",
            prenom="Jean",
            email="jean@test.com"
        )
        self.livre = Livre.objects.create(
            titre="Test Livre",
            nombre_exemplaires=2
        )

    def test_creer_emprunt_direct_livre(self):
        """Test de création d'un emprunt direct depuis la liste des médias"""
        response = self.client.post(
            reverse('creer_emprunt_livre', args=[self.livre.pk]),
            {'membre': self.membre.pk}
        )
        self.assertEqual(Emprunt.objects.count(), 1)
        self.assertRedirects(response, reverse('liste_medias'))

    def test_retourner_emprunt(self):
        """Test du retour d'un emprunt"""
        emprunt = Emprunt.objects.create(membre=self.membre, livre=self.livre)

        response = self.client.post(reverse('retourner_emprunt', args=[emprunt.pk]))

        emprunt.refresh_from_db()
        self.assertIsNotNone(emprunt.date_retour_effective)
        self.assertRedirects(response, reverse('liste_emprunts'))

    def test_emprunt_membre_bloque(self):
        """Test qu'un membre bloqué ne peut pas emprunter"""
        # Créer 3 emprunts pour bloquer le membre
        livre2 = Livre.objects.create(titre="Livre 2", nombre_exemplaires=1)
        livre3 = Livre.objects.create(titre="Livre 3", nombre_exemplaires=1)

        Emprunt.objects.create(membre=self.membre, livre=self.livre)
        Emprunt.objects.create(membre=self.membre, livre=livre2)
        Emprunt.objects.create(membre=self.membre, livre=livre3)

        livre4 = Livre.objects.create(titre="Livre 4", nombre_exemplaires=1)
        response = self.client.post(
            reverse('creer_emprunt_livre', args=[livre4.pk]),
            {'membre': self.membre.pk}
        )

        # L'emprunt ne devrait pas être créé (toujours 3)
        self.assertEqual(Emprunt.objects.count(), 3)
