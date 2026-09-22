from fastapi import APIRouter, HTTPException
from app.schemas.interest_only import InterestOnlyRuleIn, InterestOnlyRuleUpdate
from app.services.mortgage_service import MortgageService

router = APIRouter()

@router.get("/interest-only-rules")
def list_rules():
    with MortgageService() as s:
        return {"items": s.list_interest_only_rules()}

@router.post("/interest-only-rules", status_code=201)
def create_rule(body: InterestOnlyRuleIn):
    with MortgageService() as s:
        return s.create_interest_only_rule(body.name, body.interest_only_months, body.enabled)

@router.put("/interest-only-rules/{rule_id}")
def update_rule(rule_id: int, body: InterestOnlyRuleUpdate):
    with MortgageService() as s:
        row = s.update_interest_only_rule(rule_id, body.name, body.interest_only_months, body.enabled)
        if not row:
            raise HTTPException(404)
        return row

@router.post("/interest-only-rules/{rule_id}/disable")
def disable_rule(rule_id: int):
    with MortgageService() as s:
        row = s.set_interest_only_rule_enabled(rule_id, False)
        if not row:
            raise HTTPException(404)
        return row

@router.post("/interest-only-rules/{rule_id}/enable")
def enable_rule(rule_id: int):
    with MortgageService() as s:
        row = s.set_interest_only_rule_enabled(rule_id, True)
        if not row:
            raise HTTPException(404)
        return row
