# Part 6 — Jobs and Employment

Part 6 adds bounded, persistent employment on top of the Part 5 economy. Jobs have authored workplaces, shift windows, durations and wages. Runtime state tracks employment, attendance, shift history, earnings, work reputation and fatigue. Wages enter the same transaction ledger as purchases and produce sales.

The first vertical slice includes bakery morning work, village-shop assistance and local cottage repair odd jobs. Jobs are discovered in person, worked only at valid places and times, limited to one shift per job per day, and advance the living simulation for the full shift duration.

Part 6 also corrects the Part 5 gardening integration defect found during player testing. Fresh games now start with zero seed stock. Crop-specific sow actions are unavailable without owned seed units, direct stale-action attempts are rejected server-side, purchases add seed units, and sowing consumes them. The cumulative diagnostic now permanently checks both the positive and negative seed-inventory invariants.
