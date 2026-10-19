import './style.css';
import { DEFAULTS, SCEN, run } from './engine.js';
const A = structuredClone(DEFAULTS), $ = id => document.getElementById(id);
const nf = (d = 0) => v => v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
const pc = d => v => (v * 100).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%';
const COL = i => `var(--c${i})`; let cur = 0;
// [clave, etiqueta, escala de entrada, ¿por escenario?]
const SEC = [
  { t: 'Modelo', o: 1, sel: 1, f: [] },
  { t: 'Política y sector externo', o: 1, f: [['ca27', 'Cuenta corriente 2027 (% PBI)', 100, 1], ['rho4', 'Riesgo país a fin de 2027 (pb)', 1, 1], ['p', 'Prob. de caída del acuerdo con el FMI (%)', 100, 1], ['pfac', 'Factor de compras del BCRA', 1, 1]] },
  { t: 'Financiamiento (US$ millones)', o: 1, f: [['saldo', 'Saldo del programa 2026', 1, 1], ['loc', 'Emisión local en dólares', 1, 1], ['intl', 'Emisión internacional', 1, 1], ['ondem', 'Pagos de ON por trimestre (T2 a T4)', 1, 1]] },
  { t: 'Generales', f: [['gtr', 'Crecimiento tendencial (%)', 100], ['pi0', 'Inflación inicial de N (% anual)', 1], ['E0', 'Tipo de cambio inicial ($/US$)', 1], ['anc4', 'Ancla de inflación T4-2027 (%)', 1]] },
  { t: 'Curva de Phillips', f: [['gamma', 'Inercia de la inflación (γ)', 1], ['theta', 'Peso de la inflación pasada (ϑ)', 1], ['kappa', 'Pendiente respecto de la brecha (κ)', 1], ['betaE', 'Traspaso de depreciación rezagada (β_E)', 1], ['betai', 'Costo financiero (β_i)', 1], ['betae', 'Expectativas de depreciación (β_ε)', 1], ['a', 'Peso de los transables en el IPC (a)', 1]] },
];
const inp = (k, sc, i) => `<input type="number" step="any" inputmode="decimal" aria-label="${k}${i === undefined ? '' : ' ' + SCEN[i]}" data-k="${k}" ${i === undefined ? '' : `data-i="${i}"`} data-sc="${sc}" value="${+((i === undefined ? A[k] : A[k][i]) * sc).toFixed(4)}">`;
function build() {
  $('ctl').innerHTML = SEC.map(s => `<details ${s.o ? 'open' : ''}><summary>${s.t}</summary><div class="body">` +
    (s.sel ? `<div class="row sel"><label class="sl">Coeficientes del modelo<select data-g="sel"><option value="1">Juego 1 (depreciación expansiva)</option><option value="2">Juego 2 (contractiva)</option></select></label></div>
      <div class="row sel"><label class="sl">Capital de organismos<select data-g="selcap"><option value="2">Presupuesto 2027</option><option value="1">Planilla MECON</option></select></label></div>` : '') +
    (s.f.some(f => f[3]) ? `<div class="row hd"><span></span><b>Base</b><b>Opt.</b><b>Pes.</b></div>` : '') +
    s.f.map(([k, l, sc, per]) => per ? `<div class="row"><span class="l">${l}</span>${[0, 1, 2].map(i => inp(k, sc, i)).join('')}</div>`
      : `<div class="row one"><span class="l">${l}</span>${inp(k, sc)}</div>`).join('') + '</div></details>').join('');
  $('tabs').innerHTML = SCEN.map((s, i) => `<button type="button" data-t="${i}" aria-pressed="${i === cur}">${s}</button>`).join('');
  $('legend').innerHTML = SCEN.map((s, i) => `<span><i style="background:${COL(i)}"></i>${s}</span>`).join('');
}
$('ctl').addEventListener('input', e => {
  const t = e.target, d = t.dataset;
  if (d.g) A[d.g] = +t.value; else if (t.value !== '' && isFinite(+t.value)) { const v = +t.value / +d.sc; d.i === undefined ? A[d.k] = v : A[d.k][+d.i] = v; }
  render();
});
$('tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; cur = +b.dataset.t; $('tabs').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); render(); });
$('reset').onclick = () => { Object.assign(A, structuredClone(DEFAULTS)); build(); render(); };
const ITEMS = [['Sector externo y reservas'],
  ['Cuenta corriente', 'ca', pc(2)], ['Compras de divisas del BCRA (US$ M)', 'pur', nf()], ['Colchón acumulado a septiembre (US$ M)', 'cum3', nf()], ['Colchón acumulado a diciembre (US$ M)', 'cum4', nf()],
  ['Compras adicionales necesarias en T4 (US$ M)', 'need', nf()], ['Variación de reservas en 2027 (US$ M)', 'dR', nf()], ['Reservas brutas a fin de 2027, ilustrativo (US$ M)', 'reservas', nf()],
  ['Flujo neto de ON (US$ M)', 'onNet', nf()], ['Usos totales en moneda extranjera (US$ M)', 'uses', nf()],
  ['Actividad y precios'],
  ['Crecimiento del producto', 'growth', pc(2)], ['Inflación IPC, promedio anualizado (%)', 'cpi', nf(1)], ['Inflación IPC T4-2027 (%)', 'cpiT4', nf(1)], ['Tipo de cambio nominal a fin de 2027 ($/US$)', 'E', nf()],
  ['Tipo de cambio real a fin de 2027 (ref. = 1)', 'q', nf(3)], ['Tasa de interés, promedio (%)', 'i', nf(1)], ['Empleo, desvío respecto de la referencia', 'emp', pc(2)], ['Riesgo país a fin de 2027 (pb)', 'rho', nf()]];
const QL = ['T4-2026', 'T1-2027', 'T2-2027', 'T3-2027', 'T4-2027'];
const QROWS = [['Balance en moneda extranjera'], ['Compras de divisas del BCRA (US$ M)', 'pur', nf()], ['Total fuentes (US$ M)', 'src', nf()], ['Total usos (US$ M)', 'uses', nf()], ['Resultado neto (US$ M)', 'net', nf()], ['Colchón acumulado (US$ M)', 'cum', nf()], ['Reservas brutas, ilustrativo (US$ M)', 'reservas', nf()],
  ['Actividad y precios'], ['Actividad (T4-2026 = 100)', 'act', nf(1)], ['Inflación del sector N (% anual)', 'piN', nf(1)], ['Inflación IPC (% anual)', 'cpi', nf(1)], ['Tipo de cambio nominal ($/US$)', 'E', nf()], ['Tipo de cambio real (ref. = 1)', 'q', nf(3)], ['Tasa de interés (% anual)', 'i', nf(1)], ['Riesgo país (pb)', 'rho', nf()]];
const FLOW = ['pur', 'src', 'uses', 'net', 'cum'];
const cell = (v, f) => `<td class="${v < 0 ? 'n' : ''}">${f(v)}</td>`, gp = (t, n) => `<tr class="gp"><td colspan="${n}">${t}</td></tr>`;
function chart(title, k, f, from, R) {
  const W = 440, H = 200, L = 54, Rr = 56, T = 14, B = 26, js = [0, 1, 2, 3, 4].filter(j => j >= from), all = R.flatMap(r => js.map(j => r.q[k][j]));
  let lo = Math.min(...all), hi = Math.max(...all); if (lo === hi) { lo -= 1; hi += 1; } const pd = (hi - lo) * .12; lo -= pd; hi += pd;
  const x = j => L + (j - js[0]) / (js.length - 1) * (W - L - Rr), y = v => T + (1 - (v - lo) / (hi - lo)) * (H - T - B);
  const grid = [0, 1, 2, 3].map(n => { const v = lo + (hi - lo) * n / 3; return `<line class="g" x1="${L}" x2="${W - Rr}" y1="${y(v)}" y2="${y(v)}"/><text x="${L - 6}" y="${y(v) + 4}" text-anchor="end">${f(v)}</text>`; }).join('');
  const zero = lo < 0 && hi > 0 ? `<line class="z" x1="${L}" x2="${W - Rr}" y1="${y(0)}" y2="${y(0)}"/>` : '';
  const xl = js.map(j => `<text x="${x(j)}" y="${H - 8}" text-anchor="middle">${QL[j].replace('-20', ' ')}</text>`).join('');
  const lines = R.map((r, i) => { const p = js.map((j, n) => `${n ? 'L' : 'M'}${x(j).toFixed(1)} ${y(r.q[k][j]).toFixed(1)}`).join(''), v = r.q[k][4];
    return `<path d="${p}" style="stroke:${COL(i)}"/><circle cx="${x(4)}" cy="${y(v)}" r="3.5" style="fill:${COL(i)}"/><text class="e" x="${x(4) + 8}" y="${y(v) + 4}" style="fill:${COL(i)}">${f(v)}</text>`; }).join('');
  return `<figure><figcaption>${title}</figcaption><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${title}">${grid}${zero}${xl}${lines}</svg></figure>`;
}
function render() {
  document.querySelectorAll('[data-g]').forEach(s => s.value = A[s.dataset.g]);
  const R = SCEN.map((_, i) => run(A, i)), Y = R.map(r => r.y);
  $('kpi').innerHTML = Y.map((y, i) => `<article style="--c:${COL(i)}"><h3>${SCEN[i]}</h3><p class="big">${nf(1)(y.cpi)}%</p><p class="sub">Inflación IPC, promedio anualizado</p><dl>
    <dt>Crecimiento</dt><dd>${pc(2)(y.growth)}</dd><dt>Tipo de cambio, fin 2027</dt><dd>$ ${nf()(y.E)}</dd><dt>Reservas, fin 2027</dt><dd>US$ ${nf()(y.reservas)} M</dd><dt>Compras extra en T4</dt><dd>US$ ${nf()(y.need)} M</dd></dl></article>`).join('');
  $('charts').innerHTML = [['Inflación IPC (% anual)', 'cpi', nf(0), 0], ['Tipo de cambio nominal ($/US$)', 'E', nf(0), 0], ['Colchón acumulado (US$ M)', 'cum', nf(0), 1], ['Actividad (T4-2026 = 100)', 'act', nf(1), 0]].map(c => chart(...c.slice(0, 1), c[1], c[2], c[3], R)).join('');
  $('cmp').innerHTML = `<table><thead><tr><th>Indicador</th>${SCEN.map((s, i) => `<th><span class="d" style="background:${COL(i)}"></span>${s}</th>`).join('')}</tr></thead><tbody>${ITEMS.map(([l, k, f]) => k ? `<tr><td>${l}</td>${Y.map(y => cell(y[k], f)).join('')}</tr>` : gp(l, 4)).join('')}</tbody></table>`;
  const r = R[cur];
  $('det').innerHTML = `<table><thead><tr><th>Concepto</th>${QL.map(q => `<th>${q}</th>`).join('')}</tr></thead><tbody>${QROWS.map(([l, k, f]) => k ? `<tr><td>${l}</td>${r.q[k].map((v, j) => (!j && FLOW.includes(k)) ? '<td>–</td>' : cell(v, f)).join('')}</tr>` : gp(l, 6)).join('')}</tbody></table>`;
}
build(); render();
