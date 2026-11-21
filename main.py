#!/usr/bin/env python3
"""THE WORLD TODAY - Saturday 21 November 2026 in one image.

Entry for make.fun's news-image-20261121 bounty. Pure Python 3 standard
library: the program draws a newspaper front page of the day entirely
in code (its own 5x7 bitmap font and rasteriser) and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

The day's stories, each cross-checked across at least two independent
news sources reporting 21 November 2026:
  * Russia fires 404 drones and 111 missiles (27 ballistic, 84
    cruise) at Ukraine in the biggest bombardment of November; at
    least 8 killed, Kyiv bridges and power infrastructure hit. Two
    missiles and a suspected drone come down in Poland near the
    Nowa Deba exercises; PM Tusk calls it an intentional provocation,
    NATO's Rutte a grave violation.
    (AP via Reflector and EuropeSays; ISW's 20 Nov assessment;
    One Turn's 21 Nov brief; France 24 / CBS via One Turn)
  * An AI and chip sell-off pushes the S&P 500 and the Dow into
    correction; US stocks fall 3.7% in the worst week in over
    18 months. (One Turn's 21 Nov brief; AP market wrap)
  * COP31 in Antalya, Turkiye runs into overtime: nearly 200
    nations miss the deadline with no agreement on fossil fuels.
    (One Turn's 21 Nov brief; European news wires, 21 Nov)
  * The UK and the EU sign their biggest post-Brexit agreements in
    Brussels: food exports, carbon markets and youth mobility.
    (One Turn's 21 Nov brief; TFI's 21 Nov front page)
  * The pancreatic cancer pill daraxonrasib, with chemotherapy,
    makes tumours undetectable in 1 in 12 patients and shrinks or
    clears them in 6 in 10, in results presented in Barcelona.
    (Medindia; The News International; NY Post; EMJ Reviews)
  * A fire at the Hartha power station north of Basra, Iraq kills
    at least four people and injures 30. (Reuters, 21 Nov)
Ticker: Mongolia's president resigns (Binder wire, 21 Nov); the EU
approves 1 billion euros in defence aid for Ukraine (Binder wire);
Iran says it downed a US MQ-9 drone over the Strait of Hormuz
(Standard Topic's 21 Nov archive); James Harden scores 51 for
Cleveland (Reuters NBA roundup).

No network, no inputs: two runs write byte-identical files.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 242, 231)
PANEL = (252, 250, 243)
INK = (24, 24, 28)
GRAY = (96, 92, 84)
RED = (178, 30, 30)
BLUE = (28, 62, 138)
SKY = (170, 198, 224)
SEA = (62, 108, 156)
GOLD = (198, 148, 26)
GREEN = (28, 128, 66)
DARK = (14, 16, 32)
WHITE = (246, 246, 246)
CLOUD = (218, 224, 232)
ORANGE = (232, 116, 28)
BROWN = (120, 90, 50)

# ---------------------------------------------------------------- canvas

_buf = bytearray(PAPER * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        _buf[i] = c[0]
        _buf[i + 1] = c[1]
        _buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for ox in range(t):
            for oy in range(t):
                px(x0 + ox, y0 + oy, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(cy - r - t, cy + r + t + 1):
        for xx in range(cx - r - t, cx + r + t + 1):
            d = math.hypot(xx - cx, yy - cy)
            if r - t <= d <= r:
                px(xx, yy, c)


# ------------------------------------------------------------------ font
# 5x7 bitmap glyphs, each row a 5-bit integer, bit 4 = leftmost pixel.

FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 10, 4, 4, 4, 10, 17),
    "Y": (17, 10, 4, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 2, 4, 8, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 31, 0, 0, 0),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "/": (1, 1, 2, 4, 8, 16, 16),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "+": (0, 4, 4, 31, 4, 4, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "$": (4, 14, 21, 14, 5, 14, 4),
    "%": (25, 26, 2, 4, 8, 11, 19),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def text(x, y, s, scale, c):
    for ch in s.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    rect(x + col * scale, y + row * scale, scale, scale, c)
        x += 6 * scale
    return x


def text_c(cx, y, s, scale, c):
    return text(cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, c, max_w, pitch=None):
    if pitch is None:
        pitch = 9 * scale
    for ln in wrap(s, scale, max_w):
        text(x, y, ln, scale, c)
        y += pitch
    return y


# ---------------------------------------------------------- illustrations

def draw_lead_banner(x, y, w, h):
    # night over Kyiv: skyline, missile trails, bursts, and at the far
    # right the white-and-red flag of Poland, where two missiles and
    # a drone came down
    rect(x, y, w, h, DARK)
    seed = 20261121
    for _ in range(70):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sx = x + seed % (w - 170)
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sy = y + seed % (h - 22)
        px(sx, sy, WHITE)
    base = y + h
    for bx, bw, bh in ((6, 52, 20), (66, 30, 30), (104, 44, 16),
                       (156, 24, 34), (188, 54, 22), (250, 30, 28),
                       (288, 46, 18), (342, 26, 32), (376, 50, 20),
                       (434, 30, 26), (472, 44, 16), (524, 26, 30),
                       (558, 48, 20), (614, 30, 24), (652, 40, 17)):
        rect(x + bx, base - bh, bw, bh, (50, 54, 82))
    rect(x + 162, base - 38, 12, 38, GOLD)
    disc(x + 168, base - 41, 7, GOLD)
    # three missile trails arcing down from the top left
    for tx, ty, ex, ey in ((90, 4, 300, 34), (210, 2, 470, 38),
                           (330, 6, 640, 32)):
        line(x + tx, y + ty, x + ex, y + ey, CLOUD, 2)
        disc(x + ex, y + ey, 4, RED)
        disc(x + ex, y + ey, 2, GOLD)
    # one burst over the skyline
    bx, by = x + 470, y + 36
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        line(bx, by, bx + int(13 * math.cos(rad)),
             by + int(13 * math.sin(rad)), GOLD, 2)
    # Poland flag at the right end, sized to fit the banner's height
    fx, fy = x + w - 148, y + 8
    rect(fx, fy, 120, 14, WHITE)
    rect(fx, fy + 14, 120, 14, RED)
    frame(fx, fy, 120, 28, CLOUD, 1)


def draw_chart(x, y, w, h):
    # a market chart that climbs, then plunges into correction
    rect(x, y, w, h, DARK)
    frame(x, y, w, h, GRAY, 1)
    for gy in range(y + 12, y + h - 6, 14):
        line(x + 6, gy, x + w - 6, gy, (44, 48, 66), 1)
    pts = ((8, 44), (30, 38), (52, 40), (74, 30), (96, 32), (112, 22))
    for i in range(len(pts) - 1):
        line(x + pts[i][0], y + pts[i][1], x + pts[i + 1][0],
             y + pts[i + 1][1], GREEN, 2)
    line(x + 112, y + 22, x + w - 26, y + h - 12, RED, 3)
    line(x + w - 40, y + h - 14, x + w - 24, y + h - 10, RED, 3)
    line(x + w - 26, y + h - 26, x + w - 24, y + h - 10, RED, 3)
    text(x + 8, y + 6, "AI STOCKS", 1, CLOUD)


def draw_globe(x, y, w, h):
    # a warming globe: ocean disc, land blobs, sun, rising heat bars
    cx, cy, r = x + 44, y + h // 2, 34
    disc(cx, cy, r, SEA)
    for gx, gy, gr in ((cx - 16, cy - 14, 10), (cx + 8, cy - 18, 8),
                       (cx - 4, cy + 8, 12), (cx + 18, cy + 12, 7),
                       (cx - 22, cy + 16, 6)):
        disc(gx, gy, gr, GREEN)
    ring(cx, cy, r, INK, 1)
    sx, sy = x + w - 30, y + 16
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        line(sx + int(13 * math.cos(rad)), sy + int(13 * math.sin(rad)),
             sx + int(19 * math.cos(rad)), sy + int(19 * math.sin(rad)),
             GOLD, 2)
    disc(sx, sy, 11, GOLD)
    for i, bh in enumerate((10, 18, 28)):
        rect(x + w - 62 + i * 16, y + h - 12 - bh, 10, bh, RED)


def flag_uk(x, y, w, h):
    rect(x, y, w, h, BLUE)
    line(x, y, x + w, y + h, WHITE, 5)
    line(x + w, y, x, y + h, WHITE, 5)
    line(x, y, x + w, y + h, RED, 2)
    line(x + w, y, x, y + h, RED, 2)
    rect(x + w // 2 - 7, y, 14, h, WHITE)
    rect(x, y + h // 2 - 7, w, 14, WHITE)
    rect(x + w // 2 - 4, y, 8, h, RED)
    rect(x, y + h // 2 - 4, w, 8, RED)


def flag_eu(x, y, w, h):
    rect(x, y, w, h, BLUE)
    cx, cy = x + w // 2, y + h // 2
    for k in range(12):
        ang = math.radians(k * 30 - 90)
        sx = cx + int((w // 3) * math.cos(ang))
        sy = cy + int((h // 3) * math.sin(ang))
        rect(sx - 2, sy - 2, 4, 4, GOLD)


def draw_flags(x, y):
    flag_uk(x, y, 66, 44)
    frame(x, y, 66, 44, INK, 1)
    flag_eu(x + 76, y, 66, 44)
    frame(x + 76, y, 66, 44, INK, 1)


def draw_flames(x, y, w, h):
    # the Hartha power station ablaze: a pylon silhouette against a
    # dark sky, with layered flame tongues along the ground
    rect(x, y, w, h, DARK)
    frame(x, y, w, h, GRAY, 1)
    gy = y + h - 8
    # pylon: two legs, cross braces and a top bar
    line(x + 30, gy, x + 48, y + 14, CLOUD, 2)
    line(x + 78, gy, x + 60, y + 14, CLOUD, 2)
    line(x + 22, y + 22, x + 86, y + 22, CLOUD, 2)
    line(x + 34, gy - 22, x + 74, gy - 40, CLOUD, 1)
    line(x + 74, gy - 22, x + 34, gy - 40, CLOUD, 1)
    # flame tongues: wide red bases, orange middles, gold tips
    for fx, fh in ((96, 30), (116, 44), (140, 26), (156, 38)):
        for t in range(fh):
            half = max(2, (fh - t) // 4)
            c = RED if t < fh // 3 else (ORANGE if t < 2 * fh // 3
                                         else GOLD)
            rect(x + fx - half, gy - t, half * 2, 1, c)
    rect(x, gy, w, 3, (52, 40, 30))


def draw_pill(x, y):
    # one big two-tone capsule, tilted, with sparkle crosses of hope:
    # a row of discs along a falling diagonal, red half then white,
    # with a dark seam where the two halves join
    for t in range(-17, 18):
        disc(x + 62 + t, y + 42 - t // 2, 16, RED if t < 0 else WHITE)
    ring(x + 45, y + 50, 16, INK, 1)
    ring(x + 79, y + 34, 16, INK, 1)
    line(x + 60, y + 28, x + 64, y + 56, INK, 2)
    for sx, sy in ((x + 8, y + 6), (x + 118, y + 58), (x + 126, y + 2)):
        line(sx - 5, sy, sx + 5, sy, GOLD, 2)
        line(sx, sy - 5, sx, sy + 5, GOLD, 2)


# ------------------------------------------------------------------ page

def story_panel(x, y, w, h, kicker, head_lines, body, art):
    frame(x, y, w, h, INK, 2)
    rect(x + 2, y + 2, w - 4, h - 4, PANEL)
    text(x + 20, y + 14, kicker, 2, RED)
    yy = y + 38
    for hl in head_lines:
        text(x + 20, yy, hl, 3, INK)
        yy += 27
    art(x + w - 168, y + 34)
    para(x + 20, y + 126, body, 2, INK, w - 40, 17)


def build():
    # masthead
    rect(24, 20, 976, 3, INK)
    text_c(512, 30, "THE WORLD TODAY", 9, INK)
    rect(24, 100, 976, 3, INK)
    text_c(512, 108, "SATURDAY - 21 NOVEMBER 2026", 3, INK)
    rect(24, 136, 976, 2, INK)

    # lead: Russia's biggest November bombardment; missiles in Poland
    frame(24, 148, 976, 256, INK, 2)
    rect(26, 150, 972, 252, PANEL)
    text(44, 162, "WAR IN EUROPE - UKRAINE AND POLAND", 2, RED)
    text(44, 186, "MISSILES LAND IN POLAND", 5, INK)
    text(44, 232, "AS RUSSIA POUNDS UKRAINE", 5, INK)
    draw_lead_banner(44, 274, 936, 44)
    para(44, 328, "404 DRONES AND 111 MISSILES: THE BIGGEST "
                  "BOMBARDMENT OF NOVEMBER. AT LEAST 8 KILLED ACROSS "
                  "UKRAINE; KYIV BRIDGES AND POWER HIT. TUSK CALLS "
                  "THE POLAND LANDINGS AN INTENTIONAL PROVOCATION. "
                  "RUTTE: A GRAVE VIOLATION.", 2, INK, 936, 17)

    # row A: markets / climate
    story_panel(24, 412, 472, 208, "MARKETS - NEW YORK",
                ("AI SELL-OFF", "TIPS WALL ST", "INTO CORRECTION"),
                "THE S&P 500 AND THE DOW SLIDE INTO CORRECTION AS "
                "AI AND CHIP STOCKS PLUNGE. STOCKS FALL 3.7% IN THE "
                "WORST WEEK IN OVER 18 MONTHS.",
                lambda ax, ay: draw_chart(ax, ay, 148, 84))
    story_panel(528, 412, 472, 208, "CLIMATE - ANTALYA",
                ("COP31 TALKS RUN", "PAST DEADLINE", "ON FOSSIL FUELS"),
                "NEARLY 200 NATIONS MISS THE DEADLINE WITH NO DEAL "
                "ON FOSSIL FUELS, AND THE TALKS IN ANTALYA RUN "
                "INTO OVERTIME.",
                lambda ax, ay: draw_globe(ax, ay, 148, 84))

    # row B: Europe / health
    story_panel(24, 628, 472, 196, "EUROPE - BRUSSELS",
                ("UK AND EU SIGN", "BIGGEST POST-", "BREXIT DEAL"),
                "BURNHAM AND EU LEADERS SIGN THREE AGREEMENTS: "
                "FOOD EXPORTS, CARBON MARKETS AND YOUTH MOBILITY.",
                lambda ax, ay: draw_flags(ax, ay + 16))
    story_panel(528, 628, 472, 196, "HEALTH - BARCELONA",
                ("CANCER PILL", "MAKES TUMOURS", "VANISH IN TRIAL"),
                "DARAXONRASIB, TAKEN WITH CHEMO, MADE PANCREATIC "
                "TUMOURS UNDETECTABLE IN 1 IN 12 PATIENTS. THEY "
                "SHRANK OR VANISHED IN 6 IN 10.",
                lambda ax, ay: draw_pill(ax, ay))

    # strip: the Basra power station fire in Iraq
    frame(24, 832, 976, 96, INK, 2)
    rect(26, 834, 972, 92, PANEL)
    text(44, 842, "IRAQ - BASRA", 2, RED)
    text(44, 862, "FIRE AT BASRA POWER STATION KILLS FOUR", 3, INK)
    para(44, 890, "AT LEAST FOUR DEAD AND 30 INJURED IN THE BLAZE "
                  "AT THE HARTHA POWER STATION, NORTH OF BASRA.",
         2, INK, 620, 17)
    draw_flames(790, 838, 180, 84)

    # ticker
    rect(24, 944, 976, 2, INK)
    text_c(512, 956, "MONGOLIA'S PRESIDENT RESIGNS - EU APPROVES "
                     "1BN EUROS DEFENCE AID FOR UKRAINE", 2, INK)
    text_c(512, 974, "IRAN SAYS IT DOWNED A US MQ-9 DRONE OVER "
                     "HORMUZ - HARDEN SCORES 51 FOR THE CAVS", 2, INK)
    rect(24, 998, 976, 2, INK)


# -------------------------------------------------------------- png write

def png_bytes():
    raw = bytearray()
    rowlen = W * 3
    for y in range(H):
        raw.append(0)
        raw += _buf[y * rowlen:(y + 1) * rowlen]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(png_bytes())


if __name__ == "__main__":
    main()
