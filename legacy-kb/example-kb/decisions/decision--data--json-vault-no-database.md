---
type: decision
scope: [data, deployment]
status: active
date: 2025-10-14
source_of_truth: false
tags: [storage, backend]
---

# JSON vault storage instead of a database

## Context

The system needs persistent storage for domain entities. The project is designed for a single operator (admin).

## Decision

Use JSON files in a `vault/` directory as the source of truth. No database.

## Why

- Simplicity — files are human-readable, git-diffable, and easy to debug
- No database setup — reduces infrastructure requirements
- Version-controlled — JSON catalogs are tracked in git (binary assets excluded)
- Single-user design — concurrent access is minimal
- Portable — the entire data layer is a directory

## Vault structure

```
vault/
├── arts/fullsize/          # Original uploaded images
├── arts/previews/          # Generated previews (JPEG + WebP + AVIF)
├── hopper/                 # Upload staging area
├── json/
│   ├── art_catalog.json
│   ├── techniques.json
│   ├── users.json
│   ├── block_collection/block_collection.json
│   ├── streams/index.json + {stream_id}.json
│   ├── events/catalog.json
│   ├── public/home.json
│   └── public_stream.json
└── streams/                # Stream-level media assets
```

## Concurrency mechanisms (per-repo)

All repos use `asyncio.Lock` (in-process only).

| Mechanism | Repos that implement it |
|-----------|------------------------|
| Optimistic concurrency (version + 409) | StreamRepo, PublicStreamRepo, HomeDocRepo |
| Version field exists but NOT enforced | EventRepo, EventPageRepo, TextVisualRepo, MediaItemRepo, CatalogRepo, BlockCollectionRepo |
| Atomic writes (tmp+rename) | All repos EXCEPT CatalogRepo and BlockCollectionRepo |

## Git policy

- JSON files and folder structure tracked in git
- Binary image assets excluded via `.gitignore`

## Limitations

- Not safe for multi-process or multi-instance deployments
- No query engine (filtering done in-memory)

## Alternatives considered

- PostgreSQL / SQLite — adds infrastructure complexity for a single-user system
- Cloud storage — appropriate for media but not structured data at this scale
