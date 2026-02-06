from django import forms
from .models import Membre, Livre, DVD, CD, JeuPlateau, Emprunt


class MembreForm(forms.ModelForm):
    """Formulaire pour créer/modifier un membre"""
    class Meta:
        model = Membre
        fields = ['nom', 'prenom', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'prenom': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }


class LivreForm(forms.ModelForm):
    """Formulaire pour ajouter un livre"""
    class Meta:
        model = Livre
        fields = ['titre', 'auteur', 'nombre_exemplaires']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'auteur': forms.TextInput(attrs={'class': 'form-input'}),
            'nombre_exemplaires': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
        }


class DVDForm(forms.ModelForm):
    """Formulaire pour ajouter un DVD"""
    class Meta:
        model = DVD
        fields = ['titre', 'auteur', 'duree', 'nombre_exemplaires']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'auteur': forms.TextInput(attrs={'class': 'form-input'}),
            'duree': forms.NumberInput(attrs={'class': 'form-input'}),
            'nombre_exemplaires': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
        }


class CDForm(forms.ModelForm):
    """Formulaire pour ajouter un CD"""
    class Meta:
        model = CD
        fields = ['titre', 'artiste', 'nombre_pistes', 'nombre_exemplaires']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'artiste': forms.TextInput(attrs={'class': 'form-input'}),
            'nombre_pistes': forms.NumberInput(attrs={'class': 'form-input'}),
            'nombre_exemplaires': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
        }


class JeuPlateauForm(forms.ModelForm):
    """Formulaire pour ajouter un jeu de plateau"""
    class Meta:
        model = JeuPlateau
        fields = ['titre', 'editeur', 'nombre_joueurs_min', 'nombre_joueurs_max']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'editeur': forms.TextInput(attrs={'class': 'form-input'}),
            'nombre_joueurs_min': forms.NumberInput(attrs={'class': 'form-input'}),
            'nombre_joueurs_max': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class EmpruntForm(forms.Form):
    """Formulaire pour créer un emprunt"""
    membre = forms.ModelChoiceField(
        queryset=Membre.objects.all(),
        label="Membre",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    type_media = forms.ChoiceField(
        choices=[('livre', 'Livre'), ('dvd', 'DVD'), ('cd', 'CD')],
        label="Type de média",
        widget=forms.Select(attrs={'class': 'form-input', 'id': 'type_media'})
    )
    livre = forms.ModelChoiceField(
        queryset=Livre.objects.all(),
        required=False,
        label="Livre",
        widget=forms.Select(attrs={'class': 'form-input media-select', 'id': 'select_livre'})
    )
    dvd = forms.ModelChoiceField(
        queryset=DVD.objects.all(),
        required=False,
        label="DVD",
        widget=forms.Select(attrs={'class': 'form-input media-select', 'id': 'select_dvd'})
    )
    cd = forms.ModelChoiceField(
        queryset=CD.objects.all(),
        required=False,
        label="CD",
        widget=forms.Select(attrs={'class': 'form-input media-select', 'id': 'select_cd'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer pour n'afficher que les médias avec des exemplaires disponibles
        self.fields['livre'].queryset = Livre.objects.all()
        self.fields['dvd'].queryset = DVD.objects.all()
        self.fields['cd'].queryset = CD.objects.all()

        # Ajouter le nombre d'exemplaires disponibles dans le label
        livre_choices = [('', '---------')]
        for livre in Livre.objects.all():
            dispo = livre.exemplaires_disponibles()
            if dispo > 0:
                livre_choices.append((livre.pk, f"{livre.titre} ({dispo} dispo)"))
        self.fields['livre'].choices = livre_choices

        dvd_choices = [('', '---------')]
        for dvd in DVD.objects.all():
            dispo = dvd.exemplaires_disponibles()
            if dispo > 0:
                dvd_choices.append((dvd.pk, f"{dvd.titre} ({dispo} dispo)"))
        self.fields['dvd'].choices = dvd_choices

        cd_choices = [('', '---------')]
        for cd in CD.objects.all():
            dispo = cd.exemplaires_disponibles()
            if dispo > 0:
                cd_choices.append((cd.pk, f"{cd.titre} ({dispo} dispo)"))
        self.fields['cd'].choices = cd_choices
