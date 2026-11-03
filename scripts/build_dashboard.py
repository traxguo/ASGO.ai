#!/usr/bin/env python3
"""
Builds the "ASGO TAKİP" page: one HTML file that shows where the research
stands, built only from files already in the repo (no invented numbers).

Sources:
  docs/roadmap.md      current level, levels, next steps
  CLAUDE.md            test pipeline stages
  docs/metrics.md      pass thresholds
  cards/*.md           strategies, status, lessons
  results/*/rapor.md   backtest metrics (and optional islemler.csv trade lists)
  journal/*.md         last session notes
  docs/decisions.md    last decisions
  strategies/active/   which strategies are allowed to send signals

Usage:
  python scripts/build_dashboard.py [--root .] [--out dashboard/asgo_takip.html]

Standard library only, so it runs anywhere (also on the owner's Windows PC).
The output has no <html>/<head>/<body> tags on purpose: browsers open it as is,
and the Artifact publisher wraps it in its own skeleton.
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import re
from pathlib import Path

# ---------------------------------------------------------------- markdown helpers


def inline(text: str) -> str:
    """Escape text and render the few inline markdown bits the repo uses."""
    t = html.escape(text.strip(), quote=False)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # links -> their text
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def sections(md: str, level: int = 2) -> dict[str, str]:
    """Split markdown into {heading: body} for headings of the given level."""
    out: dict[str, str] = {}
    marker = "#" * level + " "
    current = None
    buf: list[str] = []
    for line in md.splitlines():
        if line.startswith(marker):
            if current is not None:
                out[current] = "\n".join(buf).strip()
            current, buf = line[len(marker):].strip(), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf).strip()
    return out


def find_section(secs: dict[str, str], prefix: str) -> tuple[str, str] | None:
    for k, v in secs.items():
        if k.lower().startswith(prefix.lower()):
            return k, v
    return None


def bullets(body: str) -> list[str]:
    items: list[str] = []
    open_item = False
    for line in body.splitlines():
        s = line.strip()
        if re.match(r"^([-*]|\d+\.)\s+", s) and s != "---":
            items.append(re.sub(r"^([-*]|\d+\.)\s+", "", s))
            open_item = True
        elif s and open_item and not s.startswith(("|", "#", "```", "---")):
            items[-1] += " " + s  # wrapped bullet
        else:
            open_item = False
    return items


def table(body: str) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("|") and not re.match(r"^\|[\s\-|:]+\|$", s):
            rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


def num(text: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", "."))
    return float(m.group()) if m else None


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


# ---------------------------------------------------------------- data collection


def load_roadmap(root: Path) -> dict:
    md = read(root / "docs/roadmap.md")
    m = re.search(r"Şu anki seviye:\s*(\d+)\s*[—-]\s*([^*\n(]+)", md)
    levels = re.findall(r"^## Seviye (\d+) [—-] (.+)$", md, re.M)
    nxt = find_section(sections(md), "Sıradaki adım")
    return {
        "level": int(m.group(1)) if m else None,
        "level_name": m.group(2).strip() if m else "",
        "levels": [(int(n), name.strip()) for n, name in levels],
        "next": bullets(nxt[1]) if nxt else [],
    }


def load_pipeline(root: Path) -> list[str]:
    m = re.search(r"Test hattı:\s*(.+)", read(root / "CLAUDE.md"))
    if not m:
        return []
    return [s.strip(" .") for s in m.group(1).split("→")]


def load_thresholds(root: Path) -> dict:
    """Pass thresholds from docs/metrics.md, keyed by metric."""
    rows = table(sections(read(root / "docs/metrics.md")).get("Geçme eşikleri", ""))
    out = {}
    for name, value in (r for r in rows[1:] if len(r) >= 2):
        n = name.lower()
        if "profit factor" in n:
            out["pf"] = num(value)
        elif "drawdown" in n:
            out["dd"] = num(value)
        elif "işlem sayısı" in n:
            out["trades"] = num(value)
        elif "expectancy" in n:
            out["r"] = num(value)
        elif "coin oranı" in n:
            out["coins"] = num(value)
    return out


def card_status_kind(text: str) -> str:
    t = text.lower()
    if re.search(r"\bactive\b|\baktif\b", t) and not re.search(r"elendi|retired|emekli", t):
        return "active"
    if re.search(r"\baday\b", t):  # e.g. "en iyi aday" wins over a retired sibling variant
        return "candidate"
    if re.search(r"elendi|retired|emekli", t):
        return "retired"
    return "candidate"


def load_cards(root: Path) -> list[dict]:
    cards = []
    for p in sorted((root / "cards").glob("*.md")):
        if p.name.startswith("_") or p.name.upper() == "README.MD":
            continue
        md = read(p)
        title = re.search(r"^# (.+)$", md, re.M)
        name, _, desc = (title.group(1) if title else p.stem).partition("—")
        secs = sections(md)
        status = find_section(secs, "Durum")
        # Status is either on the heading line ("## Durum: retired") or a list below it.
        status_lines: list[str] = []
        if status:
            head = status[0].partition(":")[2].strip()
            if head:
                status_lines.append(head)
            status_lines += bullets(status[1])
        hyp = find_section(secs, "Hipotez")
        hist = find_section(secs, "Test geçmişi")
        notes = find_section(secs, "Notlar")
        retire = find_section(secs, "Emeklilik")
        retire_items = bullets(retire[1]) if retire else []
        if retire and not retire_items and retire[1].strip():
            retire_items = [retire[1].strip()]
        cards.append({
            "id": p.stem,
            "name": name.strip(),
            "desc": desc.strip(),
            "status": status_lines,
            "kind": card_status_kind(" ".join(status_lines)),
            "hypothesis": hyp[1].split("\n\n")[0] if hyp else "",
            "history": table(hist[1])[1:] if hist else [],
            "notes": bullets(notes[1]) if notes else [],
            "retire": retire_items,
        })
    return cards


def load_results(root: Path) -> list[dict]:
    results = []
    for d in sorted((root / "results").iterdir() if (root / "results").exists() else []):
        rep = d / "rapor.md"
        if not d.is_dir() or not rep.exists():
            continue
        md = read(rep)
        secs = sections(md)
        title = re.search(r"^# (.+)$", md, re.M)
        period = re.search(r"Dönem:\s*(\S+)[^→]*→\s*(\S+)", md)
        metrics = table(secs.get("Metrikler", ""))
        strategies = []
        if metrics:
            header = metrics[0]
            by_metric = {r[0]: r for r in metrics[1:]}
            for i, col in enumerate(header[1:], start=1):
                if col.lower() == "al-tut":
                    continue
                g = lambda k: by_metric.get(k, [""] * (i + 1))[i]  # noqa: E731
                strategies.append({
                    "name": col,
                    "net": g("Net getiri"), "dd": g("Max drawdown"), "pf": g("Profit factor"),
                    "r": g("Ortalama R"), "trades": g("İşlem sayısı"), "winrate": g("Winrate"),
                })
            hold = header.index("Al-tut") if "Al-tut" in header else None
            buy_hold = by_metric.get("Net getiri", [])[hold] if hold else ""
        else:
            buy_hold = ""
        decision = find_section(secs, "Karar")
        sermaye = sorted(d.glob("*_sermaye.png"))
        results.append({
            "dir": d.name,
            "date": d.name[:10],
            "title": title.group(1) if title else d.name,
            "kind": "dogrulama" if "dogrulama" in d.name else "gelistirme",
            "period": (period.group(1), period.group(2)) if period else None,
            "strategies": strategies,
            "buy_hold": buy_hold,
            "long_short": table(secs.get("Long / short ayrımı", ""))[1:],
            "coins": table(secs.get("Coin bazında", ""))[1:],
            "decision": decision[1].split("\n\n")[0] if decision else "",
            "charts": sermaye,
            "trades_csv": d / "islemler.csv" if (d / "islemler.csv").exists() else None,
        })
    return results


JOURNAL_SECTIONS = ("Bulgular", "Başarısız", "Açık sorular", "Sıradaki adım")


def load_journal(root: Path, n: int = 3, per_section: int = 4) -> list[dict]:
    files = sorted(p for p in (root / "journal").glob("*.md") if re.match(r"\d{4}-\d{2}-\d{2}", p.name))
    out = []
    for p in reversed(files[-n:]):
        secs = sections(read(p))
        keep = {k: bullets(v)[:per_section] for k, v in secs.items()
                if k.startswith(JOURNAL_SECTIONS) and bullets(v)}
        out.append({"date": p.stem, "sections": keep})
    return out


def load_decisions(root: Path, n: int = 3) -> list[dict]:
    md = read(root / "docs/decisions.md")
    out = []
    for head, body in sections(md).items():
        m = re.match(r"(\d{4}-\d{2}-\d{2})\s*[—-]\s*(.+)", head)
        if m:
            out.append({"date": m.group(1), "title": m.group(2), "items": bullets(body)})
    return out[:n]  # file is newest first


def active_strategies(root: Path) -> list[str]:
    return sorted(p.stem for p in (root / "strategies/active").glob("*.py") if p.stem != "__init__")


# ---------------------------------------------------------------- analysis


def best_candidate(results: list[dict]) -> tuple[dict, dict] | None:
    """Strategy with the highest average R on validation data (or development if none)."""
    pool = [r for r in results if r["kind"] == "dogrulama"] or results
    best = None
    for rep in pool:
        for s in rep["strategies"]:
            r = num(s["r"])
            if r is not None and (best is None or r > num(best[1]["r"])):
                best = (rep, s)
    return best


def checks(s: dict, rep: dict, th: dict) -> list[tuple[str, str, bool | None]]:
    """(label, value vs threshold, passed) rows for one strategy result."""
    out = []
    r, pf, dd, tr = num(s["r"]), num(s["pf"]), num(s["dd"]), num(s["trades"])
    if r is not None:
        out.append(("İşlem başına ortalama sonuç", f"{s['r']}R (gereken > {th.get('r', 0):g}R)", r > th.get("r", 0)))
    if pf is not None and "pf" in th:
        out.append(("Profit factor (kazanç / kayıp)", f"{s['pf']} (gereken ≥ {th['pf']:g})", pf >= th["pf"]))
    if dd is not None and "dd" in th:
        out.append(("En büyük düşüş", f"%{dd:g} (gereken ≤ %{th['dd']:g})", dd <= th["dd"]))
    if tr is not None and "trades" in th:
        out.append(("İşlem sayısı", f"{tr:g} (gereken ≥ {th['trades']:g})", tr >= th["trades"]))
    coins = [c for c in rep["coins"] if c and c[0] == s["name"]]
    if coins and "coins" in th:
        pos = sum(1 for c in coins if (num(c[4]) or 0) > 0)
        pct = 100 * pos / len(coins)
        out.append(("Kârlı coin oranı", f"{pos}/{len(coins)} coin (gereken ≥ %{th['coins']:g})", pct >= th["coins"]))
    return out


def stage_reached(cards: list[dict], best_name: str) -> int | None:
    """Pipeline stage (1-based) where the best candidate got stuck, from its card status."""
    for c in cards:
        for line in c["status"]:
            plain = line.replace("`", "")
            if best_name.rsplit("_", 1)[0] in plain or c["id"] in best_name.lower():
                m = re.search(r"aşama\s*(\d+)", plain, re.I)
                if m:
                    return int(m.group(1))
    return None


def load_trades(path: Path, n: int = 15) -> tuple[list[str], list[list[str]]]:
    with path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return (rows[0], rows[1:][-n:][::-1]) if rows else ([], [])


# ---------------------------------------------------------------- html


KIND_LABEL = {"active": "Aktif", "candidate": "Aday", "retired": "Elendi"}


def chip(kind: str, label: str | None = None) -> str:
    return f'<span class="chip {kind}">{html.escape(label or KIND_LABEL.get(kind, kind))}</span>'


def r_class(value: str) -> str:
    v = num(value)
    return "" if v is None else ("pos" if v > 0 else "neg" if v < 0 else "")


def render(root: Path) -> str:
    road = load_roadmap(root)
    stages = load_pipeline(root)
    th = load_thresholds(root)
    cards = load_cards(root)
    results = load_results(root)
    journal = load_journal(root)
    decisions = load_decisions(root)
    active = active_strategies(root)
    best = best_candidate(results)

    dates = [r["date"] for r in results] + [j["date"] for j in journal]
    updated = max(dates) if dates else "—"
    tested = sorted({s["name"].rsplit("_", 1)[0] for r in results for s in r["strategies"]})

    h: list[str] = []
    a = h.append

    # --- header
    a('<header class="top"><div class="brand"><span class="mark" aria-hidden="true"></span>'
      '<div><h1>ASGO TAKİP</h1><p class="sub">Araştırma sisteminin defteri: ne denedi, ne öğrendi, nerede duruyor.</p></div></div>'
      f'<div class="stamp">Son kayıt<br><b>{html.escape(updated)}</b></div></header>')
    a('<p class="honest"><b>Bilmen gerekenler:</b> Buradaki "yapay zeka", kendi kendine öğrenen bir model değil; '
      'kuralları önceden yazılmış stratejileri geçmiş veride test eden bir araştırma sistemi. '
      '<b>Henüz gerçek ya da sanal canlı işlem yok</b>; bütün rakamlar geçmiş veri testlerinden (backtest). '
      'Sayfadaki her şey repodaki dosyalardan otomatik okunur.</p>')

    # --- summary tiles
    a('<section class="tiles">')
    a(f'<div class="tile"><span class="lbl">Seviye</span><span class="big">{road["level"] if road["level"] is not None else "—"}</span>'
      f'<span class="foot">{html.escape(road["level_name"])}</span></div>')
    a(f'<div class="tile"><span class="lbl">Test edilen strateji</span><span class="big">{len(tested)}</span>'
      f'<span class="foot">{len(results)} test raporu</span></div>')
    a(f'<div class="tile"><span class="lbl">Seçilen (aktif) strateji</span><span class="big">{len(active)}</span>'
      f'<span class="foot">{html.escape(", ".join(active)) if active else "Henüz hiçbiri testleri geçmedi"}</span></div>')
    if best:
        rep, s = best
        a(f'<div class="tile accent"><span class="lbl">En iyi aday</span><span class="big sm">{html.escape(s["name"])}</span>'
          f'<span class="foot">{"Doğrulama" if rep["kind"] == "dogrulama" else "Geliştirme"}: '
          f'<b class="{r_class(s["r"])}">{html.escape(s["r"])}R</b> / işlem, isabet {html.escape(s["winrate"])}</span></div>')
    a('</section>')

    # --- progress
    a('<section><h2>İlerleme</h2><div class="two">')
    a('<div class="panel"><h3>Proje seviyeleri</h3><ol class="levels">')
    for n, name in road["levels"]:
        state = "done" if road["level"] is not None and n < road["level"] else "now" if n == road["level"] else "todo"
        tag = {"done": "tamam", "now": "şu an", "todo": "sırada"}[state]
        a(f'<li class="{state}"><span class="dot">{n}</span><span class="nm">{inline(name)}</span><span class="st">{tag}</span></li>')
    a('</ol></div>')
    if stages:
        stuck = stage_reached(cards, best[1]["name"]) if best else None
        title = f"Test hattı: {html.escape(best[1]['name'])}" if best else "Test hattı"
        a(f'<div class="panel"><h3>{title}</h3><ol class="pipe">')
        for i, st in enumerate(stages, start=1):
            state = "todo" if stuck is None else "done" if i < stuck else "stuck" if i == stuck else "todo"
            tag = {"done": "geçti", "stuck": "takıldı", "todo": "bekliyor"}[state]
            a(f'<li class="{state}"><span class="dot">{i}</span><span class="nm">{inline(st)}</span><span class="st">{tag}</span></li>')
        a('</ol><p class="note">Bir stratejinin sinyal göndermesi için 1-6 arası aşamaların hepsini geçmesi gerekir.</p></div>')
    a('</div>')
    if road["next"]:
        a('<div class="panel next"><h3>Şu an ne bekleniyor / sıradaki iş</h3><ul>')
        a("".join(f"<li>{inline(x)}</li>" for x in road["next"]))
        a('</ul></div>')
    a('</section>')

    # --- why not selected
    if best:
        rep, s = best
        rows = checks(s, rep, th)
        a(f'<section><h2>Neden henüz seçilmedi?</h2><p class="lead">En iyi aday <b>{html.escape(s["name"])}</b>, '
          f'görmediği veride ({html.escape(" → ".join(rep["period"]) if rep["period"] else rep["dir"])}) geçme eşikleriyle kıyaslandı. '
          f'Aynı dönemde coinleri sadece alıp tutmak: <b>{html.escape(rep["buy_hold"] or "—")}</b>, bu strateji: <b>{html.escape(s["net"])}</b>.</p>')
        a('<div class="checks">')
        for label, val, ok in rows:
            a(f'<div class="check {"ok" if ok else "bad"}"><span class="ico" aria-hidden="true">{"✓" if ok else "✕"}</span>'
              f'<span class="cl">{html.escape(label)}</span><span class="cv">{html.escape(val)}</span></div>')
        a('</div>')
        if rep["decision"]:
            a(f'<p class="decision">{inline(rep["decision"])}</p>')
        if rep["charts"]:
            img = next((c for c in rep["charts"] if c.name.startswith(s["name"])), rep["charts"][0])
            data = base64.b64encode(img.read_bytes()).decode()
            a(f'<figure class="chart"><img alt="{html.escape(s["name"])} sermaye eğrisi" src="data:image/png;base64,{data}">'
              f'<figcaption>Sermaye eğrisi, doğrulama dönemi (rapordaki grafik)</figcaption></figure>')
        a('</section>')

    # --- strategies
    a('<section><h2>Denenen stratejiler</h2><div class="cards">')
    order = {"active": 0, "candidate": 1, "retired": 2}
    for c in sorted(cards, key=lambda c: order[c["kind"]]):
        a(f'<article class="card {c["kind"]}"><div class="ch"><h3>{inline(c["name"])}</h3>{chip(c["kind"])}</div>')
        if c["desc"]:
            a(f'<p class="desc">{inline(c["desc"])}</p>')
        if c["hypothesis"]:
            a(f'<p class="hyp">{inline(c["hypothesis"])}</p>')
        if c["status"]:
            a('<ul class="status">' + "".join(f"<li>{inline(x)}</li>" for x in c["status"]) + '</ul>')
        if c["retire"]:
            a('<p class="why"><b>Neden elendi:</b> ' + " ".join(inline(x) for x in c["retire"]) + '</p>')
        if c["history"]:
            a('<details><summary>Test geçmişi</summary><div class="scroll"><table><thead><tr><th>Tarih</th><th>Test</th><th>Sonuç</th></tr></thead><tbody>')
            for row in c["history"]:
                a("<tr>" + "".join(f"<td>{inline(x)}</td>" for x in row[:3]) + "</tr>")
            a('</tbody></table></div></details>')
        a('</article>')
    a('</div></section>')

    # --- results table
    a('<section><h2>Başarı rakamları</h2><p class="lead">Her test raporundaki sonuçlar. '
      '<b>R</b> = risk birimi: stop olunca kaybedilen miktar 1R. İşlem başına +0.10R, her işlemde riskin onda biri kadar kâr demek. '
      'İsabet oranı (winrate) tek başına başarı ölçüsü değildir.</p>')
    a('<div class="scroll"><table class="res"><thead><tr><th>Tarih</th><th>Veri</th><th>Strateji</th>'
      '<th class="n">İşlem</th><th class="n">İsabet</th><th class="n">R / işlem</th><th class="n">PF</th>'
      '<th class="n">En büyük düşüş</th><th class="n">Net</th><th class="n">Al-tut</th></tr></thead><tbody>')
    for rep in reversed(results):
        for s in rep["strategies"]:
            kind = "Doğrulama" if rep["kind"] == "dogrulama" else "Geliştirme"
            a(f'<tr><td>{rep["date"]}</td><td><span class="tag {rep["kind"]}">{kind}</span></td><td class="sn">{html.escape(s["name"])}</td>'
              f'<td class="n">{html.escape(s["trades"])}</td><td class="n">{html.escape(s["winrate"])}</td>'
              f'<td class="n {r_class(s["r"])}">{html.escape(s["r"])}</td><td class="n">{html.escape(s["pf"])}</td>'
              f'<td class="n">{html.escape(s["dd"])}</td><td class="n {r_class(s["net"])}">{html.escape(s["net"])}</td>'
              f'<td class="n">{html.escape(rep["buy_hold"])}</td></tr>')
    a('</tbody></table></div></section>')

    # --- trades
    a('<section><h2>Son işlemler</h2>')
    with_trades = [r for r in results if r["trades_csv"]]
    if with_trades:
        rep = with_trades[-1]
        head, rows = load_trades(rep["trades_csv"])
        a(f'<p class="lead">Canlı işlem yok. Bunlar <b>backtest (geçmiş veri testi)</b> işlemleri: {html.escape(rep["title"])}.</p>')
        a('<div class="scroll"><table><thead><tr>' + "".join(f"<th>{html.escape(x)}</th>" for x in head) + '</tr></thead><tbody>')
        for row in rows:
            a("<tr>" + "".join(f"<td>{html.escape(x)}</td>" for x in row) + "</tr>")
        a('</tbody></table></div>')
    else:
        a('<p class="lead">Canlı işlem yok (sinyal gönderen strateji henüz yok). Test raporları işlemleri tek tek saklamıyor, '
          'sadece özetliyor. Bir rapor klasörüne <code>islemler.csv</code> eklendiğinde son işlemler burada listelenir.</p>')
        if best:
            rep, s = best
            ls = [r for r in rep["long_short"] if r and r[0] == s["name"]]
            coins = [c for c in rep["coins"] if c and c[0] == s["name"]]
            a(f'<p class="lead">Şimdilik en iyi adayın ({html.escape(s["name"])}) son testteki işlemlerinin dökümü:</p><div class="two">')
            if ls:
                a('<div class="scroll"><table><thead><tr><th>Yön</th><th class="n">İşlem</th><th class="n">R / işlem</th><th class="n">Toplam R</th></tr></thead><tbody>')
                for r in ls:
                    a(f'<tr><td>{html.escape(r[1])}</td><td class="n">{r[2]}</td><td class="n {r_class(r[3])}">{r[3]}</td><td class="n {r_class(r[4])}">{r[4]}</td></tr>')
                a('</tbody></table></div>')
            if coins:
                a('<div class="scroll"><table><thead><tr><th>Coin</th><th class="n">İşlem</th><th class="n">Toplam R</th><th class="n">Al-tut</th></tr></thead><tbody>')
                for c in coins:
                    coin = c[1].split("/")[0]
                    a(f'<tr><td>{html.escape(coin)}</td><td class="n">{c[2]}</td><td class="n {r_class(c[4])}">{c[4]}</td><td class="n">{html.escape(c[5] if len(c) > 5 else "")}</td></tr>')
                a('</tbody></table></div>')
            a('</div>')
    a('</section>')

    # --- lessons
    lessons = [(c["name"], n) for c in cards for n in c["notes"]]
    if lessons:
        a('<section><h2>Ne öğrendi</h2><ul class="lessons">')
        for name, note in lessons:
            a(f'<li><span class="src">{inline(name)}</span>{inline(note)}</li>')
        a('</ul></section>')

    # --- notes
    a('<section><h2>Kendine aldığı son notlar</h2><div class="notes">')
    for j in journal:
        a(f'<article class="jn"><h3>Günlük · {j["date"]}</h3>')
        for head, items in j["sections"].items():
            a(f'<h4>{inline(head)}</h4><ul>' + "".join(f"<li>{inline(x)}</li>" for x in items) + '</ul>')
        a('</article>')
    a('</div>')
    if decisions:
        a('<h3 class="dh">Son kararlar</h3><div class="decs">')
        for d in decisions:
            a(f'<article class="dec"><span class="dd">{d["date"]}</span><h4>{inline(d["title"])}</h4><ul>'
              + "".join(f"<li>{inline(x)}</li>" for x in d["items"]) + '</ul></article>')
        a('</div>')
    a('</section>')

    a('<footer>Bu sayfa <code>scripts/build_dashboard.py</code> ile repodaki dosyalardan üretilir. '
      'Yatırım tavsiyesi değildir.</footer>')

    return PAGE_HEAD + '<main class="wrap">' + "".join(h) + "</main>"


PAGE_HEAD = """<title>ASGO TAKİP</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Figtree:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap">
<style>
/* Layout: a research logbook; summary tiles first, then progress, verdict, detail, notes. */
:root {
  --bg: #f3f5f4; --surface: #ffffff; --ink: #18211f; --muted: #5d6b67; --line: #dbe2df;
  --accent: #0e6b5c; --accent-soft: #dcefe9;
  --good: #1d7a3e; --good-soft: #e1f3e6; --bad: #b3322a; --bad-soft: #fbe5e2; --warn: #9a6a00; --warn-soft: #fbf0d6;
  --f-display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --f-body: "Figtree", "Segoe UI", system-ui, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0f1514; --surface: #172020; --ink: #e4ece9; --muted: #96a6a1; --line: #293533;
  --accent: #4fc4a8; --accent-soft: #163a33;
  --good: #5fcf86; --good-soft: #15301f; --bad: #f08a7f; --bad-soft: #3a1a17; --warn: #e3b94f; --warn-soft: #3a2f12;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0f1514; --surface: #172020; --ink: #e4ece9; --muted: #96a6a1; --line: #293533;
  --accent: #4fc4a8; --accent-soft: #163a33;
  --good: #5fcf86; --good-soft: #15301f; --bad: #f08a7f; --bad-soft: #3a1a17; --warn: #e3b94f; --warn-soft: #3a2f12;
  color-scheme: dark; }
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); margin: 0; }
.wrap { max-width: 1080px; margin: 0 auto; padding: 28px 16px 48px; display: grid; gap: 36px; }
h1, h2, h3 { font-family: var(--f-display); text-wrap: balance; margin: 0; }
h1 { font-size: 2.1rem; font-weight: 800; letter-spacing: .02em; }
h2 { font-size: 1.35rem; font-weight: 800; margin-bottom: 12px; }
h3 { font-size: 1.02rem; font-weight: 600; }
h4 { font-size: .78rem; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); margin: 12px 0 4px; }
section { display: grid; gap: 12px; min-width: 0; }
code { font-family: var(--f-mono); font-size: .86em; background: var(--accent-soft); padding: 0 4px; border-radius: 4px; }
.top { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; border-bottom: 2px solid var(--ink); padding-bottom: 14px; }
.brand { display: flex; gap: 14px; align-items: center; }
.mark { width: 44px; height: 44px; border-radius: 10px; background:
  linear-gradient(135deg, transparent 46%, var(--bg) 46%, var(--bg) 54%, transparent 54%), var(--accent); flex: none; }
.sub { margin: 2px 0 0; color: var(--muted); }
.stamp { font: 500 .8rem/1.4 var(--f-mono); color: var(--muted); text-align: right; }
.stamp b { color: var(--ink); font-size: 1rem; }
.honest { margin: 0; padding: 12px 14px; background: var(--warn-soft); border-radius: 8px; max-width: 75ch; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
.tile { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 14px 16px; display: grid; gap: 2px; min-width: 0; }
.tile.accent { border-color: var(--accent); background: var(--accent-soft); }
.lbl { font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); }
.big { font: 800 2.2rem/1.1 var(--f-display); font-variant-numeric: tabular-nums; }
.big.sm { font-size: 1.35rem; padding-block: 6px; overflow-wrap: anywhere; }
.foot { color: var(--muted); font-size: .88rem; }
.two { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; display: grid; gap: 10px; align-content: start; min-width: 0; }
.panel ul { margin: 0; padding-left: 18px; }
.levels, .pipe { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
.levels li, .pipe li { display: grid; grid-template-columns: 28px 1fr auto; gap: 10px; align-items: center; }
.dot { width: 28px; height: 28px; border-radius: 50%; display: grid; place-items: center; font: 500 .82rem var(--f-mono); border: 2px solid var(--line); color: var(--muted); }
.st { font-size: .76rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
.done .dot { background: var(--good); border-color: var(--good); color: var(--surface); }
.done .st { color: var(--good); }
.now .dot { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.now .nm { font-weight: 600; } .now .st { color: var(--accent); font-weight: 600; }
.stuck .dot { border-color: var(--bad); color: var(--bad); background: var(--bad-soft); }
.stuck .nm { font-weight: 600; } .stuck .st { color: var(--bad); font-weight: 600; }
.todo .nm { color: var(--muted); }
.note, .lead { margin: 0; color: var(--muted); max-width: 75ch; }
.lead b { color: var(--ink); }
.checks { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 8px; }
.check { display: grid; grid-template-columns: 26px 1fr; gap: 2px 10px; padding: 10px 12px; border-radius: 8px; }
.check.ok { background: var(--good-soft); } .check.bad { background: var(--bad-soft); }
.ico { grid-row: span 2; width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; font-weight: 700; color: var(--surface); }
.ok .ico { background: var(--good); } .bad .ico { background: var(--bad); }
.cl { font-weight: 600; } .cv { font: 500 .84rem var(--f-mono); color: var(--muted); }
.decision { margin: 0; padding: 12px 14px; border-left: 3px solid var(--ink); background: var(--surface); max-width: 75ch; }
.chart { margin: 0; background: #fff; border: 1px solid var(--line); border-radius: 10px; padding: 8px; max-width: 760px; }
.chart img { display: block; width: 100%; height: auto; }
.chart figcaption { font-size: .8rem; color: #5d6b67; padding: 4px 4px 0; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; display: grid; gap: 8px; align-content: start; min-width: 0; }
.card.retired { background: transparent; }
.ch { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
.ch h3 { font-family: var(--f-mono); font-weight: 500; font-size: .98rem; overflow-wrap: anywhere; }
.desc { margin: 0; font-weight: 600; }
.hyp { margin: 0; color: var(--muted); font-size: .92rem; }
.status { margin: 0; padding-left: 18px; font-size: .92rem; }
.why { margin: 0; font-size: .9rem; padding: 8px 10px; background: var(--bad-soft); border-radius: 6px; }
.chip { font-size: .72rem; text-transform: uppercase; letter-spacing: .07em; padding: 2px 8px; border-radius: 99px; font-weight: 600; white-space: nowrap; }
.chip.active { background: var(--good-soft); color: var(--good); }
.chip.candidate { background: var(--warn-soft); color: var(--warn); }
.chip.retired { background: var(--bad-soft); color: var(--bad); }
details summary { cursor: pointer; color: var(--accent); font-weight: 600; font-size: .9rem; }
details summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.scroll { overflow-x: auto; min-width: 0; }
table { border-collapse: collapse; width: 100%; font-size: .88rem; background: var(--surface); }
th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
th { font-size: .72rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); font-weight: 600; white-space: nowrap; }
td.n, th.n { text-align: right; font-family: var(--f-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.sn { font-family: var(--f-mono); font-size: .84rem; white-space: nowrap; }
.pos { color: var(--good); } .neg { color: var(--bad); }
.tag { font-size: .74rem; padding: 1px 7px; border-radius: 99px; white-space: nowrap; }
.tag.dogrulama { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
.tag.gelistirme { background: var(--bg); color: var(--muted); border: 1px solid var(--line); }
.lessons { margin: 0; padding: 0; list-style: none; display: grid; gap: 8px; max-width: 85ch; }
.lessons li { display: grid; gap: 2px; padding-bottom: 8px; border-bottom: 1px dashed var(--line); }
.src { font: 500 .76rem var(--f-mono); color: var(--accent); }
.notes { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
.jn { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 16px; min-width: 0; }
.jn ul, .dec ul { margin: 0; padding-left: 18px; font-size: .92rem; }
.dh { margin-top: 8px; }
.decs { display: grid; gap: 10px; }
.dec { display: grid; gap: 4px; padding: 12px 0; border-top: 1px solid var(--line); }
.dec h4 { text-transform: none; letter-spacing: 0; font-size: 1rem; color: var(--ink); margin: 0; font-family: var(--f-display); }
.dd { font: 500 .78rem var(--f-mono); color: var(--muted); }
footer { color: var(--muted); font-size: .84rem; border-top: 1px solid var(--line); padding-top: 12px; }
@media (max-width: 480px) { h1 { font-size: 1.7rem; } .stamp { text-align: left; } }
</style>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--root", default=".", help="repo root to read from")
    ap.add_argument("--out", default="dashboard/asgo_takip.html")
    args = ap.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(Path(args.root)), encoding="utf-8")
    print(f"Yazıldı: {out}")


if __name__ == "__main__":
    main()
