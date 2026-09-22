from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules import interest_only as interest_only_module
from app.repositories import interest_only as interest_only_repo
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def list_interest_only_rules(self): return interest_only_repo.list_all(self._c)
    def create_interest_only_rule(self, name, interest_only_months, enabled=True):
        return interest_only_repo.create(self._c, name, interest_only_months, enabled)
    def update_interest_only_rule(self, rid, name, interest_only_months, enabled):
        if not interest_only_repo.get(self._c, rid): return None
        return interest_only_repo.update(self._c, rid, name, interest_only_months, enabled)
    def set_interest_only_rule_enabled(self, rid, enabled):
        if not interest_only_repo.get(self._c, rid): return None
        return interest_only_repo.set_enabled(self._c, rid, enabled)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, interest_only=False, interest_only_months=None):
        payload = {"principal": principal, "annual_rate": annual_rate, "months": months}
        if interest_only:
            k = interest_only_module.validate_k(interest_only_months, months)
            full = interest_only_module.schedule(principal, annual_rate, months, k)
            out = {key: full[key] for key in ("monthly_payment_io", "monthly_payment_after", "total_interest", "total_payment")}
            out["interest_only"] = True
            out["interest_only_months"] = k
            payload["interest_only"] = True
            payload["interest_only_months"] = k
        else:
            full = equal_payment_schedule(principal, annual_rate, months)
            out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
