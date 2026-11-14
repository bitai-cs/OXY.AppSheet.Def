# OXY Industrial S.R.L. — Historial de cambios de los documentos de AppSheet

Este documento es el único lugar donde se registran los cambios de los documentos de AppSheet: el instructivo `OXY_AppSheet_Acciones_y_Bots` (hasta su reemplazo), la arquitectura y la especificación de cada app. Los demás documentos no llevan historial ni mencionan versiones anteriores: solo describen lo vigente. Cada entrada nueva se agrega **arriba**.

---

## El repositorio pasa a control de versiones con Git — 13 de noviembre de 2026

**Motivo:** los nombres de archivo ya no llevan número de versión; Git guarda el historial de cada archivo. La carpeta de versiones anteriores se elimina del repositorio y el historial sigue siendo la única fuente de resumen de cambios.

| Dónde | Cambio |
|---|---|
| `CONSTITUTION.md` | Se elimina la numeración de versiones y la carpeta de versiones anteriores; los nombres de archivo no llevan sufijo de versión |
| Documentos de especificación | Se les quitó el sufijo de versión al nombre: arquitectura y seguridad, modelo de datos, dashboard e indicadores, proforma, pendientes y este historial |
| `OXY_AppSheet_Acciones_y_Bots` | No cambia; es el instructivo histórico de solo referencia y conserva su nombre |
| Carpeta de versiones anteriores | Eliminada del repositorio |

---

## Aplicación en `OXYData` de la copia de planificación y conceptos — 14 de noviembre de 2026

**Motivo:** la entrada del 12 de noviembre de 2026 registró el cambio de estructura de `OXYData` (`Control_Copias` y `Proformas.Copiar_Desde_ID`) pero el Sheet no lo tenía; solo estaban actualizados los documentos. Se aplicó y verificó.

| Dónde | Cambio |
|---|---|
| `OXYData` · respaldo previo | Copia `OXYData_20261114_0239` en la carpeta de respaldos |
| `OXYData` · `Control_Copias` | Pestaña nueva con `Control_ID`, `Proforma_Destino_ID`, `Proforma_Origen_ID`, `Estado`, `Creado_En` y la fila `COPIAS` con `Estado = "Libre"` |
| `OXYData` · `Proformas` | Columna `Copiar_Desde_ID` agregada al final (columna Y), vacía |
| `OXYData` · `_Diccionario` | 6 filas nuevas: 5 de `Control_Copias` y `Proformas.Copiar_Desde_ID` (después de `Doc_Proforma_Personalizado`) |
| Este historial | Entrada nueva |

---

## Copia de planificación y conceptos de proforma — 12 de noviembre de 2026

**Motivo:** agregar la acción "Copiar planificación y conceptos" a OXY Proformas, que copie líneas de `Proforma_Conceptos` y `Proforma_Planificacion` desde una proforma origen hacia la proforma que ejecuta la acción.

| Dónde | Cambio |
|---|---|
| `OXY_App_Proformas_Especificacion`, 1.3 | Nota de que la copia de conceptos y planificación es independiente de la relación previa (`Proforma_Previa_ID` / `Tipo_Relacion`) |
| `OXY_App_Proformas_Especificacion`, 3.1 | Tabla `Control_Copias` con permisos L·I·A |
| `OXY_App_Proformas_Especificacion`, 3.2 | Paso 5: crear la fila `COPIAS` de `Control_Copias` con `Estado = "Libre"` |
| `OXY_App_Proformas_Especificacion`, 3.3 | Columna `Copiar_Desde_ID` en `Proformas`; columnas de `Control_Copias`; acciones auxiliares de copia |
| `OXY_App_Proformas_Especificacion`, 3.4 | Slice `S_Control_Copias_En_Proceso` |
| `OXY_App_Proformas_Especificacion`, 3.5 | Acciones de sistema de `Control_Copias` |
| `OXY_App_Proformas_Especificacion`, 5 | Acciones PRO-A13 a PRO-A17; bot PRO-B05 |
| `OXY_App_Proformas_Especificacion`, 10 | Pruebas PR-18 a PR-21 |
| `OXY_App_Proformas_Especificacion`, 12 | Pendientes P-03, P-04, P-05 decididos (agregar, solo Borrador, conserva Orden) |
| `OXY_DataModel_Especificacion` | Tabla `Control_Copias` en mapa de tablas y sección 8; columna `Copiar_Desde_ID` en `Proformas`; nota de copia en `Proformas`, `Proforma_Conceptos` y `Proforma_Planificacion`; `_Diccionario` actualizado (solo estructura) |
| `OXY_AppSheet_Arquitectura_y_Seguridad`, 1 | Se remueve la fila de `OXY_AppSheet_Componentes_Comunes` |
| `OXY_AppSheet_Arquitectura_y_Seguridad`, 6 | `Control_Copias` en matriz de tablas por app (solo Proformas, L·I·A) |
| `OXY_AppSheet_Arquitectura_y_Seguridad`, 7.2 | Grupo de componentes de copia (PRO-A13 a PRO-A17, PRO-B05) en Proformas |
| `OXY_AppSheet_Arquitectura_y_Seguridad`, 11 | DA-10: tabla de control de una fila + bot con dos pasos "Execute an action on a set of rows"; solo en Borrador, agrega líneas, conserva Orden |
| `Pendientes` | 4.14: pendiente de copia de planificación y conceptos |
| `OXYData` · `_Diccionario` | Respaldo previo. Filas de `Control_Copias` (5 columnas) y `Proformas.Copiar_Desde_ID` (1 columna) |
| Este historial | Entrada nueva |

---

## Reglas de `_Diccionario` y de `OXYData_URL.txt` en la constitución — 12 de noviembre de 2026

**Motivo:** la constitución no decía que todo cambio de estructura debe reflejarse en `_Diccionario`, ni dónde vive la URL de `OXYData`, ni qué hacer cuando ese archivo no existe.

| Dónde | Cambio |
|---|---|
| `CONSTITUTION.md`, 2 | Nuevo tipo de archivo `OXYData_URL.txt` y nota de que la URL no se repite en la constitución |
| `CONSTITUTION.md`, 3.5, 4.2 y 4.6 | La URL de `OXYData` está en `OXYData_URL.txt` |
| `CONSTITUTION.md`, 6.4 | Nueva regla: todo cambio que cree, renombre o elimine una tabla o columna se refleja en `_Diccionario` (solo estructura); la configuración de columnas va en la especificación de la app |
| `CONSTITUTION.md`, 9 | Nueva sección: si `OXYData_URL.txt` no existe, el usuario lo crea antes de continuar con cualquier comando o petición |
| Este historial | Entrada nueva |

---

## Códigos de permisos de las tablas — 18 de octubre de 2026

**Cambio:** los códigos pasan de L·A·U·D a **L** lectura, **I** inserción (*Adds*), **A** actualización (*Updates*) y **E** eliminación (*Deletes*). Equivalencia: antes A → ahora I; antes U → ahora A; antes D → ahora E.

| Dónde | Cambio |
|---|---|
| `OXY_App_Proformas_Especificacion` (v10), 3.1 | Leyenda y tabla de permisos (por ejemplo `Proformas` L·A·U pasa a L·I·A; `Proforma_Conceptos` L·A·U·D pasa a L·I·A·E; `Obras` L·A pasa a L·I) |
| `OXY_AppSheet_Arquitectura_y_Seguridad`, 5.2 | Leyenda, matriz de tablas por app, nota 9 y las decisiones DA-02, DA-04 y DA-09 |
| Este historial | La entrada de DA-02 usa el código nuevo |
| Sin cambio | Los nombres de AppSheet en inglés (*Adds*, *Updates*, *Deletes*, *Delete row*, *Data change type*) se conservan porque son los rótulos del editor. Modelo de datos, dashboard y pendientes no usan estos códigos |

---

## `Require?` por ciclo de vida en OXY Proformas — 18 de octubre de 2026

**Motivo:** la sección 3.3 solo indicaba `Require?` en 12 columnas, y AppSheet decide por su cuenta al agregar la tabla (en `Obras` marcaba como requeridas fechas que no lo son). Se definió para todas las columnas reales según el ciclo de vida de cada tabla.

| Dónde | Cambio |
|---|---|
| `OXY_App_Proformas_Especificacion`, 3.3 | Criterio de `Require?` al inicio de 3.3 y la línea `Require?` en las 71 columnas reales de `Proformas`, `Proforma_Conceptos`, `Proforma_Planificacion`, `Obras`, `Clientes` y `Contactos_Cliente`; fichas nuevas para las columnas de `Clientes` y `Contactos_Cliente` que no tenían. Orden de las propiedades como en el editor: `Show?`, `Editable?`, `Require?`, valor inicial, `Valid if` |
| Fórmulas (*Required If*) | `Fecha_Envio` desde `Enviada`; `Fecha_Aceptacion` y `Doc_Aceptacion` en `Aceptada`; `Motivo_Rechazo` y `Fecha_Rechazo` en `Rechazada`; `Motivo_Anulacion` y `Fecha_Anulacion` en `Anulada`; `Eliminada_Por` y `Fecha_Eliminacion` en `Z-Eliminada`; `Tipo_Relacion` con `ISNOTBLANK([Proforma_Previa_ID])` (ya existía). En `Enviada` no se exige ningún dato de salida: aceptar, rechazar y anular son excluyentes y lo exigen los `Only if` de las acciones |
| `OXYData` · `_Diccionario` | Respaldo previo `OXYData_20261018_0407`. `Requerido` = `Condicional` en esas nueve columnas |
| `OXY_DataModel_Especificacion` | `Req.` = `Condicional` en las mismas nueve columnas |
| Sin cambio | Arquitectura, dashboard y pendientes. Las próximas especificaciones de app llevarán `Require?` en cada ficha con este criterio |

---

## OXY Proformas: configuración de las columnas de `Obras` — 18 de octubre de 2026

**Motivo:** la sección 3.3 mezclaba la configuración de la tabla (*Adds* sin *Updates*, que va en 3.1) con la de las columnas. Al agregar `Obras` en AppSheet, el editor adivina tipos, marca `Require?` y pone `TODAY()` como valor inicial en las fechas.

| Dónde | Cambio |
|---|---|
| `OXY_App_Proformas_Especificacion`, 3.3 `Obras`, campo por campo con el mismo formato que `Proformas` | Se quitó la frase "solo lectura". Las doce columnas que escribe `A_Aceptar_CrearObra` llevan `Editable?` = `CONTEXT("ViewType") = "Never"` y su tipo (Ref a `Proformas`, `Obras` y `Clientes` donde corresponde). Las ocho que escribe OXY Gestión quedan opcionales y sin valor inicial; `Responsable_ID` ya no remite a una corrección pendiente en `OXYData` (hecha) |
| 3.2 | El paso 3 recuerda corregir los tipos y las propiedades de `Obras` tras agregar la tabla |
| Sin cambio | Modelo de datos, arquitectura, `OXYData` y demás documentos: no cambia ninguna estructura ni regla |

---

## Nuevo `_Diccionario` solo con la estructura — 18 de octubre de 2026

**Motivo:** la misma columna se describía en tres lugares (modelo de datos, `_Diccionario` y especificación de cada app). Cada tipo de información queda en una sola fuente: el significado en el modelo de datos, la configuración de columnas en la especificación de cada app y la estructura en `_Diccionario`.

| Dónde | Cambio |
|---|---|
| `OXYData` | Respaldo previo: `OXYData_20261018_0146`. La pestaña `_Diccionario` anterior pasa a `_Diccionario_Legado` (solo consulta mientras se terminan las especificaciones). Nuevo `_Diccionario` con seis columnas: Tabla, Columna, Tipo AppSheet, Clave, Requerido y Virtual (419 columnas, las mismas de antes) |
| `OXYData` · `_Leeme` | Puntos 3, 4 y 10 reescritos. Corregido un error mío del cambio anterior: el punto 1 había quedado reemplazado por el texto del punto 4; ya está restaurado |
| `OXY_DataModel_Especificacion` | Convenciones: describen el nuevo `_Diccionario` y remiten a las especificaciones de app para la configuración |
| `OXY_App_Proformas_Especificacion` | Las fórmulas de las virtuales ya no se dicen "iguales a las de `_Diccionario`": esta especificación es la única fuente |
| `Pendientes` | 4.2 corregido; 4.13 nuevo con la limpieza del modelo de datos, la migración de roles y apps y el borrado de `_Diccionario_Legado` |
| Sin cambio | Instructivo `OXY_AppSheet_Acciones_y_Bots` (obsoleto, solo referencia) |

---

## OXY Proformas: PDF, documento personalizado y líneas nuevas en `Enviada` (cambio integral) — 18 de octubre de 2026

**Motivo:** el cliente puede pedir ajustes después del envío. Mientras la proforma está `Enviada` se puede corregir, agregar líneas, regenerar el PDF y volver a subir el documento personalizado. Desde `Aceptada` todo queda bloqueado. Se aplicó en todos los documentos y en `OXYData` a la vez (respaldo previo: `OXYData_20261018_0124`).

| Dónde | Cambio |
|---|---|
| `OXY_App_Proformas_Especificacion` | `A_Generar_PDF`: `Only if` con `Borrador` o `Enviada`, y sus pruebas y notas de falla. `Doc_Proforma_Personalizado`: `Show?` y `Editable?` con `Borrador` o `Enviada`. Mensaje de `A_Enviar` sin la frase de que el PDF no se regenera. Regla 7 de 1.4 y nota de *Add* de líneas. `V_Control_PDF`. PR-9 y PR-16 ajustadas, PR-17 nueva, V29 nueva. Pendientes P-01 a P-03 y P-05 a P-08 cerrados; quedan P-01 (roles antiguos) y P-02 (¿`A_Iniciar` exige responsable?) |
| `OXYData` · `_Diccionario` | Las diez columnas de líneas con `Editable / If` = `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`; `Doc_Proforma` y `Doc_Proforma_Personalizado` (Show, Editable y notas); `Proforma_ID` con valor inicial `"PRF-"&UNIQUEID()`; `Motivo_Rechazo` sin `Reemplazada`; `Obras.Responsable_ID` no requerido; notas de `Snap_Global_Dia.Proformas_Abiertas_N` y `Proformas_Abiertas` |
| `OXYData` · `_Reglas` y `_Leeme` | Regla *Enviar* reescrita; punto 4 de `_Leeme` sin número de versión |
| `OXY_DataModel_Especificacion` | `Doc_Proforma`, `Doc_Proforma_Personalizado` (la fila estaba por error en `Proveedores`; se movió a `Proformas`), `Obras.Responsable_ID` no requerido, notas de las líneas y de los indicadores de proformas abiertas |
| `OXY_Propuesta_Dashboard_Indicadores` | `Proformas_Abiertas_N` y `Proformas_Abiertas` se leen en vivo de las `Enviada` y pueden cambiar; los días pasados no se recalculan |
| `OXY_AppSheet_Arquitectura_y_Seguridad` | V27 reformulada; V29 nueva |
| `Pendientes` | 4.10: una `Enviada` sí se regenera con `A_Generar_PDF` |
| Sin cambio | El instructivo `OXY_AppSheet_Acciones_y_Bots` está obsoleto y no se actualiza. La migración de roles y de las tres a cinco apps en `OXYData` y en el modelo de datos sigue pendiente aparte |

---

## OXY Proformas: líneas editables en `Enviada` — 18 de octubre de 2026

**Motivo:** permitir cambios mínimos en conceptos y planificación cuando el cliente los pide después del envío.

| Tema | Cambio |
|---|---|
| `Proforma_Conceptos` | `Orden`, `Concepto` y `Monto_Sin_IGV`: `Editable?` pasa a `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))` |
| `Proforma_Planificacion` | `Tipo_Costo_ID`, `Descripcion`, `Cantidad`, `Unidad`, `Costo_Unitario`, `Tiene_IGV` y `Es_Credito_Fiscal`: igual |
| Sin cambio | Borrar líneas sigue solo en `Borrador`; `Doc_Proforma_Personalizado` sigue editable solo en `Borrador` |
| `A_Enviar` | El mensaje de confirmación ya no dice que el detalle no se podrá editar; avisa que el PDF no se vuelve a generar |
| Pruebas y validaciones | PR-9 reformulada, PR-16 nueva, V27 ampliada |
| Pendientes nuevos | P-05 a P-08: PDF desactualizado, indicadores, alta de líneas en `Enviada` y `_Diccionario` |

---

## OXY Proformas: `Editable?` de los campos que escriben solo acciones y bots — 18 de octubre de 2026

**Cambio:** en la tabla `Proformas` (sección 3.3), `Editable?` pasa de `FALSE` a `CONTEXT("ViewType") = "Never"` en los siete campos que escriben exclusivamente acciones o bots: `Estado`, `Fecha_Envio`, `Fecha_Rechazo`, `Fecha_Anulacion`, `Eliminada_Por`, `Fecha_Eliminacion` y `Doc_Proforma`. Los campos que se llenan solo con su valor inicial (`Proforma_ID`, `Creado_Por`, `Creado_En`) conservan `FALSE`.

---

## Respuestas a los pendientes de OXY Proformas — 17 de octubre de 2026

| Decisión | Resultado | Cambio en los documentos |
|---|---|---|
| Aviso de obra sin responsable | `OBRA_CREADA` envía correo a `Operaciones` y `Supervisor`, además del push a `Administracion` y `Supervisor` | `OBR-B01` con paso de correo; notificaciones 7 de la app y 9.1 y 9.2 de la arquitectura |
| Corregir líneas de un `Borrador` | Se pueden borrar conceptos y líneas de planificación mientras la proforma es `Borrador` | Permisos **D** en las dos tablas; acción de sistema *Delete* con condición de estado; prueba PR-15; validación V27 ampliada |

---

## OXY Proformas: especificación de la app — 17 de octubre de 2026

**Motivo:** primer documento de app (piloto) del nuevo esquema de cinco apps. Reemplaza, para proformas, la sección 5 del instructivo de acciones y bots.

| Tema | Cambio |
|---|---|
| Documento nuevo | `OXY_App_Proformas_Especificacion` con las 12 secciones de la plantilla: 12 acciones (`PRO-A01` a `PRO-A12`), 5 bots (`PRO-B01` a `PRO-B04` y `OBR-B01`), 6 vistas de menú, matriz acción × rol y pruebas PR-1 a PR-14 |
| Roles | `Admin` y `Gerencia` se reemplazan por la expresión de rol de la app (`Super`, `Administracion`, `Supervisor`, `Planificacion`) |
| Responsable de la obra | `A_Aceptar_CrearObra` ya no llena `Responsable_ID`; el aviso `OBRA_CREADA` va solo por push a `Administracion` y `Supervisor` |
| Clientes y contactos | Altas desde la app; sin ediciones ni borrados |
| Filtros nuevos | `Cliente_ID` y `Tipo_Costo_ID` ofrecen solo registros con `Activo = Si` |
| Estado inexistente | Se quita `Reemplazada` de la visibilidad de `Motivo_Rechazo` |
| Arquitectura | Regla 6 de 5.3 (acciones auxiliares sin condición de rol); `OBRA_CREADA` sin responsable; validaciones V26 a V28 |
| Pendientes | P-01 a P-06 del documento de la app (aviso para asignar responsable, `Responsable_ID` requerido en `OXYData`, borrar líneas de un borrador, correcciones al diccionario) |

---

## Decisiones DA-08 y DA-09 — 17 de octubre de 2026

| Decisión | Resultado | Cambio en el documento |
|---|---|---|
| DA-08 | `Obras.Responsable_ID` queda en blanco al crear la obra | Pasa a decisión tomada; falta definir en OXY Gestión si `A_Iniciar` lo exige |
| DA-09 | `Trabajadores` se da de baja con `Activo = No`; `Compania` y `Configuracion` no se borran | `Trabajadores` y `Configuracion` sin **D** en la matriz |
| V18 | Un bot reacciona solo a los cambios hechos desde su app | Registrada como confirmada por el propietario, a verificar en la primera prueba |

---

## Decisiones de arquitectura DA-01 a DA-07 — 17 de octubre de 2026

**Motivo:** cerrar las decisiones abiertas del documento de arquitectura y seguridad.

| Decisión | Resultado | Cambio en el documento |
|---|---|---|
| DA-01 | Sin restricción de dispositivo; cada usuario decide cómo visualiza cada app | Columna "Uso previsto"; Master y Proformas pasan a "Escritorio o celular" |
| DA-02 | OXY Proformas puede dar de alta clientes y contactos, sin ediciones ni borrados | `Clientes` y `Contactos_Cliente` en L·I en OXY Proformas |
| DA-03 | El responsable de la obra lo asigna cualquier usuario con rol de OXY Gestión | `Obras.Responsable_ID` queda en blanco al crear la obra desde la aceptación; T1 actualizado |
| DA-04 | OXY Master puede borrar filas | Nuevo código **D** en la matriz de tablas; `Compania` sin borrado |
| DA-05 | `Proforma_Planificacion` en lectura en OXY Campo | Matriz y riesgos (la planificación de costos queda visible en Campo) |
| DA-06 | `Administracion` y `Supervisor` se agregan a la lista de usuarios de OXY Campo solo para push | Matriz rol × app con "avisos"; pasos de alta y pruebas; notificaciones 9.2 |
| DA-07 | Los jobs de indicadores viven en OXY Gestión | Sin cambio de contenido; pasa a decisión tomada |

**Nuevo:** decisiones abiertas DA-08 (responsable al iniciar la obra) y DA-09 (protección contra borrado de filas referenciadas); validación V25 (columnas *Ref* con tabla destino ausente).

---

## Arquitectura de 5 apps — 17 de octubre de 2026

**Motivo:** pasar de tres aplicaciones (`OXY Gestión`, `OXY Campo`, `OXY Dashboard`) a cinco (`OXY Master`, `OXY Proformas`, `OXY Gestión`, `OXY Campo`, `OXY Dashboard`), con un documento de especificación por app y una seguridad simple por inicio de sesión y por rol en las acciones.

### Estructura de los documentos

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Instructivo `OXY_AppSheet_Acciones_y_Bots` | Un solo documento con todas las acciones, bots, columnas y seguridad de las tres apps | Queda reemplazado por un documento por app: `OXY_App_Master_Especificacion`, `OXY_App_Proformas_Especificacion`, `OXY_App_Gestion_Especificacion`, `OXY_App_Campo_Especificacion` y `OXY_App_Dashboard_Especificacion` | Cada app se construye en el editor por separado (datos, vistas, acciones y automatizaciones) |
| Contenido común | Dentro del instructivo (secciones 0.5, 1, 2, 14, 15 y 17) | Documentos `OXY_AppSheet_Arquitectura_y_Seguridad` y `OXY_AppSheet_Componentes_Comunes` | Evitar repetir en cinco documentos lo que es común |
| `OXY_DataModel_Especificacion` | Vigente | Sigue vigente: es la especificación de la base de datos central `OXYData` | Sin cambio de papel |
| `OXY_Propuesta_Dashboard_Indicadores` | Vigente | Sigue vigente como propuesta al cliente y base de la especificación de OXY Dashboard | Sin cambio de papel |

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Aplicaciones | Tres: Gestión, Campo y Dashboard | Cinco: Master, Proformas, Gestión, Campo y Dashboard | Separar maestras, ciclo de la proforma y operación de la obra |
| Roles | `Admin`, `Gerencia` y `Campo` en las fórmulas; `Administracion`, `Gerencia` y `Campo` en los datos | Seis: `Super`, `Administracion`, `Supervisor`, `Planificacion`, `Operaciones` y `Campo` | Un rol por persona, uno o varios roles por app |
| Equivalencia de roles | — | `Admin` (valor `Administracion` en los datos) pasa a `Supervisor`; `Gerencia` pasa a `Administracion`; `Comercial` pasa a `Planificacion`; `Super` y `Operaciones` son nuevos | Nombres definitivos de los roles |
| Seguridad de datos | Filtros de seguridad por tabla con rol, obras asignadas y dueño del registro | Solo la lista de usuarios de cada app y las tablas que lleva cada app. El filtro de seguridad por tabla queda diferido | Simplificar la primera versión; ver `Pendientes` |
| Reglas por rol en columnas | `Show?` y `Editable?` con el rol del usuario | No se usan; la diferencia entre audiencias se resuelve con las tablas y columnas de cada app | Simplificar la primera versión |
| Expresión de rol de las acciones | Dos expresiones reutilizables (Gestión y Gerencia) | Una expresión completa en cada acción, con `Activo` y la lista de roles de la app | La expresión debe ser segura y cada acción se lee sin consultar otra sección |
| Roles por acción | `Cerrar con saldo` solo de Gerencia; excepción de Gerencia al tope de facturación | Todas las acciones admiten todos los roles de su app; `Cerrar con saldo` queda abierto a todos los roles de OXY Gestión; el tope de facturación aplica a todos | Decisiones de esta versión; se podrán restringir quitando roles de la lista de cada acción |
| Quién puede abrir OXY Dashboard | Los usuarios de Gestión | `Super` y `Administracion` | Decisión del dueño |
| Quién edita los roles | No definido | Cualquier usuario de OXY Master con acceso a las acciones de `Trabajadores` | Decisión del dueño |
| Creación de la obra | Acción de OXY Gestión | Acción de OXY Proformas, con `Obras` en altas y lectura; el bot `B_Log_Obra_Creada` vive en OXY Proformas | La obra nace al aceptar la proforma |
| Destinatarios de avisos | "Gestión" (Admin y Gerencia) y "Gerencia" | Por rol (ver el documento de arquitectura): `Administracion` y `Supervisor` en general; `Planificacion` en proformas; `Operaciones` en estado y atraso de obras; `Super` nunca | Los nuevos roles |

### Decisiones cerradas

| ID | Decisión | Resultado |
|---|---|---|
| D02 | ¿Los precios y el presupuesto de costo de las obras llegan al teléfono de Campo? | Sí, y en esta versión de todas las obras. Riesgo aceptado |
| D03 | ¿Quién ejecuta *Cerrar con saldo*? | Todos los roles de OXY Gestión |
| D07 | ¿Las cuentas bancarias de `Compania` llegan al teléfono de Campo? | Sí. Riesgo aceptado |

### Datos y documentos por actualizar

| Elemento | Qué falta |
|---|---|
| `OXYData` · `_Listas.Roles` y `Trabajadores` | Los seis roles; migrar primero los valores `Administracion` a `Supervisor` y después los `Gerencia` a `Administracion`, para no mezclarlos |
| `OXYData` · `_Diccionario` | Quitar o reemplazar las fórmulas con `LIST("Admin","Gerencia")` en `Show if`, `Editable`, `Valid if` y valores iniciales |
| `OXYData` · `_Reglas` y `_Leeme` | Apps, Dashboard, Seguridad y versión del modelo |
| `OXY_DataModel_Especificacion` | Columna de apps del mapa de tablas, descripción de `Rol` y textos "solo Gestión" |
| `OXY_Propuesta_Dashboard_Indicadores` | Tercera app, usuarios y roles de OXY Dashboard |
| Documentos de las cinco apps y `OXY_AppSheet_Componentes_Comunes` | Redactarlos. Hasta entonces el instructivo sigue siendo la única fuente de las fichas |
| Instructivo | Sus fichas pasan a las especificaciones de cada app; el instructivo queda como referencia histórica |

---

## Instructivo: aceptación y rechazo visibles tras el cambio de estado — 17 de octubre de 2026

**Motivo:** que los datos de aceptación y el motivo de rechazo sigan visibles una vez que la proforma cambia de estado.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| `Proformas.Fecha_Aceptacion` (*Show?*) | `[Estado]="Enviada"` | `IN([Estado],LIST("Enviada","Aceptada"))` | Se ve también en `Aceptada` |
| `Proformas.Doc_Aceptacion` (*Show?*) | `[Estado]="Enviada"` | `IN([Estado],LIST("Enviada","Aceptada"))` | Se ve también en `Aceptada` |
| `Proformas.Motivo_Rechazo` (*Show?*) | `[Estado]="Enviada"` | `IN([Estado],LIST("Enviada","Rechazada","Reemplazada"))` | Se ve en `Rechazada`; `Reemplazada` aún no existe como estado |

*Editable?* no cambia: las tres columnas siguen editables solo en `Enviada`.

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| Sección 5.1, columnas de `Proformas` | *Show?* de las tres columnas |

### Datos (`OXYData`)

La columna `Show if` de `_Diccionario` se actualizó para las tres filas. Ese mismo día se copió la columna `Valores Enum / Notas`, con las fórmulas de visualización, a `Show if` y se eliminó la columna sobrante, y se puso `CONTEXT("ViewType") = "Never"` en `Editable` para los campos que solo cambian bots y acciones. Copias de seguridad: `OXYData_20261017_1241` y `OXYData_20261017_1250`.

---

## Instructivo: exclusión mutua entre motivo de rechazo y anulación — 16 de octubre de 2026

**Motivo:** una proforma `Enviada` no debe tener a la vez motivo de rechazo y motivo de anulación; solo uno de los dos puede llenarse.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| `Proformas.Motivo_Rechazo` | Sin *Valid if* | *Valid if* `ISBLANK([Motivo_Anulacion])` | Exclusión mutua con la anulación |
| `Proformas.Motivo_Anulacion` | Sin *Valid if* | *Valid if* `ISBLANK([Motivo_Rechazo])` | Exclusión mutua con el rechazo |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| Sección 5, columnas de `Proformas` | *Valid if* e *Invalid value error* en ambas columnas |

### Datos (`OXYData`)

La columna `Data Validity Formula` de `_Diccionario` se actualizó para ambas filas, con el texto de `Valid if` y de `Invalid value error`.

---

## Instructivo: `Configuracion.Valor` pasa a Decimal y nace `Compania` — 15 de octubre de 2026

**Motivo:** en AppSheet la columna `Configuracion.Valor` es Decimal y no puede leer textos: las columnas virtuales de datos de OXY salían vacías. Los datos de empresa y los correos de cobranza pasan a una tabla propia.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Datos de OXY y textos de la proforma | Diez claves `EMPRESA_*` y `PROFORMA_*` en `Configuracion` | Columnas de la tabla nueva `Compania` (una sola fila, `Compania_ID` = `OXY`) | `Valor` es Decimal; los textos necesitan tipos propios |
| `EMAILS_COBRANZA` | Clave de `Configuracion`; `None` apagaba el aviso | Columna `Emails_Cobranza` de `Compania`; vacía apaga el aviso | Es texto |
| `Configuracion.Valor` | Text | Decimal; solo números | Es el tipo que tiene la app |
| Columnas virtuales de `Proformas` | `LOOKUP("CLAVE","Configuracion","Clave","Valor")` | `LOOKUP("OXY","Compania","Compania_ID","Columna")`; mismos nombres | La plantilla no cambia |
| Permisos de `Compania` | — | Solo *Updates*; edita Gestión; Campo la puede leer | Decisión del usuario |
| LOG-B01, paso 2 | Condición `<>"None"` sobre `Configuracion` | `ISNOTBLANK` sobre `Compania.Emails_Cobranza` | Mismo motivo |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| 3.1 y 3.2 | `Configuracion` solo con claves numéricas; `Compania` descrita; permisos |
| 5.1 y 5.2 | Fórmulas de las diez virtuales; preparación con `Compania` |
| LOG-B01 | Condición y *To* leen `Compania.Emails_Cobranza` |
| 14.2 y 14.4 | `Compania` en la tabla de apps; riesgo de que Campo reciba cuentas bancarias y correos |
| 17.1 y 17.2 | V24 nueva; D06 ajustada; D07 nueva |

### Datos (`OXYData`)

Respaldo previo: `OXYData_20261015_1940`.

- Hoja nueva `Compania` con la fila `OXY` (textos en `COMPLETAR`).
- `Configuracion`: se quitaron las diez claves de empresa y `EMAILS_COBRANZA`; quedan siete claves numéricas.
- `_Diccionario`: `Configuracion.Valor` pasa a Decimal; filas nuevas de `Compania`; fórmulas de las diez virtuales actualizadas.
- `_Reglas` (fila de Apps y regla nueva de `Compania`) y `_Leeme` actualizados.

Pendiente de OXY: reemplazar `COMPLETAR` por los datos reales en `Compania`.

---

## Instructivo: la plantilla pasa a Google Docs — 15 de octubre de 2026

**Motivo:** el usuario creó la plantilla en Google Docs (`Plantilla_Demo`) a partir de la plantilla Word aprobada, y es la que usará el bot.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Formato de la plantilla | Word (.docx) | Google Docs, con las mismas marcas | Decisión del usuario |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| 3.3, 5.2, PRO-B02, 17.1 (V06) | Mencionan la plantilla de Google Docs |

Las marcas se revisaron contra la documentación de AppSheet y hilos de la comunidad: la forma de `If`/`EndIf` está documentada; `Start`/`End` deben ir en la misma tabla o ambos fuera de tablas; `TEXT(...)`, las referencias `[Cliente_ID].[Razon_Social]` y `Related ...` quedan para probar en V06 y V11.

### Datos (`OXYData`)

Sin cambios de estructura. `_Leeme` apunta al modelo de datos.

---

## Instructivo: PDF regenerable durante Borrador y documento personalizado — 14 de octubre de 2026

**Motivo:** generar el PDF de la proforma durante el Borrador, las veces que haga falta, para revisarlo antes de enviar; y permitir una versión propia del documento.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Generación del PDF | Al enviar (PRO-A01 disparaba PRO-B02) | Con la acción `A_Generar_PDF` (antes `A_Regenerar_PDF`), solo en `Borrador`, repetible | Revisar el diseño antes de enviar |
| `A_Enviar` | Cambiaba estado, fijaba `Fecha_Envio` y `Fecha_Vigencia` | Solo cambia `Estado` y fija `Fecha_Envio`. Exige `Doc_Proforma` generado (no la señal `PENDIENTE`), `Fecha_Vigencia` llena y no vencida | Decisión del usuario |
| Confirmación de `A_Enviar` | Mensaje solo con margen bajo | Siempre recuerda verificar que el PDF esté actualizado; añade el aviso de margen cuando aplica | Decisión del usuario |
| Regenerar tras enviar | Permitido a Gestión | No se puede regenerar el PDF después de enviar | Decisión del usuario |
| Documento propio | No existía | Columna `Doc_Proforma_Personalizado` (opcional, editable solo en Borrador). Si existe es el oficial; si no, `Doc_Proforma`. Columna virtual `Doc_Oficial` | Decisión del usuario |
| `Fecha_Vigencia` | La fijaba el envío | Requerida, con valor inicial hoy + `VIGENCIA_PROFORMA_DIAS`; el usuario la ajusta en Borrador. El PDF siempre la toma de la proforma | Decisión del usuario |
| Señal del bot | `PENDIENTE` fijo | `PENDIENTE\|yyyyMMddHHmmss`, distinta en cada pulsación | Que cada reintento dispare el bot |
| Nombre del archivo | `<Numero>.pdf` | `<Numero>_<Sello>.pdf`; nada se sobrescribe | Evitar duplicados |
| `Numero` | Único | Único y sin `/ : * ? < > \|` | Es parte del nombre del archivo |
| Plantilla | Google Docs | Word (.docx) | Plantilla aprobada por el usuario |
| `S_Proformas_Sin_PDF` | Comparaba con `PENDIENTE` | Prueba el inicio del valor | La señal ahora lleva sello |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| 5.1 | Bloques nuevos o ajustados: `Numero`, `Fecha_Vigencia`, `Doc_Proforma`, `Doc_Proforma_Personalizado`, `Doc_Oficial` |
| 5.3 | `S_Proformas_Sin_PDF` ajustado |
| PRO-A01, PRO-A10, PRO-B02 | Reescritos según lo anterior |
| 17.1 | V06 y V04 ampliadas; V23 nueva (columna virtual File) |

### Datos (`OXYData`)

Respaldo previo: `OXYData_20261014_2326`.

- `Proformas`: columna nueva `Doc_Proforma_Personalizado` (X).
- `_Diccionario`: filas nuevas `Doc_Proforma_Personalizado` y `Doc_Oficial`; filas ajustadas `Numero`, `Fecha_Vigencia`, `Doc_Proforma`.
- `_Reglas` (Proforma, Enviar) y `_Leeme` actualizados.

Pendiente: las proformas Borrador de demostración (PRF-019, PRF-022, PRF-023) tienen `Fecha_Vigencia` vacía; llenarla antes de enviarlas.

---

## Instructivo: datos de OXY en la plantilla del PDF — 14 de octubre de 2026

**Motivo:** que la plantilla de Google Docs de la proforma pueda imprimir los datos de OXY como empresa y los textos fijos de la proforma, editables sin tocar las apps ni la plantilla.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Datos de OXY | No existían en el modelo | Diez claves nuevas en `Configuracion`: `EMPRESA_NOMBRE_COMERCIAL`, `EMPRESA_RAZON_SOCIAL`, `EMPRESA_RUC`, `EMPRESA_DIRECCION_FISCAL`, `EMPRESA_TELEFONO`, `EMPRESA_EMAIL`, `EMPRESA_WEB`, `PROFORMA_CONDICIONES`, `PROFORMA_CUENTAS_BANCARIAS`, `PROFORMA_FIRMA_NOMBRE` | La plantilla necesita estos datos y deben poder cambiarse sin editar el Doc |
| Acceso desde la plantilla | — | Diez columnas virtuales de solo lectura en `Proformas` (`Empresa_*`, `Proforma_Condiciones`, `Proforma_Cuentas_Bancarias`, `Proforma_Firma_Nombre`), cada una con un `LOOKUP` a su clave | La plantilla solo ve columnas de la fila de la proforma |
| Datos en proformas ya enviadas | — | Reflejan siempre lo vigente en `Configuracion`; no se congelan al enviar. Una proforma regenerada con `A_Regenerar_PDF` sale con los datos actuales | Decisión del usuario |
| Edición de las claves | — | Igual que el resto de `Configuracion`: sin restricción adicional por rol | Decisión del usuario |
| Plantilla del PDF | Marcas de la proforma y el cliente | Se agregan las marcas de los datos de OXY y de los textos fijos | Mismo motivo |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| 3.2 | Lista las diez claves nuevas; traen el valor `COMPLETAR` hasta que OXY escriba los datos reales |
| 5.1 | Diez bloques de columna nuevos con su `App formula` |
| 5.2 | La preparación pide las claves con valores reales y las virtuales creadas |
| PRO-B02 | La plantilla lista las marcas nuevas |

### Datos (`OXYData`)

Respaldo previo: `OXYData_20261014_2206`.

- `Configuracion`: diez filas nuevas (A10:C19). `EMPRESA_WEB` queda vacía; el resto con `COMPLETAR`.
- `_Diccionario`: diez filas nuevas de `Proformas` después de `Total_Relacionadas`.
- `_Leeme`: referencia al modelo de datos actualizada.

Pendiente de OXY: reemplazar `COMPLETAR` por los datos reales.

---

## Instructivo: un bloque por columna y una propiedad por línea — 14 de octubre de 2026

**Motivo:** que el programador pueda leer el instructivo línea a línea y aplicarlo en AppSheet sin memorizar qué propiedad va en qué columna o acción. Antes, varias propiedades y varias columnas compartían una sola línea. No cambia ninguna regla de negocio, expresión ni nombre de componente: cambia la forma de presentarlos.

### Cambios de formato

| Tema | Antes | Ahora |
|---|---|---|
| Configuración de columnas (5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1) | Viñetas y tablas con varias columnas y varias propiedades en una línea | Un bloque por columna, con una propiedad por línea: `Show?`, `Editable?`, `Require?`, `Initial value`, `App formula`, `Valid if`, `Invalid value error` |
| Columnas con la misma regla | Una sola línea nombraba varias columnas (por ejemplo `Fecha_Aceptacion`, `Doc_Aceptacion`, `Motivo_Rechazo`) | Un bloque por cada columna |
| Acciones | `Tipo`, `Configuración`, `Only if`, `Confirmación`, `Visibilidad` | `For a record of this table`, `Action name`, `Do this`, `Table to add rows to`, `Set these columns` (una columna por línea) o `Actions` (lista numerada), `Only if this condition is true`, `Needs confirmation?` y `Confirmation Message`, `Position` y `Display name` |
| Bots | `Evento` y `Proceso` en líneas largas separadas por puntos medios | `Event` con una propiedad por línea (tipo, tabla, `Data change type`, condición; o `Schedule`, `Day`, `Time`, `Time zone`) y `Process` con pasos numerados: `Step type` y una línea por propiedad o columna |
| Nombres de propiedades | `Valid_If`, `Show_If`, `Editable_If`, `Required_If`, `Prominence`, `Display prominently` | Los del editor nuevo de AppSheet: `Valid if`, `Show?`, `Editable?`, `Require?`, `Position` (*Prominent* / *Hide*) |
| Procedimientos del editor (sección 2) | Rótulos mezclados del editor anterior | Reescritos con los rótulos del editor nuevo; nueva sección 2.5 sobre cómo aplicar los bloques de columnas |
| Verificación del documento | No revisaba el formato de las líneas | Una regla marca cualquier línea con más de una asignación o con varias propiedades |

### Rótulos por confirmar

`Set these columns`, `Table to add rows to` y `Data change type` no se pudieron confirmar en la documentación del editor nuevo. Quedan registrados en la validación V15; si el editor usa otro rótulo, se anota allí.

### Datos (`OXYData`)

Sin cambios.

---

## Instructivo: simplificación del manejo de proformas — 14 de octubre de 2026

**Motivo:** simplificar el manejo de proformas. Se retira todo lo que el sistema hacía solo con las revisiones, las complementarias y los reemplazos; la relación entre proformas la asigna el usuario. Se agrega el estado `Z-Eliminada` y la acción *Eliminar* para los borradores.

### Cambios de comportamiento

| Tema | Antes | Ahora | Por qué |
|---|---|---|---|
| Borrador no usado | Se anulaba (`Anulada`) | `A_Eliminar` (PRO-A04) lo pasa a `Z-Eliminada`: solo Gestión, sin motivo, guarda `Eliminada_Por` y `Fecha_Eliminacion`, deja el evento `PROFORMA_ELIMINADA` sin correo | Separar lo que nunca se envió de lo que se anula después de enviarlo |
| Anular proforma | Desde `Borrador` o `Enviada` | Solo desde `Enviada` | Un borrador no se anula |
| Enviar | Grupo de dos pasos; marcaba la previa como `Reemplazada` | Una sola acción (PRO-A01) que no toca otras proformas | Sin efectos automáticos sobre la previa |
| Estado `Reemplazada` | Existía | Se retira de la lista de estados | Nada lo produce |
| Revisión y complementaria automáticas | Botones *Crear revisión* y *Crear complementaria*, copia de conceptos y planificación, identificadores `<origen>-R<n>`, slice de revisiones incompletas y botón de reparación | Se retiran. El usuario crea un `Borrador` nuevo y digita todo | Complicaban el modelo y la recuperación de fallos |
| Relación entre proformas | Se creaba junto con la copia | `Proforma_Previa_ID` y `Tipo_Relacion` los elige el usuario en un `Borrador`. `Tipo_Relacion` es obligatorio si hay previa. La lista de previas excluye la propia proforma y las `Z-Eliminada`. Sin más validaciones | Decisión exclusiva del usuario |
| `Numero` | Descrito como autogenerado, con sufijo `-R<n>` | Lo digita el usuario; no puede repetirse entre proformas no eliminadas (propuesta, ver decisiones) | El PDF se nombra con el `Numero` |
| `Revision_Nro` | Columna de `Proformas` | Se quita de los datos y de la documentación | Ya no hay revisiones numeradas |
| Contador de relacionadas | No existía | `Total_Relacionadas` (virtual): cuenta las proformas no eliminadas que apuntan a esta | Saber si una proforma tiene relacionadas |
| Obra de una complementaria | Tomaba la obra principal de la previa | Se mantiene, pero depende de que el usuario haya elegido previa y tipo `Complementaria`; si no, la obra nace como principal | Misma fórmula, ahora con entrada manual |
| Vistas de proformas | No distinguían eliminadas | `S_Proformas_Activas` para la lista normal y `S_Proformas_Eliminadas` para auditar | Que lo eliminado no estorbe |

### Estructura del instructivo

| Cambio | Detalle |
|---|---|
| Componentes | Pasan de 77 a 67 (40 acciones y 27 bots). Las acciones de proformas bajan de 22 a 12 y se renumeran PRO-A01 a PRO-A12 |
| Validaciones | Pasan de 25 a 22. Se retiran las tres que solo servían a la copia y al reemplazo, y el resto se renumera V01 a V22. La validación de `Valid_If` sobre la misma tabla (V04) incluye ahora el `Numero` y la previa de las proformas |
| Pruebas | Las pruebas de humo bajan de 16 a 15. Se reescriben los escenarios E2E-2 a E2E-6 y la tabla de recuperación de fallos |
| Expresiones | Se retiran tres expresiones reutilizables que solo usaba la copia de revisiones |

### Corrección sobre los identificadores deterministas

El esquema de identificadores deterministas `<origen>-R<n>` era un diseño propio del instructivo y no estaba en el modelo de datos, donde `Proforma_ID` se genera con `"PRF'" & UNIQUEID()`. Se retira junto con las revisiones automáticas.

### Datos (`OXYData`)

Respaldo previo: `OXYData_20261014_0245`.

- `Proformas`: se quita `Revision_Nro`; se agregan `Eliminada_Por` y `Fecha_Eliminacion` (después de `Fecha_Anulacion`); la lista de estados pasa a Borrador, Enviada, Aceptada, Rechazada, Vencida, Anulada y Z-Eliminada.
- Datos demo: `PRF-005` (antes `Reemplazada`) pasa a `Anulada`, con motivo "Reemplazada por la proforma 005-2026-R1" y fecha 2026-06-22; el evento `EVT-0021` pasa de `PROFORMA_REEMPLAZADA` a `PROFORMA_ANULADA`.
- Hojas auxiliares: `_Diccionario`, `_Listas`, `_Reglas` y `_Leeme` actualizadas.

### Decisiones tomadas

1. `Z-Eliminada` se queda como nombre por ahora; el nombre y el orden en las listas pueden revisarse más adelante.
2. Eliminar no pide motivo, pero guarda quién y cuándo.
3. Cualquier usuario de Gestión puede eliminar un borrador.
4. Las proformas anuladas antes desde `Borrador` conservan su estado `Anulada`.
5. No hay clonación de proformas.

### Propuestas por defecto pendientes de confirmar

- `Numero` único entre proformas no eliminadas (`Valid_If`).
- `Proforma_Previa_ID` y `Tipo_Relacion` editables solo mientras la proforma es `Borrador`.
- `PRF-005` pasa a `Anulada` en los datos demo.
