# OXY Industrial S.R.L. — Instructivo de construcción de acciones, bots y seguridad en AppSheet

**Plan:** Core · **Alcance:** todo dentro de AppSheet · **Datos:** un solo Google Sheet, `OXYData`.
**Apps:** `OXY Campo` (celular, 10 usuarios) y `OXY Gestión` (escritorio, 5 usuarios). La tercera app, `OXY Dashboard`, y sus procesos programados de indicadores se describen en `OXY_Propuesta_Dashboard_Indicadores.md`.
**Para quién es:** el programador que construye las apps en el editor de AppSheet. Está escrito para seguirse en orden, sin conocimiento previo del diseño.

---

## 0. Cómo usar este documento

### 0.1 Fuentes de verdad

| Qué | Dónde está la definición vigente |
|---|---|
| Tablas, columnas, tipos, claves, relaciones y valores permitidos | `OXY_DataModel_Especificacion.md` |
| Fórmulas, `Valid if`, `Show?`, `Editable?` y valores iniciales de cada columna | Pestaña `_Diccionario` de `OXYData` |
| Parámetros editables (IGV, vigencia, tolerancias) y umbrales de alertas | Pestañas `Configuracion` y `Metas_KPI` de `OXYData` |
| Procesos programados de indicadores (`Snap_*`, `Jobs_Control`) y reglas de alerta de consumo y CPI | `OXY_Propuesta_Dashboard_Indicadores.md` |
| Acciones, bots, seguridad, pruebas y recuperación | Este documento |

Si una columna, un tipo o un valor permitido de este documento no coincide con el modelo de datos, **manda el modelo de datos** y se corrige este documento. Antes de empezar, comprobar que las pestañas de `OXYData` coinciden con el modelo de datos.

### 0.2 Cómo está organizado

1. Las secciones 1 a 4 son de lectura previa: convenciones, procedimientos generales, prerrequisitos e inventario con el orden de construcción.
2. Las secciones 5 a 13 son los procedimientos de construcción, una por flujo de negocio. Cada una trae su preparación, sus fichas de acciones y bots, y sus **criterios de salida**: no pasar a la siguiente sección hasta cumplirlos.
3. La sección 14 es la seguridad; la 15, las pruebas; la 16, el diagnóstico y la recuperación; la 17, el registro de validaciones y decisiones abiertas.

### 0.3 Cómo se lee una ficha

Cada acción y cada bot tiene una ficha con el mismo formato (plantillas completas en la sección 2.4). La ficha dice **qué valores poner**; la sección 2 dice **dónde hacer clic**. Las expresiones de las fichas están completas y listas para copiar; no contienen marcadores entre signos angulares.

### 0.4 Marca `⚠ V##`

`⚠ V##` señala una expresión o capacidad que no se debe dar por buena hasta probarla en el editor. Cada marca remite a una fila del **registro de validaciones** (sección 17), que dice qué probar, con qué datos, qué resultado lo confirma y qué alternativa usar si falla. Una marca se cierra solo cuando su fila del registro tiene resultado.

### 0.5 Alcance de las apps

Una acción pertenece a la app donde se crea y solo aparece en ella. Un bot de cambio de datos **solo reacciona a cambios hechos desde la app en la que existe** (⚠ V18). Por eso:

- Las tablas que escriben ambas apps (`Gastos_Obra`, `Registro_Horas`, `Avances_Obra`) llevan sus bots de cambio de datos y sus acciones de anulación **en las dos apps**, con la misma configuración. Cada ficha indica la app.
- Los bots programados se crean **solo en OXY Gestión**; actúan sobre los datos sin importar quién los use.
- Un push solo llega a quien tiene instalada **la app donde vive el bot**. Los avisos a personas que no usan esa app (por ejemplo, el responsable de una obra que trabaja solo en OXY Campo) van por correo (13.4).

---

## 1. Convenciones y expresiones reutilizables

### 1.1 Nombres

- Prefijos: acciones `A_`, bots `B_`, slices `S_`.
- Cada componente de este documento tiene un código (`PRO-A01`, `GAS-B01`…): tres letras de la sección, `A` (acción) o `B` (bot) y un número. El código se usa en las dependencias, el inventario y las pruebas.
- Las claves de las tablas terminan en `_ID`.

### 1.2 Reglas de datos que el programador debe respetar

- `Estado` nunca es editable por el usuario (`Editable?` = `FALSE`): cambia solo con acciones. Las acciones y los bots ignoran `Editable?`, así que pueden escribir en columnas no editables.
- No hay botón *Delete* en tablas transaccionales: lo erróneo se **anula** (`Estado = Anulado` + motivo).
- Una proforma `Rechazada` no se edita ni se reabre; se corrige con una proforma nueva que el usuario relaciona a mano.
- Un `Borrador` no se anula: se elimina (`Estado = Z-Eliminada`, con quién y cuándo). La anulación es solo para proformas `Enviada`.
- Cada proforma genera exactamente una obra. Una proforma puede apuntar a una previa que el usuario asigna a mano, con el tipo de relación (revisión o complementaria); el sistema no copia ni cambia nada por esa relación.
- Moneda única: soles. Los costos se registran **sin IGV**; el IGV pasa a costo solo si ese registro no es crédito fiscal (`Es_Credito_Fiscal` se decide por registro).
- Fechas: los datos de control de registro (`Creado_En`, `Procesado_En`, `Fecha_Hora`) son `DateTime` con `NOW()`; las fechas de cambio de estado de un documento (`Fecha_Envio`, `Fecha_Rechazo`, `Fecha_Anulacion`, `Fecha_Inicio`, `Fecha_Cierre`, `Fecha_Pago_Real`) son `Date` con `TODAY()`. La hora exacta de cada cambio queda en `Log_Eventos`.
- Para llegar a una tabla a través de otra se usan las columnas virtuales de tipo Ref definidas en el modelo de datos (por ejemplo `[Obra_ID].[Cliente_ID]`), no `LOOKUP`.

### 1.3 Interfaz no es seguridad

`Show?`, `Editable?`, `Only if this condition is true` y la `Position` de un botón controlan **lo que se ve y lo que se puede hacer desde la pantalla**. No impiden que los datos lleguen al dispositivo. La protección real son las tablas que se incluyen en cada app y los *security filters* (sección 14). Toda regla de rol de este documento debe leerse con esta salvedad.

### 1.4 Expresiones reutilizables

Se copian tal cual. Fallan de forma segura: si el usuario no existe en `Trabajadores` o está inactivo, devuelven falso.

**¿Es Gestión (Admin o Gerencia, activo)?**
```
AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))
```
**¿Es Gerencia (activo)?**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Gerencia",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))
```
**¿La obra del registro está abierta?** (para tablas con `Obra_ID`)
```
NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada")))
```
**Tasa de IGV** (decimal: se lee con `DECIMAL()`; `NUMBER()` devuelve 0 con 0.18)
```
DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))
```
**Valor entero de configuración** (días): `NUMBER(LOOKUP("VIGENCIA_PROFORMA_DIAS","Configuracion","Clave","Valor"))`; para otra clave se cambia el texto entre comillas.

**Destinatarios: Gestión**
```
SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))
```
**Destinatarios: Gerencia**
```
SELECT(Trabajadores[Email],AND([Rol]="Gerencia",[Activo]=TRUE))
```
**Correo del responsable de la obra** (en tablas con `Obra_ID`)
```
[Obra_ID].[Responsable_ID].[Email]
```
**Tarifa vigente por hora y por hora extra** (tabla `Registro_Horas`)
```
ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))
```
```
ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora_Extra],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))
```

---

## 2. Procedimientos generales del editor

Las fichas de las secciones 5 a 13 y los bloques de columnas traen **una propiedad por línea**, con el nombre que esa propiedad tiene en el editor nuevo de AppSheet (el que viene activado por defecto). Aquí está el procedimiento que se repite.

> **Rutas confirmadas en la documentación de AppSheet:** `Automation → Bots` (panel de bots); `+` en el encabezado del panel para crear un bot; `More (⋮) → Test` para probar un bot; `Monitor` en el encabezado del bot; `Enable/Disable` en el mismo encabezado; los avisos de error aparecen como un indicador en el encabezado. Propiedades de columna: `Show?`, `Editable?`, `Require?`, `Initial value`, `App formula`, `Valid if`, `Invalid value error`, `Type Details`. Propiedades de acción: `Action name`, `For a record of this table`, `Do this`, `Position`, `Display name`, `Action Icon`, `Only if this condition is true`, `Needs confirmation?`, `Confirmation Message`. Propiedades de bot: `Event`, `Process`.
> **Pendiente de confirmar en el editor (⚠ V15):** los rótulos `Set these columns`, `Table to add rows to` y `Data change type`, y el acceso exacto para crear acciones. Si un rótulo difiere, usar el equivalente y anotarlo en el registro de validaciones.

### 2.1 Procedimiento A — crear una acción

Cada línea de la ficha corresponde a un campo del editor; se completan de arriba abajo.

1. Abrir la app indicada en **App · Tabla** (`OXY Gestión` o `OXY Campo`) en el editor.
2. Ir a **Actions**. Pulsar **+** y elegir **Create a new action** (⚠ V15).
3. **For a record of this table:** elegir la tabla de la ficha.
4. **Action name:** escribir el nombre de la ficha.
5. **Do this:** elegir el tipo de la ficha. Los tipos que se usan son:
   - *Data: set the values of some columns in this row* (cambiar columnas de la fila).
   - *Data: add a new row to another table using values from this row* (crear una fila en otra tabla).
   - *Grouped: execute a sequence of actions* (grupo: lista de acciones en orden).
6. Completar lo que pide el tipo:
   - En los tipos de cambiar columnas o crear fila: **Set these columns**. Por cada línea `Columna` = `expresión` de la ficha, agregar la columna y pegar la expresión en su campo.
   - En el tipo de crear fila: antes, **Table to add rows to** (la tabla de la ficha).
   - En el grupo: **Actions**, agregando las acciones en el orden numerado de la ficha.
7. **Only if this condition is true:** pegar la expresión de la ficha; si la ficha dice "(dejar vacío)", no tocar el campo.
8. **Needs confirmation?:** si la ficha dice *Yes*, activarlo y completar **Confirmation Message**; si dice *No*, dejarlo apagado. El mensaje puede ser texto simple (se escribe tal cual, sin comillas) o una expresión (se escribe la expresión de la ficha). El Sí/No no es condicional.
9. **Position:** *Prominent* para un botón visible; *Hide* para una auxiliar que solo llama un grupo o un bot. Si es *Prominent*, escribir **Display name**.
10. Guardar y comprobar que el indicador de errores del encabezado no marca la acción.
11. Ejecutar las pruebas de la ficha (la sección 15 explica el formato).

### 2.2 Procedimiento B — crear un bot de cambio de datos

1. Abrir la app indicada en la ficha. Ir a `Automation → Bots` y pulsar `+` para crear un bot. Nombrarlo con el nombre de la ficha.
2. **Event:** completar las líneas del bloque *Event* de la ficha: tipo *Data change*, **Table**, **Data change type** (*Adds only* o *Updates only*) y **Condition** (si la ficha dice "(sin condición)", dejarla vacía). En las condiciones de *Updates* se usan `[_THISROW_BEFORE]` (valores antes) y `[_THISROW_AFTER]` (valores después).
3. **Process:** agregar los pasos en el orden numerado de la ficha. Cada paso trae su *Step type* y las líneas que lo configuran:
   - *Run a data action → Add new rows to another table:* **Table** y una línea `Columna` = `expresión` por cada columna.
   - *Run a data action → Set row values:* una línea `Columna` = `expresión` por cada columna; actúa sobre la fila que disparó el bot.
   - *Send an email:* **To**, **Subject**, **Body**.
   - *Send a push notification:* **Recipients**, **Message**.
   - *Run a data action → Create a new file:* **Template**, **File type**, **Folder path**, **File name prefix**, **Disable timestamp**.
4. Revisar la opción **Trigger other bots** del bot según la ficha. Si está activa, los cambios que haga este bot pueden disparar otros bots (máximo 5 en cadena; un bot no puede dispararse a sí mismo) (⚠ V10).
5. Guardar. Corregir cualquier error que muestre el indicador del encabezado.
6. Probar con `More (⋮) → Test` y provocando el evento real desde la app. Revisar el resultado en `Monitor`.

### 2.3 Procedimiento C — crear un bot programado

1. Igual que B pasos 1 y 5. En **Event** elegir *Scheduled*.
2. Completar las líneas del bloque *Event* de la ficha: **Schedule** (diaria o semanal), **Day** si es semanal, **Time** y **Time zone** (**America/Lima**). Los bots programados necesitan una suscripción que los soporte; confirmar que el plan Core los permite (⚠ V13).
3. **Process:** un bot programado no tiene fila propia. Para actuar sobre filas se usa un paso *Run a data action → Execute an action on a set of rows*, con tres líneas: **Referenced Table**, **Referenced Rows** (la expresión `SELECT(...)` de la ficha) y **Referenced Action** (una acción auxiliar ya creada, que actúa sobre cada fila). Por eso las acciones auxiliares se construyen **antes** que el bot.
4. Para probar: ejecutar el bot a mano (`More (⋮) → Test`, o *Run* si el editor lo ofrece) sobre datos que cumplan y que no cumplan la condición (⚠ V13).

### 2.4 Formato de las fichas

Cada línea de una ficha es una propiedad del editor o un dato de control. Las líneas de configuración se pueden aplicar de arriba abajo, sin consultar otra parte.

**Ficha de acción**

- **App · Tabla:** dónde se crea.
- **Depende de:** códigos de lo que debe existir antes. "—" si nada.
- **For a record of this table:** la tabla.
- **Action name:** el nombre exacto.
- **Do this:** el tipo.
- **Table to add rows to:** solo en acciones que crean una fila.
- **Set these columns:** una línea `Columna` = `expresión` por columna. En un grupo, **Actions** con la lista numerada.
- **Only if this condition is true:** expresión completa, o "(dejar vacío)".
- **Needs confirmation?:** *Yes* o *No*.
- **Confirmation Message:** solo si es *Yes*.
- **Position:** *Prominent* o *Hide*.
- **Display name:** solo si es *Prominent*.
- **Idempotencia:** qué impide duplicados o estados inválidos al repetirla.
- **Prueba +:** datos de partida, qué ejecutar y el resultado esperado.
- **Prueba −:** cuándo no debe aparecer o no debe cambiar nada.
- **Repetición:** qué pasa al ejecutarla otra vez.
- **Si falla:** qué revisar y cómo recuperar.

En el texto de apoyo, "`Only if`" es la abreviatura de *Only if this condition is true*.

**Ficha de bot**

- **App · Tabla:** dónde se crea y sobre qué tabla actúa.
- **Event:** líneas con el tipo de evento, la tabla, el tipo de cambio y la condición (o la programación).
- **Depende de:** códigos.
- **Process:** pasos numerados; cada uno con su *Step type* y una línea por propiedad o columna.
- **Datos que escribe:** tablas y columnas que crea o modifica.
- **Idempotencia:** qué impide duplicados.
- **Límites del plan Core:** cuotas de correo, push y ejecuciones relevantes.
- **Prueba +, Prueba −, Repetición, Si falla:** igual que en las acciones; para los bots se agrega cómo comprobar la ejecución en `Monitor`.

Una línea que empieza por "Nota:" es una explicación; no se configura nada en el editor.

### 2.5 Cómo aplicar los bloques de columnas

Los bloques de las secciones 5.1 a 11.1 se aplican así:

1. En el editor, ir a **Data → Tables**, abrir la tabla indicada y entrar a **Columns**.
2. Abrir la columna del bloque (el título en negrita).
3. Aplicar sus líneas de arriba abajo; cada línea es una propiedad de la columna:
   - `Show?`, `Editable?` y `Require?`: abrir el campo y escribir la expresión de la línea (un valor `TRUE` o `FALSE` fijo también se escribe como expresión).
   - `Initial value` y `App formula`: pegar la expresión. Una columna real con **App formula** se recalcula al guardar; con **Initial value** solo se llena al crear la fila.
   - `Valid if` e `Invalid value error`: pegar la expresión y el mensaje de la línea siguiente.
   - `Type Details`: los valores o ajustes propios del tipo (por ejemplo, la lista de un Enum).
4. Las propiedades que no aparecen en el bloque se dejan como están.
5. Los bloques que dicen "acción de sistema *Edit*" se configuran en **Actions**, en la acción *Edit* de la tabla, con su `Only if this condition is true`.

---

## 3. Prerrequisitos

Todo esto debe estar listo antes de crear la primera acción.

### 3.1 Datos

1. `OXYData` tiene las pestañas y columnas del modelo de datos (las fórmulas están en `_Diccionario`). Las columnas virtuales no existen en el Sheet: se crean en el editor de cada app según el `_Diccionario`.
2. Las tablas se agregan a cada app desde `OXYData` (*Data → Tables*) y se regenera su estructura. Qué tablas lleva cada app: sección 14.2.
3. Permisos de cada tabla en la app: permitir *Adds* y *Updates*; **sin *Deletes*** en las tablas transaccionales (`Proformas`, `Proforma_Conceptos`, `Proforma_Planificacion`, `Obras`, `Gastos_Obra`, `Registro_Horas`, `Avances_Obra`, `Facturas_Obra`, `Abonos_Obra`, `Asignaciones_Obra`, `Log_Eventos`, `Alertas`). `Compania`: solo *Updates* (sin *Adds* ni *Deletes*), porque es una tabla de una sola fila.
4. Cada columna configurada según el `_Diccionario`: tipo, requerido, `Initial value`, `Editable?`, `Show?`, `Valid if`.

### 3.2 Configuración

1. Zona horaria de las apps y de los bots programados: **America/Lima** (UTC-5), para que `TODAY()` y los horarios usen la fecha local.
2. Pestaña `Configuracion` con las claves numéricas: `VIGENCIA_PROFORMA_DIAS`, `IGV_PCT`, `MARGEN_MINIMO_PCT`, `TOLERANCIA_COBRANZA`, `PLAZO_PAGO_DIAS_DEFECTO`, `DIAS_RECORDATORIO_COBRANZA` y `DIAS_ALERTA_SIN_GASTOS`. La columna `Valor` debe ser de tipo **Decimal** y solo admite números: un texto no se puede leer. Valores iniciales en el modelo de datos, sección de parámetros.
2b. Pestaña `Compania`: una sola fila (`Compania_ID` = `OXY`) con los datos de OXY para la proforma impresa (`Nombre_Comercial`, `Razon_Social`, `RUC`, `Direccion_Fiscal`, `Telefono`, `Email`, `Web`, `Condiciones_Proforma`, `Cuentas_Bancarias`, `Firma_Nombre`) y los correos del aviso de cobranza completa (`Emails_Cobranza`, separados por coma; vacío = sin aviso). Los textos traen `COMPLETAR` hasta que OXY escriba los datos reales; `Web` y `Emails_Cobranza` pueden quedar vacíos. La fila se crea en el Sheet; la app no agrega ni borra filas.
3. Pestaña `Metas_KPI` con los umbrales de las alertas (`DIAS_SIN_GASTOS`, `DIAS_SIN_AVANCE`, `REZAGO_FACTURACION_PP`, `DIAS_FACTURA_VENCIDA`, `DIAS_ATRASO` y los demás). Las alertas de este documento leen sus umbrales de aquí.
4. Pestaña `Trabajadores` con todos los usuarios, su `Email` (la cuenta Google con la que inician sesión), `Rol` (`Admin`, `Gerencia` o `Campo`) y `Activo`. Las expresiones de rol dependen de esto.

### 3.3 Archivos

1. En Drive, bajo la carpeta de datos de las apps: `Proformas_Files`, `Gastos_Obra_Images`, `Avances_Obra_Images`, `Facturas_Obra_Files`, `Abonos_Obra_Images`.
2. Plantilla de Google Docs `Plantilla_Proforma` (copia de `Plantilla_Demo`, ya en Drive) (marcas en la sección 5, bot `B_Proforma_PDF`).

### 3.4 Usuarios de prueba

Crear en `Trabajadores` y tener a mano seis cuentas Google reales: **Gerencia**, **Admin**, **Campo asignado a una obra**, **Campo sin asignación**, **Campo inactivo** (`Activo = No`) y **una cuenta que no está en `Trabajadores`**. La sección 14.6 las usa para las pruebas de seguridad.

### 3.5 Datos de prueba

Las pruebas usan los datos demo cargados en `OXYData`. Cada prueba dice el **estado** de la fila que necesita ("una proforma `Borrador` con conceptos y planificación"); los identificadores que se citan son ejemplos y pueden cambiar si se regeneran los datos.

---

## 4. Inventario y orden de construcción

### 4.1 Cómo leer el inventario

La tabla siguiente lista **todas** las acciones y bots del documento, en el orden en que se pueden construir sin que falte nada de lo que cada uno necesita. Se genera a partir de las fichas.

- **Se apoya en:** componentes que deben existir antes (los que la ficha declara en *Depende de* y los que llama en su configuración).
- **Lo invocan o disparan:** qué otros componentes lo llaman o dependen de que exista. Una auxiliar con "—" en esta columna no la llama nadie y debe revisarse.
- Las secciones 5 a 13 se pueden seguir en su orden; el inventario solo anticipa lo que una sección necesita de otra (por ejemplo, los bots de notificación del log antes de los bots programados que los disparan).

### 4.2 Inventario

| N.º | Código | Nombre | App | Tabla | Tipo | Se apoya en | Lo invocan o disparan |
|---|---|---|---|---|---|---|---|
| 1 | PRO-A01 | `A_Enviar` | Gestión | `Proformas` | Acción visible | — | PRO-B02 |
| 2 | PRO-A02 | `A_Rechazar` | Gestión | `Proformas` | Acción visible | — | — |
| 3 | PRO-A03 | `A_Anular` | Gestión | `Proformas` | Acción visible | — | — |
| 4 | PRO-A04 | `A_Eliminar` | Gestión | `Proformas` | Acción visible | — | — |
| 5 | PRO-A05 | `A_Aceptar_Set` | Gestión | `Proformas` | Auxiliar | — | PRO-A07, PRO-A08 |
| 6 | PRO-A06 | `A_Aceptar_CrearObra` | Gestión | `Proformas` | Auxiliar | — | PRO-A07, PRO-A09 |
| 7 | PRO-A07 | `A_Aceptar` | Gestión | `Proformas` | Grupo (botón) | PRO-A05, PRO-A06 | — |
| 8 | PRO-A08 | `A_Aceptar_Completar` | Gestión | `Proformas` | Grupo (botón de reparación) | PRO-A05 | — |
| 9 | PRO-A09 | `A_Aceptar_Reparar_Obra` | Gestión | `Proformas` | Grupo (botón de reparación) | PRO-A06 | — |
| 10 | PRO-A10 | `A_Generar_PDF` | Gestión | `Proformas` | Acción visible | — | PRO-B02 |
| 11 | PRO-A11 | `A_Vencer_Log` | Gestión | `Proformas` | Auxiliar | — | PRO-B01 |
| 12 | PRO-A12 | `A_Vencer_Set` | Gestión | `Proformas` | Auxiliar | — | PRO-B01 |
| 13 | PRO-B01 | `B_Proformas_Vencidas` | Gestión | `Proformas` | Bot programado | PRO-A11, PRO-A12 | — |
| 14 | PRO-B02 | `B_Proforma_PDF` | Gestión | `Proformas` | Bot de evento | PRO-A01, PRO-A10 | — |
| 15 | PRO-B03 | `B_Log_Proformas` | Gestión | `Proformas` | Bot de evento | — | — |
| 16 | PRO-B04 | `B_Notif_Proformas` | Gestión | `Proformas` | Bot de evento | — | — |
| 17 | OBR-A01 | `A_Iniciar` | Gestión | `Obras` | Acción visible | — | — |
| 18 | OBR-A02 | `A_Pausar` | Gestión | `Obras` | Acción visible | — | — |
| 19 | OBR-A03 | `A_Reanudar` | Gestión | `Obras` | Acción visible | — | — |
| 20 | OBR-A04 | `A_Terminar` | Gestión | `Obras` | Acción visible | — | — |
| 21 | OBR-A05 | `A_Cancelar` | Gestión | `Obras` | Acción visible | — | — |
| 22 | OBR-A06 | `A_Cerrar` | Gestión | `Obras` | Acción visible | — | — |
| 23 | OBR-A07 | `A_Cerrar_Con_Saldo` | Gestión | `Obras` | Acción visible | — | — |
| 24 | OBR-A08 | `A_Log_Obra_Atrasada` | Gestión | `Obras` | Auxiliar | — | OBR-B04 |
| 25 | OBR-B01 | `B_Log_Obra_Creada` | Gestión | `Obras` | Bot de evento | — | — |
| 26 | OBR-B02 | `B_Log_Obra_Estado` | Gestión | `Obras` | Bot de evento | — | — |
| 27 | OBR-B03 | `B_Log_Obra_Cerrada` | Gestión | `Obras` | Bot de evento | — | — |
| 28 | LOG-B01 | `B_Notif_Log_Correo` | Gestión | `Log_Eventos` | Bot de evento | — | ABO-B03, ABO-B04, ABO-B05, FAC-B01, FAC-B02, OBR-B04 |
| 29 | OBR-B04 | `B_Obra_Atrasada` | Gestión | `Obras` | Bot programado | LOG-B01, OBR-A08 | — |
| 30 | GAS-A01 | `A_Anular_Gasto` | Gestión y Campo | `Gastos_Obra` | Acción visible | — | — |
| 31 | GAS-A02 | `A_Marcar_Pagado` | Gestión | `Gastos_Obra` | Acción visible | — | — |
| 32 | GAS-B01 | `B_Log_Gasto_Creado` | Gestión y Campo | `Gastos_Obra` | Bot de evento | — | — |
| 33 | GAS-B02 | `B_Log_Gasto_Anulado` | Gestión y Campo | `Gastos_Obra` | Bot de evento | — | — |
| 34 | GAS-B03 | `B_Log_Credito_Fiscal` | Gestión | `Gastos_Obra` | Bot de evento | — | — |
| 35 | GAS-B04 | `B_Log_Gasto_Pagado` | Gestión | `Gastos_Obra` | Bot de evento | — | — |
| 36 | GAS-B05 | `B_Gasto_Sobre_Planificado` | Gestión y Campo | `Gastos_Obra` | Bot de evento | — | — |
| 37 | HOR-A01 | `A_Aprobar_Horas` | Gestión | `Registro_Horas` | Acción visible | — | — |
| 38 | HOR-A02 | `A_Rechazar_Horas` | Gestión | `Registro_Horas` | Acción visible | — | — |
| 39 | HOR-B01 | `B_Log_Horas_Pendientes` | Gestión y Campo | `Registro_Horas` | Bot de evento | — | — |
| 40 | AVA-A01 | `A_Anular_Avance` | Gestión y Campo | `Avances_Obra` | Acción visible | — | — |
| 41 | ABO-A01 | `A_Anular_Abono` | Gestión | `Abonos_Obra` | Acción visible | — | — |
| 42 | ABO-A02 | `A_Cobranza_Marcar` | Gestión | `Obras` | Auxiliar | — | ABO-B03 |
| 43 | ABO-A03 | `A_Cobranza_Log` | Gestión | `Obras` | Auxiliar | — | ABO-B03 |
| 44 | ABO-A04 | `A_Cobranza_Reabrir` | Gestión | `Obras` | Auxiliar | — | ABO-B04 |
| 45 | ABO-A05 | `A_Cobranza_Reabierta_Log` | Gestión | `Obras` | Auxiliar | — | ABO-B04 |
| 46 | ABO-A06 | `A_Recordatorio_Log` | Gestión | `Obras` | Auxiliar | — | ABO-B05 |
| 47 | ABO-B01 | `B_Log_Abono_Creado` | Gestión | `Abonos_Obra` | Bot de evento | — | — |
| 48 | ABO-B02 | `B_Log_Abono_Anulado` | Gestión | `Abonos_Obra` | Bot de evento | — | — |
| 49 | LOG-B02 | `B_Notif_Log_Push` | Gestión | `Log_Eventos` | Bot de evento | — | ABO-B03, ABO-B04, FAC-B02 |
| 50 | ABO-B03 | `B_Cobranza_Completa` | Gestión | `Obras` | Bot programado | ABO-A02, ABO-A03, LOG-B01, LOG-B02 | — |
| 51 | ABO-B04 | `B_Cobranza_Reabierta` | Gestión | `Obras` | Bot programado | ABO-A04, ABO-A05, LOG-B01, LOG-B02 | — |
| 52 | ABO-B05 | `B_Recordatorio_Cobranza` | Gestión | `Obras` | Bot programado | ABO-A06, LOG-B01 | — |
| 53 | FAC-A01 | `A_Anular_Factura` | Gestión | `Facturas_Obra` | Acción visible | — | — |
| 54 | FAC-A02 | `A_Factura_Log_Por_Vencer` | Gestión | `Facturas_Obra` | Auxiliar | — | FAC-B01 |
| 55 | FAC-A03 | `A_Factura_Log_Vencida` | Gestión | `Facturas_Obra` | Auxiliar | — | FAC-B02 |
| 56 | FAC-A04 | `A_Factura_Marcar_Vencida` | Gestión | `Facturas_Obra` | Auxiliar | — | FAC-B02 |
| 57 | FAC-B01 | `B_Factura_Por_Vencer` | Gestión | `Facturas_Obra` | Bot programado | FAC-A02, LOG-B01 | — |
| 58 | FAC-B02 | `B_Factura_Vencida` | Gestión | `Facturas_Obra` | Bot programado | FAC-A03, FAC-A04, LOG-B01, LOG-B02 | — |
| 59 | ALE-A01 | `A_Reconocer_Alerta` | Gestión | `Alertas` | Acción visible | — | — |
| 60 | ALE-A02 | `A_Resolver_Alerta` | Gestión | `Alertas` | Acción visible | — | — |
| 61 | ALE-A03 | `A_Alerta_Sin_Gastos` | Gestión | `Obras` | Auxiliar | — | ALE-B01 |
| 62 | ALE-A04 | `A_Alerta_Sin_Avance` | Gestión | `Obras` | Auxiliar | — | ALE-B02 |
| 63 | ALE-A05 | `A_Alerta_Rezago_Facturacion` | Gestión | `Obras` | Auxiliar | — | ALE-B03 |
| 64 | ALE-B04 | `B_Notif_Alerta` | Gestión | `Alertas` | Bot de evento | — | ALE-B01, ALE-B02, ALE-B03 |
| 65 | ALE-B01 | `B_Obra_Sin_Gastos` | Gestión | `Obras` | Bot programado | ALE-A03, ALE-B04 | — |
| 66 | ALE-B02 | `B_Obra_Sin_Avance` | Gestión | `Obras` | Bot programado | ALE-A04, ALE-B04 | — |
| 67 | ALE-B03 | `B_Rezago_Facturacion` | Gestión | `Obras` | Bot programado | ALE-A05, ALE-B04 | — |

### 4.3 Reglas de construcción

1. Las auxiliares (*Do not display*) se construyen antes que los grupos y bots que las llaman.
2. Un bot programado se crea con la opción **Trigger other bots** activa cuando su ficha lo indica; si no, los bots de notificación no se enterarán de lo que escribe.
3. Los componentes de "Gestión y Campo" se crean **en las dos apps** con la misma configuración (0.5).
4. Al terminar cada sección, marcar sus criterios de salida antes de pasar a la siguiente.

---

## 5. Proformas (solo OXY Gestión)

**Qué se imprime:** la proforma muestra los `Proforma_Conceptos` (concepto y monto sin IGV), luego `IGV_Monto` y `Total_Cobrar`. La `Proforma_Planificacion` (costo interno) **no se imprime**.

**Ciclo de vida:** `Borrador → Enviada → Aceptada | Rechazada | Vencida | Anulada`. Un `Borrador` solo puede pasar a `Enviada` o a `Z-Eliminada` (acción *Eliminar*); nunca a `Anulada`. `Anulada` solo se alcanza desde `Enviada`. `Z-Eliminada` es un estado final: no se edita y no se muestra en las vistas normales (el prefijo `Z` la deja al final al ordenar por estado). Una `Aceptada` crea una obra. Una `Rechazada` no se reabre: se corrige con una proforma nueva que el usuario relaciona a mano con la rechazada.

**Relación entre proformas:** es manual. El sistema no copia datos, no cambia el estado de la proforma previa y no numera revisiones. Cada proforma se digita completa y su `Numero` lo escribe el usuario. Si una proforma es la revisión o la complementaria de otra, el usuario elige la previa y el tipo de relación en el formulario del `Borrador`.

### 5.1 Configuración de columnas

Cada bloque es una columna; cada línea, una propiedad del editor de columnas (cómo se aplica: 2.5). Las propiedades que no aparecen se dejan como están.

#### Tabla `Proformas`

**`Numero`**
- Editable?: `[Estado]="Borrador"`
- Valid if: `AND(NOT(IN([_THIS],SELECT(Proformas[Numero],AND([Proforma_ID]<>[_THISROW].[Proforma_ID],[Estado]<>"Z-Eliminada")))),NOT(OR(CONTAINS([_THIS],"/"),CONTAINS([_THIS],":"),CONTAINS([_THIS],"*"),CONTAINS([_THIS],"?"),CONTAINS([_THIS],"<"),CONTAINS([_THIS],">"),CONTAINS([_THIS],"|"))))`
- Invalid value error: `Numero repetido o con caracteres no permitidos (/ : * ? < > |).`
- Nota: lo digita el usuario al crear la proforma (el sistema no lo genera). El PDF se nombra con el `Numero`, así que no puede repetirse entre proformas vigentes ni llevar caracteres inválidos en nombres de archivo. La barra invertida y las comillas dobles también son inválidas, pero su forma de escribirlas en una fórmula de AppSheet no está confirmada: se prueban en V04 y, si funcionan, se añaden al `OR`.

**`Nombre`**
- Editable?: `[Estado]="Borrador"`

**`Cliente_ID`**
- Editable?: `[Estado]="Borrador"`

**`Contacto_ID`**
- Editable?: `[Estado]="Borrador"`

**`Direccion_Servicio`**
- Editable?: `[Estado]="Borrador"`

**`Fecha_Emision`**
- Editable?: `[Estado]="Borrador"`

**`Fecha_Vigencia`** (Date)
- Require?: `TRUE`
- Editable?: `[Estado]="Borrador"`
- Initial value: `TODAY()+NUMBER(LOOKUP("VIGENCIA_PROFORMA_DIAS","Configuracion","Clave","Valor"))`
- Valid if: `[_THIS]>=[Fecha_Emision]`
- Invalid value error: `La vigencia no puede ser anterior a la fecha de emision.`
- Nota: es responsabilidad del usuario ajustarla en `Borrador`, antes de enviar. `A_Enviar` ya no la fija; el PDF siempre muestra este valor. El bot PRO-B01 vence la proforma cuando pasa.

**`Estado`**
- Editable?: `FALSE`
- Nota: solo cambian el estado las acciones.

**`Fecha_Aceptacion`**
- Show?: `IN([Estado],LIST("Enviada","Aceptada"))`
- Editable?: `[Estado]="Enviada"`

**`Doc_Aceptacion`** (File)
- Show?: `IN([Estado],LIST("Enviada","Aceptada"))`
- Editable?: `[Estado]="Enviada"`
- Nota: orden de compra, correo o carta, en PDF o imagen.

**`Motivo_Rechazo`**
- Show?: `IN([Estado],LIST("Enviada","Rechazada","Reemplazada"))`
- Editable?: `[Estado]="Enviada"`
- Valid if: `ISBLANK([Motivo_Anulacion])`
- Invalid value error: `No se puede indicar motivo de rechazo si la proforma ya tiene motivo de anulacion.`

**`Motivo_Anulacion`**
- Show?: `IN([Estado],LIST("Enviada","Anulada"))`
- Editable?: `[Estado]="Enviada"`
- Valid if: `ISBLANK([Motivo_Rechazo])`
- Invalid value error: `No se puede indicar motivo de anulacion si la proforma ya tiene motivo de rechazo.`

**`Fecha_Rechazo`** (Date)
- Editable?: `FALSE`
- Nota: la fija `A_Rechazar` con `TODAY()`.

**`Fecha_Anulacion`** (Date)
- Editable?: `FALSE`
- Nota: la fija `A_Anular` con `TODAY()`.

**`Eliminada_Por`** (Email)
- Show?: `ISNOTBLANK([Eliminada_Por])`
- Editable?: `FALSE`
- Nota: la fija `A_Eliminar` con `USEREMAIL()`.

**`Fecha_Eliminacion`** (Date)
- Show?: `ISNOTBLANK([Fecha_Eliminacion])`
- Editable?: `FALSE`
- Nota: la fija `A_Eliminar` con `TODAY()`.

**`Doc_Proforma`** (File)
- Show?: `ISNOTBLANK([Doc_Proforma])`
- Editable?: `FALSE`
- Nota: guarda la señal `PENDIENTE|yyyyMMddHHmmss` mientras el bot trabaja y luego la ruta final `Proformas_Files/<Numero>_<Sello>.pdf`. Solo se genera en `Borrador`.

**`Doc_Proforma_Personalizado`** (File, opcional)
- Show?: `OR(ISNOTBLANK([Doc_Proforma_Personalizado]),[Estado]="Borrador")`
- Editable?: `[Estado]="Borrador"`
- Nota: copia propia que sube el usuario. Al enviar queda bloqueada **solo en pantalla** (no es seguridad: un bot o una edición directa en `OXYData` la puede cambiar). Si existe, es el documento oficial.

**`Doc_Oficial`** (virtual, File)
- App formula: `IF(ISNOTBLANK([Doc_Proforma_Personalizado]),[Doc_Proforma_Personalizado],[Doc_Proforma])`
- Nota: el documento oficial de la proforma: el personalizado si existe; si no, el PDF generado. Se usa en las vistas de detalle. ⚠ V23

**`Proforma_Previa_ID`** (Ref a `Proformas`, opcional)
- Editable?: `[Estado]="Borrador"`
- Valid if: `SELECT(Proformas[Proforma_ID],AND([Proforma_ID]<>[_THISROW].[Proforma_ID],[Estado]<>"Z-Eliminada"))`
- Invalid value error: `Seleccione otra proforma (no la misma ni una eliminada).`
- Nota: la lista excluye la propia proforma y las `Z-Eliminada`; no valida nada más (la relación es decisión del usuario) ⚠ V04

**`Tipo_Relacion`** (Enum: `Revision`, `Complementaria`)
- Require?: `ISNOTBLANK([Proforma_Previa_ID])`
- Editable?: `[Estado]="Borrador"`
- Nota: sin previa queda vacío. Solo `Complementaria` tiene efecto en el sistema: `A_Aceptar_CrearObra` liga la obra nueva a la obra de la previa. `Revision` es informativa.

**`Total_Relacionadas`** (virtual, Number)
- App formula: `COUNT(SELECT(Proformas[Proforma_ID],AND([Proforma_Previa_ID]=[_THISROW],[Estado]<>"Z-Eliminada")))`
- Nota: cuenta las proformas no eliminadas que apuntan a esta; no recorre cadenas.

**`Precio_Neto`** (virtual, Price)
- App formula: `SUM(SELECT(Proforma_Conceptos[Monto_Sin_IGV],[Proforma_ID]=[_THISROW]))`
- Nota: el filtro por proforma es obligatorio; sin él se sumarían las líneas de todas las proformas.

**`Costo_Planificado`** (virtual, Price)
- App formula: `SUM(SELECT(Proforma_Planificacion[Costo_Imputable],[Proforma_ID]=[_THISROW]))`
- Nota: mismo filtro obligatorio que en `Precio_Neto`.

**Datos de OXY para el PDF.** Las diez columnas siguientes son virtuales de `Proformas`, de solo lectura, y alimentan la plantilla del PDF. Cada una lee una columna de la fila única de `Compania`, así que un cambio allí se refleja en el siguiente PDF que se genere.

**`Empresa_Nombre_Comercial`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Nombre_Comercial")`

**`Empresa_Razon_Social`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Razon_Social")`

**`Empresa_RUC`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","RUC")`

**`Empresa_Direccion_Fiscal`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Direccion_Fiscal")`

**`Empresa_Telefono`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Telefono")`

**`Empresa_Email`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Email")`

**`Empresa_Web`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Web")`
- Nota: puede estar vacía.

**`Proforma_Condiciones`** (virtual, LongText)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Condiciones_Proforma")`

**`Proforma_Cuentas_Bancarias`** (virtual, LongText)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Cuentas_Bancarias")`

**`Proforma_Firma_Nombre`** (virtual, Text)
- App formula: `LOOKUP("OXY","Compania","Compania_ID","Firma_Nombre")`

**Acción de sistema *Edit* de `Proformas`**
- Only if this condition is true: `IN([Estado],LIST("Borrador","Enviada"))`

#### Tabla `Proforma_Conceptos`

**`Orden`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Concepto`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Monto_Sin_IGV`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

#### Tabla `Proforma_Planificacion`

La planificación usa las mismas columnas que el gasto, para comparar plan y real sin conversiones. No tiene fechas de pago.

**`Tipo_Costo_ID`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Descripcion`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Cantidad`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Unidad`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Costo_Unitario`**
- Editable?: `[Proforma_ID].[Estado]="Borrador"`
- Nota: siempre **sin IGV**. Si la cotización del proveedor trae IGV, dividirla entre 1.18 antes de digitarla.

**`Tiene_IGV`**
- Initial value: `LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Aplica_IGV_Defecto")`
- Editable?: `[Proforma_ID].[Estado]="Borrador"`

**`Es_Credito_Fiscal`**
- Initial value: `IF([Tiene_IGV]="Si",LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Credito_Fiscal_Defecto"),"No")`
- Editable?: `[Proforma_ID].[Estado]="Borrador"`
- Valid if: `OR([_THIS]="No",[Tiene_IGV]="Si")`
- Nota: si el planificador cambia `Tiene_IGV`, el valor inicial no se recalcula; el `Valid if` obliga a corregir el crédito.

#### Slices y vistas

**Slice `S_Proformas_Activas`**
- Source table: `Proformas`
- Row filter condition: `[Estado]<>"Z-Eliminada"`
- Nota: la lista normal de proformas usa este slice.

**Slice `S_Proformas_Eliminadas`**
- Source table: `Proformas`
- Row filter condition: `[Estado]="Z-Eliminada"`
- Nota: una vista aparte para auditar lo eliminado, con `Numero`, `Nombre`, `Eliminada_Por` y `Fecha_Eliminacion`.

### 5.2 Preparación

1. Estructura de `Proformas`, `Proforma_Conceptos` y `Proforma_Planificacion` regenerada desde `OXYData` (incluye `Doc_Proforma`, `Doc_Proforma_Personalizado`, `Fecha_Rechazo`, `Fecha_Anulacion`, `Eliminada_Por` y `Fecha_Eliminacion`).
2. Configuración de columnas de 5.1 aplicada, y las virtuales `Total_Relacionadas`, `Doc_Oficial` y las diez de datos de OXY para el PDF creadas.
3. Permisos de las tres tablas: *Adds* y *Updates*, sin *Deletes* (una proforma no se borra: se pasa a `Z-Eliminada`).
4. La tabla `Compania` agregada a la app (solo *Updates*) y su fila `OXY` con los datos reales, y `Plantilla_Proforma` (Google Docs) en Drive (ver `B_Proforma_PDF`).
5. Orden de construcción: auxiliares PRO-A05, PRO-A06, PRO-A11 y PRO-A12; luego las acciones visibles y los grupos (PRO-A01 a PRO-A04, PRO-A07 a PRO-A10; `A_Generar_PDF` antes que `A_Enviar`); al final los bots PRO-B01 a PRO-B04.

### 5.3 Detección de datos incompletos

Crear estos slices en `Proformas` (visibles solo para Gestión, en una vista de control). Si aparece una fila, hay una operación a medias (procedimientos en la sección 16.4):

- `S_Proformas_Inconsistentes`: `OR(AND([Estado]="Aceptada",ISBLANK([Obra_Generada])),AND([Estado]="Enviada",ISNOTBLANK([Obra_Generada])))`
- `S_Proformas_Sin_PDF`: `AND(IN([Estado],LIST("Enviada","Aceptada","Rechazada","Vencida")),OR(ISBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)="PENDIENTE"))`

### 5.4 Acciones

#### PRO-A01 · `A_Enviar` · Gestión · Proformas · Acción visible
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Enviar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Enviada"`
  - `Fecha_Envio` = `TODAY()`
  - Nota: ya no genera el PDF ni fija `Fecha_Vigencia`; solo cambia el estado.
- **Only if this condition is true:** `AND([Estado]="Borrador",COUNT(SELECT(Proforma_Conceptos[Concepto_ID],[Proforma_ID]=[_THISROW].[Proforma_ID]))>0,COUNT(SELECT(Proforma_Planificacion[Planif_ID],[Proforma_ID]=[_THISROW].[Proforma_ID]))>0,ISNOTBLANK([Cliente_ID]),ISNOTBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)<>"PENDIENTE",ISNOTBLANK([Fecha_Vigencia]),[Fecha_Vigencia]>=TODAY())`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `IF([Aviso_Margen],"El margen planificado es menor al mínimo. ","")&"¿Enviar la proforma "&[Numero]&"? El detalle ya no se podrá editar. Verifique que el PDF esté generado con los últimos cambios."` ⚠ V05
- **Position:** Prominent
- **Display name:** Enviar
- **Idempotencia:** tras ejecutarse el estado deja de ser `Borrador` y el botón desaparece.
- **Prueba +:** con una proforma `Borrador` con conceptos, planificación, `Fecha_Vigencia` vigente y el PDF ya generado con PRO-A10 (por ejemplo `PRF-019`): aparece, pide confirmación (con el recordatorio del PDF), queda `Enviada` con `Fecha_Envio`. Efectos laterales: PRO-B03 escribe el log y PRO-B04 envía el correo interno; PRO-B02 **no** se dispara. Con `Proforma_Previa_ID` asignada, la proforma previa **no cambia de estado**.
- **Prueba −:** un `Borrador` sin conceptos, sin planificación o sin cliente: el botón no aparece. Un `Borrador` con `Aviso_Margen` verdadero: el mensaje de confirmación es el de margen bajo. Un `Borrador` sin PDF generado, con `Doc_Proforma` en `PENDIENTE|...`, o con `Fecha_Vigencia` vacía o vencida: no aparece. Una proforma que no está en `Borrador`: no aparece. Subir un `Doc_Proforma_Personalizado` no es requisito.
- **Repetición:** la proforma ya `Enviada` no muestra el botón.
- **Si falla:** si el botón no aparece, revisar cuál de las condiciones falta (PDF, vigencia, conceptos). Si el mensaje de confirmación no cambia con `Aviso_Margen`, ver V05. Comprobar que existe la clave `VIGENCIA_PROFORMA_DIAS` en `Configuracion` y que su valor es un entero (se usa en el valor inicial de `Fecha_Vigencia`).

#### PRO-A02 · `A_Rechazar` · Gestión · Proformas · Acción visible
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Rechazar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Rechazada"`
  - `Fecha_Rechazo` = `TODAY()`
- **Only if this condition is true:** `AND([Estado]="Enviada",ISNOTBLANK([Motivo_Rechazo]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Marcar la proforma como rechazada por el cliente? No podrá editarse; para corregirla cree una proforma nueva y relaciónela con esta.`
- **Position:** Prominent
- **Display name:** Rechazar
- **Idempotencia:** después del cambio el estado ya no es `Enviada`.
- **Prueba +:** con una proforma `Enviada`: el botón aparece solo después de guardar `Motivo_Rechazo`. Resultado: `Rechazada`, `Fecha_Rechazo` = hoy y un evento `PROFORMA_RECHAZADA` en `Log_Eventos`.
- **Prueba −:** `Enviada` sin motivo, o cualquier otro estado: no aparece.
- **Repetición:** ya `Rechazada`: no aparece.
- **Si falla:** si no hay evento en el log, revisar PRO-B03.

#### PRO-A03 · `A_Anular` · Gestión · Proformas · Acción visible
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Anular`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulada"`
  - `Fecha_Anulacion` = `TODAY()`
- **Only if this condition is true:** `AND([Estado]="Enviada",ISNOTBLANK([Motivo_Anulacion]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular la proforma? Esta acción no se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** después del cambio el estado ya no es `Enviada`.
- **Prueba +:** una proforma `Enviada` con `Motivo_Anulacion`: queda `Anulada`, con `Fecha_Anulacion` = hoy y evento `PROFORMA_ANULADA`.
- **Prueba −:** sin motivo o en otro estado: no aparece. Un `Borrador` no se anula: se elimina con PRO-A04.
- **Repetición:** ya `Anulada`: no aparece.
- **Si falla:** igual que PRO-A02.

#### PRO-A04 · `A_Eliminar` · Gestión · Proformas · Acción visible
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Eliminar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Z-Eliminada"`
  - `Eliminada_Por` = `USEREMAIL()`
  - `Fecha_Eliminacion` = `TODAY()`
  - Nota: No se pide motivo.
- **Only if this condition is true:** `AND([Estado]="Borrador",AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `"¿Eliminar la proforma "&[Numero]&"? Dejará de mostrarse y no se puede deshacer."`
- **Position:** Prominent
- **Display name:** Eliminar
- **Idempotencia:** después del cambio el estado ya no es `Borrador` y el botón desaparece.
- **Prueba +:** con una proforma `Borrador` (por ejemplo `PRF-022`) y una cuenta de Gestión: aparece, pide confirmación y queda `Z-Eliminada` con `Eliminada_Por` = la cuenta y `Fecha_Eliminacion` = hoy; PRO-B03 escribe `PROFORMA_ELIMINADA`; no sale correo. Sale de la lista normal y aparece en la vista de eliminadas. Si era la previa de otra proforma, deja de contar en el `Total_Relacionadas` de esa previa.
- **Prueba −:** en una proforma `Enviada`, `Aceptada`, `Rechazada`, `Vencida` o `Anulada`: no aparece. Con una cuenta de Campo: la app no la ofrece (las proformas no están en OXY Campo).
- **Repetición:** ya `Z-Eliminada`: no aparece.
- **Si falla:** si el evento no queda en `Log_Eventos`, revisar PRO-B03. Las líneas de conceptos y planificación de la proforma eliminada permanecen en `OXYData`; no se tocan.

#### PRO-A05 · `A_Aceptar_Set` · Gestión · Proformas · Auxiliar
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_Set`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Aceptada"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** poner el mismo estado dos veces no cambia nada.
- **Prueba +:** se verifica con PRO-A07.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** no aplica.
- **Si falla:** ver PRO-A07 y PRO-A08.

#### PRO-A06 · `A_Aceptar_CrearObra` · Gestión · Proformas · Auxiliar
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_CrearObra`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Obras`
- **Set these columns:**
  - `Obra_ID` = `UNIQUEID()`
  - `Codigo` = `[Numero]&" - "&[Nombre]`
  - `Proforma_ID` = `[Proforma_ID]`
  - `Cliente_ID` = `[Cliente_ID]`
  - `Obra_Principal_ID` = `IF(AND([Tipo_Relacion]="Complementaria",ISNOTBLANK([Proforma_Previa_ID])),LOOKUP([Proforma_Previa_ID],"Obras","Proforma_ID","Obra_ID"),"")`. Depende de que el usuario haya asignado a mano la previa y el tipo `Complementaria`
  - Nota: si no lo hizo, la obra nace como principal.
  - `Responsable_ID` = `LOOKUP([Creado_Por],"Trabajadores","Email","Trabajador_ID")`
  - Nota: (Gestión lo cambia después)
  - `Estado` = `"Por iniciar"`
  - `Precio_Neto_Base` = `[Precio_Neto]`
  - `IGV_Base` = `[IGV_Monto]`
  - `Total_Cobrar_Base` = `[Total_Cobrar]`
  - `Costo_Planificado_Base` = `[Costo_Planificado]`
  - `Notificado_Cobro_Completo` = `"No"`
  - `Creado_En` = `NOW()`
- **Only if this condition is true:** (dejar vacío) (la condición está en los grupos que la llaman)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** esta acción **no** comprueba si ya existe una obra; lo hacen PRO-A07 y PRO-A09 con `ISBLANK([Obra_Generada])`. No exponerla en ningún botón.
- **Prueba +:** se verifica con PRO-A07.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ejecutarla dos veces crea dos obras: por eso solo la llaman los grupos con su condición.
- **Si falla:** la planificación sigue ligada a la proforma congelada: no se copia a la obra; solo se guardan los totales. Si algún total sale en blanco, revisar las virtuales de la proforma.

#### PRO-A07 · `A_Aceptar` · Gestión · Proformas · Grupo (botón)
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** PRO-A05, PRO-A06
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_CrearObra`
  2. `A_Aceptar_Set`
- **Nota:** La obra se crea **antes** de cambiar el estado: si falla la creación, la proforma sigue `Enviada` y el botón sigue disponible para reintentar.
- **Only if this condition is true:** `AND([Estado]="Enviada",ISNOTBLANK([Fecha_Aceptacion]),ISNOTBLANK([Doc_Aceptacion]),ISBLANK([Obra_Generada]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Aceptar la proforma y crear la obra?`
- **Position:** Prominent
- **Display name:** Aceptar
- **Idempotencia:** la condición `ISBLANK([Obra_Generada])` oculta el botón en cuanto existe la obra. Si el paso 1 se completa y el paso 2 falla, la proforma queda `Enviada` con obra: PRO-A08 completa el cambio de estado.
- **Prueba +:** una `Enviada` con `Fecha_Aceptacion` y `Doc_Aceptacion`: queda `Aceptada` y existe una obra `Por iniciar` con los totales congelados; evento `PROFORMA_ACEPTADA`.
- **Prueba −:** sin `Fecha_Aceptacion` o sin `Doc_Aceptacion`: el botón no aparece. Una `Enviada` que ya tiene obra: no aparece.
- **Repetición:** el botón desaparece tras la primera ejecución; no se crea una segunda obra.
- **Si falla:** revisar `S_Proformas_Inconsistentes`. Una `Enviada` con obra se completa con PRO-A08; una `Aceptada` sin obra, con PRO-A09.

#### PRO-A08 · `A_Aceptar_Completar` · Gestión · Proformas · Grupo (botón de reparación)
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** PRO-A05
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_Completar`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_Set`
- **Only if this condition is true:** `AND(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Estado]="Enviada",ISNOTBLANK([Obra_Generada]),ISNOTBLANK([Fecha_Aceptacion]),ISNOTBLANK([Doc_Aceptacion]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `La obra ya existe pero la proforma sigue Enviada. ¿Completar la aceptación?`
- **Position:** Prominent
- **Display name:** Completar aceptación
- **Idempotencia:** tras ejecutarse el estado es `Aceptada` y el botón desaparece. No crea filas.
- **Prueba +:** provocar el fallo poniendo una `Enviada` con obra (crear la obra a mano desde `OXYData` y ligarla a la proforma): el botón aparece; al ejecutarlo la proforma queda `Aceptada` y no hay segunda obra.
- **Prueba −:** una `Enviada` sin obra: no aparece.
- **Repetición:** ya `Aceptada`: no aparece.
- **Si falla:** comprobar que `Obra_Generada` resuelve la obra de esa proforma.

#### PRO-A09 · `A_Aceptar_Reparar_Obra` · Gestión · Proformas · Grupo (botón de reparación)
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** PRO-A06
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_Reparar_Obra`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_CrearObra`
- **Only if this condition is true:** `AND(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Estado]="Aceptada",ISBLANK([Obra_Generada]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `La proforma está Aceptada pero no tiene obra. ¿Crear la obra ahora?`
- **Position:** Prominent
- **Display name:** Crear obra faltante
- **Idempotencia:** `ISBLANK([Obra_Generada])` oculta el botón en cuanto la obra existe.
- **Prueba +:** poner a mano una proforma en `Aceptada` sin obra: aparece; al ejecutarlo existe una obra `Por iniciar` con los totales congelados.
- **Prueba −:** una `Aceptada` con obra: no aparece.
- **Repetición:** el botón desaparece; no se crea otra obra.
- **Si falla:** ver PRO-A06.

#### PRO-A10 · `A_Generar_PDF` · Gestión · Proformas · Acción visible
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Generar_PDF`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Doc_Proforma` = `"PENDIENTE|"&TEXT(NOW(),"yyyyMMddHHmmss")`
  - Nota: la señal lleva el sello de fecha y hora, así que es distinta en cada pulsación; eso dispara a PRO-B02 aunque el valor anterior fuera otra señal. El mismo sello da nombre al archivo.
- **Only if this condition is true:** `AND(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Estado]="Borrador",OR(ISBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)<>"PENDIENTE"))`
- **Needs confirmation?:** No
- **Position:** Prominent
- **Display name:** Generar PDF
- **Idempotencia:** se puede pulsar las veces que haga falta mientras sea `Borrador`; cada pulsación crea un archivo nuevo con otro sello y `Doc_Proforma` apunta al último. Los anteriores quedan en Drive sin usar.
- **Prueba +:** en un `Borrador`: al pulsarlo, `Doc_Proforma` pasa a `PENDIENTE|<Sello>` y poco después a `Proformas_Files/<Numero>_<Sello>.pdf`. Cambiar un concepto y pulsarlo otra vez genera un segundo archivo con el cambio.
- **Prueba −:** una proforma `Enviada`, `Aceptada`, `Rechazada`, `Vencida`, `Anulada` o `Z-Eliminada`: no aparece (el PDF no se regenera después de enviar). Un usuario de Campo: no aparece.
- **Repetición:** mientras el valor empiece por `PENDIENTE` el botón no aparece; al terminar el bot reaparece.
- **Si falla:** si el valor se queda en `PENDIENTE|...`, el bot no corrió: revisar `Monitor` de PRO-B02. Para reintentar hay que vaciar `Doc_Proforma` en `OXYData` (el botón no aparece mientras haya una señal pendiente).

#### PRO-A11 · `A_Vencer_Log` · Gestión · Proformas · Auxiliar
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Vencer_Log`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"PROFORMA_VENCIDA|"&[Proforma_ID]`
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"PROFORMA_VENCIDA"`
  - `Tabla` = `"Proformas"`
  - `Registro_ID` = `[Proforma_ID]`
  - `Obra_ID` = `""`
  - `Usuario` = `""`
  - `Resumen` = `"Proforma "&[Numero]&" - Vencida"`
  - `Procesado` = `"Si"`
  - `Procesado_En` = `NOW()`
  - `Canal` = `"Correo"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` es único por proforma; PRO-B01 solo la llama para proformas sin ese evento.
- **Prueba +:** se verifica con PRO-B01.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver PRO-B01.
- **Si falla:** comprobar que `Log_Eventos` permite *Adds* en la app.

#### PRO-A12 · `A_Vencer_Set` · Gestión · Proformas · Auxiliar
- **App · Tabla:** OXY Gestión · `Proformas`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Vencer_Set`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Vencida"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** poner el mismo estado dos veces no cambia nada.
- **Prueba +:** se verifica con PRO-B01.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver PRO-B01.
- **Si falla:** ver PRO-B01.

### 5.5 Bots

#### PRO-B01 · `B_Proformas_Vencidas` · Gestión · Proformas · Bot programado
- **App · Tabla:** OXY Gestión · `Proformas`
- **Event:**
  - Event type: Scheduled
  - Schedule: Daily
  - Time: 06:00
  - Time zone: America/Lima
- **Depende de:** PRO-A11, PRO-A12
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Proformas`
     - Referenced Rows: `SELECT(Proformas[Proforma_ID],AND([Estado]="Enviada",[Fecha_Vigencia]<TODAY(),ISBLANK(LOOKUP("PROFORMA_VENCIDA|"&[Proforma_ID],"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Vencer_Log`
  2. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Proformas`
     - Referenced Rows: `SELECT(Proformas[Proforma_ID],AND([Estado]="Enviada",[Fecha_Vigencia]<TODAY()))`
     - Referenced Action: `A_Vencer_Set` ⚠ V19
  Nota: Activar **Trigger other bots** para que PRO-B04 envíe el correo interno al pasar a `Vencida` (⚠ V10).
- **Datos que escribe:** `Log_Eventos` (evento `PROFORMA_VENCIDA`) y `Proformas.Estado`.
- **Idempotencia:** primero se registra el evento (una sola vez por proforma, por su `Evento_ID`) y después se cambia el estado. Si la corrida se corta entre los dos pasos, la siguiente completa el estado sin duplicar el log.
- **Límites del plan Core:** una ejecución diaria; el correo de PRO-B04 cuenta contra la cuota de correos.
- **Prueba +:** poner `Fecha_Vigencia` en una fecha pasada en una proforma `Enviada` y ejecutar el bot a mano: pasa a `Vencida`, con un evento `PROFORMA_VENCIDA` en el log.
- **Prueba −:** una `Enviada` con vigencia futura, o una proforma de otro estado con vigencia pasada: no cambia.
- **Repetición:** ejecutar el bot dos veces seguidas no crea un segundo evento ni cambia nada.
- **Si falla:** en `Monitor`, abrir la ejecución y ver en qué paso quedó. Si el paso 1 corrió y el 2 no, ejecutar el bot otra vez.

#### PRO-B02 · `B_Proforma_PDF` · Gestión · Proformas · Bot de evento
- **App · Tabla:** OXY Gestión · `Proformas`
- **Event:**
  - Event type: Data change
  - Table: `Proformas`
  - Data change type: Updates only
  - Condition: `AND(LEFT([_THISROW_AFTER].[Doc_Proforma],9)="PENDIENTE",[_THISROW_AFTER].[Doc_Proforma]<>[_THISROW_BEFORE].[Doc_Proforma])`
- **Depende de:** PRO-A10 (se dispara al generar; ya no depende de PRO-A01)
- **Process:**
  1. Step type: Run a data action → Create a new file ⚠ V06
     - Template: `Plantilla_Proforma` (Google Docs en Drive)
     - File type: PDF
     - Folder path: `Proformas_Files`
     - File name prefix: `<<[Numero]>>_<<MID([Doc_Proforma],11,14)>>`
     - Disable timestamp: activado (el sello lo aporta la señal de `Doc_Proforma`, para poder predecir la ruta)
  2. Step type: Run a data action → Set row values
     - Table: (esta fila)
     - `Doc_Proforma` = `"Proformas_Files/"&[Numero]&"_"&MID([Doc_Proforma],11,14)&".pdf"`
  Nota: **No hay paso de correo: el PDF no se envía al cliente; solo se archiva.**
- **Plantilla `Plantilla_Proforma`:** un Google Doc con estas marcas de AppSheet: `<<[Numero]>>`, `<<[Nombre]>>`, `<<[Fecha_Emision]>>`, `<<[Fecha_Vigencia]>>`, `<<[Direccion_Servicio]>>`, el cliente y el contacto por referencia (`<<[Cliente_ID].[Razon_Social]>>`, `<<[Contacto_ID].[Nombre]>>`), la tabla de conceptos entre `<<Start: [Related Proforma_Conceptoss]>>` y `<<End>>` con `<<[Concepto]>>` y `<<[Monto_Sin_IGV]>>`, y al final `<<[Precio_Neto]>>`, `<<[IGV_Monto]>>` y `<<[Total_Cobrar]>>`. Los datos de OXY: `<<[Empresa_Nombre_Comercial]>>`, `<<[Empresa_Razon_Social]>>`, `<<[Empresa_RUC]>>`, `<<[Empresa_Direccion_Fiscal]>>`, `<<[Empresa_Telefono]>>`, `<<[Empresa_Email]>>` y `<<[Empresa_Web]>>` en el encabezado y el pie; y al final `<<[Proforma_Condiciones]>>`, `<<[Proforma_Cuentas_Bancarias]>>` y `<<[Proforma_Firma_Nombre]>>`. La planificación no se imprime. Verificar el nombre exacto de la columna inversa `Related ...` en el editor (⚠ V11).
- **Datos que escribe:** el archivo PDF en Drive y `Doc_Proforma`. Cada generación crea un archivo nuevo (nombre con `Numero` y sello); nada se sobrescribe.
- **Idempotencia:** la condición solo se cumple cuando `Doc_Proforma` cambia a una señal `PENDIENTE|...`; el segundo paso la reemplaza por una ruta, que no empieza por `PENDIENTE`, y no vuelve a disparar el bot.
- **Límites del plan Core:** verificar que *Create a new file* está disponible en Core y su cuota (⚠ V06).
- **Prueba +:** al pulsar *Generar PDF* (PRO-A10) en un `Borrador` aparece `Proformas_Files/<Numero>_<Sello>.pdf` en Drive, `Doc_Proforma` apunta a él y el PDF muestra `Fecha_Vigencia`, conceptos, subtotal, IGV y total, sin la planificación. No sale ningún correo al cliente. La ruta guardada abre desde la app con una cuenta de Gestión.
- **Prueba −:** editar otra columna, subir un `Doc_Proforma_Personalizado` o enviar la proforma no genera un PDF nuevo.
- **Repetición:** cada pulsación de PRO-A10 genera otro archivo con otro sello; los anteriores quedan en Drive y se pueden borrar a mano. `Doc_Proforma` apunta siempre al último.
- **Si falla:** ver el árbol de diagnóstico de la sección 16.1. Casos de desincronización: si `Doc_Proforma` se queda en `PENDIENTE|...` en un `Borrador`, vaciar el valor en `OXYData` y pulsar PRO-A10. Una proforma ya enviada sin PDF válido no se puede regenerar; se corrige a mano en `OXYData`.

#### PRO-B03 · `B_Log_Proformas` · Gestión · Proformas · Bot de evento
- **App · Tabla:** OXY Gestión · `Proformas`
- **Event:**
  - Event type: Data change
  - Table: `Proformas`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]<>[_THISROW_AFTER].[Estado],IN([_THISROW_AFTER].[Estado],LIST("Enviada","Aceptada","Rechazada","Anulada","Z-Eliminada")))`
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `SWITCH([_THISROW_AFTER].[Estado],"Enviada","PROFORMA_ENVIADA","Aceptada","PROFORMA_ACEPTADA","Rechazada","PROFORMA_RECHAZADA","Anulada","PROFORMA_ANULADA","Z-Eliminada","PROFORMA_ELIMINADA")`
     - `Tabla` = `"Proformas"`
     - `Registro_ID` = `[_THISROW_AFTER].[Proforma_ID]`
     - `Obra_ID` = `""`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Proforma "&[_THISROW_AFTER].[Numero]&" - "&[_THISROW_AFTER].[Estado]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `IF(IN([_THISROW_AFTER].[Estado],LIST("Enviada","Aceptada","Rechazada")),"Correo","")`
  Nota: `Vencida` no se registra aquí: lo hace PRO-A11 dentro de PRO-B01.
- **Datos que escribe:** una fila en `Log_Eventos` por cada cambio de estado.
- **Idempotencia:** la condición exige que el estado **cambie**; una actualización que no lo cambia no genera evento. Reenviar el mismo valor no duplica.
- **Límites del plan Core:** una ejecución por cambio de estado.
- **Prueba +:** cada una de PRO-A01, PRO-A02, PRO-A03, PRO-A04 y PRO-A07 deja una fila nueva en `Log_Eventos` con el tipo correcto, con `PROFORMA_ELIMINADA` para PRO-A04.
- **Prueba −:** editar `Motivo_Rechazo` sin cambiar el estado, o que el bot PRO-B02 actualice `Doc_Proforma`: no deja evento.
- **Repetición:** repetir la acción no es posible (el botón desaparece); si se fuerza a mano el mismo estado, no hay evento.
- **Si falla:** en `Monitor`, comprobar si el evento se disparó, si la condición fue falsa o si falló la escritura en `Log_Eventos`.

#### PRO-B04 · `B_Notif_Proformas` · Gestión · Proformas · Bot de evento
- **App · Tabla:** OXY Gestión · `Proformas`
- **Event:**
  - Event type: Data change
  - Table: `Proformas`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]<>[_THISROW_AFTER].[Estado],IN([_THISROW_AFTER].[Estado],LIST("Enviada","Aceptada","Rechazada","Vencida")))`
- **Depende de:** —
- **Process:**
  1. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))` ⚠ V03
     - Subject: `Proforma <<[Numero]>>: <<[Estado]>>`
     - Body: texto con `<<[Etiqueta]>>`, el cliente (`<<[Cliente_ID].[Razon_Social]>>`) y `<<[Total_Cobrar]>>`. Es un aviso **interno**; nunca va al cliente.
- **Datos que escribe:** ninguno (solo envía correo).
- **Idempotencia:** un correo por cambio de estado.
- **Límites del plan Core:** cuota diaria de correos; el aviso de `Vencida` depende de que PRO-B01 tenga activo *Trigger other bots* (⚠ V10). Si V10 falla, quitar `Vencida` de la condición: ese caso queda cubierto por la alerta de proforma sin respuesta del Dashboard.
- **Prueba +:** enviar una proforma (PRO-A01) genera un correo a todos los usuarios activos Admin y Gerencia.
- **Prueba −:** anular o eliminar una proforma no envía correo.
- **Repetición:** repetir la acción no es posible; no hay segundo correo.
- **Si falla:** si el bot se ejecutó pero no llegó el correo, ver la sección 13.5 (diferencia entre "el proceso corrió" y "el destinatario lo recibió").

### 5.6 Criterios de salida de Proformas

Antes de pasar a la sección 6:

- [ ] Los dos slices de 5.3 existen y devuelven cero filas con los datos demo.
- [ ] Todas las acciones PRO-A01 a PRO-A12 y los bots PRO-B01 a PRO-B04 guardan sin errores.
- [ ] Prueba de punta a punta de Proformas (sección 15.3, escenarios E2E-1 a E2E-6) ejecutada con resultado registrado.
- [ ] V04, V05, V06, V10, V11 y V19 cerradas en el registro de validaciones.

---
## 6. Obras (acciones solo en OXY Gestión; OXY Campo las ve en lectura)

Cada obra nace de una proforma aceptada (PRO-A06) y concentra, como columnas virtuales, costos, cobranza, facturación, avance y KPIs. Sus fórmulas están en el `_Diccionario`.

### 6.1 Configuración de columnas

Cada bloque es una columna; cada línea, una propiedad del editor de columnas (2.5).

#### Tabla `Obras`

**`Estado`**
- Editable?: `FALSE`
- Nota: solo cambia con las acciones de la sección 6.3.

**Columnas virtuales de `Obras`.** Crear una por línea, con el tipo y la fórmula de su fila en el `_Diccionario`:

1. `Total_Gastos`
2. `Total_Personal`
3. `Costo_Real`
4. `Consumo_Pct`
5. `Margen_Real_Parcial`
6. `IGV_No_Recuperable`
7. `Total_Abonos`
8. `Saldo`
9. `Estado_Cobranza`
10. `Cobranza_Completa`
11. `Flujo_Caja`
12. `Por_Pagar`
13. `Flujo_Caja_Proyectado`
14. `Avance_Actual`
15. `Valor_Ganado`
16. `CPI`
17. `Proyeccion_Costo_Final`
18. `Margen_Proyectado`
19. `Facturado_Acum`
20. `Por_Facturar`
21. `Pct_Facturado`
22. `Facturado_Sin_Cobrar`
23. `Cartera_Vencida`
24. `Rezago_Facturacion_pp`
25. `Dias_Sin_Gastos`

Qué significan algunas:

- `Flujo_Caja` = abonos − gastos con `Fecha_Pago_Real` − personal.
- `Por_Pagar` = gastos vigentes sin `Fecha_Pago_Real` (base + IGV).
- `Flujo_Caja_Proyectado` = `Flujo_Caja − Por_Pagar`.
- El costo (`Total_Gastos`, `Costo_Real`, CPI, valor ganado) se reconoce al registrar el gasto; la caja, al pagarlo.
- `Cobranza_Completa` es verdadera cuando el saldo está dentro de `TOLERANCIA_COBRANZA`, que se lee con `DECIMAL(LOOKUP("TOLERANCIA_COBRANZA","Configuracion","Clave","Valor"))`.

#### Tablas hijas bloqueadas por el estado de la obra

La columna `Obra_ID` de estas seis tablas lleva la misma regla. Se evalúa sobre las obras, no sobre el `Estado` de la fila hija.

**`Obra_ID` en `Gastos_Obra`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Obra_ID` en `Abonos_Obra`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Obra_ID` en `Facturas_Obra`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Obra_ID` en `Avances_Obra`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Obra_ID` en `Asignaciones_Obra`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Obra_ID` en `Registro_Horas`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

### 6.2 Preparación

1. Estructura de `Obras` y virtuales creadas; `Valid if` de `Obra_ID` en las seis tablas hijas aplicado.
2. `Estado` con `Editable?` = `FALSE`. Sin *Deletes* en `Obras`.
3. Orden de construcción: OBR-A01 a OBR-A08; luego los bots OBR-B01 a OBR-B04.

### 6.3 Acciones

#### OBR-A01 · `A_Iniciar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Iniciar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"En ejecucion"`
  - `Fecha_Inicio` = `TODAY()`
- **Only if this condition is true:** `[Estado]="Por iniciar"`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Iniciar la obra con fecha de hoy?`
- **Position:** Prominent
- **Display name:** Iniciar
- **Idempotencia:** el estado deja de ser `Por iniciar`.
- **Prueba +:** una obra `Por iniciar`: queda `En ejecucion` con `Fecha_Inicio` = hoy y evento `OBRA_ESTADO_CAMBIADO`.
- **Prueba −:** una obra en cualquier otro estado: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** si no hay evento en el log, ver OBR-B02.

#### OBR-A02 · `A_Pausar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Pausar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Pausada"`
- **Only if this condition is true:** `[Estado]="En ejecucion"`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Pausar la obra?`
- **Position:** Prominent
- **Display name:** Pausar
- **Idempotencia:** el estado deja de ser `En ejecucion`.
- **Prueba +:** una obra `En ejecucion` queda `Pausada` y deja evento de cambio de estado.
- **Prueba −:** una obra `Por iniciar` o `Terminada`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** ver OBR-B02.

#### OBR-A03 · `A_Reanudar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Reanudar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"En ejecucion"` (no cambia `Fecha_Inicio`
- **Only if this condition is true:** `[Estado]="Pausada"`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Reanudar la obra?`
- **Position:** Prominent
- **Display name:** Reanudar
- **Idempotencia:** el estado deja de ser `Pausada`.
- **Prueba +:** una obra `Pausada` vuelve a `En ejecucion` conservando su `Fecha_Inicio`.
- **Prueba −:** una obra `En ejecucion`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** ver OBR-B02.

#### OBR-A04 · `A_Terminar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Terminar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Terminada"`
  - `Fecha_Fin_Real` = `TODAY()`
- **Only if this condition is true:** `IN([Estado],LIST("En ejecucion","Pausada"))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Marcar la obra como terminada? Ya no podrá reanudarse.`
- **Position:** Prominent
- **Display name:** Terminar
- **Idempotencia:** el estado deja de ser `En ejecucion` o `Pausada`.
- **Prueba +:** una obra `En ejecucion` queda `Terminada` con `Fecha_Fin_Real` = hoy.
- **Prueba −:** una obra `Por iniciar`, `Terminada`, `Cerrada` o `Cancelada`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** ver OBR-B02.

#### OBR-A05 · `A_Cancelar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cancelar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Cancelada"`
- **Only if this condition is true:** `AND(NOT(IN([Estado],LIST("Cerrada","Cancelada"))),ISNOTBLANK([Motivo_Cancelacion]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Cancelar la obra? Ya no se podrán registrar gastos, horas, avances, facturas ni abonos.`
- **Position:** Prominent
- **Display name:** Cancelar
- **Idempotencia:** el estado pasa a uno excluido por la condición.
- **Prueba +:** una obra abierta con `Motivo_Cancelacion`: queda `Cancelada`; ya no se puede elegir en gastos, horas, avances, facturas ni abonos.
- **Prueba −:** sin motivo, o una obra `Cerrada` o `Cancelada`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** si una tabla hija todavía acepta la obra cancelada, revisar su `Valid if` de `Obra_ID` (6.1).

#### OBR-A06 · `A_Cerrar` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cerrar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Cerrada"`
  - `Fecha_Cierre` = `TODAY()`
- **Only if this condition is true:** `AND([Estado]="Terminada",[Cobranza_Completa])`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Cerrar la obra? Ya no se podrán registrar movimientos.`
- **Position:** Prominent
- **Display name:** Cerrar
- **Idempotencia:** el estado deja de ser `Terminada`.
- **Prueba +:** una obra `Terminada` con cobranza completa queda `Cerrada` con `Fecha_Cierre` = hoy y eventos `OBRA_ESTADO_CAMBIADO` y `OBRA_CERRADA`.
- **Prueba −:** una `Terminada` con saldo mayor que la tolerancia: no aparece (se usa OBR-A07).
- **Repetición:** el botón desaparece.
- **Si falla:** si el botón no aparece con la cobranza completa, revisar `Cobranza_Completa` y `TOLERANCIA_COBRANZA`.

#### OBR-A07 · `A_Cerrar_Con_Saldo` · Gestión · Obras · Acción visible
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cerrar_Con_Saldo`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Cerrada"`
  - `Fecha_Cierre` = `TODAY()`
- **Only if this condition is true:** `AND([Estado]="Terminada",NOT([Cobranza_Completa]),AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Gerencia",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),ISNOTBLANK([Motivo_Cierre_Con_Saldo]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Cerrar la obra con saldo pendiente? Quedará registrado el motivo.`
- **Position:** Prominent
- **Display name:** Cerrar con saldo
- **Idempotencia:** el estado deja de ser `Terminada`.
- **Prueba +:** con la cuenta Gerencia, una `Terminada` con saldo y `Motivo_Cierre_Con_Saldo`: queda `Cerrada`.
- **Prueba −:** con la cuenta Admin, o sin motivo, o con cobranza completa: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** si Gerencia no ve el botón, revisar que su `Rol` sea exactamente `Gerencia` y `Activo` esté en Sí (V09).

#### OBR-A08 · `A_Log_Obra_Atrasada` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Log_Obra_Atrasada`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"OBRA_ATRASADA|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"OBRA_ATRASADA"`
  - `Tabla` = `"Obras"`
  - `Registro_ID` = `[Obra_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `[Codigo]&": "&(TODAY()-[Fecha_Fin_Estimada])&" días de atraso sobre la fecha estimada"`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Correo"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` incluye la fecha: un solo evento por obra y día. OBR-B04 excluye las obras que ya tienen el de hoy.
- **Prueba +:** se verifica con OBR-B04.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver OBR-B04.
- **Si falla:** ver OBR-B04.

### 6.4 Bots

#### OBR-B01 · `B_Log_Obra_Creada` · Gestión · Obras · Bot de evento
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Data change
  - Table: `Obras`
  - Data change type: Adds only
  - Condition: (sin condición)
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"OBRA_CREADA"`
     - `Tabla` = `"Obras"`
     - `Registro_ID` = `[_THISROW].[Obra_ID]`
     - `Obra_ID` = `[_THISROW].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Obra "&[_THISROW].[Codigo]&" creada desde la proforma"`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `Obra <<[Codigo]>> creada` (⚠ V03, V14)
  3. Step type: Send an email
     - To: `[Responsable_ID].[Email]`
     - Subject: `Nueva obra <<[Codigo]>>`
     - Body: texto con `<<[Codigo]>>`, `<<[Cliente_ID].[Razon_Social]>>` y `<<[Total_Cobrar_Base]>>`. Informa al responsable, que puede usar solo OXY Campo y no recibiría el push.
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara una vez por alta de obra.
- **Límites del plan Core:** un correo y un push por obra creada.
- **Prueba +:** aceptar una proforma (PRO-A07): aparece la obra, el evento `OBRA_CREADA`, el push a Gestión y el correo al responsable.
- **Prueba −:** editar una obra existente no dispara este bot (solo altas).
- **Repetición:** no se puede crear dos veces la obra de una proforma (PRO-A07 y PRO-A09).
- **Si falla:** ver la sección 16.1 para ubicar el paso que falló; si el correo no llegó, ver 13.5.

#### OBR-B02 · `B_Log_Obra_Estado` · Gestión · Obras · Bot de evento
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Data change
  - Table: `Obras`
  - Data change type: Updates only
  - Condition: `[_THISROW_BEFORE].[Estado]<>[_THISROW_AFTER].[Estado]` ⚠ V07
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"OBRA_ESTADO_CAMBIADO"`
     - `Tabla` = `"Obras"`
     - `Registro_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Obra "&[_THISROW_AFTER].[Codigo]&" pasó a "&[_THISROW_AFTER].[Estado]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `Obra <<[Codigo]>>: <<[Estado]>>`
  3. Step type: Send an email
     - To: `[Responsable_ID].[Email]`
     - Subject: `Obra <<[Codigo]>>: <<[Estado]>>`
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara solo cuando el estado cambia.
- **Límites del plan Core:** un push y un correo por cambio de estado.
- **Prueba +:** cada una de OBR-A01 a OBR-A07 deja un evento `OBRA_ESTADO_CAMBIADO`.
- **Prueba −:** que el bot de cobranza (ABO-B03) modifique `Notificado_Cobro_Completo`, o editar el responsable, no deja evento.
- **Repetición:** repetir la acción no es posible (los botones desaparecen).
- **Si falla:** ver 16.1.

#### OBR-B03 · `B_Log_Obra_Cerrada` · Gestión · Obras · Bot de evento
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Data change
  - Table: `Obras`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]<>"Cerrada",[_THISROW_AFTER].[Estado]="Cerrada")`
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"OBRA_CERRADA"`
     - `Tabla` = `"Obras"`
     - `Registro_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Obra "&[_THISROW_AFTER].[Codigo]&" cerrada"`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `Obra <<[Codigo]>> cerrada`
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** el cierre ocurre una sola vez por obra.
- **Límites del plan Core:** un push por cierre.
- **Prueba +:** OBR-A06 y OBR-A07 dejan el evento `OBRA_CERRADA` (además del `OBRA_ESTADO_CAMBIADO` de OBR-B02).
- **Prueba −:** cualquier otro cambio de estado no deja `OBRA_CERRADA`.
- **Repetición:** una obra cerrada no vuelve a cambiar de estado.
- **Si falla:** ver 16.1.

#### OBR-B04 · `B_Obra_Atrasada` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled
  - Schedule: Daily
  - Time: 07:15
  - Time zone: America/Lima
- **Depende de:** OBR-A08, LOG-B01
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND(IN([Estado],LIST("En ejecucion","Pausada")),ISNOTBLANK([Fecha_Fin_Estimada]),[Fecha_Fin_Estimada]<TODAY(),ISBLANK(LOOKUP("OBRA_ATRASADA|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Log_Obra_Atrasada`
     - Nota: Activar **Trigger other bots**: el correo lo envía LOG-B01 al aparecer el evento (⚠ V10).
- **Datos que escribe:** una fila en `Log_Eventos` por obra atrasada y por día.
- **Idempotencia:** el `Evento_ID` incluye la fecha y las obras que ya tienen el evento de hoy quedan fuera del conjunto.
- **Límites del plan Core:** una ejecución diaria; un correo por obra atrasada y por día.
- **Prueba +:** poner `Fecha_Fin_Estimada` en una fecha pasada en una obra `En ejecucion` y ejecutar el bot: aparece un evento `OBRA_ATRASADA` y llega un correo a Gestión y al responsable.
- **Prueba −:** una obra `Terminada`, o una `En ejecucion` con fecha futura o sin fecha: no genera evento.
- **Repetición:** ejecutar el bot dos veces el mismo día no crea un segundo evento ni un segundo correo.
- **Si falla:** si el evento aparece pero no llega el correo, el problema está en LOG-B01 (ver 13.5).

### 6.5 Criterios de salida de Obras

- [ ] OBR-A01 a OBR-A08 y OBR-B01 a OBR-B04 guardan sin errores.
- [ ] El `Valid if` de `Obra_ID` impide elegir una obra `Cerrada` o `Cancelada` en las seis tablas hijas.
- [ ] Escenarios E2E-1 (tramo de obra) y E2E-5 ejecutados con resultado registrado.
- [ ] V07 y V21 cerradas.

---

## 7. Gastos (OXY Campo y OXY Gestión)

Quién registra qué: **Campo registra solo Material y Consumible** (los tipos con `Visible_Campo = "Si"`). Subcontrato, alquileres, transporte, viáticos y depreciación los registra Gestión. Los gastos se registran directamente, sin aprobación.

### 7.1 Configuración de columnas de `Gastos_Obra`

Cada bloque es una columna; cada línea, una propiedad del editor de columnas (2.5). Se aplica **en las dos apps**.

**`Tipo_Costo_ID`**
- Valid if: `SELECT(Tipos_Costo[Tipo_Costo_ID],AND([Activo],[Origen_Costo]<>"Calculado",OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Visible_Campo]="Si")))`

**`Proveedor_ID`**
- Show?: `LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Origen_Costo")="Externo"`
- Type Details → alta rápida de proveedor desde el formulario: activada

**`Tipo_Comprobante`**
- Initial value: `Boleta` en tipos externos (la mayoría de viáticos y transporte); `Sin comprobante` en tipos de origen `Interno manual`
- Nota: no es una expresión única; si se prefiere automatizar, usar `IF(LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Origen_Costo")="Interno manual","Sin comprobante","Boleta")`.

**`Foto_Comprobante`**
- Require?: `IN([Tipo_Comprobante],LIST("Factura","Boleta","Recibo por honorarios"))`

**`Monto_Base`**
- Nota: costo **sin IGV**. Con boleta, recibo o sin comprobante se digita el **total pagado**.

**`Tiene_IGV`**
- Initial value: `IF([Tipo_Comprobante]="Factura","Si","No")`

**`Monto_IGV`**
- Show?: `[Tiene_IGV]="Si"`
- Initial value: `IF([Tiene_IGV]="Si",ROUND([Monto_Base]*DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))*100)/100.0,0)`
- Valid if: `ABS([_THIS]-ROUND([Monto_Base]*DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))*100)/100.0)<=0.10`
- Invalid value error: `El IGV no coincide con el calculado sobre el monto base. Revise exoneraciones o redondeos.`
- Nota: tolerancia de 0.10 para exoneraciones y redondeos.

**`Total_Gasto`** (columna real con fórmula)
- App formula: `[Monto_Base]+[Monto_IGV]`

**`Costo_Imputable`** (columna real con fórmula)
- App formula: `IF([Es_Credito_Fiscal]="Si",[Monto_Base],[Monto_Base]+[Monto_IGV])`

**`Es_Credito_Fiscal`** (columna normal con valor inicial, **no** App formula, para no pisar la decisión manual)
- Initial value: `IF(AND([Tipo_Comprobante]="Factura",[Tiene_IGV]="Si"),"Si","No")`
- Show?: `AND(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))))`
- Editable?: `AND(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))))`
- Valid if: `OR([_THIS]="No",AND([Tipo_Comprobante]="Factura",[Tiene_IGV]="Si"))` ⚠ V08
- Nota: Campo no ve la columna, pero el valor inicial se aplica igual al guardar (⚠ V09).

**`Fecha_Pago_Estimada`**
- Initial value: `[Fecha]`
- Show?: `AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))`
- Valid if: `[_THIS]>=[Fecha]`

**`Fecha_Pago_Real`**
- Initial value: `IF(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",[Fecha],"")`
- Show?: `AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))`
- Valid if: `[_THIS]<=TODAY()`
- Nota: Campo registra gastos ya pagados (las dos fechas iguales a `Fecha`). Gestión deja `Fecha_Pago_Real` vacía si el gasto queda a crédito.

**`Motivo_Anulacion`**
- Require?: `[Estado]="Anulado"`
- Show?: `[Estado]="Vigente"`
- Editable?: `[Estado]="Vigente"`

**`Pagado`** (virtual)
- App formula: `ISNOTBLANK([Fecha_Pago_Real])`
- Nota: pendiente = `Fecha_Pago_Real` vacía; no hay columna de estado de pago.

**`Revisar_Credito`** (virtual)
- App formula: `AND([Tipo_Comprobante]="Factura",[Tiene_IGV]="Si",[Es_Credito_Fiscal]="No")`
- Show?: `AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))`
- Nota: solo informativa; marca facturas con IGV sin crédito para que Gestión las confirme con Contabilidad.

**Acción de sistema *Edit* de `Gastos_Obra`**
- Only if this condition is true: `AND([Estado]="Vigente",NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))))`

Notas de la tabla:

- Si una fórmula de esta tabla difiere del `_Diccionario`, manda el `_Diccionario`.
- **Alcance actual del pago:** solo las dos fechas y el flujo de caja. No hay vista de cuentas por pagar ni alerta de vencidos.
- **Depreciación de herramienta propia (por ahora manual):** Gestión registra un gasto de tipo *Herramienta propia (depreciación)* con la herramienta en `Descripcion`, `Monto_Base` = depreciación imputada a la obra, `Tiene_IGV = "No"`, sin proveedor ni comprobante, y `Fecha_Pago_Real` = `Fecha`. La depreciación no es un desembolso, pero se registra como pagada para no complicar el flujo de caja.

### 7.2 Preparación

1. Configuración de columnas de 7.1 aplicada en **las dos apps**.
2. `Tipos_Costo` incluida en las dos apps; en Campo con security filter `[Visible_Campo]="Si"` (sección 14).
3. Orden de construcción: GAS-A01 y GAS-A02; luego GAS-B01 a GAS-B05.

### 7.3 Acciones

#### GAS-A01 · `A_Anular_Gasto` · Gestión y Campo · Gastos_Obra · Acción visible
- **App · Tabla:** OXY Gestión **y** OXY Campo (misma configuración en ambas) · `Gastos_Obra`
- **Depende de:** —
- **For a record of this table:** `Gastos_Obra`
- **Action name:** `A_Anular_Gasto`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulado"`
- **Only if this condition is true:** `AND([Estado]="Vigente",ISNOTBLANK([Motivo_Anulacion]),OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND([Registrado_Por]=USEREMAIL(),(NOW()-[Creado_En])<"024:00:00")))` ⚠ V12
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular este gasto? No se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** el estado deja de ser `Vigente`.
- **Prueba +:** (a) Con una cuenta Campo, un gasto propio registrado hace menos de 24 horas y con motivo: aparece y queda `Anulado`. (b) Con Gestión, un gasto cualquiera con motivo: queda `Anulado`. En ambos casos aparece el evento `GASTO_ANULADO`.
- **Prueba −:** Campo con un gasto propio de más de 24 horas, o con un gasto ajeno: no aparece. Sin motivo: no aparece.
- **Repetición:** un gasto `Anulado` no muestra el botón.
- **Si falla:** si el límite de 24 horas no funciona, usar la alternativa de V12. Si Campo no ve el botón, comprobar que el motivo es editable.

#### GAS-A02 · `A_Marcar_Pagado` · Gestión · Gastos_Obra · Acción visible
- **App · Tabla:** OXY Gestión · `Gastos_Obra`
- **Depende de:** —
- **For a record of this table:** `Gastos_Obra`
- **Action name:** `A_Marcar_Pagado`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Fecha_Pago_Real` = `TODAY()`
  - Nota: (para otra fecha se usa *Edit*)
- **Only if this condition is true:** `AND([Estado]="Vigente",ISBLANK([Fecha_Pago_Real]),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Marcar el gasto como pagado hoy?`
- **Position:** Prominent
- **Display name:** Marcar pagado
- **Idempotencia:** deja de aparecer en cuanto `Fecha_Pago_Real` tiene valor.
- **Prueba +:** un gasto `Vigente` sin `Fecha_Pago_Real` en una obra abierta: queda con la fecha de hoy y deja el evento `GASTO_PAGADO`.
- **Prueba −:** un gasto ya pagado, anulado, o de una obra `Cerrada`: no aparece. Con una cuenta Campo: la app no la ofrece.
- **Repetición:** el botón desaparece.
- **Si falla:** si no hay evento en el log, ver GAS-B04.

### 7.4 Bots

#### GAS-B01 · `B_Log_Gasto_Creado` · Gestión y Campo · Gastos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión **y** OXY Campo (se crea en las dos) · `Gastos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Gastos_Obra`
  - Data change type: Adds only
  - Condition: (sin condición)
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"GASTO_CREADO"`
     - `Tabla` = `"Gastos_Obra"`
     - `Registro_ID` = `[_THISROW].[Gasto_ID]`
     - `Obra_ID` = `[_THISROW].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `PROPER(INDEX(SPLIT(INDEX(SPLIT([_THISROW].[Registrado_Por],"@"),1),"."),1))&" registró S/ "&TEXT([_THISROW].[Total_Gasto],"0.00")&" - "&[_THISROW].[Tipo_Costo_ID].[Nombre]&" - "&[_THISROW].[Obra_ID].[Codigo]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Push"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND([Rol]="Gerencia",[Activo]=TRUE))`
     - Message: `<<[Registrado_Por]>> registró S/ <<[Total_Gasto]>> en <<[Obra_ID].[Codigo]>>` (⚠ V02, V14)
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara una vez por alta.
- **Límites del plan Core:** un push por gasto. Un push solo llega a quien tiene instalada **la app donde vive el bot**: para que Gerencia reciba los gastos registrados desde Campo, debe tener OXY Campo instalada (no necesita usarla). Empezar con push para gastos y dejar el correo para lo importante.
- **Prueba +:** registrar un gasto desde Campo y otro desde Gestión: cada uno deja un evento `GASTO_CREADO`; el push llega a Gerencia en el teléfono donde esté instalada la app correspondiente.
- **Prueba −:** editar un gasto existente no dispara el bot.
- **Repetición:** registrar el mismo gasto dos veces crea dos gastos y dos eventos (son dos altas); no hay duplicado por reintento del bot.
- **Si falla:** si el gasto de una app no deja evento, comprobar que el bot existe **en esa app** (⚠ V18).

#### GAS-B02 · `B_Log_Gasto_Anulado` · Gestión y Campo · Gastos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión **y** OXY Campo · `Gastos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Gastos_Obra`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]="Vigente",[_THISROW_AFTER].[Estado]="Anulado")` ⚠ V07
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"GASTO_ANULADO"`
     - `Tabla` = `"Gastos_Obra"`
     - `Registro_ID` = `[_THISROW_AFTER].[Gasto_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Gasto "&[_THISROW_AFTER].[Gasto_ID]&" anulado: "&[_THISROW_AFTER].[Motivo_Anulacion]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
  3. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))` ⚠ V03
     - Subject: `Gasto anulado en <<[Obra_ID].[Codigo]>>`
     - Body: texto con gasto, monto, motivo y usuario.
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** el cambio `Vigente → Anulado` ocurre una vez por gasto.
- **Límites del plan Core:** un correo y un push por anulación.
- **Prueba +:** anular un gasto (GAS-A01) deja el evento y envía el correo a Gestión.
- **Prueba −:** editar un gasto `Vigente` sin anularlo no dispara el bot.
- **Repetición:** un gasto anulado no vuelve a cambiar de estado.
- **Si falla:** ver 16.1; si el correo no llegó, ver 13.5.

#### GAS-B03 · `B_Log_Credito_Fiscal` · Gestión · Gastos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión · `Gastos_Obra` (solo Gestión puede cambiar `Es_Credito_Fiscal`)
- **Event:**
  - Event type: Data change
  - Table: `Gastos_Obra`
  - Data change type: Updates only
  - Condition: `[_THISROW_BEFORE].[Es_Credito_Fiscal]<>[_THISROW_AFTER].[Es_Credito_Fiscal]` ⚠ V07
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"CREDITO_FISCAL_CAMBIADO"`
     - `Tabla` = `"Gastos_Obra"`
     - `Registro_ID` = `[_THISROW_AFTER].[Gasto_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Gasto "&[_THISROW_AFTER].[Gasto_ID]&": Es_Credito_Fiscal "&[_THISROW_BEFORE].[Es_Credito_Fiscal]&" -> "&[_THISROW_AFTER].[Es_Credito_Fiscal]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Push"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara solo cuando el valor cambia.
- **Límites del plan Core:** un push por cambio.
- **Prueba +:** con Gestión, cambiar `Es_Credito_Fiscal` de Sí a No en una factura con IGV de una obra abierta: se registra `CREDITO_FISCAL_CAMBIADO` con los valores antes y después.
- **Prueba −:** cambiar otra columna del gasto (por ejemplo `Descripcion`) no dispara el bot. Cambiar el valor desde Campo no es posible.
- **Repetición:** guardar el mismo valor no deja evento.
- **Si falla:** si el bot no distingue el cambio, ver V07.

#### GAS-B04 · `B_Log_Gasto_Pagado` · Gestión · Gastos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión · `Gastos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Gastos_Obra`
  - Data change type: Updates only
  - Condition: `AND(ISBLANK([_THISROW_BEFORE].[Fecha_Pago_Real]),ISNOTBLANK([_THISROW_AFTER].[Fecha_Pago_Real]))` ⚠ V07
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"GASTO_PAGADO"`
     - `Tabla` = `"Gastos_Obra"`
     - `Registro_ID` = `[_THISROW_AFTER].[Gasto_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Gasto "&[_THISROW_AFTER].[Gasto_ID]&" pagado el "&TEXT([_THISROW_AFTER].[Fecha_Pago_Real],"yyyy-MM-dd")`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Push"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** solo se dispara cuando `Fecha_Pago_Real` pasa de vacía a con valor.
- **Límites del plan Core:** un push por pago.
- **Prueba +:** GAS-A02 sobre un gasto pendiente deja el evento.
- **Prueba −:** corregir una fecha de pago ya existente no dispara el bot; un gasto nuevo de Campo (que nace pagado) no lo dispara porque es un alta.
- **Repetición:** el gasto ya pagado no vuelve a cambiar de vacío a con valor.
- **Si falla:** ver V07.

#### GAS-B05 · `B_Gasto_Sobre_Planificado` · Gestión y Campo · Gastos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión **y** OXY Campo · `Gastos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Gastos_Obra`
  - Data change type: Adds only
  - Condition:
  ```
  SUM(SELECT(Gastos_Obra[Costo_Imputable],
    AND([Obra_ID]=[_THISROW].[Obra_ID],[Tipo_Costo_ID]=[_THISROW].[Tipo_Costo_ID],[Estado]="Vigente")))
  >
  SUM(SELECT(Proforma_Planificacion[Costo_Imputable],
    AND([Proforma_ID]=[_THISROW].[Obra_ID].[Proforma_ID],[Tipo_Costo_ID]=[_THISROW].[Tipo_Costo_ID])))
  ```
  Compara el gasto acumulado del tipo contra la planificación del mismo tipo, ambos en soles y con la misma regla (`Costo_Imputable`). Si un tipo no tiene línea planificada, el plan vale 0 y cualquier gasto dispara el aviso: sirve para detectar gastos sin partida planificada.
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"GASTO_SOBRE_PLANIFICADO"`
     - `Tabla` = `"Gastos_Obra"`
     - `Registro_ID` = `[_THISROW].[Gasto_ID]`
     - `Obra_ID` = `[_THISROW].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `[_THISROW].[Obra_ID].[Codigo]&": el gasto de "&[_THISROW].[Tipo_Costo_ID].[Nombre]&" supera lo planificado"`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
  3. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Subject: `Gasto sobre lo planificado en <<[Obra_ID].[Codigo]>>`
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se evalúa en cada alta de gasto; **mientras el acumulado siga por encima del plan, cada gasto nuevo de ese tipo vuelve a dispararlo**. Es intencional: cada exceso es un hecho nuevo.
- **Límites del plan Core:** un correo y un push por gasto que cumple.
- **Prueba +:** en una obra con una línea planificada de tipo Material, registrar gastos de Material hasta superar el monto planificado: el gasto que lo supera deja el evento y envía el correo.
- **Prueba −:** un gasto que deja el acumulado por debajo del plan no dispara el bot; un gasto anulado no cuenta en la suma.
- **Repetición:** un nuevo gasto del mismo tipo con el acumulado ya excedido dispara otro evento (esperado).
- **Si falla:** si la condición da error de sintaxis, revisar que las referencias `[Obra_ID].[Proforma_ID]` existan en `Gastos_Obra`.

### 7.5 Criterios de salida de Gastos

- [ ] La configuración de columnas de 7.1 aplicada en las dos apps.
- [ ] GAS-A01 y GAS-B01/B02/B05 existen **en las dos apps**; GAS-A02, GAS-B03 y GAS-B04, solo en Gestión.
- [ ] Escenarios E2E-1 (tramo de gastos) y E2E-7 (Campo) ejecutados con resultado registrado.
- [ ] V02, V07, V08, V09, V12, V14 y V18 cerradas.

---

## 8. Horas (Campo registra · Gestión aprueba)

`Registro_Horas` en Campo muestra solo `Obra_ID`, `Trabajador_ID`, `Fecha`, `Horas`, `Horas_Extra` y `Descripcion`. Las columnas de costo (`Costo_Hora`, `Costo_Hora_Extra`, `Costo_Total`) son para Gestión (`Show?`: `AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))`), con la salvedad de la sección 14.4 sobre datos que llegan al dispositivo. La mano de obra propia no lleva IGV.

### 8.1 Configuración de columnas

**`Trabajador_ID`**
- Valid if: `SELECT(Asignaciones_Obra[Trabajador_ID],AND([Obra_ID]=[_THISROW].[Obra_ID],[Activo]=TRUE))`
- Nota: solo trabajadores asignados a la obra.

**`Estado`**
- Initial value: `"Pendiente"`
- Editable?: `FALSE`

**`Registrado_Por`**
- Initial value: `USEREMAIL()`

**`Creado_En`**
- Initial value: `NOW()`

### 8.2 Preparación

1. Tablas `Registro_Horas`, `Asignaciones_Obra`, `Trabajadores` y `Tarifas_Trabajador` (esta última solo en Gestión) con sus permisos.
2. Orden de construcción: HOR-A01 y HOR-A02; luego HOR-B01.

### 8.3 Acciones

#### HOR-A01 · `A_Aprobar_Horas` · Gestión · Registro_Horas · Acción visible
- **App · Tabla:** OXY Gestión · `Registro_Horas`
- **Depende de:** —
- **For a record of this table:** `Registro_Horas`
- **Action name:** `A_Aprobar_Horas`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Aprobado"`
  - `Aprobado_Por` = `USEREMAIL()`
  - `Costo_Hora` = `ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))`
  - `Costo_Hora_Extra` = `ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora_Extra],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))`
  - `Costo_Total` = `[Horas]*ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))+[Horas_Extra]*ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora_Extra],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))`
  - Nota: (las expresiones de tarifa se repiten: dentro de una misma acción un *Set values* no ve lo que acaba de escribir)
  - Nota: `Costo_Total` es el costo en soles que suma `Obras.Total_Personal` (solo horas con `Estado = "Aprobado"`).
- **Only if this condition is true:** `AND([Estado]="Pendiente",AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),ISNOTBLANK(ANY(SELECT(Tarifas_Trabajador[Tarifa_Hora],AND([Trabajador_ID]=[_THISROW].[Trabajador_ID],[Vigente_Desde]<=[_THISROW].[Fecha],OR(ISBLANK([Vigente_Hasta]),[Vigente_Hasta]>=[_THISROW].[Fecha]))))))`
- **Needs confirmation?:** No
- **Position:** Prominent
- **Display name:** Aprobar
- **Idempotencia:** el estado deja de ser `Pendiente`.
- **Prueba +:** un registro `Pendiente` de un trabajador con tarifa vigente a esa fecha: queda `Aprobado` con `Costo_Hora`, `Costo_Hora_Extra` y `Costo_Total` calculados y `Aprobado_Por` = el usuario.
- **Prueba −:** un trabajador sin tarifa vigente en esa fecha: el botón no aparece (no se aprueba sin tarifa). Un registro ya aprobado o rechazado: no aparece.
- **Límite:** con `Horas_Extra` vacío y `Tarifa_Hora_Extra` vacía el costo extra es 0; con horas extra y sin tarifa extra, el costo extra es 0 (completar la tarifa en `Tarifas_Trabajador`).
- **Repetición:** el botón desaparece.
- **Si falla:** si `Costo_Total` queda en 0, revisar `Tarifas_Trabajador` (vigencias y `Trabajador_ID`).

#### HOR-A02 · `A_Rechazar_Horas` · Gestión · Registro_Horas · Acción visible
- **App · Tabla:** OXY Gestión · `Registro_Horas`
- **Depende de:** —
- **For a record of this table:** `Registro_Horas`
- **Action name:** `A_Rechazar_Horas`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Rechazado"`
  - `Aprobado_Por` = `USEREMAIL()`
- **Only if this condition is true:** `AND([Estado]="Pendiente",AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Rechazar estas horas? No sumarán costo a la obra.`
- **Position:** Prominent
- **Display name:** Rechazar
- **Idempotencia:** el estado deja de ser `Pendiente`.
- **Prueba +:** un registro `Pendiente` queda `Rechazado` y no suma a `Total_Personal`.
- **Prueba −:** un registro ya aprobado: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** si el registro rechazado todavía suma costo, revisar que `Total_Personal` filtre por `Estado="Aprobado"`.

### 8.4 Bots

#### HOR-B01 · `B_Log_Horas_Pendientes` · Gestión y Campo · Registro_Horas · Bot de evento
- **App · Tabla:** OXY Gestión **y** OXY Campo · `Registro_Horas`
- **Event:**
  - Event type: Data change
  - Table: `Registro_Horas`
  - Data change type: Adds only
  - Condition: `[Estado]="Pendiente"`
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"HORAS_PENDIENTES"`
     - `Tabla` = `"Registro_Horas"`
     - `Registro_ID` = `[_THISROW].[Horas_ID]`
     - `Obra_ID` = `[_THISROW].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Horas por aprobar: "&[_THISROW].[Trabajador_ID].[Nombres]&" "&TEXT([_THISROW].[Horas]+[_THISROW].[Horas_Extra],"0.0")&" h - "&[_THISROW].[Obra_ID].[Codigo]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Push"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))` (⚠ V14)
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** una vez por alta.
- **Límites del plan Core:** un push por registro de horas; ver la nota de alcance en GAS-B01.
- **Prueba +:** registrar horas desde Campo deja el evento `HORAS_PENDIENTES`.
- **Prueba −:** aprobar las horas (HOR-A01) no dispara el bot (no es un alta).
- **Repetición:** dos registros distintos dejan dos eventos.
- **Si falla:** si el registro de Campo no deja evento, comprobar que el bot existe en OXY Campo (⚠ V18).

### 8.5 Criterios de salida de Horas

- [ ] HOR-A01 y HOR-A02 en Gestión; HOR-B01 en las dos apps.
- [ ] Aprobación probada con y sin tarifa vigente.
- [ ] V14 y V18 cerradas.

---

## 9. Avance físico (OXY Campo y OXY Gestión)

`Avances_Obra` registra el avance físico **diario y acumulado** (0–100 %), con descripción y foto de evidencia. Habilita el valor ganado, el CPI y las proyecciones de `Obras`. El aviso por falta de avance está en la sección 12 (ALE-B02).

### 9.1 Configuración de columnas

**`Obra_ID`**
- Valid if: obras abiertas, igual que en 6.1 (`SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`)
- Nota: en Campo, además, solo las obras asignadas al trabajador (security filter, sección 14).

**`Avance_Pct`**
- Valid if: `AND([_THIS]>0,[_THIS]<=100,[_THIS]>=MAX(SELECT(Avances_Obra[Avance_Pct],AND([Obra_ID]=[_THISROW].[Obra_ID],[Estado]="Vigente"))))`
- Nota: el avance acumulado no puede bajar.

**`Motivo_Anulacion`**
- Show?: `[Estado]="Vigente"`
- Editable?: `[Estado]="Vigente"`

Un avance se anula, no se borra.

### 9.2 Preparación

1. Tabla `Avances_Obra` en las dos apps, con *Adds* y *Updates* y sin *Deletes*.
2. AVA-A01 se crea en **las dos apps**.

### 9.3 Acciones

#### AVA-A01 · `A_Anular_Avance` · Gestión y Campo · Avances_Obra · Acción visible
- **App · Tabla:** OXY Gestión **y** OXY Campo · `Avances_Obra`
- **Depende de:** —
- **For a record of this table:** `Avances_Obra`
- **Action name:** `A_Anular_Avance`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulado"`
- **Only if this condition is true:** `AND([Estado]="Vigente",ISNOTBLANK([Motivo_Anulacion]),OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Registrado_Por]=USEREMAIL()))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular este avance? No se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** el estado deja de ser `Vigente`.
- **Prueba +:** Campo anula un avance propio con motivo: queda `Anulado` y `Avance_Actual` de la obra vuelve al avance vigente anterior. Gestión anula cualquier avance con motivo.
- **Prueba −:** Campo con un avance de otra persona, o sin motivo: no aparece.
- **Repetición:** un avance `Anulado` no muestra el botón.
- **Límite:** registrar un avance igual al último vigente es válido; uno menor, no (`Valid if` de `Avance_Pct`).
- **Si falla:** si `Avance_Actual` no baja tras anular, revisar que su fórmula filtre por `Estado="Vigente"`.

### 9.4 Criterios de salida de Avance

- [ ] AVA-A01 en las dos apps.
- [ ] El `Valid if` de `Avance_Pct` rechaza un valor menor al último avance vigente y uno mayor a 100.
- [ ] V18 cerrada.

---

## 10. Abonos y cobranza (solo OXY Gestión)

- `Monto_Abono` es el depósito en soles; `Total_Abonos` de la obra suma los abonos vigentes. Las detracciones y retenciones cuentan como abono para llegar al 100 %.
- La cobranza se compara contra `Total_Cobrar_Base` (subtotal más IGV): `Saldo = Total_Cobrar_Base − Total_Abonos`. La cobranza se da por completa cuando el saldo está dentro de `TOLERANCIA_COBRANZA` (virtual `Cobranza_Completa`).
- Ni los abonos ni las facturas existen en OXY Campo.

### 10.1 Configuración de columnas de `Abonos_Obra`

Cada bloque es una columna; cada línea, una propiedad del editor de columnas (2.5).

**`Obra_ID`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Factura_ID`**
- Valid if: `SELECT(Facturas_Obra[Factura_ID],AND([Obra_ID]=[_THISROW].[Obra_ID],[Estado]="Vigente"))`
- Nota: es opcional; un abono sin factura sigue contando para la cobranza de la obra. Si un depósito paga varias facturas, se registra un abono por factura ⚠ V04

**`Fecha`**
- Initial value: `TODAY()`
- Valid if: `[_THIS]<=TODAY()`

**`Concepto`** (Enum)
- Type Details → Values: `Pago`, `Detraccion`, `Retencion`

**`Monto_Abono`**
- Valid if: `[_THIS]>0`

**`Incluye_IGV`**
- Initial value: `"Si"`
- Nota: es informativo; el abono se compara siempre contra `Total_Cobrar_Base`.

**`Estado`**
- Initial value: `"Vigente"`
- Editable?: `FALSE`

**`Motivo_Anulacion`**
- Require?: `[Estado]="Anulado"`
- Show?: `[Estado]="Vigente"`
- Editable?: `[Estado]="Vigente"`

**`Estado_Cobranza`** (virtual, en `Obras`)
- Nota: valores `Sin abonos`, `Parcial`, `Cobrada`, `Sobrepagada`. La fórmula está en el `_Diccionario`.

**`Notificado_Cobro_Completo`** (en `Obras`)
- Editable?: `FALSE`
- Nota: solo la cambian ABO-A02 y ABO-A04.

**`Fecha_Cobranza_Completa`** (en `Obras`)
- Editable?: `FALSE`
- Nota: solo la cambian ABO-A02 y ABO-A04.

**Acción de sistema *Edit* de `Abonos_Obra`**
- Only if this condition is true: `AND([Estado]="Vigente",NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`

### 10.2 Preparación

1. Configuración de 10.1 aplicada.
2. `Medios_Pago` incluida en OXY Gestión.
3. Orden de construcción: ABO-A01 a ABO-A06; luego ABO-B01 a ABO-B05. ABO-B03 y ABO-B04 dependen de que LOG-B01 y LOG-B02 existan (sección 13) para que el aviso salga; pueden construirse antes, pero su prueba completa solo es posible cuando existan.

### 10.3 Acciones

#### ABO-A01 · `A_Anular_Abono` · Gestión · Abonos_Obra · Acción visible
- **App · Tabla:** OXY Gestión · `Abonos_Obra`
- **Depende de:** —
- **For a record of this table:** `Abonos_Obra`
- **Action name:** `A_Anular_Abono`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulado"`
- **Only if this condition is true:** `AND([Estado]="Vigente",ISNOTBLANK([Motivo_Anulacion]),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular este abono? No se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** el estado deja de ser `Vigente`.
- **Prueba +:** un abono `Vigente` con motivo, en una obra abierta: queda `Anulado`, el `Saldo` de la obra sube en ese monto y aparece el evento `ABONO_ANULADO` (ABO-B02).
- **Prueba −:** sin motivo, o ya anulado, o de una obra `Cerrada`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** si el motivo no se puede escribir, revisar su `Editable?`.

#### ABO-A02 · `A_Cobranza_Marcar` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cobranza_Marcar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Notificado_Cobro_Completo` = `"Si"`
  - `Fecha_Cobranza_Completa` = `TODAY()`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** ABO-B03 solo la llama para obras con `Notificado_Cobro_Completo = "No"`.
- **Prueba +:** se verifica con ABO-B03.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ABO-B03.
- **Si falla:** ver ABO-B03.

#### ABO-A03 · `A_Cobranza_Log` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cobranza_Log`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"COBRANZA_COMPLETA|"&[Obra_ID]&"|"&TEXT([Fecha_Cobranza_Completa],"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"COBRANZA_COMPLETA"`
  - `Tabla` = `"Obras"`
  - `Registro_ID` = `[Obra_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `[Codigo]&": cobranza completa (abonos S/ "&TEXT([Total_Abonos],"0.00")&" de S/ "&TEXT([Total_Cobrar_Base],"0.00")&")"`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Ambos"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` incluye la fecha en que se completó la cobranza: una cobranza completa genera un solo evento, y si la cobranza se reabre y vuelve a completarse en otra fecha, genera otro.
- **Prueba +:** se verifica con ABO-B03.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ABO-B03.
- **Si falla:** ver ABO-B03.

#### ABO-A04 · `A_Cobranza_Reabrir` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cobranza_Reabrir`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Notificado_Cobro_Completo` = `"No"`
  - `Fecha_Cobranza_Completa` = `""`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** ABO-B04 solo la llama para obras con `Notificado_Cobro_Completo = "Si"` cuya cobranza ya no está completa.
- **Prueba +:** se verifica con ABO-B04.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ABO-B04.
- **Si falla:** ver ABO-B04.

#### ABO-A05 · `A_Cobranza_Reabierta_Log` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Cobranza_Reabierta_Log`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"COBRANZA_REABIERTA|"&[Obra_ID]&"|"&TEXT([Fecha_Cobranza_Completa],"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"COBRANZA_REABIERTA"`
  - `Tabla` = `"Obras"`
  - `Registro_ID` = `[Obra_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `[Codigo]&": la cobranza dejó de estar completa (saldo S/ "&TEXT([Saldo],"0.00")&")"`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Ambos"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` incluye la fecha de la cobranza completa que se reabre; ABO-B04 registra el evento **antes** de borrar esa fecha.
- **Prueba +:** se verifica con ABO-B04.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ABO-B04.
- **Si falla:** ver ABO-B04.

#### ABO-A06 · `A_Recordatorio_Log` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Recordatorio_Log`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"RECORDATORIO_COBRANZA|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"RECORDATORIO_COBRANZA"`
  - `Tabla` = `"Obras"`
  - `Registro_ID` = `[Obra_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `[Codigo]&": "&(TODAY()-[Fecha_Inicio])&" días desde el inicio y sin abonos registrados"`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Correo"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` incluye la fecha: un solo recordatorio por obra y día.
- **Prueba +:** se verifica con ABO-B05.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ABO-B05.
- **Si falla:** ver ABO-B05.

### 10.4 Bots

#### ABO-B01 · `B_Log_Abono_Creado` · Gestión · Abonos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión · `Abonos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Abonos_Obra`
  - Data change type: Adds only
  - Condition: (sin condición)
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"ABONO_CREADO"`
     - `Tabla` = `"Abonos_Obra"`
     - `Registro_ID` = `[_THISROW].[Abono_ID]`
     - `Obra_ID` = `[_THISROW].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Abono S/ "&TEXT([_THISROW].[Monto_Abono],"0.00")&" ("&[_THISROW].[Concepto]&") - "&[_THISROW].[Obra_ID].[Codigo]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `Abono S/ <<[Monto_Abono]>> en <<[Obra_ID].[Codigo]>>` (⚠ V14)
  3. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))` ⚠ V03
     - Subject: `Abono registrado en <<[Obra_ID].[Codigo]>>`
     - Body: texto con monto, concepto, medio de pago, número de operación y usuario.
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara una vez por alta.
- **Límites del plan Core:** un correo y un push por abono.
- **Prueba +:** registrar un abono: aparece el evento `ABONO_CREADO`, llega el push y el correo a Gestión.
- **Prueba −:** editar un abono existente no dispara el bot.
- **Repetición:** registrar otro abono crea otro evento (son dos altas).
- **Si falla:** ver 16.1; si el correo no llegó, ver 13.5.

#### ABO-B02 · `B_Log_Abono_Anulado` · Gestión · Abonos_Obra · Bot de evento
- **App · Tabla:** OXY Gestión · `Abonos_Obra`
- **Event:**
  - Event type: Data change
  - Table: `Abonos_Obra`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]="Vigente",[_THISROW_AFTER].[Estado]="Anulado")` ⚠ V07
- **Depende de:** —
- **Process:**
  1. Step type: Run a data action → Add new rows to another table
     - Table: `Log_Eventos`
     - `Evento_ID` = `UNIQUEID()`
     - `Fecha_Hora` = `NOW()`
     - `Tipo_Evento` = `"ABONO_ANULADO"`
     - `Tabla` = `"Abonos_Obra"`
     - `Registro_ID` = `[_THISROW_AFTER].[Abono_ID]`
     - `Obra_ID` = `[_THISROW_AFTER].[Obra_ID]`
     - `Usuario` = `USEREMAIL()`
     - `Resumen` = `"Abono "&[_THISROW_AFTER].[Abono_ID]&" anulado: "&[_THISROW_AFTER].[Motivo_Anulacion]`
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - `Canal` = `"Ambos"`
  2. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
  3. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Subject: `Abono anulado en <<[Obra_ID].[Codigo]>>`
     - Body: texto con monto, motivo y usuario.
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** el cambio `Vigente → Anulado` ocurre una vez por abono.
- **Límites del plan Core:** un correo y un push por anulación.
- **Prueba +:** ABO-A01 deja el evento y envía el correo.
- **Prueba −:** editar un abono `Vigente` sin anularlo no dispara el bot.
- **Repetición:** un abono anulado no vuelve a cambiar de estado.
- **Si falla:** ver 16.1.

#### ABO-B03 · `B_Cobranza_Completa` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 08:00
  - Time zone: America/Lima
- **Depende de:** ABO-A02, ABO-A03, LOG-B01, LOG-B02
- **Process:**
  el orden es **marcar primero y registrar después**; el segundo paso no depende de que el primero haya corrido en la misma ejecución.
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Notificado_Cobro_Completo]="No",NOT(IN([Estado],LIST("Cerrada","Cancelada"))),[Total_Abonos]>0,[Cobranza_Completa]))`
     - Referenced Action: `A_Cobranza_Marcar`
  2. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Notificado_Cobro_Completo]="Si",ISNOTBLANK([Fecha_Cobranza_Completa]),NOT(IN([Estado],LIST("Cerrada","Cancelada"))),[Cobranza_Completa],ISBLANK(LOOKUP("COBRANZA_COMPLETA|"&[Obra_ID]&"|"&TEXT([Fecha_Cobranza_Completa],"yyyy-MM-dd"),"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Cobranza_Log`
  Nota: Activar **Trigger other bots** para que LOG-B01 y LOG-B02 avisen al aparecer el evento (⚠ V10). El bot **no cierra la obra**: el cierre es decisión de Gerencia (OBR-A06).
- **Datos que escribe:** `Obras.Notificado_Cobro_Completo`, `Obras.Fecha_Cobranza_Completa` y una fila en `Log_Eventos`.
- **Idempotencia:** marcar saca a la obra del primer conjunto; el evento tiene `Evento_ID` único por obra y fecha de cobranza completa y el segundo conjunto excluye a las obras que ya lo tienen. Si la corrida se corta entre los dos pasos, la siguiente registra el evento que faltó, sin repetir el aviso.
- **Límites del plan Core:** una ejecución diaria; un correo y un push por obra que completa su cobranza.
- **Prueba +:** en una obra `En ejecucion` sin cobranza completa, registrar abonos hasta cubrir el `Total_Cobrar_Base` (o dejar el saldo dentro de la tolerancia) y ejecutar el bot: `Notificado_Cobro_Completo = "Si"`, `Fecha_Cobranza_Completa` = hoy, un evento `COBRANZA_COMPLETA` y los avisos a Gestión.
- **Prueba −:** una obra con saldo fuera de la tolerancia, `Cerrada`, `Cancelada` o sin abonos: no cambia.
- **Repetición:** ejecutarlo dos veces el mismo día no crea otro evento ni otro aviso.
- **Si falla:** en `Monitor` ver en qué paso quedó. Si `Notificado_Cobro_Completo` es `Si` y no hay evento, ejecutar el bot otra vez. Si el evento está y no llegó el aviso, ver 13.5.

#### ABO-B04 · `B_Cobranza_Reabierta` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 08:05
  - Time zone: America/Lima
- **Depende de:** ABO-A04, ABO-A05, LOG-B01, LOG-B02
- **Process:**
  el orden es **registrar primero y reabrir después**, porque el `Evento_ID` usa la fecha que el segundo paso borra.
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Notificado_Cobro_Completo]="Si",ISNOTBLANK([Fecha_Cobranza_Completa]),NOT([Cobranza_Completa]),NOT(IN([Estado],LIST("Cerrada","Cancelada"))),ISBLANK(LOOKUP("COBRANZA_REABIERTA|"&[Obra_ID]&"|"&TEXT([Fecha_Cobranza_Completa],"yyyy-MM-dd"),"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Cobranza_Reabierta_Log`
  2. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Notificado_Cobro_Completo]="Si",NOT([Cobranza_Completa]),NOT(IN([Estado],LIST("Cerrada","Cancelada")))))`
     - Referenced Action: `A_Cobranza_Reabrir`
  Nota: Activar **Trigger other bots** (⚠ V10).
- **Datos que escribe:** una fila en `Log_Eventos` y las dos columnas de cobranza de `Obras`.
- **Idempotencia:** igual que ABO-B03; si se corta entre pasos, la siguiente corrida completa la reapertura sin repetir el evento.
- **Límites del plan Core:** una ejecución diaria; un correo y un push por obra reabierta.
- **Prueba +:** con la obra de la prueba de ABO-B03, anular un abono (ABO-A01) para que el saldo salga de la tolerancia y ejecutar el bot: `Notificado_Cobro_Completo = "No"`, `Fecha_Cobranza_Completa` vacía, un evento `COBRANZA_REABIERTA` y los avisos.
- **Prueba −:** una obra con cobranza completa o ya reabierta: no cambia.
- **Repetición:** ejecutarlo dos veces no duplica el evento.
- **Si falla:** igual que ABO-B03.

#### ABO-B05 · `B_Recordatorio_Cobranza` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Weekly
  - Day: Monday
  - Time: 08:10
  - Time zone: America/Lima
- **Depende de:** ABO-A06, LOG-B01
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND(NOT(IN([Estado],LIST("Cerrada","Cancelada"))),[Estado_Cobranza]="Sin abonos",ISNOTBLANK([Fecha_Inicio]),(TODAY()-[Fecha_Inicio])>NUMBER(LOOKUP("DIAS_RECORDATORIO_COBRANZA","Configuracion","Clave","Valor")),ISBLANK(LOOKUP("RECORDATORIO_COBRANZA|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Recordatorio_Log`
     - Nota: Activar **Trigger other bots** (⚠ V10).
- **Datos que escribe:** una fila en `Log_Eventos` por obra y por corrida.
- **Idempotencia:** `Evento_ID` con la fecha; las obras que ya tienen el evento de hoy quedan fuera.
- **Límites del plan Core:** una ejecución semanal; un correo por obra en el conjunto.
- **Prueba +:** una obra iniciada hace más días que `DIAS_RECORDATORIO_COBRANZA` y sin abonos vigentes: un evento `RECORDATORIO_COBRANZA` y un correo a Gestión.
- **Prueba −:** una obra con algún abono vigente, o iniciada hace menos días, o sin `Fecha_Inicio`: no genera evento.
- **Repetición:** ejecutarlo dos veces el mismo día no crea otro evento.
- **Si falla:** si el evento aparece y el correo no llega, ver 13.5.

### 10.5 Criterios de salida de Abonos y cobranza

- [ ] Configuración de 10.1 aplicada.
- [ ] ABO-A01 a ABO-A06 y ABO-B01 a ABO-B05 guardan sin errores.
- [ ] Escenario E2E-3 (anulación de abono, tramo de cobranza) y el tramo de cobranza de E2E-1 ejecutados con resultado registrado.
- [ ] V04, V13 y V21 cerradas.

---

## 11. Facturas de venta (solo OXY Gestión)

OXY emite varias facturas por obra (adelantos, valorizaciones, liquidación final). Se registran en `Facturas_Obra`. Aportan fecha de vencimiento, antigüedad de la cartera y rezago de facturación.

### 11.1 Configuración de columnas de `Facturas_Obra`

Cada bloque es una columna; cada línea, una propiedad del editor de columnas (2.5).

**`Obra_ID`**
- Valid if: `SELECT(Obras[Obra_ID],NOT(IN([Estado],LIST("Cerrada","Cancelada"))))`

**`Tipo`** (Enum)
- Type Details → Values: `Adelanto`, `Valorizacion`, `Liquidacion final`, `Otro`

**`Nro_Factura`**
- Valid if: `NOT(IN([_THIS],SELECT(Facturas_Obra[Nro_Factura],AND([Estado]="Vigente",[Factura_ID]<>[_THISROW].[Factura_ID]))))`
- Invalid value error: `Ese número de factura ya está registrado`
- Nota: ⚠ V04

**`Fecha_Emision`**
- Initial value: `TODAY()`
- Valid if: `[_THIS]<=TODAY()`

**`Plazo_Pago_Dias`**
- Initial value: `IFS(ISNOTBLANK([Obra_ID].[Cliente_ID].[Plazo_Pago_Dias]),[Obra_ID].[Cliente_ID].[Plazo_Pago_Dias],TRUE,NUMBER(LOOKUP("PLAZO_PAGO_DIAS_DEFECTO","Configuracion","Clave","Valor")))`
- Editable?: `TRUE`

**`Fecha_Vencimiento`** (columna real con fórmula)
- App formula: `[Fecha_Emision]+[Plazo_Pago_Dias]`

**`Monto_Neto`**
- Valid if: `[_THIS]>0`

**`IGV`**
- Initial value: `ROUND([Monto_Neto]*DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))*100)/100.0`
- Editable?: `TRUE`

**`Total`** (columna real con fórmula)
- App formula: `[Monto_Neto]+[IGV]`
- Valid if: `OR(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Gerencia",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),SUM(SELECT(Facturas_Obra[Total],AND([Obra_ID]=[_THISROW].[Obra_ID],[Estado]="Vigente",[Factura_ID]<>[_THISROW].[Factura_ID])))+[_THIS]<=[Obra_ID].[Total_Cobrar_Base]+DECIMAL(LOOKUP("TOLERANCIA_COBRANZA","Configuracion","Clave","Valor")))`
- Invalid value error: `La suma de facturas supera el total a cobrar de la obra. Solo Gerencia puede sobre-facturar`
- Nota: tope de facturación ⚠ V04

**`Estado`**
- Initial value: `"Vigente"`
- Editable?: `FALSE`

**`Notificado_Vencida`**
- Initial value: `"No"`
- Editable?: `FALSE`
- Nota: solo la cambia FAC-A04.

**`Motivo_Anulacion`**
- Require?: `[Estado]="Anulado"`
- Show?: `[Estado]="Vigente"`
- Editable?: `[Estado]="Vigente"`

**Acción de sistema *Edit* de `Facturas_Obra`**
- Only if this condition is true: `AND([Estado]="Vigente",NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`

Cómo se relacionan las tablas:

- **Abono ↔ factura:** `Abonos_Obra.Factura_ID` enlaza cada abono con la factura que paga. De ese enlace salen las virtuales `Cobrado`, `Saldo_Factura`, `Estado_Pago` (`Pendiente`, `Parcial`, `Pagada`, `Anulada`), `Vencida` y `Dias_Vencida`.
- **Virtuales en `Obras`** (crear una por línea según el `_Diccionario`):
  1. `Facturado_Acum`
  2. `Por_Facturar`
  3. `Pct_Facturado`
  4. `Facturado_Sin_Cobrar`
  5. `Cartera_Vencida`
  6. `Rezago_Facturacion_pp` (avance físico % menos facturado %)

### 11.2 Preparación

1. Configuración de 11.1 aplicada.
2. `Clientes` incluida en OXY Gestión (de ahí sale el plazo de pago).
3. Orden de construcción: FAC-A01 a FAC-A04; luego FAC-B01 y FAC-B02.

### 11.3 Acciones

#### FAC-A01 · `A_Anular_Factura` · Gestión · Facturas_Obra · Acción visible
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Depende de:** —
- **For a record of this table:** `Facturas_Obra`
- **Action name:** `A_Anular_Factura`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulado"`
- **Only if this condition is true:** `AND([Estado]="Vigente",ISNOTBLANK([Motivo_Anulacion]),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),NOT(IN([Obra_ID].[Estado],LIST("Cerrada","Cancelada"))),COUNT(SELECT(Abonos_Obra[Abono_ID],AND([Factura_ID]=[_THISROW].[Factura_ID],[Estado]="Vigente")))=0)`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular esta factura? No se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** el estado deja de ser `Vigente`.
- **Prueba +:** una factura `Vigente` sin abonos vigentes y con motivo: queda `Anulado`, `Facturado_Acum` de la obra baja y `Por_Facturar` sube.
- **Prueba −:** una factura con un abono vigente aplicado, o sin motivo, o ya anulada: no aparece. Para anular una factura con abonos hay que anular antes esos abonos (ABO-A01).
- **Repetición:** el botón desaparece.
- **Si falla:** si no aparece estando todo en regla, comprobar que `Abonos_Obra.Factura_ID` y `Facturas_Obra.Factura_ID` son claves del mismo tipo.

#### FAC-A02 · `A_Factura_Log_Por_Vencer` · Gestión · Facturas_Obra · Auxiliar
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Depende de:** —
- **For a record of this table:** `Facturas_Obra`
- **Action name:** `A_Factura_Log_Por_Vencer`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"FACTURA_POR_VENCER|"&[Factura_ID]` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"FACTURA_POR_VENCER"`
  - `Tabla` = `"Facturas_Obra"`
  - `Registro_ID` = `[Factura_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `"Factura "&[Nro_Factura]&" ("&[Obra_ID].[Codigo]&") vence el "&TEXT([Fecha_Vencimiento],"yyyy-MM-dd")&"; saldo S/ "&TEXT([Saldo_Factura],"0.00")`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Correo"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` es único por factura: se avisa una sola vez.
- **Prueba +:** se verifica con FAC-B01.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver FAC-B01.
- **Si falla:** ver FAC-B01.

#### FAC-A03 · `A_Factura_Log_Vencida` · Gestión · Facturas_Obra · Auxiliar
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Depende de:** —
- **For a record of this table:** `Facturas_Obra`
- **Action name:** `A_Factura_Log_Vencida`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Log_Eventos`
- **Set these columns:**
  - `Evento_ID` = `"FACTURA_VENCIDA|"&[Factura_ID]` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Tipo_Evento` = `"FACTURA_VENCIDA"`
  - `Tabla` = `"Facturas_Obra"`
  - `Registro_ID` = `[Factura_ID]`
  - `Obra_ID` = `[Obra_ID]`
  - `Usuario` = `""`
  - `Resumen` = `"Factura "&[Nro_Factura]&" ("&[Obra_ID].[Codigo]&") vencida hace "&[Dias_Vencida]&" días; saldo S/ "&TEXT([Saldo_Factura],"0.00")`
  - `Procesado` = `"No"`
  - `Procesado_En` = `""`
  - `Canal` = `"Ambos"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** el `Evento_ID` es único por factura.
- **Prueba +:** se verifica con FAC-B02.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver FAC-B02.
- **Si falla:** ver FAC-B02.

#### FAC-A04 · `A_Factura_Marcar_Vencida` · Gestión · Facturas_Obra · Auxiliar
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Depende de:** —
- **For a record of this table:** `Facturas_Obra`
- **Action name:** `A_Factura_Marcar_Vencida`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Notificado_Vencida` = `"Si"`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** poner el mismo valor dos veces no cambia nada.
- **Prueba +:** se verifica con FAC-B02.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver FAC-B02.
- **Si falla:** ver FAC-B02.

### 11.4 Bots

#### FAC-B01 · `B_Factura_Por_Vencer` · Gestión · Facturas_Obra · Bot programado
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 07:20
  - Time zone: America/Lima
- **Depende de:** FAC-A02, LOG-B01
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Facturas_Obra`
     - Referenced Rows: `SELECT(Facturas_Obra[Factura_ID],AND([Estado]="Vigente",[Estado_Pago]<>"Pagada",[Fecha_Vencimiento]>=TODAY(),([Fecha_Vencimiento]-TODAY())<=3,ISBLANK(LOOKUP("FACTURA_POR_VENCER|"&[Factura_ID],"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Factura_Log_Por_Vencer`
     - Nota: Activar **Trigger other bots** (⚠ V10).
- **Datos que escribe:** una fila en `Log_Eventos` por factura.
- **Idempotencia:** la ventana "vence en 3 días o menos" más el `Evento_ID` único por factura garantizan un solo aviso, y si el bot no corrió el día exacto, avisa al día siguiente en vez de omitirla.
- **Límites del plan Core:** una ejecución diaria; un correo por factura.
- **Prueba +:** una factura `Vigente` con saldo y `Fecha_Vencimiento` dentro de 3 días: un evento `FACTURA_POR_VENCER` y un correo a Gestión.
- **Prueba −:** una factura `Pagada`, `Anulada`, ya vencida o que vence en más de 3 días: no genera evento.
- **Repetición:** ejecutarlo dos veces no crea un segundo evento.
- **Si falla:** si el evento aparece y el correo no llega, ver 13.5.

#### FAC-B02 · `B_Factura_Vencida` · Gestión · Facturas_Obra · Bot programado
- **App · Tabla:** OXY Gestión · `Facturas_Obra`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 07:25
  - Time zone: America/Lima
- **Depende de:** FAC-A03, FAC-A04, LOG-B01, LOG-B02
- **Process:**
  registrar primero y marcar después.
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Facturas_Obra`
     - Referenced Rows: `SELECT(Facturas_Obra[Factura_ID],AND([Estado]="Vigente",[Vencida],[Notificado_Vencida]="No",ISBLANK(LOOKUP("FACTURA_VENCIDA|"&[Factura_ID],"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Factura_Log_Vencida`
  2. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Facturas_Obra`
     - Referenced Rows: `SELECT(Facturas_Obra[Factura_ID],AND([Estado]="Vigente",[Vencida],[Notificado_Vencida]="No"))`
     - Referenced Action: `A_Factura_Marcar_Vencida`
  Nota: Activar **Trigger other bots** (⚠ V10).
- **Datos que escribe:** una fila en `Log_Eventos` y `Facturas_Obra.Notificado_Vencida`.
- **Idempotencia:** el evento es único por factura y la factura queda marcada. Si la corrida se corta entre pasos, la siguiente marca sin duplicar el evento.
- **Límites del plan Core:** una ejecución diaria; un correo y un push por factura que vence.
- **Prueba +:** una factura `Vigente` con saldo y `Fecha_Vencimiento` anterior a hoy: `Notificado_Vencida = "Si"`, un evento `FACTURA_VENCIDA` y los avisos.
- **Prueba −:** una factura pagada en su totalidad, anulada o ya marcada: no genera evento.
- **Repetición:** ejecutarlo dos veces no duplica.
- **Si falla:** en `Monitor` ver en qué paso quedó y volver a ejecutar el bot; es seguro.

### 11.5 Criterios de salida de Facturas

- [ ] Configuración de 11.1 aplicada; el tope de facturación (`Total`) probado con una cuenta Gestión y con la de Gerencia.
- [ ] FAC-A01 a FAC-A04 y FAC-B01/B02 guardan sin errores.
- [ ] Tramo de facturación y cobranza de E2E-1 ejecutado con resultado registrado.
- [ ] V04, V13 y V21 cerradas.

---

## 12. Alertas (OXY Gestión)

Las alertas son filas de `Alertas` que Gestión reconoce o resuelve desde la app. Este documento construye las acciones de atención y los tres procesos programados de alertas de operación (obra sin gastos, obra sin avance, rezago de facturación). Las alertas de consumo, CPI y demás reglas de indicadores las crean los procesos descritos en `OXY_Propuesta_Dashboard_Indicadores.md`.

### 12.1 Reglas comunes

- **Clave:** `Alerta_ID = Regla|Obra_ID|yyyy-MM-dd`. Una regla genera como máximo una alerta por obra y por día. Mientras la condición siga cumpliéndose, el proceso crea una alerta nueva cada día; es intencional (recordatorio diario) y Gestión la cierra con *Resolver*.
- **Umbrales:** se leen siempre de `Metas_KPI` (`Umbral_Ambar` y `Umbral_Rojo`), nunca se escriben dentro de las expresiones. Las tres reglas son *Menor_Mejor*: ámbar si el valor supera `Umbral_Ambar`; rojo si supera `Umbral_Rojo`. La lectura de `Metas_KPI` desde una acción auxiliar se prueba en V20.
- **Valores de `Severidad`:** `Info`, `Ambar`, `Rojo` (sin tilde, como en el modelo de datos).
- **Estado inicial:** `Abierta`. `Reconocida_Por` y `Reconocida_En` quedan vacíos hasta que alguien la reconoce.
- **Tablas:** `Alertas`, `Metas_KPI` y `Obras` incluidas en OXY Gestión. `Alertas` permite *Adds* y *Updates*, sin *Deletes*.

### 12.2 Preparación

1. Filas de `Metas_KPI` para `DIAS_SIN_GASTOS`, `DIAS_SIN_AVANCE` y `REZAGO_FACTURACION_PP` con sus umbrales (valores iniciales en el modelo de datos).
2. Virtuales de `Obras` `Dias_Sin_Gastos`, `Dias_Sin_Avance` y `Rezago_Facturacion_pp` creadas según el `_Diccionario`.
3. Orden de construcción: ALE-A01 a ALE-A05; luego ALE-B01 a ALE-B04 (ALE-B04 puede ir antes que los otros tres).

### 12.3 Acciones

#### ALE-A01 · `A_Reconocer_Alerta` · Gestión · Alertas · Acción visible
- **App · Tabla:** OXY Gestión · `Alertas`. Si la app OXY Dashboard ofrece *Reconocer*, se crea también allí con la misma configuración.
- **Depende de:** —
- **For a record of this table:** `Alertas`
- **Action name:** `A_Reconocer_Alerta`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Reconocida"`
  - `Reconocida_Por` = `USEREMAIL()`
  - `Reconocida_En` = `NOW()`
- **Only if this condition is true:** `AND([Estado]="Abierta",AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`
- **Needs confirmation?:** No
- **Position:** Prominent
- **Display name:** Reconocer
- **Idempotencia:** el estado deja de ser `Abierta`.
- **Prueba +:** una alerta `Abierta`: queda `Reconocida` con el usuario y la hora.
- **Prueba −:** una alerta `Reconocida` o `Resuelta`: no aparece. Con una cuenta Campo no existe la tabla.
- **Repetición:** el botón desaparece.
- **Si falla:** si el botón no aparece, comprobar que `Alertas` permite *Updates* en la app.

#### ALE-A02 · `A_Resolver_Alerta` · Gestión · Alertas · Acción visible
- **App · Tabla:** OXY Gestión · `Alertas` (y OXY Dashboard si ofrece la atención de alertas)
- **Depende de:** —
- **For a record of this table:** `Alertas`
- **Action name:** `A_Resolver_Alerta`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Resuelta"`
- **Only if this condition is true:** `AND(IN([Estado],LIST("Abierta","Reconocida")),AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")))`
- **Needs confirmation?:** No
- **Position:** Prominent
- **Display name:** Resolver
- **Idempotencia:** el estado deja de ser `Abierta` o `Reconocida`.
- **Prueba +:** una alerta `Abierta` o `Reconocida` queda `Resuelta`.
- **Prueba −:** una alerta ya `Resuelta`: no aparece.
- **Repetición:** el botón desaparece.
- **Si falla:** ver ALE-A01.

#### ALE-A03 · `A_Alerta_Sin_Gastos` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Alerta_Sin_Gastos`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Alertas`
- **Set these columns:**
  - `Alerta_ID` = `"OBRA_SIN_GASTOS|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Regla` = `"OBRA_SIN_GASTOS"`
  - `Severidad` = `IF([Dias_Sin_Gastos]>LOOKUP("DIAS_SIN_GASTOS","Metas_KPI","KPI","Umbral_Rojo"),"Rojo","Ambar")` ⚠ V20
  - `Obra_ID` = `[Obra_ID]`
  - `Mensaje` = `[Codigo]&": "&[Dias_Sin_Gastos]&" días sin gastos ni horas registradas"`
  - `Estado` = `"Abierta"`
  - `Reconocida_Por` = `""`
  - `Reconocida_En` = `""`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** `Alerta_ID` con fecha; ALE-B01 excluye a las obras que ya tienen la alerta de hoy.
- **Prueba +:** se verifica con ALE-B01.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ALE-B01.
- **Si falla:** ver ALE-B01.

#### ALE-A04 · `A_Alerta_Sin_Avance` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Alerta_Sin_Avance`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Alertas`
- **Set these columns:**
  - `Alerta_ID` = `"OBRA_SIN_AVANCE|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Regla` = `"OBRA_SIN_AVANCE"`
  - `Severidad` = `IF([Dias_Sin_Avance]>LOOKUP("DIAS_SIN_AVANCE","Metas_KPI","KPI","Umbral_Rojo"),"Rojo","Ambar")` ⚠ V20
  - `Obra_ID` = `[Obra_ID]`
  - `Mensaje` = `[Codigo]&": "&[Dias_Sin_Avance]&" días sin registrar avance físico"`
  - `Estado` = `"Abierta"`
  - `Reconocida_Por` = `""`
  - `Reconocida_En` = `""`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** igual que ALE-A03.
- **Prueba +:** se verifica con ALE-B02.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ALE-B02.
- **Si falla:** ver ALE-B02.

#### ALE-A05 · `A_Alerta_Rezago_Facturacion` · Gestión · Obras · Auxiliar
- **App · Tabla:** OXY Gestión · `Obras`
- **Depende de:** —
- **For a record of this table:** `Obras`
- **Action name:** `A_Alerta_Rezago_Facturacion`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Alertas`
- **Set these columns:**
  - `Alerta_ID` = `"REZAGO_FACTURACION|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd")` ⚠ V21
  - `Fecha_Hora` = `NOW()`
  - `Regla` = `"REZAGO_FACTURACION"`
  - `Severidad` = `IF([Rezago_Facturacion_pp]>LOOKUP("REZAGO_FACTURACION_PP","Metas_KPI","KPI","Umbral_Rojo"),"Rojo","Ambar")` ⚠ V20
  - `Obra_ID` = `[Obra_ID]`
  - `Mensaje` = `[Codigo]&": el avance físico supera lo facturado en "&TEXT([Rezago_Facturacion_pp],"0.0")&" puntos"`
  - `Estado` = `"Abierta"`
  - `Reconocida_Por` = `""`
  - `Reconocida_En` = `""`
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** igual que ALE-A03.
- **Prueba +:** se verifica con ALE-B03.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver ALE-B03.
- **Si falla:** ver ALE-B03.

### 12.4 Bots

#### ALE-B01 · `B_Obra_Sin_Gastos` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 07:15
  - Time zone: America/Lima
- **Depende de:** ALE-A03, ALE-B04
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Estado]="En ejecucion",[Dias_Sin_Gastos]>LOOKUP("DIAS_SIN_GASTOS","Metas_KPI","KPI","Umbral_Ambar"),ISBLANK(LOOKUP("OBRA_SIN_GASTOS|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Alertas","Alerta_ID","Alerta_ID"))))` ⚠ V20
     - Referenced Action: `A_Alerta_Sin_Gastos`
     - Nota: Activar **Trigger other bots** para que ALE-B04 notifique la alerta nueva (⚠ V10).
- **Datos que escribe:** una fila en `Alertas` por obra y por día.
- **Idempotencia:** `Alerta_ID` con fecha y exclusión de las obras que ya tienen la de hoy.
- **Límites del plan Core:** una ejecución diaria; un push por alerta y un correo si es roja.
- **Prueba +:** una obra `En ejecucion` cuyo último gasto u hora supera `Umbral_Ambar` días: aparece una alerta `OBRA_SIN_GASTOS` `Abierta`, ámbar (o roja si supera `Umbral_Rojo`).
- **Prueba −:** una obra con gasto reciente, o `Pausada`/`Terminada`: no genera alerta.
- **Repetición:** ejecutarlo dos veces el mismo día no crea una segunda alerta.
- **Si falla:** si la severidad sale siempre ámbar, revisar V20 (lectura de `Metas_KPI`).

#### ALE-B02 · `B_Obra_Sin_Avance` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 07:15
  - Time zone: America/Lima
- **Depende de:** ALE-A04, ALE-B04
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND([Estado]="En ejecucion",[Dias_Sin_Avance]>LOOKUP("DIAS_SIN_AVANCE","Metas_KPI","KPI","Umbral_Ambar"),ISBLANK(LOOKUP("OBRA_SIN_AVANCE|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Alertas","Alerta_ID","Alerta_ID"))))` ⚠ V20
     - Referenced Action: `A_Alerta_Sin_Avance`
     - Nota: Activar **Trigger other bots** (⚠ V10). El avance se registra a diario; con el umbral ámbar inicial la alerta sale desde el tercer día sin avance.
- **Datos que escribe:** una fila en `Alertas` por obra y por día.
- **Idempotencia:** igual que ALE-B01.
- **Límites del plan Core:** una ejecución diaria; un push por alerta.
- **Prueba +:** una obra `En ejecucion` con el último avance de hace más días que `Umbral_Ambar`: alerta `OBRA_SIN_AVANCE`.
- **Prueba −:** una obra con avance de ayer: no genera alerta.
- **Repetición:** igual que ALE-B01.
- **Si falla:** igual que ALE-B01.

#### ALE-B03 · `B_Rezago_Facturacion` · Gestión · Obras · Bot programado
- **App · Tabla:** OXY Gestión · `Obras`
- **Event:**
  - Event type: Scheduled ⚠ V13
  - Schedule: Daily
  - Time: 07:15
  - Time zone: America/Lima
- **Depende de:** ALE-A05, ALE-B04
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Obras`
     - Referenced Rows: `SELECT(Obras[Obra_ID],AND(IN([Estado],LIST("En ejecucion","Terminada")),[Rezago_Facturacion_pp]>LOOKUP("REZAGO_FACTURACION_PP","Metas_KPI","KPI","Umbral_Ambar"),ISBLANK(LOOKUP("REZAGO_FACTURACION|"&[Obra_ID]&"|"&TEXT(TODAY(),"yyyy-MM-dd"),"Alertas","Alerta_ID","Alerta_ID"))))` ⚠ V20
     - Referenced Action: `A_Alerta_Rezago_Facturacion`
     - Nota: Activar **Trigger other bots** (⚠ V10).
- **Datos que escribe:** una fila en `Alertas` por obra y por día.
- **Idempotencia:** igual que ALE-B01.
- **Límites del plan Core:** una ejecución diaria; un push por alerta y un correo si es roja.
- **Prueba +:** una obra con avance físico de 70 % y 30 % facturado (rezago de 40 puntos): alerta `REZAGO_FACTURACION` roja.
- **Prueba −:** una obra con rezago por debajo del umbral ámbar: no genera alerta.
- **Repetición:** igual que ALE-B01.
- **Si falla:** igual que ALE-B01.

#### ALE-B04 · `B_Notif_Alerta` · Gestión · Alertas · Bot de evento
- **App · Tabla:** OXY Gestión · `Alertas`. Si los procesos que crean alertas viven en otra app (por ejemplo OXY Dashboard), crear el mismo bot también en esa app (⚠ V18).
- **Event:**
  - Event type: Data change
  - Table: `Alertas`
  - Data change type: Adds only
  - Condition: (sin condición)
- **Depende de:** —
- **Process:**
  1. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `<<[Mensaje]>>` (⚠ V14)
  2. Step type: Send an email (paso condicional ⚠ V22)
     - Step condition: `[Severidad]="Rojo"`
     - To: `SELECT(Trabajadores[Email],AND([Activo]=TRUE,OR(IN([Rol],LIST("Admin","Gerencia")),[Trabajador_ID]=[_THISROW].[Obra_ID].[Responsable_ID])))` ⚠ V03 (Gestión y el responsable de la obra)
     - Subject: `Alerta roja: <<[Regla]>>`
     - Body: texto con `<<[Mensaje]>>`.
  Nota: Si V22 falla, mover el paso 2 a un segundo bot con la condición del evento `[Severidad]="Rojo"`.
- **Datos que escribe:** ninguno.
- **Idempotencia:** una vez por alta de alerta.
- **Límites del plan Core:** un push por alerta; los correos solo para alertas rojas, para no saturar la cuota.
- **Prueba +:** una alerta ámbar nueva envía solo push; una roja envía push y correo a Gestión y al responsable.
- **Prueba −:** reconocer o resolver una alerta (ALE-A01, ALE-A02) no envía nada.
- **Repetición:** crear otra alerta envía otro aviso.
- **Si falla:** ver 13.5.

### 12.5 Criterios de salida de Alertas

- [ ] ALE-A01 a ALE-A05 y ALE-B01 a ALE-B04 guardan sin errores.
- [ ] Escenario E2E-8 ejecutado con resultado registrado.
- [ ] V13, V18, V20, V21 y V22 cerradas.

---

## 13. Log y notificaciones

### 13.1 Contrato del log

`Log_Eventos` es una bitácora que **solo escriben los bots y las acciones auxiliares**: nadie la edita ni la borra desde la app. Hay dos formas de producir un evento:

| Origen | Quién notifica | `Procesado` al crear | `Evento_ID` |
|---|---|---|---|
| **Bot de evento** (cambio de datos en la app) | El mismo bot, con sus pasos de push o correo | `Si` | `UNIQUEID()` |
| **Bot programado** (vence, atrasa, recuerda, cobranza, facturas) | Los bots LOG-B01 (correo) y LOG-B02 (push), que reaccionan al alta del evento | `No` | Determinista: incluye el identificador del registro y, si el hecho se repite, la fecha |

Reglas:

1. Un evento de un bot programado siempre usa `Evento_ID` determinista y se registra solo si no existe (`ISBLANK(LOOKUP(<Evento_ID>,"Log_Eventos","Evento_ID","Evento_ID"))`). Así una corrida repetida o cortada no duplica el aviso.
2. `Tipo_Evento` es un texto en mayúsculas del catálogo de 13.2.
3. `Canal` dice por dónde sale el aviso (`Correo`, `Push`, `Ambos`). Cuando un evento nace con `Procesado = "No"`, LOG-B01 y LOG-B02 deciden según `Canal`.
4. `Procesado_En` lo llenan los bots LOG; en los eventos que ya notificó su propio bot se llena al crear.

### 13.2 Catálogo de eventos

| Evento | Lo produce | Destinatarios | Canal |
|---|---|---|---|
| `GASTO_CREADO` | GAS-B01 | Gerencia | Push |
| `GASTO_ANULADO` | GAS-B02 | Gestión | Push y correo |
| `CREDITO_FISCAL_CAMBIADO` | GAS-B03 | Gestión | Push |
| `GASTO_PAGADO` | GAS-B04 | Gestión | Push |
| `GASTO_SOBRE_PLANIFICADO` | GAS-B05 | Gestión | Push y correo |
| `HORAS_PENDIENTES` | HOR-B01 | Gestión | Push |
| `PROFORMA_ENVIADA`, `PROFORMA_ACEPTADA`, `PROFORMA_RECHAZADA` | PRO-B03 (registro) y PRO-B04 (aviso) | Gestión | Correo |
| `PROFORMA_ANULADA`, `PROFORMA_ELIMINADA` | PRO-B03 | — (solo registro) | — |
| `PROFORMA_VENCIDA` | PRO-A11 desde PRO-B01 (registro) y PRO-B04 (aviso) | Gestión | Correo |
| `OBRA_CREADA` | OBR-B01 | Gestión (push) y responsable (correo) | Ambos |
| `OBRA_ESTADO_CAMBIADO` | OBR-B02 | Gestión (push) y responsable (correo) | Ambos |
| `OBRA_CERRADA` | OBR-B03 | Gestión | Push |
| `OBRA_ATRASADA` | OBR-A08 desde OBR-B04 | Gestión y responsable | Correo |
| `ABONO_CREADO` | ABO-B01 | Gestión | Push y correo |
| `ABONO_ANULADO` | ABO-B02 | Gestión | Push y correo |
| `COBRANZA_COMPLETA` | ABO-A03 desde ABO-B03 | Gestión | Correo y push |
| `COBRANZA_REABIERTA` | ABO-A05 desde ABO-B04 | Gestión | Correo y push |
| `RECORDATORIO_COBRANZA` | ABO-A06 desde ABO-B05 | Gestión | Correo |
| `FACTURA_POR_VENCER` | FAC-A02 desde FAC-B01 | Gestión | Correo |
| `FACTURA_VENCIDA` | FAC-A03 desde FAC-B02 | Gestión | Correo y push |

La aprobación de horas (HOR-A01) **no genera evento**: es una decisión abierta (sección 17). Las alertas de la sección 12 no pasan por el log; se notifican con ALE-B04.

### 13.3 Bots de notificación del log

#### LOG-B01 · `B_Notif_Log_Correo` · Gestión · Log_Eventos · Bot de evento
- **App · Tabla:** OXY Gestión · `Log_Eventos` (incluida con *Adds*)
- **Event:**
  - Event type: Data change
  - Table: `Log_Eventos`
  - Data change type: Adds only
  - Condition: `AND([Procesado]="No",IN([Canal],LIST("Correo","Ambos")))`
- **Depende de:** —. Lo disparan los bots programados que escriben eventos con `Procesado = "No"` (obras atrasadas, cobranza, recordatorios y facturas) y exige que esos bots tengan activo *Trigger other bots*
- **Process:**
  1. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND([Activo]=TRUE,OR(IN([Rol],LIST("Admin","Gerencia")),AND(IN([_THISROW].[Tipo_Evento],LIST("OBRA_ATRASADA")),[Trabajador_ID]=LOOKUP([_THISROW].[Obra_ID],"Obras","Obra_ID","Responsable_ID")))))` ⚠ V03
     - Subject: `<<[Tipo_Evento]>>: <<[Resumen]>>`
     - Body: texto con `<<[Resumen]>>`, la fecha (`<<[Fecha_Hora]>>`) y la obra (`<<[Obra_ID]>>`).
  2. Step type: Send an email (paso condicional ⚠ V22)
     - Step condition: `AND([Tipo_Evento]="COBRANZA_COMPLETA",ISNOTBLANK(LOOKUP("OXY","Compania","Compania_ID","Emails_Cobranza")))`
     - To: `SPLIT(LOOKUP("OXY","Compania","Compania_ID","Emails_Cobranza"),",")`
     - Subject: el mismo del paso 1
     - Body: el mismo del paso 1
     - Nota: se omite si `Compania.Emails_Cobranza` está vacío.
  3. Step type: Run a data action → Set row values
     - Table: (esta fila)
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
     - Nota: si el evento tiene `Canal = "Ambos"`, LOG-B02 hace lo mismo con su propio paso.
- **Datos que escribe:** `Log_Eventos.Procesado` y `Procesado_En`.
- **Idempotencia:** la condición exige `Procesado = "No"`; al marcarlo, el evento ya no vuelve a cumplirla. Un evento solo se crea una vez por su `Evento_ID`.
- **Límites del plan Core:** un correo por evento (y uno más para `COBRANZA_COMPLETA` con `Compania.Emails_Cobranza`). La cuota diaria de correos es compartida por todos los bots: ver 13.5.
- **Prueba +:** crear a mano un evento de prueba con `Procesado = "No"`, `Canal = "Correo"` y una obra: llega un correo a Gestión (y al responsable si el tipo es `OBRA_ATRASADA`); `Procesado` queda en `Si`.
- **Prueba −:** un evento de bot de evento (`Procesado = "Si"`) no envía correo; uno con `Canal = "Push"` tampoco.
- **Repetición:** no se reenvía mientras `Procesado` sea `Si`.
- **Si falla:** si los eventos se crean y no hay correo, comprobar en `Monitor` que LOG-B01 se ejecutó. Si no lo hizo, falta **Trigger other bots** en el bot programado de origen (⚠ V10).

#### LOG-B02 · `B_Notif_Log_Push` · Gestión · Log_Eventos · Bot de evento
- **App · Tabla:** OXY Gestión · `Log_Eventos`
- **Event:**
  - Event type: Data change
  - Table: `Log_Eventos`
  - Data change type: Adds only
  - Condition: `AND([Procesado]="No",IN([Canal],LIST("Push","Ambos")))`
- **Depende de:** —. Lo disparan los mismos bots programados que disparan al bot de correo
- **Process:**
  1. Step type: Send a push notification
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))`
     - Message: `<<[Resumen]>>` (⚠ V14)
  2. Step type: Run a data action → Set row values
     - Table: (esta fila)
     - `Procesado` = `"Si"`
     - `Procesado_En` = `NOW()`
  Nota: Con `Canal = "Ambos"`, los dos bots se disparan al alta del evento (la condición se evalúa en el alta, con `Procesado = "No"`); es correcto que los dos envíen.
- **Datos que escribe:** `Log_Eventos.Procesado` y `Procesado_En`.
- **Idempotencia:** igual que LOG-B01.
- **Límites del plan Core:** un push por evento. Un push solo llega a quien tiene instalada **OXY Gestión**: el responsable de una obra que usa solo OXY Campo no lo recibe; para él existe el correo.
- **Prueba +:** un evento de prueba con `Procesado = "No"` y `Canal = "Push"`: llega el push a Gestión y `Procesado` queda en `Si`.
- **Prueba −:** un evento con `Canal = "Correo"` no envía push.
- **Repetición:** igual que LOG-B01.
- **Si falla:** igual que LOG-B01.

### 13.4 Reglas de destinatarios

| Quién | Cómo se calcula | Por dónde |
|---|---|---|
| Gestión | `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Admin","Gerencia")),[Activo]=TRUE))` (Admin y Gerencia activos) | Push y correo |
| Gerencia | `SELECT(Trabajadores[Email],AND([Rol]="Gerencia",[Activo]=TRUE))` | Push y correo |
| Responsable de la obra | Correo del responsable (`[Obra_ID].[Responsable_ID].[Email]`) | **Solo correo**; el push solo llega a quien tiene instalada la app donde vive el bot |

- Todos los destinatarios se calculan en el momento del envío a partir de `Trabajadores`; un usuario con `Activo = No` deja de recibir avisos sin tocar los bots.
- La lista de `Para` en los correos se construye con `SELECT(...)` sobre `Trabajadores` (⚠ V03).
- Para que Gerencia reciba los push de gastos que se registran desde Campo, debe tener instalada OXY Campo (no necesita usarla).

### 13.5 "El proceso corrió" no es "el destinatario lo recibió"

Un bot en `Monitor` con estado correcto solo prueba que AppSheet ejecutó los pasos. No prueba que el correo o el push llegaron. Por eso:

- **Si no llegó un correo:** revisar en este orden (1) que el evento existe en `Log_Eventos`; (2) que el bot de notificación se ejecutó en `Monitor`; (3) que el destinatario está activo y con el correo escrito igual que en su cuenta Google; (4) spam y filtros del destinatario; (5) la cuota diaria de correos del plan Core.
- **Si no llegó un push:** (1) que el destinatario tiene instalada **la app donde vive el bot**; (2) que inició sesión y aceptó notificaciones en el teléfono; (3) que el bot se ejecutó.
- Un aviso que no llegó **no se reenvía editando ni borrando el log** (nada se borra): se corrige la causa y el siguiente evento sale con normalidad. Si hace falta avisar de un hecho ya registrado, se avisa por otro medio y se anota en el registro de validaciones.

---

## 14. Seguridad y estructura por app

En AppSheet Core la seguridad real tiene tres barreras, en este orden: **quién puede abrir la app**, **qué tablas lleva cada app** y **qué filas de cada tabla sincroniza al dispositivo** (*security filters*). Todo lo demás (`Show?`, `Editable?`, `Only if`) es interfaz (sección 1.3).

### 14.1 Quién puede abrir cada app

1. En cada app, activar **Require user sign-in** (inicio de sesión obligatorio con Google). Ninguna app se deja pública.
2. Restringir el acceso por lista de usuarios en la configuración de uso compartido de la app (⚠ V15 para la ruta exacta en el editor): OXY Gestión y OXY Dashboard, solo los usuarios de Gestión; OXY Campo, los usuarios de Campo y, si van a recibir sus push, los de Gerencia.
3. Una cuenta Google que no esté en `Trabajadores` pasa el inicio de sesión pero **no debe ver ningún dato** (todas las expresiones de rol fallan en falso y los filtros de 14.3 devuelven falso). Se prueba en 14.6 (⚠ V17).
4. Dar de baja a una persona = poner `Activo = No` en `Trabajadores` (y quitarla de la lista de usuarios de la app). Ninguna acción ni filtro la reconoce desde ese momento.

### 14.2 Tablas por app

| Tabla | OXY Campo | OXY Gestión |
|---|---|---|
| `Obras` | Lectura (solo obras asignadas) | Todo + acciones |
| `Asignaciones_Obra` | Lectura (equipos de sus obras) | Todo |
| `Gastos_Obra` | Altas; edita y anula solo los propios (24 h) | Todo |
| `Registro_Horas` | Altas y lectura de lo propio | Todo + aprobar o rechazar |
| `Avances_Obra` | Altas y edición de las obras asignadas | Todo |
| `Proveedores` | Altas y lectura | Todo |
| `Categorias_Costo` | Lectura | Todo |
| `Tipos_Costo` | Lectura (solo `Visible_Campo = "Si"`) | Todo |
| `Trabajadores` | Lectura (solo activos) | Todo |
| `Areas_Compania` | Lectura (si una fórmula la necesita) | Todo |
| `Compania` | Lectura (una sola fila; ver 14.4) | Todo (*Updates*; sin *Adds* ni *Deletes*) |
| `Configuracion` | **No incluida** (si una fórmula de Campo la necesita, incluirla de solo lectura) | Todo |
| `Proformas`, `Proforma_Conceptos`, `Proforma_Planificacion` | **No incluidas** | Todo |
| `Clientes`, `Contactos_Cliente` | **No incluidas** | Todo |
| `Facturas_Obra`, `Abonos_Obra`, `Medios_Pago` | **No incluidas** | Todo |
| `Tarifas_Trabajador` | **No incluida** | Todo |
| `Log_Eventos` | **No incluida** | Altas y lectura |
| `Alertas`, `Metas_KPI`, `Jobs_Control` | **No incluidas** | Todo |
| `Snap_*` | **No incluidas** | Lectura (si algún slice las usa) |

La app `OXY Dashboard` lleva solo las tablas que describe `OXY_Propuesta_Dashboard_Indicadores.md` (snapshots, alertas, metas y catálogos ligeros) y es de solo lectura, salvo la atención de alertas.

### 14.3 Security filters

Se crean en el editor, en la configuración de cada tabla de la app (*Data → Tables → tabla → Security filter*; ⚠ V15). Usan los macros de rol de la sección 1.4 y este macro adicional:

**¿Es Campo (activo)?**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))
```
**Obras asignadas al usuario** (se usa dentro de varios filtros):
```
SELECT(Asignaciones_Obra[Obra_ID],AND([Trabajador_ID]=LOOKUP(USEREMAIL(),"Trabajadores","Email","Trabajador_ID"),[Activo]=TRUE))
```

**Filtros en OXY Campo**

| Tabla | Filtro |
|---|---|
| `Obras` | `OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),IN([Estado],LIST("Por iniciar","En ejecucion","Pausada","Terminada")),IN([Obra_ID],SELECT(Asignaciones_Obra[Obra_ID],AND([Trabajador_ID]=LOOKUP(USEREMAIL(),"Trabajadores","Email","Trabajador_ID"),[Activo]=TRUE)))))` ⚠ V16 |
| `Asignaciones_Obra` | `OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),IN([Obra_ID],SELECT(Asignaciones_Obra[Obra_ID],AND([Trabajador_ID]=LOOKUP(USEREMAIL(),"Trabajadores","Email","Trabajador_ID"),[Activo]=TRUE)))))` ⚠ V16. Se necesita el equipo completo de cada obra para el `Valid if` de `Trabajador_ID` en horas |
| `Gastos_Obra` | `OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Registrado_Por]=USEREMAIL()))` |
| `Registro_Horas` | `OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),[Registrado_Por]=USEREMAIL()))` |
| `Avances_Obra` | `OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),IN([Obra_ID],SELECT(Asignaciones_Obra[Obra_ID],AND([Trabajador_ID]=LOOKUP(USEREMAIL(),"Trabajadores","Email","Trabajador_ID"),[Activo]=TRUE)))))`. Se filtra por obra y no por autor, porque la regla "el avance acumulado no puede bajar" necesita ver los avances de los demás |
| `Trabajadores` | `AND([Activo]=TRUE,OR(AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo")),AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol")="Campo",LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))))` |
| `Tipos_Costo` | `[Visible_Campo]="Si"` |

`Proveedores`, `Categorias_Costo` y `Areas_Compania` se dejan sin filtro: son catálogos sin datos económicos.

**Filtros en OXY Gestión** (segunda barrera, además de la lista de usuarios): en `Facturas_Obra`, `Abonos_Obra`, `Tarifas_Trabajador`, `Configuracion`, `Log_Eventos`, `Alertas`, `Metas_KPI`, `Proformas`, `Proforma_Conceptos` y `Proforma_Planificacion`, el filtro `AND(IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")),LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"))`.

### 14.4 Riesgo residual: lo que llega al teléfono de Campo

Una columna oculta con `Show?` **sí se sincroniza** al dispositivo, y un *slice* con menos columnas tampoco lo evita. Por eso:

| Dato que llega a Campo | Quién lo recibe | Riesgo | Opciones |
|---|---|---|---|
| Columnas comerciales y de presupuesto de `Obras` (`Precio_Neto`, `Total_Cobrar_Base`, `Costo_Planificado_Base`, `IGV_Base`) | Cada usuario de Campo, solo de sus obras asignadas | Medio: ve el precio y el presupuesto de costo de su obra | **(a)** Aceptarlo, porque son sus propias obras. **(b)** Mover esas columnas a una tabla aparte, p. ej. `Obras_Finanzas`, que no se incluye en Campo: es un cambio en el modelo de datos y en las virtuales de `Obras`. |
| Columnas de costo de `Registro_Horas` (`Costo_Hora`, `Costo_Hora_Extra`, `Costo_Total`) | Cada usuario de Campo, solo de sus propios registros | Bajo: ve su propia tarifa | Aceptarlo, o dejar de copiar la tarifa a la fila y calcularla solo en una virtual de Gestión. |
| Datos de `Trabajadores` (nombre, rol, correo) | Todos los usuarios de Campo, solo de personas activas | Bajo | Aceptarlo. |
| Fila de `Compania` (cuentas bancarias, condiciones comerciales, datos fiscales y los correos de `Emails_Cobranza`) | Todos los usuarios de Campo | Bajo a medio: ven las cuentas bancarias y los correos de Gestión que reciben el aviso de cobranza | **(a)** Aceptarlo: Campo necesita datos de la empresa en sus vistas. **(b)** Sacar `Emails_Cobranza` y las cuentas bancarias a otra tabla que no se incluya en Campo. |

**Esto es una decisión abierta** (sección 17): hasta que se tome, la opción (a) es la configuración vigente. Ninguna de las dos barreras (filtros y lista de usuarios) protege los datos de un dispositivo robado o de una persona de Campo que consulte la aplicación con otras herramientas; para ese caso, el control es quitarle el acceso (14.1) y bloquear el dispositivo.

### 14.5 Permisos del Sheet y de Drive

1. `OXYData` compartido **solo con el dueño** de los datos. Los usuarios de las apps **no** necesitan acceso al Sheet: la app lee y escribe con la cuenta del dueño.
2. Las carpetas de archivos (`Proformas_Files`, `Gastos_Obra_Images`, etc.) igual: solo el dueño. Los archivos se abren desde la app.
3. Quien edite el Sheet directamente puede saltarse todas las reglas de este documento. Las ediciones directas al Sheet se limitan al dueño y a la carga de datos demo; cualquier cambio de estructura pasa primero por el modelo de datos.
4. Hacer una copia de seguridad del Sheet antes de cualquier cambio de estructura o carga masiva.

### 14.6 Pruebas de seguridad con las seis cuentas

Cada fila se ejecuta con la cuenta indicada, abriendo la app **en un teléfono o navegador distinto del que usa el programador**, con la sesión recién iniciada.

| Cuenta | Qué comprobar | Resultado esperado |
|---|---|---|
| Gerencia | OXY Gestión: todas las tablas; acción *Cerrar con saldo*; facturar por encima del total a cobrar | Ve todo; las acciones y el tope de facturación le permiten operar |
| Admin | OXY Gestión: las mismas tablas | Igual que Gerencia, salvo *Cerrar con saldo* y sobre-facturar, que no le aparecen ni le dejan |
| Campo asignado a una obra | OXY Campo: lista de obras, gastos, horas, avance | Ve solo las obras asignadas; solo sus gastos y horas; no ve proformas, facturas, abonos ni tarifas; en Gastos solo elige tipos Material y Consumible |
| Campo sin asignación | OXY Campo | Lista de obras vacía; no puede registrar nada |
| Campo inactivo (`Activo = No`) | OXY Campo y expresiones de rol | No ve datos de ninguna tabla; ninguna acción le aparece |
| Cuenta que no está en `Trabajadores` | Abrir OXY Campo y OXY Gestión | No ve ningún dato (o la app no la deja entrar) ⚠ V17 |

Además: con la cuenta de Campo asignado, abrir en el teléfono el detalle de una obra y confirmar qué columnas comerciales se ven (14.4); anotar el resultado en el registro de validaciones.

### 14.7 Criterios de salida de Seguridad

- [ ] Inicio de sesión obligatorio y lista de usuarios configurados en las tres apps.
- [ ] Tablas de cada app según 14.2; sin *Deletes* en tablas transaccionales.
- [ ] Filtros de 14.3 creados y probados con las seis cuentas de 14.6.
- [ ] Decisión sobre 14.4 registrada en la sección 17.
- [ ] V15, V16 y V17 cerradas.

---

## 15. Pruebas

### 15.1 Formato y reglas

- Cada ficha trae sus pruebas unitarias (**Prueba +**, **Prueba −**, **Repetición**). Se ejecutan al terminar la ficha y se anota el resultado en el registro de la sección 17.
- Una prueba dice siempre: datos de partida (por su **estado**, no por su identificador), qué ejecutar y qué resultado se espera. Los identificadores citados son ejemplos.
- Los bots programados se prueban ejecutándolos a mano (`More (⋮) → Test`) sobre filas que cumplan y filas que no cumplan la condición, y se revisa el resultado en `Monitor` (⚠ V13).
- Los bots de cambio de datos se prueban provocando el evento real desde la app, no solo con *Test*.
- Una prueba con cuenta de Campo se hace con una cuenta Google distinta de la del programador (14.6).
- Antes de cada ronda de pruebas se hace una copia de `OXYData` (14.5).

### 15.2 Pruebas de humo (antes de construir, 1 a 2 horas)

Comprueban las capacidades de las que depende el diseño. Cada una remite a una validación del registro (17.1). Si una falla, se usa la alternativa de esa fila **antes** de seguir.

| N.º | Prueba | Valida |
|---|---|---|
| S01 | Crear un bot programado diario y otro semanal; ejecutarlos a mano y ver el resultado en `Monitor`; confirmar que el plan Core los permite | V13 |
| S02 | Bot *Adds* en `Gastos_Obra`, creado en cada app: un alta desde Campo y otra desde Gestión; comprobar que cada bot reacciona solo a los cambios de su app | V18 |
| S03 | Push de un bot a un teléfono con la app instalada y a otro sin ella | V02, V14 |
| S04 | Campo *Para* de un correo con lista calculada por `SELECT` sobre `Trabajadores` | V03 |
| S05 | Paso condicional en un bot (enviar correo solo si la fila cumple una condición) | V22 |
| S06 | Bot *Updates* con `[_THISROW_BEFORE]` y `[_THISROW_AFTER]` para detectar un cambio de valor | V07 |
| S07 | Un bot que dispara a otro (*Trigger other bots*), y que no se dispara a sí mismo | V10 |
| S08 | Si un paso intermedio de un bot falla, ¿los siguientes se ejecutan? | V01 |
| S09 | Acción auxiliar *Add row* con clave `Evento_ID` calculada como texto, y *Referenced Rows* con `SELECT` y `LOOKUP` de exclusión | V19, V21 |
| S10 | Confirmación con mensaje calculado según una columna | V05 |
| S11 | `Valid if` con `SELECT` sobre la misma tabla excluyendo la fila actual (número de factura, `Numero` y `Proforma_Previa_ID` de proformas); `Valid if` de `Es_Credito_Fiscal`; valor inicial en una columna oculta | V04, V08, V09 |
| S12 | Duración `"024:00:00"` en `Only if`; lectura de `Metas_KPI` desde una acción auxiliar | V12, V20 |
| S13 | *Create a new file* desde la plantilla de Google Docs `Plantilla_Proforma` con nombre propio con sello y sin sello automático; nombre de la columna inversa `Related ...` | V06, V11 |
| S14 | Un *security filter* con `SELECT` y `LOOKUP` anidados sobre una tabla de Campo; cuenta fuera de `Trabajadores` | V16, V17 |
| S15 | Rutas del editor nuevo para acciones, filtros de seguridad y lista de usuarios | V15 |

### 15.3 Escenarios de punta a punta

Se ejecutan en orden, con los datos demo y con las cuentas de 3.4. Cada paso nombra la ficha que lo prueba. Al terminar cada escenario, revisar `Log_Eventos`: debe haber **un** evento por hecho, sin duplicados.

#### E2E-1 · Camino feliz: proforma, obra, gastos, facturación, cobranza y cierre
1. **Tramo de proforma.** Con Gestión, crear una proforma `Borrador` con conceptos y planificación; generar el PDF (PRO-A10, PRO-B02) y enviarla (PRO-A01). Esperado: PDF en `Proformas_Files`, `Enviada`, eventos `PROFORMA_ENVIADA` (PRO-B03) y correo a Gestión (PRO-B04).
2. Cargar `Fecha_Aceptacion` y `Doc_Aceptacion` y aceptarla (PRO-A07). Esperado: `Aceptada`, obra `Por iniciar` con totales congelados, evento `OBRA_CREADA` (OBR-B01).
3. **Tramo de obra.** Asignar a un trabajador de Campo; iniciar la obra (OBR-A01). Esperado: `En ejecucion`, evento `OBRA_ESTADO_CAMBIADO` (OBR-B02).
4. **Tramo de gastos.** Con Campo, registrar un gasto de Material (GAS-B01); con Gestión, uno de subcontrato; marcar uno como pagado (GAS-A02, GAS-B04); superar lo planificado en un tipo (GAS-B05). Esperado: un evento por hecho; el exceso avisa por correo y push.
5. Registrar horas desde Campo (HOR-B01) y aprobarlas (HOR-A01); registrar avance (AVA-A01 es la anulación; el alta se prueba con el formulario). Esperado: `Total_Personal` y `Avance_Actual` cambian.
6. **Tramo de facturación y cobranza.** Registrar una factura de venta; registrar abonos hasta cubrir el total (ABO-B01); ejecutar la cobranza completa (ABO-B03). Esperado: `Notificado_Cobro_Completo = "Si"`, evento `COBRANZA_COMPLETA` y avisos.
7. Terminar (OBR-A04) y cerrar la obra (OBR-A06, OBR-B03). Esperado: `Cerrada`; ya no se pueden registrar movimientos en ninguna tabla hija.

#### E2E-2 · Rechazo y proforma relacionada
1. Enviar una proforma (PRO-A01) y rechazarla con motivo (PRO-A02).
2. Crear un `Borrador` nuevo con su propio `Numero`, conceptos y planificación (nada se copia solo). En el formulario elegir como `Proforma_Previa_ID` la rechazada. Comprobar que `Tipo_Relacion` pasa a ser obligatorio, que la lista de previas no incluye a la propia proforma ni a las `Z-Eliminada`, y que un `Numero` repetido se rechaza. Elegir `Tipo_Relacion` = `Revision`.
3. Enviar el nuevo `Borrador` (PRO-A01). Esperado: la rechazada **no cambia** (sigue `Rechazada`, con su motivo y su fecha) y su `Total_Relacionadas` vale 1.

#### E2E-3 · Anulaciones y eliminación
1. Anular, con motivo y con la cuenta que corresponda: una proforma `Enviada` (PRO-A03), un gasto (GAS-A01), un abono (ABO-A01), una factura sin abonos (FAC-A01) y un avance (AVA-A01). Esperado en cada caso: `Estado = Anulado` (`Anulada` en la proforma), el botón desaparece, el total de la obra se recalcula y hay un evento (`PROFORMA_ANULADA`, `GASTO_ANULADO`, `ABONO_ANULADO`). Intentar anular una factura con un abono vigente: el botón no aparece.
2. Eliminar un `Borrador` con Gestión (PRO-A04). Esperado: `Z-Eliminada`, con `Eliminada_Por` y `Fecha_Eliminacion`; evento `PROFORMA_ELIMINADA` sin correo; sale de la lista normal y aparece en la vista de eliminadas. Si era la previa de otra proforma, el `Total_Relacionadas` de esa previa baja.
3. Un `Borrador` no ofrece *Anular* y una `Enviada` no ofrece *Eliminar*.

#### E2E-4 · Vencimientos
1. Poner `Fecha_Vigencia` en el pasado en una proforma `Enviada` y ejecutar PRO-B01: pasa a `Vencida`, un evento `PROFORMA_VENCIDA` y un correo (PRO-B04). Ejecutarlo de nuevo: no hay segundo evento.
2. Crear un `Borrador` nuevo y relacionarlo con la `Vencida` (`Revision`): la `Vencida` no cambia de estado.
3. Poner una factura con vencimiento dentro de 3 días y ejecutar FAC-B01; poner otra con vencimiento pasado y ejecutar FAC-B02. Esperado: eventos `FACTURA_POR_VENCER` y `FACTURA_VENCIDA` con sus avisos (LOG-B01, LOG-B02), `Notificado_Vencida = "Si"`.
4. En una obra `En ejecucion` con `Fecha_Fin_Estimada` pasada, ejecutar OBR-B04: evento `OBRA_ATRASADA` y correo a Gestión y al responsable.

#### E2E-5 · Complementaria
Con una proforma `Aceptada` cuya obra está abierta, crear un `Borrador` nuevo, elegir la aceptada como previa con `Tipo_Relacion` = `Complementaria`, enviarlo (PRO-A01) y aceptarlo (PRO-A07). Esperado: se crea una segunda obra ligada a la principal (`Obra_Principal_ID`). Repetir con `Tipo_Relacion` = `Revision` o sin previa: la obra nace sin `Obra_Principal_ID`. Cerrar la principal con saldo con Gerencia (OBR-A07) y comprobar que con Admin no se ofrece.

#### E2E-6 · Fallo parcial y recuperación
1. Dejar una proforma `Enviada` con obra y sin pasar a `Aceptada`: aparece en `S_Proformas_Inconsistentes`; completarla con PRO-A08.
2. Dejar una `Aceptada` sin obra: crearla con PRO-A09.
3. Comprobar que una proforma `Enviada` no ofrece *Generar PDF* y que `A_Enviar` no aparece en un `Borrador` sin PDF (PRO-A10, PRO-A01).
4. Cortar a mano un bot programado entre sus dos pasos (dejar la marca hecha y el evento sin crear) y ejecutarlo de nuevo: ABO-B03 completa el evento sin duplicar el aviso.

#### E2E-7 · Campo y permisos
Con las cuentas de 14.6: Campo asignado registra un gasto de Material (GAS-B01), horas (HOR-B01) y un avance, y anula uno propio dentro de 24 horas (GAS-A01); no ve gastos de otros; no puede elegir un tipo de costo de Gestión; no ve `Es_Credito_Fiscal`. Campo sin asignación no ve obras. Campo inactivo y la cuenta ajena no ven nada.

#### E2E-8 · Alertas
Dejar una obra `En ejecucion` sin gastos ni horas más de `Umbral_Ambar` días, otra sin avance y otra con rezago de facturación; ejecutar ALE-B01, ALE-B02 y ALE-B03. Esperado: una alerta por obra con la severidad que corresponde a `Metas_KPI`; push a Gestión y correo solo en las rojas (ALE-B04). Reconocer una (ALE-A01) y resolver otra (ALE-A02); volver a ejecutar los bots el mismo día: no se crean alertas nuevas.

### 15.4 Matriz de cobertura

Cada fila dice en qué escenarios de 15.3 interviene el componente. Los que dicen "solo las pruebas de su ficha" se prueban con las pruebas unitarias de su ficha, que ya cubren su comportamiento.

| Código | Nombre | Escenarios de punta a punta |
|---|---|---|
| PRO-A01 | `A_Enviar` | E2E-1, E2E-2, E2E-5, E2E-6 |
| PRO-A02 | `A_Rechazar` | E2E-2 |
| PRO-A03 | `A_Anular` | E2E-3 |
| PRO-A04 | `A_Eliminar` | E2E-3 |
| PRO-A05 | `A_Aceptar_Set` | solo las pruebas de su ficha |
| PRO-A06 | `A_Aceptar_CrearObra` | solo las pruebas de su ficha |
| PRO-A07 | `A_Aceptar` | E2E-1, E2E-5 |
| PRO-A08 | `A_Aceptar_Completar` | E2E-6 |
| PRO-A09 | `A_Aceptar_Reparar_Obra` | E2E-6 |
| PRO-A10 | `A_Generar_PDF` | E2E-1, E2E-6 |
| PRO-A11 | `A_Vencer_Log` | solo las pruebas de su ficha |
| PRO-A12 | `A_Vencer_Set` | solo las pruebas de su ficha |
| PRO-B01 | `B_Proformas_Vencidas` | E2E-4 |
| PRO-B02 | `B_Proforma_PDF` | E2E-1 |
| PRO-B03 | `B_Log_Proformas` | E2E-1 |
| PRO-B04 | `B_Notif_Proformas` | E2E-1, E2E-4 |
| OBR-A01 | `A_Iniciar` | E2E-1 |
| OBR-A02 | `A_Pausar` | solo las pruebas de su ficha |
| OBR-A03 | `A_Reanudar` | solo las pruebas de su ficha |
| OBR-A04 | `A_Terminar` | E2E-1 |
| OBR-A05 | `A_Cancelar` | solo las pruebas de su ficha |
| OBR-A06 | `A_Cerrar` | E2E-1 |
| OBR-A07 | `A_Cerrar_Con_Saldo` | E2E-5 |
| OBR-A08 | `A_Log_Obra_Atrasada` | solo las pruebas de su ficha |
| OBR-B01 | `B_Log_Obra_Creada` | E2E-1 |
| OBR-B02 | `B_Log_Obra_Estado` | E2E-1 |
| OBR-B03 | `B_Log_Obra_Cerrada` | E2E-1 |
| LOG-B01 | `B_Notif_Log_Correo` | E2E-4 |
| OBR-B04 | `B_Obra_Atrasada` | E2E-4 |
| GAS-A01 | `A_Anular_Gasto` | E2E-3, E2E-7 |
| GAS-A02 | `A_Marcar_Pagado` | E2E-1 |
| GAS-B01 | `B_Log_Gasto_Creado` | E2E-1, E2E-7 |
| GAS-B02 | `B_Log_Gasto_Anulado` | solo las pruebas de su ficha |
| GAS-B03 | `B_Log_Credito_Fiscal` | solo las pruebas de su ficha |
| GAS-B04 | `B_Log_Gasto_Pagado` | E2E-1 |
| GAS-B05 | `B_Gasto_Sobre_Planificado` | E2E-1 |
| HOR-A01 | `A_Aprobar_Horas` | E2E-1 |
| HOR-A02 | `A_Rechazar_Horas` | solo las pruebas de su ficha |
| HOR-B01 | `B_Log_Horas_Pendientes` | E2E-1, E2E-7 |
| AVA-A01 | `A_Anular_Avance` | E2E-1, E2E-3 |
| ABO-A01 | `A_Anular_Abono` | E2E-3 |
| ABO-A02 | `A_Cobranza_Marcar` | solo las pruebas de su ficha |
| ABO-A03 | `A_Cobranza_Log` | solo las pruebas de su ficha |
| ABO-A04 | `A_Cobranza_Reabrir` | solo las pruebas de su ficha |
| ABO-A05 | `A_Cobranza_Reabierta_Log` | solo las pruebas de su ficha |
| ABO-A06 | `A_Recordatorio_Log` | solo las pruebas de su ficha |
| ABO-B01 | `B_Log_Abono_Creado` | E2E-1 |
| ABO-B02 | `B_Log_Abono_Anulado` | solo las pruebas de su ficha |
| LOG-B02 | `B_Notif_Log_Push` | E2E-4 |
| ABO-B03 | `B_Cobranza_Completa` | E2E-1, E2E-6 |
| ABO-B04 | `B_Cobranza_Reabierta` | solo las pruebas de su ficha |
| ABO-B05 | `B_Recordatorio_Cobranza` | solo las pruebas de su ficha |
| FAC-A01 | `A_Anular_Factura` | E2E-3 |
| FAC-A02 | `A_Factura_Log_Por_Vencer` | solo las pruebas de su ficha |
| FAC-A03 | `A_Factura_Log_Vencida` | solo las pruebas de su ficha |
| FAC-A04 | `A_Factura_Marcar_Vencida` | solo las pruebas de su ficha |
| FAC-B01 | `B_Factura_Por_Vencer` | E2E-4 |
| FAC-B02 | `B_Factura_Vencida` | E2E-4 |
| ALE-A01 | `A_Reconocer_Alerta` | E2E-8 |
| ALE-A02 | `A_Resolver_Alerta` | E2E-8 |
| ALE-A03 | `A_Alerta_Sin_Gastos` | solo las pruebas de su ficha |
| ALE-A04 | `A_Alerta_Sin_Avance` | solo las pruebas de su ficha |
| ALE-A05 | `A_Alerta_Rezago_Facturacion` | solo las pruebas de su ficha |
| ALE-B04 | `B_Notif_Alerta` | E2E-8 |
| ALE-B01 | `B_Obra_Sin_Gastos` | E2E-8 |
| ALE-B02 | `B_Obra_Sin_Avance` | E2E-8 |
| ALE-B03 | `B_Rezago_Facturacion` | E2E-8 |

---

## 16. Diagnóstico y recuperación

### 16.1 Árbol de diagnóstico

Ante cualquier resultado inesperado:

1. **¿Se ve el efecto en los datos?** Abrir la fila en la app y comprobar su `Estado` y las columnas que la ficha dice que escribe. Si el dato es correcto, el problema es solo de aviso: ir a 13.5.
2. **¿Existe el evento en `Log_Eventos`?** Buscarlo por `Tipo_Evento` y `Registro_ID`.
   - No existe y el hecho ocurrió: el bot de log no se disparó. Ir a 3.
   - Existe: el bot de log funcionó; si falta el aviso, ir a 13.5.
3. **Abrir el bot en `Monitor`.** Elegir la ejecución de la hora del hecho.
   - **Sin ejecución:** el bot no se disparó. Causas: el bot no existe **en la app desde la que se hizo el cambio** (⚠ V18); la condición del evento fue falsa; el cambio lo hizo otro bot sin *Trigger other bots* (⚠ V10); el bot está desactivado.
   - **Ejecución con error:** abrir el paso que falló. Causas habituales en 16.2.
   - **Ejecución correcta pero el efecto no está:** el `Evento_ID` ya existía (la guarda cumplió su función) o la condición del conjunto de filas no seleccionó la fila.
4. **¿Es un bot programado?** Confirmar que está activo, la hora y la zona America/Lima (⚠ V13) y ejecutarlo con *Test*.
5. **¿Es un botón que no aparece?** Evaluar el `Only if` de la ficha por partes, con la fila real: estado, motivo, rol del usuario, estado de la obra.

### 16.2 Errores frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El IGV de gastos o facturas sale en cero | Se leyó la tasa con `NUMBER()` | Usar `DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))` |
| Un botón no aparece para Gerencia | `Rol` mal escrito en `Trabajadores`, o `Activo = No` | Corregir `Trabajadores`; el rol debe ser exactamente `Admin`, `Gerencia` o `Campo` |
| Un correo no sale al responsable | El responsable no tiene correo en `Trabajadores`, o el bot no tiene *Trigger other bots* | Completar el correo; revisar V10 |
| Se duplican eventos de un bot programado | La guarda con `LOOKUP` no coincide con el `Evento_ID` que escribe la acción | Hacer que ambas usen exactamente el mismo texto |
| `Rezago_Facturacion_pp` o `Dias_Sin_Gastos` da error | Virtual mal creada o con otro nombre | Recrearla según el `_Diccionario` |
| Un bot de Campo no deja evento | El bot no existe en OXY Campo | Crearlo ahí (V18) |
| La severidad de una alerta sale siempre ámbar | La lectura de `Metas_KPI` falló | V20 |
| Un cambio de `Estado` desde el Sheet no dispara nada | Los bots solo reaccionan a cambios hechos desde la app | Hacer el cambio desde la app |

### 16.3 Detección de operaciones a medias

Los dos slices de 5.3 (`S_Proformas_Inconsistentes`, `S_Proformas_Sin_PDF`) se revisan **una vez al día** y después de cualquier corte de conexión. Una fila en cualquiera de ellos significa una operación a medias; la tabla siguiente dice cómo recuperarla.

### 16.4 Recuperación de fallos parciales

| Qué quedó a medias | Cómo se ve | Recuperación | Es seguro repetir |
|---|---|---|---|
| Aceptación: obra creada y proforma sin pasar a `Aceptada` | `Enviada` con obra; `S_Proformas_Inconsistentes` | PRO-A08 (*Completar aceptación*) | Sí; no crea otra obra |
| Aceptación: proforma `Aceptada` sin obra | `Aceptada` sin `Obra_Generada` | PRO-A09 (*Crear obra faltante*) | Sí; el botón se oculta al existir la obra |
| Proforma enviada sin PDF válido o ruta sin archivo | `S_Proformas_Sin_PDF` | Corregir a mano en `OXYData` (no se regenera después de enviar) | No aplica |
| `Doc_Proforma` se quedó en `PENDIENTE` | `S_Proformas_Sin_PDF` | Revisar `Monitor` de PRO-B02; vaciar el valor y pulsar PRO-A10 (solo en `Borrador`) | Sí |
| Vencimiento: evento creado y estado sin cambiar | `Enviada` con vigencia pasada y evento `PROFORMA_VENCIDA` | Ejecutar PRO-B01 otra vez | Sí; no duplica el evento |
| Cobranza completa: marcada y sin evento | `Notificado_Cobro_Completo = "Si"` sin evento | Ejecutar ABO-B03 | Sí |
| Cobranza reabierta: evento creado y sin reabrir | `Notificado_Cobro_Completo = "Si"` con saldo fuera de tolerancia | Ejecutar ABO-B04 | Sí |
| Factura vencida: evento creado y sin marcar | `Notificado_Vencida = "No"` con evento | Ejecutar FAC-B02 | Sí |

### 16.5 Qué no hacer

- No editar a mano `Log_Eventos`, `Estado`, `Notificado_Cobro_Completo` ni `Notificado_Vencida` para "arreglar" un caso: usar la acción o el bot indicado.
- No borrar filas de tablas transaccionales; se anulan.
- No volver a ejecutar a mano una acción auxiliar sobre filas sueltas: las auxiliares no tienen las guardas de los bots o grupos que las llaman.

---

## 17. Registro de validaciones y decisiones abiertas

### 17.1 Registro de validaciones

Cada fila es una capacidad o expresión que **se prueba en el editor antes de darla por buena**. El estado inicial de todas es *Pendiente*. Al cerrar una fila se anota la fecha, quién la probó y el resultado; si falla, se aplica la alternativa y se anota.

| ID | Qué se valida | Dónde y con qué datos | Resultado esperado | Alternativa si falla | Estado |
|---|---|---|---|---|---|
| V01 | Si un paso de un bot falla, ¿los siguientes se ejecutan? | Bot de prueba con un paso que falla a propósito y un paso posterior | Se conoce el comportamiento; el orden "registrar primero, marcar después" de los bots programados lo tiene en cuenta | Si los pasos posteriores no corren, dejar cada paso en un bot propio encadenado | Pendiente |
| V02 | Un push de un bot *Adds* llega al teléfono de Gerencia | Gasto de Campo; Gerencia con OXY Campo instalada | Llega el push | Avisar por correo | Pendiente |
| V03 | El campo *Para* acepta una lista calculada con `SELECT` | Correo de prueba a Gestión | Llega a todos los Admin y Gerencia activos | Un paso por destinatario fijo | Pendiente |
| V04 | `Valid if` con `SELECT` sobre la misma tabla excluyendo la fila actual; `Numero` con `/ : * ? < > |`, y cómo escribir `\` y `"` en una fórmula | Factura con número repetido; factura que supera el total a cobrar; proforma con `Numero` repetido; `Proforma_Previa_ID` de un `Borrador` nuevo | Rechaza el repetido y el exceso (salvo Gerencia); la lista de previas no incluye a la propia proforma ni a las `Z-Eliminada` | Validar con un slice de detección y revisión diaria | Pendiente |
| V05 | Mensaje de confirmación calculado | Proforma con y sin aviso de margen | El mensaje cambia según la columna | Dos botones con `Only if` distintos | Pendiente |
| V06 | *Create a new file* en Core con plantilla de Google Docs;  nombre `<Numero>_<Sello>` con *Disable timestamp*; marcas de tabla relacionada y `TEXT(...)` | Pulsar *Generar PDF* dos veces | Dos PDF `Proformas_Files/<Numero>_<Sello>.pdf`; `Doc_Proforma` apunta al último | Plantilla HTML o PDF manual | Pendiente |
| V07 | `[_THISROW_BEFORE]` y `[_THISROW_AFTER]` en condiciones *Updates* | Anular un gasto; cambiar `Es_Credito_Fiscal` | Solo se dispara con el cambio buscado | Un bot por tabla con la condición solo sobre el valor nuevo | Pendiente |
| V08 | `Valid if` de `Es_Credito_Fiscal` | Gasto con boleta marcado como crédito | Lo rechaza | Mensaje de aviso sin bloqueo | Pendiente |
| V09 | Valor inicial aplicado en una columna oculta | Gasto de Campo | `Es_Credito_Fiscal` se guarda con su valor inicial | Poblarlo con un bot de alta | Pendiente |
| V10 | *Trigger other bots* encadena el bot programado con LOG-B01, LOG-B02 y ALE-B04 | Ejecutar ABO-B03 | Llega el aviso del bot de notificación | Que el bot programado envíe él mismo el correo | Pendiente |
| V11 | Nombre exacto de la columna inversa `Related ...` | Plantilla del PDF | El PDF lista los conceptos | Ajustar la marca de la plantilla al nombre real | Pendiente |
| V12 | Duración `"024:00:00"` en `Only if` | Gasto de Campo de menos y de más de 24 horas | Anula solo dentro de 24 horas | `(NOW()-[Creado_En])*24<24` o `HOUR` | Pendiente |
| V13 | Bots programados disponibles en Core y ejecutables a mano | Bot diario y semanal de prueba | Se ejecutan y aparecen en `Monitor` | Disparar los procesos desde una acción manual diaria | Pendiente |
| V14 | Texto del push con expresiones `<<...>>` | Push de prueba | El texto sale con los valores | Texto fijo | Pendiente |
| V15 | Rutas y rótulos del editor nuevo: crear acciones, `Set these columns`, `Table to add rows to`, `Data change type`, security filters y lista de usuarios | Recorrer el editor una vez | Se anotan las rutas reales y se corrige este documento | — | Pendiente |
| V16 | *Security filter* con `SELECT` y `LOOKUP` anidados | Cuentas de Campo con y sin asignación | Cada cuenta ve solo lo suyo | Precalcular las obras asignadas en una columna de `Trabajadores` | Pendiente |
| V17 | Una cuenta fuera de `Trabajadores` | Cuenta ajena en OXY Campo y OXY Gestión | No ve datos | Lista de usuarios de la app | Pendiente |
| V18 | Un bot de cambio de datos reacciona solo a cambios hechos desde su app | Alta de gasto desde cada app | Cada bot reacciona a su app | Duplicar el bot en la otra app (ya previsto) | Pendiente |
| V19 | *Set row values* sobre un conjunto de filas desde un bot programado | PRO-B01 | Cambia el estado de todas las filas del conjunto | Una acción auxiliar por fila con *Execute an action on a set of rows* | Pendiente |
| V20 | `LOOKUP` a `Metas_KPI` dentro de acciones y conjuntos de bots programados | ALE-B01 | La severidad cambia al cambiar el umbral | Guardar los umbrales también en `Configuracion` | Pendiente |
| V21 | *Add row* con clave calculada como texto | `A_Log_Obra_Atrasada` | La fila queda con el `Evento_ID` calculado | `UNIQUEID()` y una columna de apoyo para la guarda | Pendiente |
| V22 | Paso condicional en un bot | ALE-B04 con alerta ámbar y roja | El correo solo sale con la roja | Segundo bot con la condición en el evento | Pendiente |
| V23 | Columna virtual de tipo File (`Doc_Oficial`) se abre desde la app | Proforma con y sin personalizado | Abre el personalizado si existe; si no, el PDF | Dos columnas con `Show?` condicional | Pendiente |
| V24 | `LOOKUP` con clave fija (`"OXY"`) sobre la tabla de una fila `Compania`, desde una columna virtual, una condición de paso y el campo *To* de un bot; `Compania` con solo *Updates* | PDF de una proforma; LOG-B01 con `Emails_Cobranza` lleno y vacío | Los datos salen en el PDF; el correo sale solo con `Emails_Cobranza` lleno | Dejar los datos de OXY como parámetros en una tabla de claves de texto | Pendiente |

### 17.2 Decisiones abiertas

| ID | Decisión | Estado actual | Quién decide |
|---|---|---|---|
| D01 | ¿Se registra un evento `HORAS_APROBADAS` al aprobar horas? | No se registra | Gerencia |
| D02 | ¿Los precios y el presupuesto de costo de `Obras` pueden llegar al teléfono de Campo? (14.4) | Sí, en las obras asignadas | Gerencia |
| D03 | ¿Quién puede ejecutar *Cerrar* una obra con cobranza completa: Gestión o solo Gerencia? | Gestión (`Cerrar con saldo` es solo de Gerencia) | Gerencia |
| D04 | ¿La clave `DIAS_ALERTA_SIN_GASTOS` de `Configuracion` se mantiene? | Las alertas leen solo `Metas_KPI`; la clave no se usa | Dueño de datos |
| D05 | ¿Se permite anular una factura que tiene abonos vigentes? | No: primero se anulan los abonos | Gestión |
| D06 | ¿Los correos de `Compania.Emails_Cobranza` reciben el aviso de cobranza completa? | Sí, si el campo no está vacío (LOG-B01, paso 2) | Gestión |
| D07 | ¿Las cuentas bancarias, las condiciones y los correos de `Emails_Cobranza` de `Compania` pueden llegar al teléfono de Campo? (14.4) | Sí, `Compania` está en Campo en solo lectura | Gerencia |

---
