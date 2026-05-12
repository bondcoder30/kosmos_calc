/* ================================================================
   ОБЩИЕ ДАННЫЕ И УТИЛИТЫ
   ================================================================ */

window.FILLING_PRICES = {
  "яблочный синнабон":2800,"шоколадный с шоколадом":3000,"ванильный с клубникой":3000,
  "ванильный с вишней":3000,"кукис энд крим":2800,"мак-лимон":2800,
  "фундук-кофе шоколад":3600,"фисташка-малина":3600,"шоколад-кокос":2800,
  "морковный":3000,"сникерс":2800,"дорблю груша-грецкий орех":3600,
  "апельсин-манго-маракуйя":2800,"черника-шоколад":3600,
  "фисташковый чизкейк":2800,"чизкейк орео":2800,"чизкейк Нью Йорк":3000,"тирамису":3000
};

const _BASE = ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","сникерс","дорблю груша-грецкий орех","апельсин-манго-маракуйя"];

window.FILLING_SETS = {
  BASE: _BASE,
  PLUS_CHERNIKA: [..._BASE, "черника-шоколад"],
  PLUS_CHEESECAKE: [..._BASE, "черника-шоколад", "чизкейк Нью Йорк", "чизкейк орео", "фисташковый чизкейк"],
  NO_SNICKERS_NO_DORBLU: ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","апельсин-манго-маракуйя"],
  TYPE3_LOVE: ["яблочный синнабон","шоколадный с шоколадом","ванильный с клубникой","ванильный с вишней","кукис энд крим","мак-лимон","фундук-кофе шоколад","фисташка-малина","шоколад-кокос","морковный","дорблю груша-грецкий орех","апельсин-манго-маракуйя"],
  TIRAMISU: ["тирамису"]
};

window.fmtMoney  = n => Math.round(n).toLocaleString('ru-RU').replace(/,/g,' ') + 'р';
window.fmtWeight = w => Number.isInteger(w) ? w.toFixed(1) : w.toString();
window.range     = (min, max, price) => ({min, max, price});
window.decorForWeight = (table, w) => {
  for (const r of table) if (w >= r.min && w <= r.max) return r.price;
  return table[table.length-1].price;
};

window.sendOrder = (payload) => {
  console.log('[ORDER]', payload);
  alert('Заказ собран (см. консоль). На втором заходе подключим Google Sheets / Telegram-бот.\n\n' + JSON.stringify(payload, null, 2));
};

/* ================================================================
   SVG-ИКОНКИ (инлайн, без файлов)
   ================================================================ */
const SVG_MINUS = '<svg viewBox="0 0 100 30" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="30" rx="15"/></svg>';
const SVG_PLUS  = '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect x="33" width="34" height="100" rx="14"/><rect y="33" width="100" height="34" rx="14"/></svg>';

/* ================================================================
   HEADER (заголовок + описание + сабтайтл)
   ================================================================ */
function renderHeader(cake){
  if (!cake.title && !cake.desc && !cake.subtitle) return '';
  return `
    <header class="cake-header">
      ${cake.title    ? `<h1 class="cake-title">${cake.title}</h1>` : ''}
      ${cake.desc     ? `<p class="cake-desc">${cake.desc}</p>` : ''}
      ${cake.subtitle ? `<p class="cake-subtitle">${cake.subtitle}</p>` : ''}
    </header>
  `;
}

/* ================================================================
   ТИП 1 — ОДИН ЯРУСНЫЙ ТОРТ (без выбора торта)
   total = ярусы × декорPerTier  +  вес × 3200
   ================================================================ */
window.renderTieredCake = function(cake){
  const FILLING_RATE = 3200;
  const state = {
    weight: cake.minWeight,
    tiers:  cake.minTiers,
    tierFillings: []
  };
  const root = document.getElementById('root');

  function calc(){
    return {
      decor:   state.tiers * cake.decorPerTier,
      filling: state.weight * FILLING_RATE,
      total:   state.tiers * cake.decorPerTier + state.weight * FILLING_RATE
    };
  }

  function draw(){
    while (state.tierFillings.length < state.tiers) state.tierFillings.push(cake.fillings[0]);
    state.tierFillings = state.tierFillings.slice(0, state.tiers);
    const r = calc();

    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="w-" aria-label="минус">${SVG_MINUS}</button>
        <div class="value">${fmtWeight(state.weight)}</div>
        <button class="step-btn plus"  data-act="w+" aria-label="плюс">${SVG_PLUS}</button>
      </div>
      <div class="label">Сколько ярусов?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="t-" aria-label="минус">${SVG_MINUS}</button>
        <div class="value">${state.tiers}</div>
        <button class="step-btn plus"  data-act="t+" aria-label="плюс">${SVG_PLUS}</button>
      </div>
      <div class="hint">От ${cake.minTiers} ярус${cake.minTiers===1?'а':'ов'}. От ${fmtWeight(cake.minWeight)} кг.${cake.note?'<br>'+cake.note:''}</div>
      <div class="tiers">
        ${state.tierFillings.map((val,i)=>`
          <div class="tier-row">
            <div class="tier-label">начинка ${i+1} ярус</div>
            <select class="pill-select" data-tier="${i}">
              ${[...cake.fillings, 'фальш ярус'].map(f=>`<option ${f===val?'selected':''}>${f}</option>`).join('')}
            </select>
          </div>
        `).join('')}
      </div>
      <div class="total-wrap">
        <div class="total-label">итоговая стоимость</div>
        <div class="total-value">${fmtMoney(r.total)}</div>
      </div>
      <div class="send-row"><button id="send">Отправить заказ</button></div>
    `;

    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = () => {
        const a = b.dataset.act;
        if (a==='w+') state.weight = +(state.weight + 0.5).toFixed(1);
        if (a==='w-') state.weight = Math.max(cake.minWeight, +(state.weight - 0.5).toFixed(1));
        if (a==='t+') state.tiers++;
        if (a==='t-') state.tiers = Math.max(cake.minTiers, state.tiers - 1);
        draw();
      };
    });
    root.querySelectorAll('select[data-tier]').forEach(s => {
      s.onchange = e => { state.tierFillings[+s.dataset.tier] = e.target.value; draw(); };
    });
    root.querySelector('#send').onclick = () => {
      sendOrder({
        type:'tiered', cake:cake.name, weight:state.weight, tiers:state.tiers,
        tierFillings: state.tierFillings.slice(0, state.tiers),
        decor:r.decor, fillingCost:r.filling, total:r.total
      });
    };
  }

  draw();
};

/* ================================================================
   ТИП 2 — ФИКС. ВЕС (без выбора торта)
   total = вес × цена_начинки  +  декор(вес)
   ================================================================ */
window.renderFixedCake = function(cake){
  const state = { weight:2.5, filling:cake.fillings[0] };
  const root = document.getElementById('root');

  function calc(){
    const decor = cake.decor[state.weight];
    const filling = state.weight * FILLING_PRICES[state.filling];
    return { decor, filling, total: decor + filling };
  }

  function draw(){
    if (!cake.fillings.includes(state.filling)) state.filling = cake.fillings[0];
    const r = calc();
    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="fixed-row" data-w="2.5">
        <button class="radio-big ${state.weight===2.5?'checked':''}" aria-label="2.5 кг" type="button"></button>
        <span class="value">2.5</span>
      </div>
      <div class="fixed-row" data-w="3.5">
        <button class="radio-big ${state.weight===3.5?'checked':''}" aria-label="3.5 кг" type="button"></button>
        <span class="value">3.5</span>
      </div>
      <div class="tier-row" style="margin-top:14px">
        <div class="tier-label">начинка</div>
        <select class="pill-select" id="filling">
          ${cake.fillings.map(f=>`<option ${f===state.filling?'selected':''}>${f}</option>`).join('')}
        </select>
      </div>
      <div class="total-wrap">
        <div class="total-label">итоговая стоимость</div>
        <div class="total-value">${fmtMoney(r.total)}</div>
      </div>
      <div class="send-row"><button id="send">Отправить заказ</button></div>
    `;
    root.querySelectorAll('.fixed-row[data-w]').forEach(row => {
      row.onclick = () => { state.weight = parseFloat(row.dataset.w); draw(); };
    });
    root.querySelector('#filling').onchange = e => { state.filling = e.target.value; draw(); };
    root.querySelector('#send').onclick = () => {
      sendOrder({
        type:'fixed', cake:cake.name, weight:state.weight, filling:state.filling,
        decor:r.decor, fillingCost:r.filling, total:r.total
      });
    };
  }
  draw();
};

/* ================================================================
   ТИП 3 — ПЛОСКИЙ ПО ВЕСУ (без выбора торта)
   total = вес × цена_начинки  +  декор(вес)
   ================================================================ */
window.renderWeightCake = function(cake){
  const state = { weight: cake.minWeight, filling: cake.fillings[0] };
  const root = document.getElementById('root');

  function calc(){
    const decor = decorForWeight(cake.decorTable, state.weight);
    const filling = state.weight * FILLING_PRICES[state.filling];
    return { decor, filling, total: decor + filling };
  }

  function decorHint(){
    if (cake.id === 'berry-fields') return `От ${fmtWeight(cake.minWeight)} кг. Цена декора растёт по 1 кг — от 3 000р до 24 000р.`;
    if (cake.id === 'tiramisu')     return `Стоимость только начинки — 3 000р/кг.`;
    const parts = cake.decorTable.map(r => {
      if (r.min === r.max) return `${r.min} кг — ${r.price.toLocaleString('ru-RU').replace(/,/g,' ')}р`;
      return `${fmtWeight(r.min)}–${fmtWeight(r.max)} кг — ${r.price.toLocaleString('ru-RU').replace(/,/g,' ')}р`;
    });
    return `От ${fmtWeight(cake.minWeight)} кг. Декор: ${parts.join(' · ')}.`;
  }

  function draw(){
    if (!cake.fillings.includes(state.filling)) state.filling = cake.fillings[0];
    const r = calc();
    root.innerHTML = `
      ${renderHeader(cake)}
      <div class="label">Сколько килограмм?</div>
      <div class="stepper">
        <button class="step-btn minus" data-act="w-" aria-label="минус">${SVG_MINUS}</button>
        <div class="value">${fmtWeight(state.weight)}</div>
        <button class="step-btn plus"  data-act="w+" aria-label="плюс">${SVG_PLUS}</button>
      </div>
      <div class="hint">${decorHint()}</div>
      <div class="tier-row" style="margin-top:14px">
        <div class="tier-label">начинка</div>
        <select class="pill-select" id="filling">
          ${cake.fillings.map(f=>`<option ${f===state.filling?'selected':''}>${f}</option>`).join('')}
        </select>
      </div>
      <div class="total-wrap">
        <div class="total-label">итоговая стоимость</div>
        <div class="total-value">${fmtMoney(r.total)}</div>
      </div>
      <div class="send-row"><button id="send">Отправить заказ</button></div>
    `;
    root.querySelectorAll('button[data-act]').forEach(b => {
      b.onclick = () => {
        const a = b.dataset.act;
        if (a==='w+') state.weight = +Math.min(cake.maxWeight, state.weight + 0.5).toFixed(1);
        if (a==='w-') state.weight = +Math.max(cake.minWeight, state.weight - 0.5).toFixed(1);
        draw();
      };
    });
    root.querySelector('#filling').onchange = e => { state.filling = e.target.value; draw(); };
    root.querySelector('#send').onclick = () => {
      sendOrder({
        type:'weight', cake:cake.name, weight:state.weight, filling:state.filling,
        decor:r.decor, fillingCost:r.filling, total:r.total
      });
    };
  }
  draw();
};
