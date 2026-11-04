"""Simula las vistas de OXY Dashboard (estilo AppSheet, movil 390 px) leyendo datos/*.csv
(mismas tablas y columnas de OXYData). Salida: salida/*.png + OXY_Dashboard_Simulacion.html"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

D = lambda n: pd.read_csv(f'datos/{n}.csv')
obra = D('Snap_Obra_Dia'); costo = D('Snap_Costo_Tipo_Semana'); hora = D('Snap_Global_Hora')
dia = D('Snap_Global_Dia'); alert = D('Alertas'); metas = D('Metas_KPI').set_index('KPI')
obras = D('Obras'); cli = D('Clientes'); fac = D('Facturas_Obra')
for t, c in [(obra,'Fecha'),(costo,'Fecha'),(hora,'Fecha'),(dia,'Fecha')]: t[c] = pd.to_datetime(t[c])
alert['Fecha_Hora'] = pd.to_datetime(alert['Fecha_Hora'])
fac['Fecha_Vencimiento'] = pd.to_datetime(fac['Fecha_Vencimiento'])

HOY = dia.Fecha.max()
nom = obras.set_index('Obra_ID').Codigo.to_dict()
corto = lambda o: nom[o].split(' ')[0].replace('-2026','') + ' ' + ' '.join(nom[o].split(' ')[1:3]).rstrip(' -')
cliente = obras.set_index('Obra_ID').Cliente_ID.map(cli.set_index('Cliente_ID').Nombre_Corto).to_dict()

AZ, VE, AM, RO, GR, TX = '#2F80ED', '#27AE60', '#F2B01E', '#E74C3C', '#9AA5B1', '#22313F'
SEM = {'Verde': VE, 'Ambar': AM, 'Rojo': RO}
W, DPI = 3.9, 200
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.edgecolor': '#CBD2D9', 'axes.titlesize': 9,
                     'axes.titleweight': 'bold', 'axes.titlelocation': 'left'})
soles = lambda v: f'S/ {v:,.0f}'
ult = obra[obra.Fecha == obra.Fecha.max()].copy()
ult['Obra'] = ult.Obra_ID.map(corto)

def pantalla(titulo, alto, filas):
    fig = plt.figure(figsize=(W, alto), facecolor='#F4F6F8')
    gs = fig.add_gridspec(len(filas) + 1, 1, height_ratios=[0.5] + filas, hspace=0.55,
                          left=0.30, right=0.95, top=0.985, bottom=0.03)
    h = fig.add_subplot(gs[0]); h.axis('off'); p = h.get_position(); h.set_position([0, p.y0, 1, p.height])
    h.add_patch(plt.Rectangle((-1, 0), 3, 1, color=AZ, transform=h.transAxes, clip_on=False))
    h.text(0.04, 0.45, titulo, color='white', fontsize=11, fontweight='bold', va='center', transform=h.transAxes)
    return fig, [fig.add_subplot(gs[i + 1]) for i in range(len(filas))]

def tarjetas(ax, items):
    ax.axis('off'); n = len(items); p = ax.get_position(); ax.set_position([.03, p.y0, .94, p.height])
    for i, (t, v, c) in enumerate(items):
        x = i / n
        ax.add_patch(FancyBboxPatch((x + .01, .05), 1 / n - .03, .9, boxstyle='round,pad=0.01,rounding_size=0.04',
                                    fc='white', ec='#E1E5EA', transform=ax.transAxes))
        ax.text(x + .5 / n, .66, v, ha='center', fontsize=11, fontweight='bold', color=c, transform=ax.transAxes)
        ax.text(x + .5 / n, .25, t, ha='center', fontsize=6.5, color=GR, transform=ax.transAxes)

def guardar(fig, nombre, figs):
    fig.savefig(f'salida/{nombre}.png', dpi=DPI, facecolor=fig.get_facecolor()); figs.append(nombre)
    plt.close(fig)

def barras_h(ax, labels, vals, colors, fmt='{:.0f}', titulo=''):
    ax.barh(labels, vals, color=colors); ax.invert_yaxis(); ax.set_title(titulo)
    for i, v in enumerate(vals): ax.text(v, i, ' ' + fmt.format(v), va='center', fontsize=6.5, color=TX)
    ax.tick_params(labelsize=6.5); ax.set_xlim(0, max(vals) * 1.2 if len(vals) and max(vals) > 0 else 1)

figs = []
# ---------- 1. HOY ----------
g = dia[dia.Fecha == HOY].iloc[0]; hh = hora[hora.Fecha == hora.Fecha.max()]
fig, (a, b, c, d) = pantalla(f'Hoy · {HOY:%d/%m/%Y}', 7.6, [.8, 1.6, 1.6, 1.6])
tarjetas(a, [('Obras en ejecución', f'{int(g.Obras_En_Ejecucion)}', AZ), ('Alertas abiertas', f'{int(hh.Alertas_Abiertas.iloc[-1])}', RO),
             ('Horas por aprobar', f'{int(hh.Horas_Pend_Aprobar.iloc[-1])}', AM)])
b.bar(hh.Hora.astype(str) + 'h', hh.Gastos_Hoy, color=AZ); b.set_title('Gastos del día por hora (S/)'); b.tick_params(labelsize=6)
c.plot(dia.Fecha.tail(14), dia.Horas_Dia.tail(14), color=AZ, marker='o', ms=3); c.set_title('Horas registradas · 14 días')
c.tick_params(labelsize=6); c.tick_params(axis='x', rotation=30)
d.bar(dia.Fecha.tail(14).dt.strftime('%d'), dia.Abonos_Dia.tail(14), color=VE); d.set_title('Abonos diarios (S/) · 14 días'); d.tick_params(labelsize=6)
guardar(fig, '01_Hoy', figs)
# ---------- 2. OBRAS ----------
act = ult[ult.Estado_Obra.isin(['En ejecucion', 'Pausada', 'Terminada'])].sort_values('Consumo_Pct', ascending=False)
fig, (a, b, c) = pantalla('Obras', 8.4, [.9, 3.0, 2.2])
tarjetas(a, [(k, str((ult.Semaforo == k).sum()), col) for k, col in SEM.items()])
y = np.arange(len(act)); b.barh(y - .2, act.Consumo_Pct * 100, .4, color=AZ, label='Consumo %')
b.barh(y + .2, act.Avance_Pct, .4, color=VE, label='Avance %'); b.set_yticks(y, act.Obra); b.invert_yaxis()
b.axvline(metas.loc['CONSUMO_PLAN_PCT', 'Umbral_Ambar'] * 100, color=AM, ls='--', lw=.8)
b.axvline(100, color=RO, ls='--', lw=.8); b.set_title('Consumo vs avance (%)'); b.legend(fontsize=6, frameon=False, loc='lower right'); b.tick_params(labelsize=6.5)
c.barh(act.Obra, act.Margen_Proyectado, color=[SEM[s] for s in act.Semaforo]); c.invert_yaxis()
c.set_title('Margen proyectado (S/)'); c.tick_params(labelsize=6.5)
guardar(fig, '02_Obras', figs)
# ---------- 3. DETALLE OBRA (la de mayor consumo) ----------
oid = act.iloc[0].Obra_ID; s = obra[obra.Obra_ID == oid].sort_values('Fecha')
fig, (a, b, c, d) = pantalla(f'Detalle · {corto(oid)}', 8.2, [.8, 1.8, 1.6, 1.6])
r = s.iloc[-1]
tarjetas(a, [('CPI', f'{r.CPI:.2f}', RO if r.CPI < metas.loc['CPI', 'Umbral_Rojo'] else AM if r.CPI < metas.loc['CPI', 'Umbral_Ambar'] else VE),
             ('Avance', f'{r.Avance_Pct:.0f}%', AZ), ('Consumo', f'{r.Consumo_Pct * 100:.0f}%', AM)])
b.plot(s.Fecha, s.Consumo_Pct * 100, color=AZ, label='Consumo %'); b.plot(s.Fecha, s.Avance_Pct, color=VE, label='Avance %')
b.set_title('Consumo vs avance'); b.legend(fontsize=6, frameon=False); b.tick_params(labelsize=6)
c.plot(s.Fecha, s.CPI, color=TX); c.axhline(metas.loc['CPI', 'Umbral_Ambar'], color=AM, ls='--', lw=.8)
c.axhline(metas.loc['CPI', 'Umbral_Rojo'], color=RO, ls='--', lw=.8); c.set_title('CPI (umbrales ámbar/rojo)'); c.tick_params(labelsize=6)
d.plot(s.Fecha, s.Margen_Plan, color=GR, label='Margen plan'); d.plot(s.Fecha, s.Margen_Proyectado, color=AZ, label='Margen proyectado')
d.set_title('Margen (S/)'); d.legend(fontsize=6, frameon=False); d.tick_params(labelsize=6)
guardar(fig, '03_Detalle_Obra', figs)
# ---------- 4. SEMANA ----------
ult_sem = costo[costo.Anio_Semana == costo.Anio_Semana.max()]
t = ult_sem.groupby('Tipo_Costo_ID')[['Presupuesto', 'Real']].sum()
sem_cost = obra[obra.Fecha >= HOY - pd.Timedelta(days=27)].groupby('Anio_Semana').Gasto_Dia.sum()
fig, (a, b, c) = pantalla(f'Semana · {costo.Anio_Semana.max()}', 7.0, [.8, 2.0, 2.0])
tarjetas(a, [('Presupuesto', soles(t.Presupuesto.sum()), GR), ('Real', soles(t.Real.sum()), AZ), ('Desvío', f'{t.Real.sum() / t.Presupuesto.sum() - 1:+.0%}', AM)])
x = np.arange(len(t)); b.bar(x - .2, t.Presupuesto, .4, color=GR, label='Presupuesto'); b.bar(x + .2, t.Real, .4, color=AZ, label='Real')
b.set_xticks(x, t.index, fontsize=6.5); b.set_title('Costo por tipo: presupuesto vs real'); b.legend(fontsize=6, frameon=False); b.tick_params(labelsize=6)
c.bar(sem_cost.index.str[-3:], sem_cost.values, color=AZ); c.set_title('Gasto semanal (S/) · últimas 4 semanas'); c.tick_params(labelsize=6.5)
guardar(fig, '04_Semana', figs)
# ---------- 5. MES ----------
dm = dia.assign(M=dia.Fecha.dt.to_period('M').astype(str)).groupby('M').agg(Abonos=('Abonos_Dia', 'sum'), Facturado=('Facturado_Dia', 'sum'), Horas=('Horas_Dia', 'sum'), Extra=('Horas_Extra_Dia', 'sum'))
cm = obra.assign(M=obra.Fecha.dt.to_period('M').astype(str)).groupby('M').Gasto_Dia.sum()
fig, (a, b, c) = pantalla('Mes', 7.0, [.8, 2.0, 2.0])
mact = dm.index[-1]
tarjetas(a, [('Abonos mes', soles(dm.Abonos[mact]), VE), ('Costo mes', soles(cm[mact]), AZ), ('Horas mes', f'{dm.Horas[mact]:,.0f}', AM)])
x = np.arange(len(dm)); b.bar(x - .2, dm.Abonos, .4, color=VE, label='Abonos'); b.bar(x + .2, cm.reindex(dm.index).fillna(0), .4, color=AZ, label='Costo')
b.set_xticks(x, dm.index.str[-2:]); b.set_title('Abonos vs costo por mes (S/)'); b.legend(fontsize=6, frameon=False); b.tick_params(labelsize=6.5)
c.bar(x, dm.Horas - dm.Extra, color=AZ, label='Normales'); c.bar(x, dm.Extra, bottom=dm.Horas - dm.Extra, color=AM, label='Extra')
c.set_xticks(x, dm.index.str[-2:]); c.set_title('Horas por mes'); c.legend(fontsize=6, frameon=False); c.tick_params(labelsize=6.5)
guardar(fig, '05_Mes', figs)
# ---------- 6. COBRANZA ----------
hoyd = HOY; pend = fac[(fac.Estado == 'Vigente')].copy()
pend['Dias'] = (hoyd - pend.Fecha_Vencimiento).dt.days
cart = dia.tail(60)
fig, (a, b, c) = pantalla('Cobranza', 7.4, [.8, 2.2, 2.0])
tarjetas(a, [('Por cobrar', soles(g.Por_Cobrar), AZ), ('Cartera vencida', soles(g.Cartera_Vencida), RO), ('% vencido', f'{g.Cartera_Vencida / g.Por_Cobrar:.0%}', AM)])
b.plot(cart.Fecha, cart.Por_Cobrar - cart.Cartera_Vencida, color=AZ, label='Vigente'); b.plot(cart.Fecha, cart.Cartera_Vencida, color=RO, label='Vencida')
b.set_title('Por cobrar · 60 días (S/)'); b.legend(fontsize=6, frameon=False, loc='upper left'); b.tick_params(labelsize=6)
por = ult.set_index('Obra').Cartera_Vencida.sort_values(ascending=False); por = por[por > 0]
barras_h(c, por.index, por.values, RO, '{:,.0f}', 'Cartera vencida por obra (S/)')
guardar(fig, '06_Cobranza', figs)
# ---------- 7. COMERCIAL ----------
cd = dia.tail(90).assign(S=lambda d: d.Anio_Semana).groupby('S').agg(Acep=('Aceptadas_Dia', 'sum'), Rech=('Rechazadas_Dia', 'sum'))
fig, (a, b, c) = pantalla('Comercial', 7.0, [.8, 2.0, 2.0])
tarjetas(a, [('Proformas abiertas', f'{int(g.Proformas_Abiertas_N)}', AZ), ('Monto abierto', soles(g.Proformas_Abiertas), AM), ('Obras por iniciar', f'{int(g.Obras_Por_Iniciar)}', GR)])
b.plot(dia.Fecha, dia.Proformas_Abiertas, color=AZ)
b.set_title('Monto en proformas abiertas (S/)'); b.tick_params(labelsize=6)
x = np.arange(len(cd)); c.bar(x, cd.Acep, color=VE, label='Aceptadas'); c.bar(x, -cd.Rech, color=RO, label='Rechazadas')
c.set_xticks(x, cd.index.str[-3:], fontsize=6); c.set_title('Aceptadas / rechazadas por semana'); c.legend(fontsize=6, frameon=False); c.tick_params(labelsize=6)
guardar(fig, '07_Comercial', figs)
# ---------- 8. ALERTAS ----------
ab = alert[alert.Estado == 'Abierta']; porr = alert.groupby(['Regla', 'Severidad']).size().unstack(fill_value=0)
semn = alert.assign(S=alert.Fecha_Hora.dt.strftime('%G-W%V')).groupby('S').size().tail(12)
fig, (a, b, c) = pantalla('Alertas', 8.0, [.8, 2.4, 1.9])
tarjetas(a, [('Abiertas', str(len(ab)), RO), ('Reconocidas', str((alert.Estado == 'Reconocida').sum()), AM), ('Resueltas', str((alert.Estado == 'Resuelta').sum()), VE)])
bot = np.zeros(len(porr))
for sv in [s for s in ['Rojo', 'Ambar', 'Info'] if s in porr]:
    b.barh(porr.index, porr[sv], left=bot, color={'Rojo': RO, 'Ambar': AM, 'Info': AZ}[sv], label=sv); bot += porr[sv].values
b.invert_yaxis(); b.set_title('Alertas por regla y severidad'); b.legend(fontsize=6, frameon=False); b.tick_params(labelsize=5.5)
c.bar(semn.index.str[-3:], semn.values, color=AZ); c.set_title('Alertas por semana · 12 semanas'); c.tick_params(labelsize=6)
guardar(fig, '08_Alertas', figs)

# ---------- Hojas de contacto ----------
from matplotlib.image import imread
imgs = [imread(f'salida/{n}.png') for n in figs]
fig, axs = plt.subplots(1, 4, figsize=(16, 9), facecolor='white')
for ax, im in zip(axs, imgs[:4]): ax.imshow(im); ax.axis('off')
fig.savefig('salida/00_Contacto_1.png', dpi=110); plt.close(fig)
fig, axs = plt.subplots(1, 4, figsize=(16, 9), facecolor='white')
for ax, im in zip(axs, imgs[4:]): ax.imshow(im); ax.axis('off')
fig.savefig('salida/00_Contacto_2.png', dpi=110); plt.close(fig)


# ---------- Pagina HTML descriptiva ----------
rng = lambda t, c='Fecha': f"{pd.to_datetime(t[c]).min():%d/%m/%Y} – {pd.to_datetime(t[c]).max():%d/%m/%Y}"
d14 = f"{dia.Fecha.tail(14).min():%d/%m/%Y} – {HOY:%d/%m/%Y}"; d60 = f"{dia.Fecha.tail(60).min():%d/%m/%Y} – {HOY:%d/%m/%Y}"
d90 = f"{dia.Fecha.tail(90).min():%d/%m/%Y} – {HOY:%d/%m/%Y}"; d4s = f"{HOY - pd.Timedelta(days=27):%d/%m/%Y} – {HOY:%d/%m/%Y}"
hd = f"{hora.Fecha.max():%d/%m/%Y}"; u = f"{obra.Fecha.max():%d/%m/%Y}"
V = [
 ('01_Hoy', 'Hoy', 'Foto operativa del día para saber de un vistazo si algo requiere atención: obras activas, alertas abiertas, horas por aprobar y cómo avanzan gastos, horas y abonos.',
  [('Snap_Global_Dia', 'Obras_En_Ejecucion, Horas_Dia, Abonos_Dia', f'Tarjeta: {u}. Líneas/barras: {d14}'),
   ('Snap_Global_Hora', 'Hora, Gastos_Hoy, Horas_Pend_Aprobar, Alertas_Abiertas', f'Último día con datos: {hd} (07–19 h)')], 'Barras y línea'),
 ('02_Obras', 'Obras', 'Compara todas las obras vivas: cuánto presupuesto han consumido frente a cuánto han avanzado y qué margen proyectado dejan. El color es el semáforo calculado por el job.',
  [('Snap_Obra_Dia', 'Obra_ID, Estado_Obra, Consumo_Pct, Avance_Pct, Margen_Proyectado, Semaforo', f'Último snapshot: {u}'),
   ('Metas_KPI (KPI: Indicador Clave de Desempeño)', 'CONSUMO_PLAN_PCT (Umbral_Ambar, Umbral_Rojo)', 'Líneas punteadas de ámbar y rojo'),
   ('Obras', 'Obra_ID, Codigo', 'Etiquetas')], 'Barras agrupadas / barras'),
 ('03_Detalle_Obra', 'Detalle de obra', f'Historia de una obra ({corto(oid)}, la de mayor consumo): si el consumo se adelanta al avance, cómo evoluciona el CPI (Índice de Desempeño de Costo: valor ganado ÷ costo real; menor a 1 indica sobrecosto) y si el margen proyectado se aleja del plan.',
  [('Snap_Obra_Dia', 'Fecha, Consumo_Pct, Avance_Pct, CPI (Índice de Desempeño de Costo), Margen_Plan, Margen_Proyectado', f'Toda la vida de la obra: {rng(s)}'),
   ('Metas_KPI (KPI: Indicador Clave de Desempeño)', 'CPI (Índice de Desempeño de Costo): Umbral_Ambar, Umbral_Rojo', 'Líneas de referencia')], 'Líneas'),
 ('04_Semana', 'Semana', 'Control semanal del gasto: presupuesto vs real por tipo de costo en la última semana, y la tendencia del gasto de las últimas semanas.',
  [('Snap_Costo_Tipo_Semana', 'Anio_Semana, Tipo_Costo_ID, Presupuesto, Real', f'Última semana: {costo.Anio_Semana.max()}'),
   ('Snap_Obra_Dia', 'Anio_Semana, Gasto_Dia', f'{d4s}')], 'Barras agrupadas / barras'),
 ('05_Mes', 'Mes', 'Visión mensual: cuánto se cobró frente a cuánto se gastó, y el volumen de horas normales y extra.',
  [('Snap_Global_Dia', 'Fecha, Abonos_Dia, Horas_Dia, Horas_Extra_Dia', f'{rng(dia)}'),
   ('Snap_Obra_Dia', 'Fecha, Gasto_Dia', f'{rng(obra)}')], 'Barras / barras apiladas'),
 ('06_Cobranza', 'Cobranza', 'Seguimiento de la plata por cobrar y la cartera vencida, global y por obra.',
  [('Snap_Global_Dia', 'Fecha, Por_Cobrar, Cartera_Vencida', f'{d60}'),
   ('Snap_Obra_Dia', 'Obra_ID, Cartera_Vencida', f'Último snapshot: {u}')], 'Líneas y barras'),
 ('07_Comercial', 'Comercial', 'Pipeline comercial: proformas abiertas, su monto en el tiempo y cuántas se aceptan o rechazan por semana.',
  [('Snap_Global_Dia', 'Proformas_Abiertas_N, Proformas_Abiertas, Obras_Por_Iniciar, Aceptadas_Dia, Rechazadas_Dia', f'Tarjetas: {HOY:%d/%m/%Y}. Gráficos: {d90}')], 'Línea y barras'),
 ('08_Alertas', 'Alertas', 'Estado de las alertas generadas por las reglas: cuántas siguen abiertas, qué reglas disparan más y cómo evoluciona por semana.',
  [('Alertas', 'Regla, Severidad, Estado, Fecha_Hora', f'{alert.Fecha_Hora.min():%d/%m/%Y} – {alert.Fecha_Hora.max():%d/%m/%Y}')], 'Barras apiladas / barras'),
]
import base64
uri = lambda n: 'data:image/png;base64,' + base64.b64encode(open(f'salida/{n}.png', 'rb').read()).decode()
sec = ''
for img, t, why, src, kind in V:
    rows = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in src)
    sec += f'''<section><img src="{uri(img)}" alt="{t}"><div><h2>{t}</h2><p>{why}</p>
<p class="k">Tipo de gráfico (AppSheet): {kind}</p>
<table><tr><th>Tabla (OXYData)</th><th>Columnas</th><th>Periodo / alcance</th></tr>{rows}</table></div></section>'''
html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OXY Dashboard - Simulación</title><style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;background:#f4f6f8;color:#22313f;margin:0;padding:16px}}
main{{max-width:1000px;margin:auto}} h1{{font-size:22px}} h2{{margin:0 0 6px;font-size:18px}}
section{{display:flex;gap:20px;background:#fff;border:1px solid #e1e5ea;border-radius:10px;padding:16px;margin:16px 0}}
img{{width:315px;flex:none;align-self:flex-start;border:1px solid #e1e5ea;border-radius:6px}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{border:1px solid #e1e5ea;padding:5px 8px;text-align:left;vertical-align:top}} th{{background:#eef2f6}}
.k{{color:#5b6b7a;font-size:13px}} @media(max-width:700px){{section{{flex-direction:column}} img{{width:100%}}}}
</style></head><body><main><h1>OXY Dashboard · Simulación de vistas</h1>
<p>Maqueta hecha con los datos reales de OXYData (corte al {HOY:%d/%m/%Y}). Muestra qué vería un usuario de Gestión en cada vista y de qué tabla sale cada gráfico. No es la app final: el aspecto definitivo lo da AppSheet.</p>
<p>Datos disponibles: Snap_Obra_Dia {rng(obra)} · Snap_Global_Dia {rng(dia)} · Snap_Global_Hora {rng(hora)} · Alertas {alert.Fecha_Hora.min():%d/%m/%Y} – {alert.Fecha_Hora.max():%d/%m/%Y}.</p>
{sec}</main></body></html>'''
open('OXY_Dashboard_Simulacion.html', 'w', encoding='utf-8').write(html)
print('OK', figs)
