"""
Сборка трёх stand-alone HTML-сниппетов для копипаста в Readymag/Tilda.

Что инлайнится: общий CSS и общий JS.
Что НЕ инлайнится: шрифты (тянутся из GitHub Pages, см. @font-face в style.css)
                   SVG (уже инлайн в HTML-разметке кнопок).

Получаются маленькие файлы (~10–15 KB), которые можно целиком
скопировать и вставить в HTML-виджет.
"""

import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent
OUT = ROOT / "standalone"
OUT.mkdir(exist_ok=True)

# Чистим старые большие файлы, если есть
for old in OUT.glob("*.html"):
    old.unlink()

SHARED_CSS = (ROOT / "style.css").read_text(encoding='utf-8')
SHARED_JS  = (ROOT / "core.js").read_text(encoding='utf-8')

def extract_script(html_file):
    """Достаём только пользовательский <script> блок (без <script src="core.js">)."""
    text = (ROOT / html_file).read_text(encoding='utf-8')
    blocks = re.findall(r'<script>\s*(.*?)\s*</script>', text, flags=re.DOTALL)
    return blocks[0] if blocks else ""

JS_TIERED = extract_script("tiered.html")
JS_FIXED  = extract_script("fixed.html")
JS_WEIGHT = extract_script("weight.html")

def page(title, js_block):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<style>
{SHARED_CSS}
</style>
</head>
<body>

<div class="calc-frame">
  <div class="calc-scroll" id="root"></div>
</div>

<script>
{SHARED_JS}
{js_block}
</script>
</body>
</html>
"""

(OUT / "kosmos-calc-tiered.html").write_text(page("Калькулятор — ярусные",          JS_TIERED), encoding='utf-8')
(OUT / "kosmos-calc-fixed.html" ).write_text(page("Калькулятор — фикс. вес",         JS_FIXED),  encoding='utf-8')
(OUT / "kosmos-calc-weight.html").write_text(page("Калькулятор — плоский по весу",   JS_WEIGHT), encoding='utf-8')

for f in sorted(OUT.iterdir()):
    print(f"{f.stat().st_size:>7} bytes  {f.name}")
print(f"\nГотово. Файлы в: {OUT}")
