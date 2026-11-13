# OXY Solution — Pendientes

Fecha de este corte: 12 de noviembre de 2026.
Estado de los documentos al momento del corte: `OXY_App_Proformas_Especificacion_v11`, `OXY_DataModel_Especificacion_v18`, `OXY_AppSheet_Arquitectura_y_Seguridad_v8`, `OXY_AppSheet_Historial_de_Cambios_v24`, `OXY_Propuesta_Dashboard_Indicadores_v5`. Los datos están en `OXYData` (último respaldo: `OXYData_20261014_2206`).

Cada pendiente dice qué es, por qué importa, cómo se retoma y qué cierra el pendiente.

---

## 1. Dashboard: quitar las citas a versiones de otros archivos

**Qué es.** `OXY_Propuesta_Dashboard_Indicadores.md` todavía menciona versiones de otros archivos (según lo que quedó pendiente en la revisión anterior, por ejemplo nombres de archivo con número de versión o referencias al modelo de datos y al libro de datos con su número de versión). Los otros dos documentos ya se limpiaron: el instructivo solo describe lo vigente, y los cambios van únicamente en el historial.

**Por qué importa.** Cada vez que cambia una versión, esas citas quedan desactualizadas y obligan a corregir el Dashboard a mano.

**Cómo se retoma.**
1. Buscar en el documento menciones de `_v` seguido de número, de `OXY_Datos`, `DataModel_v` y de las palabras "versión" o "v" + número.
2. Reemplazarlas por el nombre del documento sin versión (por ejemplo `OXY_DataModel_Especificacion`) o por una referencia a `OXYData`, que es la fuente oficial de los datos.
3. Al guardar el resultado, el archivo lleva su propia versión en el nombre (regla del proyecto).
4. Revisar de paso que las columnas y los nombres que el Dashboard cita sigan existiendo tras los cambios de proformas (se quitó `Revision_Nro` y el estado `Reemplazada`; se agregó el estado `Z-Eliminada`).

**Cierra cuando.** El documento no contiene ninguna cita a versiones de otros archivos y sus referencias a proformas coinciden con el modelo de datos vigente.

---

## 2. Validar V01–V24 en el editor de AppSheet

**Qué es.** El registro de validaciones (sección 17.1 del instructivo) lista 24 capacidades o expresiones que no se pueden dar por buenas hasta probarlas en el editor. Todas están en estado *Pendiente*. Cada una trae qué probar, con qué datos, el resultado esperado y la alternativa si falla.

**Cómo se retoma.** Recorrerlas por grupos, en este orden sugerido, porque unas dependen de otras:

| Grupo | IDs | Qué cubre | Nota |
|---|---|---|---|
| Editor y rótulos | V15 | Rutas del editor nuevo y los rótulos `Set these columns`, `Table to add rows to` y `Data change type`, que no se pudieron confirmar en la documentación | Hacerla **primero**: si un rótulo cambia, se corrige el instructivo antes de construir nada |
| Bots y encadenado | V01, V10, V13, V18, V19, V22 | Qué pasa si falla un paso, *Trigger other bots*, bots programados en Core, bots por app, *Set row values* sobre un conjunto, paso condicional | Condicionan el diseño de todos los bots programados |
| Notificaciones | V02, V03, V14 | Push de un bot *Adds*, lista calculada en *Para*, expresiones `<<...>>` en el texto del push | |
| Archivos y PDF | V06, V11, V23, V24 | *Create a new file* en Core con plantilla de Google Docs y nombre con sello propio; columna virtual File; nombre de la columna inversa `Related ...` para la plantilla | Alternativa si falla V06: plantilla HTML o PDF manual |
| Validaciones de columna | V04, V08, V09, V12 | `Valid if` con `SELECT` sobre la misma tabla (incluye `Numero` y `Proforma_Previa_ID` de proformas), crédito fiscal, valor inicial en columna oculta, duración de 24 horas | |
| Expresiones en acciones y bots | V05, V07, V20, V21 | Mensaje de confirmación calculado, `[_THISROW_BEFORE]`/`[_THISROW_AFTER]`, `LOOKUP` a `Metas_KPI`, clave calculada como texto | |
| Seguridad | V16, V17 | *Security filter* con `SELECT` y `LOOKUP` anidados; cuenta fuera de `Trabajadores` | Usa las seis cuentas de prueba de 3.4 |

**Cómo se cierra cada fila.** Se anota la fecha, quién la probó y el resultado. Si falla, se aplica la alternativa de la fila y se corrige el instructivo en la parte que dependía de ella. El criterio de salida de cada sección (5.6, 6.x, 7.5, 8.5, etc.) menciona qué V debe estar cerrada antes de pasar a la siguiente sección.

**Cierra cuando.** Las 24 filas tienen fecha, responsable y resultado, y el instructivo refleja las alternativas que hubo que aplicar.

---

## 3. Cerrar las decisiones abiertas D01–D07

**Qué es.** La sección 17.2 del instructivo registra seis decisiones de negocio. Hoy cada una tiene un comportamiento por defecto ya implementado; falta que quien corresponde las confirme o las cambie.

| ID | Decisión | Qué hace hoy el sistema | Quién decide | Si cambia, qué se toca |
|---|---|---|---|---|
| D01 | ¿Se registra un evento `HORAS_APROBADAS` al aprobar horas? | No se registra | Gerencia | Agregar el tipo de evento al modelo, un paso de log a `A_Aprobar_Horas` (HOR-A01) o un bot nuevo, y la fila en la tabla de eventos de 13.2 |
| D02 | ¿Los precios y el presupuesto de costo de `Obras` pueden llegar al teléfono de Campo? (14.4) | Sí, en las obras asignadas | Gerencia | Cambiar el *security filter* o las columnas visibles de `Obras` en OXY Campo (sección 14) y recordar que `Show?` no protege el dato, solo la pantalla |
| D03 | ¿Quién ejecuta *Cerrar* una obra con cobranza completa: Gestión o solo Gerencia? | Gestión (*Cerrar con saldo* es solo de Gerencia) | Gerencia | Cambiar el `Only if this condition is true` de la acción de cierre (OBR-A06) para usar `ES_GERENCIA` |
| D04 | ¿Se mantiene la clave `DIAS_ALERTA_SIN_GASTOS` de `Configuracion`? | Las alertas leen solo `Metas_KPI`; la clave no se usa | Dueño de datos | Si se elimina, quitarla de `Configuracion` y del modelo de datos (confirmar antes de borrar nada en `OXYData`, con respaldo previo) |
| D05 | ¿Se permite anular una factura con abonos vigentes? | No: primero se anulan los abonos | Gestión | Cambiar el `Only if this condition is true` de la anulación de facturas (FAC-A01) y revisar el efecto en `Estado_Pago` y en la cobranza |
| D06 | ¿Los correos de `Compania.Emails_Cobranza` reciben el aviso de cobranza completa? | Sí, si el campo no está vacío (LOG-B01, paso 2) | Gestión | Dejar el campo vacío apaga el aviso sin tocar el bot |
| D07 | ¿Las cuentas bancarias, las condiciones y los correos de `Emails_Cobranza` de `Compania` pueden llegar al teléfono de Campo? (14.4) | Sí, solo lectura | Gerencia | Sacar esos campos a otra tabla fuera de Campo |

**Cierra cuando.** Cada fila de 17.2 dice la decisión tomada, quién la tomó y la fecha, y el cambio correspondiente (si lo hubo) está aplicado en el modelo de datos, en `OXYData` y en el instructivo.

---

## 4. Otros pendientes anotados durante el trabajo

### 4.1 Mover los documentos viejos a la carpeta `deprecated`

Quedan en la carpeta `appsheet-def` las versiones anteriores del instructivo y del historial (`OXY_AppSheet_Acciones_y_Bots_v6`, `_v7` y los historiales v1 y v2), además de versiones anteriores del modelo de datos. Las debes pasar tú a `deprecated`; yo no leo ni toco esa carpeta.

### 4.2 Fórmulas de las columnas virtuales de `Obras`

La sección 6.1 del instructivo lista las 25 columnas virtuales de `Obras` solo con su nombre; las fórmulas ya no viven en `_Diccionario` (que ahora solo lista la estructura); están en `_Diccionario_Legado` solo para consulta y vivirán en la especificación de cada app. Al construir las virtuales en el editor se copian de la especificación de la app. Si se quiere que el instructivo sea autosuficiente, habría que pasar cada fórmula a un bloque de columna (`App formula`).

### 4.3 Dos textos propuestos en 7.1 que conviene confirmar

- `Monto_IGV`: el texto de `Invalid value error` ("El IGV no coincide con el calculado sobre el monto base. Revise exoneraciones o redondeos.") lo redacté yo; antes el instructivo solo decía "mensaje de advertencia".
- `Tipo_Comprobante`: agregué una expresión opcional para el valor inicial (`Boleta` en tipos externos, `Sin comprobante` en tipos de origen `Interno manual`) además de la regla en texto.

### 4.4 Paso condicional del correo de cobranza (LOG-B01, paso 2)

Al reestructurar escribí la condición del paso (`AND([Tipo_Evento]="COBRANZA_COMPLETA",ISNOTBLANK(LOOKUP("OXY","Compania","Compania_ID","Emails_Cobranza")))`). Antes la regla estaba solo en prosa. Se valida junto con V22.

### 4.5 Construcción en AppSheet

Todo el instructivo está listo pero ninguna acción, bot ni columna se ha construido aún en el editor. El orden de construcción está en la sección 4 del instructivo (inventario) y cada sección 5 a 13 trae su lista de preparación y sus criterios de salida.

### 4.6 Completar los datos de OXY en `Compania`

La fila de `Compania` quedó con `COMPLETAR` en los textos (`Web` y `Emails_Cobranza` vacías). OXY debe escribir los datos reales: nombre comercial, razón social, RUC, dirección fiscal, teléfono, correo, web si aplica, condiciones comerciales, cuentas bancarias, nombre de firma y los correos del aviso de cobranza.

### 4.7 Plantilla de Google Docs de la proforma

La plantilla `Plantilla_Demo` ya está en Drive. Falta renombrarla o copiarla como `Plantilla_Proforma`, revisar que "PROFORMA N°" no haya perdido el salto de línea y decidir si lleva logo (las imágenes necesitan URL pública). En V06 y V11 se prueba que AppSheet lea las marcas: `Start`/`End` en la fila de conceptos, `TEXT(...)` y `Related ...`. Opcionales: total en letras ("SON: ...") y unidad/cantidad por concepto.

### 4.8 Fecha_Vigencia vacía en borradores de demostración

`PRF-019`, `PRF-022` y `PRF-023` (Borrador) no tienen `Fecha_Vigencia`; como ahora es requerida y `A_Enviar` la exige, hay que llenarla antes de probarlos.

### 4.9 Barra invertida y comillas en `Numero`

La validación rechaza `/ : * ? < > |`. La barra invertida y las comillas dobles no se añadieron porque no está confirmado cómo escribirlas en una fórmula de AppSheet; se prueban en V04.

### 4.10 Proforma sin PDF válido

Mientras la proforma es `Borrador` o `Enviada`, el PDF se corrige pulsando `A_Generar_PDF`. Solo en `Aceptada`, `Rechazada` o `Vencida` hay que corregir `Doc_Proforma` a mano en `OXYData`. Con la condición de `A_Enviar` esto no debería ocurrir; la lista `S_Proformas_Sin_PDF` lo detecta si pasa.

### 4.11 Construir `Compania` en AppSheet

Agregar la tabla `Compania` desde `OXYData` con solo *Updates*; en `Configuracion` regenerar la estructura y confirmar que `Valor` es Decimal; cambiar las fórmulas de las diez columnas virtuales de `Proformas` y las de LOG-B01 (paso 2). Se valida en V24.

### 4.12 Filtro de seguridad mínimo por tabla (diferido)

**Qué es.** Una condición única, igual para todas las tablas de una app, que se pega en *Data → Tables → tabla → Security filter* y que solo envía filas al dispositivo si quien abre la app está en `Trabajadores`, está activo y tiene un rol permitido en esa app. No filtra por obra ni por dueño del registro. Forma general (la lista de roles cambia por app):

```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST(<roles de la app>)))
```

| App | Roles permitidos |
|---|---|
| OXY Master | `Super`, `Administracion` |
| OXY Proformas | `Super`, `Administracion`, `Supervisor`, `Planificacion` |
| OXY Gestión | `Super`, `Administracion`, `Supervisor`, `Operaciones` |
| OXY Campo | `Super`, `Campo` |
| OXY Dashboard | `Super`, `Administracion` |

**Decisión tomada.** No se usa en la primera versión de las 5 apps. En esta versión la seguridad de datos es solo la lista de usuarios de cada app (inicio de sesión de Google) y los roles solo controlan las acciones (`Only if this condition is true`). Todo usuario que entra a una app lee todos los datos que esa app ofrece.

**Por qué importa.** Mientras no exista, la lista de usuarios de cada app es la única barrera de datos:
- Una cuenta agregada por error a la lista de una app, con un rol que esa app no permite, lee los datos igual.
- Dar de baja a una persona exige poner `Activo = No` en `Trabajadores` y además quitarla de la lista de cada app donde esté; si falta una, sigue leyendo los datos de esa app (las acciones sí dejan de aparecerle, porque la expresión de roles comprueba `Activo`).
- Un cambio de rol no recorta lo que la persona ya puede leer.

**Cómo se retoma.**
1. Pegar la expresión, con la lista de roles de la app, en el filtro de seguridad de cada tabla de esa app. Es el mismo texto para todas las tablas de la app.
2. Probar con una cuenta que esté en la lista de la app pero con un rol no permitido, y con una cuenta con `Activo = No`: en ambos casos la app debe abrir sin datos.
3. Confirmar que la tabla `Trabajadores` sigue entregando al usuario permitido su propia fila, porque las expresiones de rol de las acciones la consultan.
4. Registrar la prueba en el registro de validaciones del documento de arquitectura y seguridad.

**Cierra cuando.** Cada tabla de cada app tiene el filtro (o se decide por escrito mantenerlo diferido) y las dos pruebas del paso 2 dieron el resultado esperado.

### 4.13 Alinear el modelo de datos y `OXYData` con la nueva estructura de documentos

Quedan para una sola pasada, con respaldo previo de `OXYData`, cuando estén escritas las especificaciones de Gestión, Campo, Master y Dashboard:

1. Quitar de `OXY_DataModel_Especificacion` el texto de configuración que ya vive en las especificaciones de app (`Editable_If`, valores iniciales, `Valid If`, `Show if`), y corregir el campo *Apps* de cada tabla (hoy dice Gestión o Campo).
2. Migrar los roles antiguos (`Admin`, `Gerencia`, `Campo`) a los seis roles nuevos en `Trabajadores`, `_Listas`, `Compania` y las notas.
3. Pasar de tres a cinco apps el texto de `_Leeme` y `_Reglas`.
4. Eliminar `_Diccionario_Legado` cuando todas las especificaciones estén completas.

### 4.14 Copia de planificación y conceptos de proforma

**Qué es.** Nueva acción `A_Copiar_Planificacion_Conceptos` (PRO-A13) con tabla de control `Control_Copias` y bot `B_Copiar_Lineas` (PRO-B05). Copia líneas de `Proforma_Conceptos` y `Proforma_Planificacion` desde una proforma origen (`Copiar_Desde_ID`) hacia la proforma destino en `Borrador`.

**Cómo se retoma.**
1. Respaldar `OXYData` (`OXYData_aaaammdd_hhmm`).
2. Agregar columna `Copiar_Desde_ID` a `Proformas` en `OXYData` y crear tabla `Control_Copias` con la fila `COPIAS` (`Estado = "Libre"`).
3. Actualizar `_Diccionario` de `OXYData` (solo estructura: Tabla, Columna, Tipo AppSheet, Clave, Requerido, Virtual).
4. Escribir los cambios en `OXY_App_Proformas_Especificacion` (v11), `OXY_DataModel_Especificacion` (v18), `OXY_AppSheet_Arquitectura_y_Seguridad` (v8), `Pendientes` (v9).
5. Registrar todo en `OXY_AppSheet_Historial_de_Cambios` (v24).
6. Construir en el editor: tabla `Control_Copias`, acciones PRO-A13 a PRO-A17, bot PRO-B05, slice `S_Control_Copias_En_Proceso`.
7. Probar con PR-18 a PR-21.

**Cierra cuando.** Las pruebas PR-18 a PR-21 pasaron y el historial v24 está registrado.

---

## Orden sugerido para retomar

1. V15 (confirmar rótulos del editor) y corregir el instructivo si hace falta.
2. Cerrar D01–D07 con quienes corresponde, para no construir algo que luego cambie.
3. Limpiar el Dashboard (pendiente 1) y completar los datos de OXY (4.6).
4. Construir sección por sección, cerrando las validaciones V que cada sección pide en sus criterios de salida.
