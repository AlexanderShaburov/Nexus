---
type: architecture
scope: [system]
status: active
date: 2026-04-10
source_of_truth: true
tags: [constitution, overview]
---

# Overall system structure

## System composition

atSashas.Gallery is a modular art gallery system with three layers:

- **Vault** (`vault/`) — runtime data layer. JSON catalogs + media assets. Source of truth for all domain data. No database.
- **Knowledge** (`knowledge/`) — agent reasoning layer. Invariants, decisions, architecture descriptions, patterns.
- **Application** — frontend (React 19 + Vite) + backend (FastAPI). Public gallery + admin dashboard.

## High-level deployment

```
Caddy (reverse proxy, :8080)
  /media/* → static files from vault/
  /api/*   → FastAPI backend (:8000)
  /*       → React SPA (:3000)
```

All three services run via Docker Compose.

## Technology stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript 5.9, Vite 7, React Router 7 |
| Backend | Python 3.12, FastAPI, Pydantic, Uvicorn |
| Reverse proxy | Caddy 2 |
| Containerization | Docker Compose |
| State | Custom pub/sub stores (no Redux/Zustand) |
| Styling | Plain CSS (co-located with components) |
| Auth | JWT + bcrypt + HTTP-only cookies |
| Drag & Drop | @dnd-kit |

## Monorepo layout

```
SashaGallery/
├── apps/
│   ├── frontend/         # React 19 + Vite + TypeScript
│   └── admin-backend/    # FastAPI + Poetry
├── docker/               # Docker Compose + Caddy config
├── vault/                # JSON data + media assets (source of truth)
├── rules/                # Architecture Constitution + ADRs
├── knowledge/            # Agent knowledge layer
└── Docs/                 # Project documentation
```

## Canonical content pipeline

```
Hopper → ArtItem → Block → Stream → HomeDoc → Publish
```

No shortcuts bypassing this pipeline.

## Related

- [Frontend layering](architecture--system--frontend-layering.md)
- [Domain model](architecture--data--domain-model.md)
- [State management](architecture--state--custom-pubsub-stores.md)
