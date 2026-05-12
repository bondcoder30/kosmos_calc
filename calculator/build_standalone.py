"""
Сборка трёх stand-alone HTML-файлов для копипаста в Readymag/Tilda/верстальщику.
Все ассеты (шрифты, SVG, общий CSS/JS) инлайнятся прямо в HTML.
"""

import base64
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent
ASSETS = ROOT / "assets"
OUT = ROOT / "standalone"
OUT.mkdir(exist_ok=True)

# ---------- 1) Кодируем шрифты в base64 ----------
def b64(path, mime):
    data = path.read_bytes()
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"

font_beast = b64(ASSETS / "ALS_Beast_Ultra.otf",   "font/otf")
font_golos = b64(ASSETS / "GolosText-Regular.ttf", "font/ttf")

# ---------- 2) Читаем SVG как data URI ----------
def svg_uri(path):
    text = path.read_text(encoding='utf-8').strip()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('#', '%23').replace('"', "'")
    return "data:image/svg+xml;utf8," + text

uri_star  = svg_uri(ASSETS / "star.svg")
uri_plus  = svg_uri(ASSETS / "plus.svg")
uri_minus = svg_uri(ASSETS / "minus.svg")
uri_chev  = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='%23d83448' stroke-width='2.5' fill='none' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'/></svg>"

# ---------- 3) Общий CSS (вместо style.css, но с инлайн-URI ассетов) ----------
SHARED_CSS = f"""
@font-face{{
  font-family:'ALS Beast';
  src:url('{font_beast}') format('opentype');
  font-weight:900;font-style:normal;font-display:swap;
}}
@font-face{{
  font-family:'Golos Text';
  src:url('{font_golos}') format('truetype');
  font-weight:400;font-style:normal;font-display:swap;
}}
:root{{
  --bg:#cfcfcf; --red:#d83448; --red-2:#c41d33; --pink:#f08a99;
  --display:'ALS Beast', system-ui, sans-serif;
  --text:'Golos Text', system-ui, sans-serif;
}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;height:100%;background:var(--bg);font-family:var(--text);color:#1a1a1a}}
.calc-frame{{position:relative;height:100%;background:var(--bg);overflow:hidden}}
.calc-scroll{{height:100%;overflow-y:auto;padding:48px 24px 40px;scrollbar-width:thin;scrollbar-color:rgba(0,0,0,.25) transparent}}
.calc-scroll::-webkit-scrollbar{{width:6px}}
.calc-scroll::-webkit-scrollbar-thumb{{background:rgba(0,0,0,.2);border-radius:3px}}
.calc-scroll::-webkit-scrollbar-track{{background:transparent}}
.sparkle{{position:absolute;width:22px;height:22px;background:url("{uri_star}") center/contain no-repeat;pointer-events:none;z-index:2}}
.sparkle.tl{{top:14px;left:18px}}
.sparkle.tr{{top:14px;right:18px}}
.calc-meta{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;font-family:var(--display);font-size:11px;color:#555;letter-spacing:.5px;text-transform:uppercase}}
.cake-picker, .pill-select{{
  width:100%;display:block;font-family:var(--display);font-size:14px;
  border:2px solid var(--red);border-radius:999px;background:#fff;color:var(--red);
  padding:11px 16px;text-align:center;appearance:none;cursor:pointer;letter-spacing:.5px;text-transform:lowercase;
  background-image:url("{uri_chev}");
  background-repeat:no-repeat;background-position:right 16px center;background-size:14px;padding-right:38px;
}}
.label{{text-align:center;color:#fff;font-family:var(--display);font-size:34px;text-transform:lowercase;margin:24px 0 8px;letter-spacing:.5px;line-height:1}}
.label::first-letter{{text-transform:uppercase}}
.stepper{{display:flex;align-items:center;justify-content:center;gap:22px;color:var(--red);font-family:var(--display)}}
.stepper .step-btn{{background:none;border:0;padding:0;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:transform .08s ease, filter .15s ease}}
.stepper .step-btn:active{{transform:scale(.92)}}
.stepper .step-btn:hover{{filter:brightness(.95) saturate(1.15)}}
.stepper .step-btn .icn{{display:block;background-position:center;background-repeat:no-repeat;background-size:contain;user-select:none}}
.stepper .step-btn .icn.plus {{width:48px;height:48px;background-image:url("{uri_plus}")}}
.stepper .step-btn .icn.minus{{width:48px;height:18px;background-image:url("{uri_minus}")}}
.stepper .value{{font-size:88px;line-height:1;min-width:140px;text-align:center;letter-spacing:1px;color:var(--red)}}
.fixed-row{{display:flex;align-items:center;justify-content:center;gap:28px;margin:8px 0;cursor:pointer;border-radius:8px;padding:6px 10px;user-select:none}}
.fixed-row .value{{font-family:var(--display);color:var(--red);font-size:88px;line-height:1;letter-spacing:1px}}
.radio-big{{width:72px;height:72px;border-radius:50%;border:0;background:#fff;cursor:pointer;flex-shrink:0;padding:0;transition:background-color .15s ease, transform .08s ease}}
.radio-big:hover{{background:var(--pink)}}
.radio-big.checked{{background:var(--red)}}
.radio-big:active{{transform:scale(.94)}}
.fixed-row:hover .radio-big:not(.checked){{background:var(--pink)}}
.hint{{text-align:center;color:#3a3a3a;font-size:13px;margin:14px 8px 6px;line-height:1.4;font-family:var(--text)}}
.tiers{{display:flex;flex-direction:column;gap:10px;margin-top:14px}}
.tier-row .tier-label{{text-align:center;font-family:var(--display);font-size:12px;color:var(--red);text-transform:lowercase;margin-bottom:5px;letter-spacing:.5px}}
.total-wrap{{margin-top:32px;text-align:center;position:relative;padding-top:14px}}
.total-wrap .sparkle{{position:absolute;top:-2px;width:14px;height:14px;background-position:center}}
.total-wrap .sparkle.l{{left:30%}}
.total-wrap .sparkle.r{{right:30%}}
.total-label{{font-family:var(--display);color:var(--red);font-size:14px;text-transform:lowercase;letter-spacing:1.5px;margin-bottom:8px}}
.total-value{{font-family:var(--display);color:var(--red);font-size:60px;line-height:1;letter-spacing:1px}}
.send-row{{margin-top:22px;display:flex;justify-content:center}}
.send-row button{{font-family:var(--display);font-size:14px;letter-spacing:1px;text-transform:uppercase;background:var(--red);color:#fff;border:0;padding:13px 24px;border-radius:999px;cursor:pointer}}
.send-row button:hover{{background:var(--red-2)}}
@media (max-width:480px){{
  .calc-scroll{{padding:38px 18px 30px}}
  .stepper{{gap:14px}}
  .stepper .step-btn .icn.plus{{width:36px;height:36px}}
  .stepper .step-btn .icn.minus{{width:36px;height:14px}}
  .stepper .value, .fixed-row .value{{font-size:64px;min-width:auto}}
  .label{{font-size:26px}}
  .total-value{{font-size:44px}}
  .radio-big{{width:56px;height:56px}}
}}
"""

# ---------- 4) Общий JS (вместо core.js) ----------
SHARED_JS = """
const FILLING_PRICES = {
  "яблочный синнабон":2800,"шоколадный с шоколадом":3000,"ванильный с клубникой":3000,
  "ванильный с вишней":3000,"кукис энд крим":2800,"мак-лимон":2800,
  "фундук-кофе шоколад":3600,"фисташка-малина":3600,"шоколад-кокос":2800,
  "морковный":3000,"сникерс":2800,"дорблю груша-грецкий орех":3600,
  "апельсин-манго-маракуйя":2800,"черника-шоколад":3600,
  "фисташковый чизкейк":2800,"чизкейк орео":2800,"чизкейк Нью Йорк":3000,"тирамису":3000
};
const _BASE=["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","сникерс","дорблю груша-грецкий орех","апельсин-манго-маракуйя"];
const FILLING_SETS = {
  BASE:_BASE,
  PLUS_CHERNIKA:[..._BASE,"черника-шоколад"],
  PLUS_CHEESECAKE:[..._BASE,"черника-шоколад","чизкейк Нью Йорк","чизкейк орео","фисташковый чизкейк"],
  NO_SNICKERS_NO_DORBLU:["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","апельсин-манго-маракуйя"],
  TYPE3_LOVE:["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","дорблю груша-грецкий орех","апельсин-манго-маракуйя"]
};
const fmtMoney = n => Math.round(n).toLocaleString('ru-RU').replace(/,/g,' ')+'р';
const fmtWeight = w => Number.isInteger(w) ? w.toFixed(1) : w.toString();
const range = (min,max,price) => ({min,max,price});
const decorForWeight = (t,w) => { for(const r of t){ if(w>=r.min && w<=r.max) return r.price;} return t[t.length-1].price; };
const sendOrder = (p) => { console.log('[ORDER]',p); alert('Заказ собран (см. консоль). На втором заходе подключим Google Sheets / Telegram-бот.\\n\\n'+JSON.stringify(p,null,2)); };
"""

# ---------- 5) Тип-специфичные блоки (читаем из соответствующих html и вырезаем <script>) ----------
def extract_script(html_file):
    text = (ROOT / html_file).read_text(encoding='utf-8')
    # ищем второй <script> блок (первый — это <script src="core.js"></script>)
    blocks = re.findall(r'<script>\s*(.*?)\s*</script>', text, flags=re.DOTALL)
    return blocks[0] if blocks else ""

JS_TIERED = extract_script("tiered.html")
JS_FIXED  = extract_script("fixed.html")
JS_WEIGHT = extract_script("weight.html")

# В extracted JS заменяем ссылки на assets/...svg на инлайн-URI
def inline_svg_refs(js):
    js = js.replace("assets/minus.svg", uri_minus)
    js = js.replace("assets/plus.svg",  uri_plus)
    js = js.replace("assets/star.svg",  uri_star)
    return js

# Также заменим конструкции <img src="assets/plus.svg"> на <span class="icn plus">
# чтобы не зависеть от src и поддержать ретина через background. Эти строки придут
# из tiered.html / weight.html, заменим их в JS-исходнике до записи.
def patch_step_imgs(js):
    js = js.replace('<img src="assets/minus.svg" alt="">', '<span class="icn minus"></span>')
    js = js.replace('<img src="assets/plus.svg" alt="">',  '<span class="icn plus"></span>')
    return js

JS_TIERED = patch_step_imgs(inline_svg_refs(JS_TIERED))
JS_FIXED  = patch_step_imgs(inline_svg_refs(JS_FIXED))
JS_WEIGHT = patch_step_imgs(inline_svg_refs(JS_WEIGHT))

# ---------- 6) Сборка финальных HTML ----------
def page(title, js_block):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<title>{title}</title>
<style>{SHARED_CSS}</style>
</head>
<body>

<div class="calc-frame">
  <span class="sparkle tl"></span>
  <span class="sparkle tr"></span>
  <div class="calc-scroll" id="root"></div>
</div>

<script>
{SHARED_JS}
{js_block}
</script>
</body>
</html>
"""

(OUT / "kosmos-calc-tiered.html").write_text(page("Калькулятор — ярусные", JS_TIERED), encoding='utf-8')
(OUT / "kosmos-calc-fixed.html").write_text(page("Калькулятор — фикс. вес", JS_FIXED), encoding='utf-8')
(OUT / "kosmos-calc-weight.html").write_text(page("Калькулятор — плоский по весу", JS_WEIGHT), encoding='utf-8')

for f in sorted(OUT.iterdir()):
    print(f"{f.stat().st_size:>8}  {f.name}")
print("\nSTANDALONE files ready in:", OUT)
