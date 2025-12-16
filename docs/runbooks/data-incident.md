# Runbook: Data Incident

**Severity**: Critical
**Compliance Impact**: LFPDPPP violation risk
**On-Call**: Platform Team + Legal

---

## Incident Types

| Type | Description | Severity |
|------|-------------|----------|
| Data Breach | Unauthorized access to user data | Critical |
| Data Loss | Accidental deletion of user data | Critical |
| PII Exposure | PII logged or exposed in error | High |
| Consent Violation | Data processed without consent | High |

---

## Immediate Actions (First 15 Minutes)

### 1. Assess Scope

```bash
# Check for unauthorized access attempts
gcloud logging read \
  'protoPayload.authenticationInfo.principalEmail!~"@ngx-genesis"
   protoPayload.methodName:"aiplatform"' \
  --project=ngx-genesis-prod \
  --limit=100

# Check for data access anomalies
gcloud logging read \
  'protoPayload.methodName:"supabase" OR protoPayload.methodName:"postgres"' \
  --project=ngx-genesis-prod \
  --limit=100
```

### 2. Contain the Incident

If breach confirmed:

```bash
# Rotate service account keys immediately
gcloud iam service-accounts keys list \
  --iam-account=genesis-gateway@ngx-genesis-prod.iam.gserviceaccount.com

# Revoke suspicious keys
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=genesis-gateway@ngx-genesis-prod.iam.gserviceaccount.com
```

### 3. Document Everything

Create incident ticket with:
- Timestamp of detection
- How it was detected
- Initial scope assessment
- Actions taken

---

## Data Classification (Genesis NGX)

### Tier 1: General Data (Lower Risk)
- Weight, height, steps
- Active minutes, calories
- Water intake, sleep hours

### Tier 2: Sensitive Data (Higher Risk)
- Body fat percentage
- Muscle mass
- Resting heart rate
- Sleep quality score

### Tier 3: Excluded from v1
- Blood glucose, blood pressure
- Menstrual cycle data
- Medical conditions

---

## Incident Response by Type

### Data Breach

1. **Contain**: Revoke access, rotate credentials
2. **Assess**: Identify affected users and data types
3. **Notify**: Legal team within 1 hour
4. **Report**: LFPDPPP requires notification within 72 hours

```bash
# Identify affected users (example query)
SELECT DISTINCT user_id
FROM health_metrics
WHERE created_at BETWEEN 'BREACH_START' AND 'BREACH_END';
```

### PII Exposure in Logs

1. **Delete**: Remove PII from Cloud Logging

```bash
# Delete specific log entries (requires admin)
gcloud logging delete \
  'jsonPayload.email!="" OR jsonPayload.phone!=""' \
  --project=ngx-genesis-prod
```

2. **Fix**: Update logging configuration to sanitize PII
3. **Audit**: Review all log sinks for PII patterns

### Consent Violation

1. **Stop**: Halt processing of affected data type
2. **Verify**: Check user_consents table for consent status
3. **Remediate**: Delete data collected without consent

```sql
-- Find Tier 2 data without consent
SELECT hm.*
FROM health_metrics hm
LEFT JOIN user_consents uc ON hm.user_id = uc.user_id
  AND uc.consent_type = 'tier2_health_data'
WHERE hm.metric_type IN ('body_fat_percentage', 'muscle_mass_kg', 'resting_hr_bpm', 'sleep_quality_score')
  AND (uc.granted IS NULL OR uc.granted = false);
```

---

## LFPDPPP Compliance Requirements

### Notification Timeline

| Event | Deadline |
|-------|----------|
| Internal escalation | Immediately |
| Legal team notification | 1 hour |
| Authority notification | 72 hours |
| User notification | 72 hours (if high risk) |

### Required Documentation

- [ ] Nature of the breach
- [ ] Categories of data affected
- [ ] Approximate number of users affected
- [ ] Contact details of DPO
- [ ] Likely consequences
- [ ] Measures taken to address breach

---

## Escalation Matrix

| Time | Action | Contact |
|------|--------|---------|
| 0 min | Detect & contain | On-call engineer |
| 15 min | Assess scope | Platform lead |
| 1 hour | Legal notification | Legal team |
| 4 hours | Executive briefing | CTO/CEO |
| 72 hours | Regulatory filing | Legal + Compliance |

---

## Post-Incident

### Within 24 Hours

- [ ] Complete incident timeline
- [ ] Identify root cause
- [ ] Implement immediate fixes

### Within 1 Week

- [ ] Conduct post-mortem
- [ ] Document lessons learned
- [ ] Update security controls
- [ ] Update this runbook if needed

### Within 1 Month

- [ ] Complete security audit
- [ ] Implement long-term fixes
- [ ] Training for affected teams

---

## Prevention Checklist

- [x] RLS policies on all tables
- [x] SECURITY DEFINER RPCs for writes
- [x] PII sanitization in logs
- [x] Tiered consent system
- [ ] Regular security audits (quarterly)
- [ ] Penetration testing (annual)
- [ ] Data retention policy enforcement
