# -*- coding: utf-8 -*-
"""
Генерирует страницы тортов site/desktop/cakes/*.html и site/mobile/cakes/*.html
по данным calculator/build_cakes.py (поле name, desc, subtitle, fillings, type, id).

Также перезаписывает site/desktop/index.html и site/mobile/index.html —
порядок обложек как в CATALOG_ORDER, подписи = name из документа.

Запуск из корня репозитория kosmos_calc:
  python site/build_site_pages.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BC = ROOT / "calculator" / "build_cakes.py"
PH = SITE / "photos"

# Порядок на главной (как договорились с заказчиком), без fuji
CATALOG_ORDER = [
    "fairy-cake", "tiramisu", "lumiere", "letter", "big-cherry-fairy-cake",
    "swan-lake", "babylon", "love-in-mood", "dancing-queen", "secret-garden",
    "chapito", "anna", "bell", "bohemian-rhapsody", "totoro", "kelly",
    "la-la-land", "darcy", "shine-bright", "green-day", "orpheus",
    "cherry-orchard", "elizabeth", "berry-fields", "kuinji", "faberge",
    "sailor-moon", "apollo", "blueberry-hill",
]


def load_cakes():
    src = BC.read_text(encoding="utf-8")
    cut = src.index("#  ГЕНЕРАЦИЯ")
    ns = {"__file__": str(BC), "__name__": "build_cakes_cat"}
    exec(compile(src[:cut], str(BC), "exec"), ns)
    return ns["CAKES"]


def photo_paths(cid: str) -> tuple[list[str], list[str]]:
    """Десктоп: cover + slice-…; мобилка: slice-… + cover в конце."""
    d = PH / cid
    cover = d / "cover.jpg"
    slices = []
    if d.is_dir():
        for p in sorted(d.glob("slice-*.jpg")):
            slices.append(p.name)
    rel = f"../../photos/{cid}"
    desk: list[str] = []
    if cover.exists():
        desk.append(f"{rel}/cover.jpg")
    for s in slices:
        desk.append(f"{rel}/{s}")
    mob = [f"{rel}/{s}" for s in slices]
    if cover.exists():
        mob.append(f"{rel}/cover.jpg")
    if not desk:
        desk = ["../../photos/fairy-cake/cover.jpg"]
    if not mob:
        mob = ["../../photos/fairy-cake/cover.jpg"]
    return desk, mob


def desktop_photos_html(cid: str, cname: str) -> str:
    paths, _ = photo_paths(cid)
    lines = []
    for i, p in enumerate(paths):
        if i == 0 and "cover" in p:
            alt = cname
        else:
            alt = f"{cname} — деталь"
        lines.append(f'    <img class="photo" src="{html.escape(p)}" alt="{html.escape(alt)}">')
    return "\n".join(lines)


def mobile_photos_html(cid: str, cname: str) -> str:
    _, paths = photo_paths(cid)
    lines = []
    for i, p in enumerate(paths):
        if "cover" in p.split("/")[-1]:
            alt = f"{cname} — обложка"
        else:
            alt = f"{cname} — деталь"
        load = "eager" if i == 0 else "lazy"
        lines.append(
            f'    <img src="{html.escape(p)}" alt="{html.escape(alt)}" loading="{load}">'
        )
    return "\n".join(lines)


def subtitle_html(cake: dict) -> str:
    parts = [html.escape(cake.get("subtitle") or "")]
    if cake.get("note"):
        parts.append(html.escape(cake["note"]))
    return " ".join(x for x in parts if x).strip()


DESKTOP_HEAD = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1280">
<title>__PAGE_TITLE__</title>
<link rel="stylesheet" href="../../style.css">
<style>
  /* десктоп-вариант: жёстко 3 колонки даже в узком iframe-превью */
  @media (max-width:900px){
    .cake-page{grid-template-columns:1fr 1fr 1fr;grid-template-rows:none}
    .cake-col{height:100%}
    .col-photo,.col-third{overflow-y:auto}
    .col-info{padding:0 22px 24px;overflow-y:auto;display:flex;flex-direction:column;align-items:center;gap:10px}
    .col-info .cake-title{
      position:sticky;top:0;z-index:5;background:var(--bg);
      font-size:56px;line-height:.7;margin:0 -22px;padding:18px 22px 14px;width:calc(100% + 44px);
    }
    .cake-title .word{line-height:.7;padding-bottom:.05em}
    .col-info .calc-frame{height:720px;flex:none}
    .col-third{overflow:hidden;height:100%;position:relative}
    .col-third .col-fillings,.col-third .col-delivery{position:absolute;inset:0;height:auto;overflow-y:auto;transition:transform .4s ease}
    .col-third .col-delivery{display:flex;transform:translateX(100%)}
    .cake-page.is-delivery .col-third .col-delivery{transform:translateX(0)}
    .cake-page.is-delivery .col-third .col-fillings{display:block;transform:translateX(-20%);opacity:.45}
    .delivery-back{position:absolute;width:64px;height:64px}
    .delivery-back svg{width:42px;height:42px}
  }
</style>
</head>
<body>

<button class="menu-btn" id="menu-toggle" aria-label="меню" type="button">
  <svg viewBox="0 0 54 65" xmlns="http://www.w3.org/2000/svg">
    <path d="M21.5183 26.4696C21.6112 26.4696 21.7061 26.4146 21.7357 26.3215C22.5312 23.2215 24.6898 15.7815 26.055 13.0814C27.8169 9.58359 30.7331 4.22365 35.8564 2.85457C44.0267 0.670814 49.705 4.96003 50.952 9.56666C51.9818 13.3692 50.0173 17.6881 47.5295 20.1067C45.0417 22.5317 37.9074 25.8348 32.9023 28.3847C27.397 31.1863 24.8164 29.8786 30.9694 31.4275C38.0108 33.1966 47.3818 32.5998 52.2856 43.9863C53.7437 47.3825 53.9146 52.9371 52.3553 56.4202C49.5087 62.8127 39.4668 67.9759 31.1003 61.45C26.7176 58.0305 24.2931 51.7712 23.4132 45.8018C23.0165 43.1568 22.3286 37.6635 22.1345 36.1611C22.1113 35.9897 21.9467 35.8797 21.7757 35.9114H21.7378C21.5901 35.9432 21.4951 36.0765 21.5035 36.2246C21.7209 38.7512 21.7694 40.262 21.9002 42.3273C22.1429 45.9648 22.6324 49.5811 22.835 53.2186C22.9047 54.5644 22.6557 56.0117 22.2336 57.311C19.8935 64.5881 11.9722 66.2619 6.8025 60.629C3.83149 57.3893 2.10965 53.5085 1.39222 49.2531C-0.93944 35.3951 -0.667231 21.7339 4.72195 8.51076C5.30645 7.06338 5.89095 5.56945 6.81939 4.32521C8.65939 1.87695 11.3266 -0.376626 14.9833 0.0529308C18.5156 0.467676 20.6912 2.71279 21.5099 5.93764C22.0627 8.14468 21.9066 10.5549 21.877 12.8783C21.8538 14.3955 21.4318 24.1293 21.2145 26.2348C21.206 26.3511 21.2841 26.4464 21.3938 26.4527C21.4318 26.4527 21.4803 26.4527 21.5183 26.4612H21.5099L21.5183 26.4696Z"/>
  </svg>
  <span class="menu-label">меню</span>
</button>
<ul class="menu-list" id="menu-list">
  <li><a href="../index.html">каталог</a></li>
  <li><a href="#">доставка</a></li>
  <li><a href="#">о нас</a></li>
</ul>

<div class="cake-page">

  <section class="cake-col col-photo" aria-label="фото торта">
__PHOTOS_DESKTOP__
  </section>

  <section class="cake-col col-info" aria-label="параметры торта">
    <h1 class="cake-title">__H1__</h1>
    <p class="cake-desc">__DESC__</p>
    <p class="cake-sub">__SUB__</p>
    <iframe class="calc-frame"
            src="__CALC_SRC__"
            title="__IFRAME_TITLE__"></iframe>
    <img class="end-bow" src="../../assets/bow.svg" alt="" aria-hidden="true">
  </section>

  <section class="cake-col col-third" aria-label="третья колонка">
    <div class="col-fillings" id="fillings-col" data-fillings="__FILL__"></div>
    <div class="col-delivery" id="delivery-col" aria-hidden="true">
      <button class="delivery-back" id="delivery-back" type="button" aria-label="назад к начинкам">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M14.7 4.3a1 1 0 0 1 0 1.4L9.4 11H20a1 1 0 1 1 0 2H9.4l5.3 5.3a1 1 0 1 1-1.4 1.4l-7-7a1 1 0 0 1 0-1.4l7-7a1 1 0 0 1 1.4 0Z"/>
        </svg>
      </button>
      <iframe class="delivery-frame"
              src="../../../calculator/delivery/index.html"
              title="доставка"></iframe>
    </div>
  </section>

</div>

<script src="../../fillings/data.js"></script>
<script>
__SHARED_JS__
</script>

</body>
</html>
"""

MOBILE_BODY = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__PAGE_TITLE__</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body class="mob-page">

<button class="menu-btn" id="menu-toggle" aria-label="меню" type="button">
  <svg viewBox="0 0 54 65" xmlns="http://www.w3.org/2000/svg">
    <path d="M21.5183 26.4696C21.6112 26.4696 21.7061 26.4146 21.7357 26.3215C22.5312 23.2215 24.6898 15.7815 26.055 13.0814C27.8169 9.58359 30.7331 4.22365 35.8564 2.85457C44.0267 0.670814 49.705 4.96003 50.952 9.56666C51.9818 13.3692 50.0173 17.6881 47.5295 20.1067C45.0417 22.5317 37.9074 25.8348 32.9023 28.3847C27.397 31.1863 24.8164 29.8786 30.9694 31.4275C38.0108 33.1966 47.3818 32.5998 52.2856 43.9863C53.7437 47.3825 53.9146 52.9371 52.3553 56.4202C49.5087 62.8127 39.4668 67.9759 31.1003 61.45C26.7176 58.0305 24.2931 51.7712 23.4132 45.8018C23.0165 43.1568 22.3286 37.6635 22.1345 36.1611C22.1113 35.9897 21.9467 35.8797 21.7757 35.9114H21.7378C21.5901 35.9432 21.4951 36.0765 21.5035 36.2246C21.7209 38.7512 21.7694 40.262 21.9002 42.3273C22.1429 45.9648 22.6324 49.5811 22.835 53.2186C22.9047 54.5644 22.6557 56.0117 22.2336 57.311C19.8935 64.5881 11.9722 66.2619 6.8025 60.629C3.83149 57.3893 2.10965 53.5085 1.39222 49.2531C-0.93944 35.3951 -0.667231 21.7339 4.72195 8.51076C5.30645 7.06338 5.89095 5.56945 6.81939 4.32521C8.65939 1.87695 11.3266 -0.376626 14.9833 0.0529308C18.5156 0.467676 20.6912 2.71279 21.5099 5.93764C22.0627 8.14468 21.9066 10.5549 21.877 12.8783C21.8538 14.3955 21.4318 24.1293 21.2145 26.2348C21.206 26.3511 21.2841 26.4464 21.3938 26.4527C21.4318 26.4527 21.4803 26.4527 21.5183 26.4612H21.5099L21.5183 26.4696Z"/>
  </svg>
  <span class="menu-label">меню</span>
</button>
<ul class="menu-list" id="menu-list">
  <li><a href="../index.html">каталог</a></li>
  <li><a href="#">доставка</a></li>
  <li><a href="#">о нас</a></li>
</ul>

<section class="mob-photos-wrap" aria-label="фото торта">
  <div class="mob-photos" id="mob-photos">
__PHOTOS_MOBILE__
  </div>
  <p class="mob-swipe-hint">листайте фото&nbsp;→</p>
</section>

<header class="mob-head">
  <h1 class="cake-title">__H1__</h1>
  <p class="cake-desc">__DESC__</p>
  <p class="cake-sub">__SUB__</p>
</header>

<div class="mob-fill-head">
  <h2 class="mob-section-title">Что внутри?</h2>
  <p class="mob-section-hint">листайте вправо — нажмите на начинку, чтобы узнать больше</p>
</div>

<section class="mob-fillings" id="mob-fillings" data-fillings="__FILL__" aria-label="начинки"></section>

<iframe class="mob-calc-frame"
        src="__CALC_SRC__"
        title="__IFRAME_TITLE__"></iframe>

<iframe class="mob-delivery-frame" id="mob-delivery"
        src="../../../calculator/delivery/index.html"
        title="доставка"></iframe>

<img class="end-bow" src="../../assets/bow.svg" alt="" aria-hidden="true">

<script src="../../fillings/data.js"></script>
<script>
__SHARED_JS_MOBILE__
</script>

</body>
</html>
"""

SHARED_JS = r"""  const menuBtn  = document.getElementById('menu-toggle');
  const menuList = document.getElementById('menu-list');
  menuBtn.addEventListener('click', (e) => { e.stopPropagation(); menuList.classList.toggle('is-open'); });
  document.addEventListener('click', (e) => {
    if (!menuList.contains(e.target) && e.target !== menuBtn && !menuBtn.contains(e.target)) menuList.classList.remove('is-open');
  });

  (function fitCakeTitle(){
    const title = document.querySelector('.cake-title');
    if (!title) return;
    const raw = title.textContent.trim();
    title.innerHTML = raw.split(/\s+/).map(w => `<span class="word">${w}</span>`).join('');
    const MAX = 160, MIN = 28, TARGET = 0.96;
    function fit(){
      const cw = title.clientWidth;
      if (!cw) return;
      title.querySelectorAll('.word').forEach(word => {
        word.style.fontSize = MAX + 'px';
        const w = word.scrollWidth;
        if (!w) return;
        let size = MAX * (cw * TARGET / w);
        size = Math.max(MIN, Math.min(MAX, size));
        word.style.fontSize = size + 'px';
      });
    }
    fit();
    window.addEventListener('resize', fit);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit).catch(()=>{});
  })();

  const SPARKLE = '<svg viewBox="0 0 100 100"><path d="M50 4 C52 38, 62 48, 96 50 C62 52, 52 62, 50 96 C48 62, 38 52, 4 50 C38 48, 48 38, 50 4 Z"/></svg>';
  const CLOSE_X  = '<svg viewBox="0 0 22 21" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' +
    '<path d="M0.877209 0.877275C2.04698 -0.292499 3.94367 -0.292351 5.11354 0.877275L10.5657 6.32942L16.012 0.883134C17.1818 -0.286425 19.0785 -0.286409 20.2483 0.883134C21.4181 2.05291 21.4179 3.9496 20.2483 5.11946L14.802 10.5658L20.1174 15.8812C21.2873 17.051 21.2873 18.9477 20.1174 20.1175C18.9476 21.2872 17.0509 21.2873 15.8811 20.1175L10.5657 14.8021L5.2444 20.1234C4.07455 21.2932 2.17792 21.2932 1.00807 20.1234C-0.161545 18.9535 -0.161701 17.0568 1.00807 15.887L6.32936 10.5658L0.877209 5.1136C-0.292372 3.94378 -0.292433 2.04706 0.877209 0.877275Z"/>' +
    '</svg>';
  const MAX_OPEN = 3;
  const openStack = [];
  const CLASS_SLUG = {
    'космос база':'base', 'космос классика':'classic', 'космос люкс':'lux'
  };

  function buildBubble(name){
    const f = (window.KOSMOS_FILLINGS || {})[name];
    if (!f) return null;
    const bubble = document.createElement('div');
    bubble.className = 'filling-bubble';
    bubble.insertAdjacentHTML('beforeend',
      `<span class="spark left"  aria-hidden="true">${SPARKLE}</span>` +
      `<span class="spark right" aria-hidden="true">${SPARKLE}</span>`);
    const h3 = document.createElement('h3');
    if (f.display){
      h3.innerHTML = f.display;
      const lines = (f.display.match(/<br\s*\/?>/gi) || []).length + 1;
      if (lines === 2) bubble.classList.add('is-title-2');
      if (lines >= 3) bubble.classList.add('is-title-3');
    } else {
      h3.textContent = name;
    }
    bubble.appendChild(h3);
    const desc = document.createElement('p');
    desc.className = 'desc';
    desc.textContent = f.desc;
    bubble.appendChild(desc);
    const slug = CLASS_SLUG[f.cls];
    if (slug){
      const cls = document.createElement('img');
      cls.className = 'bb-class';
      cls.src = `../../assets/class-${slug}.svg`;
      cls.alt = f.cls;
      bubble.appendChild(cls);
    }
    const price = document.createElement('p');
    price.className = 'bb-price';
    price.textContent = f.price;
    bubble.appendChild(price);
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'close';
    close.setAttribute('aria-label', 'закрыть');
    close.innerHTML = CLOSE_X;
    bubble.appendChild(close);
    return bubble;
  }
  function closeWrap(wrap){
    wrap.classList.remove('is-open');
    const b = wrap.querySelector('.filling-bubble');
    if (b) b.remove();
    const i = openStack.indexOf(wrap);
    if (i !== -1) openStack.splice(i, 1);
  }
  function openWrap(wrap, name){
    if (wrap.classList.contains('is-open')) return;
    if (openStack.length >= MAX_OPEN) closeWrap(openStack[0]);
    const bubble = buildBubble(name);
    if (!bubble) return;
    wrap.appendChild(bubble);
    wrap.classList.add('is-open');
    openStack.push(wrap);
    bubble.addEventListener('click', () => closeWrap(wrap));
  }

  function resolveFillings(raw){
    if (!raw) return [];
    const sets = window.KOSMOS_FILLING_SETS || {};
    const list = sets[raw] ? sets[raw] : raw.split(',').map(s => s.trim()).filter(Boolean);
    return typeof window.sortByCanonical === 'function' ? window.sortByCanonical(list) : list;
  }
  function buildSlice(name){
    const f = (window.KOSMOS_FILLINGS || {})[name];
    const wrap = document.createElement('div');
    wrap.className = 'slice-wrap';
    wrap.dataset.filling = name;
    const img = document.createElement('img');
    img.className = 'slice'; img.alt = name; img.loading = 'lazy';
    img.src = f && f.photo
      ? `../../fillings/photos/${f.photo}`
      : '../../photos/fairy-cake/slice-1.jpg';
    wrap.appendChild(img);
    const dot = document.createElement('button');
    dot.type = 'button'; dot.className = 'info-dot';
    dot.setAttribute('aria-label', name + ' — описание');
    dot.innerHTML = SPARKLE;
    wrap.appendChild(dot);
    dot.addEventListener('click', () => openWrap(wrap, name));
    return wrap;
  }

  const col = document.getElementById('fillings-col');
  resolveFillings(col.dataset.fillings).forEach(name => col.appendChild(buildSlice(name)));

  const page = document.querySelector('.cake-page');
  const deliveryCol = document.getElementById('delivery-col');
  window.addEventListener('message', (e) => {
    const d = e.data;
    if (d && typeof d === 'object' && d.type === 'kosmos-next'){
      page.classList.add('is-delivery');
      deliveryCol.setAttribute('aria-hidden','false');
    }
  });
  document.getElementById('delivery-back').addEventListener('click', () => {
    page.classList.remove('is-delivery');
    deliveryCol.setAttribute('aria-hidden','true');
  });
"""


def fix_mobile_js():
    """Мобильный скрипт: только fillings + scroll к доставке, без delivery overlay."""
    base = SHARED_JS
    # убрать блок desktop delivery
    base = re.sub(
        r"\n  const page = document\.querySelector\('\.cake-page'\);.*?deliveryCol\.setAttribute\('aria-hidden','true'\);\n  \}\);\n",
        "\n",
        base,
        flags=re.S,
    )
    base = base.replace(
        "const col = document.getElementById('fillings-col');",
        "const col = document.getElementById('mob-fillings');",
    )
    tail = """
  const dlv = document.getElementById('mob-delivery');
  window.addEventListener('message', (e) => {
    const d = e.data;
    if (d && typeof d === 'object' && d.type === 'kosmos-next'){
      dlv.scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
"""
    # fitCakeTitle mobile params
    base = base.replace("const MAX = 160, MIN = 28, TARGET = 0.96;", "const MAX = 200, MIN = 32, TARGET = 0.94;")
    return base + tail


SHARED_JS_MOBILE = fix_mobile_js()


def render_desktop(cake: dict) -> str:
    cid = cake["id"]
    typ = cake["type"]
    name = cake["name"]
    calc = f"../../../calculator/cakes-mobile/{typ}/{cid}.html"
    page_title = html.escape(f"{name} — kosmos")
    h1 = html.escape(name)
    desc = html.escape(cake.get("desc") or "")
    sub = subtitle_html(cake)
    fill = html.escape(cake.get("fillings") or "BASE")
    iframe_title = html.escape(f"калькулятор {name}")
    photos = desktop_photos_html(cid, name)
    return (
        DESKTOP_HEAD.replace("__PAGE_TITLE__", page_title)
        .replace("__PHOTOS_DESKTOP__", photos)
        .replace("__H1__", h1)
        .replace("__DESC__", desc)
        .replace("__SUB__", sub)
        .replace("__CALC_SRC__", html.escape(calc))
        .replace("__IFRAME_TITLE__", iframe_title)
        .replace("__FILL__", fill)
        .replace("__SHARED_JS__", SHARED_JS)
    )


def render_mobile(cake: dict) -> str:
    cid = cake["id"]
    typ = cake["type"]
    name = cake["name"]
    calc = f"../../../calculator/cakes-mobile/{typ}/{cid}.html"
    page_title = html.escape(f"{name} — kosmos")
    h1 = html.escape(name)
    desc = html.escape(cake.get("desc") or "")
    sub = subtitle_html(cake)
    fill = html.escape(cake.get("fillings") or "BASE")
    iframe_title = html.escape(f"калькулятор {name}")
    photos = mobile_photos_html(cid, name)
    return (
        MOBILE_BODY.replace("__PAGE_TITLE__", page_title)
        .replace("__PHOTOS_MOBILE__", photos)
        .replace("__H1__", h1)
        .replace("__DESC__", desc)
        .replace("__SUB__", sub)
        .replace("__CALC_SRC__", html.escape(calc))
        .replace("__IFRAME_TITLE__", iframe_title)
        .replace("__FILL__", fill)
        .replace("__SHARED_JS_MOBILE__", SHARED_JS_MOBILE)
    )


def write_catalog(path: Path, by_id: dict):
    text = path.read_text(encoding="utf-8")
    parts = text.split('<main class="cover-grid">', 1)
    head = parts[0]
    rest = parts[1].split("</main>", 1)
    foot = rest[1]
    # актуальный комментарий вместо старого «только fairy-cake»
    head = re.sub(
        r"<!-- Каталог тортов\.[\s\S]*?-->\s*\n",
        "<!-- Каталог: порядок — CATALOG_ORDER в site/build_site_pages.py; "
        "подписи и ссылки — из calculator/build_cakes.py (поле name, id). -->\n",
        head,
        count=1,
    )
    rows = []
    for cid in CATALOG_ORDER:
        c = by_id[cid]
        nm = html.escape(c["name"])
        rows.append(
            f'  <a class="cover" href="cakes/{html.escape(cid)}.html">'
            f'<img src="../photos/{html.escape(cid)}/cover.jpg" alt="{nm}" loading="lazy">'
            f'<div class="cover-name">{nm}</div></a>'
        )
    body = "<main class=\"cover-grid\">\n" + "\n".join(rows) + "\n</main>"
    path.write_text(head + body + foot, encoding="utf-8")


def main():
    cakes = load_cakes()
    by_id = {c["id"]: c for c in cakes}
    desk_dir = SITE / "desktop" / "cakes"
    mob_dir = SITE / "mobile" / "cakes"
    desk_dir.mkdir(parents=True, exist_ok=True)
    mob_dir.mkdir(parents=True, exist_ok=True)

    for cake in cakes:
        cid = cake["id"]
        (desk_dir / f"{cid}.html").write_text(render_desktop(cake), encoding="utf-8")
        (mob_dir / f"{cid}.html").write_text(render_mobile(cake), encoding="utf-8")

    write_catalog(SITE / "desktop" / "index.html", by_id)
    write_catalog(SITE / "mobile" / "index.html", by_id)

    print(f"OK: {len(cakes)} тортов → desktop/cakes + mobile/cakes")
    print("OK: каталог desktop/index.html, mobile/index.html")


if __name__ == "__main__":
    main()
