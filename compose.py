#!/usr/bin/env python3
"""Compose entry.png: a broadsheet front page summing up Friday 20 November 2026.

The page is typeset with PIL on a flowing vertical cursor: every block is
measured with the real font metrics before it is drawn, headlines wrap to
their column, and the script asserts that the last block still ends above
the footer rule.  The render is fully deterministic -- no clocks, no
randomness, fixed fonts -- so two runs write byte-identical PNG files.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- layout ---
W = H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN            # 944 px of live matter
GUTTER = 28
COL_W = (CONTENT_W - GUTTER) // 2     # 458 px per column
COL2_X = MARGIN + COL_W + GUTTER
FOOTER_RULE_Y = 966

PAPER = (247, 243, 234)               # #F7F3EA
INK = (18, 18, 18)                    # #121212
RED = (168, 12, 28)                   # #A80C1C
GREY = (90, 86, 78)                   # #5A564E
BODY = (38, 36, 33)                   # soft black for text
DIVIDER = (203, 196, 180)             # warm hairline grey
WHITE = (250, 248, 240)

FONT_DIR = "/usr/share/fonts/truetype/"
SERIF_BLACK = "noto/NotoSerifDisplay-Black.ttf"
SERIF_BOLD = "noto/NotoSerif-Bold.ttf"
SANS_XBOLD = "noto/NotoSans-ExtraBold.ttf"
SANS_BLACK = "noto/NotoSans-Black.ttf"
SANS_BOLD = "noto/NotoSans-Bold.ttf"
SERIF = "liberation/LiberationSerif-Regular.ttf"
SERIF_IT = "liberation/LiberationSerif-Italic.ttf"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def tw(draw, text, fnt):
    """Width of a string in a given font, in pixels."""
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap of a single-font string to a measure."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if tw(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, text, fnt, y, fill, tracking=0):
    """Draw a line centred on the page; tracking adds px between letters."""
    if tracking:
        width = sum(tw(draw, ch, fnt) for ch in text) + tracking * (len(text) - 1)
        x = (W - width) / 2
        for ch in text:
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += tw(draw, ch, fnt) + tracking
        return width
    draw.text(((W - tw(draw, text, fnt)) / 2, y), text, font=fnt, fill=fill)
    return tw(draw, text, fnt)


def rule(draw, y, height=2, fill=INK):
    draw.rectangle([MARGIN, y, W - MARGIN, y + height - 1], fill=fill)


# ---------------------------------------------------------------- panels ---
def draw_panel(draw, x, y, kicker, headline, body):
    """One news panel: red kicker, serif headline, serif body. Returns bottom."""
    f_kick = font(SANS_XBOLD, 17)
    f_head = font(SERIF_BOLD, 32)
    f_body = font(SERIF, 19)
    draw.text((x, y), kicker, font=f_kick, fill=RED)
    y += 22
    for line in wrap(draw, headline, f_head, COL_W):
        draw.text((x, y), line, font=f_head, fill=INK)
        y += 35
    y += 5
    for line in wrap(draw, body, f_body, COL_W):
        draw.text((x, y), line, font=f_body, fill=BODY)
        y += 23
    return y


def draw_panel_row(draw, y, left, right):
    """Two panels side by side with a hairline divider. Returns row bottom."""
    bottom_l = draw_panel(draw, MARGIN, y, *left)
    bottom_r = draw_panel(draw, COL2_X, y, *right)
    bottom = max(bottom_l, bottom_r)
    div_x = MARGIN + COL_W + GUTTER // 2
    draw.line([div_x, y + 2, div_x, bottom - 4], fill=DIVIDER, width=1)
    return bottom


# ---------------------------------------------------------------- briefs ---
def draw_brief(draw, x, y, place, text):
    """A brief: red square bullet, bold sans place name, serif text.

    The place name and the text are wrapped as one mixed-font stream so the
    first line flows on from the name and later lines use the full measure.
    Returns the bottom of the brief.
    """
    f_place = font(SANS_BOLD, 16)
    f_text = font(SERIF, 17)
    indent = 22
    max_w = COL_W - indent
    # Token stream: (word, font); the dash belongs to the text run.
    tokens = [(place, f_place), ("—", f_text)]
    tokens += [(word, f_text) for word in text.split()]
    space_w = tw(draw, " ", f_text)

    lines, cur, cur_w = [], [], 0.0
    for word, fnt in tokens:
        w = tw(draw, word, fnt)
        add = w if not cur else w + space_w
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(word, fnt)], w
        else:
            cur.append((word, fnt))
            cur_w += add
    if cur:
        lines.append(cur)

    draw.rectangle([x, y + 5, x + 8, y + 13], fill=RED)
    for line in lines:
        lx = x + indent
        for word, fnt in line:
            draw.text((lx, y), word, font=fnt, fill=INK if fnt is f_place else BODY)
            lx += tw(draw, word, fnt) + space_w
        y += 21
    return y


# ------------------------------------------------------------------ page ---
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = 26

    # 1. Folio strip ------------------------------------------------------
    f_folio = font(SANS_BOLD, 16)
    draw.text((MARGIN, y), "THE DAY'S NEWS · ONE PAGE · ONE IMAGE",
              font=f_folio, fill=GREY)
    right = "EST. 2026 — NO. 20"
    draw.text((W - MARGIN - tw(draw, right, f_folio), y), right,
              font=f_folio, fill=GREY)
    y += 24
    rule(draw, y, 2)
    y += 12

    # 2. Masthead ---------------------------------------------------------
    f_mast = font(SERIF_BLACK, 84)
    mast = "The Daily World"
    bbox = draw.textbbox((0, 0), mast, font=f_mast)
    draw.text(((W - (bbox[2] - bbox[0])) / 2 - bbox[0], y - bbox[1]),
              mast, font=f_mast, fill=INK)
    y += (bbox[3] - bbox[1]) + 7
    rule(draw, y, 5)
    y += 8
    rule(draw, y, 1)
    y += 14

    # 3. Date bar ---------------------------------------------------------
    bar_h = 42
    draw.rectangle([MARGIN, y, W - MARGIN, y + bar_h - 1], fill=INK)
    f_date = font(SANS_BLACK, 29)
    date = "FRIDAY · 20 NOVEMBER 2026"
    tracking = 3
    text_w = sum(tw(draw, ch, f_date) for ch in date) + tracking * (len(date) - 1)
    bbox = draw.textbbox((0, 0), date, font=f_date)
    text_h = bbox[3] - bbox[1]
    tx = (W - text_w) / 2
    ty = y + (bar_h - text_h) / 2 - bbox[1]
    for ch in date:
        draw.text((tx, ty), ch, font=f_date, fill=WHITE)
        tx += tw(draw, ch, f_date) + tracking
    y += bar_h + 13

    # 4. Lead story -------------------------------------------------------
    draw.text((MARGIN, y), "THE HAGUE  ·  INTERNATIONAL COURT OF JUSTICE",
              font=font(SANS_XBOLD, 19), fill=RED)
    y += 26
    banner = ["World Court: Myanmar committed", "genocide against the Rohingya"]
    size = 57
    while size > 30:
        f_banner = font(SERIF_BLACK, size)
        if max(tw(draw, line, f_banner) for line in banner) <= CONTENT_W:
            break
        size -= 1
    for line in banner:
        bbox = draw.textbbox((0, 0), line, font=f_banner)
        draw.text((MARGIN - bbox[0], y - bbox[1]), line, font=f_banner, fill=INK)
        y += (bbox[3] - bbox[1]) + 7
    y += 4
    f_sub = font(SERIF_IT, 23)
    subhead = ("The first genocide verdict against a state in the court's "
               "history, over the 2017 crackdown — Myanmar rejects the judgment.")
    for line in wrap(draw, subhead, f_sub, CONTENT_W):
        draw.text((MARGIN, y), line, font=f_sub, fill=BODY)
        y += 27
    y += 10
    rule(draw, y, 2)
    y += 12

    # 5-6. Panel rows -----------------------------------------------------
    y = draw_panel_row(
        draw, y,
        ("SHENZHEN · FIRST THREE-WAY SUMMIT",
         "Trump, Xi & Putin sign a peace declaration",
         "US, Chinese and Russian leaders meet face to face for the first "
         "time and sign a four-point pact. Europe warns: no deal over our "
         "heads."),
        ("KYIV · WARSAW · THE WAR",
         "Russia pounds Kyiv; a missile hits Poland",
         "400+ drones and 110 missiles in one night; three Kyiv bridges "
         "hit. Ukraine hits the Crimea Bridge a third time; Putin vows a "
         "hard reply."))
    y += 10
    rule(draw, y, 2)
    y += 12

    y = draw_panel_row(
        draw, y,
        ("NEW YORK · MARKETS",
         "AI sell-off deepens as Anthropic lists",
         "S&P 500 −2%, a fifth straight loss; Nikkei −4.8%. Anthropic, "
         "the first pure-AI listing, closed its debut +17% at $97, then "
         "slid. Gold −4.2%."),
        ("RIYADH · MIDDLE EAST",
         "Houthi missiles strike the Riyadh skyline",
         "Missiles damage the sovereign wealth fund tower in the financial "
         "district. Oil tops $92 as Hormuz tanker attacks intensify."))
    y += 10
    rule(draw, y, 2)
    y += 12

    # 7. Briefs -----------------------------------------------------------
    draw.text((MARGIN, y), "ALSO ON FRIDAY", font=font(SANS_BLACK, 19), fill=INK)
    y += 25
    briefs = [
        ("BRUSSELS", "EU–UK summit seals a Brexit “reset” deal."),
        ("NAIROBI", "Last Ebola patient home; outbreak over, 37 days on."),
        ("GAZA", "Israeli troops cross the Gaza ceasefire line."),
        ("ANTALYA", "COP31 draft drops fossil phase-out call."),
        ("LOS ANGELES", "GTA VI launch sales top $2.3 billion."),
    ]
    for row in range(3):
        bottoms = []
        for col, idx in enumerate((row * 2, row * 2 + 1)):
            if idx < len(briefs):
                x = MARGIN if col == 0 else COL2_X
                bottoms.append(draw_brief(draw, x, y, *briefs[idx]))
        y = max(bottoms) + 5

    # 8. Footer -----------------------------------------------------------
    assert y <= FOOTER_RULE_Y - 8, f"content overflows: ends at y={y}"
    rule(draw, FOOTER_RULE_Y, 2)
    draw.text((MARGIN, FOOTER_RULE_Y + 10),
              "Compiled from the day's reporting by Reuters, the BBC and "
              "international news wires.",
              font=font(SERIF_IT, 15), fill=GREY)
    return img


if __name__ == "__main__":
    out = Path(__file__).with_name("entry.png")
    compose().save(out)
    print(f"wrote {out}")
