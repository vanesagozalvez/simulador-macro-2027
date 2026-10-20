// Texto de la solapa "Metodología" (HTML). Lenguaje explicativo para no especialistas.
const dl = rows => `<dl>${rows.map(([t, d]) => `<dt>${t}</dt><dd>${d}</dd>`).join('')}</dl>`;
export const METODOLOGIA = `<article class="doc">
<h2>Definición metodológica del modelo</h2>
<p class="lead">Este simulador responde a una pregunta concreta: <em>¿qué le pasaría a la economía argentina durante 2027 (actividad, precios, tipo de cambio, tasas y dólares disponibles) bajo tres combinaciones de supuestos: una base, una optimista y una pesimista?</em> No predice el futuro: muestra las consecuencias lógicas de los supuestos que se cargan. Si los supuestos cambian, los resultados cambian.</p>

<h3>1. Cómo funciona, paso a paso</h3>
<ol>
<li><strong>Punto de partida.</strong> El modelo toma como referencia la economía de 2026 (cuarto trimestre) y mide cuánto se aleja cada variable de esa referencia a lo largo de los cuatro trimestres de 2027. Es un modelo <em>lineal</em>: si un supuesto se duplica, su efecto se duplica.</li>
<li><strong>Los supuestos se convierten en “impulsos”.</strong> Cada supuesto que se carga (por ejemplo, un menor superávit externo, más compras de dólares del Banco Central o un mayor riesgo país) se compara con su valor de referencia. La diferencia es un impulso que empuja a la economía.</li>
<li><strong>El bloque macro calcula la reacción real.</strong> La economía se representa con dos sectores: el <em>no transable</em> (N: servicios y actividades que dependen del mercado interno, como comercio o construcción) y el <em>transable</em> (T: lo que se exporta o compite con importaciones). Tres mercados se equilibran a la vez: bienes (qué se produce y se gasta), dinero (cuánta liquidez hay y a qué tasa) y balanza de pagos (cuántos dólares entran y salen). Del equilibrio salen el producto, el tipo de cambio real, la tasa de interés, el empleo y la brecha de actividad del sector N. Las reacciones a cada impulso se calcularon de antemano (juegos de coeficientes) y están guardadas en el simulador.</li>
<li><strong>La curva de Phillips calcula los precios.</strong> Con la brecha de actividad, la tasa, las expectativas y el movimiento del tipo de cambio, se obtiene la inflación trimestre a trimestre, y con ella el tipo de cambio nominal.</li>
<li><strong>Un módulo de dólares calcula la liquidez en moneda extranjera.</strong> Suma las fuentes de dólares de cada trimestre (compras del Banco Central, financiamiento, desembolsos del FMI, emisiones de deuda) y resta los usos (vencimientos de capital e intereses, BOPREAL), para dar el <em>colchón</em> acumulado y las reservas. Algunos de sus componentes (compras, obligaciones negociables, cuenta corriente) también alimentan el paso 2.</li>
</ol>

<h3>2. Supuestos (datos de entrada)</h3>
<p>En el panel de la izquierda se editan los principales, con tres valores cada uno (base, optimista, pesimista). Los demás parten de valores fijos, tomados de la planilla de Excel, y pueden cambiarse en el código. Los datos provistos por el usuario no fueron verificados por el analista.</p>
<h4>Magnitudes generales</h4>
${dl([
['Crecimiento tendencial 2027', 'Cuánto crecería la economía en un año “normal”, sin los impulsos del modelo. El crecimiento resultante es este valor más el efecto de los demás supuestos.'],
['Inflación externa', 'Inflación de los socios comerciales (3,5% anual). Sirve para pasar de la depreciación nominal a la real.'],
['Tipo de cambio inicial', 'Cotización mayorista al cierre de 2026 (pesos por dólar), desde donde parte la trayectoria.'],
['Inflación inicial de N', 'Ritmo anualizado de aumento de precios del sector no transable al arrancar el período.'],
['Ancla de expectativas de inflación', 'Inflación que la gente espera a mediano plazo. Se parte de un valor a fines de 2026 y se llega a otro a fines de 2027; cuanto más bajo, más fácil bajar la inflación.'],
['PBI en dólares y cuenta corriente 2026', 'Tamaño de la economía (US$700.000 millones) y saldo externo de referencia (0,6% del PBI), contra los cuales se mide todo cambio de 2027.'],
['Juego de coeficientes', 'Dos versiones de cómo reacciona la economía a una depreciación. En el juego 1 devaluar tiende a expandir la actividad (los exportadores ganan competitividad); en el juego 2 tiende a contraerla (se pierde poder de compra de los salarios y se encarecen las deudas en dólares). Es la principal fuente de incertidumbre del modelo: conviene mirar ambos.']])}
<h4>Cuenta corriente y política económica</h4>
${dl([
['Cuenta corriente 2027', 'Saldo de las cuentas con el exterior (bienes, servicios e intereses) como porcentaje del PBI. Positivo: entran más dólares de los que salen por estos conceptos.'],
['Baja de derechos de exportación y de aranceles', 'Recortes de 0,75 y 0,25 puntos porcentuales por trimestre. Abaratar exportar impulsa al sector transable; abaratar importar presiona sobre la producción local y sobre los dólares.'],
['Variación del gasto público', 'Cambio del gasto fiscal en unidades del modelo (por defecto, cero). Más gasto expande la actividad y tiende a apreciar el tipo de cambio real.']])}
<h4>Obligaciones negociables (ON) de empresas</h4>
${dl([
['Liquidación pendiente de ON ya emitidas', 'Dólares de emisiones de empresas que todavía deben ingresar al mercado de cambios (US$ 2.700 millones llegarían en el primer trimestre de 2027).'],
['Pagos de ON', 'Dólares que las empresas necesitan para pagar esas deudas: US$ 2.600 millones en el primer trimestre de 2027 y el valor por trimestre que se cargue de T2 a T4. Un pago mayor reduce los dólares disponibles.']])}
<h4>Capital de organismos internacionales</h4>
${dl([
['Fuente del capital de organismos', 'Elige entre la planilla de deuda del Ministerio de Economía (MECON) y los montos del Presupuesto 2027. La elegida reemplaza a la otra; no se suman.'],
['Tipo de cambio de conversión, BID, otros préstamos y resto de organismos', 'El Presupuesto expresa las amortizaciones en pesos; se convierten a dólares con este tipo de cambio.']])}
<h4>Compras de dólares del Banco Central</h4>
${dl([
['Factor de compras', 'Multiplicador sobre las compras mensuales de 2026, que se usan como “espejo” para 2027. Con 1 se repite el ritmo de 2026; con 1,15, compra 15% más; con 0,75, 25% menos.'],
['Compras de octubre de 2027', 'Se supone cero, por las elecciones. Por eso el “colchón a septiembre” muestra la situación antes de ese mes.']])}
<h4>Fuentes de financiamiento en dólares</h4>
${dl([
['Saldo del programa 2026 arrastrado', 'Financiamiento ya asegurado que pasa de 2026 a 2027.'],
['Desembolso del FMI y trimestre', 'Monto (US$ 850 millones) y trimestre en que ingresa el desembolso de la cuarta revisión del acuerdo.'],
['Organismos internacionales, préstamo bilateral y privatizaciones', 'Programa total de 2027 y qué porcentaje se considera que efectivamente ingresa en cada escenario. Una parte se reparte en el primer trimestre y el resto en el segundo.'],
['Roll over intra sector público', 'Vencimientos que se renuevan dentro del propio sector público y por tanto no consumen dólares.'],
['Emisión local e internacional de deuda', 'Dólares que el Tesoro conseguiría colocando deuda en el mercado local (segundo y tercer trimestre) e internacional (tercero). Son cero en el escenario base.']])}
<h4>Riesgo y expectativas</h4>
${dl([
['Riesgo país a fin de 2027', 'Sobretasa que paga el país por endeudarse, en puntos básicos (100 pb = 1 punto porcentual). Baja gradualmente desde el valor inicial; menos riesgo abarata el crédito y alivia la presión cambiaria.'],
['Probabilidad de caída del acuerdo con el FMI', 'Chance, por trimestre, de que el acuerdo se interrumpa. Cuando sube, el mercado espera más depreciación, lo que impulsa la inflación.']])}
<h4>Parámetros de la curva de Phillips</h4>
${dl([
['Inercia (γ) y peso de la inflación pasada en las expectativas (ϑ)', 'Cuánto de la inflación de hoy repite la de ayer, y cuánto las expectativas miran al pasado en lugar de a la meta.'],
['Pendiente respecto de la brecha (κ)', 'Cuánto sube la inflación cuando la actividad del sector N supera su capacidad.'],
['Traspaso de la depreciación rezagada (β_E)', 'Parte de la suba del dólar de períodos anteriores que se traslada a precios.'],
['Costo financiero (β_i)', 'Efecto de la tasa de interés sobre los precios.'],
['Expectativas de depreciación (β_ε)', 'Cuánto influye en los precios lo que se espera que suba el dólar.'],
['Peso de los transables en el IPC (a)', 'Participación de los bienes transables en el índice de precios al consumidor (60%); el resto son bienes y servicios no transables.']])}

<h3>3. Resultados (datos de salida)</h3>
<h4>Actividad y precios</h4>
${dl([
['Crecimiento del producto', 'Variación anual del PBI real en 2027. Se calcula sumando al crecimiento tendencial el efecto de los demás supuestos.'],
['Inflación IPC, promedio anualizado y T4-2027', 'Ritmo de aumento de precios al consumidor, expresado como tasa anual. El promedio resume el año; el valor de T4 muestra dónde termina.'],
['Tipo de cambio nominal a fin de 2027', 'Cotización final del dólar mayorista, en pesos.'],
['Tipo de cambio real (referencia = 1)', 'Poder de compra del dólar en términos de bienes, ajustado por precios. Menor a 1: el peso está más “fuerte” que en la referencia (apreciación real); mayor a 1: más “débil”.'],
['Tasa de interés, promedio', 'Tasa anual de la economía, que surge del equilibrio entre dinero y dólares disponibles.'],
['Empleo', 'Desvío porcentual del empleo respecto de la referencia. Un valor negativo indica menos empleo que en el punto de partida.'],
['Riesgo país', 'El valor supuesto a fin de 2027, para facilitar la lectura conjunta.'],
['Actividad (T4-2026 = 100)', 'Índice del nivel de actividad trimestre a trimestre.']])}
<h4>Dólares y reservas</h4>
${dl([
['Compras de divisas del BCRA', 'Total de dólares que compra el Banco Central en 2027 con el factor elegido.'],
['Fuentes, usos y resultado neto', 'Dólares que entran, dólares que salen (capital e intereses de deuda, BOPREAL) y su diferencia en cada trimestre.'],
['Colchón acumulado (septiembre y diciembre)', 'Suma acumulada de los resultados netos: cuántos dólares sobran (positivo) o faltan (negativo) para cubrir los vencimientos.'],
['Compras adicionales necesarias en T4', 'Si el colchón de diciembre es negativo, cuánto tendría que comprar de más el Banco Central para cerrar la brecha. Es cero si no hace falta.'],
['Variación de reservas y reservas brutas', 'Cambio de las reservas en el año y su nivel final, partiendo de US$ 48.653 millones. Es una cifra ilustrativa que ignora otros movimientos.'],
['Flujo neto de ON y usos totales', 'Ingresos menos pagos de obligaciones negociables, y todas las salidas de dólares por deuda en el año.']])}

<h3>4. Cómo leer los resultados</h3>
<p class="callout">Lo importante es comparar escenarios entre sí y ver qué supuesto mueve cada resultado, no leer una cifra aislada. Por ejemplo, un colchón negativo en el escenario pesimista no es una predicción de crisis: señala que, bajo esos supuestos de financiamiento y compras, los dólares no alcanzarían a cubrir los vencimientos y habría que conseguir más.</p>

<h3>5. Limitaciones</h3>
<ul>
<li>El modelo es lineal y sus parámetros son <strong>ilustrativos, no estimados</strong> con datos históricos.</li>
<li>No incluye la defensa del tipo de cambio con venta de reservas ni el régimen de techo de la banda cambiaria.</li>
<li>El escenario pesimista no contempla la caída del acuerdo con el FMI como evento: solo eleva su probabilidad.</li>
<li>Las reservas son un cálculo ilustrativo, y los datos cargados por el usuario no fueron verificados por el analista.</li>
<li>Las cifras son resultados condicionados a los supuestos, <strong>no pronósticos</strong>.</li>
</ul></article>`;
