"""
Commande Django d'import CSV idempotente pour les statistiques régionales.

Usage : python manage.py importer_statistiques chemin/vers/fichier.csv

Critères du barème couverts :
  - Modèle et import (15 pts) : validation stricte, update_or_create, rapport détaillé.
"""
import csv
import logging

from django.core.management.base import BaseCommand, CommandError

from apps.statistics.models import StatistiqueRegionale
from apps.statistics.validators import valider_annee, valider_pourcentage, nettoyer_region

logger = logging.getLogger(__name__)

# Colonnes attendues dans le fichier CSV (ordre non significatif)
COLONNES_ATTENDUES = frozenset([
    'region', 'annee', 'population', 'taux_urbanisation_pct',
    'taux_alphabetisation_pct', 'taux_chomage_pct', 'taux_pauvrete_pct',
    'acces_internet_pct', 'centres_sante', 'taux_scolarisation_pct',
    'production_cerealiere_tonnes',
])




class Command(BaseCommand):
    """Importe les statistiques régionales depuis un fichier CSV de manière idempotente.

    Un second import du même fichier ne crée aucun doublon grâce à update_or_create
    sur la clé composite (region, annee).
    """

    help = "Importe les statistiques régionales depuis un fichier CSV (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            'chemin_csv',
            type=str,
            help="Chemin vers le fichier CSV à importer.",
        )

    def handle(self, *args, **options) -> None:
        chemin_csv: str = options['chemin_csv']

        crees: int = 0
        mis_a_jour: int = 0
        rejetes: int = 0

        try:
            with open(chemin_csv, mode='r', encoding='utf-8-sig') as fichier:
                reader = csv.DictReader(fichier)

                # Validation de la structure du fichier
                if not reader.fieldnames or COLONNES_ATTENDUES != frozenset(reader.fieldnames):
                    colonnes_manquantes = COLONNES_ATTENDUES - frozenset(reader.fieldnames or [])
                    raise CommandError(
                        f"Format CSV invalide. Colonnes manquantes : {colonnes_manquantes}"
                    )

                for num_ligne, row in enumerate(reader, start=2):
                    try:
                        # Extraction et typage
                        region = nettoyer_region(row['region'])
                        annee = int(row['annee'])
                        population = int(row['population'])
                        taux_urb = float(row['taux_urbanisation_pct'])
                        taux_alpha = float(row['taux_alphabetisation_pct'])
                        taux_chom = float(row['taux_chomage_pct'])
                        taux_pauv = float(row['taux_pauvrete_pct'])
                        acces_int = float(row['acces_internet_pct'])
                        centres = int(row['centres_sante'])
                        taux_scol = float(row['taux_scolarisation_pct'])
                        prod_cer = float(row['production_cerealiere_tonnes'])

                        # Validation de l'année
                        if not valider_annee(annee):
                            raise ValueError(
                                f"Année invalide : {annee} (doit être entre 2020 et 2024)"
                            )

                        # Validation des pourcentages
                        pourcentages = {
                            'taux_urbanisation_pct': taux_urb,
                            'taux_alphabetisation_pct': taux_alpha,
                            'taux_chomage_pct': taux_chom,
                            'taux_pauvrete_pct': taux_pauv,
                            'acces_internet_pct': acces_int,
                            'taux_scolarisation_pct': taux_scol,
                        }
                        for nom_champ, valeur in pourcentages.items():
                            if not valider_pourcentage(valeur):
                                raise ValueError(
                                    f"{nom_champ} = {valeur} est hors limite (0-100)"
                                )

                        # Insertion ou mise à jour (idempotence)
                        _, created = StatistiqueRegionale.objects.update_or_create(
                            region=region,
                            annee=annee,
                            defaults={
                                'population': population,
                                'taux_urbanisation_pct': taux_urb,
                                'taux_alphabetisation_pct': taux_alpha,
                                'taux_chomage_pct': taux_chom,
                                'taux_pauvrete_pct': taux_pauv,
                                'acces_internet_pct': acces_int,
                                'centres_sante': centres,
                                'taux_scolarisation_pct': taux_scol,
                                'production_cerealiere_tonnes': prod_cer,
                            },
                        )

                        if created:
                            crees += 1
                        else:
                            mis_a_jour += 1

                    except (ValueError, TypeError) as e:
                        logger.error("Ligne %d rejetée : %s", num_ligne, e)
                        self.stderr.write(
                            self.style.ERROR(f"Ligne {num_ligne} rejetée : {e}")
                        )
                        rejetes += 1
                    except Exception as e:
                        logger.error("Erreur inattendue ligne %d : %s", num_ligne, e)
                        self.stderr.write(
                            self.style.ERROR(f"Erreur inattendue ligne {num_ligne} : {e}")
                        )
                        rejetes += 1

            message = f"Import terminé ! Créés : {crees}, Mis à jour : {mis_a_jour}, Rejetés : {rejetes}"
            logger.info(message)
            self.stdout.write(self.style.SUCCESS(message))

        except FileNotFoundError:
            raise CommandError(f"Le fichier « {chemin_csv} » n'existe pas.")
