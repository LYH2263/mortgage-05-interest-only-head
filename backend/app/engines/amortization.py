def equal_payment_schedule(principal: float, annual_rate: float, months: int) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }


def interest_only_schedule(principal: float, annual_rate: float, months: int, interest_only_months: int) -> dict:
    """Two-segment schedule: first K periods pay interest only (principal 0),
    then the remaining balance is re-amortized as equal payment over months-K."""
    P = float(principal)
    n = int(months)
    k = int(interest_only_months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if k <= 0 or k >= n:
        raise ValueError("interest_only_months")
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, k + 1):
        interest = bal * r
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(interest, 2),
            "principal": 0.0,
            "interest": round(interest, 2),
            "balance": round(bal, 2),
            "segment": "interest_only",
        })
    m = n - k
    if r == 0:
        pay = bal / m
    else:
        pay = bal * r * (1 + r) ** m / ((1 + r) ** m - 1)
    for j in range(1, m + 1):
        interest = bal * r
        principal_part = pay - interest
        if j == m:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": k + j,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
            "segment": "equal_payment",
        })
    return {
        "monthly_payment_io": round(P * r, 2),
        "monthly_payment_after": round(pay, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
