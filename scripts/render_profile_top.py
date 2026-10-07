#!/usr/bin/env python3
"""BoardUI-style dark dashboard for the profile README (SVG, no JS).

BoardUI (boardui.com) is a React + Tailwind design system — React can't run
inside a GitHub README, so this reimplements its dashboard language in a
self-contained SVG: secondary-surface cards (rounded-2xl), plain KPI stat
cards with gradient icon tiles + delta chips, and an orders-chart-card
style header (label, headline, delta chip, comparison line, legend dots)
with top-rounded bars.

Layout (880 wide, transparent page = dashboard gap look):
  row 1: 4 stat cards (Contribuições, Streak, Melhor dia, Este mês)
  row 2: chart card with the 12 monthly bars
  row 3: heatmap calendar card
Regenerated daily by the workflow, same as before.

Usage:
    python scripts/render_profile_top.py
    STATIC=1 python scripts/render_profile_top.py   # frozen frame (previews)
"""
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import load_config

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"

STATIC = os.environ.get("STATIC") == "1"
THEME = os.environ.get("THEME", "dark")
LIGHT = THEME == "light"
OUT = ROOT / ("profile-top-light.svg" if LIGHT else "profile-top.svg")

W = 880
if LIGHT:  # BoardUI light tokens
    CARD = "#FFFFFF"
    CARD_BORDER = "#E4E4E7"
    FG = "#18181B"
    SEC = "#52525B"
    TER = "#71717A"
    TRACK = "#F4F4F5"
    BAND = "#F4F4F5"
    NEU_BG = "#F4F4F5"
    LIME_BG, LIME_TXT = "#D9F99D", "#3F6212"
    ROSE_BG, ROSE_TXT = "#FECDD3", "#9F1239"
    HEAT = ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"]
    HEAT_TOP = "#216E39"
else:  # BoardUI dark tokens
    CARD = "#131318"
    CARD_BORDER = "rgba(255,255,255,0.08)"
    FG = "#FAFAFA"
    SEC = "#A1A1AA"
    TER = "#71717A"
    TRACK = "#232327"
    BAND = "#1A1A1F"
    NEU_BG = "#232327"
    LIME_BG, LIME_TXT = "#1A2E05", "#84CC16"
    ROSE_BG, ROSE_TXT = "#4C0519", "#F43F5E"
    HEAT = ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]
    HEAT_TOP = "#69F0A0"
ACCENT = "#10B981"      # chart-9-active / emerald
NEUTRAL_BAR = "#3F3F46"
NEU_TXT = SEC

TONES = {
    "emerald": ("#10B981", "#059669"),
    "blue": ("#3B82F6", "#2563EB"),
    "purple": ("#A855F7", "#9333EA"),
    "orange": ("#FB923C", "#F97316"),
    "yellow": ("#EAB308", "#CA8A04"),
    "sky": ("#38BDF8", "#0284C7"),
}

FONT = "Inter,ui-sans-serif,system-ui,-apple-system,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

MESES = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# GitHub linguist colors for common languages
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "HTML": "#E34C26", "CSS": "#563D7C", "Shell": "#89E051",
    "Dockerfile": "#384D54", "Vue": "#41B883", "Go": "#00ADD8",
    "Rust": "#DEA584", "Java": "#B07219", "Ruby": "#701516",
    "PHP": "#4F5D95", "C++": "#F34B7D", "C": "#555555",
    "Jupyter Notebook": "#DA5B0B", "MDX": "#FCB32C", "SCSS": "#C6538C",
    "Less": "#1D365D", "Elixir": "#6E4A7E", "Kotlin": "#A97BFF",
    "Swift": "#F05138", "Dart": "#00B4AB", "R": "#198CE7",
    "Lua": "#000080", "HCL": "#844FBA", "Makefile": "#427819",
}
LANG_DEFAULT = "#8B949E"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def measure(text: str, size: int = 14) -> float:
    """Real text width (system font metrics) + safety margin, so pills
    always keep their BoardUI padding whatever the string is."""
    try:
        from PIL import ImageFont
        font = None
        for path in ("/System/Library/Fonts/HelveticaNeue.ttc",
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            try:
                font = ImageFont.truetype(path, size)
                break
            except OSError:
                continue
        if font is None:
            return len(text) * 7.7
        left, _, right, _ = font.getbbox(text)
        return (right - left) + 2.0
    except Exception:
        return len(text) * 7.7


def chip(x: float, y: float, text: str, kind: str) -> tuple[str, float]:
    """BoardUI Chip (variant=bold) + DeltaPill, exact spec from chip.tsx:
    bold = py-0.5 (2px) + text-body-medium (14/20/500); DeltaPill adds
    rounded-full, ps-1/pe-2, gap-1 and a size-4 (16px) Remix-style
    circle-arrow icon. Lime/rose dark: 950 @60% bg + 500 text.
    Returns (svg, width)."""
    FS = 14
    H = 24  # 20px line + 2px top/bottom
    tw = measure(text, FS)
    base = "" if STATIC else ' class="meta"'
    if kind == "lime":
        bg, fg = LIME_BG, LIME_TXT
        w = 4 + 16 + 4 + tw + 8
        cx, cy = x + 4 + 8, y + H / 2
        icon = (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="8" fill="{fg}"/>'
                f'<rect x="{cx - 1.9:.1f}" y="{cy - 1.5:.1f}" width="3.8" height="5.5" rx="1" fill="{CARD}"/>'
                f'<polygon points="{cx - 5:.1f},{cy - 0.5:.1f} {cx:.1f},{cy - 6:.1f} {cx + 5:.1f},{cy - 0.5:.1f}" fill="{CARD}"/>')
        tx = x + 24
    elif kind == "rose":
        bg, fg = ROSE_BG, ROSE_TXT
        w = 4 + 16 + 4 + tw + 8
        cx, cy = x + 4 + 8, y + H / 2
        icon = (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="8" fill="{fg}"/>'
                f'<rect x="{cx - 1.9:.1f}" y="{cy - 4:.1f}" width="3.8" height="5.5" rx="1" fill="{CARD}"/>'
                f'<polygon points="{cx - 5:.1f},{cy + 0.5:.1f} {cx:.1f},{cy + 6:.1f} {cx + 5:.1f},{cy + 0.5:.1f}" fill="{CARD}"/>')
        tx = x + 24
    else:
        bg, fg = NEU_BG, NEU_TXT
        w = 6 + tw + 6
        icon, tx = "", x + 6
    rx = 12 if kind in ("lime", "rose") else 6
    op = "" if (kind == "neutral" or LIGHT) else ' fill-opacity="0.6"'
    return ((f'<g{base}><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{H}" rx="{rx}" fill="{bg}"{op}/>{icon}'
             f'<text x="{tx:.0f}" y="{y + 17:.0f}" fill="{fg}" font-size="{FS}" font-weight="500">{esc(text)}</text></g>'), w)


def delta_kind(pct: float | None) -> tuple[str, str]:
    if pct is None or abs(pct) < 0.05:
        return "0%", "neutral"
    return (f'{"+" if pct > 0 else ""}{pct:.1f}%'.replace(".", ","), "lime" if pct > 0 else "rose")


def main() -> None:
    payload = json.loads(DATA.read_text())
    svg_user = payload.get("username") or "GitHub"
    days = payload["days"]
    total = payload["total_last_year"]
    stats = payload["stats"]
    by_date = {d["date"]: d for d in days}

    counts = [d["count"] for d in days]
    last30 = sum(counts[-30:])
    prev30 = sum(counts[-60:-30])
    d_total = ((last30 - prev30) / prev30 * 100) if prev30 else None

    monthly = stats.get("monthly_totals", {})
    trail = sorted(monthly.keys())
    cur_val = monthly[trail[-1]] if trail else 0
    prev_val = monthly[trail[-2]] if len(trail) > 1 else 0
    d_month = ((cur_val - prev_val) / prev_val * 100) if prev_val else None
    # chart series: January -> December of the current (latest) year
    Y = int(trail[-1][:4]) if trail else date.today().year
    keys = [f"{Y}-{m:02d}" for m in range(1, 13)]
    mvals = [monthly.get(k, 0) for k in keys]
    ytd = sum(mvals)
    yp = Y - 1
    yprev = sum(monthly.get(f"{yp}-{m:02d}", 0) for m in range(1, 13))
    # full previous calendar year when available (trailing scrape is partial)
    yprev_full = stats.get("yearly_totals", {}).get(str(yp), 0) or yprev
    if yprev_full > 0:
        d_yoy = (ytd - yprev_full) / yprev_full * 100
        t_yoy, k_yoy = delta_kind(d_yoy)
    else:
        t_yoy, k_yoy = str(Y), "neutral"
    last = next((i for i in range(11, -1, -1) if mvals[i] > 0), 0)
    if last > 0 and mvals[last - 1]:
        d_chart = (mvals[last] - mvals[last - 1]) / mvals[last - 1] * 100
    else:
        d_chart = None
    cmp_lbl = f"{MESES[last + 1]} {Y}"

    t_total, k_total = delta_kind(d_total)
    t_month, k_month = delta_kind(d_month)
    t_chart, k_chart = str(Y), "neutral"

    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    best_n = stats.get("best_day_count", 0)
    best_d = stats.get("best_day") or ""
    try:
        bd = date.fromisoformat(best_d)
        best_lbl = f"{bd.day} {MESES[bd.month].lower()}"
    except ValueError:
        best_lbl = best_d

    # heatmap weeks
    start = date.fromisoformat(days[0]["date"])
    end = date.fromisoformat(days[-1]["date"])
    cur = start - timedelta(days=(start.weekday() + 1) % 7)
    weeks: list[list] = []
    while cur <= end:
        week = []
        for _ in range(7):
            week.append(by_date.get(cur.isoformat()))
            cur += timedelta(days=1)
        weeks.append(week)
    weeks = weeks[-53:]

    try:
        gstats = json.loads((ROOT / "data" / "github_stats.json").read_text())
    except (OSError, ValueError):
        gstats = {"languages": [], "repos": [], "repo_count": 0}
    langs = gstats.get("languages", [])[:8]
    repo_count = gstats.get("repo_count", 0)
    try:
        logos = json.loads((ROOT / "data" / "lang_logos.json").read_text())
    except (OSError, ValueError):
        logos = {}

    H_STATS, GAP = 172, 16
    H_CHART, H_HEAT = 300, 196
    H_LANG = (76 + (len(langs) - 1) * 30) if langs else 120
    SHOW = load_config()["sections"]
    y = GAP
    if SHOW["kpis"]:
        y_kpi = y
        y += H_STATS + GAP
    if SHOW["extras"]:
        y_kpi2 = y
        y += H_STATS + GAP
    if SHOW["chart"]:
        y_chart = y
        y += H_CHART + GAP
    if SHOW["languages"]:
        y_lang = y
        y += H_LANG + GAP
    if SHOW["heatmap"]:
        y_heat = y
        y += H_HEAT + GAP
    H = y + 2

    p: list[str] = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
             f'viewBox="0 0 {W} {H}" font-family="{FONT}" role="img">')
    p.append(f'<title>Dashboard GitHub de {esc(svg_user)}</title>'
             '<desc>Contribuições, linguagens, streak e estatísticas atualizados automaticamente.</desc>')
    p.append("<defs>" + "".join(
        f'<linearGradient id="t{t}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
        for t, (a, b) in TONES.items()) + "</defs>")
    if STATIC:
        p.append("<style>.cell,.row,.meta{opacity:1;}</style>")
    else:
        p.append("""<style>
.cell{opacity:0;animation:drop .45s ease-out forwards;}
@keyframes drop{from{opacity:0;transform:translateY(-7px);}to{opacity:1;transform:translateY(0);}}
.row{opacity:0;animation:rowin .5s ease-out forwards;}
@keyframes rowin{from{opacity:0;transform:translateX(10px);}to{opacity:1;transform:translateX(0);}}
.meta{opacity:0;animation:fadein .8s ease-out forwards;}
@keyframes fadein{to{opacity:1;}}
@media (prefers-reduced-motion:reduce){.cell,.row,.meta{animation:none;opacity:1;}}
</style>""")

    def card(x: float, y: float, w: float, h: float) -> None:
        p.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="16" fill="{CARD}" stroke="{CARD_BORDER}"/>')

    px = 20

    # ---- row 1: plain stat cards ----
    cw = (W - 3 * GAP) / 4
    # drawn tile glyphs (centered)
    GLYPHS = {
        "●": '<circle cx="0" cy="0" r="6" fill="#FFFFFF"/>',
        "▲": '<polygon points="0,-7 7,5 -7,5" fill="#FFFFFF"/>',
        "★": '<polygon points="0,-8 2.4,-2.6 8,-2.5 3.5,1.2 5,7 0,3.5 -5,7 -3.5,1.2 -8,-2.5 -2.4,-2.6" fill="#FFFFFF"/>',
        "◆": '<polygon points="0,-7 7,0 0,7 -7,0" fill="#FFFFFF"/>',
        "PR": '<g fill="#FFFFFF"><circle cx="0" cy="-5" r="2.6"/><circle cx="0" cy="5" r="2.6"/><rect x="-1.1" y="-5" width="2.2" height="10"/></g>',
    }
    plbl = MESES[int(trail[-2][5:7])] if len(trail) > 1 else ""
    cards = [
        ("●", "emerald", "Contribuições", fmt(ytd), t_yoy, k_yoy,
         f"{fmt(yprev_full)} em {yp}", 0.05),
        ("◆", "orange", "Este mês", fmt(cur_val), t_month, k_month,
         f"{fmt(prev_val)} em {plbl}", 0.12),
        ("★", "purple", "Melhor dia", fmt(best_n), best_lbl, "neutral",
         "Recorde pessoal", 0.19),
        ("▲", "blue", "Streak atual", f"{streak}", f"{longest}", "neutral",
         "Recorde", 0.26),
    ]
    def stat_card(x, y0, w, glyph, tone, label, value, delta, kind, caption, dl):
        card(x, y0, w, H_STATS)
        anim = "" if STATIC else f' class="row" style="animation-delay:{dl:.2f}s"'
        tcx, tcy = x + 32, y0 + 30
        p.append(f'<g{anim}><rect x="{x + 16:.0f}" y="{y0 + 14:.0f}" width="32" height="32" rx="8" fill="url(#t{tone})"/>'
                 f'<g transform="translate({tcx:.0f},{tcy:.0f})">{GLYPHS[glyph]}</g>'
                 f'<text x="{x + 16:.0f}" y="{y0 + 66:.0f}" fill="{SEC}" font-size="12">{esc(label)}</text>'
                 f'<text x="{x + 16:.0f}" y="{y0 + 106:.0f}" fill="{FG}" font-size="40" font-weight="600">{esc(value)}</text></g>')
        # footer band: comparison caption (left) + delta pill (right)
        by = y0 + H_STATS - 52
        p.append(f'<rect x="{x + 8:.0f}" y="{by:.0f}" width="{w - 16:.0f}" height="40" rx="10" fill="{BAND}"/>')
        _, chw = chip(0, 0, delta, kind)
        pill_x = x + w - 14 - chw
        ch, _ = chip(pill_x, by + 8, delta, kind)
        if not STATIC:
            ch = ch.replace(' class="meta"', f' class="meta" style="animation-delay:{dl + 0.15:.2f}s"', 1)
        p.append(ch)
        cap_w = (pill_x - 6) - (x + 18)
        cap = caption if len(caption) * 5.6 <= cap_w else caption[:max(0, int(cap_w / 5.6) - 1)] + "…"
        p.append(f'<text x="{x + 18:.0f}" y="{by + 26:.0f}" fill="{TER}" font-size="11">{esc(cap)}</text>')

    if SHOW["kpis"]:
        for i, (glyph, tone, label, value, delta, kind, caption, dl) in enumerate(cards):
            stat_card(i * (cw + GAP), y_kpi, cw,
                      glyph, tone, label, value, delta, kind, caption, dl)

    # ---- row 1b: PRs + Stars ----
    cw2 = (W - GAP) / 2
    prs_v = gstats.get("prs")
    stars_v = gstats.get("stars", 0)
    cards2 = [
        ("PR", "sky", "Pull requests", fmt(prs_v) if prs_v is not None else "—",
         "total", "neutral", "Criados por você", 0.33),
        ("★", "yellow", "Stars", fmt(stars_v),
         "recebidas", "neutral", "Nos repositórios", 0.40),
    ]
    if SHOW["extras"]:
        for i, (glyph, tone, label, value, delta, kind, caption, dl) in enumerate(cards2):
            stat_card(i * (cw2 + GAP), y_kpi2, cw2,
                      glyph, tone, label, value, delta, kind, caption, dl)

    # ---- row 2: chart card ----
    if SHOW["chart"]:
        card(0, y_chart, W, H_CHART)
        px = 20
        p.append(f'<text x="{px}" y="{y_chart + 28:.0f}" fill="{SEC}" font-size="12">Contribuições</text>')
        hv = fmt(ytd)
        p.append(f'<text x="{px}" y="{y_chart + 58:.0f}" fill="{FG}" font-size="24" font-weight="600">{hv}</text>')
        hx = px + len(hv) * 13.2 + 10
        chh, chhw = chip(hx, y_chart + 38, t_chart, k_chart)
        if hx + chhw > W - 260:
            hx = W - 260 - chhw
            chh, chhw = chip(hx, y_chart + 38, t_chart, k_chart)
        p.append(chh)
        p.append(f'<text x="{px}" y="{y_chart + 78:.0f}" fill="{TER}" font-size="12">{fmt(mvals[last])} em {cmp_lbl}</text>')
        # legend, right-aligned
        p.append(f'<text x="{W - 20:.0f}" y="{y_chart + 34:.0f}" fill="{SEC}" font-size="12" text-anchor="end">Este período</text>'
                 f'<circle cx="{W - 106:.0f}" cy="{y_chart + 30:.0f}" r="4" fill="{ACCENT}"/>')
        # bars
        bx0, bx1 = 56, W - 16
        by0, by1 = y_chart + 96, y_chart + H_CHART - 34
        mx = max(mvals) if mvals else 1
        # y ticks
        for f in (1.0, 0.66, 0.33):
            v = mx * f
            yy = by1 - (by1 - by0) * f
            lbl = f'{v / 1000:.1f}k'.replace(".", ",") if v >= 1000 else f'{v:.0f}'
            p.append(f'<text x="{bx0 - 8:.0f}" y="{yy + 4:.0f}" fill="{TER}" font-size="11" text-anchor="end">{lbl}</text>')
        slot = (bx1 - bx0) / max(len(keys), 1)
        bw = max(10, slot - 26)
        for i, (k, v) in enumerate(zip(keys, mvals)):
            hgt = max(4, v / mx * (by1 - by0))
            x = bx0 + i * slot + (slot - bw) / 2
            d = 0.5 + i * 0.06
            at = "" if STATIC else f' class="cell" style="animation-delay:{d:.2f}s"'
            p.append(f'<rect{at} x="{x:.0f}" y="{by1 - hgt:.0f}" width="{bw:.0f}" height="{hgt:.0f}" rx="4" fill="{ACCENT}"><title>{k}: {v}</title></rect>')
            p.append(f'<text x="{bx0 + i * slot + slot / 2:.0f}" y="{y_chart + H_CHART - 12:.0f}" fill="{TER}" font-size="12" text-anchor="middle">{MESES[int(k[5:7])]}</text>')

    # ---- languages card (bar list) ----
    if SHOW["languages"]:
        card(0, y_lang, W, H_LANG)
        p.append(f'<text x="{px}" y="{y_lang + 26:.0f}" fill="{SEC}" font-size="12">Linguagens mais usadas</text>')
        p.append(f'<text x="{W - 20:.0f}" y="{y_lang + 26:.0f}" fill="{TER}" font-size="11" text-anchor="end">{repo_count} repositórios</text>')
        if langs:
            tx0, tx1 = 210, W - 84
            for i, lang in enumerate(langs):
                ry = y_lang + 52 + i * 30
                color = LANG_COLORS.get(lang["name"], LANG_DEFAULT)
                pct = lang["pct"]
                dl = 0.7 + i * 0.08
                at = "" if STATIC else f' class="cell" style="animation-delay:{dl:.2f}s"'
                if lang["name"] in logos:
                    mark = (f'<g transform="translate(23,{ry - 3:.0f}) scale(0.5833)">'
                            f'<path d="{logos[lang["name"]]["path"]}" fill="{logos[lang["name"]].get("color", color)}"/></g>')
                else:
                    mark = f'<circle cx="30" cy="{ry + 4:.0f}" r="4" fill="{color}"/>'
                p.append(f'{mark}'
                         f'<text x="44" y="{ry + 8:.0f}" fill="{FG}" font-size="12">{esc(lang["name"][:18])}</text>'
                         f'<rect x="{tx0}" y="{ry:.0f}" width="{tx1 - tx0:.0f}" height="8" rx="4" fill="{TRACK}"/>'
                         f'<rect{at} x="{tx0}" y="{ry:.0f}" width="{max(4, pct / 100 * (tx1 - tx0)):.0f}" height="8" rx="4" fill="{color}">'
                         f'<title>{esc(lang["name"])}: {lang["bytes"] / 1024:.0f} KB</title></rect>'
                         f'<text x="{W - 20:.0f}" y="{ry + 8:.0f}" fill="{SEC}" font-size="12" text-anchor="end">{str(pct).replace(".", ",")}%</text>')
        else:
            p.append(f'<text x="{px}" y="{y_lang + 64:.0f}" fill="{TER}" font-size="12">coletando dados…</text>')

    # ---- row 3: heatmap card ----
    if SHOW["heatmap"]:
        card(0, y_heat, W, H_HEAT)
        p.append(f'<text x="{px}" y="{y_heat + 26:.0f}" fill="{SEC}" font-size="12">Calendário</text>')
        CELL, STEP, LEFT, TOP = 12, 15, 64, y_heat + 44
        last_m, last_x = None, -100.0
        for wi, week in enumerate(weeks):
            for dd in week:
                if dd:
                    m = int(dd["date"][5:7])
                    x = LEFT + wi * STEP
                    if m != last_m and x - last_x >= 30:
                        p.append(f'<text x="{x:.0f}" y="{TOP - 8:.0f}" fill="{TER}" font-size="9">{MESES[m]}</text>')
                        last_x = x
                    last_m = m
                    break
        for di, nm in ((0, "Dom"), (2, "Ter"), (4, "Qui"), (6, "Sáb")):
            p.append(f'<text x="30" y="{TOP + di * STEP + 10:.0f}" fill="{TER}" font-size="9">{nm}</text>')
        for wi, week in enumerate(weeks):
            # one animation group per week (53) instead of per cell (~370):
            # same staggered reveal, far fewer bytes -> faster first paint
            at = "" if STATIC else f' class="cell" style="animation-delay:{wi * 0.035:.2f}s"'
            p.append(f'<g{at}>')
            for di, dd in enumerate(week):
                x = LEFT + wi * STEP
                yy = TOP + di * STEP
                if dd is None:
                    continue
                lv, ct = dd["level"], dd["count"]
                color = (HEAT + [HEAT_TOP])[5 if (lv >= 4 and ct >= 30) else max(0, min(lv, 4))]
                p.append(f'<rect x="{x:.0f}" y="{yy:.0f}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"><title>{ct} em {dd["date"]}</title></rect>')
            p.append('</g>')
        foot = (f'streak atual {streak} dias · melhor dia {best_d} ({fmt(best_n)})')
        fat = "" if STATIC else ' class="meta" style="animation-delay:1.8s"'
        p.append(f'<text{fat} x="{px}" y="{y_heat + H_HEAT - 12:.0f}" fill="{TER}" font-size="11">{esc(foot)}</text>')
        # Less -> More legend, bottom-right (same line as the footer)
        llx = W - 196
        p.append(f'<text x="{llx - 40:.0f}" y="{y_heat + H_HEAT - 12:.0f}" fill="{TER}" font-size="10">Less</text>')
        for i, c in enumerate(HEAT):
            p.append(f'<rect x="{llx + i * 13:.0f}" y="{y_heat + H_HEAT - 22:.0f}" width="10" height="10" rx="2" fill="{c}"/>')
        p.append(f'<text x="{llx + 70:.0f}" y="{y_heat + H_HEAT - 12:.0f}" fill="{TER}" font-size="10">More</text>')

    p.append("</svg>")
    OUT.write_text("\n".join(p) + "\n")
    print(f"Wrote {OUT} ({H}px tall, static={STATIC})")


if __name__ == "__main__":
    main()
