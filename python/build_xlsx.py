# -*- coding: utf-8 -*-
import json, csv, sys
SEL = int(sys.argv[1]); OUT = sys.argv[2]; SENS = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

SA = json.load(open('set_A.json')); SB = json.load(open('set_B.json'))
unit, info = SA['unit'], SA['info']; unitB, infoB = SB['unit'], SB['info']; SCALE = SA['SCALE']; Ytot = SA['Ytot']; P1 = SA['P']

DM = json.load(open('deuda_mensual.json'))
qsum = lambda v: [sum(v[a:b]) for a, b in [(0, 3), (3, 6), (6, 9), (9, 12)]]
FMI_CAP_Q = qsum(DM['cap27']['fmi'][:12])
ORG_CAP_Q = [sum(x) for x in zip(*[qsum(DM['cap27'][k][:12]) for k in ('birf', 'bid', 'otros', 'oficiales')])]
FN = 'Arial'
f_norm = Font(name=FN, size=10); f_bold = Font(name=FN, size=10, bold=True)
f_in = Font(name=FN, size=10, color='0000FF'); f_link = Font(name=FN, size=10, color='008000')
f_h = Font(name=FN, size=10, bold=True, color='FFFFFF'); f_t = Font(name=FN, size=14, bold=True, color='1F3864')
fill_h = PatternFill('solid', fgColor='1F3864'); fill_s = PatternFill('solid', fgColor='D9E2F3'); fill_y = PatternFill('solid', fgColor='FFFF00')
thin = Side(style='thin', color='BFBFBF'); bd = Border(top=thin, bottom=thin, left=thin, right=thin)
NUM = '#,##0;(#,##0);-'; NUM1 = '#,##0.0;(#,##0.0);-'; NUM3 = '0.000;(0.000);-'; PCT = '0.0%;(0.0%);-'; PCT2 = '0.00%;(0.00%);-'

wb = Workbook()
def put(ws, ref, v, font=f_norm, fmt=None, fill=None, bold=False, align=None, wrap=False):
    c = ws[ref]; c.value = v; c.font = Font(name=FN, size=10, bold=bold or font.bold, color=font.color) if bold else font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if align or wrap: c.alignment = Alignment(horizontal=align, vertical='top', wrap_text=wrap)
    return c
def header(ws, row, labels, start=1):
    for k, lab in enumerate(labels):
        c = ws.cell(row=row, column=start+k, value=lab); c.font = f_h; c.fill = fill_h; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = bd
def section(ws, row, text, ncol=8):
    for k in range(1, ncol+1): ws.cell(row=row, column=k).fill = fill_s
    c = ws.cell(row=row, column=1, value=text); c.font = f_bold

# =============================== Leyenda
ws = wb.active; ws.title = 'Leyenda'
put(ws, 'A1', 'Simulador macro trimestral 2027: escenarios base, optimista y pesimista', f_t)
lines = [
 'Modelo: IS–LM–BP de dos sectores (versión 6), linealizado en torno a la posición de referencia de 2026. Las respuestas por unidad de shock se obtienen del script verificacion_modelo_v6.py y de la recalibración del archivo calib.py (ver hoja Coeficientes).',
 'Período: T4-2026 (referencia) y T1 a T4 de 2027. Flujos de balanza de pagos en US$ millones por trimestre. El bloque macro se expresa como desvíos respecto de la referencia de 2026 y se acumula sobre una tendencia de crecimiento.',
 'Colores: azul = dato de entrada editable; negro = fórmula; verde = vínculo a otra hoja; fondo amarillo = supuesto clave a revisar.',
 'Columna Origen de la hoja Supuestos: USUARIO = dato dado por el usuario y no verificado por mí, a pedido suyo; MECON = planilla de deuda pública al 30/06/2026; FMI = archivo extforth; ANALISTA = supuesto propuesto por mí, no verificado, editable.',
 'Las hojas Base, Optimista y Pesimista tienen la misma estructura. Cambie los supuestos en la hoja Supuestos (celdas azules) y todo se recalcula, salvo la hoja Coeficientes, que son valores del script.',
 'Limitaciones: el bloque macro usa un modelo lineal con parámetros ilustrativos (no estimados); no contiene la defensa del tipo de cambio por venta de reservas ni el régimen de techo de la banda; el escenario pesimista no incluye la caída del acuerdo con el FMI (ver nota en Supuestos). Las cifras son resultados condicionados a los supuestos, no pronósticos.',
 'Obligaciones negociables: ingresan US$ 4.400 millones pendientes de liquidación (T4-2026 y T1-2027) y las empresas demandan US$ 2.600 millones en T4-2026 y T1-2027 más 300 por trimestre en T2 a T4 de 2027 (base). El flujo neto se suma a las compras del BCRA y a las reservas; el reparto del ingreso entre T4-2026 y T1-2027 es un supuesto del analista calibrado para que el neto de 2027 sea +500. Los intereses de las ON pertenecen a la cuenta corriente: si el objetivo ya los contiene hay doble conteo (parámetro en Supuestos).',
 'Capital de organismos internacionales: la hoja Presupuesto_2027 convierte a dólares las amortizaciones del Cuadro 16 (FMI, por mes) y los totales del texto del informe (BID, otros y resto) y reemplaza el capital de la planilla MECON (no se suma) según el selector de la hoja Supuestos; el cuadro y el archivo del FMI no coinciden en los meses de pago.',
 'Ejemplo de lectura: en la hoja Comparativo, la fila Cobertura acumulada a septiembre indica el colchón en US$ millones antes de octubre de 2027, mes en el que se supone que no hay compras por las elecciones.',
]
for k, t in enumerate(lines): put(ws, f'A{3+k}', t, f_norm, wrap=True); ws.row_dimensions[3+k].height = 48
ws.column_dimensions['A'].width = 140

# =============================== Supuestos
S = wb.create_sheet('Supuestos'); SR = {}
put(S, 'A1', 'Supuestos por escenario', f_t)
header(S, 3, ['Parámetro', 'Unidad', 'Base', 'Optimista', 'Pesimista', 'Origen', 'Nota'])
r = 4
def sec(txt):
    global r; section(S, r, txt, 7); r += 1
def row(key, label, unit_, base, opt=None, pes=None, origin='USUARIO', note='', fmt=NUM, key_assump=False):
    global r
    SR[key] = r
    put(S, f'A{r}', label); put(S, f'B{r}', unit_)
    for col, v in zip('CDE', (base, opt, pes)):
        if v is None:
            put(S, f'{col}{r}', f'=C{r}', f_norm, fmt)
        else:
            put(S, f'{col}{r}', v, f_in, fmt, fill=fill_y if key_assump else None)
    put(S, f'F{r}', origin); put(S, f'G{r}', note, wrap=True); r += 1
sec('Magnitudes generales')
row('gdp', 'PBI 2026 en dólares', 'US$ millones', 700000, origin='USUARIO', note='Dato del usuario; se usa como escala fija del modelo para 2026 y 2027.')
row('g26', 'Crecimiento 2026', '% anual', 0.021, origin='USUARIO', fmt=PCT)
row('inf26', 'Inflación 2026', '% anual', 0.31, origin='USUARIO', fmt=PCT)
row('ca26', 'Cuenta corriente 2026', '% del PBI', 0.006, origin='USUARIO', fmt=PCT2, note='Superávit; es la referencia respecto de la cual se miden los shocks de 2027.')
row('xs', 'Exportaciones', '% del PBI', 0.25, origin='USUARIO', fmt=PCT)
row('ms', 'Importaciones', '% del PBI', 0.15, origin='USUARIO', fmt=PCT, note='Con exportaciones de 25%, el peso del sector transable se toma como 40% del PBI total.')
row('gtr', 'Crecimiento tendencial 2027', '% anual', 0.021, origin='ANALISTA', fmt=PCT, key_assump=True, note='Supuesto de continuidad con 2026; no dado por el usuario.')
row('pistar', 'Inflación externa', '% anual', 0.03, origin='ANALISTA', fmt=PCT)
row('E0', 'Tipo de cambio mayorista inicial (T4-2026)', '$ por US$', 1507, origin='ANALISTA', note='Cercano al valor de mediados de septiembre de 2026 según prensa; verificar.')
row('pi0', 'Inflación del sector N inicial (anualizada)', '% anual', 33.0, origin='ANALISTA', fmt=NUM1, key_assump=True, note='Supuesto: ritmo reciente de servicios y regulados; no verificado.')
row('anc0', 'Ancla de expectativas de inflación, T4-2026', '% anual', 28.0, origin='ANALISTA', fmt=NUM1)
row('anc4', 'Ancla de expectativas de inflación, T4-2027', '% anual', 18.0, origin='ANALISTA', fmt=NUM1)
sec('Selector de coeficientes del bloque macro')
row('sel', 'Juego de coeficientes (1 = calibración heredada; 2 = alternativa con depreciación contractiva)', 'número 1 o 2', SEL, origin='ANALISTA', fmt='0', key_assump=True, note='Juego 1: propensión a gastar del sector transable 0,40 e indexación salarial 0,60 (la depreciación es expansiva). Juego 2: 0,10 y 0,20 (la depreciación es contractiva). Es una decisión de calibración que debe validarse.')
sec('Cuenta corriente y política')
row('ca27', 'Cuenta corriente 2027', '% del PBI', 0.0, 0.005, -0.005, 'USUARIO', fmt=PCT2, key_assump=True, note='Base 0%, optimista +0,5%, pesimista −0,5%, dados por el usuario.')
row('dtx', 'Baja trimestral de derechos de exportación', 'pp por trimestre', 0.75, origin='ANALISTA', fmt=NUM3, note='Derivado del cronograma del Decreto 423/2026 (soja de 24% a 21% hasta diciembre de 2027), repartido en forma lineal.')
row('dtm', 'Baja trimestral del arancel efectivo de importación', 'pp por trimestre', 0.25, origin='ANALISTA', fmt=NUM3, note='Supuesto: apertura gradual; no hay cronograma verificado.')
row('dG', 'Variación del gasto público (unidades del modelo)', 'unidades', 0.0, origin='ANALISTA', fmt=NUM3)
sec('Obligaciones negociables en dólares de empresas argentinas (liquidaciones pendientes y pagos)')
row('onpend', 'Liquidación pendiente en el MULC de ON ya emitidas (a octubre de 2026)', 'US$ millones', 4400, origin='USUARIO', note='Dato del BCRA verificado por el usuario: emitido 23.700 millones contra 19.200 liquidados. Ingresa en T4-2026 y T1-2027.')
row('onq1', '  de ello, ingresa en T1-2027', 'US$ millones', 2700, origin='ANALISTA', key_assump=True, note='El usuario no fija el reparto entre T4-2026 y T1-2027. 2.700 en T1 (y 1.700 en T4-2026) reproduce el neto de +500 de 2027; un reparto igual daría 0.')
row('ondemq1', 'Demanda por pagos de ON en T4-2026 y T1-2027 (estimación del BCRA)', 'US$ millones', 2600, origin='USUARIO', note='Vencimientos financieros y recompras anunciadas de empresas y provincias. Se reparte por igual: 1.300 en T4-2026 y 1.300 en T1-2027.')
row('ondem', 'Demanda por pagos de ON en cada trimestre de T2, T3 y T4 de 2027', 'US$ millones por trimestre', 300, 180, 420, 'USUARIO', note='Base: 300 por trimestre (usuario). Optimista y pesimista: menos y más 40% (analista).')
row('onca', '  fracción de esa demanda ya contenida en la cuenta corriente objetivo', '% de la demanda', 0.0, origin='ANALISTA', fmt=PCT, note='Los intereses de las ON son renta de inversión y pertenecen a la cuenta corriente. Si el objetivo de cuenta corriente ya los incluye, cargar aquí esa fracción para no contarlos dos veces. Por defecto 0%.')
sec('Capital de organismos internacionales según el Presupuesto 2027 (Cuadro 16 y texto del informe)')
row('selcap', 'Fuente del capital de organismos en los usos (1 = planilla MECON; 2 = Presupuesto 2027)', 'número 1 o 2', 2, origin='USUARIO', fmt='0', key_assump=True, note='Con 2 se reemplaza el capital de FMI y de organismos de la planilla MECON por el del Presupuesto 2027 (no se suma, para no contar dos veces); los intereses siguen siendo los de MECON.')
row('fxpl', 'Tipo de cambio para convertir el Cuadro 16 a dólares', '$ por US$', 1778.8, origin='ANALISTA', fmt=NUM1, key_assump=True, note='Es el cociente entre los 7,84 billones del FMI y los US$4.407 millones de capital del FMI de la planilla MECON, de modo que el total del FMI no cambia y solo cambia el calendario. El Cuadro 16 no informa el tipo de cambio del Presupuesto; es editable.')
row('bidpl', 'BID: amortización de capital 2027', 'billones de $', 2.0, origin='USUARIO', fmt=NUM1, note='Texto del informe (usuario).')
row('otrospl', 'Otros préstamos: amortización de capital 2027', 'billones de $', 2.0, origin='USUARIO', fmt=NUM1)
row('restopl', 'Resto de organismos multilaterales y bilaterales: amortización de capital 2027', 'billones de $', 2.8, origin='USUARIO', fmt=NUM1)
sec('Compras de divisas del BCRA')
row('pfac', 'Factor sobre el espejo de 2026', 'multiplicador', 1.0, 1.15, 0.75, 'USUARIO', fmt=NUM3, key_assump=True, note='Base: espejo de 2026 (usuario). Optimista y pesimista: propuesta del analista.')
row('oct27', 'Compras de octubre de 2027', 'US$ millones', 0.0, origin='USUARIO', note='Cero por las elecciones (usuario).')
row('novdic', 'Compras mensuales de noviembre y diciembre de 2027 (antes del factor)', 'US$ millones por mes', '=AVERAGE(C{m1}:C{m9})', origin='ANALISTA', note='Supuesto: igual al promedio mensual de enero a septiembre de 2026; depende del resultado electoral.')
S_novdic_row = SR['novdic']
sec('Compras mensuales del BCRA en 2026 (US$ millones)')
mnames = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre']; mvals = [1158,1557,1671,2769,2596,1418,2162,768,473]
for k, (mn, mv) in enumerate(zip(mnames, mvals)):
    row(f'm{k+1}', mn + ' 2026', 'US$ millones', mv, origin='USUARIO', note='Serie dada por el usuario.' if k == 0 else '')
# arreglar fórmula del promedio nov-dic (refiere a filas de la serie)
S[f'C{S_novdic_row}'].value = f"=AVERAGE(C{SR['m1']}:C{SR['m9']})"; S[f'C{S_novdic_row}'].font = f_norm
for col in 'DE': S[f'{col}{S_novdic_row}'].value = f'=C{S_novdic_row}'
sec('Fuentes de financiamiento en moneda extranjera (US$ millones)')
row('saldo', 'Saldo del programa financiero 2026 arrastrado', 'US$ millones', 1850, 3700, 0, 'USUARIO', key_assump=True, note='Base: 50% de 3.700 (usuario). Optimista: 100%. Pesimista: 0 (propuestas del analista).')
row('imf', 'Desembolso del FMI (cuarta revisión)', 'US$ millones', 850, origin='USUARIO', note='Los 1.700 incluyen los unos 870 de la tercera revisión, de modo que en 2027 solo hay 850 (usuario).')
row('imfq', 'Trimestre del desembolso del FMI', 'número 1 a 4', 2, 2, 4, 'USUARIO', fmt='0', note='Base: T2 (usuario). Pesimista: se demora al T4 (analista).')
row('ooii', 'Organismos internacionales: programa 2027', 'US$ millones', 4200, origin='USUARIO')
row('ooiip', '  % considerado', '% del programa', 1.0, 1.0, 0.5, 'USUARIO', fmt=PCT, note='Base 100% (usuario). Pesimista 50% (analista).')
row('bil', 'Préstamo bilateral', 'US$ millones', 2000, origin='USUARIO')
row('bilp', '  % considerado', '% del programa', 1.0, 1.0, 0.0, 'USUARIO', fmt=PCT, note='Pesimista 0% (analista).')
row('priv', 'Privatizaciones: programa 2027', 'US$ millones', 1500, origin='USUARIO')
row('privp', '  % considerado', '% del programa', 0.5, 1.0, 0.0, 'USUARIO', fmt=PCT, note='Base 50% (usuario). Optimista 100% y pesimista 0% (analista).')
row('sh1', 'Reparto de organismos, bilateral y privatizaciones en T1', '% del total', 0.5, origin='USUARIO', fmt=PCT, note='Se reparten en los dos primeros trimestres (usuario); se supone mitad y mitad.')
row('intra', 'Roll over intra sector público', 'US$ millones', 1800, origin='USUARIO', note='100% del programa; se asigna en proporción al servicio de cada trimestre.')
row('loc', 'Emisión local de deuda en dólares', 'US$ millones', 0, 5000, 0, 'USUARIO', note='Base: cero (usuario). Optimista: el monto del programa, repartido entre T2 y T3 (analista).')
row('intl', 'Emisión internacional de deuda', 'US$ millones', 0, 4000, 0, 'USUARIO', note='Base y pesimista: cero (usuario). Optimista: propuesta del analista, en T3.')
sec('Riesgo y expectativas')
row('p', 'Probabilidad de caída del acuerdo con el FMI (por trimestre)', 'probabilidad', 0.05, 0.02, 0.10, 'ANALISTA', fmt=PCT, key_assump=True, note='Es la probabilidad percibida; no modela la caída efectiva del acuerdo.')
row('pref', 'Probabilidad de referencia', 'probabilidad', 0.05, origin='ANALISTA', fmt=PCT)
row('rho0', 'Riesgo país inicial', 'puntos básicos', 636, origin='USUARIO', fmt=NUM, note='Valor del 1 de octubre de 2026 según fuentes consultadas.')
row('rho4', 'Riesgo país a fin de 2027', 'puntos básicos', 636, 450, 900, 'ANALISTA', fmt=NUM, key_assump=True, note='Trayectoria lineal desde el valor inicial; propuesta del analista.')
S.column_dimensions['A'].width = 58; S.column_dimensions['B'].width = 20
for c_ in 'CDE': S.column_dimensions[c_].width = 14
S.column_dimensions['F'].width = 12; S.column_dimensions['G'].width = 70
S.freeze_panes = 'C4'

# =============================== Presupuesto_2027
B = wb.create_sheet('Presupuesto_2027')
put(B, 'A1', 'Amortizaciones de capital de organismos internacionales en 2027 según el Presupuesto (Cuadro 16 y texto del informe)', f_t)
put(B, 'A2', 'Fuente: archivo Datos Consolidados de los Cuadros 11 al 20 del Informe PLP2027 (Cuadro 16, en billones de pesos) y texto del informe aportado por el usuario. Conversión a dólares al tipo de cambio de la hoja Supuestos.', f_norm)
header(B, 4, ['Concepto', 'Unidad'] + ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'] + ['2027'])
put(B, 'A5', 'FMI: amortización de capital (acuerdo de facilidades extendidas 2022)'); put(B, 'B5', 'billones de $')
for j, v in enumerate([1.33, 0.58, 0, 1.48, 0, 0, 2.25, 0.62, 0, 1.58, 0, 0]): put(B, f'{L(3+j)}5', v, f_in, '0.00;(0.00);-')
put(B, 'O5', '=SUM(C5:N5)', f_norm, '0.00')
put(B, 'A6', 'Tipo de cambio de conversión'); put(B, 'B6', '$ por US$')
for j in range(12): put(B, f'{L(3+j)}6', f"=Supuestos!$C${SR['fxpl']}", f_link, NUM1)
put(B, 'A7', 'FMI: amortización de capital'); put(B, 'B7', 'US$ millones')
for j in range(12): put(B, f'{L(3+j)}7', f'={L(3+j)}5*1000000/{L(3+j)}6', f_norm, NUM)
put(B, 'O7', '=SUM(C7:N7)', f_norm, NUM)
header(B, 9, ['Concepto', 'Unidad', 'T4-2026', 'T1-2027', 'T2-2027', 'T3-2027', 'T4-2027', '2027'])
put(B, 'A10', 'FMI: capital según Presupuesto'); put(B, 'B10', 'US$ millones')
put(B, 'C10', 0, f_norm, NUM); put(B, 'D10', '=SUM(C7:E7)', f_norm, NUM); put(B, 'E10', '=SUM(F7:H7)', f_norm, NUM); put(B, 'F10', '=SUM(I7:K7)', f_norm, NUM); put(B, 'G10', '=SUM(L7:N7)', f_norm, NUM); put(B, 'H10', '=SUM(D10:G10)', f_norm, NUM)
put(B, 'A11', 'FMI: capital según planilla MECON'); put(B, 'B11', 'US$ millones'); put(B, 'C11', 0, f_in, NUM)
for j, v in enumerate(FMI_CAP_Q): put(B, f'{L(4+j)}11', round(v, 1), f_in, NUM)
put(B, 'H11', '=SUM(D11:G11)', f_norm, NUM)
put(B, 'A12', 'FMI: diferencia (Presupuesto menos MECON)'); put(B, 'B12', 'US$ millones')
for j in range(5): put(B, f'{L(3+j)}12', f'={L(3+j)}10-{L(3+j)}11', f_norm, NUM)
put(B, 'A14', 'BID, otros préstamos y resto de multilaterales y bilaterales: capital según Presupuesto'); put(B, 'B14', 'US$ millones')
put(B, 'H14', f"=(Supuestos!$C${SR['bidpl']}+Supuestos!$C${SR['otrospl']}+Supuestos!$C${SR['restopl']})*1000000/Supuestos!$C${SR['fxpl']}", f_link, NUM)
put(B, 'A15', 'Capital de BIRF, BID, otros y oficiales según planilla MECON (perfil trimestral)'); put(B, 'B15', 'US$ millones'); put(B, 'C15', 0, f_in, NUM)
for j, v in enumerate(ORG_CAP_Q): put(B, f'{L(4+j)}15', round(v, 1), f_in, NUM)
put(B, 'H15', '=SUM(D15:G15)', f_norm, NUM)
put(B, 'A16', 'Otros organismos: capital según Presupuesto, con el perfil trimestral de MECON'); put(B, 'B16', 'US$ millones'); put(B, 'C16', 0, f_norm, NUM)
for j in range(4): put(B, f'{L(4+j)}16', f'=$H$14*{L(4+j)}15/$H$15', f_norm, NUM)
put(B, 'H16', '=SUM(D16:G16)', f_norm, NUM)
put(B, 'A17', 'Otros organismos: diferencia (Presupuesto menos MECON)'); put(B, 'B17', 'US$ millones')
for j in range(5): put(B, f'{L(3+j)}17', f'={L(3+j)}16-{L(3+j)}15', f_norm, NUM)
put(B, 'A18', 'Ajuste total del capital de organismos (Presupuesto menos MECON)', f_bold); put(B, 'B18', 'US$ millones')
for j in range(5): put(B, f'{L(3+j)}18', f'={L(3+j)}12+{L(3+j)}17', f_bold, NUM)
put(B, 'H18', '=SUM(D18:G18)', f_bold, NUM)
put(B, 'A20', 'Nota: el Cuadro 16 asigna el capital del FMI a enero, febrero, abril, julio, agosto y octubre, mientras que el archivo del FMI (extforth) lo ubica en marzo, abril, junio, septiembre, octubre y diciembre. Las demás categorías no tienen calendario mensual en el informe; se reparten con el perfil de MECON.', f_norm, wrap=True)
B.column_dimensions['A'].width = 74; B.column_dimensions['B'].width = 14
for k in range(3, 16): B.column_dimensions[L(k)].width = 11

# =============================== Calendario_FX
K = wb.create_sheet('Calendario_FX')
put(K, 'A1', 'Servicio de deuda en moneda extranjera por trimestre (US$ millones)', f_t)
put(K, 'A2', 'Fuente: planilla de deuda pública de la Administración Central al 30/06/2026 (MECON), agrupada por trimestre; BOPREAL Serie 1 según prospecto y datos del usuario.', f_norm)
header(K, 4, ['Concepto', 'Unidad', 'T4-2026', 'T1-2027', 'T2-2027', 'T3-2027', 'T4-2027', '2027'])
cal = {
 'Capital en moneda extranjera': [1191.0, 5708.0, 1774.0, 6141.0, 4845.0],
 'Intereses en moneda extranjera': [1505.0, 3337.0, 1437.0, 3275.0, 1395.0],
 'FMI (capital más cargos)': [1140.0, 1583.0, 1943.0, 2009.0, 1936.0],
 'Organismos (BIRF, BID y otros)': [1050.0, 1038.0, 1053.0, 1114.0, 1063.0],
}
KR = {}
rr = 5
for k_, v in cal.items():
    put(K, f'A{rr}', k_); put(K, f'B{rr}', 'US$ millones')
    for j, x in enumerate(v): put(K, f'{L(3+j)}{rr}', x, f_in, NUM)
    put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); KR[k_] = rr; rr += 1
KR['tot'] = rr
put(K, f'A{rr}', 'Servicio total en moneda extranjera (MECON)', f_bold); put(K, f'B{rr}', 'US$ millones')
for j in range(5): put(K, f'{L(3+j)}{rr}', f'={L(3+j)}5+{L(3+j)}6', f_norm, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); rr += 1
KR['resto'] = rr
put(K, f'A{rr}', 'Resto (bonos, letras, banca, oficiales, avales)'); put(K, f'B{rr}', 'US$ millones')
for j in range(5): put(K, f'{L(3+j)}{rr}', f'={L(3+j)}{KR["tot"]}-{L(3+j)}7-{L(3+j)}8', f_norm, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); rr += 1
KR['adj'] = rr
put(K, f'A{rr}', 'Ajuste: capital de organismos según Presupuesto 2027 menos MECON'); put(K, f'B{rr}', 'US$ millones')
put(K, f'C{rr}', 0, f_norm, NUM)
for j, c_ in enumerate('DEFG'): put(K, f'{c_}{rr}', f"=IF(Supuestos!$C${SR['selcap']}=2,Presupuesto_2027!{c_}18,0)", f_link, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); rr += 1
KR['totadj'] = rr
put(K, f'A{rr}', 'Servicio total en moneda extranjera usado en el modelo', f_bold); put(K, f'B{rr}', 'US$ millones')
for j in range(5): put(K, f'{L(3+j)}{rr}', f'={L(3+j)}{KR["tot"]}+{L(3+j)}{KR["adj"]}', f_bold, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_bold, NUM); rr += 1
KR['bop'] = rr
put(K, f'A{rr}', 'BOPREAL Serie 1 (capital e intereses)'); put(K, f'B{rr}', 'US$ millones')
for j, x in enumerate([0, 0, 2625.0, 0, 2562.5]): put(K, f'{L(3+j)}{rr}', x, f_in, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); put(K, f'I{rr}', 'Cuotas de 2.500 el 30/04/2027 y el 1/11/2027 más intereses de 125 y 62,5 (datos del usuario).', f_norm); rr += 1
KR['all'] = rr
put(K, f'A{rr}', 'Usos totales del sector público consolidado', f_bold); put(K, f'B{rr}', 'US$ millones')
for j in range(5): put(K, f'{L(3+j)}{rr}', f'={L(3+j)}{KR["totadj"]}+{L(3+j)}{KR["bop"]}', f_norm, NUM)
put(K, f'H{rr}', f'=SUM(D{rr}:G{rr})', f_norm, NUM); rr += 2
put(K, f'A{rr}', 'Nota: la planilla del FMI (extforth) en DEG coincide con el perfil trimestral de la fila FMI a un tipo implícito de unos 1,29 US$ por DEG; a 1,377 el servicio de 2027 sería unos US$500 millones mayor.', f_norm, wrap=True)
K.column_dimensions['A'].width = 52
for c_ in 'BCDEFGH': K.column_dimensions[c_].width = 14

# =============================== Coeficientes
Co = wb.create_sheet('Coeficientes')
put(Co, 'A1', 'Coeficientes del modelo linealizado y parámetros (valores del script; no recalculan)', f_t)
put(Co, 'A2', 'Respuestas del régimen interior de la banda, rama sin restricción de capacidad transable, a un shock unitario. Unidades del modelo anualizadas: 1 unidad = US$ %.0f millones por año; producto total de referencia = %.1f unidades.' % (SCALE, Ytot), f_norm)
header(Co, 4, ['Shock unitario', 'Tamaño del shock', 'dY^N (unid.)', 'di (decimal anual)', 'dq (relativo)', 'dY total (unid.)', 'dEmpleo (unid.)', 'dBrecha N (pp)'])
order = [('dPsi', 'Exceso de demanda de divisas', '+1 unidad anual'), ('dPur', 'Compras del BCRA (subyacentes)', '+1 unidad anual'),
         ('dp', 'Probabilidad de caída del acuerdo', '+1 pp'), ('drho', 'Riesgo país', '+100 pb'),
         ('dtx', 'Derechos de exportación', '−1 pp'), ('dtm', 'Arancel de importación', '−1 pp'),
         ('dG', 'Gasto público', '+1 unidad'), ('dYT0', 'Producto transable autónomo', '+1 unidad')]
for k, (nm, lab, sz) in enumerate(order):
    rw = 5 + k; u = unit[nm]
    put(Co, f'A{rw}', lab); put(Co, f'B{rw}', sz)
    for j, key in enumerate(['dYN', 'di', 'dq', 'dYtot', 'dEmp', 'dgap']): put(Co, f'{L(3+j)}{rw}', u[key], f_in, '0.00000;(0.00000);-')
CR0 = 5
put(Co, 'A32', 'Juego 2: calibración alternativa (propensión a gastar del sector transable 0,10; indexación salarial 0,20)', f_bold)
header(Co, 33, ['Shock unitario', 'Tamaño del shock', 'dY^N (unid.)', 'di (decimal anual)', 'dq (relativo)', 'dY total (unid.)', 'dEmpleo (unid.)', 'dBrecha N (pp)'])
for k, (nm, lab, sz) in enumerate(order):
    rw = 34 + k; u = unitB[nm]
    put(Co, f'A{rw}', lab); put(Co, f'B{rw}', sz)
    for j, key in enumerate(['dYN', 'di', 'dq', 'dYtot', 'dEmp', 'dgap']): put(Co, f'{L(3+j)}{rw}', u[key], f_in, '0.00000;(0.00000);-')
put(Co, 'A43', 'Efecto de una depreciación real sobre la demanda de N (Θ^N): juego 1 = %.2f; juego 2 = %.2f' % (info['ThN'], infoB['ThN']), f_norm)
put(Co, 'A3', 'Juego 1: calibración heredada (propensión a gastar del sector transable 0,40; indexación salarial 0,60).', f_bold)
put(Co, 'A14', 'Parámetros de la curva de Phillips y de referencia', f_bold)
phil = [('gamma', 'Inercia de la inflación (γ)', 0.5), ('theta', 'Peso de la inflación pasada en las expectativas (ϑ)', 0.6), ('kappa', 'Pendiente respecto de la brecha de N (κ)', 0.40),
        ('betaE', 'Traspaso de la depreciación rezagada (β_E)', 0.10), ('betai', 'Costo financiero (β_i)', 0.10), ('betae', 'Expectativas de depreciación (β_ε)', 0.30),
        ('a', 'Peso de los transables en el IPC (a)', 0.35), ('e4', 'Efecto de la probabilidad de caída en la depreciación esperada (ε_4)', 0.40),
        ('i0', 'Tasa de referencia (% anual)', 25.0), ('eps0', 'Depreciación esperada de referencia (% anual)', 20.0), ('x0', 'Brecha inicial de N (pp)', 100*info['xgap']),
        ('Ytot', 'Producto total de referencia (unidades)', Ytot), ('Yref', 'Producto no transable de referencia (unidades)', 100.0), ('scale', 'US$ millones por unidad anual', SCALE),
        ('emp0', 'Empleo de referencia (unidades)', 100.0 + P1['lT']*P1['YT00'])]
CP = {}
for k, (key, lab, v) in enumerate(phil):
    rw = 15 + k; CP[key] = f'Coeficientes!$B${rw}'; put(Co, f'A{rw}', lab); put(Co, f'B{rw}', v, f_in, '0.0000')
put(Co, 'D14', 'Las constantes de la curva de Phillips son ilustrativas (no estimadas). Fuente: modelo versión 6, sección 8.', f_norm)
Co.column_dimensions['A'].width = 62
for c_ in 'BCDEFGH': Co.column_dimensions[c_].width = 16

# =============================== Hojas por escenario
scen = [('Base', 'C'), ('Optimista', 'D'), ('Pesimista', 'E')]
QL = ['T4-2026', 'T1-2027', 'T2-2027', 'T3-2027', 'T4-2027']; COLS = ['C', 'D', 'E', 'F', 'G']
def sp(key, col): return f'Supuestos!${col}${SR[key]}'
SC = {}
for name, sc in scen:
    W = wb.create_sheet(name); R = {}
    put(W, 'A1', f'Escenario {name.lower()}: sector externo, financiamiento y bloque macro trimestral', f_t)
    header(W, 3, ['Concepto', 'Unidad'] + QL + ['2027'])
    rw = 4
    def sect(t):
        global rw; section(W, rw, t, 8); rw += 1
    def line(key, label, unit_, formulas, fmt=NUM, total=None, font=f_norm):
        global rw
        R[key] = rw; put(W, f'A{rw}', label); put(W, f'B{rw}', unit_)
        for col, fm in zip(COLS, formulas):
            if fm is None: continue
            put(W, f'{col}{rw}', fm, font, fmt)
        if total: put(W, f'H{rw}', total.replace('#', str(rw)), f_norm, fmt)
        rw += 1
    # ---- A. fuentes y usos
    sect('A. Fuentes y usos de moneda extranjera del sector público consolidado (US$ millones)')
    qidx = {'D': 1, 'E': 2, 'F': 3, 'G': 4}
    purf = {'D': f"=Supuestos!$C${SR['m1']}+Supuestos!$C${SR['m2']}+Supuestos!$C${SR['m3']}", 'E': f"=Supuestos!$C${SR['m4']}+Supuestos!$C${SR['m5']}+Supuestos!$C${SR['m6']}",
            'F': f"=Supuestos!$C${SR['m7']}+Supuestos!$C${SR['m8']}+Supuestos!$C${SR['m9']}", 'G': f"={sp('oct27', sc)}+2*{sp('novdic', sc)}"}
    line('pur', 'Compras de divisas del BCRA', 'US$ millones', [None] + [f"={sp('pfac', sc)}*({purf[c][1:]})" for c in 'DEFG'], total='=SUM(D#:G#)')
    line('on_adj', 'Compras adicionales por flujo neto de ON (liquidaciones menos pagos)', 'US$ millones', [None, None, None, None, None], total='=SUM(D#:G#)')
    line('saldo', 'Saldo del programa financiero 2026 (caja inicial)', 'US$ millones', [None, f"={sp('saldo', sc)}", 0, 0, 0], total='=SUM(D#:G#)')
    line('imf', 'Desembolso del FMI', 'US$ millones', [None] + [f"=IF({qidx[c]}={sp('imfq', sc)},{sp('imf', sc)},0)" for c in 'DEFG'], total='=SUM(D#:G#)')
    line('ooii', 'Organismos internacionales', 'US$ millones', [None, f"={sp('ooii', sc)}*{sp('ooiip', sc)}*{sp('sh1', sc)}", f"={sp('ooii', sc)}*{sp('ooiip', sc)}*(1-{sp('sh1', sc)})", 0, 0], total='=SUM(D#:G#)')
    line('bil', 'Préstamo bilateral', 'US$ millones', [None, f"={sp('bil', sc)}*{sp('bilp', sc)}*{sp('sh1', sc)}", f"={sp('bil', sc)}*{sp('bilp', sc)}*(1-{sp('sh1', sc)})", 0, 0], total='=SUM(D#:G#)')
    line('priv', 'Privatizaciones', 'US$ millones', [None, f"={sp('priv', sc)}*{sp('privp', sc)}*{sp('sh1', sc)}", f"={sp('priv', sc)}*{sp('privp', sc)}*(1-{sp('sh1', sc)})", 0, 0], total='=SUM(D#:G#)')
    line('intra', 'Roll over intra sector público', 'US$ millones', [None] + [f"={sp('intra', sc)}*Calendario_FX!{c}${KR['totadj']}/Calendario_FX!$H${KR['totadj']}" for c in 'DEFG'], total='=SUM(D#:G#)')
    line('loc', 'Emisión local en dólares', 'US$ millones', [None, 0, f"={sp('loc', sc)}/2", f"={sp('loc', sc)}/2", 0], total='=SUM(D#:G#)')
    line('intl', 'Emisión internacional', 'US$ millones', [None, 0, 0, f"={sp('intl', sc)}", 0], total='=SUM(D#:G#)')
    line('src', 'Total fuentes (incluye caja inicial)', 'US$ millones', [None] + [f"=SUM({c}{R['pur']}:{c}{R['intl']})" for c in 'DEFG'], total='=SUM(D#:G#)', font=f_bold)
    line('sd', 'Servicio de deuda en moneda extranjera (planilla MECON ajustada con el Presupuesto 2027)', 'US$ millones', [None] + [f"=Calendario_FX!{c}{KR['totadj']}" for c in 'DEFG'], total='=SUM(D#:G#)', font=f_link)
    line('bo', 'BOPREAL Serie 1', 'US$ millones', [None] + [f"=Calendario_FX!{c}{KR['bop']}" for c in 'DEFG'], total='=SUM(D#:G#)', font=f_link)
    line('uses', 'Total usos', 'US$ millones', [None] + [f"={c}{R['sd']}+{c}{R['bo']}" for c in 'DEFG'], total='=SUM(D#:G#)', font=f_bold)
    line('net', 'Resultado neto del trimestre', 'US$ millones', [None] + [f"={c}{R['src']}-{c}{R['uses']}" for c in 'DEFG'], total='=SUM(D#:G#)')
    line('cum', 'Cobertura acumulada (colchón)', 'US$ millones', [None, f"=D{R['net']}"] + [f"={p}{rw}+{c}{R['net']}" for p, c in zip('DEF', 'EFG')], font=f_bold)
    line('cov', 'Fuentes sobre usos', 'razón', [None] + [f"=IF({c}{R['uses']}=0,0,{c}{R['src']}/{c}{R['uses']})" for c in 'DEFG'], fmt='0.00x')
    line('need', 'Compras adicionales necesarias en T4 para cubrir el año', 'US$ millones', [None, None, None, None, f"=MAX(0,-G{R['cum']})"])
    line('dR', 'Variación de reservas del trimestre (sin caja inicial; roll over neteado)', 'US$ millones',
         [None] + [f"={c}{R['pur']}+{c}{R['on_adj']}+{c}{R['imf']}+{c}{R['ooii']}+{c}{R['bil']}+{c}{R['priv']}+{c}{R['loc']}+{c}{R['intl']}-({c}{R['sd']}-{c}{R['intra']})-{c}{R['bo']}" for c in 'DEFG'], total='=SUM(D#:G#)')
    line('dRc', 'Variación acumulada de reservas desde diciembre de 2026', 'US$ millones', [0, f"=D{R['dR']}"] + [f"={p}{rw}+{c}{R['dR']}" for p, c in zip('DEF', 'EFG')], font=f_bold)
    line('Rlev', 'Reservas brutas, nivel ilustrativo (base: 48.653 al 2/10/2026)', 'US$ millones', [f"=48653+{c}{R['dRc']}" for c in COLS])
    # ---- B. cuenta corriente
    sect('B. Cuenta corriente y flujos de obligaciones negociables')
    line('ca_pct', 'Cuenta corriente', '% del PBI', [f"={sp('ca26', sc)}"] + [f"={sp('ca27', sc)}"] * 4, fmt=PCT2, total='=AVERAGE(D#:G#)')
    line('ca_usd', 'Cuenta corriente (flujo trimestral)', 'US$ millones', [f"={c}{R['ca_pct']}*{sp('gdp', sc)}/4" for c in COLS], total='=SUM(D#:G#)')
    line('ca_ref', 'Cuenta corriente de referencia de 2026 (flujo trimestral)', 'US$ millones', [f"={sp('ca26', sc)}*{sp('gdp', sc)}/4"] * 5)
    line('on_in', 'Ingresos de dólares por liquidación de ON emitidas', 'US$ millones', [None, f"={sp('onq1', sc)}", 0, 0, 0], total='=SUM(D#:G#)')
    line('on_dem', 'Demanda de dólares en el MULC por pagos de ON', 'US$ millones', [None, f"={sp('ondemq1', sc)}/2*(1-{sp('onca', sc)})"] + [f"={sp('ondem', sc)}*(1-{sp('onca', sc)})"] * 3, total='=SUM(D#:G#)')
    line('on_net', 'Flujo neto de ON (ingresos menos demanda)', 'US$ millones', [None] + [f"={c}{R['on_in']}-{c}{R['on_dem']}" for c in 'DEFG'], total='=SUM(D#:G#)', font=f_bold)
    for c in 'DEFG': W[f"{c}{R['on_adj']}"] = f"={c}{R['on_net']}"; W[f"{c}{R['on_adj']}"].number_format = NUM; W[f"{c}{R['on_adj']}"].font = f_norm
    # ---- C. shocks
    sect('C. Shocks en unidades del modelo respecto de la referencia de 2026')
    line('p', 'Probabilidad de caída del acuerdo', 'probabilidad', [f"={sp('pref', sc)}"] + [f"={sp('p', sc)}"] * 4, fmt=PCT)
    line('rho', 'Riesgo país', 'pb', [f"={sp('rho0', sc)}"] + [f"={sp('rho0', sc)}+({sp('rho4', sc)}-{sp('rho0', sc)})*{k}/4" for k in (1, 2, 3, 4)], fmt=NUM)
    seas = {'D': f"(Supuestos!$C${SR['m1']}+Supuestos!$C${SR['m2']}+Supuestos!$C${SR['m3']})", 'E': f"(Supuestos!$C${SR['m4']}+Supuestos!$C${SR['m5']}+Supuestos!$C${SR['m6']})", 'F': f"(Supuestos!$C${SR['m7']}+Supuestos!$C${SR['m8']}+Supuestos!$C${SR['m9']})"}
    avgq = f"(SUM(Supuestos!$C${SR['m1']}:Supuestos!$C${SR['m9']})/3)"
    line('s_psi', 'Exceso de demanda de divisas (CA menor que la referencia más demanda de ON)', 'unid. anual', [0] + [f"=(-({c}{R['ca_usd']}-{c}{R['ca_ref']})+({c}{R['on_dem']}-{c}{R['on_in']}))*4/{CP['scale']}" for c in 'DEFG'], fmt=NUM3)
    # compras subyacentes: se descuenta el patrón estacional de 2026 (T4 sin patrón)
    pur_und = {'D': f"(D{R['pur']}+D{R['on_adj']}-{sp('pfac', sc)}*({seas['D']}-{avgq}))", 'E': f"(E{R['pur']}+E{R['on_adj']}-{sp('pfac', sc)}*({seas['E']}-{avgq}))", 'F': f"(F{R['pur']}+F{R['on_adj']}-{sp('pfac', sc)}*({seas['F']}-{avgq}))", 'G': f"(G{R['pur']}+G{R['on_adj']})"}
    line('s_pur', 'Compras subyacentes del BCRA respecto de la referencia', 'unid. anual', [0] + [f"=({pur_und[c]}-{avgq})*4/{CP['scale']}" for c in 'DEFG'], fmt=NUM3)
    line('s_p', 'Variación de la probabilidad respecto de la referencia', 'pp', [0] + [f"=({c}{R['p']}-{sp('pref', sc)})*100" for c in 'DEFG'], fmt=NUM3)
    line('s_rho', 'Variación del riesgo país respecto de la referencia', 'cientos de pb', [0] + [f"=({c}{R['rho']}-{sp('rho0', sc)})/100" for c in 'DEFG'], fmt=NUM3)
    line('s_tx', 'Baja acumulada de derechos de exportación', 'pp', [0] + [f"={sp('dtx', sc)}*{k}" for k in (1, 2, 3, 4)], fmt=NUM3)
    line('s_tm', 'Baja acumulada del arancel de importación', 'pp', [0] + [f"={sp('dtm', sc)}*{k}" for k in (1, 2, 3, 4)], fmt=NUM3)
    line('s_G', 'Variación del gasto público', 'unidades', [0] + [f"={sp('dG', sc)}"] * 4, fmt=NUM3)
    line('s_YT', 'Producto transable autónomo (términos de intercambio)', 'unidades', [0, 0, 0, 0, 0], fmt=NUM3)
    s0, s1 = R['s_psi'], R['s_YT']
    # ---- D. respuestas
    sect('D. Respuesta del modelo (desvíos respecto de la referencia de 2026)')
    resp = [('r_YN', 'Producto no transable', 'unidades', 'C'), ('r_i', 'Tasa de interés', 'decimal anual', 'D'), ('r_q', 'Tipo de cambio real', 'relativo', 'E'),
            ('r_Yt', 'Producto total', 'unidades', 'F'), ('r_emp', 'Empleo', 'unidades', 'G'), ('r_gap', 'Brecha del sector N', 'pp', 'H')]
    for key, lab, un, cc in resp:
        fm = [0] + [f"=IF({sp('sel', sc)}=1,SUMPRODUCT(Coeficientes!${cc}$5:${cc}$12,{c}${s0}:{c}${s1}),SUMPRODUCT(Coeficientes!${cc}$34:${cc}$41,{c}${s0}:{c}${s1}))" for c in 'DEFG']
        line(key, lab, un, fm, fmt='0.0000;(0.0000);-')
    # ---- E. niveles
    sect('E. Niveles macro')
    line('act', 'Actividad real (índice, T4-2026 = 100)', 'índice', [100] + [f"=100*(1+{sp('gtr', sc)})^({k}/4)*(1+{c}{R['r_Yt']}/{CP['Ytot']})" for k, c in zip((1, 2, 3, 4), 'DEFG')], fmt='0.0')
    line('growth', 'Crecimiento 2027 (promedio anual, aproximado)', '% anual', [None, None, None, None, None], fmt=PCT, total=f"=(1+{sp('gtr', sc)})*(1+AVERAGE(D{R['r_Yt']}:G{R['r_Yt']})/{CP['Ytot']})-1")
    line('emp', 'Empleo (desvío porcentual respecto de la referencia)', '%', [0] + [f"={c}{R['r_emp']}/{CP['emp0']}" for c in 'DEFG'], fmt=PCT2, total='=AVERAGE(D#:G#)')
    line('q', 'Tipo de cambio real (índice, referencia = 1)', 'índice', [1] + [f"=1+{c}{R['r_q']}" for c in 'DEFG'], fmt='0.000')
    line('i', 'Tasa de interés', '% anual', [f"={CP['i0']}"] + [f"={CP['i0']}+100*{c}{R['r_i']}" for c in 'DEFG'], fmt='0.0', total='=AVERAGE(D#:G#)')
    line('eps', 'Depreciación esperada', '% anual', [f"={CP['eps0']}"] + [f"={CP['eps0']}+100*{CP['e4']}*({c}{R['p']}-{sp('pref', sc)})" for c in 'DEFG'], fmt='0.0')
    line('anc', 'Ancla de expectativas de inflación', '% anual', [f"={sp('anc0', sc)}+({sp('anc4', sc)}-{sp('anc0', sc)})*{k}/4" for k in (0, 1, 2, 3, 4)], fmt='0.0')
    line('gap', 'Brecha del sector N', 'pp', [f"={CP['x0']}"] + [f"={CP['x0']}+{c}{R['r_gap']}" for c in 'DEFG'], fmt='0.00')
    # inflación y tipo de cambio (recursivos); fila previa de depreciación nominal anualizada
    R['dlnE'] = rw + 4
    line('piN', 'Inflación del sector N (anualizada)', '% anual', [f"={sp('pi0', sc)}"] + [None] * 4, fmt='0.0')
    line('E', 'Tipo de cambio nominal mayorista', '$ por US$', [f"={sp('E0', sc)}"] + [None] * 4, fmt='#,##0')
    line('piT', 'Inflación de transables (depreciación anualizada más inflación externa)', '% anual', [0.0] + [None] * 4, fmt='0.0')
    line('cpi', 'Inflación del IPC (anualizada)', '% anual', [None] + [None] * 4, fmt='0.0', total='=AVERAGE(D#:G#)')
    # fila de depreciación nominal anualizada (para el rezago): T4-26 = 0
    line('dlnE', 'Depreciación nominal anualizada del trimestre', '% anual', [0.0] + [None] * 4, fmt='0.0')
    prev = {'D': 'C', 'E': 'D', 'F': 'E', 'G': 'F'}
    for c in 'DEFG':
        p_ = prev[c]
        W[f"{c}{R['piN']}"] = (f"={CP['gamma']}*{p_}{R['piN']}+(1-{CP['gamma']})*({CP['theta']}*{p_}{R['piN']}+(1-{CP['theta']})*{c}{R['anc']}+{CP['betae']}*({c}{R['eps']}-{CP['eps0']}))"
                               f"+{CP['kappa']}*{c}{R['gap']}+{CP['betaE']}*{p_}{R['dlnE']}+{CP['betai']}*({c}{R['i']}-{CP['i0']})")
        W[f"{c}{R['E']}"] = f"={p_}{R['E']}*({c}{R['q']}/{p_}{R['q']})*(1+{c}{R['piN']}/400)/(1+{sp('pistar', sc)}*100/400)"
        W[f"{c}{R['dlnE']}"] = f"=400*LN({c}{R['E']}/{p_}{R['E']})"
        W[f"{c}{R['piT']}"] = f"={c}{R['dlnE']}+{sp('pistar', sc)}*100"
        W[f"{c}{R['cpi']}"] = f"={CP['a']}*{c}{R['piT']}+(1-{CP['a']})*{c}{R['piN']}"
        for k_ in ('piN', 'E', 'dlnE', 'piT', 'cpi'): W[f"{c}{R[k_]}"].font = f_norm
        W[f"{c}{R['piN']}"].number_format = '0.0'; W[f"{c}{R['E']}"].number_format = '#,##0'; W[f"{c}{R['dlnE']}"].number_format = '0.0'; W[f"{c}{R['piT']}"].number_format = '0.0'; W[f"{c}{R['cpi']}"].number_format = '0.0'
    W[f"C{R['cpi']}"] = f"={CP['a']}*C{R['piT']}+(1-{CP['a']})*C{R['piN']}"; W[f"C{R['cpi']}"].number_format = '0.0'; W[f"C{R['cpi']}"].font = f_norm
    W.column_dimensions['A'].width = 66; W.column_dimensions['B'].width = 16
    for c_ in 'CDEFGH': W.column_dimensions[c_].width = 13
    W.freeze_panes = 'C4'
    SC[name] = R

# =============================== Comparativo
Cm = wb.create_sheet('Comparativo', 3)
put(Cm, 'A1', 'Comparación de escenarios, 2027', f_t)
header(Cm, 3, ['Indicador', 'Unidad', 'Base', 'Optimista', 'Pesimista'])
items = [
 ('Cuenta corriente 2027', '% del PBI', lambda n, R: f"={n}!H{R['ca_pct']}", PCT2),
 ('Crecimiento del producto (aproximado)', '% anual', lambda n, R: f"={n}!H{R['growth']}", PCT),
 ('Inflación del IPC, promedio anualizado', '% anual', lambda n, R: f"={n}!H{R['cpi']}", '0.0'),
 ('Inflación del IPC en el T4-2027 (anualizada)', '% anual', lambda n, R: f"={n}!G{R['cpi']}", '0.0'),
 ('Tipo de cambio nominal a fin de 2027', '$ por US$', lambda n, R: f"={n}!G{R['E']}", '#,##0'),
 ('Tipo de cambio real a fin de 2027 (referencia = 1)', 'índice', lambda n, R: f"={n}!G{R['q']}", '0.000'),
 ('Tasa de interés, promedio', '% anual', lambda n, R: f"={n}!H{R['i']}", '0.0'),
 ('Empleo, desvío promedio respecto de la referencia', '%', lambda n, R: f"={n}!H{R['emp']}", PCT2),
 ('Riesgo país a fin de 2027', 'pb', lambda n, R: f"={n}!G{R['rho']}", NUM),
 ('Compras de divisas del BCRA en 2027', 'US$ millones', lambda n, R: f"={n}!H{R['pur']}", NUM),
 ('Cobertura acumulada a septiembre de 2027 (colchón)', 'US$ millones', lambda n, R: f"={n}!F{R['cum']}", NUM),
 ('Cobertura acumulada a diciembre de 2027', 'US$ millones', lambda n, R: f"={n}!G{R['cum']}", NUM),
 ('Compras adicionales necesarias en T4 para cubrir el año', 'US$ millones', lambda n, R: f"={n}!G{R['need']}", NUM),
 ('Variación acumulada de reservas en 2027', 'US$ millones', lambda n, R: f"={n}!G{R['dRc']}", NUM),
 ('Reservas brutas a fin de 2027, nivel ilustrativo', 'US$ millones', lambda n, R: f"={n}!G{R['Rlev']}", NUM),
 ('Flujo neto de ON en 2027 (ingresos menos demanda)', 'US$ millones', lambda n, R: f"={n}!H{R['on_net']}", NUM),
 ('Usos totales en moneda extranjera en 2027 (servicio ajustado más BOPREAL)', 'US$ millones', lambda n, R: f"={n}!H{R['uses']}", NUM),
]
for k, (lab, un, fn, fmt) in enumerate(items):
    rw = 4 + k; put(Cm, f'A{rw}', lab); put(Cm, f'B{rw}', un)
    for col, (n, sc) in zip('CDE', scen): put(Cm, f'{col}{rw}', fn(n, SC[n]), f_link, fmt)
put(Cm, f'A{4+len(items)+1}', 'Los resultados dependen de los supuestos de la hoja Supuestos y de coeficientes ilustrativos; no son pronósticos. El crecimiento y la inflación 2027 no fueron dados por el usuario: surgen de la tendencia supuesta y de la respuesta del modelo.', f_norm, wrap=True)
Cm.column_dimensions['A'].width = 62; Cm.column_dimensions['B'].width = 16
for c_ in 'CDE': Cm.column_dimensions[c_].width = 15

# =============================== Verificacion
V = wb.create_sheet('Verificacion')
put(V, 'A1', 'Verificación de la calibración y de la planilla', f_t)
header(V, 3, ['Control', 'Valor', 'Esperado', 'Estado'])
checks = [
 ('Residuo de la IS en la referencia (script)', info['res']['IS'], 0.0, 'script'),
 ('Residuo de la LM en la referencia (script)', info['res']['LM'], 0.0, 'script'),
 ('Residuo de la balanza de pagos en la referencia (script)', info['res']['BOP'], 0.0, 'script'),
 ('Peso del sector transable en el producto total', f"={CP['Ytot']}", None, 'T'),
]
checks = checks[:3] + [('Residuo de la IS, juego 2 (script)', infoB['res']['IS'], 0.0, 'script'), ('Residuo de la LM, juego 2 (script)', infoB['res']['LM'], 0.0, 'script'), ('Residuo de la balanza de pagos, juego 2 (script)', infoB['res']['BOP'], 0.0, 'script')]
rw = 4
for lab, v, e, kind in checks[:6]:
    put(V, f'A{rw}', lab); put(V, f'B{rw}', v, f_in, '0.0E+00'); put(V, f'C{rw}', e, f_norm, '0'); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.000001,"OK","REVISAR")'); rw += 1
put(V, f'A{rw}', 'Presupuesto 2027: suma mensual del capital del FMI (billones de $)'); put(V, f'B{rw}', '=Presupuesto_2027!O5', f_link, '0.00'); put(V, f'C{rw}', 7.84, f_in, '0.00'); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.005,"OK","REVISAR")'); rw += 1
put(V, f'A{rw}', 'Presupuesto 2027: suma trimestral del capital del FMI igual a la suma mensual (US$ millones)'); put(V, f'B{rw}', '=Presupuesto_2027!H10', f_link, NUM); put(V, f'C{rw}', '=Presupuesto_2027!O7', f_link, NUM); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.5,"OK","REVISAR")'); rw += 1
put(V, f'A{rw}', 'Peso del sector transable en el producto total'); put(V, f'B{rw}', f"=({CP['Ytot']}-{CP['Yref']})/{CP['Ytot']}", f_link, PCT); put(V, f'C{rw}', f"=Supuestos!C{SR['xs']}+Supuestos!C{SR['ms']}", f_link, PCT); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.0001,"OK","REVISAR")'); rw += 1
for name, sc in scen:
    R = SC[name]
    put(V, f'A{rw}', f'{name}: fuentes menos usos igual a la suma de los netos'); put(V, f'B{rw}', f"={name}!H{R['src']}-{name}!H{R['uses']}", f_link, NUM); put(V, f'C{rw}', f"={name}!G{R['cum']}", f_link, NUM); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.5,"OK","REVISAR")'); rw += 1
    put(V, f'A{rw}', f'{name}: flujo neto de ON de 2027 igual a ingresos menos pagos'); put(V, f'B{rw}', f"={name}!H{R['on_net']}", f_link, NUM); put(V, f'C{rw}', f"=Supuestos!{dict(Base='C',Optimista='D',Pesimista='E')[name]}{SR['onq1']}-(Supuestos!{dict(Base='C',Optimista='D',Pesimista='E')[name]}{SR['ondemq1']}/2+3*Supuestos!{dict(Base='C',Optimista='D',Pesimista='E')[name]}{SR['ondem']})*(1-Supuestos!{dict(Base='C',Optimista='D',Pesimista='E')[name]}{SR['onca']})", f_link, NUM); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.5,"OK","REVISAR")'); rw += 1
    put(V, f'A{rw}', f'{name}: compras de septiembre iguales al espejo de 2026 por el factor'); put(V, f'B{rw}', f"={name}!H{R['pur']}-{name}!G{R['pur']}", f_link, NUM); put(V, f'C{rw}', f"=SUM(Supuestos!C{SR['m1']}:C{SR['m9']})*Supuestos!{dict(Base='C',Optimista='D',Pesimista='E')[name]}{SR['pfac']}", f_link, NUM); put(V, f'D{rw}', f'=IF(ABS(B{rw}-C{rw})<0.5,"OK","REVISAR")'); rw += 1
put(V, f'A{rw+1}', 'Detalle de la descomposición de Θ^N (script): ' + ', '.join(f"{k} {v:.3f}" for k, v in info['comp'].items()), f_norm, wrap=True)
V.column_dimensions['A'].width = 80
for c_ in 'BCD': V.column_dimensions[c_].width = 16

if SENS:
    Z = wb.create_sheet('Sensibilidad')
    put(Z, 'A1', 'Sensibilidad al juego de coeficientes (valores calculados con cada juego; no se actualizan)', f_t)
    header(Z, 3, ['Indicador', 'Unidad', 'Base juego 1', 'Optimista juego 1', 'Pesimista juego 1', 'Base juego 2', 'Optimista juego 2', 'Pesimista juego 2'])
    for k, (lab, un, fmt) in enumerate(SENS['labels']):
        rw = 4 + k; put(Z, f'A{rw}', lab); put(Z, f'B{rw}', un)
        for j, v in enumerate(SENS['v1'][k] + SENS['v2'][k]): put(Z, f'{L(3+j)}{rw}', v, f_in, fmt)
    put(Z, f'A{4+len(SENS["labels"])+1}', 'Con el juego 1 la depreciación es expansiva (derrame del ingreso transable alto) y el escenario pesimista muestra más crecimiento que el base; es un resultado de la calibración y no debe leerse como pronóstico. El juego 2 invierte ese signo. La elección entre ambos requiere estimar la propensión a gastar del sector transable y la indexación salarial.', f_norm, wrap=True)
    Z.column_dimensions['A'].width = 58; Z.column_dimensions['B'].width = 16
    for c_ in 'CDEFGH': Z.column_dimensions[c_].width = 17
# orden de hojas
order_names = ['Leyenda', 'Supuestos', 'Comparativo'] + (['Sensibilidad'] if SENS else []) + ['Calendario_FX', 'Presupuesto_2027', 'Base', 'Optimista', 'Pesimista', 'Coeficientes', 'Verificacion']
wb._sheets = [wb[n] for n in order_names]
wb.save(OUT)
print('guardado; filas Base:', {k: v for k, v in SC['Base'].items() if k in ('pur', 'cum', 'dRc', 'r_YN', 'piN', 'E', 'cpi')})
