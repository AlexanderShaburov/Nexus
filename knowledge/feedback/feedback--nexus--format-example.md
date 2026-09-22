---
type: feedback
scope: nexus
status: deprecated
created: 2026-09-22
updated: 2026-09-22
source_of_truth: false
knowledge_visibility: historical
kind: wish
nexus_version: 1.0.0
host: nexus-template
touches: [knowledge/specs/spec--system--feedback-channel.md]
delivered: []
tags: [feedback, nexus, example]
---

# Format example: a feedback note

This document is the template's own fixture for `spec--system--feedback-channel.md`: it shows the shape a host writes, and `tools/validate-vault.py` validates it like any note. It is `deprecated` and `historical` on purpose, it is never delivered anywhere, and the Nexus updater never owns `knowledge/feedback/`.

## What happened

While writing this specification in the template, there was no example of a note to point a host at.

## What is proposed

Keep this file as the example. A host copies its shape, not its content: `kind`, `nexus_version`, `host` and `touches` describe the host's situation; the three sections below stay.

## Attachment

none
