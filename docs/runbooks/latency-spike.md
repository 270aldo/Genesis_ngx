# Runbook: Latency Spike

**Severity**: Warning
**SLO Impact**: P95 latency > target
**On-Call**: Platform Team

---

## Symptoms

- Alert: "Genesis NGX - High Latency P95"
- Users report slow responses
- P95 latency exceeds SLO targets:
  - Pro models (GENESIS_X, LOGOS): > 6 seconds
  - Flash models: > 2 seconds

---

## SLO Targets

| Model Tier | Agents | P95 Target | P99 Target |
|------------|--------|------------|------------|
| Pro | GENESIS_X, LOGOS | ≤ 6s | ≤ 10s |
| Flash | All others | ≤ 2s | ≤ 4s |

---

## Diagnosis Steps

### 1. Identify Slow Agent(s)

```bash
# Check latency by agent in last hour
gcloud logging read \
  'jsonPayload.latency_ms>0' \
  --project=ngx-genesis-prod \
  --limit=500 \
  --format="json" | jq -r '[.jsonPayload.agent_type, .jsonPayload.latency_ms] | @tsv' | \
  awk '{sum[$1]+=$2; count[$1]++} END {for (a in sum) print a, sum[a]/count[a]}' | sort -k2 -rn
```

### 2. Check Vertex AI Status

- Visit: https://status.cloud.google.com/
- Check for Vertex AI degradation in us-central1

### 3. Check Token Usage (Correlation)

High token usage = longer processing time

```bash
# Average tokens per request by agent
gcloud logging read \
  'jsonPayload.tokens_used>0' \
  --project=ngx-genesis-prod \
  --limit=500 \
  --format="json" | jq -r '[.jsonPayload.agent_type, .jsonPayload.tokens_used] | @tsv' | \
  awk '{sum[$1]+=$2; count[$1]++} END {for (a in sum) print a, sum[a]/count[a]}' | sort -k2 -rn
```

### 4. Check Cold Start Issues

```bash
# Look for cold start indicators
gcloud logging read \
  'textPayload:"cold start" OR jsonPayload.cold_start=true' \
  --project=ngx-genesis-prod \
  --limit=50
```

---

## Resolution Steps

### If Vertex AI Degradation

1. Monitor GCP Status page
2. Wait for resolution (usually <1 hour)
3. Consider caching frequent responses

### If Cold Starts

Increase minimum instances:

```bash
# Update Cloud Run min instances
gcloud run services update genesis-gateway \
  --min-instances=1 \
  --project=ngx-genesis-prod \
  --region=us-central1
```

### If High Token Usage

1. Review recent prompt changes
2. Check for verbose agent responses
3. Consider prompt optimization

```bash
# Find requests with >5000 tokens
gcloud logging read \
  'jsonPayload.tokens_used>5000' \
  --project=ngx-genesis-prod \
  --limit=20 \
  --format="table(timestamp,jsonPayload.agent_type,jsonPayload.tokens_used)"
```

### If Specific Agent Slow

1. Check agent's tool execution time
2. Review Supabase RPC latency
3. Consider agent prompt optimization

---

## Performance Optimization Checklist

### Quick Wins

- [ ] Enable response caching for common queries
- [ ] Reduce system prompt length
- [ ] Optimize tool implementations

### Medium-term

- [ ] Implement streaming for all responses
- [ ] Add context window management
- [ ] Pre-warm agents with synthetic traffic

### Long-term

- [ ] Deploy to multiple regions
- [ ] Implement smart routing based on load
- [ ] Consider Flash model for more agents

---

## Escalation

| P95 Latency | Action |
|-------------|--------|
| 6-10s (Pro) | Monitor, investigate |
| 10-15s | Alert team lead |
| >15s | Consider degraded mode |

---

## Degraded Mode Options

If latency is unacceptable and can't be resolved:

1. **Fallback responses**: Return cached/static responses for common queries
2. **Disable specialists**: Route all to GENESIS_X only
3. **Queue requests**: Async processing with notification

```python
# Example: Fallback mode in Gateway
if latency_p95 > 15000:  # 15 seconds
    return {"response": "High demand. Your request is queued.", "queued": True}
```
