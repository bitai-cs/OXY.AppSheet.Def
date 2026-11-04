# Tabla de contenido del directorio

## Carpeta simulacion-graficos
- Es una carpeta temporal donde reside el programa simulador de graficos. Esta carpeta se borrara en un futuro y solo debe ser leida por el agente IA cuando se le solicite hacerlo explicitamente.

## Archivo OXY_App_Proformas_Especificacion_vX.md
- Es la esoecificacion del aplicativo AppSheet "OXY Proformas".
- Plan: Core · Datos: OXYData (Google Sheet) · Zona horaria: America/Lima (UTC-5). Para quién es: quien construye la app en el editor de AppSheet. Cada propiedad se escribe en una línea, con el nombre que tiene en el editor nuevo de AppSheet. Documentos relacionados: OXY_AppSheet_Arquitectura_y_Seguridad (roles, seguridad, reparto entre apps), OXY_DataModel_Especificacion (significado de cada tabla y columna) y OXY_Propuesta_Dashboard_Indicadores

## Archivo OXY_AppSheet_Arquitectura_y_Seguridad_vX.md
- Es la arquitectura y seguridad general que aplica a todas las aplicaciones que se definiran en este directorio.
- Plan: Core · Datos: un solo Google Sheet, OXYData · Zona horaria de las apps y de los bots programados: America/Lima (UTC-5). Aplicaciones: OXY Master, OXY Proformas, OXY Gestión, OXY Campo y OXY Dashboard. Para quién es: quien diseña y construye las aplicaciones en el editor de AppSheet. Este documento fija lo que es común a las cinco: qué hace cada una, quién entra, qué tablas lleva, cómo se reparten los bots y cómo se prueba lo que cruza de una a otra. El detalle de cada aplicación (datos, vistas, acciones y automatizaciones) está en su propio documento.

## Archivo OXY_DataModel_Especificacion_vX.md
- Es la documentación del modelo de datos de las apps AppSheet (Google Sheets como persistencia). Corresponde al Google Sheet OXYData. Complementa a OXY_AppSheet_Acciones_y_Bots (acciones, bots, seguridad) y a OXY_Propuesta_Dashboard_Indicadores (indicadores).

## Archivo OXY_Propuesta_Dashboard_Indicadores_vX.md
- Como su nombre lo indica este archivo es la definicion de la propuesta de control diario e indicadores que se plasmaran en el aplicativo "OXY Dashboard"

## Archivo Pendientes_vX.md
- Archivo donde se registran las tareas pendientes a realizar para cerrar todas las definiciones que se estan haciendo.

## Archivo OXY_AppSheet_Acciones_y_Bots_v14.md
- Este es la ANTIGUA definicion de la solucion (aplicativos Appsheet) para OXY Industrial. Solo sirve como REFERENCIA para crear la nueva definicion de la solucion. Este archivo ya no se actualiza, es de solo lectura.

