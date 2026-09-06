#!/usr/bin/env python3
import json, math, base64, os

BUILD = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BUILD)
LOGOS = os.path.join(ROOT, "logos")

with open(os.path.join(BUILD, "data.json")) as f:
    DATA = json.load(f)
with open(os.path.join(BUILD, "tools-lookup.json")) as f:
    LOOKUP = json.load(f)

LEVEL_ORDER = ["avance", "plus_loin", "decouvrir"]  # inner -> outer

LEVEL_LABELS = {
    "fr": {"avance": "Utilisation avancée (bonus)", "plus_loin": "Pour aller plus loin", "decouvrir": "Pour découvrir"},
    "en": {"avance": "Advanced use (bonus)", "plus_loin": "Going further", "decouvrir": "Getting started"},
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


def img_data_uri(slug):
    path = os.path.join(LOGOS, f"{slug}.png")
    with open(path, "rb") as f:
        b = f.read()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


def build_svg(lang):
    cats = DATA["categories"]
    defs = []
    parts = []

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

    # chips (logos)
    CHIP_W, CHIP_H = 58, 38
    for i, cat in enumerate(cats):
        a0 = (CAT_START + i * SECTOR_W) % 360
        for level in LEVEL_ORDER:
            r_in, r_out = RING_BOUNDS[level]
            r_mid = (r_in + r_out) / 2
            slugs = cat["levels"][level]
            k = len(slugs)
            sub = SECTOR_W / k
            for j, slug in enumerate(slugs):
                a_mid = a0 + sub * (j + 0.5)
                x, y = polar(CX, CY, r_mid, a_mid)
                uri = img_data_uri(slug)
                info = LOOKUP[slug]
                parts.append(
                    f'<a href="{info["url"]}" target="_blank" rel="noopener">'
                    f'<g transform="translate({x:.2f},{y:.2f})">'
                    f'<title>{info["name"]}</title>'
                    f'<rect x="{-CHIP_W/2}" y="{-CHIP_H/2}" width="{CHIP_W}" height="{CHIP_H}" rx="6" '
                    f'fill="#ffffff" stroke="#111111" stroke-width="0.8"/>'
                    f'<image href="{uri}" x="{-CHIP_W/2+4}" y="{-CHIP_H/2+4}" width="{CHIP_W-8}" height="{CHIP_H-8}" '
                    f'preserveAspectRatio="xMidYMid meet"/>'
                    f'</g></a>'
                )

    # category labels: curved along an arc in the outer label band (R3..R4)
    label_r = (R3 + R4) / 2
    for i, cat in enumerate(cats):
        a0 = (CAT_START + i * SECTOR_W) % 360
        a1 = a0 + SECTOR_W
        mid = a0 + SECTOR_W / 2
        left_half = math.cos(math.radians(mid)) < 0
        half_span = 48  # wider than one sector so long labels have room; the guide path itself is invisible
        if left_half:
            # reverse sweep so text reads left-to-right upright on the left hemisphere
            sa, ea = mid + half_span, mid - half_span
            sweep = 0
        else:
            sa, ea = mid - half_span, mid + half_span
            sweep = 1
        x0, y0 = polar(CX, CY, label_r, sa)
        x1, y1 = polar(CX, CY, label_r, ea)
        large = 1 if abs(ea - sa) > 180 else 0
        path_id = f"catpath{i}"
        defs.append(f'<path id="{path_id}" d="M {x0:.2f} {y0:.2f} A {label_r} {label_r} 0 {large} {sweep} {x1:.2f} {y1:.2f}" fill="none"/>')
        parts.append(
            f'<text font-family="Montserrat,sans-serif" font-weight="800" font-size="17" fill="#111111" letter-spacing="0.5">'
            f'<textPath href="#{path_id}" startOffset="50%" text-anchor="middle">{cat[lang].upper()}</textPath></text>'
        )

    # axis legend inside the gap: THEMATIQUES (outer band) + 3 level labels (each ring band), all rotated to read bottom-to-top
    gap_mid = (GAP_START + GAP_END) / 2
    axis_r = (R3 + R4) / 2
    x, y = polar(CX, CY, axis_r, gap_mid)
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" transform="rotate(-90 {x:.2f} {y:.2f})" '
        f'text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="800" font-size="19" '
        f'letter-spacing="1.5" fill="#111111">{AXIS_LABEL[lang]}</text>'
    )
    labels = LEVEL_LABELS[lang]
    for level in LEVEL_ORDER:
        r_in, r_out = RING_BOUNDS[level]
        r_mid = (r_in + r_out) / 2
        x, y = polar(CX, CY, r_mid, gap_mid)
        parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" transform="rotate(-90 {x:.2f} {y:.2f})" '
            f'text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="700" font-size="15" '
            f'fill="#111111">{labels[level]}</text>'
        )

    # center content
    if lang == "fr":
        center_lines = ["Sélection subjective", "de 60 applications", "d'IA génératives", "gratuites ou freemium"]
        site_line = "uneiaparjour.fr"
        tag_line = "#uneIAparjour"
        version_line = "Mise à jour : août 2026"
    else:
        center_lines = ["A subjective selection", "of 60 free or freemium", "generative AI apps"]
        site_line = "uneiaparjour.fr"
        tag_line = "#uneIAparjour"
        version_line = "Updated: August 2026"

    ty = CY - 58
    center_text_parts = []
    for line in center_lines:
        center_text_parts.append(f'<tspan x="{CX}" y="{ty:.2f}">{line}</tspan>')
        ty += 15
    parts.append(
        f'<text text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" font-size="12.5" '
        f'fill="#222222">{"".join(center_text_parts)}</text>'
    )
    ty += 8
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="800" '
        f'font-size="14" fill="#E67E22" text-decoration="underline">{site_line}</text>'
    )
    ty += 17
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="600" '
        f'font-size="12" fill="#555555">{tag_line}</text>'
    )
    ty += 22
    # CC BY badge (simple)
    badge_w = 64
    parts.append(
        f'<g transform="translate({CX-badge_w/2:.2f},{ty-11:.2f})">'
        f'<rect width="{badge_w}" height="16" rx="2" fill="none" stroke="#333" stroke-width="1"/>'
        f'<circle cx="10" cy="8" r="6" fill="none" stroke="#333" stroke-width="1"/>'
        f'<circle cx="26" cy="8" r="6" fill="none" stroke="#333" stroke-width="1"/>'
        f'<text x="46" y="12" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="700" font-size="9" fill="#333">BY</text>'
        f'</g>'
    )
    ty += 18
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="Montserrat,sans-serif" font-weight="500" '
        f'font-size="9.5" fill="#999999">{version_line}</text>'
    )

    svg = (
        f'<svg viewBox="-40 -40 1080 1080" xmlns="http://www.w3.org/2000/svg" '
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
:root{{--orange:#E67E22;--amber:#F39C12;--dark:#2e2e2e;--muted:#888;--font:'Montserrat',sans-serif}}
body{{font-family:var(--font);background:#252525;display:flex;justify-content:center;padding:24px;min-height:100vh}}
.wrap{{width:100%;max-width:880px;background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 12px 48px rgba(0,0,0,.5);position:relative}}
.wrap::before{{content:'';position:absolute;top:0;left:0;right:0;height:4px;background:linear-gradient(90deg,var(--orange),var(--amber) 50%,var(--orange));z-index:2}}
.head{{padding:18px 28px 6px;text-align:center}}
.head h1{{font-size:18px;font-weight:800;color:var(--dark)}}
.head h1 em{{font-style:normal;color:var(--orange)}}
.head p{{font-size:11px;color:var(--muted);margin-top:2px}}
.wheel-box{{padding:8px 16px 16px}}
svg{{width:100%;height:auto;display:block}}
svg a:hover rect{{stroke:var(--orange);stroke-width:2}}
.foot{{text-align:center;padding:0 20px 18px;font-size:10px;color:var(--muted)}}
.foot a{{color:var(--orange);text-decoration:none;font-weight:600}}
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h1>Une <em>IA</em> par jour — {heading}</h1>
    <p>{subheading}</p>
  </div>
  <div class="wheel-box">
    {svg}
  </div>
  <div class="foot">{footer}</div>
</div>
</body>
</html>
"""

FOOTERS = {
    "fr": 'uneiaparjour.fr · CC BY 4.0 · <a href="https://www.uneiaparjour.fr/selection/" target="_blank" rel="noopener">page complète</a>',
    "en": 'uneiaparjour.fr · CC BY 4.0 · <a href="https://www.uneiaparjour.fr/en/selection/" target="_blank" rel="noopener">full page</a>',
}
HEADINGS = {"fr": "Sélection d'outils IA", "en": "AI tools selection"}
SUBHEADINGS = {
    "fr": "60 applications d'IA générative · 10 catégories · 3 niveaux d'appropriation",
    "en": "60 generative AI apps · 10 categories · 3 skill levels",
}


def build_page(lang):
    svg = build_svg(lang)
    html = PAGE_TEMPLATE.format(
        lang_attr=lang,
        title=HEADINGS[lang],
        heading=HEADINGS[lang],
        subheading=SUBHEADINGS[lang],
        svg=svg,
        footer=FOOTERS[lang],
    )
    return html


if __name__ == "__main__":
    for lang, fname in [("fr", "selection-outils.html"), ("en", "selection-outils-en.html")]:
        html = build_page(lang)
        out_path = os.path.join(ROOT, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", out_path, len(html), "bytes")
