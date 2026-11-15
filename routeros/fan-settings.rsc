# SPDX-License-Identifier: MIT
# MikroTik CRS804-4DDQ fan controller settings for a single Noctua NF-A12x25 PWM (via the A12x25 adapter)
# RouterOS 7.25+ (7.25 shortened the fan control interval to 10 s; on 7.24 the 30 s loop overshoots badly).
#
# Why these values:
#  - fan-min-speed-percent=40 : the default 12 % runs an A12x25 at ~270 rpm - too little air, the switch chip
#    overheats past the target, the fan jumps to full speed, cools, drops back -> sawtooth. 40 % ~= 900 rpm, silent.
#  - fan-target-temp=55       : chip temperature the controller holds. The A12x25 is quiet even flat out, so a low
#    target keeps the chip cool; it reaches full speed (~2,040 rpm) at roughly 32 C room and up.
#  - fan-full-speed-temp=65   : RouterOS maximum on this model (cannot be set higher).
#  - Never set fan-target-temp = fan-full-speed-temp: it saw-tooths between minimum and full speed every few minutes.

/system/health/settings/set fan-min-speed-percent=40 fan-target-temp=55 fan-full-speed-temp=65

# check:
/system/health/print
# expect: fan-state=ok, fan1-speed = fan2-speed (both from the one A12x25 tach), switch-temperature near 55 C
