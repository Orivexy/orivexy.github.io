"""Builds index.html (English), es/index.html and ca/index.html from textos.py.
Run: python _src/build.py"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from textos import APPS, IB, LANGS, MAIL  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://orivexy.com/"
import hashlib
VER = hashlib.sha1((ROOT / "assets" / "web.css").read_bytes() + (ROOT / "assets" / "web.js").read_bytes()).hexdigest()[:8]
VERSIONS = ["15.0", "16.0", "17.0", "18.0", "19.0", "20.0"]


def mod97_ok(iban):
    s = iban.replace(" ", "")
    n = "".join(str(int(c, 36)) for c in s[4:] + s[:4])
    return int(n) % 97 == 1


# The IBANs meant to be valid must pass mod-97; the "typo" and "invalid" ones must not.
for k, v in IB.items():
    assert mod97_ok(v) == (k not in ("beta_typo", "invalid")), (k, v)


def e(s):
    return html.escape(s, quote=True)


def badge(kind, text):
    return f'<span class="badge badge--{kind}">{e(text)}</span>'


def page(L):
    b = L["base"]
    apps = APPS.format(v="18.0")
    anchors = {"en": ("how", "payments", "price"), "es": ("como", "pagos", "precio"), "ca": ("com", "pagaments", "preu")}[L["lang"]]
    a_how, a_pay, a_price = anchors
    langs = [("es", "ES", "es/"), ("ca", "CA", "ca/"), ("en", "EN", "")]
    lang_links = "".join(
        f'<a href="{b}{p or "./"}" lang="{c}" hreflang="{c}"{" aria-current=\"page\"" if c == L["lang"] else ""}>{t}</a>'
        for c, t, p in langs)
    nav = "".join(f'<a class="link {cls}" href="{href}">{e(txt)}</a>' for href, txt, cls in L["nav"])
    f = L["frame"]
    res = L["result"]

    # ---------- hero ----------
    frame1 = f"""<div class="reel__frame reel__frame--live" data-ui>
      <div class="ui-card result-frame">
        <div class="result-frame__top"><span>{e(f['top'])}</span><span>ORIVEXY Verify</span></div>
        <div class="result-frame__pair">
          <div><span class="ui-label">{e(f['mine'])}</span><strong>{e(f['mine_name'])}</strong><span class="iban">{IB['hero']}</span></div>
          <div><span class="ui-label">{e(f['cert'])}</span><strong>{e(f['cert_name'])}</strong><span class="iban">{IB['hero']}</span></div>
        </div>
        <div class="result-frame__note">{badge('other', f['badge'])}<span>{e(f['note'])}</span></div>
      </div>
    </div>"""
    reel = f"""<div class="reel" role="group" aria-label="{e(L['reel_label'])}">
    <div class="reel__track">
    <div class="reel__frame is-far"><img src="{b}img/web-reel-certificado.jpg" width="1008" height="567" alt="{e(L['alt_cert'])}"></div>
    {frame1}
    <div class="reel__frame is-far"><img src="{b}img/web-reel-odoo.jpg" width="1008" height="567" alt="{e(L['alt_odoo'])}"></div>
    <div class="reel__frame is-far"><video src="{b}img/web-clip-validacion.mp4" poster="{b}img/web-clip-validacion.jpg" muted loop playsinline preload="metadata" aria-label="{e(L['alt_clip'])}"></video></div>
    </div>
  </div>"""

    # ---------- how it works ----------
    h = L["how"]
    read_rows = "".join(f'<div class="read-list__row"><span class="iban">{IB[k]}</span><span>{e(n)}</span></div>' for k, n in h[0]["rows"])
    batch = "\n".join(f"{IB[k]} | {n}" for k, n in L["batch"])
    table_rows = "".join(
        f'<tr><td class="iban">{IB[k]}</td><td>{e(m)}</td><td>{e(c)}</td><td>{badge(r, res[r])}</td><td>{e(n)}</td></tr>'
        for k, m, c, r, n in L["table"])
    head_cells = "".join(f"<th scope=\"col\">{e(x)}</th>" for x in L["table_head"])

    # ---------- states ----------
    R = L["review"]
    pair = (f'<div><span class="ui-label">{e(R["mine"])}</span><strong>{e(R["mine_name"])}</strong><span class="iban ui-label">{IB["juan"]}</span></div>'
            f'<div><span class="ui-label">{e(R["cert"])}</span><strong>{e(R["cert_name"])}</strong><span class="iban ui-label">{IB["juan"]}</span></div>')
    states = f"""
    <div class="states__row" data-reveal>
      <p class="states__word">{e(L['states'][0])}</p>
      <div class="states__copy" data-ui><div class="ui-card review-row">
        <div class="review-row__main">{pair}<span>{badge('review', res['review'])}</span></div>
        <p class="review-row__log">{badge('missing', R['pending'])} &nbsp;{e(R['why'])}</p>
        <div class="review-row__actions"><span class="ui-btn" aria-hidden="true">{e(R['start'])}</span></div>
      </div></div>
    </div>
    <div class="states__row" data-reveal data-review-live>
      <p class="states__word">{e(L['states'][1])}</p>
      <div class="states__copy" data-ui><div class="ui-card review-row">
        <div class="review-row__main">{pair}<span data-review-status class="badge badge--review">{e(R['inreview'])}</span></div>
        <p class="review-row__log">{e(R['why'])}</p>
        <div data-review-actions>
          <label class="ui-label" for="review-note">{e(R['note_label'])}</label>
          <textarea id="review-note" rows="2">{e(R['note'])}</textarea>
          <div class="review-row__actions" style="margin-top:8px"><button type="button" class="ui-btn" data-resolve>{e(R['resolve'])}</button><button type="button" class="ui-btn ui-btn--ghost">{e(R['dismiss'])}</button><span class="review-row__log" data-review-msg role="status"></span></div>
        </div>
      </div></div>
    </div>
    <div class="states__row" data-reveal id="review-done">
      <p class="states__word">{e(L['states'][2])}</p>
      <div class="states__copy" data-ui><div class="ui-card review-row">
        <div class="review-row__main">{pair}<span>{badge('ok', R['resolved'])}</span></div>
        <p class="review-row__note">{e(R['done_note'])}</p>
        <p class="review-row__log">{e(R['done_log'])}</p>
      </div></div>
    </div>"""

    # ---------- lab ----------
    lab_blocks = []
    controls = [
        f'<div class="lab__control"><label for="lab-holder">{e(L["lab_holder_label"])}</label><input class="field" id="lab-holder" value="{e(L["lab_holder"])}" autocomplete="off" spellcheck="false"></div>',
        '<div class="lab__control"><div class="seg" role="group" aria-label="' + e(L["lab"][1][0]) + '">'
        + "".join(f'<button type="button" data-legal="{x}" aria-pressed="false">{x}</button>' for x in ("S.L.", "S.A.", "GmbH")) + "</div></div>",
        '<div class="lab__control"><div class="seg" role="group" aria-label="' + e(L["lab"][2][0]) + '">'
        f'<button type="button" data-typo="0" aria-pressed="true">{e(L["lab_typo"][0])}</button><button type="button" data-typo="1" aria-pressed="false">{e(L["lab_typo"][1])}</button></div></div>',
        f'<div class="lab__control"><label class="switch"><input type="checkbox" id="lab-cert" checked> {e(L["lab_cert"])}</label></div>',
    ]
    for (t, p), c in zip(L["lab"], controls):
        lab_blocks.append(f'<div class="lab__block" data-reveal><h3>{e(t)}</h3><p>{e(p)}</p>{c}</div>')
    C = L["lab_card"]
    lab_card = f"""<div class="ui-card check" data-ui aria-live="polite">
        <div class="check__head"><span>{e(C['head'])}</span><span class="ui-label">ORIVEXY Verify</span></div>
        <div class="check__row"><span class="ui-label">{e(C['iban'])}</span><strong class="iban" data-out="iban">{IB['beta']}</strong></div>
        <div class="check__row"><span class="ui-label">{e(C['mine'])}</span><strong data-out="mine">{e(L['lab_holder'])}</strong></div>
        <div class="check__row"><span class="ui-label">{e(C['cert'])}</span><strong data-out="cert">Ficticia Beta 2024 SL</strong></div>
        <ul class="check__list">
          <li><span>{e(C['c_format'])}</span><span data-out="c-format" class="yes">{e(L['js']['yes'])}</span></li>
          <li><span>{e(C['c_in'])}</span><span data-out="c-in" class="yes">{e(L['js']['yes'])}</span></li>
          <li><span>{e(C['c_holder'])}</span><span data-out="c-holder" class="yes">{e(L['js']['how']['normalised'])}</span></li>
        </ul>
        <div class="check__verdict"><span data-out="badge" class="badge badge--ok">{e(res['ok'])}</span><span class="check__why" data-out="why">{e(L['js']['why']['punct'])}</span></div>
        <p class="check__foot">{e(C['foot'])}</p>
      </div>"""

    # ---------- proof ----------
    proof = "".join(f'<li><a class="link" href="{APPS.format(v=v)}">Odoo {v[:2]}</a></li>' for v in VERSIONS)

    # ---------- payments ----------
    tabs, panels = [], []
    for k, (ini, name, role, items) in enumerate(L["pay_people"]):
        sel = k == 0
        tabs.append(f'<button class="pay__tab" role="tab" id="tab-{ini}" aria-controls="panel-{ini}" aria-selected="{str(sel).lower()}" tabindex="{0 if sel else -1}"><b>{e(name)}</b><span>{e(role)}</span></button>')
        bands = "".join(
            f'<li class="pay__band"><span class="pay__time">{t}</span><span class="pay__what"><b>{e(w)}</b><span>{e(n)}</span></span><span class="avatar avatar--{ini}" aria-hidden="true">{name[0]}</span></li>'
            for t, w, n in items)
        panels.append(f'<ol class="pay__bands" role="tabpanel" id="panel-{ini}" aria-labelledby="tab-{ini}"{"" if sel else " hidden"}>{bands}</ol>')

    # ---------- install ----------
    tiles = "".join(
        f'<a class="inst__tile" href="{b}odoo-sh/" data-reveal style="--d:{i}"><div class="inst__pic"><img src="{b}img/web-instalar-{i + 1}.jpg" width="960" height="540" loading="lazy" alt="{e(L["inst_alt"].format(t=w + " · " + d))}"></div>'
        f'<div class="inst__strip"><b>{e(w)}</b><span>{t} · {e(d)}</span></div></a>'
        for i, (t, w, d) in enumerate(L["inst_tiles"]))
    server_steps = "".join(f"<li>{e(s)}</li>" for s in L["inst_server"])

    # ---------- price ----------
    num = f'<span>{L["price_num"]}</span><span class="price__cur">{L["price_cur"]}</span>' if L["cur_after"] else f'<span class="price__cur">{L["price_cur"]}</span><span>{L["price_num"]}</span>'
    price_list = "".join(f"<li>{e(x)}</li>" for x in L["price_list"])
    price_alt = L["price_alt"].format(mail=MAIL, subj=e(L["price_alt_subj"]).replace(" ", "%20"))

    # ---------- faq ----------
    faq = "".join(f'<details name="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in L["faq"])

    # ---------- contact ----------
    rows = []
    for label, val in L["contact_rows"]:
        if val == "mail":
            v = f'<a class="link" href="mailto:{MAIL}">{MAIL}</a>'
        elif val == "apps":
            v = f'<a class="link" href="{apps}">apps.odoo.com · orivexy_validator</a>'
        else:
            v = e(val)
        rows.append(f"<div><dt>{e(label)}</dt><dd>{v}</dd></div>")

    # ---------- footer ----------
    foot_nav = "".join(f'<li><a href="{apps if h == "APPS" else b + h}">{e(t)}</a></li>' for h, t in L["foot_nav"])

    i18n = dict(L["js"])
    i18n.update({"result": res, "mail": MAIL, "mailSubject": L["mail_subject"],
                 "lab": {"iban": IB["beta"], "ibanTypo": IB["beta_typo"], "certHolder": "Ficticia Beta 2024 SL", "noCert": "—"}})
    i18n["review"]["by"] = i18n["review"].get("by", "")

    canonical = SITE + L["path"]
    ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "ORIVEXY Verify",
          "applicationCategory": "BusinessApplication", "operatingSystem": "Odoo 15–20 (Odoo.sh, Community, Enterprise)",
          "description": L["desc"], "inLanguage": L["lang"], "url": canonical, "image": SITE + "img/web-resultados-odoo.jpg",
          "author": {"@type": "Person", "name": "Eric Muñiz Genebriera"},
          "offers": {"@type": "Offer", "price": "449.99", "priceCurrency": "EUR", "url": apps, "availability": "https://schema.org/InStock"}}

    out = f"""<!DOCTYPE html>
<html lang="{L['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(L['title'])}</title>
<meta name="description" content="{e(L['desc'])}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{SITE}">
<link rel="alternate" hreflang="es" href="{SITE}es/">
<link rel="alternate" hreflang="ca" href="{SITE}ca/">
<link rel="alternate" hreflang="x-default" href="{SITE}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{L['og_locale']}">
<meta property="og:title" content="{e(L['title'])}">
<meta property="og:description" content="{e(L['desc'])}">
<meta property="og:image" content="{SITE}img/web-resultados-odoo.jpg">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0f2747">
<link rel="icon" href="{b}img/web-simbolo.svg" type="image/svg+xml">
<link rel="preload" href="{b}assets/fonts/stack-sans-text-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{b}assets/fonts/stack-sans-headline-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{b}assets/web.css?v={VER}">
<script>document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<main>
<section class="hero" aria-labelledby="titulo">
  <div class="hero__stage">
    <header class="top">
      <a class="brand" href="{b or './'}{'' if not L['path'] else L['path']}"><img src="{b}img/web-simbolo.svg" width="30" height="30" alt="">ORIVEXY Verify</a>
      <nav aria-label="{e(L['nav'][0][1])}">{nav}<span class="langs">{lang_links}</span><a class="button button--small" href="{b}demo/">{e(L['action'])}</a></nav>
    </header>
    <div class="hero__body">
      <h1 class="hero__title" id="titulo"><span class="hero__a" data-rise>{e(L['hero_a'])}</span> <span class="hero__b" data-rise style="--d:2">{e(L['hero_b'])}</span></h1>
      {reel}
      <div class="hero__foot">
        <p class="hero__sub" data-rise style="--d:3">{e(L['hero_sub'])}</p>
        <div class="hero__actions" data-rise style="--d:4"><a class="button" href="{b}demo/">{e(L['action'])}</a><a class="link" href="{apps}">{e(L['hero_link'])}</a></div>
      </div>
    </div>
  </div>
</section>

<section class="wrap section" aria-labelledby="intro-t">
  <h2 class="intro__title" id="intro-t" data-reveal>{e(L['intro_title'])}</h2>
  <div class="grid">
    <p class="intro__lead" data-reveal style="--d:1">{e(L['intro_lead'])}</p>
    <div class="intro__cols">{''.join(f'<p data-reveal style="--d:{i + 2}"><b>{e(t)}</b> {e(x)}</p>' for i, (t, x) in enumerate(L['intro_cols']))}</div>
  </div>
</section>

<section class="wrap section how" id="{a_how}" aria-labelledby="how-t">
  <div class="how__inner">
    <h2 class="head how__title" id="how-t" data-reveal>{e(L['how_title'])}</h2>
    <div class="how__step" data-reveal>
      <p class="how__say">{e(h[0]['say'])}</p>
      <div class="how__call" data-ui><div class="file-chip"><span class="file-chip__icon">PDF</span><span><strong>{e(h[0]['file'])}</strong><br><span class="ui-label">{e(h[0]['hint'])}</span></span></div></div>
      <div class="how__resp" data-ui><div class="ui-card read-list"><div class="read-list__head"><span>{e(h[0]['read'])}</span>{badge('ok', 'OK')}</div>{read_rows}</div></div>
    </div>
    <div class="how__step" data-reveal>
      <p class="how__say">{e(h[1]['say'])}</p>
      <div class="how__call" data-ui><pre class="batch-lines" aria-label="{e(h[1]["hint"])}">IBAN | {"Holder" if L["lang"] == "en" else "Titular"}
{e(batch)}</pre><span class="ui-label">{e(h[1]['hint'])}</span></div>
      <div class="how__resp" data-ui><div class="ui-card read-list"><div class="read-list__head"><span>{e(h[1]['count'])}</span>{badge('ok', 'OK')}</div></div></div>
    </div>
    <div class="how__step how__step--wide" data-reveal>
      <p class="how__say">{e(h[2]['say'])}</p>
      <div class="how__call" data-ui><span class="validate-btn">{e(h[2]['button'])}</span></div>
      <div class="how__resp" data-ui><div class="ui-card results"><table><thead><tr>{head_cells}</tr></thead><tbody>{table_rows}</tbody></table><div class="results__counts ui-label">{e(L['counts'])}</div></div></div>
    </div>
  </div>
</section>

<section class="wrap section grid" aria-labelledby="states-t">
  <h2 class="head states__title" id="states-t" data-reveal>{e(L['states_title'])}</h2>
  {states}
</section>

<section class="wrap lab" data-lab aria-labelledby="lab-t">
  <h2 class="lab__title" id="lab-t" data-reveal>{e(L['lab_title'])}</h2>
  <div class="lab__field">{lab_card}</div>
  <div class="lab__text">
    {''.join(lab_blocks)}
  </div>
</section>

<section class="wrap proof" aria-labelledby="proof-t">
  <h2 id="proof-t">{e(L['proof_title'])}</h2>
  <ul>{proof}</ul>
  <p class="proof__note">{e(L['proof_note'])}</p>
</section>

<section class="wrap section" id="{a_pay}" aria-labelledby="pay-t">
  <div class="pay__head">
    <h2 class="pay__title" id="pay-t" data-reveal><span class="soft">{e(L['pay_soft'])}</span><span>{e(L['pay_title'])}</span></h2>
    <a class="button button--ink" href="mailto:{MAIL}?subject={e(L['pay_button']).replace(' ', '%20')}%20%C2%B7%20ORIVEXY%20Verify" data-reveal>{e(L['pay_button'])}</a>
  </div>
  <p class="pay__intro" data-reveal>{e(L['pay_intro'])}</p>
  <div class="pay__body">
    <div class="pay__tabs" role="tablist" aria-label="{e(L['pay_title'])}" aria-orientation="vertical">{''.join(tabs)}</div>
    <div>{''.join(panels)}</div>
  </div>
  <div class="pay__shots">
    <figure data-reveal><img src="{b}img/web-pagos-tablero.jpg" width="1600" height="894" loading="lazy" alt="{e(L['pay_alt1'])}"><figcaption>{e(L['pay_shot1'])}</figcaption></figure>
    <figure data-reveal style="--d:1"><img src="{b}img/web-pagos-relacionado.jpg" width="1600" height="950" loading="lazy" alt="{e(L['pay_alt2'])}"><figcaption>{e(L['pay_shot2'])}</figcaption></figure>
  </div>
</section>

<section class="wrap section" aria-labelledby="inst-t">
  <div class="inst__head">
    <h2 class="head" id="inst-t" data-reveal>{e(L['inst_title'])}</h2>
    <p data-reveal style="--d:1">{e(L['inst_sub'])}</p>
  </div>
  <div class="inst__tiles">{tiles}</div>
  <div class="inst__more">
    <div data-reveal><h3>{e(L['inst_server_t'])}</h3><ol>{server_steps}</ol><p class="small muted" style="margin-top:12px">{e(L['inst_server_note'])}</p></div>
    <div data-reveal style="--d:1"><h3>{e(L['inst_win_t'])}</h3><p>{e(L['inst_win'])}</p>
      <div class="code"><pre><code id="cmd">git add orivexy_validator && git commit -m "ORIVEXY Verify" && git push</code></pre><button type="button" data-copy="cmd">{e(L['js']['copy'])}</button></div>
      <div class="price__actions"><a class="button" href="{apps}">{e(L['inst_dl'])}</a><a class="link" href="{b}odoo-sh/">{e(L['inst_win_more'])}</a></div></div>
  </div>
</section>

<section class="wrap price" id="{a_price}" aria-labelledby="price-t">
  <div class="price__text">
    <h2 id="price-t">{e(L['price_title'])}</h2>
    <p>{e(L['price_p'])}</p>
  </div>
  <div class="price__fig">
    <p class="price__num nums">{num}<span class="price__per">{e(L['price_per'])}</span></p>
    <img class="price__mark" src="{b}img/web-simbolo.svg" width="100" height="100" alt="">
    <ul class="price__list">{price_list}</ul>
    <p class="price__alt">{price_alt}</p>
    <div class="price__actions"><a class="button" href="{apps}">{e(L['price_button'])}</a></div>
  </div>
</section>

<section class="wrap section faq" aria-labelledby="faq-t">
  <h2 class="faq__title" id="faq-t">{e(L['faq_title'])}</h2>
  <div class="faq__list">{faq}</div>
</section>

<section class="wrap contact" aria-labelledby="contact-t">
  <div class="contact__inner">
    <h2 id="contact-t" data-reveal><span class="soft">{e(L['contact_soft'])}</span>{e(L['contact_title'])}</h2>
    <form data-contact data-reveal style="--d:1">
      <label class="sr-only" for="contact-q">{e(L['contact_ph'])}</label>
      <input id="contact-q" name="q" placeholder="{e(L['contact_ph'])}" autocomplete="off">
      <button type="submit" aria-label="{e(L['contact_btn'])}"><svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 10h13M11 4l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
    </form>
    <p class="contact__hint">{e(L['contact_hint'])}</p>
    <dl>{''.join(rows)}</dl>
  </div>
</section>
</main>

<footer class="foot">
  <div class="tile tile--say"><p>{e(L['foot_say'])}</p><p class="foot__legal">{e(L['foot_legal'])} · <a href="mailto:{MAIL}">{MAIL}</a></p></div>
  <nav class="tile tile--nav" aria-label="ORIVEXY Verify"><ul>{foot_nav}</ul></nav>
  <div class="tile tile--time"><span class="small muted">{e(L['foot_time'])}</span><strong data-clock></strong></div>
  <div class="tile tile--mail"><a href="mailto:{MAIL}">{MAIL}</a></div>
  <div class="tile tile--word" aria-hidden="true"><span>ORIVEXY Verify</span></div>
  <a class="tile tile--go" href="{b}demo/"><p>{e(L['foot_go'])}</p><svg width="56" height="56" viewBox="0 0 56 56" aria-hidden="true"><path d="M14 42L42 14M20 14h22v22" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="square"/></svg></a>
</footer>
<script type="application/json" id="i18n">{json.dumps(i18n, ensure_ascii=False)}</script>
<script src="{b}assets/web.js?v={VER}" defer></script>
</body>
</html>
"""
    return out


def main():
    for L in LANGS:
        dest = ROOT / L["path"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page(L), encoding="utf-8", newline="\n")
        print("ok", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
