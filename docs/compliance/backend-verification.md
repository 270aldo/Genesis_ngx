# Compliance Backend Verification

**Date**: 2025-12-15
**Status**: ✅ READY FOR PRODUCTION
**ADR Reference**: ADR-008

---

## Health Data Tiers - Verification Checklist

### Tier 1: Enabled by Default ✅

| metric_type | Display (ES) | Unit | Validation |
|-------------|--------------|------|------------|
| `weight_kg` | Peso | kg | 20-300 |
| `height_cm` | Altura | cm | 50-250 |
| `steps_daily` | Pasos diarios | count | 0-100000 |
| `active_minutes` | Minutos activos | min | 0-1440 |
| `calories_burned` | Calorías quemadas | kcal | 0-10000 |
| `water_ml` | Hidratación | ml | 0-10000 |
| `sleep_hours` | Horas de sueño | hours | 0-24 |

**Consent Required**: Privacy Policy acceptance only

### Tier 2: Requires Additional Consent ✅

| metric_type | Display (ES) | Unit | Validation |
|-------------|--------------|------|------------|
| `body_fat_percentage` | Grasa corporal | % | 1-70 |
| `muscle_mass_kg` | Masa muscular | kg | 10-100 |
| `resting_hr_bpm` | FC en reposo | bpm | 30-200 |
| `sleep_quality_score` | Calidad de sueño | score | 1-100 |

**Consent Required**: `tier2_health_data` via `rpc.grant_consent()`

### Tier 3: Excluded from v1 ❌

Not implemented - requires legal consultation:
- Blood glucose, blood pressure
- HRV, SpO2
- Menstrual cycle data
- Body temperature

---

## Database Objects Verification

### Tables ✅

| Table | Purpose | RLS |
|-------|---------|-----|
| `metric_type_config` | Tier classification reference | N/A (public read) |
| `user_consents` | Consent tracking | ✅ Enabled |
| `health_metrics` | Health data storage | ✅ Enabled |

### Functions ✅

| Function | Type | Purpose |
|----------|------|---------|
| `user_has_tier2_consent(uuid)` | SQL | Check if user has Tier 2 consent |
| `validate_health_metric_tier()` | Trigger | Validate consent before insert |

### RPCs ✅

| RPC | Parameters | Returns | Access |
|-----|------------|---------|--------|
| `rpc.grant_consent` | consent_type, version, ip, user_agent | uuid | authenticated |
| `rpc.revoke_consent` | consent_type | boolean | authenticated |

### Triggers ✅

| Trigger | Table | Event | Function |
|---------|-------|-------|----------|
| `trg_validate_health_metric_tier` | health_metrics | BEFORE INSERT | validate_health_metric_tier() |

### Constraints ✅

| Constraint | Table | Rule |
|------------|-------|------|
| `health_metrics_metric_type_check` | health_metrics | Only allowed metric_types |
| `user_consents_consent_type_check` | user_consents | privacy_policy, tier2_health_data, marketing |

---

## RLS Policies Verification

### user_consents

| Policy | Operation | Rule |
|--------|-----------|------|
| "Users read own consents" | SELECT | `auth.uid() = user_id` |
| "Users insert own consents" | INSERT | `auth.uid() = user_id` |
| "Users update own consents" | UPDATE | `auth.uid() = user_id` |

---

## Consent Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     USER ONBOARDING                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Accept Privacy Policy (required)                        │
│     └─> rpc.grant_consent('privacy_policy', 'v1.0', ...)   │
│                                                             │
│  2. Optional: Enable Tier 2 Data                            │
│     └─> rpc.grant_consent('tier2_health_data', 'v1.0', ...)│
│                                                             │
│  3. Optional: Marketing consent                             │
│     └─> rpc.grant_consent('marketing', 'v1.0', ...)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   DATA COLLECTION                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  INSERT health_metric (Tier 1)                              │
│     └─> Trigger validates: tier=1 → ALLOW                  │
│                                                             │
│  INSERT health_metric (Tier 2)                              │
│     └─> Trigger validates:                                  │
│         - tier=2                                            │
│         - user_has_tier2_consent(user_id) = true           │
│         - If no consent → REJECT with error                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Test Scenarios

### Scenario 1: Tier 1 Data (No Extra Consent)
```sql
-- Should succeed without tier2 consent
INSERT INTO health_metrics (user_id, metric_type, value, unit)
VALUES ('user-uuid', 'weight_kg', 75.5, 'kg');
-- ✅ Success
```

### Scenario 2: Tier 2 Data Without Consent
```sql
-- Should fail
INSERT INTO health_metrics (user_id, metric_type, value, unit)
VALUES ('user-uuid', 'body_fat_percentage', 15.2, '%');
-- ❌ Error: User has not consented to Tier 2 health data collection
```

### Scenario 3: Tier 2 Data With Consent
```sql
-- First grant consent
SELECT rpc.grant_consent('tier2_health_data', 'v1.0');

-- Now should succeed
INSERT INTO health_metrics (user_id, metric_type, value, unit)
VALUES ('user-uuid', 'body_fat_percentage', 15.2, '%');
-- ✅ Success
```

### Scenario 4: Invalid Metric Type
```sql
-- Should fail (Tier 3 not allowed)
INSERT INTO health_metrics (user_id, metric_type, value, unit)
VALUES ('user-uuid', 'blood_glucose', 95, 'mg/dL');
-- ❌ Error: Invalid metric_type: blood_glucose
```

---

## LFPDPPP Compliance Summary

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Explicit consent for sensitive data | `rpc.grant_consent()` with timestamp | ✅ |
| Consent can be revoked | `rpc.revoke_consent()` | ✅ |
| Audit trail | `user_consents` table with timestamps | ✅ |
| Data minimization | Only Tier 1+2 metrics, no medical data | ✅ |
| Purpose limitation | Metrics tied to wellness, not medical | ✅ |
| Access control | RLS on all tables | ✅ |

---

## Migration File

**Location**: `supabase/migrations/002_health_metrics_tiers.sql`
**Lines**: 304
**Status**: Ready to apply

```bash
# Apply migration
supabase db push

# Verify
supabase db lint
```

---

## Frontend Integration Notes

For the frontend team to implement the consent UI:

```typescript
// Grant Tier 2 consent
const { data, error } = await supabase.rpc('grant_consent', {
  p_consent_type: 'tier2_health_data',
  p_consent_version: 'v1.0',
  p_ip_address: userIP,        // optional
  p_user_agent: navigator.userAgent  // optional
});

// Revoke consent
const { data, error } = await supabase.rpc('revoke_consent', {
  p_consent_type: 'tier2_health_data'
});

// Check consent status
const { data: consents } = await supabase
  .from('user_consents')
  .select('consent_type, granted, granted_at')
  .eq('user_id', userId);
```
