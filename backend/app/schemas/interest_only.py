from pydantic import BaseModel, Field

class InterestOnlyRuleIn(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    interest_only_months: int = Field(gt=0, le=599)
    enabled: bool = True

class InterestOnlyRuleUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    interest_only_months: int = Field(gt=0, le=599)
    enabled: bool
