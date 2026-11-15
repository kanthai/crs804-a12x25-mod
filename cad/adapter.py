"""CRS804-4DDQ in-bay fan adapter + tilted Noctua NF-A12x25 plenum (three printed parts: A plugs, B plenum, C grommet).
Axes: X across the bays, Y up (desk at Y = -BAY_CY), Z depth (+Z out of the rear panel; bays are Z<0).
Part A = two carrier-shaped plugs + mating flange.  Part B = plenum + fan plate + mating flange.
Joined with 4x M3 (Part A: 2.9 mm pilot for self-tapping or heat inserts; Part B: 3.4 mm clearance).
Dimensions measured on a real CRS804-4DDQ fan carrier unless marked PLACEHOLDER.  Units mm.
"""
from build123d import *
import math, json, os

# ---- measured ----
CAR_W, CAR_H, CAR_D = 43.23, 40.65, 44.19   # carrier itself, excluding connector
PARTITION = 3.4                             # metal wall between the two bays 
CAR_BOTTOM = 5.0                            # desk -> carrier bottom (switch feet)
LATCH_W, LATCH_BUMP = 10.0, 1.5             # left side, vertically centred; bump assumed OUTSIDE CAR_W
LATCH_FROM_BACK = 2.5                       # bump edge 2.5 mm in from the carrier's OUTER end (rear-panel side)
CONN_TIP = 16.0                             # connector tip beyond the carrier's inner end
CONN_WALL = 0.8                             # carrier floor the connector sits on (connector is at the BOTTOM, centred)
# ---- placeholders ----
CONN_W, CONN_L = 20.0, 12.0                 # PLACEHOLDER connector footprint on the floor: width x length along depth
CONN_ENABLE = True
# v4.3 connector mount : housing 39.78 long ear-to-ear, 7.44 thick, 8 cavities
# (wire side: 2 yellow PWM, 4 blue tach, 6 red +12 V, 8 black GND); ears on the fan's lower screw pair.
CONN_HOLE_DX = 16.0                         # +/- from plug centre (40 mm fan hole pattern, 32 mm pitch)
FAN_FROM_GRILLE, FAN_T = 9.0, 28.0         # on the carrier the Delta (40x40x28) sits 9 mm in from the grille (outer) end
# The connector ears screw onto the fan's inner face, i.e. 9 + 28 = 37 mm in from the outer end = 7.19 mm short of
# the inner end (v4.4; v4.3 wrongly had them flush with the inner end).
CONN_FACE_INSET = float(os.environ.get("CONN_INSET", CAR_D - (FAN_FROM_GRILLE + FAN_T)))
INSERT_L, INSERT_OD = 4.0, 5.0              # heat-set insert M3 x L4 x OD5 
INSERT_BORE = float(os.environ.get("INSERT_BORE", INSERT_OD - 0.4))   # 4.6 for OD5
BOSS_WALL = 1.8
BOSS_D = 10.0                               # boss depth along the plug (toward the outer end) - stiff, tied to floor + rail
STREAMLINE = os.environ.get("STREAMLINE", "1") == "1"   # v4.5: faired standoff tails + lozenge tie anchors
FAIR_L = 12.0                               # standoff tail length (flow is from the inner end toward the outer end)
CHAMF = 2.0                                 # chamfer on the standoff's exposed top-inboard edge
import os
LATCH_ENABLE = os.environ.get("LATCH", "1") == "1"   # LATCH=0: smooth rails, friction fit (no slots, no bump)
VERSION = os.environ.get("VERSION", "v4.9")   # running version: .x = minor revision, new major = redesign 
SUFFIX = "" if LATCH_ENABLE else "_smooth"
# ---- design ----
FDM = float(os.environ.get("FDM", 0.0))    # per-side width allowance: 0 = exact carrier (X1C prints true; 0.10 was loose)
FDM_H = float(os.environ.get("FDM_H", 0.0))   # per-side HEIGHT allowance: 0.10 fitted loose in the bays 
CLOSED_TB = os.environ.get("CLOSED_TB", "1") == "1"   # closed top+bottom walls (less leakage); 0 = open like the carrier
TB_WALL = 0.8                               # top/bottom wall when closed (= carrier wall; 2 perimeters @0.4)
RAIL = 1.6
TILT = 45.0
PLEN_LEN = 30.0
WALL = 2.0
FLANGE_T = 3.0
FAN, FAN_PITCH, FAN_HOLE, FAN_OPEN = 120.0, 105.0, 4.4, 116.0

BAY_CY = CAR_BOTTOM + CAR_H / 2             # bay centre above desk = 25.33
PITCH = CAR_W + PARTITION                   # 44.91
W, H = CAR_W - 2 * FDM, CAR_H - 2 * FDM_H
xs = (-PITCH / 2, PITCH / 2)
IN_W = PITCH + W                            # outer width across both plugs
# A<->B interface (flange outline, M3 holes, plenum inlet). Defaults to this build; B_PITCH=44.91 reproduces the
# interface of the first-printed Part B (made with the 1.68 mm partition) so a new Part A bolts onto it.
B_PITCH = float(os.environ.get("B_PITCH", PITCH))
IN_W_B = B_PITCH + float(os.environ.get("B_W", W))   # B_W=43.03 = plug width the first Part B was built with
if B_PITCH != PITCH:
    SUFFIX += "_fitB%.2f" % B_PITCH            # (kept for the report; file names use VERSION)
DESK = -BAY_CY
DESK_CLEAR = float(os.environ.get("DESK_CLEAR", 3.0))   # v4.8: nothing below desk + 3 mm (switch must stand on its own feet)

CABLE_CLIPS = os.environ.get("CLIPS", "0") == "1"   # Part A tie anchors: OFF since v4.9 (crowded the connector, little use). Part B inlet anchor stays.
ANCHOR_Z = (-9.0, -22.0)                    # anchor centres along each plug (connector pad starts at -CAR_D + CONN_L + 4)
TIE_W, TIE_T = 3.2, 1.6                     # slot for a 2.5 mm mini cable tie

def tie_anchor(base_pt, up=(0, 1, 0)):
    """Cable-tie anchor standing on a wall whose inward normal is +Y: a 7 (X) x 3.6 (up) x 5 (Z) block with a
    TIE_W x TIE_T slot running across X; the cable lies on top along Z, the tie goes through the slot and around it.
    Sunk 0.4 mm into the wall so it fuses (no coincident faces)."""
    bx, by, bz = base_pt
    if not STREAMLINE:
        blk = Pos(bx, by + 1.8 - 0.4, bz) * Box(7.0, 3.6 + 0.4, 5.0)
    else:
        # v4.5: lozenge plan pointed along the flow (Z): 7 wide, flat 4 mm middle (cable seat + tie slot), tips +/-5.5
        pts = [(-3.5, -2.0), (0.0, -5.5), (3.5, -2.0), (3.5, 2.0), (0.0, 5.5), (-3.5, 2.0)]
        pl = Plane(origin=(bx, by - 0.4, bz), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
        blk = extrude(pl * Polygon(*pts, align=None), amount=3.6 + 0.4)
        bb = blk.bounding_box()                           # extrude follows winding: put it on the wall, centred on bz
        blk = blk.translate((0, (by - 0.4) - bb.min.Y, bz - (bb.min.Z + bb.max.Z) / 2))
    blk -= Pos(bx, by + 1.0 + TIE_T / 2, bz) * Box(9.0, TIE_T, TIE_W)
    return blk

def plug(x):
    p = Pos(x, 0, -CAR_D / 2) * Box(W, H, CAR_D)
    ch = (H - 2 * TB_WALL) if CLOSED_TB else (H + 2)                      # channel height: closed tube or open top/bottom
    p -= Pos(x, 0, -CAR_D / 2) * Box(W - 2 * RAIL, ch, CAR_D + 2)
    for z0 in (() if CLOSED_TB else (-CAR_D + 1.5, -1.5)):                  # end frames tie open rails together (not needed when closed)
        for y0 in (H / 2 - 0.6, -H / 2 + 0.6):
            p += Pos(x, y0, z0) * Box(W, 1.2, 3.0)
    # snap latch on the LEFT rail: U-slot cantilever, FREE end toward the panel (outer end), hinge deeper inside
    lx = x - W / 2 + RAIL / 2
    tab_len, tab_h, slot = LATCH_W + 8.0, 7.0, 0.8
    t_out = -1.2                                   # tab's free end, 1.2 mm in from the outer end (0.4 mm rail bridge kept)
    zt = t_out - tab_len / 2                       # tab centre; hinge at t_out - tab_len
    zc = -(LATCH_FROM_BACK + LATCH_W / 2)          # bump centre: edge 2.5 mm from the outer end
    if LATCH_ENABLE:
        for yy in (tab_h / 2 + slot / 2, -tab_h / 2 - slot / 2):             # slots above and below the tab
            p -= Pos(lx, yy, zt + slot / 2) * Box(RAIL + 1, slot, tab_len + slot)
        p -= Pos(lx, 0, t_out + slot / 2) * Box(RAIL + 1, tab_h + 2 * slot, slot)   # slot across the free end
    # bump = pull-to-release detent: 45-degree ramps on BOTH ends, so it clicks in and pops out with a firm pull
    # (the tab flexes inward either way). Profile in the X-Z plane, extruded along Y.
    if LATCH_ENABLE:
        bx0 = x - W / 2 + 0.3                       # 0.3 mm into the tab (overlap, no coincident faces)
        bx1 = x - W / 2 - LATCH_BUMP                # outer face
        rz = min(LATCH_BUMP, LATCH_W / 2 - 1.0)     # ramp length along Z (45 deg)
        prof = [(bx0, zc - LATCH_W / 2), (bx0, zc + LATCH_W / 2), (bx1 + 0.0, zc + LATCH_W / 2 - rz - 0.3),
                (bx1, zc - LATCH_W / 2 + rz + 0.3)]
        pl = Plane(origin=(0, -(tab_h - 1.0) / 2, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))   # local (x, -z)
        face = pl * Polygon(*[(px, -pz) for px, pz in prof], align=None)
        bump = extrude(face, amount=tab_h - 1.0)
        bb = bump.bounding_box()                    # extrude direction follows the polygon winding: re-centre on the tab
        bump = bump.translate((0, -(bb.min.Y + bb.max.Y) / 2, zc - (bb.min.Z + bb.max.Z) / 2))
        p += bump
    if CONN_ENABLE:
        # v4.3: the salvaged card-edge connector mounts exactly as on the MikroTik carrier: its two ears take the
        # fan's two LOWER screws (40 mm fan pattern: +/-16 mm, 16 mm below centre). Two bosses at the plug's inner
        # end, flush with the end face, each with a heat-set insert bore (insert pressed in from the end face).
        hole_y = -CAR_H / 2 + (CAR_H - 40.0) / 2 + 4.0          # = -16.0: fan bottom holes inside the carrier
        z_face = -CAR_D + CONN_FACE_INSET                        # ear mounting plane (carrier: fan frame face)
        floor_y = -H / 2 + (TB_WALL if CLOSED_TB else 0.0)
        rail_in = W / 2 - RAIL                                   # inner rail face, relative to plug centre
        for sx in (-1, 1):
            hx = x + sx * CONN_HOLE_DX
            r = INSERT_BORE / 2 + BOSS_WALL
            # block from the floor up past the hole, out to the rail (fuses with both), BOSS_D deep from the face
            x_in, x_out = sx * (CONN_HOLE_DX - r), sx * (rail_in + 0.3)
            bx0, bx1 = min(x_in, x_out), max(x_in, x_out)
            y0, y1 = floor_y - 0.3, hole_y + r
            p += Pos(x + (bx0 + bx1) / 2, (y0 + y1) / 2, z_face + BOSS_D / 2) * Box(bx1 - bx0, y1 - y0, BOSS_D)
            if STREAMLINE:
                # v4.5 (mating face untouched): tapered tail downstream (toward the outer end) into the floor/rail
                # corner, and a chamfer on the exposed top-inboard edge starting 1 mm behind the face.
                z_end = z_face + BOSS_D
                x_rail = sx * rail_in
                tail_w, tail_h = 1.2, 1.2                     # what's left at the tail tip, hugging the corner
                tx0, tx1 = (x_rail - tail_w, x_rail + 0.3) if sx > 0 else (x_rail - 0.3, x_rail + tail_w)
                s0 = Plane.XY.offset(z_end - 0.01) * Pos(x + (bx0 + bx1) / 2, (y0 + y1) / 2) * Rectangle(bx1 - bx0, y1 - y0)
                s1 = Plane.XY.offset(z_end + FAIR_L) * Pos(x + (tx0 + tx1) / 2, y0 + tail_h / 2) * Rectangle(tx1 - tx0, tail_h)
                p += loft([s0, s1], ruled=True)
                xi = x + (bx0 if sx > 0 else bx1)             # inboard edge (toward the plug centre)
                c = CHAMF
                tri = [(xi, y1 + 0.01), (xi + sx * c, y1 + 0.01), (xi - sx * 0.01, y1 - c)]
                cp = Plane(origin=(0, 0, z_face + 1.0), x_dir=(1, 0, 0), z_dir=(0, 0, 1))
                pr = extrude(cp * Polygon(*tri, align=None), amount=BOSS_D - 1.0 + 0.02)
                pb = pr.bounding_box()                        # extrude follows winding: pin it to [face+1, end]
                pr = pr.translate((0, 0, (z_face + 1.0) - pb.min.Z))
                p -= pr
            # insert bore from the end face (vertical when printed flange-down) + 0.4 mm lead-in chamfer
            p -= Pos(hx, hole_y, z_face + (INSERT_L + 1.0) / 2 - 0.01) * Cylinder(INSERT_BORE / 2, INSERT_L + 1.0)
            p -= Pos(hx, hole_y, z_face + 0.2 - 0.01) * Cylinder(INSERT_BORE / 2 + 0.4, 0.4)
    if CABLE_CLIPS and CLOSED_TB:
        # cable-tie anchors on the inside of the bottom wall, leading to the connector pad (cable runs along Z on top)
        for za in ANCHOR_Z:
            p += tie_anchor((x, -H / 2 + TB_WALL, za), up=(0, 1, 0))
    return p

# ---- Part A: plugs + flange ----
EAR = 9.0                                   # flange ear beyond the plugs on each side (screw holes here)
FL_TOP = H / 2 + 5.0                        # flange top edge
FL_BOT = DESK + DESK_CLEAR                  # flange bottom edge (v4.8: 3 mm above the desk; was 0.5 and lifted the switch)
holes = [(sx * (IN_W_B / 2 + EAR / 2), hy) for sx in (-1, 1) for hy in (-10.0, 10.0)]

def flange(z, opening_w, opening_h, hole_r, windows=None):
    """windows: list of (x_centre, w, h) openings; default one centred opening_w x opening_h."""
    fh = FL_TOP - FL_BOT
    f = Pos(0, (FL_TOP + FL_BOT) / 2, z + FLANGE_T / 2) * Box(IN_W_B + 2 * EAR, fh, FLANGE_T)
    for wx, ww, wh in (windows or [(0.0, opening_w, opening_h)]):
        f -= Pos(wx, 0, z + FLANGE_T / 2) * Box(ww, wh, FLANGE_T + 2)
    for hx, hy in holes:
        f -= Pos(hx, hy, z + FLANGE_T / 2) * Cylinder(hole_r, FLANGE_T + 2)
    return f

CH_A = (H - 2 * TB_WALL) if CLOSED_TB else (H - 2.4)
# one window per plug channel: the divider (inner rails + partition slot) continues flush to the mating face with B
flA = flange(0.0, 0, 0, 1.45, windows=[(x, W - 2 * RAIL, CH_A) for x in xs])  # opening 2.4 shorter than the plugs: overlap, no shared edges          # 2.9 mm pilot: M3 self-tap / heat insert
partA = plug(xs[0]) + plug(xs[1]) + flA
partA -= Pos(0, DESK + DESK_CLEAR - 100, 0) * Box(2000, 200, 2000)           # never below desk + DESK_CLEAR

# ---- Part B: plenum + fan plate ----
z0 = FLANGE_T
flB = flange(z0, IN_W_B, H, 1.7)                       # 3.4 mm clearance for M3
t = math.radians(TILT)
cz = z0 + FLANGE_T + PLEN_LEN + FAN / 2 * math.sin(t)
cy = DESK + (FAN + 2.0) / 2 * math.cos(t) + DESK_CLEAR   # v4.8: the 122 mm plate's lowest edge sits DESK_CLEAR above the desk
fp = Plane(origin=(0, cy, cz), x_dir=(1, 0, 0), z_dir=(0, math.sin(t), math.cos(t)))
base = Plane.XY.offset(z0 + FLANGE_T)
outer = loft([base * RectangleRounded(IN_W_B + 2 * WALL, H + 2 * WALL, 3.0 + WALL), fp * Circle(FAN_OPEN / 2 + WALL)], ruled=False)
inner = loft([base.offset(-1.0) * RectangleRounded(IN_W_B, H, 3.0), fp.offset(1.0) * Circle(FAN_OPEN / 2)], ruled=False)   # 1 mm past both ends: no slivers
PLATE = FAN + 2.0                            # >120 so the 120 mm wall ring overlaps, not tangent
plate = fp * extrude(Rectangle(PLATE, PLATE), amount=4)
plate -= fp * extrude(Circle(FAN_OPEN / 2), amount=4)
for sx in (-1, 1):
    for sy in (-1, 1):
        plate -= fp * Pos(sx * FAN_PITCH / 2, sy * FAN_PITCH / 2, 0) * extrude(Circle(FAN_HOLE / 2), amount=4)
partB = flB + (outer - inner) + plate

# ---- v4.2: cable port (keyhole) on the RIGHT side as you look at the fan (= +X, same view as "left latch") ----
PORT = os.environ.get("PORT", "1") == "1"
PORT_BACK = 10.0                             # port centre this far back from the fan plate, along the fan axis
PASS_U, PASS_V, PASS_R = 8.0, 13.5, 1.5      # pass-through 13.5 x 8 (v4.7: = the opening enlarged by hand; header 10.6 x 6 + cable); u = along the fan axis
SEAT_D, SEAT_U = 5.0, -8.5                   # seat for the 4.5 mm cable, offset away from the plate (u < 0 = toward the switch)
n = Vector(0, math.sin(t), math.cos(t))      # fan axis (out of the plate)
b = Vector(0, math.cos(t), -math.sin(t))     # in the Y-Z plane, perpendicular to the axis
pc = Vector(0, cy, cz) - n * PORT_BACK       # port centre on the plenum axis; cut runs along +X through the right wall
port_plane = Plane(origin=(0, pc.Y, pc.Z), x_dir=(n.X, n.Y, n.Z), z_dir=(1, 0, 0))   # local x = u (fan axis), local y = v
def keyhole(grow=0.0):
    s = RectangleRounded(PASS_U + 2 * grow, PASS_V + 2 * grow, PASS_R + grow)
    s += Pos(SEAT_U, 0) * Circle(SEAT_D / 2 + grow)
    s += Pos(SEAT_U / 2, 0) * Rectangle(abs(SEAT_U), SEAT_D + 2 * grow)
    return s
if PORT:
    partB -= port_plane * Pos(0, 0, 40) * extrude(keyhole(), amount=45)       # from x=40 outward: right wall only
    # tie anchor on the plenum floor just inside the inlet, right of centre (toward the port)
    partB += tie_anchor((IN_W_B / 4, -H / 2, z0 + FLANGE_T + 4.0))
partB -= Pos(0, DESK + DESK_CLEAR - 100, 0) * Box(2000, 200, 2000)

# ---- Part C (v4.2): snap-in grommet for the pass-through (cable then sits in the 5 mm seat) ----
GROM_CLEAR = 0.15
grommet = extrude(RectangleRounded(PASS_U - 2 * GROM_CLEAR, PASS_V - 2 * GROM_CLEAR, PASS_R - GROM_CLEAR), amount=WALL + 0.6)
grommet += Pos(0, 0, WALL + 0.6) * extrude(RectangleRounded(PASS_U + 4, PASS_V + 4, PASS_R + 2), amount=1.2)   # outer lip
# small catch ridges on the long sides (snap behind the wall)
for sv in (-1, 1):
    grommet += Pos(0, sv * (PASS_V / 2 - GROM_CLEAR + 0.15), 0.4) * Box(PASS_U - 2.5, 0.6, 0.8)

report = {}
A_NAME = f"{VERSION}_partA_" + ("detent" if LATCH_ENABLE else "smooth")
PARTS = [(A_NAME, partA)]
if B_PITCH == PITCH or os.environ.get("BUILD_B") == "1":      # BUILD_B=1: plenum with the pinned (legacy) interface
    PARTS += [(f"{VERSION}_partB_plenum", partB)]
    if PORT:
        PARTS += [(f"{VERSION}_partC_grommet", grommet)]
for name, part in PARTS:
    bb = part.bounding_box().size
    report[name] = dict(valid=part.is_valid, solids=len(part.solids()), bbox=[round(v, 1) for v in bb], cm3=round(part.volume / 1000, 1))
    export_step(part, f"{name}.step")
    try:
        m = Mesher(); m.add_shape(part); m.write(f"{name}.3mf")
    except Exception as e:
        report.setdefault("warnings", []).append(f"{name} 3mf: {e}")
    # STL from the same (validated) mesh as the 3MF: build123d's export_stl leaves gaps on the lofted plenum
    import trimesh
    tm = trimesh.load(f"{name}.3mf").to_geometry(); tm.merge_vertices(); tm.process(validate=True)
    tm.export(f"{name}.stl")
    report[name]["mesh_watertight"] = bool(tm.is_watertight)
asm = partA + partB
export_step(asm, f"{VERSION}_assembly_{'detent' if LATCH_ENABLE else 'smooth'}.step")
report["interface"] = dict(b_pitch=B_PITCH, holes_x=round(IN_W_B / 2 + EAR / 2, 2), plug_outer_x=round(IN_W / 2, 2), hole_edge_to_plug=round(IN_W_B / 2 + EAR / 2 - 1.45 - IN_W / 2, 2), flangeA_windows=[round(W - 2 * RAIL, 2), round(CH_A, 2)], divider_w=round(PITCH - W + 2 * RAIL, 2), plug_channel_outer_x=round(IN_W / 2 - RAIL, 2), plenum_inlet_x=round(IN_W_B / 2, 2))
report["geometry"] = dict(bay_centre_above_desk=round(BAY_CY, 2), pitch=round(PITCH, 2), plug_w=round(W, 2),
                          gap_between_plugs=round(PITCH - W, 2), behind_panel=round(asm.bounding_box().max.Z, 1),
                          height_above_desk=round(asm.bounding_box().max.Y - DESK, 1))
report["print_up_partB_fanplate_on_bed"] = [0.0, -round(math.sin(t), 4), -round(math.cos(t), 4)]
print(json.dumps(report, indent=1))
