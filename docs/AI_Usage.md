# AI-Assisted Workflow

Technical Dashboard Creation in Celonis | Process Mining Seminar | TH Köln | Group 07

## Summary

We used an AI assistant to support documentation, explanation, verification and presentation work. The Celonis work itself (data pools, data models, PQL formulas, dashboards and deployments) was built by the team in Celonis. All AI output was reviewed before use. Every number on the slides was recomputed from the raw data.

This log covers the main tasks. More entries will be added as the project continues.

## Tool

| Item | Value |
|---|---|
| Assistant | Claude (Anthropic) |
| Used for | Drafting, explaining, checking and formatting |
| Not used for | Building the Celonis data pools, data models, views or deployments |

## Tasks

### 1. Runbook

| | |
|---|---|
| **Goal** | A reproducible step-by-step guide from raw files to a deployed dashboard. |
| **What AI did** | Helped structure and draft the runbook: step format (What, Why, Steps, Expected result, If this occurs), the common issues table and the key concepts appendix. |
| **How we checked** | Every step was compared with what we did in Celonis and with our screenshots. Error messages and names were taken from the Celonis interface. |
| **Result** | [`docs/Runbook.md`](Runbook.md) |

### 2. Celonis concepts

| | |
|---|---|
| **Goal** | A clear explanation of how Celonis works for the presentation. |
| **What AI did** | Explained the pipeline (Data Pool, Data Model, Studio, Version, Apps), event logs (case, activity, timestamp), variants and the PQL functions used in our KPIs (COUNT, CALC_THROUGHPUT, REMAP_TIMESTAMPS). |
| **How we checked** | Compared with the course material and the Celonis documentation. |
| **Result** | Speaker notes and Q&A preparation. |

### 3. Object-centric data

| | |
|---|---|
| **Goal** | Explain the object-centric part and the structure of the dataset. |
| **What AI did** | Explained the three file groups: `Events.csv` (what happened and when), `OT_*.csv` (the objects: order, item, package) and `E2O_*.csv` (which event involves which object). Explained convergence and divergence. |
| **How we checked** | Traced order `ord990001` through the files: 10 items, 3 packages, one `place order` event linked to 1 order and 10 items. |
| **Result** | Slides 22 to 30. |

### 4. Data cross-check

| | |
|---|---|
| **Goal** | Make sure every number on the slides is correct. |
| **What AI did** | Compared every figure in the deck with the raw data files. |
| **How we checked** | All figures match: 10,000 cases, 12.48% cancellation rate, 28 resources, 20.17 days order to delivery, 200 orders, 791 items, 128 packages, 2,244 events. |
| **Notes** | The pizza log has 1,278 cases (Celonis rounds to 1.28K). The script shows a minimum throughput of 3.32 days on START TIME; Celonis shows 3.38 days on END TIME. |

### 5. Verification script

| | |
|---|---|
| **Goal** | Recompute the KPIs independently of Celonis. |
| **What AI did** | Wrote [`analysis/verify_kpis.py`](../analysis/verify_kpis.py), which recomputes the KPIs from the raw files with pandas. |
| **How we checked** | Ran the script. Total Cases, Cancellation Rate and Order to Delivery match Celonis exactly. |
| **Result** | Independent proof that our PQL formulas are correct. |

### 6. Slide design

| | |
|---|---|
| **Goal** | A clean and consistent deck. |
| **What AI did** | Fixed text alignment, padding, bullet indents and connector lines. Designed the worked example on slide 30 (one real order, three ways to count) and the layout of this AI slide. Corrected the footer slide numbers. |
| **How we checked** | Reviewed every changed slide in PowerPoint. |
| **Result** | Slides 22 to 30 and 34. |

### 7. Markdown documents

| | |
|---|---|
| **Goal** | Documentation that renders well on GitHub. |
| **What AI did** | Converted the runbook to Markdown without changing its wording, and created this AI log. |
| **How we checked** | Reviewed the rendered pages on GitHub. |
| **Result** | [`docs/Runbook.md`](Runbook.md), [`docs/AI_Usage.md`](AI_Usage.md) |

### 8. Repository

| | |
|---|---|
| **Goal** | A clear project repository for the course. |
| **What AI did** | Proposed the folder structure, wrote the README, extracted the screenshots from the slides, saved the PQL formulas as files and reviewed the repository for mistakes. |
| **How we checked** | Checked every link and image on GitHub. Fixed the issues found in the review (outdated deck, runbook details, screenshot names). |
| **Result** | [github.com/Msuhxn/07_DashboardCelonis](https://github.com/Msuhxn/07_DashboardCelonis) |

## Principles

- AI output was a starting point, never the final answer.
- Numbers were only used after they were checked against the data.
- The Celonis implementation was done by the team.

## To be added

More entries will be added here as the project continues.
