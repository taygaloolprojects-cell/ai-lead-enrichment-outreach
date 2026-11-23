import os
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Lead Enrichment & Outreach API")


class LeadInput(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    company: str = Field(..., min_length=1)
    website: str = Field(default="")
    role: str = Field(default="Decision Maker")
    notes: str = Field(default="")


class EnrichedLeadOutput(BaseModel):
    company: str
    lead_score: int = Field(..., ge=0, le=100)
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    company_snapshot: str
    pain_point_hypothesis: str
    outreach_subject: str
    outreach_email_draft: str


def score_and_draft_lead(lead: LeadInput) -> EnrichedLeadOutput:
    """
    Rule-based baseline scorer that can be swapped with an LLM call
    while preserving strict Pydantic output validation.
    """
    score = 50
    role_lower = lead.role.lower()

    if any(k in role_lower for k in ["founder", "ceo", "owner", "vp", "director", "head"]):
        score += 25
    if lead.website.strip():
        score += 10
    if any(k in lead.notes.lower() for k in ["urgent", "automation", "scale", "crm", "leads"]):
        score += 10
    if lead.email.lower().endswith(("@gmail.com", "@yahoo.com", "@hotmail.com")):
        score -= 10

    score = max(0, min(100, score))
    priority: Literal["HIGH", "MEDIUM", "LOW"] = (
        "HIGH" if score >= 75 else "MEDIUM" if score >= 45 else "LOW"
    )

    first_name = lead.full_name.strip().split()[0]
    snapshot = (
        f"{lead.company} ({lead.website or 'no website provided'}) — "
        f"contacted by {lead.full_name}, {lead.role}."
    )
    pain_hypothesis = (
        lead.notes.strip()
        if lead.notes.strip()
        else f"Manual bottlenecks in {lead.company}'s lead qualification and follow-up workflow."
    )

    subject = f"Quick idea for {lead.company}'s {lead.role.lower()} workflow"
    draft = (
        f"Hi {first_name},\n\n"
        f"Noticed {lead.company} and looked into how teams at your stage handle {pain_hypothesis.lower()}\n\n"
        f"We help teams automate lead research and personalized follow-ups so reps spend time closing instead of sorting data.\n\n"
        f"Open to a 10-minute walkthrough this week?"
    )

    return EnrichedLeadOutput(
        company=lead.company,
        lead_score=score,
        priority=priority,
        company_snapshot=snapshot,
        pain_point_hypothesis=pain_hypothesis,
        outreach_subject=subject,
        outreach_email_draft=draft,
    )


@app.post("/enrich-lead", response_model=EnrichedLeadOutput)
def enrich_lead_endpoint(lead: LeadInput) -> EnrichedLeadOutput:
    try:
        return score_and_draft_lead(lead)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.enrich_lead:app", host="0.0.0.0", port=port, reload=True)