#!/usr/bin/env python3
import json, math, base64, os

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
LOGOS = os.path.join(ROOT, "logos")

with open(os.path.join(BUILD, "data.json")) as f:
    DATA = json.load(f)
with open(os.path.join(BUILD, "tools-lookup.json")) as f:
    LOOKUP = json.load(f)
with open(os.path.join(BUILD, "logo-sizes.json")) as f:
    LOGO_SIZES = json.load(f)

with open(os.path.join(BUILD, "cc-by-badge.png"), "rb") as f:
    CC_BADGE_URI = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")
with open(os.path.join(BUILD, "transparent-logos.json")) as f:
    TRANSPARENT_LOGOS = set(json.load(f))
with open(os.path.join(BUILD, "logo-frame-colors.json")) as f:
    LOGO_FRAME_COLORS = json.load(f)

LEVEL_ORDER = ["avance", "plus_loin", "decouvrir"]  # inner -> outer

LEVEL_LABELS = {
    "fr": {"avance": ["Usage avancé", "(bonus)"], "plus_loin": ["Pour aller plus loin"], "decouvrir": ["Pour découvrir"]},
    "en": {"avance": ["Advanced use", "(bonus)"], "plus_loin": ["Going further"], "decouvrir": ["Getting started"]},
}
AXIS_LABEL = {"fr": "THÉMATIQUES", "en": "CATEGORIES"}

# category base colors, extracted from the official PDF export (v6 - 0826), per ring level
CAT_COLORS = {
    "Éducation":               {"avance": "#dfb10b", "plus_loin": "#c1990b", "decouvrir": "#a58309"},
    "Chatbots":                {"avance": "#dfa1ab", "plus_loin": "#c18b93", "decouvrir": "#a5777d"},
    "Analyse de documents":    {"avance": "#dbcd9f", "plus_loin": "#bfb189", "decouvrir": "#a39775"},
    "Présentation":            {"avance": "#a3abdb", "plus_loin": "#8d93bd", "decouvrir": "#797fa3"},
    "Quiz et flashcards":      {"avance": "#dba3a9", "plus_loin": "#bd8d91", "decouvrir": "#a3797d"},
    "Musique":                 {"avance": "#ddcda3", "plus_loin": "#bdb18d", "decouvrir": "#a39779"},
    "Voix":                    {"avance": "#df09cd", "plus_loin": "#c109b1", "decouvrir": "#a50797"},
    "Recherche":               {"avance": "#55d970", "plus_loin": "#49bd61", "decouvrir": "#3fa153"},
    "Image et vidéo":          {"avance": "#87d397", "plus_loin": "#73b581", "decouvrir": "#61996d"},
    "Applications et agents":  {"avance": "#03afd1", "plus_loin": "#0397b5", "decouvrir": "#037f99"},
}

CX, CY = 500, 500
RMAX = 480
R0 = RMAX * 0.235   # empty hole
R1 = RMAX * 0.425   # avance / plus_loin boundary
R2 = RMAX * 0.615   # plus_loin / decouvrir boundary
R3 = RMAX * 0.80    # decouvrir outer / label band start
R4 = RMAX * 1.0     # outer bounding circle / label band end

RING_BOUNDS = {"avance": (R0, R1), "plus_loin": (R1, R2), "decouvrir": (R2, R3)}

GAP_START, GAP_END = 150, 210  # blank sector reserved for the axis legend, centered on west (180deg)
SECTOR_W = 30
CAT_START = 210  # first category (Éducation) begins here, sectors run clockwise through the gap boundary


def polar(cx, cy, r, deg):
    rad = math.radians(deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def wrap_label(text):
    words = text.split(" ")
    if len(words) < 2 or len(text) <= 10:
        return [text]
    mid = len(words) / 2
    best_i, best_diff = 1, None
    for i in range(1, len(words)):
        a = " ".join(words[:i])
        b = " ".join(words[i:])
        diff = abs(len(a) - len(b))
        if best_diff is None or diff < best_diff:
            best_diff, best_i = diff, i
    return [" ".join(words[:best_i]), " ".join(words[best_i:])]


def single_line_font(text, available_px, factor=0.58, safety=0.85, min_font=10, max_font=30):
    # `available_px` here is the TANGENTIAL room (the chord width at this radius within the
    # 60deg gap) — at gap_mid, rotated text's length runs tangentially, not radially, so that's
    # the real constraint on fitting the whole word/phrase on one line without truncating it.
    # Radial thickness only bounds the font's cap-height, which a normal font size never
    # threatens given how thick these rings are, so it isn't checked here.
    f = (available_px * safety) / (len(text) * factor)
    return max(min_font, min(f, max_font))


def label_rotation(mid_angle):
    raw = (mid_angle + 90) % 360
    if 90 <= raw <= 270:
        raw = (raw + 180) % 360
    return raw


def img_data_uri(slug):
    path = os.path.join(LOGOS, f"{slug}.png")
    with open(path, "rb") as f:
        b = f.read()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def build_svg(lang, id_prefix="m"):
    cats = DATA["categories"]
    defs = []
    parts = []

    # white disc behind the whole wheel — the circle itself is always white, regardless of the
    # page theme around it; only the square corners outside r=R4 show the page background
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{R4}" fill="#ffffff"/>')

    # sector wedges, colored per category/level
    for i, cat in enumerate(cats):
        a0 = (CAT_START + i * SECTOR_W) % 360
        a1 = a0 + SECTOR_W
        colors = CAT_COLORS[cat["fr"]]
        for level in LEVEL_ORDER:
            r_in, r_out = RING_BOUNDS[level]
            large = 0
            x0o, y0o = polar(CX, CY, r_out, a0)
            x1o, y1o = polar(CX, CY, r_out, a1)
            x1i, y1i = polar(CX, CY, r_in, a1)
            x0i, y0i = polar(CX, CY, r_in, a0)
            d = (f"M {x0o:.2f} {y0o:.2f} A {r_out} {r_out} 0 {large} 1 {x1o:.2f} {y1o:.2f} "
                 f"L {x1i:.2f} {y1i:.2f} A {r_in} {r_in} 0 {large} 0 {x0i:.2f} {y0i:.2f} Z")
            parts.append(f'<path d="{d}" fill="{colors[level]}"/>')

    # center hole (white)
    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{R0}" fill="#ffffff"/>')

    # ring circles (black, full circles including through the gap)
    for r in (R0, R1, R2, R3, R4):
        w_ = 2.6 if r in (R0, R4) else 1.3
        parts.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="#111111" stroke-width="{w_}"/>')

    # radial divider lines: 10 category boundaries + the 2 gap boundaries (150/210 already included)
    boundary_angles = [(CAT_START + i * SECTOR_W) % 360 for i in range(len(cats) + 1)]
    for a in boundary_angles:
        x0, y0 = polar(CX, CY, R0, a)
        x1, y1 = polar(CX, CY, R4, a)
        parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="#111111" stroke-width="1.6"/>')

    # chips (logos) — no background box; native aspect ratio, capped to fit its ring slot without
    # ever touching the sector dividers, the ring circles, or a neighbouring logo
    MARGIN = 0.78
    GAP_PX = 8  # fixed extra clearance on top of the margin, in viewBox units
    clip_counter = [0]
    for i, cat in enumerate(cats):
        a0 = (CAT_START + i * SECTOR_W) % 360
        for level in LEVEL_ORDER:
            r_in, r_out = RING_BOUNDS[level]
            r_mid = (r_in + r_out) / 2
            ring_h = (r_out - r_in) * MARGIN - GAP_PX
            slugs = cat["levels"][level]
            k = len(slugs)
            sub = SECTOR_W / k
            for j, slug in enumerate(slugs):
                a_mid = a0 + sub * (j + 0.5)
                x, y = polar(CX, CY, r_mid, a_mid)
                nat_w, nat_h = LOGO_SIZES[slug]
                # first pass: height-limited scale, to estimate how far inward this image's
                # bottom edge would reach — the wedge is narrowest there, so that's the radius
                # we must use for the width constraint (a plain rectangle's width is constant,
                # so sizing it to fit at its widest point would let the corners poke past the
                # sector boundary near the inner edge)
                scale_h = ring_h / nat_h
                r_inner_est = max(r_mid - (nat_h * scale_h) / 2, r_in + 1)
                slot_w = 2 * r_inner_est * math.sin(math.radians(sub) / 2) * MARGIN - GAP_PX
                scale = min(slot_w / nat_w, scale_h, 4.0)
                dw, dh = nat_w * scale, nat_h * scale
                uri = img_data_uri(slug)
                info = LOOKUP[slug]
                pad = 3
                frame_color = LOGO_FRAME_COLORS.get(slug, "#ffffff")
                rx = min(dw, dh) * 0.14
                clip_id = f"{id_prefix}clip{clip_counter[0]}"
                clip_counter[0] += 1
                defs.append(
                    f'<clipPath id="{clip_id}"><rect x="{-dw/2:.2f}" y="{-dh/2:.2f}" '
                    f'width="{dw:.2f}" height="{dh:.2f}" rx="{rx:.2f}"/></clipPath>'
                )
                parts.append(
                    f'<a href="{info["url"]}" target="_blank" rel="noopener">'
                    f'<g transform="translate({x:.2f},{y:.2f})">'
                    f'<title>{info["name"]}</title>'
                    f'<rect x="{-dw/2-pad:.2f}" y="{-dh/2-pad:.2f}" width="{dw+2*pad:.2f}" '
                    f'height="{dh+2*pad:.2f}" rx="{rx+pad*0.6:.2f}" fill="{frame_color}"/>'
                    f'<image href="{uri}" x="{-dw/2:.2f}" y="{-dh/2:.2f}" width="{dw:.2f}" height="{dh:.2f}" '
                    f'preserveAspectRatio="xMidYMid meet" clip-path="url(#{clip_id})"/>'
                    f'</g></a>'
                )

    # category labels: one rigid text block per category, rotated tangent to the circle and
    # flipped on the lower hemisphere so it never reads upside down (matches the original wheel)
    label_r = (R3 + R4) / 2
    for i, cat in enumerate(cats):
        a0 = (CAT_START + i * SECTOR_W) % 360
        mid = a0 + SECTOR_W / 2
        x, y = polar(CX, CY, label_r, mid)
        rot = label_rotation(mid)
        lines = wrap_label(cat[lang].upper())
        n = len(lines)
        tspans = "".join(
            f'<tspan x="{x:.2f}" y="{y + (li - (n-1)/2) * 19:.2f}">{line}</tspan>' for li, line in enumerate(lines)
        )
        parts.append(
            f'<text transform="rotate({rot:.2f} {x:.2f} {y:.2f})" text-anchor="middle" '
            f'dominant-baseline="central" font-family="Montserrat,sans-serif" font-weight="800" '
            f'font-size="18" fill="#111111" letter-spacing="0.3">{tspans}</text>'
        )

    # axis legend inside the gap: THEMATIQUES sits centered in the same band as the category
    # names (so it visually lines up with them), and the 3 level labels are each centered in
    # their own ring band — every one of these is a single, complete, un-truncated line, sized
    # to whatever font fits its own band, all rotated to read bottom-to-top like the original
    gap_mid = (GAP_START + GAP_END) / 2

    axis_r = (R3 + R4) / 2
    axis_text = AXIS_LABEL[lang]
    chord = 2 * axis_r * math.sin(math.radians((GAP_END - GAP_START) / 2))
    axis_font = single_line_font(axis_text, chord, max_font=30)
    x, y = polar(CX, CY, axis_r, gap_mid)
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" transform="rotate(-90 {x:.2f} {y:.2f})" '
        f'dominant-baseline="central" text-anchor="middle" font-family="Montserrat,sans-serif" '
        f'font-weight="800" font-size="{axis_font:.1f}" letter-spacing="0.5" fill="#111111">{axis_text}</text>'
    )

    labels = LEVEL_LABELS[lang]
    half_gap = math.radians((GAP_END - GAP_START) / 2)
    level_fonts = []
    for level in LEVEL_ORDER:
        r_in, r_out = RING_BOUNDS[level]
        r_mid = (r_in + r_out) / 2
        chord = 2 * r_mid * math.sin(half_gap)
        longest = max(labels[level], key=len)
        level_fonts.append(single_line_font(longest, chord, max_font=24))
    level_font = min(level_fonts)  # same size for all three, per the tightest one

    for level in LEVEL_ORDER:
        r_in, r_out = RING_BOUNDS[level]
        r_mid = (r_in + r_out) / 2
        lines = labels[level]
        n = len(lines)
        line_h = level_font * 1.15
        x, y = polar(CX, CY, r_mid, gap_mid)
        tspans = "".join(
            f'<tspan x="{x:.2f}" y="{y + (li - (n-1)/2) * line_h:.2f}">{line}</tspan>'
            for li, line in enumerate(lines)
        )
        parts.append(
            f'<text transform="rotate(-90 {x:.2f} {y:.2f})" '
            f'dominant-baseline="central" text-anchor="middle" font-family="Montserrat,sans-serif" '
            f'font-weight="700" font-size="{level_font:.1f}" fill="#111111">{tspans}</text>'
        )

    # center content
    if lang == "fr":
        center_lines = ["Sélection subjective", "de 60 applications", "d'IA génératives", "gratuits ou freemium"]
        site_line = "uneIAparjour.fr"
        tag_line = "#uneIAparjour"
        version_line = "(V6) · août 2026"
    else:
        center_lines = ["A subjective selection", "of 60 free or freemium", "generative AI apps"]
        site_line = "uneIAparjour.fr"
        tag_line = "#uneIAparjour"
        version_line = "(V6) · August 2026"

    ty = CY - 64
    center_text_parts = []
    for line in center_lines:
        center_text_parts.append(f'<tspan x="{CX}" y="{ty:.2f}">{line}</tspan>')
        ty += 17
    parts.append(
        f'<text text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" font-size="14.5" '
        f'fill="#222222">{"".join(center_text_parts)}</text>'
    )
    ty += 9
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="800" '
        f'font-size="16" fill="#E67E22" text-decoration="underline">{site_line}</text>'
    )
    ty += 19
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" '
        f'font-size="13.5" fill="#555555">{tag_line}</text>'
    )
    ty += 24
    badge_w, badge_h = 46, 46 * (57 / 162)
    parts.append(
        f'<image href="{CC_BADGE_URI}" x="{CX-badge_w/2:.2f}" y="{ty-badge_h+4:.2f}" '
        f'width="{badge_w:.2f}" height="{badge_h:.2f}" preserveAspectRatio="xMidYMid meet"/>'
    )
    ty += 19
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" '
        f'font-size="11" fill="#999999">{version_line}</text>'
    )

    svg = (
        f'<svg viewBox="-8 -8 1016 1016" xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" font-family="Montserrat,sans-serif">'
        f'<defs>{"".join(defs)}</defs>'
        + "".join(parts) +
        "</svg>"
    )
    return svg


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang_attr}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#383838;--dark:#2e2e2e;--border:#505050;--orange:#E67E22;--amber:#F39C12;--muted:#aaa;--font:'Montserrat',sans-serif}}
body{{font-family:var(--font);background:#252525;display:flex;justify-content:center;align-items:flex-start;padding:24px;min-height:100vh}}
.wrap{{width:100%;max-width:880px;background:var(--bg);color:#fff;border-radius:10px;overflow:hidden;box-shadow:0 12px 48px rgba(0,0,0,.5);position:relative}}
.wrap::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--orange),var(--amber) 50%,var(--orange));z-index:2}}
.head{{padding:18px 28px 14px;text-align:center;background:var(--dark);border-bottom:1px solid var(--border)}}
.head h1{{font-size:18px;font-weight:800;color:#fff}}
.head h1 em{{font-style:normal;color:var(--orange)}}
.head p{{font-size:11px;color:var(--muted);margin-top:2px}}
.wheel-box{{padding:24px;display:flex;flex-direction:column;gap:14px}}
.wheel-card{{background:transparent}}
svg{{width:100%;height:auto;display:block}}
svg a:hover rect{{stroke:var(--orange);stroke-width:2}}
.toolbar{{display:flex;justify-content:flex-end}}
.print-btn{{display:flex;align-items:center;gap:7px;background:rgba(0,0,0,.25);border:1px solid var(--border);color:#fff;font-family:var(--font);font-size:11.5px;font-weight:700;padding:9px 14px;border-radius:7px;cursor:pointer}}
.print-btn:hover{{border-color:var(--orange);color:var(--orange)}}
.print-btn svg{{width:13px;height:13px;fill:currentColor}}
.foot{{text-align:center;padding:14px 20px 18px;font-size:10px;color:var(--muted);background:var(--dark);border-top:1px solid var(--border)}}
.foot a{{color:var(--orange);text-decoration:none;font-weight:600}}
@media print{{
  body{{background:#fff;padding:0;display:block}}
  .wrap{{box-shadow:none;max-width:none;background:#fff;color:#000}}
  .head,.foot{{background:#fff;color:#000;border-color:#ccc}}
  .head h1{{color:#000}}
  .toolbar{{display:none!important}}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h1>Une <em>IA</em> par jour : {heading_lower}</h1>
    <p>{subheading}</p>
  </div>
  <div class="wheel-box">
    <div class="wheel-card">
      {svg}
    </div>
    <div class="toolbar">
      <button class="print-btn" id="printBtn" type="button">
        <svg viewBox="0 0 24 24"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
        {print_label}
      </button>
    </div>
  </div>
  <div class="foot">{footer}</div>
</div>
<script>
document.getElementById('printBtn').onclick = function(){{ window.print(); }};
</script>
</body>
</html>
"""

FOOTERS = {
    "fr": 'uneiaparjour.fr · CC BY 4.0 · <a href="https://www.uneiaparjour.fr/selection/" target="_blank" rel="noopener">page complète</a>',
    "en": 'uneiaparjour.fr · CC BY 4.0 · <a href="https://www.uneiaparjour.fr/en/selection/" target="_blank" rel="noopener">full page</a>',
}
HEADINGS = {"fr": "Sélection d'applications", "en": "Apps selection"}
SUBHEADINGS = {
    "fr": "60 applications d'IA génératives · 10 catégories · 3 niveaux d'appropriation",
    "en": "60 generative AI apps · 10 categories · 3 skill levels",
}
UI_LABELS = {
    "fr": {"print": "Télécharger en PDF"},
    "en": {"print": "Download as PDF"},
}


def build_page(lang):
    svg = build_svg(lang)
    heading = HEADINGS[lang]
    labels = UI_LABELS[lang]
    html = PAGE_TEMPLATE.format(
        lang_attr=lang,
        title=heading,
        heading_lower=heading[0].lower() + heading[1:],
        subheading=SUBHEADINGS[lang],
        svg=svg,
        footer=FOOTERS[lang],
        print_label=labels["print"],
    )
    return html


if __name__ == "__main__":
    for lang, fname in [("fr", "selection-outils.html"), ("en", "selection-outils-en.html")]:
        html = build_page(lang)
        out_path = os.path.join(ROOT, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", out_path, len(html), "bytes")
