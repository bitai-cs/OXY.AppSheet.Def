# CONSTITUTION.md — Gestión de archivos de especificación (OXY AppSheet)

Este documento define las reglas para crear, nombrar, versionar y referenciar los archivos de especificación del proyecto OXY AppSheet. No describe el contenido funcional de la solución; describe cómo se gestionan los documentos.

## 1. Propósito

Establecer un estándar único para que todos los documentos del directorio se creen, nombren, versionen y referencien de la misma forma, evitando citas desactualizadas y archivos huérfanos.

## 2. Archivos permitidos

Solo se pueden crear los siguientes tipos de archivo en la raíz del directorio (salvo las carpetas temporales `temp` y `simulacion-graficos`, que no forman parte de las especificaciones):

| Tipo de archivo | Patrón de nombre | Descripción |
|---|---|---|
| Arquitectura y seguridad | `OXY_AppSheet_Arquitectura_y_Seguridad_vX.md` | Documento común a todas las apps: roles, seguridad, tablas por app, bots, traspasos, notificaciones. |
| Modelo de datos | `OXY_DataModel_Especificacion_vX.md` | Base de datos central (`OXYData`): tablas, columnas, relaciones, reglas. |
| Propuesta de dashboard e indicadores | `OXY_Propuesta_Dashboard_Indicadores_vX.md` | Indicadores, tablas de consolidación, jobs programados. |
| Especificación de app | `OXY_App_<Nombre>_Especificacion_vX.md` | Detalle de una app: datos, vistas, acciones, automatizaciones. Una por app. |
| Acciones y bots (legado) | `OXY_AppSheet_Acciones_y_Bots_vX.md` | Definición antigua; solo referencia, no se actualiza. |
| Historial de cambios | `OXY_AppSheet_Historial_de_Cambios_vX.md` | Historial único de todos los documentos. |
| Pendientes | `Pendientes_vX.md` | Tareas pendientes y decisiones abiertas. |
| Componentes comunes | `OXY_AppSheet_Componentes_Comunes_vX.md` | Convenciones, expresiones reutilizables, plantillas de ficha. |
| Leeme | `Leeme_vX.md` | Índice del directorio y reglas de lectura. |
| Conexión a la fuente de datos | `OXYData_URL.txt` | Texto plano con la URL del Google Sheet `OXYData` (una sola línea). No es un documento de especificación: no se versiona. Es la referencia que usan las personas y los agentes IA para localizar la fuente oficial de datos. |
| Constitución | `CONSTITUTION.md` | Este documento (sin versión). |

No se crean otros archivos de especificación fuera de esta lista. Si se necesita un nuevo tipo, se agrega primero aquí.

La URL de `OXYData` vive únicamente en `OXYData_URL.txt`; esta constitución no la repite.

## 3. Numeración de versiones

1. El número de versión va al final del nombre, con el formato `_vN` (N entero, sin ceros a la izquierda).
2. Cada vez que se guarda un cambio en un documento, su número de versión sube en uno.
3. El número de versión nunca se menciona dentro del contenido del documento. El documento describe solo lo vigente.
4. El historial de cambios es el único lugar donde se registran las versiones y qué cambió en cada una.
5. Un documento nuevo empieza en `_v1`.

## 4. Control de cambios

1. **Historial único.** Todos los cambios de todos los documentos se registran en `OXY_AppSheet_Historial_de_Cambios`. Ningún documento guarda su propio historial.
2. **Un cambio = una entrada.** Cada modificación significativa genera una entrada en el historial con: fecha, documento afectado, versión anterior, versión nueva, descripción del cambio.
3. **Respaldo previo.** Antes de cualquier cambio de estructura o carga masiva se copia `OXYData` con el nombre `OXYData_aaaammdd_hhmm`.
4. **Versiones anteriores.** Las versiones viejas de los documentos se mueven a la carpeta `deprecated`. No se borran; no se leen ni se tocan salvo para consulta.
5. **Sin citas a versiones.** Los documentos no mencionan números de versión de otros archivos. Se citan por nombre sin versión (ej. `OXY_DataModel_Especificacion`).
6. **Fuente de datos.** Las referencias a datos se hacen a `OXYData`, que es la fuente oficial. No se cita por versión. La URL del Sheet está en `OXYData_URL.txt`.

## 5. Referencias permitidas

Un documento puede referenciar:

1. **Otros documentos por nombre, sin versión.** Ejemplo: `OXY_AppSheet_Arquitectura_y_Seguridad`, `OXY_DataModel_Especificacion`, `OXY_Propuesta_Dashboard_Indicadores`.
2. **La fuente de datos.** `OXYData` (Google Sheet), por su nombre, sin versión. Su URL está en `OXYData_URL.txt`; la constitución no la repite.
3. **Tablas y columnas del modelo de datos.** Por su nombre exacto del Sheet.
4. **Decisiones y validaciones.** Por su ID (`D01`, `V04`, `DA-03`, etc.), que son estables entre versiones.
5. **Apps y roles.** Por su nombre exacto (`OXY Master`, `Super`, `Administracion`, etc.).
6. **La ubicación de la fuente de datos.** `OXYData_URL.txt`, por su nombre.

Un documento NO puede referenciar:

1. Números de versión de otros documentos (ej. `OXY_DataModel_Especificacion_v17`).
2. Rutas o nombres de archivos con versión.
3. Versiones de `OXYData` (ej. `OXYData_20261014_2206`), salvo en el historial de cambios o en pendientes operativos.

## 6. Reglas de creación de un documento nuevo

1. Verificar que el tipo de archivo esté en la lista de la sección 2. Si no está, agregarlo primero a esta constitución.
2. Usar el patrón de nombre exacto, con `_v1` como versión inicial.
3. Incluir las secciones estándar definidas en `OXY_AppSheet_Arquitectura_y_Seguridad` (sección 2 de ese documento) cuando sea una especificación de app.
4. No incluir historial de cambios ni citas a versiones de otros archivos.
5. Citar a los demás documentos por nombre, sin versión.
6. Registrar la creación en `OXY_AppSheet_Historial_de_Cambios`.

## 7. Reglas de actualización

1. Subir la versión en uno.
2. Actualizar el contenido sin mencionar la versión dentro del texto.
3. Registrar el cambio en el historial.
4. Si el cambio afecta a otros documentos, actualizarlos también y registrar cada uno en el historial.
5. **Diccionario de estructura.** Todo cambio en `OXYData` que cree, renombre o elimine una tabla o columna se refleja en la pestaña `_Diccionario` de `OXYData` (columnas: Tabla, Columna, Tipo AppSheet, Clave, Requerido, Virtual). El `_Diccionario` registra solo la estructura; la configuración de cada columna (`Show?`, `Editable?`, valor inicial, `Valid if` y fórmulas) va en la especificación de la app.

## 8. Subcarpeta `simulacion-graficos`

1. Es temporal y se borrará en el futuro.
2. Solo se lee cuando se solicita explícitamente.
3. No se versiona como documento de especificación.
4. Sus archivos internos (CSV, PNG, HTML, scripts) no siguen el patrón de nombres de especificación.

## 9. Carpeta `deprecated`

1. Contiene versiones anteriores de los documentos.
2. No se leen ni se tocan en el trabajo normal.
3. Sirve solo como archivo histórico.
4. Los archivos que se pasan ahí conservan su nombre original con versión.

## 10. Carpeta `temp`

1. Es una carpeta de trabajo para archivos temporales del usuario o generados por un agente IA a solicitud del usuario.
2. **Ningún agente IA debe leer su contenido**, salvo que el usuario lo pida explícitamente.
3. Un agente IA solo puede crear o escribir archivos en ella cuando el usuario lo solicite.
4. No se versiona como documento de especificación ni sigue el patrón de nombres.
5. Su contenido es descartable: puede borrarse en cualquier momento sin afectar la solución.
6. No se registra en `OXY_AppSheet_Historial_de_Cambios`.

## 11. Archivo `OXYData_URL.txt`

1. Es obligatorio para trabajar con `OXYData`: sin su URL no se puede abrir la fuente de datos.
2. Si el archivo no existe, el usuario lo crea antes de continuar con cualquier comando o petición.
3. Ningún agente IA lo crea por su cuenta; si falta, el agente IA detiene el trabajo y pide al usuario que lo cree.