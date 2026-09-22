from pydantic import BaseModel, Field, model_validator


class RuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    interest_only_months: int = Field(gt=0)


class RuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    interest_only_months: int | None = Field(default=None, gt=0)
    enabled: bool | None = None


class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
    interest_only: bool = False
    # 只息期数 K：须为正且小于总期数。勾选只息时必填，未勾选时忽略。
    interest_only_months: int | None = Field(default=None, gt=0)
    interest_only_rule_id: int | None = None

    @model_validator(mode="after")
    def _check_k(self):
        if self.interest_only:
            if self.interest_only_months is None:
                raise ValueError("interest_only_months required when interest_only enabled")
            if self.interest_only_months >= self.months:
                raise ValueError("interest_only_months must be less than months")
        return self
