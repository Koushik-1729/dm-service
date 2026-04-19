# Autonomous Marketing OS Plan

## Goal

Transform `marketing-service` from a WhatsApp-first marketing automation MVP into an autonomous performance marketing operating system that:

- ingests customer and campaign events in real time
- tracks each user across registration, follow-up, conversion, and revenue
- predicts conversion and revenue outcomes
- decides the next best marketing action automatically
- executes across channels
- measures ROAS and feeds results back into the models

## Product North Star

For each business, the platform should answer these questions continuously:

- Which channels are driving revenue right now?
- Which users are most likely to convert?
- Which users are dropping off and why?
- What follow-up or campaign action should happen next?
- Where should the next dollar of budget go?

## MVP Sequence

### Stage 1: Single-channel closed loop

Start with one narrow use case:

- Meta / Facebook lead ads for SMBs
- track ad click -> registration -> thank-you -> follow-up -> conversion -> revenue
- run AI-assisted follow-up and attribution
- show per-campaign revenue and ROAS

Success criteria:

- every lead gets a stable external identifier
- conversion events can be linked back to campaign and channel
- system can trigger follow-up for non-converters
- dashboard can show cost, leads, conversions, revenue, ROAS

### Stage 2: Decisioning MVP

Add a policy engine that chooses:

- follow-up timing
- follow-up message type
- incentive type
- campaign pause/continue decisions
- budget shift suggestions

Success criteria:

- measurable lift in conversion rate vs baseline follow-up logic
- measurable reduction in wasted spend

### Stage 3: Multi-channel growth OS

Expand to:

- Google Ads
- Instagram / Meta organic + paid
- WhatsApp
- email / SMS
- landing-page events

Success criteria:

- cross-channel attribution
- unified customer journey
- next-best-action decisions across channels

## System Architecture

### 1. Event layer

All meaningful actions become events:

- `ad_clicked`
- `landing_page_viewed`
- `registration_completed`
- `thank_you_sent`
- `followup_sent`
- `followup_opened`
- `survey_completed`
- `purchase_completed`
- `service_booked`
- `lead_marked_lost`
- `refund_issued`
- `campaign_paused`
- `budget_changed`

Every event should carry:

- `event_id`
- `event_type`
- `event_time`
- `tenant_id`
- `business_id`
- `user_id`
- `session_id`
- `channel`
- `campaign_id`
- `adset_id`
- `creative_id`
- `message_id`
- `revenue_amount`
- `currency`
- `metadata`

### 2. Identity layer

Create a stable identity graph:

- external ad click IDs
- form/registration ID
- email
- phone
- WhatsApp number
- CRM/contact ID
- payment/customer ID

This is what makes end-to-end attribution possible.

### 3. Decision layer

The decision engine should produce:

- next best action
- confidence score
- expected conversion lift
- expected revenue impact
- explanation

Possible actions:

- send reminder
- send survey
- send offer
- escalate to human
- pause campaign
- increase budget
- decrease budget
- refresh creative
- retarget user segment

### 4. Prediction layer

Do not rely only on LLMs for prediction.

Use tabular ML models for:

- conversion probability
- dropout probability
- expected revenue
- channel-level ROAS forecast
- time-to-conversion prediction

Recommended starting point:

- Logistic Regression for fast baseline
- XGBoost or LightGBM for production tabular models

### 5. LLM reasoning layer

Use LLMs for:

- strategy generation
- experimentation ideas
- anomaly explanation
- audience summarization
- message generation
- report generation
- decision explanation

### 6. Execution layer

Channel adapters should support:

- fetch performance
- launch campaign
- update budget
- pause/resume campaign
- send follow-up
- record delivery/open/click

## Recommended Google Cloud Stack

### Ingestion and orchestration

- Pub/Sub for event bus
- Cloud Run for stateless services and webhook handlers
- Cloud Scheduler for cron-like jobs
- Cloud Tasks for retryable action delivery

### Storage and analytics

- Cloud SQL for transactional app state
- BigQuery for event warehouse, attribution analysis, cohort analysis, and model features
- Cloud Storage for raw files, exports, and training artifacts

### AI and ML

- Vertex AI for model hosting, pipelines, and managed training
- Gemini on Vertex AI for LLM tasks
- Vertex AI Pipelines for retraining and evaluation

### Monitoring

- Cloud Logging
- Cloud Monitoring
- BigQuery audit / analytics tables for decision outcomes

## Model Strategy

### Premium reasoning model

Use for:

- strategy generation
- budget reallocation decisions
- root-cause analysis
- experiment planning

Options:

- GPT-5.4
- Gemini 2.5 Pro

### Cheap fast model

Use for:

- event classification
- follow-up drafting
- lead summarization
- survey analysis
- report generation

Options:

- GPT-5.4 mini
- Gemini 2.5 Flash

### Ultra-low-cost background model

Use for:

- tagging
- normalization
- fallback enrichment
- bulk summarization

Options:

- GPT-5.4 nano
- Gemini 2.5 Flash-Lite

## Recommended First Production Routing

- `onboarding_service`: cheap fast model
- `strategy_service`: premium reasoning model
- `content_service`: cheap fast model, premium for campaign launches only
- `optimization_service`: premium reasoning for decisions, cheap fast for reporting
- new `decision_service`: premium reasoning + ML scores
- new `feature_service`: no LLM, pure feature generation
- new `prediction_service`: XGBoost/LightGBM models on Vertex AI

## Changes Needed In This Repository

### Keep

- hexagonal architecture
- service separation
- outbound adapter pattern
- WhatsApp orchestration
- strategy/content/execution split

### Add

- event ingestion module
- identity resolution service
- feature store / feature builder
- prediction service
- decision service
- attribution pipeline
- dashboard/report APIs
- ad platform adapters
- experiment tracking

### Existing services that need expansion

- `AttributionService`
  - move from tag parsing to real event-join attribution

- `LeadService`
  - extend from lead capture to lifecycle state machine

- `OptimizationService`
  - move from reporting to actual action selection

- `ExecutionService`
  - add campaign update/pause/budget controls for paid channels

## Data Model Additions

Add at least these new entities:

- `users`
- `user_identities`
- `marketing_events`
- `conversions`
- `revenue_events`
- `decision_logs`
- `model_predictions`
- `budget_actions`
- `channel_accounts`
- `campaign_performance_snapshots`
- `experiments`
- `experiment_variants`

## Delivery Roadmap

### Phase 1: Foundation

- add event table and ingestion API
- add stable user identity resolution
- add registration/conversion/revenue event types
- store source metadata across all touchpoints

### Phase 2: Closed-loop SMB funnel

- implement thank-you flow
- implement no-conversion follow-up flow
- add survey capture for drop-off reasons
- add revenue linking back to user and campaign

### Phase 3: Prediction

- build baseline feature extraction in BigQuery
- train first conversion model
- train dropout-risk model
- expose model scores to decision engine

### Phase 4: Decision engine

- define action policy schema
- combine model scores + rules + business constraints
- log every decision and outcome

### Phase 5: Autonomous paid media

- integrate Meta Ads
- ingest spend + conversion data
- enable budget and pause/resume actions
- roll out with safety guardrails and approval thresholds

### Phase 6: Multi-channel expansion

- Google Ads
- email/SMS
- landing page instrumentation
- richer attribution

## Guardrails

Autonomy should be progressive:

- supervised mode: recommendations only
- assisted mode: auto-send follow-ups, human approves spend changes
- autonomous mode: bounded budget and policy-driven execution

Hard rules:

- never exceed account-level daily budget caps
- require approval for first launch in a new channel
- block risky claims in regulated sectors
- log every automated action with reason and model version

## MVP Success Metrics

Measure from day one:

- cost per lead
- lead-to-conversion rate
- revenue per campaign
- ROAS
- follow-up response rate
- time to first follow-up
- dropout rate by step
- budget wasted on non-converting campaigns
- lift vs manual baseline

## Build Principle

The correct center of the system is:

`events -> features -> prediction -> decision -> action -> measurement -> learning`

Not:

`prompt -> content -> report`
