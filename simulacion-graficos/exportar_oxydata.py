"""Exporta a datos/*.csv las hojas que usara OXY Dashboard, desde un .xlsx descargado de OXYData.
Uso: python exportar_oxydata.py OXYData.xlsx   (solo lectura; nunca escribe en OXYData)"""
import sys, pandas as pd
HOJAS = ['Snap_Obra_Dia','Snap_Costo_Tipo_Semana','Snap_Global_Hora','Snap_Global_Dia',
         'Alertas','Metas_KPI','Jobs_Control','Obras','Clientes','Facturas_Obra']
x = pd.ExcelFile(sys.argv[1])
for h in HOJAS:
    df = x.parse(h).dropna(how='all').dropna(axis=1, how='all')
    df.to_csv(f'datos/{h}.csv', index=False); print(h, df.shape)
