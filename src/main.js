import './style.css';
import { DEFAULTS, SCEN, run } from './engine.js';
const A = structuredClone(DEFAULTS), $ = id => document.getElementById(id);
const nf = (d = 0) => v => v.toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d });
const pc = d => v => (v * 100).toLocaleString('es-AR', { minimumFractionDigits: d, maximumFractionDigits: d }) + '%';
// [clave, etiqueta, escala de entrada, ¿por escenario?]
const FIELDS = [
  ['Política y sector externo', [['ca27', 'Cuenta corriente 2027 (% PBI)', 100, 1], ['rho4', 'Riesgo país a fin de 2027 (pb)', 1, 1], ['p', 'Prob. de caída del acuerdo con el FMI (%)', 100, 1], ['pfac', 'Factor de compras del BCRA', 1, 1]]],
  ['Financiamiento (US$ millones)', [['saldo', 'Saldo del programa 2026', 1, 1], ['loc', 'Emisión local en dólares', 1, 1], ['intl', 'Emisión internacional', 1, 1], ['ondem', 'Pagos de ON por trimestre (T2 a T4)', 1, 1]]],
  ['Generales', [['gtr', 'Crecimiento tendencial (%)', 100, 0], ['pi0', 'Inflación inicial de N (% anual)', 1, 0], ['E0', 'Tipo de cambio inicial ($/US$)', 1, 0], ['anc4', 'Ancla de inflación T4-2027 (%)', 1, 0]]],
];
$('ctl').innerHTML = FIELDS.map(([t, fs]) => `<fieldset><legend>${t}</legend>
  <label>Coeficientes del modelo<select data-g="sel"><option value="1">Juego 1 (depreciación expansiva)</option><option value="2">Juego 2 (contractiva)</option></select></label>`.replace(/<label>Coeficientes[^]*?<\/label>/, t === FIELDS[0][0] ? '$&' : '') +
  (t === FIELDS[1][0] ? `<label>Capital de organismos<select data-g="selcap"><option value="2">Presupuesto 2027</option><option value="1">Planilla MECON</option></select></label>` : '') +
  fs.map(([k, l, sc, per]) => per ? `<label>${l}</label>` + SCEN.map((s, i) => `<label>&nbsp;&nbsp;${s}<input type="number" step="any" data-k="${k}" data-i="${i}" data-sc="${sc}" value="${+(A[k][i] * sc).toFixed(4)}"></label>`).join('')
    : `<label>${l}<input type="number" step="any" data-k="${k}" data-sc="${sc}" value="${+(A[k] * sc).toFixed(4)}"></label>`).join('') + '</fieldset>').join('');
$('ctl').addEventListener('input', e => {
  const t = e.target, d = t.dataset;
  if (d.g) A[d.g] = +t.value; else if (t.value !== '') { const v = +t.value / +d.sc; d.i === undefined ? A[d.k] = v : A[d.k][+d.i] = v; }
  render();
});
$('sc').innerHTML = SCEN.map((s, i) => `<option value="${i}">${s}</option>`).join(''); $('sc').onchange = render;
const ITEMS = [['Cuenta corriente', 'ca', pc(2)], ['Crecimiento del producto', 'growth', pc(1)], ['Inflación IPC, promedio anualizado (%)', 'cpi', nf(1)], ['Inflación IPC T4-2027 (%)', 'cpiT4', nf(1)],
  ['Tipo de cambio nominal a fin de 2027 ($/US$)', 'E', nf()], ['Tipo de cambio real a fin de 2027 (ref. = 1)', 'q', nf(3)], ['Tasa de interés, promedio (%)', 'i', nf(1)],
  ['Empleo, desvío respecto de la referencia', 'emp', pc(2)], ['Riesgo país a fin de 2027 (pb)', 'rho', nf()], ['Compras de divisas del BCRA (US$ M)', 'pur', nf()],
  ['Colchón acumulado a septiembre (US$ M)', 'cum3', nf()], ['Colchón acumulado a diciembre (US$ M)', 'cum4', nf()], ['Compras adicionales necesarias en T4 (US$ M)', 'need', nf()],
  ['Variación de reservas en 2027 (US$ M)', 'dR', nf()], ['Reservas brutas a fin de 2027, ilustrativo (US$ M)', 'reservas', nf()], ['Flujo neto de ON (US$ M)', 'onNet', nf()], ['Usos totales en moneda extranjera (US$ M)', 'uses', nf()]];
const QL = ['T4-2026', 'T1-2027', 'T2-2027', 'T3-2027', 'T4-2027'];
const QROWS = [['Compras de divisas del BCRA (US$ M)', 'pur', nf()], ['Total fuentes (US$ M)', 'src', nf()], ['Total usos (US$ M)', 'uses', nf()], ['Resultado neto (US$ M)', 'net', nf()], ['Colchón acumulado (US$ M)', 'cum', nf()],
  ['Reservas brutas, ilustrativo (US$ M)', 'reservas', nf()], ['Actividad (T4-2026 = 100)', 'act', nf(1)], ['Inflación del sector N (% anual)', 'piN', nf(1)], ['Inflación IPC (% anual)', 'cpi', nf(1)],
  ['Tipo de cambio nominal ($/US$)', 'E', nf()], ['Tipo de cambio real (ref. = 1)', 'q', nf(3)], ['Tasa de interés (% anual)', 'i', nf(1)], ['Riesgo país (pb)', 'rho', nf()]];
const cell = (v, f) => `<td class="${v < 0 ? 'n' : ''}">${f(v)}</td>`;
function render() {
  $('ctl').querySelectorAll('[data-g]').forEach(s => s.value = A[s.dataset.g]);
  const R = SCEN.map((_, i) => run(A, i));
  $('cmp').innerHTML = `<table><tr><th>Indicador</th>${SCEN.map(s => `<th>${s}</th>`).join('')}</tr>${ITEMS.map(([l, k, f]) => `<tr><td>${l}</td>${R.map(r => cell(r.y[k], f)).join('')}</tr>`).join('')}</table>`;
  const r = R[+$('sc').value];
  $('det').innerHTML = `<table><tr><th>Concepto</th>${QL.map(q => `<th>${q}</th>`).join('')}</tr>${QROWS.map(([l, k, f]) => `<tr><td>${l}</td>${r.q[k].map((v, j) => (j === 0 && ['pur', 'src', 'uses', 'net', 'cum'].includes(k)) ? '<td>–</td>' : cell(v, f)).join('')}</tr>`).join('')}</table>`;
}
render();
