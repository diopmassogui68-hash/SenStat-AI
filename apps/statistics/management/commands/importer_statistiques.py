import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from apps.statistics.models import StatistiqueRegionale
from apps.statistics.validators import valider_annee, valider_pourcentage, nettoyer_region

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Importe les statistiques régionales à partir d\'un fichier CSV de manière idempotente.'

    def add_arguments(self, parser):
        parser.add_argument('chemin_csv', type=str, help='Chemin vers le fichier CSV')

    def handle(self, *args, **options):
        chemin_csv = options['chemin_csv']
        
        crees = 0
        mis_a_jour = 0
        rejetes = 0

        colonnes_attendues = [
            'region', 'annee', 'population', 'taux_urbanisation_pct', 
            'taux_alphabetisation_pct', 'taux_chomage_pct', 'taux_pauvrete_pct', 
            'acces_internet_pct', 'centres_sante', 'taux_scolarisation_pct', 
            'production_cerealiere_tonnes'
        ]

        try:
            with open(chemin_csv, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Validation des colonnes
                if not reader.fieldnames or set(colonnes_attendues) != set(reader.fieldnames):
                    raise CommandError(f"Le format du CSV est invalide. Colonnes attendues : {colonnes_attendues}")
                
                for ligne_num, row in enumerate(reader, start=2):
                    try:
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

                        # Validation stricte
                        if not valider_annee(annee):
                            raise ValueError(f"Année invalide: {annee} (doit être entre 2020 et 2024)")
                        
                        pourcentages = [taux_urb, taux_alpha, taux_chom, taux_pauv, acces_int, taux_scol]
                        if not all(valider_pourcentage(p) for p in pourcentages):
                            raise ValueError("Un ou plusieurs pourcentages sont hors limite (0-100).")

                        # update_or_create pour idempotence
                        stat, created = StatistiqueRegionale.objects.update_or_create(
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
                            }
                        )

                        if created:
                            crees += 1
                        else:
                            mis_a_jour += 1

                    except ValueError as e:
                        logger.error(f"Ligne {ligne_num} rejetée : {str(e)}")
                        self.stderr.write(self.style.ERROR(f"Ligne {ligne_num} rejetée : {str(e)}"))
                        rejetes += 1
                    except Exception as e:
                        logger.error(f"Erreur inattendue ligne {ligne_num} : {str(e)}")
                        self.stderr.write(self.style.ERROR(f"Erreur inattendue ligne {ligne_num} : {str(e)}"))
                        rejetes += 1

            self.stdout.write(self.style.SUCCESS(
                f"Import terminé ! Créés: {crees}, Mis à jour: {mis_a_jour}, Rejetés: {rejetes}"
            ))

        except FileNotFoundError:
            raise CommandError(f"Le fichier {chemin_csv} n'existe pas.")
