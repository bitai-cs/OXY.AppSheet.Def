# simulacion-graficos
Simula las vistas de OXY Dashboard (estilo AppSheet, móvil) con los datos reales de OXYData.
- `exportar_oxydata.py OXYData.xlsx` -> copia a `datos/*.csv` las hojas Snap_*, Alertas, Metas_KPI, Jobs_Control, Obras, Clientes, Facturas_Obra (solo lectura).
- `generar_vistas.py` -> `salida/01..08_*.png`, `salida/00_Contacto_*.png` y `OXY_Dashboard_Simulacion.html` (página que describe cada gráfico, su propósito, tablas/columnas y periodo).
- Solo usa line/bar/stacked bar (tipos de AppSheet Chart view). Pie, heatmap y scatter quedan para Looker Studio (fase 2).
- Dependencias: `pip install -r requirements.txt`
