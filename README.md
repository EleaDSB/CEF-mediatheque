# Mediatheque - Application de gestion de médiathèque

Application web Django permettant de gérer une médiathèque : emprunts de livres, DVDs, CDs et consultation de jeux de plateau.

## Fonctionnalités

### Accès visiteur (sans connexion)
- Consultation de la liste des médias disponibles
- Visualisation du nombre d'exemplaires disponibles

### Accès bibliothécaire (avec connexion)
- Gestion des membres (ajouter, modifier, supprimer)
- Gestion des médias (livres, DVDs, CDs, jeux de plateau)
- Création et suivi des emprunts
- Enregistrement des retours

### Règles métier
- Maximum 3 emprunts simultanés par membre
- Durée d'emprunt : 7 jours
- Blocage des emprunts si retard
- Jeux de plateau : consultation uniquement (non empruntables)

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- PostgreSQL (optionnel, pour la production)

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/EleaDSB/CEF-mediatheque.git
cd CEF-mediatheque
```

### 2. Créer un environnement virtuel (recommandé)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OU
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

#### Option A : SQLite (développement - par défaut)
Aucune configuration nécessaire. SQLite sera utilisé automatiquement.

#### Option B : PostgreSQL (production - avec mot de passe)
1. Créer une base de données PostgreSQL :
```sql
CREATE DATABASE mediatheque_db;
CREATE USER mediatheque_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE mediatheque_db TO mediatheque_user;
```

2. Configurer les variables d'environnement :
```bash
export DB_ENGINE=django.db.backends.postgresql
export DB_NAME=mediatheque_db
export DB_USER=mediatheque_user
export DB_PASSWORD=votre_mot_de_passe
export DB_HOST=localhost
export DB_PORT=5432
```

Ou copier le fichier `.env.example` vers `.env` et le modifier.

### 5. Appliquer les migrations
```bash
python3 manage.py migrate
```

### 6. Charger les données de démonstration
```bash
python3 manage.py loaddata initial_data
```

### 7. Créer un compte bibliothécaire
```bash
python3 manage.py createsuperuser
```

## Lancement

```bash
python3 manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000/

## Tests

Exécuter les tests unitaires :
```bash
python3 manage.py test mediatheque
```

45 tests couvrent les modèles, les règles métier et les vues.

## Structure du projet

```
CEF-mediatheque/
├── core/                   # Configuration Django
│   ├── settings.py         # Paramètres (BDD, sécurité, logs)
│   ├── urls.py
│   └── wsgi.py
├── mediatheque/            # Application principale
│   ├── fixtures/           # Données de test (JSON)
│   │   └── initial_data.json
│   ├── templates/          # Templates HTML
│   ├── models.py           # Modèles de données (POO avec héritage)
│   ├── views.py            # Vues
│   ├── forms.py            # Formulaires
│   ├── urls.py             # Routes
│   └── tests.py            # Tests unitaires (45 tests)
├── requirements.txt        # Dépendances Python
├── .env.example            # Exemple de configuration
├── manage.py
├── RAPPORT_PROJET.txt      # Rapport détaillé du projet
└── README.md
```

## Sécurité

- **Base de données** : Support PostgreSQL avec authentification par mot de passe
- **Variables d'environnement** : Configuration sensible externalisée
- **Authentification** : Système de login pour les bibliothécaires
- **CSRF** : Protection contre les attaques CSRF activée

## Architecture POO

Le projet utilise l'héritage pour les modèles de médias :

```
Media (classe abstraite)
├── Livre
├── DVD
└── CD

JeuPlateau (classe indépendante - non empruntable)

Membre
Emprunt (relation entre Membre et Media)
```

## Données de démonstration

Les fixtures contiennent :
- 4 membres (dont 1 inactif)
- 5 livres
- 4 DVDs
- 4 CDs
- 4 jeux de plateau
- 4 emprunts (1 retourné, 3 en cours)

## Auteur

Elea DSB - Projet de formation Développement Web (CEF)

## Licence

Projet éducatif - Centre Européen de Formation
