---
type: spec
scope: [hopper, system]
status: active
date: 2026-04-10
source_of_truth: false
tags: [ingestion, behavior]
---

# Hopper ingestion behavior

## Upload flow

1. User uploads file via UploadPage (drag-and-drop or file picker)
2. `POST /upload` (multipart) → validate MIME + size → SHA256 hash → store as `vault/hopper/{sha256}{ext}`
3. If file with same hash exists → skip (dedup)
4. File appears in hopper grid

## ArtItem ingestion (Catalog Editor path)

1. User selects file in hopper (during Journey from Catalog Editor)
2. Hopper returns loot: `{ ok: true, id, output: { thumbUrl } }`
3. Catalog Editor builds `ArtShipmentModel` with `{ kind: 'hopper', hopperSrc: filename }`
4. `POST /art/catalog/update` → `ImagesJSON.from_hopper()`:
   - Moves original from hopper to `vault/arts/fullsize/{art_id}.{ext}`
   - Converts to RGB
   - Generates JPEG, WebP, AVIF previews (quality adaptive)
5. ArtItem created in catalog with processed image paths

## MediaItem ingestion (Media Editor path)

1. User selects file in hopper (during Journey from Media Editor)
2. Hopper returns loot
3. Media Editor converts `GridItem → MediaItemData` via `newMediaItemFromHopperLoot()`
4. Enters CREATE mode, user edits metadata
5. On save: `POST /admin/media-items` (no server-side image processing)

## Lifecycle determination

Frontend decides shipment kind based on `ArtItemData.lifecycle`:
- `lifecycle === 'draft'` → `kind: 'hopper'` (triggers backend processing)
- Otherwise → `kind: 'ready'` (pre-processed, skip processing)

## Related

- [Hopper pipeline structure](../architecture/architecture--system--hopper-ingestion-pipeline.md)
