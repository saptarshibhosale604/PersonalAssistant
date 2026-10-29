# TACTICAL OPERATION PLAN: Reminder Configuration Matrix

## Objective
Establish standard operating procedures and reminder configurations for `create_calendar_event` deployments, utilizing various combinations of `email` and `popup` notification channels across tactical time windows.

---

## Reminder Configuration Profiles

### Profile Alpha: Standard Briefing (Immediate Interruption)
- **Use Case:** Routine meetings and internal syncs.
- **Reminders Payload:**
```json
[
  {"method": "popup", "minutes": 10}
]
```

### Profile Bravo: High-Priority Strategic Summit (Dual Redundancy)
- **Use Case:** Critical operations requiring advance preparation and immediate attendance.
- **Reminders Payload:**
```json
[
  {"method": "email", "minutes": 1440},
  {"method": "popup", "minutes": 15}
]
```

### Profile Charlie: Long-Range Executive Briefing (Tiered Escalation)
- **Use Case:** Major cross-departmental operations or audits requiring days of prep followed by countdown alerts.
- **Reminders Payload:**
```json
[
  {"method": "email", "minutes": 10080},
  {"method": "email", "minutes": 2880},
  {"method": "popup", "minutes": 60},
  {"method": "popup", "minutes": 5}
]
```

### Profile Delta: Rapid Deployment / Zero-Lag Huddle
- **Use Case:** Back-to-back tactical syncs or emergency situation room updates.
- **Reminders Payload:**
```json
[
  {"method": "popup", "minutes": 2},
  {"method": "popup", "minutes": 0}
]
```

---

## Execution Directives
1. When calling `create_calendar_event`, pass the desired profile's JSON list into the `reminders` argument.
2. Ensure timezone (`Asia/Kolkata`) and `calendar_id` (`saptarshibhosale604@gmail.com`) are properly maintained for all scheduled operations.
