# CONSTITUTION.md — Gestión de archivos de especificación (OXY AppSheet)

Este documento define las reglas para crear, nombrar y referenciar los archivos de especificación del proyecto OXY AppSheet. No describe el contenido funcional de la solución; describe cómo se gestionan los documentos. El control de versiones lo lleva Git: los nombres de archivo no tienen número de versión.

## 1. Propósito

Establecer un estándar único para que todos los documentos del directorio se creen, nombren y referencien de la misma forma, evitando citas desactualizadas y archivos huérfanos.

## 2. Archivos permitidos

Solo se pueden crear los siguientes tipos de archivo en la raíz del directorio (salvo las carpetas temporales `temp` y `simulacion-graficos`, que no forman parte de las especificaciones):

| Tipo de archivo | Nombre | Descripción |
|---|---|---|
| Arquitectura y seguridad | `OXY_AppSheet_Arquitectura_y_Seguridad.md` | Documento común a todas las apps: roles, seguridad, tablas por app, bots, traspasos, notificaciones. |
| Modelo de datos | `OXY_DataModel_Especificacion.md` | Base de datos central (`OXYData`): tablas, columnas, relaciones, reglas. |
| Propuesta de dashboard e indicadores | `OXY_Propuesta_Dashboard_Indicadores.md` | Indicadores, tablas de consolidación, jobs programados. |
| Especificación de app | `OXY_App_<Nombre>_Especificacion.md` | Detalle de una app: datos, vistas, acciones, automatizaciones. Una por app. |
| Acciones y bots (legado) | `OXY_AppSheet_Acciones_y_Bots_v14.md` | Definición antigua; solo referencia, no se actualiza. Es el único archivo que conserva su nombre con versión, por ser histórico. |
| Historial de cambios | `OXY_AppSheet_Historial_de_Cambios.md` | Historial único de todos los documentos. |
| Pendientes | `Pendientes.md` | Tareas pendientes y decisiones abiertas. |
| Componentes comunes | `OXY_AppSheet_Componentes_Comunes.md` | Convenciones, expresiones reutilizables, plantillas de ficha. |
| Leeme | `Leeme.md` | Índice del directorio y reglas de lectura. |
| Conexión a la fuente de datos | `OXYData_URL.txt` | Texto plano con la URL del Google Sheet `OXYData` (una sola línea). No es un documento de especificación. Es la referencia que usan las personas y los agentes IA para localizar la fuente oficial de datos. |
| Constitución | `CONSTITUTION.md` | Este documento. |

No se crean otros archivos de especificación fuera de esta lista. Si se necesita un nuevo tipo, se agrega primero aquí.

La URL de `OXYData` vive únicamente en `OXYData_URL.txt`; esta constitución no la repite.

## 3. Control de cambios

1. **Historial único.** Todos los cambios de todos los documentos se registran en `OXY_AppSheet_Historial_de_Cambios`. Ningún documento guarda su propio historial.
2. **Un cambio = una entrada.** Cada modificación significativa genera una entrada en el historial con: fecha, documento afectado y resumen del cambio.
3. **Respaldo previo.** Antes de cualquier cambio de estructura o carga masiva se copia `OXYData` con el nombre `OXYData_aaaammdd_hhmm`.
4. **Sin citas a versiones.** Los documentos no mencionan números de versión de otros archivos. Se citan por nombre (ej. `OXY_DataModel_Especificacion`).
5. **Fuente de datos.** Las referencias a datos se hacen a `OXYData`, que es la fuente oficial. La URL del Sheet está en `OXYData_URL.txt`.

## 4. Referencias permitidas

Un documento puede referenciar:

1. **Otros documentos por nombre.** Ejemplo: `OXY_AppSheet_Arquitectura_y_Seguridad`, `OXY_DataModel_Especificacion`, `OXY_Propuesta_Dashboard_Indicadores`.
2. **La fuente de datos.** `OXYData` (Google Sheet), por su nombre. Su URL está en `OXYData_URL.txt`; la constitución no la repite.
3. **Tablas y columnas del modelo de datos.** Por su nombre exacto del Sheet.
4. **Decisiones y validaciones.** Por su ID (`D01`, `V04`, `DA-03`, etc.), que son estables.
5. **Apps y roles.** Por su nombre exacto (`OXY Master`, `Super`, `Administracion`, etc.).
6. **La ubicación de la fuente de datos.** `OXYData_URL.txt`, por su nombre.

Un documento NO puede referenciar:

1. Números de versión de otros documentos (ej. `OXY_DataModel_Especificacion_v17`).
2. Rutas o nombres de archivos con versión.
3. Versiones de `OXYData` (ej. `OXYData_20261014_2206`), salvo en el historial de cambios o en pendientes operativos.

## 5. Reglas de creación de un documento nuevo

1. Verificar que el tipo de archivo esté en la lista de la sección 2. Si no está, agregarlo primero a esta constitución.
2. Usar el nombre exacto de la lista, sin sufijo de versión.
3. Incluir las secciones estándar definidas en `OXY_AppSheet_Arquitectura_y_Seguridad` (sección 2 de ese documento) cuando sea una especificación de app.
4. No incluir historial de cambios ni citas a versiones de otros archivos.
5. Citar a los demás documentos por nombre.
6. Registrar la creación en `OXY_AppSheet_Historial_de_Cambios`.

## 6. Reglas de actualización

1. Actualizar el contenido sin incluir números de versión.
2. Registrar el cambio en el historial.
3. Si el cambio afecta a otros documentos, actualizarlos también y registrar cada uno en el historial.
4. **Diccionario de estructura.** Todo cambio en `OXYData` que cree, renombre o elimine una tabla o columna se refleja en la pestaña `_Diccionario` de `OXYData` (columnas: Tabla, Columna, Tipo AppSheet, Clave, Requerido, Virtual). El `_Diccionario` registra solo la estructura; la configuración de cada columna (`Show?`, `Editable?`, valor inicial, `Valid if` y fórmulas) va en la especificación de la app.

## 7. Subcarpeta `simulacion-graficos`

1. Es temporal y se borrará en el futuro.
2. Solo se lee cuando se solicita explícitamente.
3. Sus archivos no son documentos de especificación.
4. Sus archivos internos (CSV, PNG, HTML, scripts) no siguen el patrón de nombres de especificación.

## 8. Carpeta `temp`

1. Es una carpeta de trabajo para archivos temporales del usuario o generados por un agente IA a solicitud del usuario.
2. **Ningún agente IA debe leer su contenido**, salvo que el usuario lo pida explícitamente.
3. Un agente IA solo puede crear o escribir archivos en ella cuando el usuario lo solicite.
4. Sus archivos no son documentos de especificación ni siguen el patrón de nombres.
5. Su contenido es descartable: puede borrarse en cualquier momento sin afectar la solución.
6. No se registra en `OXY_AppSheet_Historial_de_Cambios`.

## 9. Archivo `OXYData_URL.txt`

1. Es obligatorio para trabajar con `OXYData`: sin su URL no se puede abrir la fuente de datos.
2. Si el archivo no existe, el usuario lo crea antes de continuar con cualquier comando o petición.
3. Ningún agente IA lo crea por su cuenta; si falta, el agente IA detiene el trabajo y pide al usuario que lo cree.
