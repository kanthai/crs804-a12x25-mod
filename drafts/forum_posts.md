# Forum posts — DRAFTS (review before posting)

## 1. MikroTik forum — reply in "MikroTik CRS804 - FANS LOUD!"
(https://forum.mikrotik.com/t/mikrotik-crs804-fans-loud/271896)

For anyone still fighting the CRS804 fan noise: I ended up replacing both 40 mm Delta modules with a 3D-printed
adapter that ducts both fan bays into one Noctua NF-A12x25, and it works well.

- The printed plugs slide into the fan bays like the stock carriers; the fan sits tilted behind the switch.
- The fan plugs into the **original MikroTik fan connectors** (Noctua's crimp terminals fit the cavities), so RouterOS
  still controls the speed and reports `fan-state=ok` (one fan's tach goes to both fan inputs).
- Same room, AC off: switch chip 6–7 °C cooler than two NF-A4x20 at full speed, peak 57 °C on a 34.9 °C day,
  and it's near-silent.
- Settings that made it behave: `fan-min-speed-percent=40 fan-target-temp=55` (the default 12 % minimum spins a
  120 mm fan at ~270 rpm and makes it saw-tooth). RouterOS 7.25+ (10 s control loop) helps a lot.
- Useful facts I measured: the Delta FFB0412UHN-C is **blue = PWM, yellow = tach**; MikroTik connector cavities
  (wire side) 2 = tach, 4 = PWM, 6 = +12 V, 8 = GND.

Files, wiring diagram and data: <link>

## 2. NVIDIA developer forum — reply in "MikroTik CRS804 - FANS LOUD!" (DGX Spark / GB10)
(https://forums.developer.nvidia.com/t/mikrotik-crs804-fans-loud/378209)

Follow-up for Spark cluster owners on a CRS804: I made the switch near-silent by replacing the two 40 mm fan modules
with a printed adapter + one Noctua NF-A12x25 (RouterOS-controlled through the original fan connectors). With four
Sparks on 200G breakouts, the switch chip runs 54–57 °C (peak on a 34.9 °C day, AC off), 6–7 °C cooler than with two
Noctua NF-A4x20, and links are unaffected. Before printing, RouterOS 7.25 alone already tamed the fan "take-off"
bursts (shorter fan control loop). Files + settings: <link>
