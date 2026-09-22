from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.modules.interest_only import interest_only_schedule
from app.repositories import interest_only_rules, loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, rid): return runs.get(self._c, rid)
    def list_interest_only_rules(self, enabled_only=False):
        return interest_only_rules.list_all(self._c, enabled_only)
    def get_interest_only_rule(self, rid):
        return interest_only_rules.get(self._c, rid)
    def create_interest_only_rule(self, name, interest_only_months, months_cap=None):
        if interest_only_months <= 0:
            raise ValueError("interest_only_months")
        if months_cap is not None and interest_only_months >= months_cap:
            raise ValueError("interest_only_months must be less than months")
        return interest_only_rules.insert(self._c, name, interest_only_months)
    def update_interest_only_rule(self, rid, name=None, interest_only_months=None, enabled=None, months_cap=None):
        if not interest_only_rules.get(self._c, rid):
            return None
        if interest_only_months is not None and interest_only_months <= 0:
            raise ValueError("interest_only_months")
        if interest_only_months is not None and months_cap is not None and interest_only_months >= months_cap:
            raise ValueError("interest_only_months must be less than months")
        return interest_only_rules.update(self._c, rid, name, interest_only_months, enabled)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12,
                 interest_only=False, interest_only_months=None, interest_only_rule_id=None):
        if interest_only:
            if interest_only_months is None:
                raise ValueError("interest_only_months")
            full = interest_only_schedule(principal, annual_rate, months, interest_only_months)
            out_keys = (
                "monthly_payment", "monthly_payment_interest_only", "monthly_payment_amortizing",
                "interest_only_months", "total_interest", "total_payment", "segments",
            )
            kind = "schedule_interest_only"
        else:
            full = equal_payment_schedule(principal, annual_rate, months)
            out_keys = ("monthly_payment", "total_interest", "total_payment")
            kind = "schedule"
        out = {k: full[k] for k in out_keys}
        out["interest_only"] = interest_only
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            payload = {
                "principal": principal, "annual_rate": annual_rate, "months": months,
                "interest_only": interest_only,
            }
            if interest_only:
                payload["interest_only_months"] = interest_only_months
                payload["interest_only_rule_id"] = interest_only_rule_id
            rid = runs.insert(self._c, kind, payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
