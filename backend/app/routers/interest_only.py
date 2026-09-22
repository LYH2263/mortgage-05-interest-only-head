from fastapi import APIRouter, HTTPException
from app.schemas.schedule import RuleCreate, RuleUpdate
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/interest-only-rules")
def list_rules():
    with MortgageService() as s:
        return {"items": s.list_interest_only_rules()}
@router.post("/interest-only-rules", status_code=201)
def create_rule(body: RuleCreate):
    with MortgageService() as s:
        try:
            return s.create_interest_only_rule(body.name, body.interest_only_months)
        except ValueError:
            raise HTTPException(400, "interest_only_months invalid")
@router.patch("/interest-only-rules/{rule_id}")
def update_rule(rule_id: int, body: RuleUpdate):
    with MortgageService() as s:
        try:
            row = s.update_interest_only_rule(
                rule_id, body.name, body.interest_only_months, body.enabled,
            )
        except ValueError:
            raise HTTPException(400, "interest_only_months invalid")
        if not row:
            raise HTTPException(404)
        return row
@router.post("/interest-only-rules/{rule_id}/disable")
def disable_rule(rule_id: int):
    with MortgageService() as s:
        row = s.update_interest_only_rule(rule_id, enabled=False)
        if not row:
            raise HTTPException(404)
        return row
