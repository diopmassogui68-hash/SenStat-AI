from django.core.management.base import BaseCommand
import csv
from apps.statistics.models import StatistiqueRegionale

class Command(BaseCommand):
    help = 'Importe les données statistiques depuis un fichier CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Le chemin vers le fichier CSV')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        # Mappings pour nettoyer les erreurs d'encodage du CSV
        region_mapping = {
            'KAcdougou': 'Kédougou',
            'SAcdhiou': 'Sédhiou',
            'ThiA"s': 'Thiès',
        }

        try:
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                count = 0
                for row in reader:
                    region_raw = row['region']
                    region_clean = region_mapping.get(region_raw, region_raw)
                    
                    obj, created = StatistiqueRegionale.objects.update_or_create(
                        region=region_clean,
                        annee=int(row['annee']),
                        defaults={
                            'population': int(row['population']),
                            'taux_urbanisation_pct': float(row['taux_urbanisation_pct']),
                            'taux_alphabetisation_pct': float(row['taux_alphabetisation_pct']),
                            'taux_chomage_pct': float(row['taux_chomage_pct']),
                            'taux_pauvrete_pct': float(row['taux_pauvrete_pct']),
                            'acces_internet_pct': float(row['acces_internet_pct']),
                            'centres_sante': int(row['centres_sante']),
                            'taux_scolarisation_pct': float(row['taux_scolarisation_pct']),
                            'production_cerealiere_tonnes': float(row['production_cerealiere_tonnes']),
                        }
                    )
                    count += 1
                self.stdout.write(self.style.SUCCESS(f'Import terminé. {count} lignes traitées.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fichier {csv_file} introuvable.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de l\'import: {e}'))
