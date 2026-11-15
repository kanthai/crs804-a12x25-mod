# MakerWorld / Printables listing — DRAFT

**Title:** MikroTik CRS804-4DDQ silent fan mod — 1 × Noctua NF-A12x25 replaces both 40 mm fans (RouterOS-controlled)

**Short description:**
Two printed plugs slide into the CRS804's hot-swap fan bays and duct both bays into one 120 mm Noctua NF-A12x25,
tilted 45° behind the switch. The fan plugs into the original MikroTik connectors, so RouterOS still controls and
monitors it (fan-state = ok). No soldering on the switch, fully reversible.

**Results (same room, AC off):** switch chip 6–7 °C cooler than 2 × Noctua NF-A4x20 at the same room temperature;
peak 57 °C on a 34.9 °C day, near-silent instead of the stock 18,500 rpm Deltas.

**Print profile:** PETG (ASA for long term), 0.20 mm, 3–4 walls, no supports.
- Part A (plugs + flange, with snap detent): flange on the bed
- Part B (plenum + fan plate): small flange on the bed
- Part C (grommet): lip down
Tested on a Bambu Lab X1C; plugs are modelled at the exact carrier size.

**Hardware:** NF-A12x25 PWM, 4 × M3×4×5 heat-set inserts, 4 × M3×6 + 4 × M3 screws, the two original MikroTik fan
connectors (from the stock modules), a second 4-pin extension for the tach branch, mini cable ties.

**Wiring + RouterOS settings + design notes:** see the README / linked repo.

**Photos:** `docs/photos/` (cover: 03-installed-top.jpg, then 01, 02, 04, 05, 07, 08, 06)
