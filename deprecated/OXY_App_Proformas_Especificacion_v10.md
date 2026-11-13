# OXY Industrial S.R.L. — OXY Proformas: especificación de la aplicación

**Plan:** Core · **Datos:** `OXYData` (Google Sheet) · **Zona horaria:** America/Lima (UTC-5).
**Para quién es:** quien construye la app en el editor de AppSheet. Cada propiedad se escribe en una línea, con el nombre que tiene en el editor nuevo de AppSheet.
**Documentos relacionados:** `OXY_AppSheet_Arquitectura_y_Seguridad` (roles, seguridad, reparto entre apps), `OXY_DataModel_Especificacion` (significado de cada tabla y columna) y `OXY_Propuesta_Dashboard_Indicadores`.

---

## 1. Propósito y alcance

**Quién la usa:** `Super`, `Administracion`, `Supervisor` y `Planificacion`. Cada usuario decide si la abre en celular o en escritorio.

**Qué hace:**
1. Arma la proforma: cabecera, conceptos que se imprimen y planificación de costos interna.
2. Genera el PDF de la proforma desde una plantilla de Google Docs.
3. Envía la proforma (cambia su estado; el PDF no se manda al cliente, solo se archiva).
4. Registra la respuesta del cliente: aceptación, rechazo o anulación.
5. Elimina borradores.
6. Vence automáticamente las proformas enviadas cuya vigencia pasó.
7. Al aceptar, crea la obra en estado `Por iniciar`.
8. Da de alta clientes y contactos nuevos al armar una proforma.

**Qué no hace:**
- No opera la obra: sus estados, gastos, horas, avances, facturas y abonos viven en OXY Gestión y OXY Campo.
- No edita ni borra clientes ni contactos: eso se hace en OXY Master.
- No asigna el responsable de la obra: lo asigna un usuario de OXY Gestión.
- No envía el PDF al cliente por correo.
- No genera el número de la proforma: lo digita el usuario.

### 1.1 Qué se imprime

La proforma muestra los `Proforma_Conceptos` (concepto y monto sin IGV), luego `IGV_Monto` y `Total_Cobrar`. La `Proforma_Planificacion` (costo interno) no se imprime.

### 1.2 Ciclo de vida

`Borrador → Enviada → Aceptada | Rechazada | Vencida | Anulada`.

1. Un `Borrador` solo puede pasar a `Enviada` o a `Z-Eliminada` (acción *Eliminar*); nunca a `Anulada`.
2. `Anulada` solo se alcanza desde `Enviada`.
3. `Z-Eliminada` es un estado final: no se edita y no se muestra en las vistas normales (el prefijo `Z` la deja al final al ordenar por estado).
4. Una `Aceptada` crea una obra. Cada proforma genera exactamente una obra.
5. Una `Rechazada` no se reabre: se corrige con una proforma nueva que el usuario relaciona a mano con la rechazada.
6. El estado nunca lo edita el usuario: lo cambian solo las acciones y el bot de vencimiento.
7. Mientras la proforma está `Enviada`, el usuario puede corregir las líneas existentes de conceptos y de planificación, para hacer cambios mínimos cuando el cliente lo pide. También puede agregar líneas nuevas, volver a generar el PDF (`A_Generar_PDF`) y volver a subir `Doc_Proforma_Personalizado`; solo se pueden borrar líneas mientras es `Borrador`. Desde `Aceptada` todo queda bloqueado: líneas, PDF y documento personalizado.

### 1.3 Relación entre proformas

La relación es manual. El sistema no copia datos, no cambia el estado de la proforma previa y no numera revisiones. Cada proforma se digita completa. Si una proforma es la revisión o la complementaria de otra, el usuario elige la previa y el tipo de relación en el formulario del `Borrador`. Solo `Complementaria` tiene efecto: al aceptar, la obra nueva queda ligada a la obra de la previa.

### 1.4 Reglas de datos

1. Moneda única: soles. Los costos se registran sin IGV.
2. Los datos de control de registro (`Creado_En`, `Procesado_En`, `Fecha_Hora`) son `DateTime` con `NOW()`.
3. Las fechas de cambio de estado de un documento (`Fecha_Envio`, `Fecha_Rechazo`, `Fecha_Anulacion`, `Fecha_Eliminacion`) son `Date` con `TODAY()`. La hora exacta queda en `Log_Eventos`.
4. Una proforma no se borra: un `Borrador` se elimina pasándolo a `Z-Eliminada`.
5. Para llegar a una tabla a través de otra se usan las columnas virtuales de tipo Ref del modelo de datos, no `LOOKUP`.

---

## 2. Acceso y seguridad

### 2.1 Roles permitidos

`Super`, `Administracion`, `Supervisor` y `Planificacion`. En esta versión, todos ejecutan todas las acciones de la app (matriz en 5.1).

### 2.2 Lista de usuarios

1. **Require user sign-in:** activo.
2. **Allowed users:** las cuentas Google de las personas con alguno de los cuatro roles. Una cuenta que está en la lista pero no en `Trabajadores`, o está inactiva, abre la app pero no ve ninguna acción.
3. Alta, baja y cambio de rol: procedimientos de la arquitectura (sección 5.4).

### 2.3 Expresión de rol

Toda acción de usuario lleva en `Only if this condition is true` esta expresión, sola o dentro de `AND(<expresión de rol>,<condición>)`:

```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Administracion","Supervisor","Planificacion")))
```

En las fichas se abrevia **`<ROL_PRO>`**. Se copia completa en cada acción.

**Acciones auxiliares.** Las acciones con `Position` = *Hide* que solo llaman los grupos y los bots llevan `Only if` vacío. Un bot programado no tiene usuario (`USEREMAIL()` vacío), así que una auxiliar con la expresión de rol no se ejecutaría. La condición de rol la llevan los botones que las llaman.

### 2.4 Qué llega al dispositivo

Quien abre la app lee todas las tablas de 3.1, incluso las columnas ocultas con `Show?`:

- La planificación de costos de todas las proformas.
- Los datos de `Compania`: cuentas bancarias, condiciones y correos de cobranza.
- Nombre, rol y correo de todos los trabajadores.

Por eso la lista de usuarios es la protección real (arquitectura, sección 5.2).

---

## 3. Especificación de Datos

### 3.1 Tablas y permisos

Códigos: **L** lectura · **I** inserción (*Adds*) · **A** actualización (*Updates*) · **E** eliminación (*Deletes*). Solo `Proforma_Conceptos` y `Proforma_Planificacion` permiten *Deletes*, y solo mientras la proforma es `Borrador`.

| Tabla | Permisos | Para qué está en la app |
|---|---|---|
| `Proformas` | L·I·A | Cabecera de la proforma |
| `Proforma_Conceptos` | L·I·A·E | Líneas que se imprimen |
| `Proforma_Planificacion` | L·I·A·E | Costo interno planificado |
| `Obras` | L·I | La acción de aceptación agrega la fila; la lectura permite saber si la proforma ya tiene obra y cuál es la obra de la previa |
| `Clientes` | L·I | Elegir cliente y dar de alta uno nuevo (sin ediciones ni borrados) |
| `Contactos_Cliente` | L·I | Elegir contacto y dar de alta uno nuevo (sin ediciones ni borrados) |
| `Tipos_Costo` | L | Tipo de cada línea de planificación |
| `Categorias_Costo` | L | Categoría del tipo de costo |
| `Trabajadores` | L | Rol y estado del usuario, destinatarios de avisos y responsable de la obra |
| `Configuracion` | L | IGV, vigencia y margen mínimo |
| `Compania` | L | Datos de OXY que se imprimen en el PDF |
| `Log_Eventos` | L·I | Los bots y las acciones auxiliares escriben los eventos de proforma y de obra creada |

### 3.2 Preparación

1. Crear la app desde `OXYData` con las doce tablas de 3.1. No agregar otras.
2. Definir los permisos de 3.1 en **Data → Tables → (tabla) → Permissions**.
3. En `Obras`, no crear columnas virtuales: la tabla se usa solo para crear la fila y consultarla. Después de agregarla, corregir los tipos y las propiedades de columna de 3.3.
4. En `Trabajadores`, la columna `Area_ID` apunta a una tabla que no está en la app: definirla como *Text* en esta app (⚠ V25).
5. Aplicar la configuración de columnas de 3.3.
6. Crear los slices de 3.4 y los de 3.6.
7. Configurar las acciones de sistema de 3.5.
8. Dejar en Drive la carpeta `Proformas_Files` y la plantilla `Plantilla_Proforma` (Google Docs).
9. Confirmar que la fila `OXY` de `Compania` tiene los datos reales y que `Configuracion` tiene `IGV_PCT`, `VIGENCIA_PROFORMA_DIAS` y `MARGEN_MINIMO_PCT`.
10. Orden de construcción: columnas y slices; acciones auxiliares (`A_Aceptar_Set`, `A_Aceptar_CrearObra`, `A_Vencer_Log`, `A_Vencer_Set`); acciones visibles y grupos (`A_Generar_PDF` antes que `A_Enviar`); vistas; bots.

### 3.3 Configuración de columnas

Cada bloque es una columna; cada línea, una propiedad del editor (**Data → Tables → (tabla) → Columns**). Las propiedades que no aparecen se dejan como están tras regenerar la estructura desde `OXYData`. Las columnas no listadas no llevan configuración propia en esta app.

**Criterio de `Require?`.** Se define por el ciclo de vida de la tabla, no solo por la estructura de `OXYData`: `TRUE` si la columna siempre debe tener valor desde que se crea la fila; `FALSE` si es opcional o si no la llena esta app; y una fórmula (*Required If*) si el dato solo es obligatorio desde cierto estado. Tres reglas:
1. Una columna obligatoria que el usuario no puede editar y que quedó vacía impide guardar el formulario. Por eso las columnas que escriben las acciones y los bots no son `TRUE` fijo: su fórmula depende del estado al que llegan.
2. En `Enviada` las salidas son excluyentes (aceptar, rechazar o anular), así que ninguno de sus datos de salida (`Fecha_Aceptacion`, `Doc_Aceptacion`, `Motivo_Rechazo`, `Motivo_Anulacion`) se exige ahí: la exigencia de avanzar la dan los `Only if` de las acciones. La fórmula solo asegura que existan una vez alcanzado el estado.
3. Las acciones y los bots no validan `Require?`: escriben aunque la columna lo exija.

#### Tabla `Proformas`

**`Proforma_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `"PRF-"&UNIQUEID()` ⚠ V26

**`Numero`** (Text, etiqueta)
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`
- Valid if: `AND(NOT(IN([_THIS],SELECT(Proformas[Numero],AND([Proforma_ID]<>[_THISROW].[Proforma_ID],[Estado]<>"Z-Eliminada")))),NOT(OR(CONTAINS([_THIS],"/"),CONTAINS([_THIS],":"),CONTAINS([_THIS],"*"),CONTAINS([_THIS],"?"),CONTAINS([_THIS],"<"),CONTAINS([_THIS],">"),CONTAINS([_THIS],"|"))))`
- Invalid value error: `Numero repetido o con caracteres no permitidos (/ : * ? < > |).`
- Nota: lo digita el usuario al crear la proforma. El PDF se nombra con el `Numero`, así que no puede repetirse entre proformas vigentes ni llevar caracteres inválidos en nombres de archivo. La barra invertida y las comillas dobles también son inválidas, pero su forma de escribirlas en una fórmula no está confirmada: se prueban en V04 y, si funcionan, se añaden al `OR`.

**`Nombre`**
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`

**`Cliente_ID`** (Ref a `Clientes`)
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`
- Valid if: `SELECT(Clientes[Cliente_ID],[Activo]=TRUE)`
- Invalid value error: `Seleccione un cliente activo.`
- Nota: ofrece solo clientes activos (regla de `Activo` del modelo de datos).

**`Contacto_ID`** (Ref a `Contactos_Cliente`)
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`
- Valid if: `FILTER("Contactos_Cliente",[Cliente_ID]=[_THISROW].[Cliente_ID])`
- Invalid value error: `Seleccione un contacto del mismo cliente de la proforma.`

**`Direccion_Servicio`**
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`

**`Fecha_Emision`**
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`
- Initial value: `TODAY()`

**`Estado`** (Enum)
- Show?: `FALSE`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Initial value: `"Borrador"`
- Nota: solo cambian el estado las acciones y el bot de vencimiento. Se muestra en pantalla con la columna virtual `Estado_Etiqueta`.

**`Fecha_Envio`** (Date)
- Show?: `ISNOTBLANK([Fecha_Envio])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `IN([Estado],LIST("Enviada","Aceptada","Rechazada","Vencida","Anulada"))`
- Nota: la fija `A_Enviar` con `TODAY()`. Se exige desde `Enviada`; una `Borrador` o `Z-Eliminada` no pasó por el envío.

**`Fecha_Vigencia`** (Date)
- Editable?: `[Estado]="Borrador"`
- Require?: `TRUE`
- Initial value: `TODAY()+NUMBER(LOOKUP("VIGENCIA_PROFORMA_DIAS","Configuracion","Clave","Valor"))`
- Valid if: `[_THIS]>=[Fecha_Emision]`
- Invalid value error: `La vigencia no puede ser anterior a la fecha de emision.`
- Nota: el usuario la ajusta en `Borrador`, antes de enviar. `A_Enviar` no la fija; el PDF siempre muestra este valor. El bot `B_Proformas_Vencidas` vence la proforma cuando pasa.

**`Fecha_Aceptacion`** (Date)
- Show?: `IN([Estado],LIST("Enviada","Aceptada"))`
- Editable?: `[Estado]="Enviada"`
- Require?: `[Estado]="Aceptada"`
- Nota: el usuario la carga en `Enviada` (no se exige ahí: la exigencia de pasar a `Aceptada` la da el `Only if` de `A_Aceptar`). Ya aceptada, debe existir.

**`Doc_Aceptacion`** (File)
- Show?: `IN([Estado],LIST("Enviada","Aceptada"))`
- Editable?: `[Estado]="Enviada"`
- Require?: `[Estado]="Aceptada"`
- Nota: orden de compra, correo o carta, en PDF o imagen. Es requisito de `A_Aceptar`. `Require?`: igual que `Fecha_Aceptacion`: se exige a quien acepta por el `Only if` de `A_Aceptar`; ya aceptada, debe existir.

**`Motivo_Rechazo`**
- Show?: `IN([Estado],LIST("Enviada","Rechazada"))`
- Editable?: `[Estado]="Enviada"`
- Require?: `[Estado]="Rechazada"`
- Valid if: `ISBLANK([Motivo_Anulacion])`
- Invalid value error: `No se puede indicar motivo de rechazo si la proforma ya tiene motivo de anulacion.`
- Nota: en `Enviada` no se exige (aceptar, rechazar y anular son salidas excluyentes); la exigencia la da el `Only if` de `A_Rechazar`. Ya rechazada, debe existir.

**`Motivo_Anulacion`**
- Show?: `IN([Estado],LIST("Enviada","Anulada"))`
- Editable?: `[Estado]="Enviada"`
- Require?: `[Estado]="Anulada"`
- Valid if: `ISBLANK([Motivo_Rechazo])`
- Invalid value error: `No se puede indicar motivo de anulacion si la proforma ya tiene motivo de rechazo.`
- Nota: en `Enviada` no se exige; la exigencia la da el `Only if` de `A_Anular`. Ya anulada, debe existir.

**`Fecha_Rechazo`** (Date)
- Show?: `ISNOTBLANK([Fecha_Rechazo])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `[Estado]="Rechazada"`
- Nota: la fija `A_Rechazar` con `TODAY()`. Se exige una vez que está rechazada.

**`Fecha_Anulacion`** (Date)
- Show?: `ISNOTBLANK([Fecha_Anulacion])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `[Estado]="Anulada"`
- Nota: la fija `A_Anular` con `TODAY()`. Se exige una vez que está anulada.

**`Eliminada_Por`** (Email)
- Show?: `ISNOTBLANK([Eliminada_Por])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `[Estado]="Z-Eliminada"`
- Nota: la fija `A_Eliminar` con `USEREMAIL()`. Se exige una vez que está eliminada.

**`Fecha_Eliminacion`** (Date)
- Show?: `ISNOTBLANK([Fecha_Eliminacion])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `[Estado]="Z-Eliminada"`
- Nota: la fija `A_Eliminar` con `TODAY()`. Se exige una vez que está eliminada.

**`Doc_Proforma`** (File)
- Show?: `ISNOTBLANK([Doc_Proforma])`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `FALSE`
- Nota: guarda la señal `PENDIENTE|yyyyMMddHHmmss` mientras el bot trabaja y luego la ruta final `Proformas_Files/<Numero>_<Sello>.pdf`. Se genera en `Borrador` o `Enviada`, las veces que haga falta; desde `Aceptada` ya no. `Require?`: lo escribe el bot; `A_Enviar` exige que exista y no sea la señal `PENDIENTE|...` (por su `Only if`), no esta propiedad.

**`Doc_Proforma_Personalizado`** (File, opcional)
- Show?: `OR(ISNOTBLANK([Doc_Proforma_Personalizado]),IN([Estado],LIST("Borrador","Enviada")))`
- Editable?: `IN([Estado],LIST("Borrador","Enviada"))`
- Require?: `FALSE`
- Nota: copia propia que sube el usuario; se puede volver a subir mientras la proforma es `Borrador` o `Enviada`. Desde `Aceptada` queda bloqueada solo en pantalla (no es seguridad). Si existe, es el documento oficial.

**`Proforma_Previa_ID`** (Ref a `Proformas`, opcional)
- Editable?: `[Estado]="Borrador"`
- Require?: `FALSE`
- Valid if: `SELECT(Proformas[Proforma_ID],AND([Proforma_ID]<>[_THISROW].[Proforma_ID],[Estado]<>"Z-Eliminada"))`
- Invalid value error: `Seleccione otra proforma (no la misma ni una eliminada).`
- Nota: la lista excluye la propia proforma y las `Z-Eliminada`; no valida nada más, porque la relación es decisión del usuario. ⚠ V04

**`Tipo_Relacion`** (Enum: `Revision`, `Complementaria`)
- Editable?: `[Estado]="Borrador"`
- Require?: `ISNOTBLANK([Proforma_Previa_ID])`
- Nota: sin previa queda vacío. Solo `Complementaria` tiene efecto en el sistema (la obra nueva se liga a la obra de la previa).

**`Creado_Por`** (Email)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `USEREMAIL()`

**`Creado_En`** (DateTime)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `NOW()`

**Columnas virtuales de `Proformas`.** Se crean con el tipo y la fórmula indicados (esta especificación es la única fuente de la fórmula; `_Diccionario` solo registra que la columna es virtual):

**`Etiqueta`** (virtual, Text, etiqueta)
- App formula: `[Numero]&" - "&[Nombre]`

**`Estado_Etiqueta`** (virtual, Text)
- App formula: `[Estado]`
- Nota: muestra el estado en las vistas sin exponer la columna `Estado`.

**`Precio_Neto`** (virtual, Price)
- App formula: `SUM(SELECT(Proforma_Conceptos[Monto_Sin_IGV],[Proforma_ID]=[_THISROW]))`
- Nota: el filtro por proforma es obligatorio; sin él se sumarían las líneas de todas las proformas.

**`IGV_Monto`** (virtual, Price)
- App formula: `ROUND([Precio_Neto]*DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))*100)/100.0`

**`Total_Cobrar`** (virtual, Price)
- App formula: `[Precio_Neto]+[IGV_Monto]`

**`Costo_Planificado`** (virtual, Price)
- App formula: `SUM(SELECT(Proforma_Planificacion[Costo_Imputable],[Proforma_ID]=[_THISROW]))`
- Nota: mismo filtro obligatorio que en `Precio_Neto`.

**`Margen_Plan`** (virtual, Price)
- App formula: `[Precio_Neto]-[Costo_Planificado]`

**`Margen_Plan_Pct`** (virtual, Percent)
- App formula: `IF([Precio_Neto]>0,[Margen_Plan]/[Precio_Neto],0)`

**`Aviso_Margen`** (virtual, Yes/No)
- App formula: `[Margen_Plan_Pct]<DECIMAL(LOOKUP("MARGEN_MINIMO_PCT","Configuracion","Clave","Valor"))`

**`Obra_Generada`** (virtual, Ref a `Obras`)
- App formula: `INDEX(SELECT(Obras[Obra_ID],[Proforma_ID]=[_THISROW].[Proforma_ID]),1)`
- Nota: la obra creada desde esta proforma. Oculta *Crear obra faltante* y *Aceptar* cuando ya existe.

**`Total_Relacionadas`** (virtual, Number)
- App formula: `COUNT(SELECT(Proformas[Proforma_ID],AND([Proforma_Previa_ID]=[_THISROW],[Estado]<>"Z-Eliminada")))`
- Nota: cuenta las proformas no eliminadas que apuntan a esta; no recorre cadenas.

**`Doc_Oficial`** (virtual, File)
- App formula: `IF(ISNOTBLANK([Doc_Proforma_Personalizado]),[Doc_Proforma_Personalizado],[Doc_Proforma])`
- Nota: el documento oficial: el personalizado si existe; si no, el PDF generado. Se usa en las vistas de detalle. ⚠ V23

**Datos de OXY para el PDF.** Las diez columnas siguientes son virtuales de `Proformas`, de solo lectura, y alimentan la plantilla del PDF. Cada una lee una columna de la fila única de `Compania`; un cambio allí se refleja en el siguiente PDF que se genere. ⚠ V24

| Columna virtual | Tipo | App formula |
|---|---|---|
| `Empresa_Nombre_Comercial` | Text | `LOOKUP("OXY","Compania","Compania_ID","Nombre_Comercial")` |
| `Empresa_Razon_Social` | Text | `LOOKUP("OXY","Compania","Compania_ID","Razon_Social")` |
| `Empresa_RUC` | Text | `LOOKUP("OXY","Compania","Compania_ID","RUC")` |
| `Empresa_Direccion_Fiscal` | Text | `LOOKUP("OXY","Compania","Compania_ID","Direccion_Fiscal")` |
| `Empresa_Telefono` | Text | `LOOKUP("OXY","Compania","Compania_ID","Telefono")` |
| `Empresa_Email` | Text | `LOOKUP("OXY","Compania","Compania_ID","Email")` |
| `Empresa_Web` | Text (puede estar vacía) | `LOOKUP("OXY","Compania","Compania_ID","Web")` |
| `Proforma_Condiciones` | LongText | `LOOKUP("OXY","Compania","Compania_ID","Condiciones_Proforma")` |
| `Proforma_Cuentas_Bancarias` | LongText | `LOOKUP("OXY","Compania","Compania_ID","Cuentas_Bancarias")` |
| `Proforma_Firma_Nombre` | Text | `LOOKUP("OXY","Compania","Compania_ID","Firma_Nombre")` |

#### Tabla `Proforma_Conceptos`

**`Concepto_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `"CNC-"&UNIQUEID()`

**`Proforma_ID`** (Ref a `Proformas`)
- Editable?: `[Proforma_ID].[Estado]="Borrador"`
- Require?: `TRUE`
- Nota: marcar *Is a part of* para que las líneas se vean dentro de la proforma. Se queda editable solo en `Borrador`: en una `Enviada` la línea nueva toma la proforma al agregarla desde el detalle de esa proforma (no se cambia a mano). ⚠ V29

**`Orden`**
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`

**`Concepto`**
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`

**`Monto_Sin_IGV`** (Price)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`

**`Cliente_ID`** (virtual, Ref a `Clientes`)
- App formula: `[Proforma_ID].[Cliente_ID]`

**`Contacto_ID`** (virtual, Ref a `Contactos_Cliente`)
- App formula: `[Proforma_ID].[Contacto_ID]`

#### Tabla `Proforma_Planificacion`

La planificación usa las mismas columnas que el gasto, para comparar plan y real sin conversiones. No tiene fechas de pago.

**`Planif_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `"PLN-"&UNIQUEID()`

**`Proforma_ID`** (Ref a `Proformas`)
- Editable?: `[Proforma_ID].[Estado]="Borrador"`
- Require?: `TRUE`
- Nota: marcar *Is a part of*. Igual que en conceptos: la línea nueva en una `Enviada` toma la proforma desde su detalle. ⚠ V29

**`Tipo_Costo_ID`** (Ref a `Tipos_Costo`)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`
- Valid if: `SELECT(Tipos_Costo[Tipo_Costo_ID],[Activo]=TRUE)`
- Invalid value error: `Seleccione un tipo de costo activo.`

**`Descripcion`**
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`

**`Cantidad`** (Decimal)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`
- Initial value: `1`

**`Unidad`**
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `FALSE`

**`Costo_Unitario`** (Decimal)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`
- Nota: siempre sin IGV. Si la cotización del proveedor trae IGV, se divide entre 1.18 antes de digitarla.

**`Tiene_IGV`** (Enum: `Si`, `No`)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`
- Initial value: `LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Aplica_IGV_Defecto")`

**`Es_Credito_Fiscal`** (Enum: `Si`, `No`)
- Editable?: `IN([Proforma_ID].[Estado],LIST("Borrador","Enviada"))`
- Require?: `TRUE`
- Initial value: `IF([Tiene_IGV]="Si",LOOKUP([Tipo_Costo_ID],"Tipos_Costo","Tipo_Costo_ID","Credito_Fiscal_Defecto"),"No")`
- Valid if: `OR([_THIS]="No",[Tiene_IGV]="Si")`
- Invalid value error: `El credito fiscal solo aplica si la linea tiene IGV.`
- Nota: si el usuario cambia `Tiene_IGV`, el valor inicial no se recalcula; el `Valid if` obliga a corregir el crédito.

Columnas virtuales de `Proforma_Planificacion`:

| Columna virtual | Tipo | App formula |
|---|---|---|
| `Monto_Base` | Price | `[Cantidad]*[Costo_Unitario]` |
| `Monto_IGV` | Price | `IF([Tiene_IGV]="Si",ROUND([Monto_Base]*DECIMAL(LOOKUP("IGV_PCT","Configuracion","Clave","Valor"))*100)/100.0,0)` |
| `Costo_Total` | Price | `[Monto_Base]+[Monto_IGV]` |
| `Costo_Imputable` | Price | `[Monto_Base]+IF([Es_Credito_Fiscal]="Si",0,[Monto_IGV])` |
| `Cliente_ID` | Ref a `Clientes` | `[Proforma_ID].[Cliente_ID]` |
| `Contacto_ID` | Ref a `Contactos_Cliente` | `[Proforma_ID].[Contacto_ID]` |
| `Categoria_ID` | Ref a `Categorias_Costo` | `[Tipo_Costo_ID].[Categoria_ID]` |
| `Proforma_Estado` | Text | `[Proforma_ID].[Estado]` |

#### Tabla `Obras`

Sin columnas virtuales. En esta app la tabla solo permite *Adds* (3.1) y no tiene formulario ni vista de edición: la fila la crea la acción `A_Aceptar_CrearObra` (PRO-A07). Al agregar la tabla, AppSheet adivina los tipos, marca `Require?` en varias columnas y pone `TODAY()` como valor inicial en las fechas; se corrige como sigue. Las columnas que escribe la acción llevan `Editable?` = `CONTEXT("ViewType") = "Never"`; las que llena OXY Gestión solo se dejan opcionales y sin valor inicial.

**`Obra_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Initial value: (vacío)
- Nota: AppSheet pone `UNIQUEID()` como valor inicial de la clave; borrarlo. La acción asigna `"OBR-"&UNIQUEID()`.

**`Codigo`** (Text, etiqueta)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción lo fija con `[Numero]&" - "&[Nombre]`.

**`Proforma_ID`** (Ref a `Proformas`)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`

**`Obra_Principal_ID`** (Ref a `Obras`)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `FALSE`
- Nota: queda vacío si la obra es principal; la acción lo llena solo cuando la proforma es `Complementaria`.

**`Cliente_ID`** (Ref a `Clientes`)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`

**`Responsable_ID`** (Ref a `Trabajadores`)
- Require?: `FALSE`
- Nota: la obra nace sin responsable. Lo asigna un usuario de OXY Gestión (arquitectura, DA-03 y DA-08). El `Editable?` se define en la especificación de OXY Gestión.

**`Estado`** (Enum)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción lo fija en `"Por iniciar"`. Los valores del Enum están en el modelo de datos.

**`Fecha_Inicio`** (Date)
- Require?: `FALSE`
- Initial value: (vacío)
- Nota: la llena OXY Gestión; quitar el `TODAY()` que AppSheet pone por defecto. El `Editable?` se define en la especificación de OXY Gestión.

**`Fecha_Fin_Estimada`** (Date)
- Require?: `FALSE`
- Initial value: (vacío)
- Nota: la llena OXY Gestión; quitar el `TODAY()` que AppSheet pone por defecto. El `Editable?` se define en la especificación de OXY Gestión.

**`Fecha_Fin_Real`** (Date)
- Require?: `FALSE`
- Initial value: (vacío)
- Nota: la llena OXY Gestión; quitar el `TODAY()` que AppSheet pone por defecto. El `Editable?` se define en la especificación de OXY Gestión.

**`Fecha_Cierre`** (Date)
- Require?: `FALSE`
- Initial value: (vacío)
- Nota: la llena OXY Gestión; quitar el `TODAY()` que AppSheet pone por defecto. El `Editable?` se define en la especificación de OXY Gestión.

**`Motivo_Cierre_Con_Saldo`** (Text)
- Require?: `FALSE`
- Nota: la llena OXY Gestión. El `Editable?` se define en la especificación de OXY Gestión.

**`Motivo_Cancelacion`** (Text)
- Require?: `FALSE`
- Nota: la llena OXY Gestión. El `Editable?` se define en la especificación de OXY Gestión.

**`Precio_Neto_Base`** (Price)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción la fija con `[Precio_Neto]` de la proforma; queda congelada.

**`IGV_Base`** (Price)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción la fija con `[IGV_Monto]` de la proforma; queda congelada.

**`Total_Cobrar_Base`** (Price)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción la fija con `[Total_Cobrar]` de la proforma; queda congelada.

**`Costo_Planificado_Base`** (Price)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción la fija con `[Costo_Planificado]` de la proforma; queda congelada.

**`Fecha_Cobranza_Completa`** (Date)
- Require?: `FALSE`
- Initial value: (vacío)
- Nota: la llena el job de cobranza de OXY Gestión; quitar el `TODAY()` que AppSheet pone por defecto. El `Editable?` se define en la especificación de OXY Gestión.

**`Notificado_Cobro_Completo`** (Enum)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción lo fija en `"No"`; después lo cambia el job de cobranza de OXY Gestión.

**`Creado_En`** (DateTime)
- Editable?: `CONTEXT("ViewType") = "Never"`
- Require?: `TRUE`
- Nota: la acción lo fija con `NOW()`.

`Editable?` solo se evalúa si la tabla permite altas o ediciones y no bloquea a las acciones; si el editor no ofreciera alguna de las doce columnas con `Editable?` = `CONTEXT("ViewType") = "Never"` al configurar la acción, ver V28.

#### Tabla `Clientes` (solo altas)

**`Cliente_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `UNIQUEID()`

**`RUC`**
- Require?: `TRUE`
- Valid if: `LEN([_THIS])=11`
- Invalid value error: `El RUC debe tener 11 digitos.`

**`Razon_Social`**
- Require?: `TRUE`

**`Nombre_Corto`**
- Require?: `FALSE`

**`Direccion`**
- Require?: `FALSE`

**`Plazo_Pago_Dias`** (Number)
- Require?: `TRUE`
- Initial value: `NUMBER(LOOKUP("PLAZO_PAGO_DIAS_DEFECTO","Configuracion","Clave","Valor"))`

**`Activo`** (Yes/No)
- Show?: `FALSE`
- Require?: `TRUE`
- Initial value: `TRUE`

#### Tabla `Contactos_Cliente` (solo altas)

**`Contacto_ID`** (Text, clave)
- Show?: `FALSE`
- Editable?: `FALSE`
- Require?: `TRUE`
- Initial value: `UNIQUEID()`

**`Cliente_ID`** (Ref a `Clientes`)
- Require?: `TRUE`
- Nota: marcar *Is a part of* para ver los contactos dentro del cliente.

**`Nombre`**
- Require?: `TRUE`

**`Cargo`**
- Require?: `FALSE`

**`Telefono`**
- Require?: `FALSE`

**`Email`**
- Require?: `FALSE`

#### Demás tablas

`Tipos_Costo`, `Categorias_Costo`, `Trabajadores`, `Configuracion`, `Compania` y `Log_Eventos` no llevan configuración de columnas propia en esta app. Las columnas de `Log_Eventos` las llenan las acciones auxiliares y los bots; nadie las edita desde una pantalla.

### 3.4 Slices

**`S_Proformas_Activas`**
- Source table: `Proformas`
- Row filter condition: `[Estado]<>"Z-Eliminada"`
- Nota: la lista normal usa este slice.

**`S_Proformas_Enviadas`**
- Source table: `Proformas`
- Row filter condition: `[Estado]="Enviada"`
- Nota: proformas a la espera de respuesta del cliente.

**`S_Proformas_Eliminadas`**
- Source table: `Proformas`
- Row filter condition: `[Estado]="Z-Eliminada"`
- Nota: vista de auditoría con `Numero`, `Nombre`, `Eliminada_Por` y `Fecha_Eliminacion`.

### 3.5 Acciones de sistema

Se configuran en **Actions**, en las acciones de sistema de cada tabla. Las demás acciones de sistema (*View Ref*, etc.) se dejan como están. Las tablas sin *Deletes* no ofrecen la acción *Delete*.

**Acción de sistema *Add* de `Proformas`**
- Only if this condition is true: `<ROL_PRO>`

**Acción de sistema *Edit* de `Proformas`**
- Only if this condition is true: `AND(<ROL_PRO>,IN([Estado],LIST("Borrador","Enviada")))`

**Acciones de sistema *Add* y *Edit* de `Proforma_Conceptos` y de `Proforma_Planificacion`**
- Only if this condition is true: `<ROL_PRO>`
- Nota: el bloqueo por estado lo dan las columnas (`Editable?` según el estado de la proforma): las líneas existentes se editan en `Borrador` y `Enviada`. Agregar líneas nuevas en una `Enviada` es posible (decidido): la acción *Add* no depende del estado, y desde `Aceptada` la nueva línea ya no se puede guardar. ⚠ V27 ⚠ V29

**Acción de sistema *Delete* de `Proforma_Conceptos` y de `Proforma_Planificacion`**
- Only if this condition is true: `AND(<ROL_PRO>,[Proforma_ID].[Estado]="Borrador")`
- Nota: una línea digitada por error se borra solo mientras la proforma es `Borrador`. ⚠ V27

**Acción de sistema *Add* de `Obras`**
- Only if this condition is true: `FALSE`
- Nota: las obras se crean solo con `A_Aceptar_CrearObra`. Las acciones de grupo y de datos no dependen de esta condición. ⚠ V28

**Acciones de sistema *Add* de `Clientes` y de `Contactos_Cliente`**
- Only if this condition is true: `<ROL_PRO>`

### 3.6 Detección de datos incompletos

Si aparece una fila en alguno de estos slices, hay una operación a medias (la reparación está en las acciones `A_Aceptar_Completar` y `A_Aceptar_Reparar_Obra`).

**`S_Proformas_Inconsistentes`**
- Source table: `Proformas`
- Row filter condition: `OR(AND([Estado]="Aceptada",ISBLANK([Obra_Generada])),AND([Estado]="Enviada",ISNOTBLANK([Obra_Generada])))`

**`S_Proformas_Sin_PDF`**
- Source table: `Proformas`
- Row filter condition: `AND(IN([Estado],LIST("Enviada","Aceptada","Rechazada","Vencida")),OR(ISBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)="PENDIENTE"))`

---

## 4. Especificación de Vistas

Cada usuario decide cómo visualiza la app; las vistas se diseñan para celular y escritorio. Las rutas del editor están en **Views**. Cualquier usuario con alguno de los cuatro roles ve todas las vistas (no hay `Show if` por rol).

### 4.1 Navegación

| Menú | Vista | Posición |
|---|---|---|
| Navegación principal | `V_Proformas` | 1 (vista inicial) |
| Navegación principal | `V_Seguimiento` | 2 |
| Navegación principal | `V_Clientes` | 3 |
| Menú | `V_Eliminadas` | 4 |
| Menú | `V_Control_Obras` | 5 |
| Menú | `V_Control_PDF` | 6 |

### 4.2 Vistas principales

**`V_Proformas`**
- View type: Deck
- For this data: `S_Proformas_Activas`
- Sort by: `Estado` ascendente, luego `Fecha_Emision` descendente
- Group by: `Estado_Etiqueta`
- Primary header: `Etiqueta`
- Secondary header: `Cliente_ID`
- Summary column: `Total_Cobrar`
- Actions: ninguna propia; la acción de sistema *Add* crea una proforma
- Roles que la usan: los cuatro
- Nota: es la lista normal; no muestra eliminadas.

**`V_Seguimiento`**
- View type: Table
- For this data: `S_Proformas_Enviadas`
- Sort by: `Fecha_Vigencia` ascendente
- Columns: `Numero`, `Nombre`, `Cliente_ID`, `Total_Cobrar`, `Fecha_Envio`, `Fecha_Vigencia`
- Actions: ninguna propia
- Roles que la usan: los cuatro
- Nota: las que vencen primero salen arriba.

**`V_Clientes`**
- View type: Table
- For this data: `Clientes`
- Sort by: `Razon_Social` ascendente
- Columns: `Razon_Social`, `RUC`, `Nombre_Corto`, `Plazo_Pago_Dias`
- Actions: *Add* (alta de cliente); no hay *Edit* ni *Delete*
- Roles que la usan: los cuatro
- Nota: para dar de alta un cliente nuevo antes de armar la proforma. Los contactos se agregan desde el detalle del cliente.

**`V_Eliminadas`**
- View type: Table
- For this data: `S_Proformas_Eliminadas`
- Sort by: `Fecha_Eliminacion` descendente
- Columns: `Numero`, `Nombre`, `Eliminada_Por`, `Fecha_Eliminacion`
- Actions: ninguna
- Roles que la usan: los cuatro

**`V_Control_Obras`**
- View type: Table
- For this data: `S_Proformas_Inconsistentes`
- Columns: `Numero`, `Estado_Etiqueta`, `Obra_Generada`
- Actions: `A_Aceptar_Completar`, `A_Aceptar_Reparar_Obra`
- Roles que la usan: los cuatro
- Nota: debe estar vacía. Si aparece una fila, hay una aceptación a medias.

**`V_Control_PDF`**
- View type: Table
- For this data: `S_Proformas_Sin_PDF`
- Columns: `Numero`, `Estado_Etiqueta`, `Doc_Proforma`
- Actions: ninguna
- Roles que la usan: los cuatro
- Nota: debe estar vacía. Una `Enviada` sin PDF válido se corrige pulsando `A_Generar_PDF`; una `Aceptada`, `Rechazada` o `Vencida` se corrige a mano en `OXYData`.

### 4.3 Vistas de detalle y de formulario

**Detalle de `Proformas`** (vista de sistema `Proformas_Detail`)
- Column order: `Etiqueta`, `Estado_Etiqueta`, `Cliente_ID`, `Contacto_ID`, `Direccion_Servicio`, `Fecha_Emision`, `Fecha_Vigencia`, `Fecha_Envio`, `Precio_Neto`, `IGV_Monto`, `Total_Cobrar`, `Costo_Planificado`, `Margen_Plan`, `Margen_Plan_Pct`, `Proforma_Previa_ID`, `Tipo_Relacion`, `Total_Relacionadas`, `Fecha_Aceptacion`, `Doc_Aceptacion`, `Motivo_Rechazo`, `Fecha_Rechazo`, `Motivo_Anulacion`, `Fecha_Anulacion`, `Eliminada_Por`, `Fecha_Eliminacion`, `Doc_Oficial`, `Doc_Proforma_Personalizado`, `Obra_Generada`
- Inline: `Proforma_Conceptos` y `Proforma_Planificacion` (vistas en línea de las columnas inversas *Related ...*; nombres exactos por verificar en el editor, ⚠ V11)
- Actions: `A_Generar_PDF`, `A_Enviar`, `A_Aceptar`, `A_Rechazar`, `A_Anular`, `A_Eliminar`, `A_Aceptar_Completar`, `A_Aceptar_Reparar_Obra`, *Edit*
- Nota: `Doc_Proforma` y los datos de OXY para el PDF no se listan: se exponen por `Doc_Oficial`.

**Formulario de `Proformas`** (vista de sistema `Proformas_Form`)
- Column order: `Numero`, `Nombre`, `Cliente_ID`, `Contacto_ID`, `Direccion_Servicio`, `Fecha_Emision`, `Fecha_Vigencia`, `Proforma_Previa_ID`, `Tipo_Relacion`, `Doc_Proforma_Personalizado`, `Fecha_Aceptacion`, `Doc_Aceptacion`, `Motivo_Rechazo`, `Motivo_Anulacion`
- Nota: la visibilidad de cada campo la gobierna su `Show?`.

**Formularios de `Proforma_Conceptos` y `Proforma_Planificacion`**
- Column order de conceptos: `Orden`, `Concepto`, `Monto_Sin_IGV`
- Column order de planificación: `Tipo_Costo_ID`, `Descripcion`, `Cantidad`, `Unidad`, `Costo_Unitario`, `Tiene_IGV`, `Es_Credito_Fiscal`
- Nota: `Proforma_ID` se llena sola al agregar desde la vista en línea.

**Detalle de `Obras`** (vista de sistema `Obras_Detail`, de solo lectura)
- Column order: `Codigo`, `Estado`, `Cliente_ID`, `Responsable_ID`, `Precio_Neto_Base`, `IGV_Base`, `Total_Cobrar_Base`, `Costo_Planificado_Base`
- Actions: ninguna
- Nota: se llega desde `Obra_Generada`. La obra se opera en OXY Gestión.

**Detalle de `Clientes`** (vista de sistema `Clientes_Detail`)
- Inline: `Contactos_Cliente`
- Actions: *Add* de `Contactos_Cliente`; sin *Edit*

### 4.4 Reglas de formato por estado

Se crean en **Views → Format rules** sobre `Proformas`.

| Regla | Condición | Efecto |
|---|---|---|
| `F_Borrador` | `[Estado]="Borrador"` | Texto gris |
| `F_Enviada` | `[Estado]="Enviada"` | Texto azul |
| `F_Aceptada` | `[Estado]="Aceptada"` | Texto verde |
| `F_Rechazada` | `[Estado]="Rechazada"` | Texto rojo |
| `F_Vencida` | `[Estado]="Vencida"` | Texto naranja |
| `F_Anulada` | `[Estado]="Anulada"` | Texto gris oscuro, tachado |
| `F_Margen` | `AND([Estado]="Borrador",[Aviso_Margen])` | Texto del total en rojo |

---

## 5. Especificación de Acciones

### 5.1 Matriz acción × rol

✓ = la acción aparece y se ejecuta. Las auxiliares no las ve ningún usuario: las llaman los grupos y los bots.

| Acción | Código | `Super` | `Administracion` | `Supervisor` | `Planificacion` |
|---|---|---|---|---|---|
| `A_Enviar` | PRO-A01 | ✓ | ✓ | ✓ | ✓ |
| `A_Rechazar` | PRO-A02 | ✓ | ✓ | ✓ | ✓ |
| `A_Anular` | PRO-A03 | ✓ | ✓ | ✓ | ✓ |
| `A_Eliminar` | PRO-A04 | ✓ | ✓ | ✓ | ✓ |
| `A_Aceptar_Set` | PRO-A05 | auxiliar | auxiliar | auxiliar | auxiliar |
| `A_Aceptar_CrearObra` | PRO-A06 | auxiliar | auxiliar | auxiliar | auxiliar |
| `A_Aceptar` | PRO-A07 | ✓ | ✓ | ✓ | ✓ |
| `A_Aceptar_Completar` | PRO-A08 | ✓ | ✓ | ✓ | ✓ |
| `A_Aceptar_Reparar_Obra` | PRO-A09 | ✓ | ✓ | ✓ | ✓ |
| `A_Generar_PDF` | PRO-A10 | ✓ | ✓ | ✓ | ✓ |
| `A_Vencer_Log` | PRO-A11 | auxiliar | auxiliar | auxiliar | auxiliar |
| `A_Vencer_Set` | PRO-A12 | auxiliar | auxiliar | auxiliar | auxiliar |

Acciones de sistema: *Add* y *Edit* de las tablas de proforma, *Delete* de conceptos y planificación (solo en `Borrador`) y *Add* de `Clientes` y `Contactos_Cliente`, con los cuatro roles (3.5).

### 5.2 Fichas

Cada ficha lista, de arriba abajo, lo que se completa en el editor (**Actions → + → Create a new action**, ⚠ V15). Una línea que empieza por "Nota:" no se configura. **Roles permitidos** repite la lista de la app.

#### PRO-A01 · `A_Enviar` · Acción visible
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** `A_Generar_PDF` (PRO-A10)
- **For a record of this table:** `Proformas`
- **Action name:** `A_Enviar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Enviada"`
  - `Fecha_Envio` = `TODAY()`
  - Nota: no genera el PDF ni fija `Fecha_Vigencia`; solo cambia el estado.
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Borrador",COUNT(SELECT(Proforma_Conceptos[Concepto_ID],[Proforma_ID]=[_THISROW].[Proforma_ID]))>0,COUNT(SELECT(Proforma_Planificacion[Planif_ID],[Proforma_ID]=[_THISROW].[Proforma_ID]))>0,ISNOTBLANK([Cliente_ID]),ISNOTBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)<>"PENDIENTE",ISNOTBLANK([Fecha_Vigencia]),[Fecha_Vigencia]>=TODAY())`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `IF([Aviso_Margen],"El margen planificado es menor al mínimo. ","")&"¿Enviar la proforma "&[Numero]&"? Verifique que el PDF esté generado con los últimos cambios."` ⚠ V05
- **Position:** Prominent
- **Display name:** Enviar
- **Idempotencia:** tras ejecutarse, el estado deja de ser `Borrador` y el botón desaparece.
- **Prueba +:** un `Borrador` con conceptos, planificación, vigencia vigente y PDF generado con `A_Generar_PDF`: aparece, pide confirmación y queda `Enviada` con `Fecha_Envio`. Efectos: `B_Log_Proformas` escribe el log y `B_Notif_Proformas` envía el correo interno. `B_Proforma_PDF` no se dispara. La proforma previa, si hay, no cambia de estado.
- **Prueba −:** no aparece si el `Borrador` no tiene conceptos, planificación o cliente; si no tiene PDF, o `Doc_Proforma` está en `PENDIENTE|...`; si `Fecha_Vigencia` está vacía o vencida; o si la proforma no es `Borrador`. Con `Aviso_Margen` verdadero, el mensaje de confirmación es el de margen bajo. Subir `Doc_Proforma_Personalizado` no es requisito.
- **Repetición:** una proforma `Enviada` no muestra el botón.
- **Si falla:** si el botón no aparece, revisar cuál de las condiciones falta. Si el mensaje no cambia con `Aviso_Margen`, ver V05. Comprobar que `Configuracion` tiene `VIGENCIA_PROFORMA_DIAS` con un entero.

#### PRO-A02 · `A_Rechazar` · Acción visible
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Rechazar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Rechazada"`
  - `Fecha_Rechazo` = `TODAY()`
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Enviada",ISNOTBLANK([Motivo_Rechazo]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Marcar la proforma como rechazada por el cliente? No podrá editarse; para corregirla cree una proforma nueva y relaciónela con esta.`
- **Position:** Prominent
- **Display name:** Rechazar
- **Idempotencia:** después del cambio el estado ya no es `Enviada`.
- **Prueba +:** una `Enviada`: el botón aparece solo después de guardar `Motivo_Rechazo`. Resultado: `Rechazada`, `Fecha_Rechazo` = hoy y un evento `PROFORMA_RECHAZADA` en `Log_Eventos`.
- **Prueba −:** una `Enviada` sin motivo, o cualquier otro estado: no aparece.
- **Repetición:** ya `Rechazada`: no aparece.
- **Si falla:** si no hay evento en el log, revisar `B_Log_Proformas`.

#### PRO-A03 · `A_Anular` · Acción visible
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Anular`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Anulada"`
  - `Fecha_Anulacion` = `TODAY()`
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Enviada",ISNOTBLANK([Motivo_Anulacion]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Anular la proforma? Esta acción no se puede deshacer.`
- **Position:** Prominent
- **Display name:** Anular
- **Idempotencia:** después del cambio el estado ya no es `Enviada`.
- **Prueba +:** una `Enviada` con `Motivo_Anulacion`: queda `Anulada`, con `Fecha_Anulacion` = hoy y evento `PROFORMA_ANULADA`.
- **Prueba −:** sin motivo o en otro estado: no aparece. Un `Borrador` no se anula: se elimina con `A_Eliminar`.
- **Repetición:** ya `Anulada`: no aparece.
- **Si falla:** igual que `A_Rechazar`.

#### PRO-A04 · `A_Eliminar` · Acción visible
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Eliminar`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Estado` = `"Z-Eliminada"`
  - `Eliminada_Por` = `USEREMAIL()`
  - `Fecha_Eliminacion` = `TODAY()`
  - Nota: no se pide motivo.
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Borrador")`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `"¿Eliminar la proforma "&[Numero]&"? Dejará de mostrarse y no se puede deshacer."`
- **Position:** Prominent
- **Display name:** Eliminar
- **Idempotencia:** después del cambio el estado deja de ser `Borrador` y el botón desaparece.
- **Prueba +:** un `Borrador`: aparece, pide confirmación y queda `Z-Eliminada` con `Eliminada_Por` = la cuenta y `Fecha_Eliminacion` = hoy. `B_Log_Proformas` escribe `PROFORMA_ELIMINADA`; no sale correo. La proforma sale de `V_Proformas` y aparece en `V_Eliminadas`. Si era la previa de otra, deja de contar en su `Total_Relacionadas`.
- **Prueba −:** en una proforma `Enviada`, `Aceptada`, `Rechazada`, `Vencida` o `Anulada`: no aparece. Con una cuenta de rol `Campo`: la app no se abre (no está en la lista de usuarios).
- **Repetición:** ya `Z-Eliminada`: no aparece.
- **Si falla:** si el evento no queda en `Log_Eventos`, revisar `B_Log_Proformas`. Las líneas de conceptos y planificación de la proforma eliminada permanecen en `OXYData`.

#### PRO-A05 · `A_Aceptar_Set` · Auxiliar
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
- **Prueba +:** se verifica con `A_Aceptar`.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** no aplica.
- **Si falla:** ver `A_Aceptar` y `A_Aceptar_Completar`.

#### PRO-A06 · `A_Aceptar_CrearObra` · Auxiliar
- **Depende de:** tabla `Obras` con *Adds* en la app
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_CrearObra`
- **Do this:** Data: add a new row to another table using values from this row
- **Table to add rows to:** `Obras`
- **Set these columns:**
  - `Obra_ID` = `"OBR-"&UNIQUEID()`
  - `Codigo` = `[Numero]&" - "&[Nombre]`
  - `Proforma_ID` = `[Proforma_ID]`
  - `Cliente_ID` = `[Cliente_ID]`
  - `Obra_Principal_ID` = `IF(AND([Tipo_Relacion]="Complementaria",ISNOTBLANK([Proforma_Previa_ID])),LOOKUP([Proforma_Previa_ID],"Obras","Proforma_ID","Obra_ID"),"")`
  - Nota: depende de que el usuario haya asignado a mano la previa y el tipo `Complementaria`. Si no lo hizo, la obra nace como principal.
  - `Estado` = `"Por iniciar"`
  - `Precio_Neto_Base` = `[Precio_Neto]`
  - `IGV_Base` = `[IGV_Monto]`
  - `Total_Cobrar_Base` = `[Total_Cobrar]`
  - `Costo_Planificado_Base` = `[Costo_Planificado]`
  - `Notificado_Cobro_Completo` = `"No"`
  - `Creado_En` = `NOW()`
  - Nota: `Responsable_ID` no se llena: la obra nace sin responsable y lo asigna un usuario de OXY Gestión.
- **Only if this condition is true:** (dejar vacío)
- **Needs confirmation?:** No
- **Position:** Hide
- **Idempotencia:** esta acción no comprueba si ya existe una obra; lo hacen `A_Aceptar` y `A_Aceptar_Reparar_Obra` con `ISBLANK([Obra_Generada])`. No exponerla en ningún botón.
- **Prueba +:** se verifica con `A_Aceptar`.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ejecutarla dos veces crea dos obras; por eso solo la llaman los grupos con su condición.
- **Si falla:** la planificación sigue ligada a la proforma aceptada (ya bloqueada): no se copia a la obra; solo se guardan los totales. Si algún total sale en blanco, revisar las virtuales de la proforma.

#### PRO-A07 · `A_Aceptar` · Grupo (botón)
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** `A_Aceptar_Set` (PRO-A05), `A_Aceptar_CrearObra` (PRO-A06)
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_CrearObra`
  2. `A_Aceptar_Set`
  - Nota: la obra se crea antes de cambiar el estado: si falla la creación, la proforma sigue `Enviada` y el botón sigue disponible para reintentar.
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Enviada",ISNOTBLANK([Fecha_Aceptacion]),ISNOTBLANK([Doc_Aceptacion]),ISBLANK([Obra_Generada]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `¿Aceptar la proforma y crear la obra?`
- **Position:** Prominent
- **Display name:** Aceptar
- **Idempotencia:** `ISBLANK([Obra_Generada])` oculta el botón en cuanto existe la obra. Si el paso 1 se completa y el paso 2 falla, la proforma queda `Enviada` con obra: `A_Aceptar_Completar` completa el cambio de estado.
- **Prueba +:** una `Enviada` con `Fecha_Aceptacion` y `Doc_Aceptacion`: queda `Aceptada` y existe una obra `Por iniciar`, sin responsable, con los totales congelados. Eventos `PROFORMA_ACEPTADA` y `OBRA_CREADA`.
- **Prueba −:** sin `Fecha_Aceptacion` o sin `Doc_Aceptacion`: el botón no aparece. Una `Enviada` que ya tiene obra: no aparece.
- **Repetición:** el botón desaparece tras la primera ejecución; no se crea una segunda obra.
- **Si falla:** revisar `V_Control_Obras`. Una `Enviada` con obra se completa con `A_Aceptar_Completar`; una `Aceptada` sin obra, con `A_Aceptar_Reparar_Obra`.

#### PRO-A08 · `A_Aceptar_Completar` · Grupo (botón de reparación)
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** `A_Aceptar_Set` (PRO-A05)
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_Completar`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_Set`
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Enviada",ISNOTBLANK([Obra_Generada]),ISNOTBLANK([Fecha_Aceptacion]),ISNOTBLANK([Doc_Aceptacion]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `La obra ya existe pero la proforma sigue Enviada. ¿Completar la aceptación?`
- **Position:** Prominent
- **Display name:** Completar aceptación
- **Idempotencia:** tras ejecutarse el estado es `Aceptada` y el botón desaparece. No crea filas.
- **Prueba +:** provocar el fallo poniendo una `Enviada` con obra (crear la obra a mano en `OXYData` y ligarla a la proforma): el botón aparece; al ejecutarlo la proforma queda `Aceptada` y no hay segunda obra.
- **Prueba −:** una `Enviada` sin obra: no aparece.
- **Repetición:** ya `Aceptada`: no aparece.
- **Si falla:** comprobar que `Obra_Generada` resuelve la obra de esa proforma.

#### PRO-A09 · `A_Aceptar_Reparar_Obra` · Grupo (botón de reparación)
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** `A_Aceptar_CrearObra` (PRO-A06)
- **For a record of this table:** `Proformas`
- **Action name:** `A_Aceptar_Reparar_Obra`
- **Do this:** Grouped: execute a sequence of actions
- **Actions:** (en este orden)
  1. `A_Aceptar_CrearObra`
- **Only if this condition is true:** `AND(<ROL_PRO>,[Estado]="Aceptada",ISBLANK([Obra_Generada]))`
- **Needs confirmation?:** Yes
- **Confirmation Message:** `La proforma está Aceptada pero no tiene obra. ¿Crear la obra ahora?`
- **Position:** Prominent
- **Display name:** Crear obra faltante
- **Idempotencia:** `ISBLANK([Obra_Generada])` oculta el botón en cuanto la obra existe.
- **Prueba +:** poner a mano una proforma en `Aceptada` sin obra: aparece; al ejecutarlo existe una obra `Por iniciar` con los totales congelados.
- **Prueba −:** una `Aceptada` con obra: no aparece.
- **Repetición:** el botón desaparece; no se crea otra obra.
- **Si falla:** ver `A_Aceptar_CrearObra`.

#### PRO-A10 · `A_Generar_PDF` · Acción visible
- **Roles permitidos:** `Super`, `Administracion`, `Supervisor`, `Planificacion`
- **Depende de:** —
- **For a record of this table:** `Proformas`
- **Action name:** `A_Generar_PDF`
- **Do this:** Data: set the values of some columns in this row
- **Set these columns:**
  - `Doc_Proforma` = `"PENDIENTE|"&TEXT(NOW(),"yyyyMMddHHmmss")`
  - Nota: la señal lleva el sello de fecha y hora, así que es distinta en cada pulsación; eso dispara `B_Proforma_PDF` aunque el valor anterior fuera otra señal. El mismo sello da nombre al archivo.
- **Only if this condition is true:** `AND(<ROL_PRO>,IN([Estado],LIST("Borrador","Enviada")),OR(ISBLANK([Doc_Proforma]),LEFT([Doc_Proforma],9)<>"PENDIENTE"))`
- **Needs confirmation?:** No
- **Position:** Prominent
- **Display name:** Generar PDF
- **Idempotencia:** se puede pulsar las veces que haga falta mientras sea `Borrador` o `Enviada`; cada pulsación crea un archivo nuevo con otro sello y `Doc_Proforma` apunta al último. Los anteriores quedan en Drive sin usar.
- **Prueba +:** en un `Borrador`: al pulsarlo, `Doc_Proforma` pasa a `PENDIENTE|<Sello>` y poco después a `Proformas_Files/<Numero>_<Sello>.pdf`. Cambiar un concepto y pulsarlo otra vez genera un segundo archivo con el cambio. En una `Enviada` también aparece, y el nuevo PDF reemplaza al anterior como `Doc_Proforma` (el anterior queda en Drive).
- **Prueba −:** una proforma `Aceptada`, `Rechazada`, `Vencida`, `Anulada` o `Z-Eliminada`: no aparece (el PDF no se regenera desde `Aceptada`).
- **Repetición:** mientras el valor empiece por `PENDIENTE` el botón no aparece; al terminar el bot reaparece.
- **Si falla:** si el valor se queda en `PENDIENTE|...`, el bot no corrió: revisar `Monitor` de `B_Proforma_PDF`. Para reintentar hay que vaciar `Doc_Proforma` en `OXYData`. Si el bot se dispara en una `Enviada`, el estado no cambia: solo cambia `Doc_Proforma`.

#### PRO-A11 · `A_Vencer_Log` · Auxiliar
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
- **Idempotencia:** el `Evento_ID` es único por proforma; `B_Proformas_Vencidas` solo la llama para proformas sin ese evento.
- **Prueba +:** se verifica con `B_Proformas_Vencidas`.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver `B_Proformas_Vencidas`.
- **Si falla:** comprobar que `Log_Eventos` permite *Adds* en la app.

#### PRO-A12 · `A_Vencer_Set` · Auxiliar
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
- **Prueba +:** se verifica con `B_Proformas_Vencidas`.
- **Prueba −:** no aparece en ninguna vista.
- **Repetición:** ver `B_Proformas_Vencidas`.
- **Si falla:** ver `B_Proformas_Vencidas`.

---

## 6. Especificación de Automatizaciones

Los bots viven en **Automation → Bots** (⚠ V15). Todos se crean en esta app; las proformas solo se escriben aquí, así que ningún bot de proforma se duplica en otra app (⚠ V18). Zona horaria de los programados: America/Lima.

### 6.1 Inventario

| Código | Bot | Tipo | Tabla | Qué hace |
|---|---|---|---|---|
| PRO-B01 | `B_Proformas_Vencidas` | Programado, diario 06:00 | `Proformas` | Registra el evento y pasa a `Vencida` las `Enviada` con vigencia pasada |
| PRO-B02 | `B_Proforma_PDF` | Cambio de datos | `Proformas` | Genera el PDF desde la plantilla |
| PRO-B03 | `B_Log_Proformas` | Cambio de datos | `Proformas` | Escribe el evento de cada cambio de estado |
| PRO-B04 | `B_Notif_Proformas` | Cambio de datos | `Proformas` | Avisa por correo interno |
| OBR-B01 | `B_Log_Obra_Creada` | Cambio de datos | `Obras` | Escribe `OBRA_CREADA` y avisa por push y correo |

Orden de construcción: `A_Vencer_Log` y `A_Vencer_Set` antes de `B_Proformas_Vencidas`.

#### PRO-B01 · `B_Proformas_Vencidas` · Bot programado
- **Tabla:** `Proformas`
- **Event:**
  - Event type: Scheduled
  - Schedule: Daily
  - Time: 06:00
  - Time zone: America/Lima
- **Depende de:** `A_Vencer_Log` (PRO-A11), `A_Vencer_Set` (PRO-A12)
- **Process:**
  1. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Proformas`
     - Referenced Rows: `SELECT(Proformas[Proforma_ID],AND([Estado]="Enviada",[Fecha_Vigencia]<TODAY(),ISBLANK(LOOKUP("PROFORMA_VENCIDA|"&[Proforma_ID],"Log_Eventos","Evento_ID","Evento_ID"))))`
     - Referenced Action: `A_Vencer_Log`
  2. Step type: Run a data action → Execute an action on a set of rows
     - Referenced Table: `Proformas`
     - Referenced Rows: `SELECT(Proformas[Proforma_ID],AND([Estado]="Enviada",[Fecha_Vigencia]<TODAY()))`
     - Referenced Action: `A_Vencer_Set` ⚠ V19
  - Nota: activar **Trigger other bots** para que `B_Notif_Proformas` envíe el correo interno al pasar a `Vencida` (⚠ V10).
- **Datos que escribe:** `Log_Eventos` (evento `PROFORMA_VENCIDA`) y `Proformas.Estado`.
- **Idempotencia:** primero se registra el evento (una sola vez por proforma, por su `Evento_ID`) y después se cambia el estado. Si la corrida se corta entre los dos pasos, la siguiente completa el estado sin duplicar el log.
- **Límites del plan Core:** una ejecución diaria; el correo de `B_Notif_Proformas` cuenta contra la cuota de correos. ⚠ V13
- **Prueba +:** poner `Fecha_Vigencia` en una fecha pasada en una `Enviada` y ejecutar el bot a mano: pasa a `Vencida`, con un evento `PROFORMA_VENCIDA` en el log.
- **Prueba −:** una `Enviada` con vigencia futura, o una proforma de otro estado con vigencia pasada: no cambia.
- **Repetición:** ejecutar el bot dos veces seguidas no crea un segundo evento ni cambia nada.
- **Si falla:** en `Monitor`, abrir la ejecución y ver en qué paso quedó. Si el paso 1 corrió y el 2 no, ejecutar el bot otra vez.

#### PRO-B02 · `B_Proforma_PDF` · Bot de evento
- **Tabla:** `Proformas`
- **Event:**
  - Event type: Data change
  - Table: `Proformas`
  - Data change type: Updates only
  - Condition: `AND(LEFT([_THISROW_AFTER].[Doc_Proforma],9)="PENDIENTE",[_THISROW_AFTER].[Doc_Proforma]<>[_THISROW_BEFORE].[Doc_Proforma])`
- **Depende de:** `A_Generar_PDF` (PRO-A10)
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
  - Nota: no hay paso de correo: el PDF no se envía al cliente; solo se archiva.
- **Plantilla `Plantilla_Proforma`:** un Google Doc con estas marcas de AppSheet:
  - Cabecera de la proforma: `<<[Numero]>>`, `<<[Nombre]>>`, `<<[Fecha_Emision]>>`, `<<[Fecha_Vigencia]>>`, `<<[Direccion_Servicio]>>`.
  - Cliente y contacto por referencia: `<<[Cliente_ID].[Razon_Social]>>`, `<<[Contacto_ID].[Nombre]>>`.
  - Tabla de conceptos entre `<<Start: [Related Proforma_Conceptoss]>>` y `<<End>>`, con `<<[Concepto]>>` y `<<[Monto_Sin_IGV]>>`.
  - Totales: `<<[Precio_Neto]>>`, `<<[IGV_Monto]>>` y `<<[Total_Cobrar]>>`.
  - Datos de OXY en el encabezado y el pie: `<<[Empresa_Nombre_Comercial]>>`, `<<[Empresa_Razon_Social]>>`, `<<[Empresa_RUC]>>`, `<<[Empresa_Direccion_Fiscal]>>`, `<<[Empresa_Telefono]>>`, `<<[Empresa_Email]>>`, `<<[Empresa_Web]>>`.
  - Al final: `<<[Proforma_Condiciones]>>`, `<<[Proforma_Cuentas_Bancarias]>>`, `<<[Proforma_Firma_Nombre]>>`.
  - La planificación no se imprime. Verificar el nombre exacto de la columna inversa `Related ...` en el editor (⚠ V11).
- **Datos que escribe:** el archivo PDF en Drive y `Doc_Proforma`. Cada generación crea un archivo nuevo (nombre con `Numero` y sello); nada se sobrescribe.
- **Idempotencia:** la condición solo se cumple cuando `Doc_Proforma` cambia a una señal `PENDIENTE|...`; el segundo paso la reemplaza por una ruta, que no empieza por `PENDIENTE`, y no vuelve a disparar el bot.
- **Límites del plan Core:** verificar que *Create a new file* está disponible en Core y su cuota (⚠ V06).
- **Prueba +:** al pulsar *Generar PDF* en un `Borrador` o `Enviada` aparece `Proformas_Files/<Numero>_<Sello>.pdf` en Drive y `Doc_Proforma` apunta a él. El PDF muestra `Fecha_Vigencia`, conceptos, subtotal, IGV y total, sin la planificación. No sale ningún correo al cliente. La ruta guardada abre desde la app con una cuenta de cualquiera de los cuatro roles.
- **Prueba −:** editar otra columna, subir un `Doc_Proforma_Personalizado` o enviar o aceptar la proforma no genera un PDF nuevo.
- **Repetición:** cada pulsación de `A_Generar_PDF` genera otro archivo con otro sello; los anteriores quedan en Drive y se pueden borrar a mano.
- **Si falla:** si `Doc_Proforma` se queda en `PENDIENTE|...` en un `Borrador` o `Enviada`, vaciar el valor en `OXYData` y pulsar `A_Generar_PDF`. Desde `Aceptada` ya no se puede regenerar y se corrige a mano en `OXYData`.

#### PRO-B03 · `B_Log_Proformas` · Bot de evento
- **Tabla:** `Proformas`
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
  - Nota: `Vencida` no se registra aquí: lo hace `A_Vencer_Log` dentro de `B_Proformas_Vencidas`.
- **Datos que escribe:** una fila en `Log_Eventos` por cada cambio de estado.
- **Idempotencia:** la condición exige que el estado cambie; una actualización que no lo cambia no genera evento.
- **Límites del plan Core:** una ejecución por cambio de estado.
- **Prueba +:** cada una de `A_Enviar`, `A_Rechazar`, `A_Anular`, `A_Eliminar` y `A_Aceptar` deja una fila nueva en `Log_Eventos` con el tipo correcto.
- **Prueba −:** editar `Motivo_Rechazo` sin cambiar el estado, o que `B_Proforma_PDF` actualice `Doc_Proforma`: no deja evento.
- **Repetición:** repetir la acción no es posible (el botón desaparece); si se fuerza a mano el mismo estado, no hay evento.
- **Si falla:** en `Monitor`, comprobar si el evento se disparó, si la condición fue falsa o si falló la escritura en `Log_Eventos`.

#### PRO-B04 · `B_Notif_Proformas` · Bot de evento
- **Tabla:** `Proformas`
- **Event:**
  - Event type: Data change
  - Table: `Proformas`
  - Data change type: Updates only
  - Condition: `AND([_THISROW_BEFORE].[Estado]<>[_THISROW_AFTER].[Estado],IN([_THISROW_AFTER].[Estado],LIST("Enviada","Aceptada","Rechazada","Vencida")))`
- **Depende de:** —
- **Process:**
  1. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Administracion","Supervisor","Planificacion")),[Activo]=TRUE))` ⚠ V03
     - Subject: `Proforma <<[Numero]>>: <<[Estado]>>`
     - Body: texto con `<<[Etiqueta]>>`, el cliente (`<<[Cliente_ID].[Razon_Social]>>`) y `<<[Total_Cobrar]>>`. Es un aviso interno; nunca va al cliente.
- **Datos que escribe:** ninguno (solo envía correo).
- **Idempotencia:** un correo por cambio de estado.
- **Límites del plan Core:** cuota diaria de correos, compartida con los bots de las demás apps. El aviso de `Vencida` depende de que `B_Proformas_Vencidas` tenga activo *Trigger other bots* (⚠ V10). Si V10 falla, quitar `Vencida` de la condición: ese caso queda cubierto por la alerta de proforma sin respuesta del Dashboard.
- **Prueba +:** enviar una proforma genera un correo a todos los usuarios activos con rol `Administracion`, `Supervisor` o `Planificacion`. `Super` no recibe.
- **Prueba −:** anular o eliminar una proforma no envía correo.
- **Repetición:** repetir la acción no es posible; no hay segundo correo.
- **Si falla:** si el bot se ejecutó pero no llegó el correo, un `Monitor` correcto solo prueba que AppSheet ejecutó los pasos, no que el aviso llegó; revisar la cuota y la bandeja de correo no deseado.

#### OBR-B01 · `B_Log_Obra_Creada` · Bot de evento
- **Tabla:** `Obras`
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
     - Recipients: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Administracion","Supervisor")),[Activo]=TRUE))`
     - Message: `Obra <<[Codigo]>> creada. Falta asignar responsable.` ⚠ V03, V14
  3. Step type: Send an email
     - To: `SELECT(Trabajadores[Email],AND(IN([Rol],LIST("Operaciones","Supervisor")),[Activo]=TRUE))` ⚠ V03
     - Subject: `Nueva obra <<[Codigo]>>: falta asignar responsable`
     - Body: texto con `<<[Codigo]>>`, `<<[Cliente_ID].[Razon_Social]>>` y `<<[Total_Cobrar_Base]>>`. Indica que la obra ya está en OXY Gestión (después de sincronizar) y que un usuario de OXY Gestión debe asignarle el responsable.
  - Nota: la obra nace sin responsable, así que el correo va a `Operaciones` y `Supervisor`, que usan OXY Gestión y asignan el responsable.
- **Datos que escribe:** una fila en `Log_Eventos`.
- **Idempotencia:** se dispara una vez por alta de obra.
- **Límites del plan Core:** un push y un correo por obra creada.
- **Prueba +:** aceptar una proforma: aparece la obra, el evento `OBRA_CREADA`, el push a quienes tienen la app instalada y rol `Administracion` o `Supervisor`, y el correo a los usuarios activos `Operaciones` y `Supervisor`.
- **Prueba −:** editar una obra existente no dispara este bot (solo altas).
- **Repetición:** no se puede crear dos veces la obra de una proforma.
- **Si falla:** si el push no llegó, comprobar que el destinatario tiene OXY Proformas instalada (un push solo llega a quien tiene la app donde vive el bot).

---

## 7. Notificaciones

`Super` no recibe avisos. Los destinatarios se calculan en el momento del envío sobre `Trabajadores` (solo activos).

| Evento | Quién lo origina | Destinatarios | Canal | App que debe tener instalada el destinatario |
|---|---|---|---|---|
| `PROFORMA_ENVIADA`, `PROFORMA_ACEPTADA`, `PROFORMA_RECHAZADA`, `PROFORMA_VENCIDA` | `B_Notif_Proformas` | `Administracion`, `Supervisor`, `Planificacion` | Correo | Ninguna (el correo llega siempre) |
| `PROFORMA_ANULADA`, `PROFORMA_ELIMINADA` | `B_Log_Proformas` | Ninguno (solo registro) | – | – |
| `OBRA_CREADA` | `B_Log_Obra_Creada` | Push: `Administracion`, `Supervisor` · Correo: `Operaciones`, `Supervisor` | Push y correo | OXY Proformas para el push; ninguna para el correo |

---

## 8. Relación con otras apps

**Lee de otras apps (lo que se edita en OXY Master):** `Clientes` y `Contactos_Cliente` (también reciben altas aquí), `Tipos_Costo`, `Categorias_Costo`, `Trabajadores`, `Configuracion` y `Compania`. Un cambio hecho en OXY Master llega a esta app cuando sincroniza.

**Escribe, y otras apps leen:**
- `Obras`: OXY Gestión ve la obra nueva cuando sincroniza y le asigna el responsable.
- `Proformas`, `Proforma_Conceptos` y `Proforma_Planificacion`: OXY Gestión y OXY Campo leen lo que necesitan de ellas (arquitectura, sección 6).
- `Clientes` y `Contactos_Cliente`: las altas se ven en las demás apps al sincronizar.
- `Log_Eventos`: los eventos de proforma y de obra creada.

**Bots duplicados:** ninguno. Las proformas solo se escriben aquí. Tampoco hay aquí bots de notificación del log: `B_Notif_Log_Correo` y `B_Notif_Log_Push` viven en OXY Gestión y solo atienden eventos de procesos programados.

**Retrasos de sincronización:** cada app muestra los datos de otra solo después de sincronizar. Quien necesite ver una obra recién creada en OXY Gestión actualiza esa app.

---

## 9. Configuración de la app

1. **Require user sign-in:** activo (⚠ V15 para la ruta en el editor).
2. **Allowed users:** las cuentas de 2.2.
3. **Zona horaria de la app y de los bots programados:** America/Lima.
4. **Vista inicial:** `V_Proformas`.
5. **Sincronización:** sincronizar al abrir la app y después de cada acción.
6. **Apariencia:** tema claro; ícono y nombre `OXY Proformas`.
7. **Archivos:** carpeta de Drive `Proformas_Files` para los PDF y para `Doc_Aceptacion` y `Doc_Proforma_Personalizado`.

---

## 10. Pruebas

Cuentas de prueba: una por rol de la app (`Super`, `Administracion`, `Supervisor`, `Planificacion`), una `Operaciones` y una `Campo`. Las pruebas de cada acción y bot están en sus fichas.

| N.º | Cuenta | Qué se hace | Resultado esperado |
|---|---|---|---|
| PR-1 | `Planificacion` | Armar una proforma completa: cliente nuevo (alta), contacto nuevo, conceptos, planificación; generar el PDF | La proforma queda `Borrador` con PDF en `Proformas_Files`; el cliente y el contacto quedan en `Clientes` y `Contactos_Cliente` |
| PR-2 | `Supervisor` | Enviar la proforma de PR-1 | Queda `Enviada`; correo a `Administracion`, `Supervisor` y `Planificacion` (no a `Super`); evento `PROFORMA_ENVIADA` |
| PR-3 | `Administracion` | Cargar `Fecha_Aceptacion` y `Doc_Aceptacion`; aceptar | Proforma `Aceptada`; obra `Por iniciar` sin responsable y con totales congelados; eventos `PROFORMA_ACEPTADA` y `OBRA_CREADA`; push a `Administracion` y `Supervisor`; correo a `Operaciones` y `Supervisor` |
| PR-4 | `Administracion` | Abrir OXY Gestión y sincronizar | La obra aparece; el responsable está en blanco |
| PR-5 | `Planificacion` | Rechazar una enviada con motivo; crear una proforma nueva y relacionarla como `Revision` | Rechazo registrado; la relación no cambia ningún estado |
| PR-6 | `Super` | Anular una enviada con motivo; eliminar un borrador | Estados `Anulada` y `Z-Eliminada`; el eliminado solo aparece en `V_Eliminadas`; no salen correos |
| PR-7 | `Supervisor` | Complementaria: aceptar una proforma con `Tipo_Relacion = Complementaria` y previa aceptada | La obra nueva queda con `Obra_Principal_ID` igual a la obra de la previa |
| PR-8 | Cualquiera | Poner `Fecha_Vigencia` pasada en una `Enviada` y ejecutar `B_Proformas_Vencidas` a mano | Pasa a `Vencida`; un solo evento; un correo |
| PR-9 | `Planificacion` | Intentar editar, agregar o borrar un concepto o una línea de planificación de una proforma `Aceptada`, `Rechazada`, `Vencida` o `Anulada`; y borrar uno de una `Enviada` | No se puede editar, agregar ni borrar (⚠ V27, V29) |
| PR-16 | `Planificacion` | Editar el monto de un concepto y el costo unitario de una línea de planificación de una proforma `Enviada` | Se guarda; `Precio_Neto`, `Total_Cobrar` y `Costo_Planificado` se recalculan; el PDF no cambia hasta volver a generarlo (PR-17) |
| PR-10 | `Planificacion` | Intentar editar o borrar un cliente | La app no ofrece esas acciones |
| PR-11 | `Operaciones` | Intentar abrir OXY Proformas | La cuenta no está en la lista de usuarios: no abre |
| PR-12 | `Campo` | Intentar abrir OXY Proformas | La cuenta no está en la lista de usuarios: no abre |
| PR-13 | Cuenta inactiva (`Activo = No`) en la lista de usuarios | Abrir la app | Abre, pero ninguna acción aparece |
| PR-17 | `Planificacion` | En una proforma `Enviada`: agregar un concepto y una línea de planificación nuevos, pulsar `A_Generar_PDF` y subir un `Doc_Proforma_Personalizado` | Las líneas se guardan; el nuevo PDF aparece como `Doc_Proforma` con los montos corregidos y el personalizado se guarda; el estado sigue `Enviada`; en una `Aceptada` ninguna de las tres cosas es posible (⚠ V29) |
| PR-15 | `Planificacion` | Borrar un concepto y una línea de planificación de un `Borrador` | Las líneas desaparecen; `Precio_Neto` y `Costo_Planificado` se recalculan; hay que volver a generar el PDF antes de enviar |
| PR-14 | `Administracion` | Con una proforma `Enviada` y obra creada a mano, usar `A_Aceptar_Completar`; con una `Aceptada` sin obra, usar `A_Aceptar_Reparar_Obra` | Una sola obra por proforma; ninguna acción duplica |

---

## 11. Criterios de salida y orden de construcción

La app está terminada cuando:

- [ ] Las doce tablas de 3.1 están con los permisos indicados (incluidos los borrados de conceptos y planificación) y sin columnas virtuales en `Obras`.
- [ ] La configuración de columnas de 3.3, los slices de 3.4 y 3.6 y las acciones de sistema de 3.5 están aplicados.
- [ ] Las seis vistas del menú y las de detalle y formulario de la sección 4 existen y abren sin errores.
- [ ] Las acciones `A_Enviar` a `A_Vencer_Set` y los bots `B_Proformas_Vencidas`, `B_Proforma_PDF`, `B_Log_Proformas`, `B_Notif_Proformas` y `B_Log_Obra_Creada` guardan sin errores en el editor.
- [ ] Cada acción de usuario lleva la expresión de rol de 2.3 en su `Only if`.
- [ ] Las pruebas PR-1 a PR-17 se ejecutaron con resultado registrado.
- [ ] `V_Control_Obras` y `V_Control_PDF` quedan vacías con los datos de prueba.
- [ ] Las validaciones V03, V04, V05, V06, V10, V11, V13, V14, V15, V18, V19, V23, V24, V25, V26, V27, V28 y V29 están cerradas en el registro de la arquitectura.

---

## 12. Pendientes y decisiones de la app

| N.º | Tema | Qué falta |
|---|---|---|
| P-01 | Roles antiguos en el modelo de datos y el diccionario | Las descripciones de `Compania` y `Trabajadores.Rol` siguen con `Admin` y `Gerencia`. Se actualizan en la migración de roles |
| P-02 | `Obras.Responsable_ID`: ¿obligatorio para iniciar? | La columna ya no es requerida (se crea en blanco). Se define en el documento de OXY Gestión si `A_Iniciar` exige responsable |

**Validaciones nuevas de esta app** (se agregan al registro de la arquitectura):

| N.º | Qué se valida | Cómo | Resultado esperado | Plan B |
|---|---|---|---|---|
| V26 | Valor inicial `"PRF-"&UNIQUEID()` de `Proforma_ID` | Crear una proforma | La clave queda como `PRF-<id>` y es única | Usar `UNIQUEID()` solo |
| V27 | Bloqueo de líneas según el estado de la proforma | Editar un concepto y una línea de planificación en `Borrador`, `Enviada` y `Aceptada`; borrarlos en `Borrador` y en `Enviada` | Edita en `Borrador` y `Enviada`, no en `Aceptada`; borra solo en `Borrador` | Agregar la condición de estado al `Only if` de *Add* y *Edit* de esas tablas |
| V29 | Alta de líneas nuevas según el estado de la proforma | Agregar un concepto y una línea de planificación en `Borrador`, `Enviada` y `Aceptada` | Agrega en `Borrador` y `Enviada`; en `Aceptada` no se puede guardar | Agregar la condición de estado al `Only if` de *Add* de esas tablas |
| V28 | La acción `A_Aceptar_CrearObra` agrega la fila aunque la acción de sistema *Add* de `Obras` tenga `Only if` = `FALSE` | Aceptar una proforma | Se crea la obra | Dejar *Add* de `Obras` sin condición y no exponer ninguna vista de `Obras` con botón de alta |
