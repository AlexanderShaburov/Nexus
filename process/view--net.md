---
type: view
status: draft
state: active
owner: agent
created: 2026-10-08
updated: 2026-10-08
refs: [process/navigation.md]
---

# Nexus net, as a picture

A rendering of `## Net` in `navigation.md` with names instead of ids. The navigation stays the source; this file is redrawn from it by hand and may lag. Experiment of 2026-10-08: whether a diagram makes the net readable cold where the list did not. `type: view` is not yet a kind in the process-space spec; the spec is amended if this file earns its place, and the file is deleted if it does not.

Reading the picture: rounded boxes are project states (places), rectangles are work (transitions). A transition fires only when every state feeding it is reached. Green is reached, orange is being worked, grey is ahead. "critical" means every path to the goal passes through it; "feasibility unknown" means we do not yet know whether it can be done at all.

```mermaid
flowchart TD
    P1(["Knowledge layer shipped<br/>1.3.0 runs in several host projects"])
    P2(["Process-space rules drafted<br/>spec exists as a draft"])
    P3(["Charter and navigation agreed<br/>operator confirmed both files"])
    P4(["Files carry the position<br/>a fresh agent states position and reason from the two files alone"])
    P5(["Net is checkable<br/>mechanical enabling check works and the file reads cold"])
    P6(["Runtime reads process/<br/>bootstrap and PreCompact load it; position survives both"])
    P7(["Position is gated<br/>the position claim is enforced at the first mutating call"])
    P8(["One host runs layer two"])
    P9(["Layer two released<br/>next Nexus version"])

    T1["Cold-read check at session start<br/>critical; runs every session, operator judges"]
    T2["Net paper test<br/>critical, feasibility unknown; NOW<br/>paper half passed, cold reading failed"]
    T3["Teach bootstrap to read process/<br/>Mandatory Startup Reading Set grows"]
    T4["Build the position gate<br/>claim gains --step, tool gate checks the net"]
    T5["Install in one host"]
    T6["Release<br/>tag and ship"]

    S["Steering check, outside the net<br/>operator runs an ordinary session and judges whether the agent holds direction by habit<br/>decides what P5, T4 and P7 are for"]

    P3 --> T1 --> P4
    P3 --> T2 --> P5
    P4 --> T3
    P5 --> T3 --> P6
    P5 --> T4
    P6 --> T4 --> P7
    P7 --> T5 --> P8
    P8 --> T6 --> P9
    P1 -.-> T5
    P2 -.-> T4

    S -. waits on .-> T4
    S -. waits on .-> P5

    classDef done fill:#d8f0d8,stroke:#2e7d32,color:#000
    classDef now fill:#ffe8b3,stroke:#b26a00,stroke-width:2px,color:#000
    classDef ahead fill:#f2f2f2,stroke:#888,color:#333
    classDef outside fill:#fff,stroke:#b26a00,stroke-dasharray:5 3,color:#000

    class P1,P2,P3 done
    class T1,T2 now
    class P4,P5,P6,P7,P8,P9,T3,T4,T5,T6 ahead
    class S outside
```

Dotted edges from the first two states are not in the navigation's net: they show which reached states the far transitions rest on (the release goes to the hosts that run the first layer; the gate is built against the drafted rules). If they mislead, they go.
