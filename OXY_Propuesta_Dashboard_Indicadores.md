# OXY Industrial — Propuesta de control diario e indicadores (OXY Dashboard)

**Versión 5, alineada con el modelo de datos v7 (moneda única: soles; crédito fiscal por registro; fechas de pago)** (proforma con conceptos impresos y planificación de costos, IGV y crédito fiscal). **Base:** AppSheet Core, todo dentro de AppSheet, un solo Google Sheet. Esta propuesta añade datos, jobs (bots programados) y una tercera app de solo lectura. Nada aquí está probado en AppSheet; lo marcado **⚠** se valida en la prueba de humo.

---

## 1. Hallazgos de la investigación que condicionan el diseño

| Hallazgo | Consecuencia |
|---|---|
| Un bot programado de AppSheet corre como mínimo **cada hora**, con un campo "minuto de la hora". Intervalos de varias horas se logran filtrando con condiciones sobre la hora ([foro AppSheet](https://discuss.google.dev/t/bot-hourly-scheduled/123548/1)) | El "pulso" más fino que podemos tener es **horario**. Todo lo demás son jobs diarios, semanales o mensuales con condición de hora/día |
| La vista Chart de AppSheet solo ofrece series por fila, series por columna e histograma, con opción de agregación por grupo ([documentación](https://support.google.com/appsheet/answer/10107847?hl=en)). No documenta tortas ni dispersión | Las líneas, barras y apiladas se hacen en AppSheet. Tortas, mapas de calor y comparativos complejos requieren **Looker Studio** |
| Looker Studio tiene conector nativo con AppSheet y es gratuito, pero exige ser creador o editor de la app y la misma cuenta Google ([documentación](https://support.google.com/appsheet/answer/11911810?hl=en)). También puede leer el Google Sheet directamente | Looker Studio es una **fase 2 opcional**, enlazada desde el dashboard con una acción *Open URL* |
| Los KPI semanales de costo de obra recomendados: variación de productividad de mano de obra (horas reales vs presupuestadas), costo comprometido vs real, cambios aprobados vs trabajo ejecutado, flujo de caja y salud de facturación (días de cobro), absorción de gastos generales ([Builders Tax Group](https://www.builderstaxgroup.com/post/job-cost-dashboard)) | Adaptados a OXY: consumo vs avance, horas, cobranza, complementarias. Los gastos generales y los costos comprometidos (órdenes de compra) quedan fuera por ahora |

**Modelo de costos vigente:** la proforma imprime conceptos sin IGV (subtotal, IGV y total) y tiene una **planificación de costos** interna por tipo y categoría, congelada al aceptar y sin reprogramación. Mientras la proforma está `Enviada`, sus líneas pueden corregirse; por eso `Proformas_Abiertas_N` y `Proformas_Abiertas` leen los valores vigentes de las `Enviada` en cada refresco (cada hora) y los días pasados no se recalculan. Los indicadores de obra no se afectan: la obra congela sus totales al aceptar. Por eso el margen existe: `Margen_Plan = Precio_Neto − Costo_Planificado`, y el seguimiento diario compara el **costo real imputable** (según crédito fiscal) contra lo planificado. El **avance físico se registrará** (decidido), lo que habilita CPI, proyección de costo final y margen proyectado.

---

## 2. Datos nuevos que hay que capturar

| Tabla | App | Campos | Para qué |
|---|---|---|---|
| **Avances_Obra** (confirmada; la registran Gestión y Campo) | Campo | `Avance_ID`, `Obra_ID`, `Fecha`, `Avance_Pct` (acumulado 0–100, `Valid_If >= último avance`), `Descripcion`, `Foto`, `Registrado_Por`, `Creado_En` | Valor ganado, CPI, proyección de cierre, evidencia fotográfica. |
| **Partes_Diarios** (opcional) | Campo | `Parte_ID`, `Obra_ID`, `Fecha`, `Personal_Presente`, `Actividades`, `Incidentes`, `Clima`, `Foto` | Bitácora diaria; sirve de "pulso" de campo y de respaldo ante clientes industriales |
| **Facturas_Obra** (opcional) | Gestión | `Factura_ID`, `Obra_ID`, `Nro`, `Fecha_Emision`, `Monto`, `Fecha_Vencimiento` | Hoy no hay fecha de factura, así que el vencimiento de cobranza se aproxima con los días desde el fin de obra. Con facturas se calcula cartera por vencer de verdad |

**Moneda única:** todo el modelo trabaja en soles (PEN); no hay conversiones. Margen y consumo se calculan en base neta (`Precio_Neto_Base`, `Costo_Planificado_Base`, `Costo_Imputable`); cobranza en base bruta (`Total_Cobrar_Base`). El costo se reconoce al registrar el gasto (devengado) y el flujo de caja usa `Fecha_Pago_Real`: abonos − gastos pagados (`Total_Gasto` con fecha de pago real) − personal; los gastos sin pagar se muestran en `Por_Pagar`. Crédito fiscal por registro (`Es_Credito_Fiscal`), no global.

---

## 3. Tablas de indicadores (las llenan los jobs)

Principio: el dashboard **no lee transacciones**, lee estas tablas pequeñas y pre-agregadas. Las apps de Campo y Gestión siguen mostrando valores en vivo.

Campos comunes en todas: `Anio_Semana` (ej. `2026-W41`), `Anio_Mes` (ej. `2026-10`), `Es_Fin_Semana`, `Es_Fin_Mes` (Sí/No), `Generado_En`. Permiten agrupar por semana o mes en los charts sin tablas extra.

| Tabla | Granularidad | Campos principales |
|---|---|---|
| **Snap_Obra_Dia** | 1 fila por obra activa por día, **actualizada cada hora** (la última pasada es el cierre). Clave `Obra_ID\|yyyy-MM-dd` | `Obra_ID`, `Cliente_ID`, `Estado_Obra`, `Precio_Neto`, `Total_Cobrar`, `Costo_Planificado`, `Gasto_Total`, `Personal_Total`, `Costo_Real`, `Consumo_Pct` (Costo_Real/Costo_Planificado), `Margen_Plan`, `Margen_Real_Parcial`, `IGV_No_Recuperable`, `Costo_MO_Interna`, `Costo_MO_Tercerizada`, `Gasto_Dia`, `Horas_Dia`, `Abonos_Acum`, `Saldo`, `Pct_Cobrado`, `Facturado_Acum`, `Pct_Facturado`, `Facturado_Sin_Cobrar`, `Cartera_Vencida`, `Dias_Sin_Gastos`, `Dias_Sin_Avance`, `Flujo_Caja`, `Por_Pagar`, `Dias_En_Ejecucion`, `Dias_Atraso`, `Dias_Sin_Movimiento`, `Gastos_Sin_Sustento` (sin comprobante, excluye depreciación), `Semaforo`. Con avance físico: `Avance_Pct`, `Valor_Ganado` (Costo_Planificado × avance), `CPI`, `Proyeccion_Costo_Final`, `Margen_Proyectado` |
| **Snap_Costo_Tipo_Semana** | 1 fila por obra activa × tipo de costo, **solo domingo** (para no explotar el volumen) | `Obra_ID`, `Categoria_ID`, `Tipo_Costo_ID`, `Presupuesto` (`Costo_Imputable` planificado), `Real` (costo imputable), `Pct` |
| **Snap_Global_Hora** | 1 fila por hora de 07:00 a 19:00 | `Fecha_Hora`, `Gastos_Hoy_N`, `Gastos_Hoy`, `Gastos_Sin_Foto_Hoy`, `Horas_Pend_Aprobar`, `Abonos_Hoy`, `Obras_Activas`, `Alertas_Abiertas` |
| **Snap_Global_Dia** | 1 fila por día (23:45) | Conteo de obras por estado, `Costo_Dia`, `Horas_Dia`, `Horas_Extra_Dia`, `Abonos_Dia`, `Por_Cobrar`, `Proformas_Abiertas_N`, `Proformas_Abiertas`, `Aceptadas_Dia`, `Rechazadas_Dia`, `Pct_Costo_Con_Factura_30d` |
| **Alertas** | 1 fila por alerta | `Alerta_ID` (clave `Regla\|Obra\|Fecha` para no duplicar), `Fecha_Hora`, `Regla`, `Severidad` (Info/Ámbar/Rojo), `Obra_ID`, `Mensaje`, `Estado` (Abierta/Reconocida/Resuelta), `Reconocida_Por` |
| **Metas_KPI** | Configuración | `KPI`, `Verde_Hasta`, `Ambar_Hasta`, `Sentido` (Menor_Mejor/Mayor_Mejor), `Descripcion` |
| **Jobs_Control** | 1 fila por job (también sirve de ancla para bots de una sola ejecución) | `Job_ID`, `Descripcion`, `Programacion`, `Ultima_Ejecucion`, `Ultimo_Resultado`, `Activo` |

**Ejemplos de expresiones** (paso *Add new row* del bot sobre `Obras`, con `Fecha = TODAY()` y `[_THISROW]` como la obra):
```
Gasto_Dia = SUM(SELECT(Gastos_Obra[Costo_Imputable], AND([Obra_ID]=[_THISROW].[Obra_ID],[Fecha]=TODAY(),[Estado]="Vigente")))
Costo_Real = [Total_Gastos] + [Total_Personal]
CPI = IF([Costo_Real]>0, ([Costo_Planificado_Base]*[Avance_Actual]/100)/[Costo_Real], "")   // el valor ganado se mide sobre el presupuesto de COSTO, no sobre el precio
Dias_Sin_Movimiento = TODAY() - MAX(LIST(
   MAX(SELECT(Gastos_Obra[Fecha],[Obra_ID]=[_THISROW].[Obra_ID])),
   MAX(SELECT(Registro_Horas[Fecha],[Obra_ID]=[_THISROW].[Obra_ID])),
   MAX(SELECT(Avances_Obra[Fecha],[Obra_ID]=[_THISROW].[Obra_ID]))))   ⚠ validar con listas vacías
```

---

## 4. Catálogo de indicadores por periodo

**Cada hora (07:00–19:00, lun–sáb) — "pulso operativo"**
| Indicador | Por qué |
|---|---|
| Gastos registrados hoy (cantidad y monto en PEN) | Ver si el campo está registrando o hay atraso de captura |
| Gastos de hoy sin foto de comprobante | Se corrige el mismo día, no al cierre de mes |
| Horas pendientes de aprobar | Cuello de botella de Gestión |
| Abonos recibidos hoy | Cobranza en tiempo real |
| Alertas abiertas | Estado general |

**Cada día (cierre 23:30 y briefing 07:30)**
| Indicador | Definición |
|---|---|
| Consumo vs planificado por obra | `Costo_Real / Costo_Planificado_Base`; si hay avance, también frente a `Avance_Pct`. Semáforo |
| Margen real parcial vs margen planificado | `Precio_Neto − Costo_Real` frente a `Margen_Plan` |
| CPI y margen proyectado | `Valor_Ganado = Costo_Planificado × Avance`; `CPI = Valor_Ganado / Costo_Real`; `Proyección = Costo_Planificado / CPI`; `Margen_Proyectado = Precio_Neto − Proyección` |
| Gasto del día y horas del día por obra | Ritmo de gasto (burn rate) |
| Obras sin movimiento (≥3 días) | Detecta obras abandonadas o registros atrasados |
| Obras atrasadas | `Fecha_Fin_Estimada` vencida con obra abierta |
| Saldo por cobrar y % cobrado por obra | Cobranza al día |
| Proformas por vencer (≤3 días) y sin respuesta (>7 días) | Pipeline comercial |
| % del costo respaldado con factura e **IGV no recuperable** | Cuánto IGV pasa a costo por boletas o falta de factura (muy relevante en viáticos y transporte) |
| Mano de obra propia vs tercerizada | Peso de cada modalidad en el costo de la obra |

**Cada semana (lunes 07:00, cierre del domingo)**
| Indicador | Definición |
|---|---|
| Costo por tipo de costo vs presupuesto, por obra | Dónde se desvía (material, personal, transporte…) |
| Horas totales y % de horas extra por obra | Variación de productividad de mano de obra |
| Abonos vs gastos de la semana | Flujo de caja semanal |
| Pipeline: proformas emitidas, aceptadas, rechazadas y tasa de conversión | Salud comercial |
| Top 5 proveedores por monto | Concentración de compras |
| Obras terminadas sin cobrar y días transcurridos | Antigüedad de cartera (aproximada, o exacta con `Facturas_Obra`) |

**Cada mes (día 1, 07:00)**
| Indicador | Definición |
|---|---|
| Margen de las obras cerradas | `Precio_Neto − Costo real`, absoluto y %, frente al margen planificado |
| Mezcla de costos del mes | Por categoría y por modalidad (interna / tercerizada) |
| Facturación/cobranza y flujo de caja del mes | Abonos − gastos pagados (`Fecha_Pago_Real`); pendientes en `Por_Pagar` |
| Ciclo comercial | Días emisión→aceptación, aceptación→inicio, fin de obra→cobro completo |
| Concentración de clientes | % del total de los 3 mayores clientes y días medios de pago por cliente |
| Cumplimiento de plazo | % de obras terminadas dentro de la fecha estimada |

Todo consolidado en soles (PEN), la moneda única del modelo.

---

## 5. Reglas de alerta (umbrales editables en `Metas_KPI`)

| Regla | Ámbar | Rojo |
|---|---|---|
| Consumo del presupuesto de costo | ≥ 90 % | > 100 % |
| Consumo menos avance | > 10 pp | > 20 pp |
| CPI | < 0.95 | < 0.85 |
| Obra en ejecución sin avance registrado (el avance es diario) | ≥ 3 días | ≥ 7 días |
| **Días sin ingresar gastos/costos** (obra en ejecución) | > 7 días | > 14 días |
| **Factura de venta vencida** (días de mora) | ≥ 1 día | > 30 días |
| **Rezago de facturación** (avance % − facturado %) | > 15 pp | > 30 pp |
| Margen real parcial por debajo del planificado | cae > 5 pp | cae > 10 pp |
| Gasto de un tipo sobre su presupuesto | ≥ 90 % | > 100 % |
| Días sin movimiento en obra activa | ≥ 3 | ≥ 7 |
| Días de atraso sobre fecha estimada | ≥ 1 | ≥ 7 |
| % de gasto sin comprobante (30 días, excluye depreciación) | > 20 % | > 35 % |
| Gasto en un tipo sin línea planificada | cualquiera | — |
| Horas pendientes de aprobar | > 48 h | > 5 días |
| Obra terminada sin abonos | > 30 días | > 60 días |
| Proforma enviada sin respuesta | > 7 días | > 15 días |

Semántica de `Metas_KPI`: *Menor_Mejor* alerta si el valor supera el umbral; *Mayor_Mejor* (p. ej. CPI) si queda por debajo.

Cada alerta tiene clave `Regla|Obra|Fecha` para que el job no duplique, se notifica por *push* (rojas también por correo) y Gestión la marca *Reconocida* o *Resuelta* desde la app.

---

## 6. Calendario de jobs (zona horaria de la app: America/Lima)

| Job | Cuándo | Qué hace | Tabla destino |
|---|---|---|---|
| J01 Pulso horario | cada hora, minuto 05, condición 07–19 h y lun–sáb ⚠ | Una fila de métricas globales | `Snap_Global_Hora` |
| J03 Alertas del día | 07:15 | Evalúa reglas y crea alertas | `Alertas` |
| J04 Briefing matutino | 07:30 | Correo/push a Gestión: resumen de ayer y alertas abiertas | — |
| J06 Snapshot por obra | **cada hora** (07–19 h) y 23:30 | Crea la fila del día si falta y la refresca; la última pasada del día queda como cierre | `Snap_Obra_Dia` |
| J07 Snapshot global | **cada hora** (07–19 h) y 23:45 | Igual: crea y refresca la fila del día | `Snap_Global_Dia` |
| J08 Costo por tipo | domingo 23:50 | Presupuesto vs real por obra y tipo | `Snap_Costo_Tipo_Semana` |
| J09 Resumen semanal | lunes 07:00 | Correo a Gerencia con KPIs de la semana | — |
| J10 Resumen mensual | día 1, 07:00 | Correo con cierre del mes | — |
| J11 Mantenimiento | 03:00 | Purga según retención (sección 8) | varias |

**Mecánica:**
- Los bots que escriben una sola fila por ejecución cuelgan de `Jobs_Control` con condición `[Job_ID]="J07"`. Los de una fila por obra cuelgan de `Obras` con condición `[Estado]` activo.
- **Refresco horario sin duplicar filas:** un bot sobre `Obras` (activas) crea la fila de hoy solo si no existe (`ISBLANK(LOOKUP([Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Snap_Obra_Dia","Snap_ID","Snap_ID"))`), y otro bot sobre `Snap_Obra_Dia` con `[Fecha]=TODAY()` actualiza sus columnas leyendo las virtuales de la obra (`[Obra_ID].[Total_Gastos]`, `[Obra_ID].[CPI]`, …). ⚠ validar.
- Cada job termina actualizando `Jobs_Control.Ultima_Ejecucion` para mostrar "datos actualizados a las hh:mm" en el dashboard.
- Una condición de hora típica: `HOUR(TIMENOW())` entre 7 y 19, y `WEEKDAY(TODAY())<>1` (domingo). ⚠ validar en qué zona horaria evalúa `TIMENOW()` el bot.

---

## 7. App OXY Dashboard

**Por qué una tercera app y no vistas dentro de Gestión**
- **Rendimiento:** incluye solo tablas pequeñas (snapshots, alertas, metas y catálogos ligeros). No sincroniza `Gastos_Obra` ni `Abonos_Obra`, así que abre rápido en celular.
- **Seguridad:** es de solo lectura. No hay formularios ni acciones de datos, salvo reconocer alertas.
- **Costo:** AppSheet cobra por usuario, no por app. Esta app no agrega costo si la usan los mismos 5 de Gestión ⚠ confirmar condiciones de Core.

**Vistas (Dashboard view que agrupa charts y decks)**
| Vista | Contenido |
|---|---|
| **Hoy** | Tarjetas del último `Snap_Global_Hora`, barras de gastos por hora del día, alertas abiertas |
| **Obras** | Tarjetas con semáforo y barra de consumo vs avance. Al abrir una obra: línea de consumo vs avance en el tiempo, CPI, gasto diario |
| **Semana** | Barras de gasto por semana (suma de `Gasto_Dia` agrupada por `Anio_Semana`), abonos vs gastos, horas |
| **Mes** | Mezcla de costos, ahorro de obras cerradas, cobranza del mes |
| **Cobranza** | Saldo por obra y por cliente, obras terminadas sin cobrar, tendencia de días de cobro |
| **Comercial** | Pipeline de proformas, conversión mensual, ciclo de aceptación |
| **Alertas** | Lista filtrable por severidad y obra; acción *Reconocer* |

Los filtros de periodo son *slices* sobre las snapshots: `S_Hoy`, `S_Ultimos7Dias` (`[Fecha]>=TODAY()-7`), `S_MesActual`, `S_FinSemana` (`[Es_Fin_Semana]="Si"`), `S_FinMes`.

**Límites a asumir:** solo líneas, barras y apilados (más histograma). No hay torta, mapa de calor ni dispersión.

**Fase 2 (opcional): Looker Studio.** Se conecta directo al Google Sheet o a AppSheet, es gratuito y permite tortas, mapas de calor y comparativos libres. Se enlaza desde el dashboard con *Open URL*. Verifica si permite enviar el reporte por correo programado.

---

## 8. Volumen y retención (Sheets debe mantenerse liviano)

| Tabla | Filas por año (aprox.) | Retención propuesta |
|---|---|---|
| Snap_Global_Hora | 13 × 312 ≈ 4 000 | 14 días |
| Snap_Obra_Dia (20 obras activas) | ≈ 7 300 | Diario 90 días; después solo `Es_Fin_Semana="Si"`; mensuales para siempre |
| Snap_Global_Dia | 365 | Indefinida |
| Snap_Costo_Tipo_Semana (20 × 7 × 52) | ≈ 7 300 | 1 año; después solo `Es_Fin_Mes` |
| Alertas | variable | Resueltas > 90 días se archivan |

J11 aplica estas reglas con *Delete row* en bots. Si crece más, se archiva por año a otra hoja.

---

## 9. Decisiones

**Confirmadas**
- Crédito fiscal: se aplica.
- Avance físico: se registra **a diario** en `Avances_Obra` (Gestión y Campo); alerta desde 3 días sin avance.
- Dashboard: lo ven **solo los 5 usuarios de Gestión**; se procesa **cada hora**.
- Pruebas de humo: aprobadas.
- **Facturas de venta:** OXY emite varias por obra (adelantos, valorizaciones) → `Facturas_Obra` entra en esta etapa; habilita aging por factura, cartera vencida, DSO y rezago de facturación.
- **Umbrales:** los de la sección 5 quedan como valores iniciales en `Metas_KPI` (ajustables sin tocar las apps).
- **Horario:** lunes a sábado 07:00–19:00 más pasada de cierre 23:30.
- **Gastos/costos:** se ingresan casi a diario; más de 7 días sin ingreso genera alerta.

**Pendientes**
1. **Partes diarios de obra y Looker Studio:** siguen siendo opcionales, sin decidir.
