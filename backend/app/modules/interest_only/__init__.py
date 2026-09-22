"""Interest-only (只息) module: validate K and build two-segment schedules."""
from app.engines.amortization import interest_only_schedule


def validate_k(k, months) -> int:
    """K must be a positive integer strictly less than the total periods."""
    if k is None:
        raise ValueError("interest_only_months required")
    k = int(k)
    if k <= 0 or k >= int(months):
        raise ValueError("interest_only_months must be positive and less than months")
    return k


def schedule(principal, annual_rate, months, k) -> dict:
    return interest_only_schedule(principal, annual_rate, months, validate_k(k, months))
