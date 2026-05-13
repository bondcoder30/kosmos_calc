# -*- coding: utf-8 -*-
"""
Генерирует страницы тортов site/desktop/cakes/*.html и site/mobile/cakes/*.html
по данным calculator/build_cakes.py (поле name, desc, subtitle, fillings, type, id).

Также перезаписывает site/desktop/index.html и site/mobile/index.html —
порядок обложек как в CATALOG_ORDER, подписи = name из документа.

Запуск из корня репозитория kosmos_calc:
  python site/build_site_pages.py

Также: синхронизирует window.KOSMOS_FILLING_SETS в fillings/data.js с window.FILLING_SETS
из calculator/core.js; пересобирает site/index.html (превью всех страниц тортов).
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


PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp")


def list_cake_image_files(cid: str) -> list[Path]:
    d = PH / cid
    if not d.is_dir():
        return []
    xs = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in PHOTO_EXT]
    return sorted(xs, key=lambda p: p.name.lower())


def pick_cover_path(cid: str) -> Path | None:
    """Обложка: cover.* или первый файл, не slice-N.* (как после import_photos_raw)."""
    d = PH / cid
    files = list_cake_image_files(cid)
    if not files:
        return None
    for ext in PHOTO_EXT:
        p = d / f"cover{ext}"
        if p.exists():
            return p
    for p in files:
        if not re.match(r"slice-\d+\.", p.name, re.I):
            return p
    return files[0]


def slice_paths_after_cover(cid: str, cover: Path | None) -> list[Path]:
    files = list_cake_image_files(cid)
    named: list[tuple[int, Path]] = []
    for p in files:
        m = re.match(r"slice-(\d+)\.", p.name, re.I)
        if m:
            named.append((int(m.group(1)), p))
    if named:
        named.sort(key=lambda t: t[0])
        return [t[1] for t in named]
    if cover is None:
        return []
    covr = cover.resolve()
    return [p for p in files if p.resolve() != covr]


def cover_filename(cid: str) -> str:
    """Имя файла обложки для каталога (реальный файл в photos/<id>/)."""
    p = pick_cover_path(cid)
    return p.name if p else "cover.jpg"


def photo_paths(cid: str) -> tuple[list[str], list[str]]:
    """Десктоп: cover + slice-…; мобилка: slice-… + cover в конце."""
    rel = f"../../photos/{cid}"
    cov = pick_cover_path(cid)
    if cov is None:
        fb = "../../photos/fairy-cake/cover.jpg"
        return ([fb], [fb])
    slices = slice_paths_after_cover(cid, cov)
    desk = [f"{rel}/{cov.name}"] + [f"{rel}/{p.name}" for p in slices]
    mob = [f"{rel}/{p.name}" for p in slices] + [f"{rel}/{cov.name}"]
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
  /* Узкий iframe/окно: третья колонка (начинки) сужается сильнее центра и фото */
  @media (max-width:900px){
    .cake-page{
      grid-template-columns:minmax(0,1fr) minmax(0,1.22fr) minmax(0,0.26fr);
      grid-template-rows:minmax(0,1fr);
    }
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
  <li><a href="../../../calculator/delivery/preview.html">доставка</a></li>
  <li><a href="../about.html">о нас</a></li>
  <li class="menu-note">наш оператор ответит на все вопросы и подберет лучший тортик</li>
  <li class="menu-telegram"><a href="https://t.me/kosmoscake" target="_blank" rel="noopener" aria-label="написать в Telegram">telegram</a></li>
  <li class="menu-phone"><a href="tel:+79037696965">+7 (903) 769-69-65</a></li>
  <li class="menu-close-item"><button class="menu-close" type="button" aria-label="закрыть меню"></button></li>
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
  <li><a href="../../../calculator/delivery/preview.html">доставка</a></li>
  <li><a href="../about.html">о нас</a></li>
  <li class="menu-note">наш оператор ответит на все вопросы и подберет лучший тортик</li>
  <li class="menu-telegram"><a href="https://t.me/kosmoscake" target="_blank" rel="noopener" aria-label="написать в Telegram">telegram</a></li>
  <li class="menu-phone"><a href="tel:+79037696965">+7 (903) 769-69-65</a></li>
  <li class="menu-close-item"><button class="menu-close" type="button" aria-label="закрыть меню"></button></li>
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
  menuList.querySelector('.menu-close').addEventListener('click', (e) => {
    e.stopPropagation();
    menuList.classList.remove('is-open');
  });
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

  (function kosmoPeekScroll(){
    function bounce(el, vert){
      if (!el) return;
      function cap(){ return Math.max(0, vert ? el.scrollHeight - el.clientHeight : el.scrollWidth - el.clientWidth); }
      if (cap() < 10) return;
      var dir = 1, pause = 0, dead = 0;
      var id = setInterval(function(){
        if (dead) return;
        if (pause > 0) { pause--; return; }
        var m = cap();
        if (m < 8) return;
        var c = vert ? el.scrollTop : el.scrollLeft;
        c += (vert ? 0.65 : 1) * dir;
        if (c >= m) { c = m; dir = -1; pause = 75; }
        else if (c <= 0) { c = 0; dir = 1; pause = 90; }
        if (vert) el.scrollTop = c; else el.scrollLeft = c;
      }, 40);
      function kill(){ dead = 1; clearInterval(id); }
      el.addEventListener('touchstart', kill, {passive:true});
      el.addEventListener('wheel', kill, {passive:true});
      el.addEventListener('pointerdown', kill, {passive:true});
    }
    bounce(document.getElementById('mob-photos'), false);
    bounce(document.getElementById('mob-fillings'), false);
    var cp = document.querySelector('.col-photo');
    if (cp) bounce(cp, true);
    var fc = document.getElementById('fillings-col');
    if (fc) bounce(fc, true);
  })();
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


def ordered_cakes(cakes: list, by_id: dict) -> list:
    seen: set[str] = set()
    out: list = []
    for cid in CATALOG_ORDER:
        if cid in by_id:
            out.append(by_id[cid])
            seen.add(cid)
    for c in cakes:
        if c["id"] not in seen:
            out.append(c)
            seen.add(c["id"])
    return out


def sync_kosmos_filling_sets() -> None:
    core = (ROOT / "calculator" / "core.js").read_text(encoding="utf-8")
    base_start = core.index("const _BASE =")
    base_end = core.index("window.FILLING_SETS", base_start)
    base_block = core[base_start:base_end].strip()
    fs_start = core.index("window.FILLING_SETS =")
    fs_end = core.index("window.fmtMoney", fs_start)
    filling_sets = core[fs_start:fs_end].strip()
    filling_sets = filling_sets.replace("window.FILLING_SETS", "window.KOSMOS_FILLING_SETS", 1)
    extracted = base_block + "\n\n" + filling_sets
    data_path = SITE / "fillings" / "data.js"
    data = data_path.read_text(encoding="utf-8")
    m_start = "/* >>> SYNC_FILLING_SETS"
    m_end = "/* <<< SYNC_FILLING_SETS */"
    if m_start not in data or m_end not in data:
        print("WARN: маркеры SYNC_FILLING_SETS в fillings/data.js не найдены — пропуск синхрона")
        return
    a = data.index(m_start)
    b = data.index(m_end) + len(m_end)
    block = f"/* >>> SYNC_FILLING_SETS (build_site_pages.py — из calculator/core.js) */\n{extracted}\n{m_end}"
    data_path.write_text(data[:a] + block + data[b:], encoding="utf-8")
    print("OK: KOSMOS_FILLING_SETS ← calculator/core.js (fillings/data.js)")


def write_site_preview_index(cakes: list, by_id: dict) -> None:
    """Полное превью site/index.html — все страницы тортов (десктоп + мобилка)."""
    base = "https://ab-aacoop.github.io/kosmos_calc/site"
    oc = ordered_cakes(cakes, by_id)

    def card_dsk(c: dict) -> str:
        cid, nm = c["id"], html.escape(c["name"])
        sn = f"snip-dsk-{cid}"
        url = f"{base}/desktop/cakes/{cid}.html"
        return (
            f'  <div class="card">\n'
            f'    <header>\n'
            f'      <span class="type">desktop</span>\n'
            f'      <span class="name">{nm}</span>\n'
            f'      <a class="open" href="desktop/cakes/{html.escape(cid)}.html" target="_blank">↗</a>\n'
            f"    </header>\n"
            f'    <div class="frame-wrap"><iframe src="desktop/cakes/{html.escape(cid)}.html" loading="lazy" title="{nm}"></iframe></div>\n'
            f'    <div class="snip">\n'
            f'      <textarea readonly id="{sn}"><iframe src="{html.escape(url)}" width="1280" height="800" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>\n'
            f'      <div class="snip-row">\n'
            f'        <button type="button" data-copy="{sn}">копировать сниппет</button>\n'
            f'        <span class="ok" data-ok="{sn}">✓ скопировано</span>\n'
            f"      </div>\n"
            f"    </div>\n"
            f"  </div>"
        )

    def card_mob(c: dict) -> str:
        cid, nm = c["id"], html.escape(c["name"])
        sn = f"snip-mob-{cid}"
        url = f"{base}/mobile/cakes/{cid}.html"
        return (
            f'  <div class="card">\n'
            f'    <header>\n'
            f'      <span class="type">mobile</span>\n'
            f'      <span class="name">{nm}</span>\n'
            f'      <a class="open" href="mobile/cakes/{html.escape(cid)}.html" target="_blank">↗</a>\n'
            f"    </header>\n"
            f'    <div class="frame-wrap"><iframe src="mobile/cakes/{html.escape(cid)}.html" loading="lazy" title="{nm}"></iframe></div>\n'
            f'    <div class="snip">\n'
            f'      <textarea readonly id="{sn}"><iframe src="{html.escape(url)}" width="380" height="780" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>\n'
            f'      <div class="snip-row">\n'
            f'        <button type="button" data-copy="{sn}">копировать сниппет</button>\n'
            f'        <span class="ok" data-ok="{sn}">✓ скопировано</span>\n'
            f"      </div>\n"
            f"    </div>\n"
            f"  </div>"
        )

    dsk_rows = "\n".join(card_dsk(c) for c in oc)
    mob_rows = "\n".join(card_mob(c) for c in oc)

    html_out = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kosmos cake — превью страниц сайта</title>
<style>
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;background:#eaeaea;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#222}}
  body{{padding:24px}}
  h1{{margin:0 0 6px;font-size:22px}}
  h2{{margin:28px 0 10px;font-size:16px;color:#555}}
  p.lead{{margin:0 0 14px;color:#555;font-size:14px;max-width:900px;line-height:1.45}}
  p.lead a{{color:#d83448}}
  .topbar{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}}
  .topbar a{{
    text-decoration:none;background:#fff;border:1px solid #ddd;padding:7px 12px;
    border-radius:6px;color:#222;font-size:13px;font-weight:500;
  }}
  .topbar a.primary{{background:#d83448;color:#fff;border-color:#d83448}}
  .topbar a:hover{{filter:brightness(0.95)}}

  .grid-dsk{{display:grid;gap:18px;grid-template-columns:1fr;align-items:start}}
  .grid-mob{{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));align-items:start}}
  .grid-cakes{{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(520px,1fr));align-items:start}}

  .card{{display:flex;flex-direction:column;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
  .card header{{padding:8px 14px;border-bottom:1px solid #eee;display:flex;align-items:center;gap:10px;font-size:12px}}
  .card .type{{padding:2px 8px;background:#d83448;color:#fff;border-radius:999px;font-size:10px;text-transform:uppercase;letter-spacing:.3px}}
  .card .name{{font-weight:600;flex:1}}
  .card a.open{{color:#999;text-decoration:none;font-size:14px}}
  .card a.open:hover{{color:#d83448}}

  .frame-wrap{{width:100%;background:#cfcfcf}}
  .grid-dsk .frame-wrap{{aspect-ratio:1280/800}}
  .grid-cakes .frame-wrap{{aspect-ratio:1280/800}}
  .grid-cakes.grid-mob .frame-wrap{{aspect-ratio:380/780}}
  .frame-wrap iframe{{display:block;width:100%;height:100%;border:0}}

  .snip{{padding:10px 12px;border-top:1px solid #eee;background:#fafafa;display:flex;flex-direction:column;gap:6px}}
  .snip textarea{{
    width:100%;min-height:48px;resize:vertical;
    font-family:Menlo,Consolas,monospace;font-size:11px;line-height:1.4;
    border:1px solid #ddd;border-radius:5px;padding:6px;background:#fff;color:#333;
  }}
  .snip-row{{display:flex;gap:8px;align-items:center}}
  .snip button{{
    background:#d83448;color:#fff;border:0;border-radius:5px;padding:6px 12px;
    font-size:12px;cursor:pointer;font-weight:600;
  }}
  .snip button:hover{{background:#b22937}}
  .snip .ok{{font-size:11px;color:#3b9b4f;opacity:0;transition:opacity .25s}}
  .snip .ok.show{{opacity:1}}
</style>
</head>
<body>

<h1>Kosmos cake — превью страниц сайта</h1>
<p class="lead">
  Каждая страница — готовый HTML для iframe (Tilda / Readymag и т.д.).
  Ниже — главные, страница «о нас» и <strong>все страницы тортов</strong> (десктоп и мобилка), с кнопкой копирования сниппета.
  Фото торта: положите файлы в <code>site/photos raw/&lt;id&gt;/</code> и выполните
  <code>python site/import_photos_raw.py</code>, затем <code>python site/build_site_pages.py</code>.
</p>

<div class="topbar">
  <a class="primary" href="../calculator/cakes/">↗ калькуляторы — десктоп</a>
  <a href="../calculator/cakes-mobile/">↗ калькуляторы — мобилка</a>
  <a href="../calculator/cakes-mobile-full/">↗ мобилка всё-в-одном</a>
  <a href="../calculator/delivery/preview.html">↗ блок доставки</a>
</div>

<h2>Главная — десктоп</h2>
<div class="grid-dsk">
  <div class="card">
    <header>
      <span class="type">desktop</span>
      <span class="name">главная (каталог)</span>
      <a class="open" href="desktop/index.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><iframe src="desktop/index.html" loading="lazy" title="главная — десктоп"></iframe></div>
    <div class="snip">
      <textarea readonly id="snip-dsk-home"><iframe src="{base}/desktop/index.html" width="1280" height="800" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-dsk-home">копировать сниппет</button>
        <span class="ok" data-ok="snip-dsk-home">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>Главная — мобилка</h2>
<div class="grid-mob">
  <div class="card">
    <header>
      <span class="type">mobile</span>
      <span class="name">главная (каталог)</span>
      <a class="open" href="mobile/index.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><iframe src="mobile/index.html" loading="lazy" title="главная — мобилка"></iframe></div>
    <div class="snip">
      <textarea readonly id="snip-mob-home"><iframe src="{base}/mobile/index.html" width="380" height="780" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-mob-home">копировать сниппет</button>
        <span class="ok" data-ok="snip-mob-home">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>О нас — десктоп</h2>
<div class="grid-dsk">
  <div class="card">
    <header>
      <span class="type">desktop</span>
      <span class="name">о нас</span>
      <a class="open" href="desktop/about.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><iframe src="desktop/about.html" loading="lazy" title="о нас — десктоп"></iframe></div>
    <div class="snip">
      <textarea readonly id="snip-dsk-about"><iframe src="{base}/desktop/about.html" width="1280" height="800" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-dsk-about">копировать сниппет</button>
        <span class="ok" data-ok="snip-dsk-about">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>О нас — мобилка</h2>
<div class="grid-mob">
  <div class="card">
    <header>
      <span class="type">mobile</span>
      <span class="name">о нас</span>
      <a class="open" href="mobile/about.html" target="_blank">↗</a>
    </header>
    <div class="frame-wrap"><iframe src="mobile/about.html" loading="lazy" title="о нас — мобилка"></iframe></div>
    <div class="snip">
      <textarea readonly id="snip-mob-about"><iframe src="{base}/mobile/about.html" width="380" height="780" frameborder="0" style="border:0;max-width:100%"></iframe></textarea>
      <div class="snip-row">
        <button type="button" data-copy="snip-mob-about">копировать сниппет</button>
        <span class="ok" data-ok="snip-mob-about">✓ скопировано</span>
      </div>
    </div>
  </div>
</div>

<h2>Все страницы тортов — десктоп</h2>
<div class="grid-cakes">
{dsk_rows}
</div>

<h2>Все страницы тортов — мобилка</h2>
<div class="grid-cakes grid-mob">
{mob_rows}
</div>

<script>
document.addEventListener('click', function(e){{
  var b = e.target.closest('button[data-copy]');
  if (!b) return;
  var id = b.dataset.copy;
  var ta = document.getElementById(id);
  if (!ta) return;
  ta.select();
  ta.setSelectionRange(0, ta.value.length);
  var ok = false;
  try {{ ok = document.execCommand('copy'); }} catch(_{{}}){{}}
  if (!ok && navigator.clipboard){{
    navigator.clipboard.writeText(ta.value).then(function(){{ flash(id); }});
    return;
  }}
  if (ok) flash(id);
}});
function flash(id){{
  var el = document.querySelector('[data-ok="'+id+'"]');
  if (!el) return;
  el.classList.add('show');
  setTimeout(function(){{ el.classList.remove('show'); }}, 1800);
}}
</script>

</body>
</html>
"""
    (SITE / "index.html").write_text(html_out, encoding="utf-8")
    print(f"OK: site/index.html — превью всех {len(oc)} тортов + главные")


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
        cov = cover_filename(cid)
        rows.append(
            f'  <a class="cover" href="cakes/{html.escape(cid)}.html">'
            f'<img src="../photos/{html.escape(cid)}/{html.escape(cov)}" alt="{nm}" loading="lazy">'
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

    sync_kosmos_filling_sets()
    write_site_preview_index(cakes, by_id)
    (SITE / "photos raw").mkdir(parents=True, exist_ok=True)

    print(f"OK: {len(cakes)} тортов → desktop/cakes + mobile/cakes")
    print("OK: каталог desktop/index.html, mobile/index.html")


if __name__ == "__main__":
    main()
