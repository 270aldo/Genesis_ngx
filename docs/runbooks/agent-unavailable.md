# Runbook: Agent Unavailable

**Severity**: Critical
**SLO Impact**: Availability < 99.5%
**On-Call**: Platform Team

---

## Symptoms

- Alert: "Genesis NGX - Agent Unavailable"
- Users report "Agent not responding" errors
- Gateway returns 503 or timeout errors
- No successful invocations in Cloud Monitoring

---

## Diagnosis Steps

### 1. Check Agent Engine Status

```bash
# List all deployed agents
gcloud ai reasoning-engines list \
  --project=ngx-genesis-prod \
  --region=us-central1

# Check specific agent status
gcloud ai reasoning-engines describe genesis-ngx-genesis-x \
  --project=ngx-genesis-prod \
  --region=us-central1
```

### 2. Check Cloud Logging for Errors

```bash
# Recent errors from Agent Engine
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine" severity>=ERROR' \
  --project=ngx-genesis-prod \
  --limit=50 \
  --format="table(timestamp,jsonPayload.message)"
```

### 3. Verify Service Account Permissions

```bash
# Check gateway SA has aiplatform.user role
gcloud projects get-iam-policy ngx-genesis-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:genesis-gateway" \
  --format="table(bindings.role)"
```

### 4. Check Vertex AI Status

- Visit: https://status.cloud.google.com/
- Filter for "Vertex AI" in us-central1

---

## Resolution Steps

### If Agent is Not Deployed

```bash
# Redeploy the agent
cd agents/genesis_x
adk deploy --project=ngx-genesis-prod --region=us-central1
```

### If Permission Error

```bash
# Re-grant aiplatform.user role
gcloud projects add-iam-policy-binding ngx-genesis-prod \
  --member="serviceAccount:genesis-gateway@ngx-genesis-prod.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### If Vertex AI Outage

1. Monitor GCP Status page
2. Consider failover to secondary region (if configured)
3. Communicate status to users via app notification

---

## Escalation

| Time | Action |
|------|--------|
| 0-15 min | On-call investigates |
| 15-30 min | Escalate to Platform Lead |
| 30+ min | Engage GCP Support (if GCP issue) |

---

## Prevention

- [ ] Set up multi-region deployment (future)
- [ ] Implement circuit breaker in Gateway
- [ ] Add health check endpoint that probes Agent Engine
