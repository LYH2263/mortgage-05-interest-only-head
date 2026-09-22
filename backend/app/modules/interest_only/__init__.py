"""只息（先息后本）模块。

前 K 期只还利息、本金为零；第 K+1 期起对剩余本金按等额本息重算。
"""


def interest_only_schedule(principal: float, annual_rate: float, months: int, interest_only_months: int) -> dict:
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
    # 第一段：只息期，月供 = 当期利息，本金为零
    first_pay = P * r
    first_interest_sum = 0.0
    for i in range(1, k + 1):
        interest = bal * r
        rows.append({
            "period": i,
            "payment": round(interest, 2),
            "principal": 0.0,
            "interest": round(interest, 2),
            "balance": round(bal, 2),
            "segment": "interest_only",
        })
        first_interest_sum += interest
    # 第二段：剩余本金在剩余期限内按等额本息重算
    rest_n = n - k
    if r == 0:
        second_pay = P / rest_n
    else:
        second_pay = P * r * (1 + r) ** rest_n / ((1 + r) ** rest_n - 1)
    second_interest_sum = 0.0
    for j in range(1, rest_n + 1):
        i = k + j
        interest = bal * r
        principal_part = second_pay - interest
        if j == rest_n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = second_pay
        bal = max(0.0, bal - principal_part)
        second_interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
            "segment": "amortizing",
        })
    interest_sum = first_interest_sum + second_interest_sum
    return {
        "monthly_payment": round(second_pay, 2),
        "monthly_payment_interest_only": round(first_pay, 2),
        "monthly_payment_amortizing": round(second_pay, 2),
        "interest_only_months": k,
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "segments": [
            {"name": "interest_only", "label": "只息期", "periods": k, "monthly_payment": round(first_pay, 2)},
            {"name": "amortizing", "label": "等额本息期", "periods": rest_n, "monthly_payment": round(second_pay, 2)},
        ],
        "rows": rows,
    }
