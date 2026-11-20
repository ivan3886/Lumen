from decimal import Decimal, ROUND_HALF_UP

CENTAVO = Decimal("0.01")


def redondear(valor: Decimal) -> Decimal:
    """Redondea a 2 decimales (mitad hacia arriba), como se espera con dinero."""
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)
