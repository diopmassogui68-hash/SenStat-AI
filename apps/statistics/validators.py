from django.core.exceptions import ValidationError

def validate_percentage(value):
    """
    Valide qu'une valeur de pourcentage est comprise entre 0 et 100.
    """
    if value < 0 or value > 100:
        raise ValidationError(
            f"La valeur {value} n'est pas un pourcentage valide (doit être entre 0 et 100)."
        )
