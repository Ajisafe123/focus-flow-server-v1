from typing import Optional, Tuple

def calculate_nisab(gold_price_per_gram: Optional[float]) -> Optional[float]:
    if gold_price_per_gram is None:
        return None
    return float(gold_price_per_gram) * 85.0

def calculate_zakat_amount(assets_total: float, savings: float, gold_price_per_gram: Optional[float]) -> Tuple[float, Optional[float]]:
    total = float(assets_total) + float(savings)
    nisab = calculate_nisab(gold_price_per_gram)
    zakat_amount = 0.0
    if nisab is None:
        zakat_amount = round(total * 0.025, 2)
    else:
        zakat_amount = round(total * 0.025, 2) if total >= nisab else 0.0
    return zakat_amount, nisab
