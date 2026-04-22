---
type: architecture
scope: [hopper, system]
status: active
date: 2026-04-10
source_of_truth: true
tags: [ingestion, media-processing]
---

# Hopper ingestion pipeline structure

## Components

| Component | Location | Role |
|-----------|----------|------|
| Upload endpoint | `POST /upload` | Receives files, SHA256 dedup, stores in hopper |
| Hopper endpoint | `GET /hopper/content`, `DELETE /hopper/{id}` | Lists and removes staged files |
| ImagesJSON.from_hopper | `models/images_pipline.py` | Processes hopper images into art previews |
| Catalog update service | `services/catalog_service.py` | Orchestrates ArtItem creation with image processing |
| UploadPage | `pages/admin/UploadPage.tsx` | Frontend for `/admin/upload` and `/admin/hopper` |

## Shipment discriminated union

```python
ImageShipment = HopperImageShipment | ReadyImageShipment

HopperImageShipment: { kind: 'hopper', hopperSrc: str }
ReadyImageShipment:  { kind: 'ready', image: ImagesJSON }
```

## Filesystem layout

```
vault/
├── hopper/           # temporary staging (SHA256-named files)
├── arts/fullsize/    # permanent originals ({art_id}.{ext})
└── arts/previews/    # generated previews ({art_id}.jpeg, .webp, .avif)
```

## Upload constraints

- Allowed MIME: png, jpeg, webp, avif, pdf, svg
- Max size: 50 MB
- Dedup: SHA256 hash as filename

## Preview generation parameters

- Max preview dimension: 500px longest edge
- Target file size: ≤500KB soft cap
- Formats: JPEG, WebP, AVIF (AVIF optional, silent fail)
- Quality: adaptive from 90 down to 50

## Related

- [Hopper ingestion behavior](../specs/spec--system--hopper-ingestion-behavior.md)
