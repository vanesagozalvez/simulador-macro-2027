// Motor del simulador: port a JS de la lógica de build_xlsx.py (hojas Base/Optimista/Pesimista).
import SA from './data/set_A.json'; import SB from './data/set_B.json'; import DM from './data/deuda_mensual.json';
const sum = a => a.reduce((x, y) => x + y, 0), q3 = v => [0, 3, 6, 9].map(a => sum(v.slice(a, a + 3)));
const KEYS = ['dPsi','dPur','dp','drho','dtx','dtm','dG','dYT0'], OUT = ['dYN','di','dq','dYtot','dEmp','dgap'];
const FMI_Q = q3(DM.cap27.fmi.slice(0, 12));
const ORG_Q = [0,1,2,3].map(k => ['birf','bid','otros','oficiales'].reduce((s, n) => s + q3(DM.cap27[n].slice(0, 12))[k], 0));
const CAL = { cap:[1191,5708,1774,6141,4845], int:[1505,3337,1437,3275,1395], bop:[0,0,2625,0,2562.5] };
const FMI_PRES = [1.33,.58,0,1.48,0,0,2.25,.62,0,1.58,0,0];
export const SCEN = ['Base','Optimista','Pesimista'];
// Parámetros con 3 valores = [base, optimista, pesimista]
export const DEFAULTS = {
  sel:1, selcap:2, gdp:700000, ca26:.006, ca27:[0,.005,-.005], gtr:.021, pistar:.03, E0:1507, pi0:33, anc0:28, anc4:18,
  dtx:.75, dtm:.25, dG:0, onq1:2700, ondemq1:2600, ondem:[300,180,420], onca:0,
  fxpl:1778.8, bidpl:2, otrospl:2, restopl:2.8, pfac:[1,1.15,.75], oct27:0,
  m:[1158,1557,1671,2769,2596,1418,2162,768,473],
  saldo:[1850,3700,0], imf:850, imfq:[2,2,4], ooii:4200, ooiip:[1,1,.5], bil:2000, bilp:[1,1,0], priv:1500, privp:[.5,1,0], sh1:.5,
  intra:1800, loc:[0,5000,0], intl:[0,4000,0], p:[.05,.02,.10], pref:.05, rho0:636, rho4:[636,450,900],
  gamma:.5, theta:.6, kappa:.4, betaE:.1, betai:.1, betae:.3, a:.35, e4:.4, i0:25, eps0:20, R0:48653,
};
function adjustment(A) {
  if (A.selcap !== 2) return [0,0,0,0,0];
  const fm = q3(FMI_PRES.map(v => v * 1e6 / A.fxpl)), h14 = (A.bidpl + A.otrospl + A.restopl) * 1e6 / A.fxpl, h15 = sum(ORG_Q);
  return [0, ...[0,1,2,3].map(k => fm[k] - FMI_Q[k] + h14 * ORG_Q[k] / h15 - ORG_Q[k])];
}
export function run(A, s) {
  const g = k => Array.isArray(A[k]) ? A[k][s] : A[k], S = A.sel === 1 ? SA : SB, { SCALE, Ytot } = SA, P = SA.P;
  const J = [1,2,3,4], z = () => [0,0,0,0,0], adj = adjustment(A);
  const sd = CAL.cap.map((c, j) => c + CAL.int[j] + adj[j]), bo = CAL.bop, sdTot = sum(sd.slice(1));
  const m = A.m, seas = [0,1,2].map(k => sum(m.slice(3 * k, 3 * k + 3))), avgm = sum(m) / 9, avgq = sum(m) / 3;
  const pur = [0, ...[...seas, g('oct27') + 2 * avgm].map(v => g('pfac') * v)];
  const onIn = [0, g('onq1'), 0, 0, 0], onDem = [0, A.ondemq1 / 2, g('ondem'), g('ondem'), g('ondem')].map(v => v * (1 - A.onca));
  const onNet = z().map((_, j) => j ? onIn[j] - onDem[j] : 0);
  const f = { pur, on: onNet, saldo: [0, g('saldo'), 0, 0, 0], imf: z().map((_, j) => j === g('imfq') ? g('imf') : 0),
    ooii: [0, g('ooii') * g('ooiip') * g('sh1'), g('ooii') * g('ooiip') * (1 - g('sh1')), 0, 0],
    bil: [0, g('bil') * g('bilp') * g('sh1'), g('bil') * g('bilp') * (1 - g('sh1')), 0, 0],
    priv: [0, g('priv') * g('privp') * g('sh1'), g('priv') * g('privp') * (1 - g('sh1')), 0, 0],
    intra: z().map((_, j) => j ? g('intra') * sd[j] / sdTot : 0), loc: [0, 0, g('loc') / 2, g('loc') / 2, 0], intl: [0, 0, 0, g('intl'), 0] };
  const src = z().map((_, j) => j ? sum(Object.values(f).map(v => v[j])) : 0), uses = sd.map((v, j) => j ? v + bo[j] : 0);
  const net = src.map((v, j) => v - uses[j]); let c = 0; const cum = net.map((v, j) => j ? (c += v) : 0);
  const dR = z().map((_, j) => j ? f.pur[j] + f.on[j] + f.imf[j] + f.ooii[j] + f.bil[j] + f.priv[j] + f.loc[j] + f.intl[j] - (sd[j] - f.intra[j]) - bo[j] : 0);
  let r0 = 0; const dRc = dR.map(v => r0 += v), reservas = dRc.map(v => A.R0 + v);
  const caP = [A.ca26, ...J.map(() => g('ca27'))], caUsd = caP.map(v => v * A.gdp / 4), caRef = A.ca26 * A.gdp / 4;
  const rho = z().map((_, j) => A.rho0 + (g('rho4') - A.rho0) * j / 4), pj = [A.pref, ...J.map(() => g('p'))];
  const und = j => f.pur[j] + onNet[j] - (j < 4 ? g('pfac') * (seas[j - 1] - avgq) : 0);
  const sh = [ z().map((_, j) => j ? (-(caUsd[j] - caRef) + (onDem[j] - onIn[j])) * 4 / SCALE : 0),
    z().map((_, j) => j ? (und(j) - avgq) * 4 / SCALE : 0), pj.map((v, j) => j ? (v - A.pref) * 100 : 0), rho.map((v, j) => j ? (v - A.rho0) / 100 : 0),
    z().map((_, j) => A.dtx * j), z().map((_, j) => A.dtm * j), z().map((_, j) => j ? A.dG : 0), z()];
  const r = {}; OUT.forEach(o => r[o] = z().map((_, j) => sum(KEYS.map((k, i) => S.unit[k][o] * sh[i][j]))));
  const anc = z().map((_, j) => A.anc0 + (A.anc4 - A.anc0) * j / 4), q = r.dq.map(v => 1 + v);
  const i = r.di.map((v, j) => j ? A.i0 + 100 * v : A.i0), eps = pj.map((v, j) => j ? A.eps0 + 100 * A.e4 * (v - A.pref) : A.eps0);
  const gap = r.dgap.map((v, j) => 100 * S.info.xgap + (j ? v : 0)), emp = r.dEmp.map(v => v / (100 + P.lT * P.YT00));
  const act = z().map((_, j) => j ? 100 * (1 + A.gtr) ** (j / 4) * (1 + r.dYtot[j] / Ytot) : 100);
  const piN = z(), E = z(), dlnE = z(), piT = z(), cpi = z(); piN[0] = A.pi0; E[0] = A.E0; cpi[0] = (1 - A.a) * A.pi0;
  for (const j of J) {
    piN[j] = A.gamma * piN[j-1] + (1 - A.gamma) * (A.theta * piN[j-1] + (1 - A.theta) * anc[j] + A.betae * (eps[j] - A.eps0)) + A.kappa * gap[j] + A.betaE * dlnE[j-1] + A.betai * (i[j] - A.i0);
    E[j] = E[j-1] * (q[j] / q[j-1]) * (1 + piN[j] / 400) / (1 + A.pistar * 100 / 400);
    dlnE[j] = 400 * Math.log(E[j] / E[j-1]); piT[j] = dlnE[j] + A.pistar * 100; cpi[j] = A.a * piT[j] + (1 - A.a) * piN[j];
  }
  const T = v => sum(v.slice(1)), avg = v => T(v) / 4;
  return { q: { pur, src, uses, net, cum, dRc, reservas, act, piN, E, cpi, q, i, emp, gap, rho }, y: {
    ca: g('ca27'), growth: (1 + A.gtr) * (1 + avg(r.dYtot) / Ytot) - 1, cpi: avg(cpi), cpiT4: cpi[4], E: E[4], q: q[4], i: avg(i), emp: avg(emp), rho: rho[4],
    pur: T(pur), cum3: cum[3], cum4: cum[4], need: Math.max(0, -cum[4]), dR: dRc[4], reservas: reservas[4], onNet: T(onNet), uses: T(uses) } };
}
