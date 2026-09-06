#!/usr/bin/env python3
"""Standalone builder for v1 (juillet 2024) — the only version whose original Canva design is
genuinely different from the shared model in generate.py, not just a different tool list:
7 categories instead of 10 (no "Applications et agents"; "Voix" and "Musique" were still one
category; "Chatbots" was "Texte et Chatbot"), a cream background instead of white, muted pastel
category colors with gray (not white) legend rings, and a rounded display font for everything
except the category names. Reproducing it faithfully therefore needs its own layout code rather
than a new entry in generate.py's shared CAT_COLORS / CAT_START geometry, which is built around
10 equal 30deg sectors.

Note: the original v1 design placed logos directly on the wedge color with no frame or rounded
corners at all (confirmed against the PDF — e.g. "decktopus" renders low-contrast white-on-peach
with square corners). The rounded-corner + frame-color treatment below was added on top of that
original design, by explicit request, for visual consistency with v2-v6 rather than for fidelity
to v1's own PDF.

All measurements below (colors, ring radii, sector angles) were sampled directly from the
official PDF export, https://www.uneiaparjour.fr/wp-content/uploads/2024/06/selection-outils-uneIAparjour.pdf
"""
import json, math, os

from generate import (
    BUILD, ROOT, CC_BADGE_URI, polar, wrap_label, img_data_uri,
    PAGE_TEMPLATE, FOOTERS, HEADINGS, UI_LABELS,
)

LOGOS = os.path.join(ROOT, "logos", "v1-0724")

with open(os.path.join(BUILD, "data-v1.json")) as f:
    DATA = json.load(f)
with open(os.path.join(BUILD, "tools-lookup-v1.json")) as f:
    LOOKUP = json.load(f)
with open(os.path.join(BUILD, "logo-sizes-v1.json")) as f:
    LOGO_SIZES = json.load(f)
with open(os.path.join(BUILD, "logo-frame-colors-v1.json")) as f:
    LOGO_FRAME_COLORS = json.load(f)
with open(os.path.join(BUILD, "meta-v1.json")) as f:
    META = json.load(f)

LEVEL_ORDER = ["avance", "plus_loin", "decouvrir"]

LEVEL_LABELS = {
    "fr": {"avance": ["Pour une", "utilisation", "avancée"], "plus_loin": ["Pour aller", "plus loin"], "decouvrir": ["Pour découvrir"]},
    "en": {"avance": ["For advanced", "use"], "plus_loin": ["Going further"], "decouvrir": ["Getting started"]},
}
AXIS_LABEL = {"fr": "Thématiques", "en": "Categories"}

# category order = 8 equal 45deg slots sweeping clockwise from East; slot 4 (180-225deg, i.e.
# due-west to north-west) is left empty for the axis legend. Sampled from the PDF: this wheel
# is NOT symmetric around due-west the way the shared model's 60deg gap is.
CATS_ORDER = ["presentation", "quiz", "voix_musique", "image", None, "education", "texte_chatbot", "analyse"]
SLOT_W = 45
SLOT_START = 0

# colors sampled per category/ring directly from the PDF (mode color over a swept arc, to
# average out logos/text crossing the sample points)
CAT_COLORS = {
    "presentation":  {"avance": "#ff8b54", "plus_loin": "#ffb997", "decouvrir": "#fed0ba"},
    "quiz":          {"avance": "#faabca", "plus_loin": "#fcccdf", "decouvrir": "#fcdde9"},
    "voix_musique":  {"avance": "#97ccdd", "plus_loin": "#c0e0ea", "decouvrir": "#d5eaf1"},
    "image":         {"avance": "#e36281", "plus_loin": "#eea0b3", "decouvrir": "#f3c0cc"},
    "education":     {"avance": "#a8a54a", "plus_loin": "#cac891", "decouvrir": "#dbdab6"},
    "texte_chatbot": {"avance": "#ffd000", "plus_loin": "#ffe265", "decouvrir": "#feeb99"},
    "analyse":       {"avance": "#be90e9", "plus_loin": "#d8bcf2", "decouvrir": "#e4d2f5"},
}
LEGEND_COLORS = {"avance": "#818299", "plus_loin": "#b3b3c1", "decouvrir": "#ccccd5"}
CREAM = "#f9f2ed"
LINE_COLOR = "#8f8a86"

CX, CY = 500, 500
RMAX = 480
R0 = RMAX * 0.2205
R1 = RMAX * 0.4909
R2 = RMAX * 0.6636
R3 = RMAX * 0.8384
R4 = RMAX * 1.0

RING_BOUNDS = {"avance": (R0, R1), "plus_loin": (R1, R2), "decouvrir": (R2, R3)}

CAT_FONT = "Montserrat,sans-serif"   # category names (ÉDUCATION etc.) — matches the original's
                                       # tall condensed caps
BODY_FONT = "'Baloo 2',cursive"       # axis legend + center text — matches the original's rounded,
                                       # softer display face


def single_line_font(text, available_px, factor=0.58, safety=0.85, min_font=10, max_font=30):
    f = (available_px * safety) / (len(text) * factor)
    return max(min_font, min(f, max_font))


def label_rotation(mid_angle):
    raw = (mid_angle + 90) % 360
    if 90 <= raw <= 270:
        raw = (raw + 180) % 360
    return raw


def build_svg(lang, id_prefix="v1"):
    cats_by_key = {c_key: cat for c_key, cat in zip(
        ["presentation", "quiz", "voix_musique", "image", "education", "texte_chatbot", "analyse"],
        DATA["categories"])}
    defs = []
    parts = []

    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{R4}" fill="{CREAM}"/>')

    for i, cat_key in enumerate(CATS_ORDER):
        if cat_key is None:
            continue
        a0 = SLOT_START + i * SLOT_W
        a1 = a0 + SLOT_W
        colors = CAT_COLORS[cat_key]
        for level in LEVEL_ORDER:
            r_in, r_out = RING_BOUNDS[level]
            x0o, y0o = polar(CX, CY, r_out, a0)
            x1o, y1o = polar(CX, CY, r_out, a1)
            x1i, y1i = polar(CX, CY, r_in, a1)
            x0i, y0i = polar(CX, CY, r_in, a0)
            d = (f"M {x0o:.2f} {y0o:.2f} A {r_out} {r_out} 0 0 1 {x1o:.2f} {y1o:.2f} "
                 f"L {x1i:.2f} {y1i:.2f} A {r_in} {r_in} 0 0 0 {x0i:.2f} {y0i:.2f} Z")
            parts.append(f'<path d="{d}" fill="{colors[level]}"/>')

    # legend slot (index 4) — gray rings
    gap_i = CATS_ORDER.index(None)
    ga0 = SLOT_START + gap_i * SLOT_W
    ga1 = ga0 + SLOT_W
    for level in LEVEL_ORDER:
        r_in, r_out = RING_BOUNDS[level]
        x0o, y0o = polar(CX, CY, r_out, ga0)
        x1o, y1o = polar(CX, CY, r_out, ga1)
        x1i, y1i = polar(CX, CY, r_in, ga1)
        x0i, y0i = polar(CX, CY, r_in, ga0)
        d = (f"M {x0o:.2f} {y0o:.2f} A {r_out} {r_out} 0 0 1 {x1o:.2f} {y1o:.2f} "
             f"L {x1i:.2f} {y1i:.2f} A {r_in} {r_in} 0 0 0 {x0i:.2f} {y0i:.2f} Z")
        parts.append(f'<path d="{d}" fill="{LEGEND_COLORS[level]}"/>')

    parts.append(f'<circle cx="{CX}" cy="{CY}" r="{R0}" fill="{CREAM}"/>')

    for r in (R0, R1, R2, R3, R4):
        w_ = 2.2 if r in (R0, R4) else 1.1
        parts.append(f'<circle cx="{CX}" cy="{CY}" r="{r}" fill="none" stroke="{LINE_COLOR}" stroke-width="{w_}"/>')

    boundary_angles = [SLOT_START + i * SLOT_W for i in range(len(CATS_ORDER) + 1)]
    for a in boundary_angles:
        x0, y0 = polar(CX, CY, R0, a)
        x1, y1 = polar(CX, CY, R4, a)
        parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{LINE_COLOR}" stroke-width="1.3"/>')

    # logos — rounded-corner clip + frame-color background rect, matching v2-v6 for visual
    # consistency across the archive (the original v1 PDF actually placed these bare, see the
    # module docstring)
    MARGIN = 0.78
    GAP_PX = 8
    clip_counter = [0]
    for i, cat_key in enumerate(CATS_ORDER):
        if cat_key is None:
            continue
        a0 = SLOT_START + i * SLOT_W
        cat = cats_by_key[cat_key]
        for level in LEVEL_ORDER:
            r_in, r_out = RING_BOUNDS[level]
            r_mid = (r_in + r_out) / 2
            ring_h = (r_out - r_in) * MARGIN - GAP_PX
            slugs = cat["levels"][level]
            k = len(slugs)
            sub = SLOT_W / k
            for j, slug in enumerate(slugs):
                a_mid = a0 + sub * (j + 0.5)
                x, y = polar(CX, CY, r_mid, a_mid)
                nat_w, nat_h = LOGO_SIZES[slug]
                scale_h = ring_h / nat_h
                r_inner_est = max(r_mid - (nat_h * scale_h) / 2, r_in + 1)
                slot_w = 2 * r_inner_est * math.sin(math.radians(sub) / 2) * MARGIN - GAP_PX
                scale = min(slot_w / nat_w, scale_h, 4.0)
                dw, dh = nat_w * scale, nat_h * scale
                uri = img_data_uri(LOGOS, slug)
                info = LOOKUP[slug]
                pad = 3
                frame_color = LOGO_FRAME_COLORS.get(slug, "#ffffff")
                rx = min(dw, dh) * 0.14
                clip_id = f"v1clip{clip_counter[0]}"
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

    # category labels
    label_r = (R3 + R4) / 2
    for i, cat_key in enumerate(CATS_ORDER):
        if cat_key is None:
            continue
        a0 = SLOT_START + i * SLOT_W
        mid = a0 + SLOT_W / 2
        x, y = polar(CX, CY, label_r, mid)
        rot = label_rotation(mid)
        lines = wrap_label(cats_by_key[cat_key][lang].upper())
        n = len(lines)
        tspans = "".join(
            f'<tspan x="{x:.2f}" y="{y + (li - (n-1)/2) * 17:.2f}">{line}</tspan>' for li, line in enumerate(lines)
        )
        parts.append(
            f'<text transform="rotate({rot:.2f} {x:.2f} {y:.2f})" text-anchor="middle" '
            f'dominant-baseline="central" font-family="{CAT_FONT}" font-weight="800" '
            f'font-size="16.5" fill="#111111" letter-spacing="0.3">{tspans}</text>'
        )

    # axis legend, centered in the gap slot. The shared model can hardcode rotate(-90) because
    # its gap is centered exactly on due-west (180deg), where the tangent is purely vertical;
    # here the gap is centered on 202.5deg (45deg-wide slots don't straddle west symmetrically),
    # so the tangent-aligned rotation has to be derived from that angle instead, the same way
    # label_rotation() does for category names — otherwise the text reads ~22.5deg off-tangent
    # and visibly leans into the neighbouring category wedge.
    gap_mid = (ga0 + ga1) / 2
    legend_rot = (gap_mid + 90) % 360
    axis_r = (R3 + R4) / 2
    axis_text = AXIS_LABEL[lang]
    chord = 2 * axis_r * math.sin(math.radians(SLOT_W / 2))
    axis_font = single_line_font(axis_text, chord, max_font=26)
    x, y = polar(CX, CY, axis_r, gap_mid)
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" transform="rotate({legend_rot:.2f} {x:.2f} {y:.2f})" '
        f'dominant-baseline="central" text-anchor="middle" font-family="{BODY_FONT}" '
        f'font-weight="800" font-size="{axis_font:.1f}" fill="#111111">{axis_text}</text>'
    )

    labels = LEVEL_LABELS[lang]
    half_gap = math.radians(SLOT_W / 2)
    level_fonts = []
    for level in LEVEL_ORDER:
        r_in, r_out = RING_BOUNDS[level]
        r_mid = (r_in + r_out) / 2
        chord = 2 * r_mid * math.sin(half_gap)
        longest = max(labels[level], key=len)
        level_fonts.append(single_line_font(longest, chord, max_font=20))
    level_font = min(level_fonts)

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
            f'<text transform="rotate({legend_rot:.2f} {x:.2f} {y:.2f})" '
            f'dominant-baseline="central" text-anchor="middle" font-family="{BODY_FONT}" '
            f'font-weight="700" font-size="{level_font:.1f}" fill="#111111">{tspans}</text>'
        )

    # center content — v1's own wording ("outils", no version/date tag: the original had neither)
    n_tools = sum(len(l) for c in DATA["categories"] for l in c["levels"].values())
    if lang == "fr":
        center_lines = ["Sélection subjective", f"de {n_tools} outils", "d'IA génératives", "gratuits ou freemium"]
        site_line, tag_line = "uneIAparjour.fr", "#uneIAparjour"
    else:
        center_lines = ["A subjective selection", f"of {n_tools} free or freemium", "generative AI tools"]
        site_line, tag_line = "uneIAparjour.fr", "#uneIAparjour"

    ty = CY - 58
    center_text_parts = []
    for line in center_lines:
        center_text_parts.append(f'<tspan x="{CX}" y="{ty:.2f}">{line}</tspan>')
        ty += 22
    parts.append(
        f'<text text-anchor="middle" font-family="{BODY_FONT}" font-weight="400" font-size="16.5" '
        f'fill="#222222">{"".join(center_text_parts)}</text>'
    )
    ty += 6
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="{BODY_FONT}" font-weight="700" '
        f'font-size="17" fill="#222222" text-decoration="underline">{site_line}</text>'
    )
    ty += 22
    parts.append(
        f'<text x="{CX}" y="{ty:.2f}" text-anchor="middle" font-family="{BODY_FONT}" font-weight="400" '
        f'font-size="15" fill="#222222" text-decoration="underline">{tag_line}</text>'
    )
    ty += 20
    badge_w, badge_h = 46, 46 * (57 / 162)
    parts.append(
        f'<image href="{CC_BADGE_URI}" x="{CX-badge_w/2:.2f}" y="{ty-badge_h+4:.2f}" '
        f'width="{badge_w:.2f}" height="{badge_h:.2f}" preserveAspectRatio="xMidYMid meet"/>'
    )

    svg = (
        f'<svg viewBox="-8 -8 1016 1016" xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" font-family="{BODY_FONT}">'
        f'<defs>{"".join(defs)}</defs>'
        + "".join(parts) +
        "</svg>"
    )
    return svg


SUBHEADING_V1 = {
    "fr": "{n} outils d'IA génératives · 7 catégories · 3 niveaux d'appropriation",
    "en": "{n} generative AI tools · 7 categories · 3 skill levels",
}


def build_page(lang):
    svg = build_svg(lang)
    heading = HEADINGS[lang]
    labels = UI_LABELS[lang]
    n_tools = sum(len(l) for c in DATA["categories"] for l in c["levels"].values())
    html = PAGE_TEMPLATE.format(
        lang_attr=lang,
        title=heading,
        heading_lower=heading[0].lower() + heading[1:],
        subheading=SUBHEADING_V1[lang].format(n=n_tools),
        svg=svg,
        footer=FOOTERS[lang],
        print_label=labels["print"],
    )
    # v1's own page needs the rounded display font loaded too
    html = html.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&family=Baloo+2:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
    )
    return html


def build_version(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for lang, fname in [("fr", "selection-outils.html"), ("en", "selection-outils-en.html")]:
        html = build_page(lang)
        out_path = os.path.join(out_dir, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("wrote", out_path, len(html), "bytes")


if __name__ == "__main__":
    build_version(os.path.join(ROOT, "versions", "v1-0724"))
