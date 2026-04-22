---
type: open_question
scope: [data, api]
status: active
date: 2026-04-10
source_of_truth: false
tags: [backend, concurrency]
---

# Optimistic concurrency is inconsistently enforced across repos

## Observation

Only 3 of 9 backend repos enforce optimistic concurrency (version check + HTTP 409 rejection):
- StreamRepo
- PublicStreamRepo
- HomeDocRepo

The remaining 6 repos have `version` fields in their Pydantic models but do NOT validate the incoming version before saving:
- EventRepo
- EventPageRepo
- TextVisualRepo
- MediaItemRepo
- CatalogRepo (has `catalogVersion`)
- BlockCollectionRepo (has `version`)

## Risk

Without version checking, concurrent edits (e.g., two browser tabs) could silently overwrite each other. The `asyncio.Lock` prevents corrupted writes but not lost updates.

## Question

Should all repos enforce optimistic concurrency, or is the current inconsistency intentional (e.g., newer repos haven't been hardened yet)?

## Evidence

- StreamRepo version check: `stream_repo.py` lines 224-251
- PublicStreamRepo version check: `public_stream_repo.py` lines 55-78
- HomeDocRepo version check: `home_doc_repo.py` lines 79-95
- EventRepo _save() with NO version check: `event_repo.py` lines 46-53
