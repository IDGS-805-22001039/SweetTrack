from models import db
from datetime import datetime

def calcular_total_venta(items):
    """
    Calcula el total de una venta
    """
    try:
        total = sum(item.get('precio', 0) * item.get('cantidad', 0) for item in items)
        return round(total, 2)
    except Exception as e:
        print(f"Error calculando total: {str(e)}")
        return 0 