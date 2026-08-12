# 🚀 Hermes AI Ventures - Trading War Room

Real-time pipeline visualization and monitoring dashboard for the Hermes AI Ventures trading pipeline.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COGNEE MEMORY LAYER                       │
│  Vision Dataset • Agent Memory • Trade History • Regime     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     REDIS COMMS BUS                          │
│                                                              │
│  Elon-Scout → Trump-Analyst → Osin-Strategist → Ken-Executor │
│                                                              │
│  queue:scout    queue:analyst   queue:strategist  queue:executor │
└─────────────────────────────────────────────────────────────┘
```

## Components

- `war-room.html` - Live dashboard frontend (SVG pipeline visualization + real-time status cards)
- `war-room-server.py` - Flask API backend that bridges Redis/Cognee to the dashboard

## Features

- **Live Pipeline Status** - Real-time agent states (idle/active/analyzing/executing)
- **Queue Monitoring** - Live queue depths for all pipeline stages
- **Cognee Health** - Memory layer status and dataset connectivity
- **Redis Bus** - Key counts, connection status, queue types
- **Trading Session** - Balance, positions, VIX, regime, P&L
- **Live Signals Feed** - Latest analyst signals with confidence scores
- **Auto-Refresh** - Updates every 5 seconds

## Quick Start

```bash
# Install dependencies
pip install flask redis

# Start the server
python war-room-server.py

# Open dashboard
# http://localhost:5000
```

## API Endpoints

- `GET /` - Dashboard frontend
- `GET /api/status` - Full pipeline status (Redis queues, Cognee health, agent states)
- `GET /api/agents` - Agent details and capabilities
- `GET /api/trading` - Trading session data

## Pipeline

1. **Elon-Scout** - Market scanning, gap detection, regime assessment
2. **Trump-Analyst** - Signal analysis, risk scoring, trade setup validation
3. **Osin-Strategist** - Entry/exit logic, position sizing, order construction
4. **Ken-Executor** - Order routing, brokerage execution, fill confirmation

## Memory Layer

- **Cognee** - Persistent knowledge base (goals, lessons, patterns)
- **Redis** - Real-time communication bus (live signals, queues, status)

---
*Built by Ken-Executor • Hermes AI Ventures*
