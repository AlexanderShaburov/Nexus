---
type: open_question
scope: [architecture]
status: active
date: 2026-04-10
source_of_truth: false
tags: [fsd, layer-violation]
---

# entities/common imports from shared/ui (layer violation)

## Observation

`entities/common/editorSession.ts` imports `GridItem` from `@/shared/ui/grid`. This violates the downward-only dependency rule: entities should not depend on shared/ui types.

## Impact

Currently functional — no circular dependency. But it couples the domain layer to a UI-specific type.

## Possible fix

Extract `GridItem` type definition to `entities/common/` or `entities/hopper/`, since it represents a pipeline data shape, not a UI concern.

## Evidence

File: `apps/frontend/src/entities/common/editorSession.ts`
Import: `import { GridItem } from '@/shared/ui/grid';`
