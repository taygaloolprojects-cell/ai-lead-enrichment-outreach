# Automated B2B Lead Enrichment & Personalized Outreach Pipeline

An end-to-end B2B lead qualification and outreach automation built with **Make.com**, **Python (FastAPI + Pydantic)**, and **Google Workspace**. It eliminates manual lead triage by automatically scoring inbound leads, generating tailored outreach emails, routing high-value prospects for immediate outreach, and logging lower-priority leads into a nurture pipeline.

---

## Business Problem & Solution

Sales teams lose hours manually researching inbound leads, qualifying company domains, and writing personalized first-touch emails—causing slow response times on high-intent prospects.

**How This System Solves It:**
* **Instant Triage & Scoring:** Evaluates incoming leads (`0–100` score) based on decision-maker seniority, corporate vs. personal email domains, company website presence, and intent notes.
* **Structured AI & Rule-Based Copywriting:** Generates a concise company snapshot, pain-point hypothesis, custom subject line, and ready-to-send outreach draft via a validated FastAPI microservice.
* **Automated Multi-Path Routing:** High-priority leads (`HIGH`) are logged to a priority CRM sheet and sent a personalized email immediately, while lower-priority leads are routed to a separate nurture sheet without cluttering the sales inbox.

---

## Architecture & Workflow

```text
Google Sheets (Inbound_Leads)
        │
        ▼
Make.com Trigger (Watch New Rows)
        │
        ▼
HTTP POST /enrich-lead (FastAPI + Pydantic Validation)
        │
        ▼
Make.com Conditional Router
   ├──► [Priority = HIGH] ──► Google Sheets (High_Priority_Leads) ──► Gmail (Send Personalized Outreach)
   └──► [Priority != HIGH] ─► Google Sheets (Nurture_Leads)