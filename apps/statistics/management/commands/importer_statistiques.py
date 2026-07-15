import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from apps.statistics.models import StatistiqueRegionale
from apps.statistics.validators import validate_percentage

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Importe les statistiques régionales depuis un fichier CSV. (Opération idempotente)"

    def add_arguments(self, parser):
        parser.add_argument('chemin_csv', type=str, help="Chemin vers le fichier CSV à importer")

    def handle(self, *args, **options):
        chemin_csv = options['chemin_csv']
        
        colonnes_attendues = [
            "region", "annee", "population", "taux_urbanisation_pct", 
            "taux_alphabetisation_pct", "taux_chomage_pct", "taux_pauvrete_pct", 
            "acces_internet_pct", "centres_sante", "taux_scolarisation_pct", 
            "production_cerealiere_tonnes"
        ]
        
        colonnes_pct = [
            "taux_urbanisation_pct", "taux_alphabetisation_pct", "taux_chomage_pct", 
            "taux_pauvrete_pct", "acces_internet_pct", "taux_scolarisation_pct"
        ]
        
        stats_created = 0
        stats_updated = 0
        stats_rejected = 0

        try:
            with open(chemin_csv, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Validation stricte des colonnes
                if not reader.fieldnames or not all(col in reader.fieldnames for col in colonnes_attendues):
                    raise CommandError(
                        f"Format de fichier invalide. Les colonnes attendues sont : {', '.join(colonnes_attendues)}"
                    )
                
                for row_number, row in enumerate(reader, start=2):
                    try:
                        # Validation de l'année (2020-2024 selon le cahier des charges)
                        annee = int(row['annee'])
                        if not (2020 <= annee <= 2024):
                            raise ValueError(f"L'année {annee} n'est pas dans la plage autorisée (2020-2024).")
                        
                        # Conversion et validation
                        defaults = {
                            'population': int(row['population']),
                            'centres_sante': int(row['centres_sante']),
                            'production_cerealiere_tonnes': float(row['production_cerealiere_tonnes']),
                        }
                        
                        # Validation des pourcentages (0-100)
                        for col in colonnes_pct:
                            val_pct = float(row[col])
                            validate_percentage(val_pct)
                            defaults[col] = val_pct
                        
                        # Maintient l'idempotence avec update_or_create (clé: region + annee)
                        obj, created = StatistiqueRegionale.objects.update_or_create(
                            region=row['region'].strip(),
                            annee=annee,
                            defaults=defaults
                        )
                        
                        if created:
                            stats_created += 1
                        else:
                            stats_updated += 1
                            
                    except (ValueError, ValidationError) as e:
                        self.stderr.write(self.style.WARNING(f"Ligne {row_number} rejetée: {e}"))
                        stats_rejected += 1
                        continue

        except FileNotFoundError:
            raise CommandError(f"Le fichier '{chemin_csv}' est introuvable.")
        except Exception as e:
            raise CommandError(f"Erreur inattendue lors de l'importation: {e}")

        # Rapport final d'exécution
        self.stdout.write(self.style.SUCCESS(
            f"Import terminé ! "
            f"Créés: {stats_created}, "
            f"Mis à jour: {stats_updated}, "
            f"Rejetés: {stats_rejected}."
        ))
