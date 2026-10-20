// Texto de la solapa "Metodología" (redactado por el autor del modelo; verificado contra vm.py, build_xlsx.py y la planilla).
const B = (t, d) => `<dt>${t}</dt><dd>${d}</dd>`;
const dl = r => `<dl>${r.map(x => B(...x)).join('')}</dl>`, ul = r => `<ul>${r.map(x => `<li>${x}</li>`).join('')}</ul>`;
const ol = r => `<ol>${r.map(([t, d]) => `<li><strong>${t}</strong> ${d}</li>`).join('')}</ol>`;
export const METODOLOGIA = `<article class="doc">
<h2>Definición metodológica del modelo</h2>
<p class="lead">Este simulador responde a una pregunta concreta: <em>¿qué le pasaría a la economía argentina durante 2027 (actividad, precios, tipo de cambio, tasas de interés y dólares disponibles) bajo tres combinaciones de supuestos: una base, una optimista y una pesimista?</em> No predice el futuro. Muestra las consecuencias lógicas de los supuestos que se cargan: si los supuestos cambian, los resultados cambian.</p>
<h3>1. Cómo funciona, paso a paso</h3>
${ol([
['Punto de partida.', 'El modelo toma como referencia la economía del cuarto trimestre de 2026 y mide cuánto se aleja cada variable de esa referencia a lo largo de los cuatro trimestres de 2027. Es un modelo <em>lineal</em>: si un supuesto se duplica, su efecto se duplica.'],
['Los supuestos se convierten en impulsos.', 'Cada supuesto que se carga (por ejemplo, un menor superávit externo, más compras de dólares del Banco Central o un mayor riesgo país) se compara con su valor de referencia. La diferencia es un impulso que empuja a la economía hacia un lado u otro.'],
['El bloque macro calcula la reacción real.', 'La economía se representa con dos sectores. El <em>sector no transable</em> (N) reúne servicios y actividades que dependen del mercado interno, como el comercio, la construcción y también la industria que compite con importaciones. El <em>sector transable</em> (T) reúne lo que se exporta, como la minería, la energía y el agro. Tres mercados se equilibran a la vez: el de bienes (qué se produce y se gasta), el de dinero (cuánta liquidez hay y a qué tasa) y la balanza de pagos (cuántos dólares entran y salen). De ese equilibrio salen el producto, el tipo de cambio real, la tasa de interés, el empleo y la brecha de actividad del sector N. Las reacciones a cada impulso se calcularon de antemano y están guardadas en el simulador en dos juegos de coeficientes.'],
['La curva de Phillips calcula los precios, en tres pasos.', 'Una curva de Phillips es la relación que explica por qué suben los precios: por inercia, por expectativas, por el nivel de actividad, por costos y por el dólar. Primero, la curva calcula la inflación del sector no transable (N), que es el que depende de la dinámica interna. Segundo, la inflación de los transables sigue al dólar y a la inflación externa. Tercero, el índice de precios al consumidor (IPC) se obtiene combinando ambas con un peso fijo (60 % transables y 40 % no transables, ver sección 2). Finalmente, el tipo de cambio nominal surge de una identidad: el tipo de cambio real cambia según la depreciación nominal más la inflación externa menos la inflación de N. Precios y dólar se retroalimentan: la depreciación de un trimestre influye en los precios de los trimestres siguientes (por eso el modelo la incluye rezagada), y esos precios inciden a su vez en el tipo de cambio nominal.'],
['Un módulo de dólares calcula la liquidez en moneda extranjera.', 'Suma las fuentes de dólares de cada trimestre (compras del Banco Central, financiamiento, desembolsos del FMI, emisiones de deuda) y resta los usos (vencimientos de capital e intereses y BOPREAL). El resultado es el colchón acumulado y las reservas. Algunos de sus componentes (compras, obligaciones negociables, cuenta corriente) también alimentan el bloque macro.']])}
<h3>2. Supuestos (datos de entrada)</h3>
<p>En el panel de la izquierda se editan los principales, con tres valores cada uno (base, optimista y pesimista). Los demás parten de valores fijos tomados de la planilla de Excel y pueden cambiarse en el código. Los datos provistos por el usuario no fueron verificados por el analista.</p>
<h4>Magnitudes generales</h4>
${dl([
['Crecimiento tendencial 2027', 'Cuánto crecería la economía en un año “normal”, sin los impulsos del modelo. El crecimiento resultante es este valor más el efecto de los demás supuestos.'],
['Inflación externa', 'Inflación de los socios comerciales (3,5 % anual). Sirve para pasar de la depreciación nominal a la real.'],
['Tipo de cambio inicial', 'Cotización mayorista al cierre de 2026 (pesos por dólar), desde donde parte la trayectoria.'],
['Inflación inicial de N', 'Ritmo anualizado de aumento de precios del sector no transable al arrancar el período.'],
['Ancla de expectativas de inflación', 'La inflación que la gente espera a mediano plazo. Se parte de un valor a fines de 2026 y se llega a otro a fines de 2027. Cuanto más bajo, más fácil es bajar la inflación.'],
['PBI en dólares y cuenta corriente 2026', 'Tamaño de la economía (US$ 700.000 millones) y saldo externo de referencia (0,6 % del PBI), contra los cuales se mide todo cambio de 2027.'],
['Juego de coeficientes', 'Dos versiones de cómo reacciona la economía a una depreciación. En el juego 1, devaluar tiende a expandir la actividad, porque los exportadores ganan competitividad. En el juego 2, tiende a contraerla, porque se pierde poder de compra de los salarios y se encarecen las deudas en dólares. Es la principal fuente de incertidumbre del modelo: conviene mirar ambos.']])}
<h4>Cuenta corriente y política económica</h4>
${dl([
['Cuenta corriente 2027', 'Saldo de las cuentas con el exterior (bienes, servicios e intereses) como porcentaje del PBI. Positivo significa que entran más dólares de los que salen por estos conceptos.'],
['Baja de derechos de exportación y de aranceles', 'Recortes de 0,75 y 0,25 puntos porcentuales por trimestre. Abaratar exportar impulsa al sector transable. Abaratar importar presiona sobre la producción local y sobre los dólares.'],
['Variación del gasto público', 'Cambio del gasto fiscal en unidades del modelo (por defecto, cero). Más gasto expande la actividad y tiende a apreciar el tipo de cambio real.']])}
<h4>Obligaciones negociables (ON) de empresas</h4>
${dl([
['Liquidación pendiente de ON ya emitidas', 'Dólares de emisiones de empresas que todavía deben ingresar al mercado de cambios. US$ 2.700 millones llegarían en el primer trimestre de 2027.'],
['Pagos de ON', 'Dólares que las empresas necesitan para pagar esas deudas. La estimación del BCRA es de US$ 2.600 millones entre el cuarto trimestre de 2026 y el primero de 2027 (el simulador asigna la mitad al primer trimestre de 2027), más el valor por trimestre que se cargue de T2 a T4. Un pago mayor reduce los dólares disponibles.']])}
<h4>Capital de organismos internacionales</h4>
${dl([
['Fuente del capital de organismos', 'Se elige entre la planilla de deuda del Ministerio de Economía (MECON) y los montos del Presupuesto 2027. La elegida reemplaza a la otra; no se suman.'],
['Tipo de cambio de conversión, BID, otros préstamos y resto de organismos', 'El Presupuesto expresa las amortizaciones en pesos, y se convierten a dólares con este tipo de cambio.']])}
<h4>Compras de dólares del Banco Central</h4>
${dl([
['Factor de compras', 'Multiplicador sobre las compras mensuales de 2026, que se usan como “espejo” para 2027. Con 1 se repite el ritmo de 2026, con 1,15 compra 15 % más y con 0,75 compra 25 % menos.'],
['Compras de octubre de 2027', 'Se suponen cero, por las elecciones. Por eso el “colchón a septiembre” muestra la situación antes de ese mes.']])}
<h4>Fuentes de financiamiento en dólares</h4>
${dl([
['Saldo del programa 2026 arrastrado', 'Financiamiento ya asegurado que pasa de 2026 a 2027.'],
['Desembolso del FMI y trimestre', 'Monto (US$ 850 millones) y trimestre en que ingresa el desembolso de la cuarta revisión del acuerdo.'],
['Organismos internacionales, préstamo bilateral y privatizaciones', 'Programa total de 2027 y qué porcentaje se considera que efectivamente ingresa en cada escenario. Una parte se reparte en el primer trimestre y el resto en el segundo.'],
['Roll over intra sector público', 'Vencimientos que se renuevan dentro del propio sector público y, por tanto, no consumen dólares.'],
['Emisión local e internacional de deuda', 'Dólares que el Tesoro conseguiría colocando deuda en el mercado local (segundo y tercer trimestre) e internacional (tercero). Son cero en el escenario base.']])}
<h4>Riesgo y expectativas</h4>
${dl([
['Riesgo país a fin de 2027', 'Sobretasa que paga el país por endeudarse, en puntos básicos (100 pb = 1 punto porcentual). Se mueve en forma gradual desde el valor inicial hasta el valor supuesto para fines de 2027, que puede ser menor o mayor. Menos riesgo abarata el crédito y alivia la presión cambiaria.'],
['Probabilidad de caída del acuerdo con el FMI', 'Es la probabilidad que el mercado percibe, trimestre a trimestre, de que el acuerdo se interrumpa. Cuando sube, el mercado espera más depreciación del peso, lo que impulsa la inflación. En el bloque macro también empuja a los ahorristas a dolarizarse y reduce el ingreso de capitales.']])}
<h4>Parámetros de la curva de Phillips</h4>
<p>Estos parámetros determinan cómo se forman los precios del sector no transable. Son valores ilustrativos, no estimados con datos históricos.</p>
${dl([
['Inercia (γ)', 'Cuánto de la inflación de este trimestre repite la del trimestre anterior. El resto se explica por lo que la gente espera que ocurra con los precios. La inercia total es mayor que γ, porque las expectativas también miran al pasado en parte (ver ϑ).'],
['Peso de la inflación pasada en las expectativas (ϑ)', 'Al formar sus expectativas, las personas combinan lo que pasó con la meta o ancla de largo plazo. Este parámetro dice cuánto pesa el pasado. Con un valor alto, las expectativas siguen a la inflación reciente y cuesta más desinflar. Con un valor bajo, las expectativas siguen más a la meta.'],
['Pendiente respecto de la brecha (κ)', 'La brecha del sector N mide cuánto se aleja su producción de la capacidad que tiene instalada. Cuando hay holgura (la brecha es negativa), la presión sobre los precios es menor. Cuando la brecha se cierra, sube. κ mide cuánto cambia la inflación por cada punto de brecha. La depreciación reduce la holgura, porque encarece los insumos importados y reduce la capacidad que las empresas pueden ofrecer. Por eso puede subir los precios aunque la producción no aumente.'],
['Traspaso de la depreciación (β_E)', 'Parte de la suba del dólar que las empresas trasladan a sus precios, sobre todo por los insumos importados.'],
['Costo financiero (β_i)', 'Cuando la tasa de interés está por encima de la tasa de referencia (25 % anual), las empresas pagan más por su capital de trabajo y lo trasladan a los precios. Este parámetro mide ese efecto.'],
['Expectativas de depreciación (β_ε)', 'Cuando se espera que el dólar suba más de lo habitual, las empresas anticipan el costo de reposición y suben precios antes, sobre todo en bienes durables, inmuebles y servicios con costos dolarizados. Este parámetro mide cuánto influye esa diferencia en la inflación esperada.'],
['Efecto de la probabilidad de caída del FMI en la depreciación esperada (ε₄)', 'Cuánto sube la depreciación esperada cuando el mercado percibe más chances de que el acuerdo se interrumpa.'],
['Peso de los transables en el IPC (a)', 'Participación de los bienes transables en el índice de precios al consumidor. Se define en 60 %, y el 40 % restante corresponde a bienes y servicios no transables. Es una definición propia del simulador, adoptada por simplicidad. No fue estimada ni tomada de la literatura.']])}
<p>Además, la curva completa del modelo incluye tres elementos que el simulador no expone en el panel de edición: el aumento de los precios regulados (tarifas de energía y transporte), el exceso de liquidez en pesos y la pérdida de capacidad por la apertura y el costo de los insumos importados.</p>
<h3>3. Resultados (datos de salida)</h3>
<h4>Actividad y precios</h4>
${dl([
['Crecimiento del producto', 'Variación anual del PBI real en 2027. Se calcula sumando al crecimiento tendencial el efecto de los demás supuestos.'],
['Inflación IPC, promedio anualizado y T4-2027', 'Ritmo de aumento de precios al consumidor, expresado como tasa anual. El promedio resume el año y el valor de T4 muestra dónde termina.'],
['Tipo de cambio nominal a fin de 2027', 'Cotización final del dólar mayorista, en pesos.'],
['Tipo de cambio real (referencia = 1)', 'Compara el precio de los bienes transables con el de los no transables. Menor a 1 significa que el peso está más “fuerte” que en la referencia (apreciación real) y que importar o consumir bienes transables resulta más barato. Mayor a 1 significa que el peso está más “débil”.'],
['Tasa de interés, promedio', 'Tasa anual de la economía, que surge del equilibrio entre dinero y dólares disponibles mientras el tipo de cambio se mueva dentro de la banda.'],
['Empleo', 'Desvío porcentual del empleo respecto de la referencia. Un valor negativo indica menos empleo que en el punto de partida.'],
['Riesgo país', 'El valor supuesto a fin de 2027, para facilitar la lectura conjunta.'],
['Actividad (T4-2026 = 100)', 'Índice del nivel de actividad trimestre a trimestre.']])}
<h4>Dólares y reservas</h4>
${dl([
['Compras de divisas del BCRA', 'Total de dólares que compra el Banco Central en 2027 con el factor elegido.'],
['Fuentes, usos y resultado neto', 'Dólares que entran, dólares que salen (capital e intereses de deuda, BOPREAL) y su diferencia en cada trimestre.'],
['Colchón acumulado (septiembre y diciembre)', 'Suma acumulada de los resultados netos. Muestra cuántos dólares sobran (positivo) o faltan (negativo) para cubrir los vencimientos.'],
['Compras adicionales necesarias en T4', 'Si el colchón de diciembre es negativo, cuánto tendría que comprar de más el Banco Central para cerrar la brecha. Es cero si no hace falta.'],
['Variación de reservas y reservas brutas', 'Cambio de las reservas en el año y su nivel final, partiendo de US$ 48.653 millones. Es una cifra ilustrativa que ignora otros movimientos.'],
['Flujo neto de ON y usos totales', 'Ingresos menos pagos de obligaciones negociables, y todas las salidas de dólares por deuda en el año.']])}
<h3>4. Cómo leer los resultados</h3>
<p class="callout">Lo importante es comparar escenarios entre sí y ver qué supuesto mueve cada resultado, no leer una cifra aislada. Por ejemplo, un colchón negativo en el escenario pesimista no es una predicción de crisis. Señala que, con esos supuestos de financiamiento y compras, los dólares no alcanzarían a cubrir los vencimientos y habría que conseguir más.</p>
<h3>5. Limitaciones</h3>
${ul([
'El modelo es lineal y sus parámetros son <strong>ilustrativos, no estimados</strong> con datos históricos. Varios de ellos (el costo financiero, las expectativas de depreciación, el peso de los transables y el efecto de la probabilidad de caída del FMI) no tienen todavía una estimación empírica en la literatura económica para la Argentina, y por eso conviene probarlos con distintos valores.',
'El modelo teórico contempla el régimen en que el tipo de cambio llega al techo de la banda y el Banco Central lo defiende con reservas. Este simulador no lo incluye: no representa la venta de reservas para sostener el techo ni el cambio de comportamiento que ocurriría en ese caso.',
'El modelo teórico trata la caída del acuerdo con el FMI como un evento con consecuencias bruscas (desaparece el financiamiento asociado y salta la prima de riesgo). El simulador no lo incluye: el escenario pesimista solo eleva la probabilidad percibida de caída, sin que ocurra.',
'El peso de los transables en el IPC (60 %) es una definición propia del simulador, no estimada. Si se cambia, cambia cuánto se traslada una depreciación a los precios al consumidor.',
'Las reservas son un cálculo ilustrativo, y los datos cargados por el usuario no fueron verificados por el analista.',
'Las cifras son resultados condicionados a los supuestos, <strong>no pronósticos</strong>.'])}
</article>`;
