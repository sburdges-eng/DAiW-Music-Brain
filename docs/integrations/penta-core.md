# Penta-Core Integration

## Overview

This document describes the planned integration between DAiW-Music-Brain and [penta-core](https://github.com/sburdges-eng/penta-core).

The integration follows DAiW-Music-Brain's core philosophy of **"Interrogate Before Generate"** - ensuring that emotional intent drives technical decisions throughout the integration.

### Philosophy Alignment

- **Emotional intent first**: Any data exchange with penta-core should preserve and respect the emotional context established in Phase 0 (Core Wound/Desire)
- **Rule-breaking with justification**: When technical constraints from penta-core conflict with emotional intent, the integration should support intentional rule-breaking with proper justification
- **Teaching over automation**: The integration should expose learning opportunities, not just automate away complexity

---

## API Interface Points

> **Status**: Placeholder - To be implemented

### Outbound (DAiW-Music-Brain → Penta-Core)

The following data types may be sent to penta-core:

| Interface | Description | Data Type |
|-----------|-------------|-----------|
| `send_intent` | Share song intent/emotional context | `CompleteSongIntent` |
| `send_groove` | Share extracted groove templates | `GrooveTemplate` |
| `send_analysis` | Share chord progression analysis | `ProgressionDiagnosis` |

### Inbound (Penta-Core → DAiW-Music-Brain)

The following data types may be received from penta-core:

| Interface | Description | Data Type |
|-----------|-------------|-----------|
| `receive_feedback` | Receive processing feedback | `dict` |
| `receive_suggestions` | Receive creative suggestions | `list[str]` |

---

## Data Flow

> **Status**: Placeholder - Architecture to be finalized

### Typical Integration Flow

```
┌─────────────────────┐     ┌─────────────────────┐
│   DAiW-Music-Brain  │     │     Penta-Core      │
│                     │     │                     │
│  ┌───────────────┐  │     │                     │
│  │ Phase 0:      │  │     │                     │
│  │ Core Intent   │──┼────►│  Process Intent     │
│  └───────────────┘  │     │                     │
│                     │     │                     │
│  ┌───────────────┐  │     │                     │
│  │ Phase 1:      │  │◄────┼  Return Suggestions │
│  │ Emotional     │  │     │                     │
│  └───────────────┘  │     │                     │
│                     │     │                     │
│  ┌───────────────┐  │     │                     │
│  │ Phase 2:      │  │────►│  Final Processing   │
│  │ Technical     │  │     │                     │
│  └───────────────┘  │     │                     │
└─────────────────────┘     └─────────────────────┘
```

### Data Format

Data exchange will use JSON serialization compatible with DAiW-Music-Brain's existing `to_dict()` / `from_dict()` patterns:

```python
from music_brain.integrations.penta_core import PentaCoreIntegration

integration = PentaCoreIntegration()

# Send intent to penta-core
result = integration.send_intent(complete_song_intent)

# Receive and process feedback
suggestions = integration.receive_suggestions()
```

---

## Configuration

> **Status**: Placeholder - Configuration options to be defined

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PENTA_CORE_URL` | Penta-core service endpoint | `None` |
| `PENTA_CORE_API_KEY` | API authentication key | `None` |
| `PENTA_CORE_TIMEOUT` | Request timeout in seconds | `30` |

### Optional Dependencies

Install penta-core integration dependencies:

```bash
pip install idaw[penta-core]
```

---

## Future Work

- [ ] Define concrete API contracts with penta-core team
- [ ] Implement authentication and secure communication
- [ ] Add retry logic and error handling
- [ ] Create integration tests with mock penta-core responses
- [ ] Document versioning and compatibility requirements

---

## Related Documentation

- [DAiW Integration Guide](../INTEGRATION_GUIDE.md)
- [Intent Schema Documentation](../../vault/Songwriting_Guides/) (if available)
- [Penta-Core Repository](https://github.com/sburdges-eng/penta-core)
