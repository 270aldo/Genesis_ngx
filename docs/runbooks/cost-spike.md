# Runbook: Cost Spike

**Severity**: Warning
**Budget Impact**: Exceeds expected spend
**On-Call**: Platform Team

---

## Symptoms

- Alert: "Genesis NGX - Budget Spike"
- Hourly token usage exceeds threshold
- Billing dashboard shows unexpected increase
- GCP Budget alert triggered

---

## Expected Costs (Q1 Baseline)

| Metric | Expected | Alert Threshold |
|--------|----------|-----------------|
| Monthly spend | $20-50 | $100 |
| Daily spend | $0.70-1.70 | $10 |
| Hourly spend | $0.03-0.07 | $5 |
| Tokens/hour | ~50K | 4M |

---

## Diagnosis Steps

### 1. Identify Source of Spike

```bash
# Check token usage by agent in last hour
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine"
   jsonPayload.tokens_used>0
   timestamp>="2025-01-01T00:00:00Z"' \
  --project=ngx-genesis-prod \
  --limit=100 \
  --format="table(jsonPayload.agent_type,jsonPayload.tokens_used)"
```

### 2. Check for Traffic Anomalies

```bash
# Requests per user in last hour
gcloud logging read \
  'resource.type="cloud_run_revision"
   httpRequest.requestUrl:"/v1/chat"' \
  --project=ngx-genesis-prod \
  --limit=1000 \
  --format="json" | jq -r '.jsonPayload.user_id' | sort | uniq -c | sort -rn | head -20
```

### 3. Check for Infinite Loops

Look for patterns like:
- Same user making >100 requests/hour
- Agent invoking itself repeatedly
- Conversation IDs with >50 messages

```bash
# Messages per conversation
gcloud logging read \
  'jsonPayload.conversation_id!=""' \
  --project=ngx-genesis-prod \
  --limit=1000 \
  --format="json" | jq -r '.jsonPayload.conversation_id' | sort | uniq -c | sort -rn | head -10
```

---

## Resolution Steps

### If Single User Abuse

```bash
# Option 1: Temporarily block user via Supabase
# Set user.app_metadata.blocked = true

# Option 2: Reduce rate limit for user
# Update gateway rate limiting rules
```

### If Agent Loop Detected

1. Identify the looping agent in logs
2. Check recent changes to agent prompts/tools
3. Deploy fix or rollback

```bash
# Rollback to previous agent version
gcloud ai reasoning-engines deploy genesis-ngx-genesis-x \
  --project=ngx-genesis-prod \
  --region=us-central1 \
  --source=gs://ngx-genesis-prod-artifacts/agents/genesis-x-v0.9.0.tar.gz
```

### If DDoS/Bot Traffic

1. Enable Cloud Armor (if not already)
2. Add rate limiting at load balancer level
3. Consider CAPTCHA for suspicious patterns

---

## Cost Control Measures

### Immediate (Stop Bleeding)

```bash
# Set hard budget limit in GCP
gcloud billing budgets update BUDGET_ID \
  --budget-amount=100USD \
  --threshold-rules=1.0=FORECASTED_SPEND
```

### Short-term

- Reduce `max_instances` in Cloud Run
- Lower per-user rate limits
- Implement request budgeting in Gateway

### Long-term

- Implement per-user daily spending caps
- Add cost anomaly detection
- Set up budget alerts at 50%, 80%, 100%

---

## Escalation

| Cost Spike | Action |
|------------|--------|
| 2x normal | Investigate |
| 5x normal | Alert team lead |
| 10x+ normal | Emergency: consider service pause |

---

## Prevention Checklist

- [x] Budget alerts configured (50%, 80%, 100%)
- [x] Per-user rate limiting (60 req/min)
- [x] Per-IP rate limiting (100 req/min)
- [ ] Per-user daily cost cap (future)
- [ ] Anomaly detection ML model (future)
