# OXY Industrial S.R.L. — Especificación del modelo de datos

Documentación del modelo de datos de las apps AppSheet (Google Sheets como persistencia). Corresponde al Google Sheet `OXYData`. Complementa a `OXY_AppSheet_Acciones_y_Bots` (acciones, bots, seguridad) y a `OXY_Propuesta_Dashboard_Indicadores` (indicadores).

## 1. Convenciones

- **Una pestaña = una tabla de AppSheet.** La fila 1 son los nombres de columna. Las columnas **virtuales** (marcadas *virtual*) no existen en el Sheet: AppSheet las calcula al vuelo.
- **App formula** = columna real cuyo valor se calcula al guardar y queda persistido (por ejemplo `Total_Gasto` o `Costo_Imputable` de un gasto). El **crédito fiscal** no es App formula: `Es_Credito_Fiscal` nace con un valor inicial y Gestión lo puede cambiar registro a registro.
- **Referencias indirectas:** si una tabla llega a otra a través de una tercera (p. ej. `Gastos_Obra` → `Tipos_Costo` → `Categorias_Costo`), la tabla superior define una columna **virtual de tipo Ref** cuya fórmula es un *dereference expression* (`Categoria_ID = [Tipo_Costo_ID].[Categoria_ID]`). Se nombra con la clave destino y no se aplica a las tablas `Snap_*` (planas por diseño). Listado en la sección 2.
- **Nada se borra:** gastos, abonos, facturas y avances se **anulan** (`Estado = Anulado` + motivo). Una proforma `Enviada` se anula; un `Borrador` no se anula: se **elimina** pasándolo a `Z-Eliminada` (queda registrado quién y cuándo, sin motivo).
- **Moneda única:** todo el modelo trabaja en soles peruanos (PEN, S/). No hay tipos de cambio ni columnas de moneda; los montos se registran y se suman directamente.
- **IGV:** los márgenes se miden sobre base neta; la cobranza sobre el total con IGV; el flujo de caja sobre lo pagado (gastos con `Fecha_Pago_Real`). Los costos se registran **sin IGV**; el IGV pasa a costo solo si ese registro no es crédito fiscal (decisión por registro, sin flag global). El costo se reconoce al registrar el gasto; la caja, al pagarlo.
- **Tipos de tabla:** Maestra / Catálogo · Configuración · Transaccional · Consolidación para KPIs · Log · Staging (integración).
- Los **nombres de campo** son los exactos del Sheet (sin tildes ni ñ). La pestaña `_Diccionario` de `OXYData` solo lista la estructura: Tabla, Columna, Tipo AppSheet, Clave, Requerido y Virtual. La configuración de cada columna en AppSheet (`Show?`, `Editable?`, valor inicial, `Valid if` y fórmulas) está en la especificación de cada app; este documento explica el propósito, las relaciones y el significado. (Mientras se termina de escribir las especificaciones de las apps, la pestaña `_Diccionario_Legado` conserva la configuración anterior solo para consulta; algunas descripciones de este documento todavía mencionan reglas de configuración y se limpiarán en la próxima pasada.)

## 2. Mapa de tablas

| Grupo | Tabla | Tipo | Apps |
|---|---|---|---|
| Maestras y catálogos | [`Areas_Compania`](#areas_compania) | Maestra | Gestión |
| Maestras y catálogos | [`Trabajadores`](#trabajadores) | Maestra / seguridad | Campo (lectura), Gestión |
| Maestras y catálogos | [`Tarifas_Trabajador`](#tarifas_trabajador) | Configuración (con historia) | Solo Gestión |
| Maestras y catálogos | [`Clientes`](#clientes) | Maestra | Gestión |
| Maestras y catálogos | [`Contactos_Cliente`](#contactos_cliente) | Maestra | Gestión |
| Maestras y catálogos | [`Proveedores`](#proveedores) | Maestra | Campo (alta), Gestión |
| Maestras y catálogos | [`Categorias_Costo`](#categorias_costo) | Catálogo | Todas (lectura) |
| Maestras y catálogos | [`Tipos_Costo`](#tipos_costo) | Catálogo (reglas de negocio) | Campo (solo los visibles), Gestión |
| Maestras y catálogos | [`Medios_Pago`](#medios_pago) | Catálogo | Gestión |
| Configuración | [`Configuracion`](#configuracion) | Configuración | Gestión |
| Configuración | [`Compania`](#compania) | Configuración (una sola fila) | Gestión (edita); Campo (solo lectura) |
| Comercial: proformas | [`Proformas`](#proformas) | Transaccional (ciclo de vida) | Gestión |
| Comercial: proformas | [`Proforma_Conceptos`](#proforma_conceptos) | Transaccional (detalle) | Gestión |
| Comercial: proformas | [`Proforma_Planificacion`](#proforma_planificacion) | Transaccional (detalle interno) | Gestión |
| Operación: obras | [`Obras`](#obras) | Transaccional (entidad central) | Campo (lectura), Gestión |
| Operación: obras | [`Asignaciones_Obra`](#asignaciones_obra) | Transaccional (relación) | Campo (lectura), Gestión |
| Operación: obras | [`Registro_Horas`](#registro_horas) | Transaccional | Campo (sin costos), Gestión |
| Operación: obras | [`Gastos_Obra`](#gastos_obra) | Transaccional | Campo (Material/Consumible), Gestión (todos) |
| Operación: obras | [`Avances_Obra`](#avances_obra) | Transaccional | Campo, Gestión |
| Facturación y cobranza | [`Facturas_Obra`](#facturas_obra) | Transaccional | Solo Gestión |
| Facturación y cobranza | [`Abonos_Obra`](#abonos_obra) | Transaccional | Solo Gestión |
| Log y control | [`Log_Eventos`](#log_eventos) | Log / auditoría | Gestión (lectura) |
| Log y control | [`Alertas`](#alertas) | KPIs / control | Gestión, Dashboard |
| Log y control | [`Metas_KPI`](#metas_kpi) | Configuración de KPIs | Gestión |
| Log y control | [`Jobs_Control`](#jobs_control) | Control técnico | Gestión, Dashboard |
| Consolidación para el dashboard | [`Snap_Obra_Dia`](#snap_obra_dia) | Consolidación para KPIs | Dashboard (lectura) |
| Consolidación para el dashboard | [`Snap_Costo_Tipo_Semana`](#snap_costo_tipo_semana) | Consolidación para KPIs | Dashboard (lectura) |
| Consolidación para el dashboard | [`Snap_Global_Hora`](#snap_global_hora) | Consolidación para KPIs | Dashboard (lectura) |
| Consolidación para el dashboard | [`Snap_Global_Dia`](#snap_global_dia) | Consolidación para KPIs | Dashboard (lectura) |

### Relaciones principales

```
Clientes ─< Contactos_Cliente
Clientes ─< Proformas ─< Proforma_Conceptos        (lo que se imprime)
                    └─< Proforma_Planificacion ─> Tipos_Costo ─> Categorias_Costo   (costo interno)
Proformas ─1:1─> Obras      (Proformas ─> Proformas: previa asignada a mano por el usuario, revisión / complementaria; Obras ─> Obras: obra principal)
Obras ─< Gastos_Obra ─> Tipos_Costo, Proveedores
Obras ─< Registro_Horas ─> Trabajadores ─< Tarifas_Trabajador
Obras ─< Asignaciones_Obra ─> Trabajadores
Obras ─< Avances_Obra
Obras ─< Facturas_Obra ─< Abonos_Obra ─> Medios_Pago   (Abonos_Obra también ─> Obras)
Obras, Gastos_Obra, Abonos_Obra, Facturas_Obra, ... ──bots──> Snap_*, Alertas, Log_Eventos
```

### Referencias indirectas (columnas virtuales Ref)

| Tabla | Columna virtual | Tipo | Fórmula |
|---|---|---|---|
| `Tarifas_Trabajador` | `Area_ID` | Ref -> Areas_Compania | `[Trabajador_ID].[Area_ID]` |
| `Proforma_Conceptos` | `Cliente_ID` | Ref -> Clientes | `[Proforma_ID].[Cliente_ID]` |
| `Proforma_Conceptos` | `Contacto_ID` | Ref -> Contactos_Cliente | `[Proforma_ID].[Contacto_ID]` |
| `Proforma_Planificacion` | `Cliente_ID` | Ref -> Clientes | `[Proforma_ID].[Cliente_ID]` |
| `Proforma_Planificacion` | `Contacto_ID` | Ref -> Contactos_Cliente | `[Proforma_ID].[Contacto_ID]` |
| `Proforma_Planificacion` | `Categoria_ID` | Ref -> Categorias_Costo | `[Tipo_Costo_ID].[Categoria_ID]` |
| `Obras` | `Contacto_ID` | Ref -> Contactos_Cliente | `[Proforma_ID].[Contacto_ID]` |
| `Obras` | `Area_ID` | Ref -> Areas_Compania | `[Responsable_ID].[Area_ID]` |
| `Gastos_Obra` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Gastos_Obra` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Gastos_Obra` | `Responsable_ID` | Ref -> Trabajadores | `[Obra_ID].[Responsable_ID]` |
| `Gastos_Obra` | `Categoria_ID` | Ref -> Categorias_Costo | `[Tipo_Costo_ID].[Categoria_ID]` |
| `Abonos_Obra` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Abonos_Obra` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Abonos_Obra` | `Responsable_ID` | Ref -> Trabajadores | `[Obra_ID].[Responsable_ID]` |
| `Facturas_Obra` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Facturas_Obra` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Facturas_Obra` | `Responsable_ID` | Ref -> Trabajadores | `[Obra_ID].[Responsable_ID]` |
| `Avances_Obra` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Avances_Obra` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Avances_Obra` | `Responsable_ID` | Ref -> Trabajadores | `[Obra_ID].[Responsable_ID]` |
| `Asignaciones_Obra` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Asignaciones_Obra` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Asignaciones_Obra` | `Area_ID` | Ref -> Areas_Compania | `[Trabajador_ID].[Area_ID]` |
| `Registro_Horas` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Registro_Horas` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Registro_Horas` | `Area_ID` | Ref -> Areas_Compania | `[Trabajador_ID].[Area_ID]` |
| `Alertas` | `Proforma_ID` | Ref -> Proformas | `[Obra_ID].[Proforma_ID]` |
| `Alertas` | `Cliente_ID` | Ref -> Clientes | `[Obra_ID].[Cliente_ID]` |
| `Alertas` | `Responsable_ID` | Ref -> Trabajadores | `[Obra_ID].[Responsable_ID]` |

### Procesos de negocio y tablas que tocan

| Proceso | Tablas |
|---|---|
| Ciclo de vida de proformas | Proformas, Proforma_Conceptos, Proforma_Planificacion, Clientes, Contactos_Cliente, Configuracion, Compania |
| Gestión de obra | Obras, Asignaciones_Obra, Trabajadores, Avances_Obra |
| Control de costos | Gastos_Obra, Registro_Horas, Tarifas_Trabajador, Tipos_Costo, Categorias_Costo, Proveedores |
| Facturación y cobranza | Facturas_Obra, Abonos_Obra, Medios_Pago, Clientes, Compania |
| Notificaciones y auditoría | Log_Eventos, Alertas, Jobs_Control |
| Dashboard e indicadores | Snap_Obra_Dia, Snap_Costo_Tipo_Semana, Snap_Global_Hora, Snap_Global_Dia, Metas_KPI, Alertas |

## 3. Maestras y catálogos

### Areas_Compania

- **Tipo:** Maestra
- **Por qué existe:** Áreas de la empresa (Operaciones, Administración, etc.) para clasificar al personal.
- **Relaciones:** Trabajadores (1:N)
- **Procesos:** Administración de usuarios
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Area_ID` | Texto · **clave** | Si | Identificador único del área. |
| `Nombre` | Texto · etiqueta | Si | Nombre visible del registro. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

### Trabajadores

- **Tipo:** Maestra / seguridad
- **Por qué existe:** Personas con acceso a las apps. El `Email` + `Rol` determina qué ve y qué puede hacer cada usuario (`USEREMAIL()`). También es la lista de quienes pueden ser responsables, asignados u horas.
- **Relaciones:** Areas_Compania (N:1); Tarifas_Trabajador, Asignaciones_Obra, Registro_Horas (1:N); Obras.Responsable_ID
- **Procesos:** Seguridad y roles; asignación y horas; responsable de obra
- **Apps:** Campo (lectura), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Trabajador_ID` | Texto · **clave** | Si | Identificador único del trabajador. |
| `Nombres` | Text | Si | Nombres. |
| `Apellidos` | Text | Si | Apellidos. |
| `Email` | Email | Si | Correo (cuenta Google) del usuario. Debe coincidir con la cuenta Google; se usa con USEREMAIL() para identificar al usuario y su rol |
| `Rol` | Enum | Si | Rol de seguridad: Admin, Gerencia o Campo. Valores: Admin, Gerencia, Campo. Controla vistas y acciones (Show_If / Only if) |
| `Area_ID` | Ref -> Areas_Compania | No | Identificador único del área. |
| `Telefono` | Phone | No | Teléfono de contacto. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

### Tarifas_Trabajador

- **Tipo:** Configuración (con historia)
- **Por qué existe:** Tarifa por hora (normal y extra) de cada trabajador con vigencia. Permite costear la mano de obra propia sin exponer tarifas a Campo.
- **Relaciones:** Trabajadores (N:1)
- **Procesos:** Aprobación de horas (se copia la tarifa vigente a `Registro_Horas`)
- **Apps:** Solo Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Tarifa_ID` | Texto · **clave** | Si | Identificador de la tarifa. SOLO en la app de Gestion |
| `Trabajador_ID` | Ref -> Trabajadores | Si | Identificador único del trabajador. |
| `Tarifa_Hora` | Decimal | Si | Costo por hora normal. |
| `Tarifa_Hora_Extra` | Decimal | No | Costo por hora extra. |
| `Vigente_Desde` | Date | Si | Inicio de vigencia. |
| `Vigente_Hasta` | Date | No | Fin de vigencia; vacío = vigente. Vacio = vigente |
| `Area_ID` | Ref -> Areas_Compania · *virtual* | - | Fórmula: `[Trabajador_ID].[Area_ID]`. Referencia indirecta: Area_ID de Trabajadores (via Trabajador_ID). Dereference expression |

### Clientes

- **Tipo:** Maestra
- **Por qué existe:** Clientes de OXY (RUC, razón social) y su plazo de crédito por defecto para calcular vencimientos de facturas.
- **Relaciones:** Contactos_Cliente, Proformas, Obras, Facturas_Obra (vía Obra) 
- **Procesos:** Proformas; facturación y cobranza
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Cliente_ID` | Texto · **clave** | Si | Identificador del cliente (referencia). |
| `RUC` | Text | Si | RUC (11 dígitos). 11 digitos; Valid_If con LEN()=11 |
| `Razon_Social` | Texto · etiqueta | Si | Razón social. |
| `Nombre_Corto` | Text | No | Nombre corto o alias del cliente para listas, búsquedas y etiquetas compactas. |
| `Direccion` | Address | No | Dirección fiscal. |
| `Plazo_Pago_Dias` | Number | Si | Días de crédito para calcular el vencimiento. Dias de credito para calcular el vencimiento de sus facturas |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

### Contactos_Cliente

- **Tipo:** Maestra
- **Por qué existe:** Personas de contacto de cada cliente; la proforma se dirige a uno de ellos.
- **Relaciones:** Clientes (N:1); Proformas.Contacto_ID
- **Procesos:** Proformas
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Contacto_ID` | Texto · **clave** | Si | Identificador del contacto. |
| `Cliente_ID` | Ref -> Clientes | Si | Identificador del cliente (referencia). Marcar 'Is a part of' para verlos dentro del cliente |
| `Nombre` | Texto · etiqueta | Si | Nombre visible del registro. |
| `Cargo` | Text | No | Cargo del contacto. |
| `Telefono` | Phone | No | Teléfono de contacto. |
| `Email` | Email | No | Correo (cuenta Google) del usuario. |

### Proveedores

- **Tipo:** Maestra
- **Por qué existe:** Proveedores de los gastos (RUC, razón social). Se permite alta rápida desde el formulario de gasto.
- **Relaciones:** Gastos_Obra (1:N)
- **Procesos:** Registro de gastos
- **Apps:** Campo (alta), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Proveedor_ID` | Texto · **clave** | Si | Identificador del proveedor. Alta rapida desde el formulario de gasto (RUC + razon social) |
| `RUC` | Text | No | RUC (11 dígitos). Unico (Valid_If para evitar duplicados) |
| `Razon_Social` | Texto · etiqueta | Si | Razón social. |
| `Telefono` | Phone | No | Teléfono de contacto. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |
| `Creado_Por` | Email | Si | Usuario que creó el registro. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |

### Categorias_Costo

- **Tipo:** Catálogo
- **Por qué existe:** Las 4 categorías de costo con las que se compara presupuesto vs. real: Mano de obra, Materiales y consumibles, Equipos y herramientas, Viáticos y transporte.
- **Relaciones:** Tipos_Costo, Snap_Costo_Tipo_Semana
- **Procesos:** Planificación de costos; indicadores por categoría
- **Apps:** Todas (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Categoria_ID` | Texto · **clave** | Si | Categoría de costo (MO, MAT, EQP, VIA). MO, MAT, EQP, VIA |
| `Nombre` | Texto · etiqueta | Si | Nombre visible del registro. |
| `Orden` | Number | No | Orden de presentación. Orden de presentacion |

### Tipos_Costo

- **Tipo:** Catálogo (reglas de negocio)
- **Por qué existe:** Tipos concretos de costo bajo cada categoría (material, consumible, subcontrato, herramienta alquilada/propia, transporte, viáticos, mano de obra propia). Define quién lo registra (`Visible_Campo`), de dónde viene el monto (`Origen_Costo`), si aplica IGV por defecto y si la mano de obra es interna o tercerizada.
- **Relaciones:** Categorias_Costo (N:1); Proforma_Planificacion, Gastos_Obra, Snap_Costo_Tipo_Semana
- **Procesos:** Planificación; registro de gastos; consolidación por tipo
- **Apps:** Campo (solo los visibles), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Tipo_Costo_ID` | Texto · **clave** | Si | Tipo de costo. Codigo corto en minusculas |
| `Nombre` | Texto · etiqueta | Si | Nombre visible del registro. |
| `Categoria_ID` | Ref -> Categorias_Costo | Si | Categoría de costo (MO, MAT, EQP, VIA). Las 4 categorias de comparacion presupuesto vs real |
| `Origen_Costo` | Enum | Si | De dónde viene el monto: Calculado, Interno manual o Externo. Valores: Calculado, Interno manual, Externo. Calculado = viene de otra tabla (horas); Interno manual = lo digita Gestion (depreciacion); Externo = con comprobante de un tercero |
| `Modalidad_MO` | Enum | Si | Mano de obra Interna o Tercerizada; "No aplica" en otras categorías. Valores: Interno, Tercerizado, No aplica. Solo para Mano de obra: Interno o Tercerizado |
| `Aplica_IGV_Defecto` | Enum | Si | Valor por defecto de Tiene_IGV en la planificación. Valores: Si, No. Valor por defecto de Tiene_IGV en las lineas de planificacion (Si = la linea lleva IGV) |
| `Credito_Fiscal_Defecto` | Enum | Si | Valores: Si, No. Valor por defecto de Es_Credito_Fiscal en las lineas de planificacion. Si = se espera factura que da credito; No = proveedor informal o sin factura (el IGV seria costo). Editable por linea |
| `Visible_Campo` | Enum | Si | Si el tipo aparece en la app de Campo. Valores: Si, No. No = el tipo no aparece en OXY Campo (solo Gestion) |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

### Medios_Pago

- **Tipo:** Catálogo
- **Por qué existe:** Medios con los que el cliente paga (transferencia, cheque, efectivo…).
- **Relaciones:** Abonos_Obra (1:N)
- **Procesos:** Cobranza
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Medio_Pago_ID` | Texto · **clave** | Si | Medio de pago. |
| `Nombre` | Texto · etiqueta | Si | Nombre visible del registro. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

## 4. Configuración

### Configuracion

- **Tipo:** Configuración
- **Por qué existe:** Parámetros **numéricos** editables sin tocar las apps: IGV, tolerancia de cobranza, vigencia de proformas, plazo de pago por defecto, margen mínimo, días de recordatorio y de alerta sin gastos.
- **Relaciones:** Consultada por fórmulas de casi todas las tablas
- **Procesos:** Todos
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Clave` | Texto · **clave** | Si | Nombre del parámetro. |
| `Valor` | Decimal | Si | Valor numérico del parámetro. Se lee con DECIMAL() si es decimal (p. ej. IGV_PCT, MARGEN_MINIMO_PCT, TOLERANCIA_COBRANZA) y con NUMBER() si es entero, p. ej. días (NUMBER() trunca 0.18 a 0). **Solo admite números:** los datos de texto de OXY van en `Compania`. |
| `Descripcion` | Text | No | Descripción. |

### Compania

- **Tipo:** Configuración (una sola fila)
- **Por qué existe:** Datos de OXY como empresa y textos fijos de la proforma impresa, más los destinatarios del aviso de cobranza completa. Es una tabla de columnas con nombre y tipo propios (no pares clave-valor), porque `Configuracion.Valor` es numérico. La fila se crea en el Sheet con `Compania_ID` = `OXY`; la app solo la actualiza (sin altas ni bajas), para que nadie la borre ni la duplique.
- **Relaciones:** Ninguna por referencia. La leen por `LOOKUP("OXY","Compania","Compania_ID",...)` las diez columnas virtuales de `Proformas` para el PDF y el bot LOG-B01 para el aviso de cobranza.
- **Procesos:** Ciclo de vida de proformas (PDF); cobranza (aviso)
- **Apps:** Gestión (edita); Campo (solo lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Compania_ID` | Texto · **clave** | Si | Valor fijo `OXY`. No editable. |
| `Nombre_Comercial` | Texto · etiqueta | Si | Nombre comercial de OXY; encabezado de la proforma. |
| `Razon_Social` | Text | Si | Razón social de OXY; pie legal de la proforma. |
| `RUC` | Text | Si | RUC de OXY. Valid_If: 11 dígitos. Texto para no perder ceros. |
| `Direccion_Fiscal` | Text | Si | Dirección fiscal de OXY. |
| `Telefono` | Phone | Si | Teléfono de contacto de OXY. |
| `Email` | Email | Si | Correo de contacto de OXY. |
| `Web` | Url | No | Sitio web de OXY; se imprime solo si tiene valor. |
| `Condiciones_Proforma` | LongText | Si | Condiciones comerciales (forma de pago, plazo de entrega, garantía); se imprimen al final de la proforma. |
| `Cuentas_Bancarias` | LongText | Si | Cuentas bancarias donde el cliente debe pagar. |
| `Firma_Nombre` | Text | Si | Nombre y cargo de quien respalda la proforma. |
| `Emails_Cobranza` | Text | No | Correos que reciben el aviso de cobranza completa, separados por coma. Vacío = no se envía ese aviso. |

Editan solo Admin y Gerencia (`Editable?` por rol, ayuda de pantalla, no seguridad). Cualquier usuario de Campo que tenga la tabla en su app recibe también las cuentas bancarias, las condiciones y los correos de `Emails_Cobranza`; ver la sección 14.4 del instructivo.

## 5. Comercial: proformas

### Proformas

- **Tipo:** Transaccional (ciclo de vida)
- **Por qué existe:** Cabecera de la cotización al cliente. Una proforma aceptada genera una obra. Maneja estados (Borrador → Enviada → Aceptada/Rechazada/Vencida/Anulada; un Borrador también puede pasar a Z-Eliminada, nunca a Anulada). Una proforma puede apuntar a otra como previa (revisión o complementaria), relación que el usuario asigna a mano; el sistema no copia datos ni cambia el estado de la previa. Los precios y márgenes se calculan de sus tablas hijas.
- **Relaciones:** Clientes, Contactos_Cliente (N:1); Proforma_Conceptos y Proforma_Planificacion (1:N, "is a part of"); Proformas (autorreferencia, previa); Obras (1:1)
- **Procesos:** Ciclo de vida de proformas; creación de obra
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Proforma_ID` | Texto · **clave** | Si | Identificador de la proforma. |
| `Numero` | Texto · etiqueta | Si | Número visible de la proforma, ej. 014-2026. Lo digita el usuario al crear la proforma desde cero (el sistema no lo genera); no puede repetirse entre proformas no eliminadas ni llevar caracteres inválidos en nombres de archivo (`/ : * ? < > |`; el PDF se nombra con él). Es el numero que el personal memoriza |
| `Nombre` | Text | Si | Nombre del trabajo o de su ubicacion. Ej. Huanta |
| `Cliente_ID` | Ref -> Clientes | Si | Identificador del cliente (referencia). |
| `Contacto_ID` | Ref -> Contactos_Cliente | Si | Identificador del contacto. Valid_If: contactos del cliente elegido |
| `Direccion_Servicio` | Address | Si | Dirección donde se ejecuta el servicio. |
| `Fecha_Emision` | Date | Si | Fecha de emisión. |
| `Estado` | Enum | Si | Estado del registro. Valores: Borrador, Enviada, Aceptada, Rechazada, Vencida, Anulada, Z-Eliminada. Editable_If = FALSE; solo cambia con acciones. Borrador solo pasa a Enviada o Z-Eliminada; Anulada solo desde Enviada; Z-Eliminada es final y no se muestra en las vistas normales |
| `Fecha_Envio` | Date | Condicional | Fecha en que se envió al cliente. Accion Enviar |
| `Fecha_Vigencia` | Date | Si | Fecha límite de validez. Valor inicial: hoy + `VIGENCIA_PROFORMA_DIAS` de Configuracion. El usuario la ajusta en Borrador antes de enviar; `A_Enviar` no la fija. Valid_If: no anterior a Fecha_Emision. Editable solo en Borrador. El PDF siempre la toma de aquí |
| `Doc_Proforma` | File | No | PDF de la proforma, generado por el bot `B_Proforma_PDF` desde la plantilla de Google Docs cuando se ejecuta `A_Generar_PDF` (en Borrador o Enviada, las veces que haga falta). Mientras se genera guarda la señal `PENDIENTE\|yyyyMMddHHmmss`; luego la ruta `Proformas_Files/<Numero>_<Sello>.pdf`. Cada generación crea un archivo nuevo. Desde Aceptada ya no se regenera. `A_Enviar` exige que exista. Solo se archiva: **no se envía por correo** al cliente. No editable; visible solo si no está vacío |
| `Fecha_Aceptacion` | Date | Condicional | Fecha de aceptación. |
| `Doc_Aceptacion` | File | Condicional | Archivo adjunto de la aceptación. Archivo de aceptacion (orden de compra, correo o carta en PDF o imagen); requerido al aceptar |
| `Motivo_Rechazo` | Text | Condicional | Motivo del rechazo. Valid_If: `ISBLANK([Motivo_Anulacion])` (exclusivo con el motivo de anulación). |
| `Fecha_Rechazo` | Date | Condicional | Fecha del rechazo. La fija la acción `A_Rechazar` con `TODAY()`; nadie la edita. La hora exacta queda en `Log_Eventos`. |
| `Motivo_Anulacion` | Text | Condicional | Motivo de anulación (obligatorio al anular). Solo se anula una proforma Enviada. Valid_If: `ISBLANK([Motivo_Rechazo])` (exclusivo con el motivo de rechazo). |
| `Fecha_Anulacion` | Date | Condicional | Fecha de la anulación. La fija la acción `A_Anular` con `TODAY()`; nadie la edita. La hora exacta queda en `Log_Eventos`. |
| `Eliminada_Por` | Email | Condicional | Usuario que eliminó el borrador. Lo fija la acción `A_Eliminar` con `USEREMAIL()`; nadie la edita. |
| `Fecha_Eliminacion` | Date | Condicional | Fecha en que se eliminó el borrador. La fija la acción `A_Eliminar` con `TODAY()`; nadie la edita. La hora exacta queda en `Log_Eventos` (`PROFORMA_ELIMINADA`). No se pide motivo. |
| `Proforma_Previa_ID` | Ref -> Proformas | No | Proforma relacionada (autorreferencia), asignada a mano por el usuario mientras la proforma es Borrador. La lista excluye la propia proforma y las Z-Eliminada; el sistema no valida nada más. Si se llena, Tipo_Relacion es requerido |
| `Tipo_Relacion` | Enum | Condicional | Revisión o Complementaria. Valores: Revision, Complementaria. Required_If: Proforma_Previa_ID no vacía. Solo Complementaria tiene efecto: al aceptar, la obra nueva se liga a la obra de la previa (Obra_Principal_ID). Revision es informativa |
| `Creado_Por` | Email | Si | Usuario que creó el registro. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Doc_Proforma_Personalizado` | File | No | Versión propia de la proforma que sube el usuario (opcional). Editable en Borrador y Enviada: se puede volver a subir mientras está Enviada; desde Aceptada queda bloqueada (bloqueo de pantalla, no de seguridad). Visible si tiene valor o la proforma está en Borrador o Enviada. Si existe, es el documento oficial |
| `Etiqueta` | Text · *virtual* | - | Etiqueta legible de la proforma: Numero y Nombre (p. ej. 014-2026 - Huanta) |
| `Precio_Neto` | Price · *virtual* | - | Suma de conceptos sin IGV. Subtotal sin IGV (lo que se imprime) |
| `IGV_Monto` | Price · *virtual* | - | IGV calculado. Se imprime |
| `Total_Cobrar` | Price · *virtual* | - | Subtotal + IGV. Total de la proforma |
| `Costo_Planificado` | Price · *virtual* | - | Presupuesto de costo neto. Presupuesto de costo imputable de las lineas de planificacion (sin IGV si hay credito; con IGV si no) |
| `Margen_Plan` | Price · *virtual* | - | Precio neto − costo planificado. |
| `Margen_Plan_Pct` | Percent · *virtual* | - | Margen planificado sobre el precio neto. |
| `Aviso_Margen` | Yes/No · *virtual* | - | TRUE si el margen está bajo el mínimo configurado. Advertencia al enviar |
| `Obra_Generada` | Ref -> Obras · *virtual* | - | Obra creada desde esta proforma. Oculta 'Crear obra' si ya existe |
| `Total_Relacionadas` | Number · *virtual* | - | Cuántas proformas no eliminadas tienen a esta como `Proforma_Previa_ID`: `COUNT(SELECT(Proformas[Proforma_ID],AND([Proforma_Previa_ID]=[_THISROW],[Estado]<>"Z-Eliminada")))`. Relacionadas directas, sin recorrer cadenas |
| `Empresa_Nombre_Comercial` | Text · *virtual* | - | Nombre comercial de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Nombre_Comercial")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_Razon_Social` | Text · *virtual* | - | Razón social de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Razon_Social")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_RUC` | Text · *virtual* | - | RUC de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","RUC")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_Direccion_Fiscal` | Text · *virtual* | - | Dirección fiscal de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Direccion_Fiscal")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_Telefono` | Text · *virtual* | - | Teléfono de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Telefono")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_Email` | Text · *virtual* | - | Correo de OXY. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Email")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Empresa_Web` | Text · *virtual* | - | Sitio web de OXY (puede estar vacío). Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Web")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Proforma_Condiciones` | LongText · *virtual* | - | Condiciones comerciales. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Condiciones_Proforma")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Proforma_Cuentas_Bancarias` | LongText · *virtual* | - | Cuentas bancarias de pago. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Cuentas_Bancarias")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Proforma_Firma_Nombre` | Text · *virtual* | - | Nombre y cargo de quien respalda la proforma. Fórmula: `LOOKUP("OXY","Compania","Compania_ID","Firma_Nombre")`. Dato para la plantilla del PDF; refleja siempre lo vigente en Compania |
| `Doc_Oficial` | File · *virtual* | - | Documento oficial de la proforma. Fórmula: `IF(ISNOTBLANK([Doc_Proforma_Personalizado]),[Doc_Proforma_Personalizado],[Doc_Proforma])` |

### Proforma_Conceptos

- **Tipo:** Transaccional (detalle)
- **Por qué existe:** Líneas que se **imprimen** en la proforma: concepto y monto sin IGV. La proforma muestra subtotal, IGV y total. No contiene costos internos. Se pueden agregar y editar en Borrador y Enviada; borrar solo en Borrador; desde Aceptada quedan bloqueadas.
- **Relaciones:** Proformas (N:1)
- **Procesos:** Emisión de proforma
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Concepto_ID` | Texto · **clave** | Si | Identificador del concepto. Lineas que se IMPRIMEN en la proforma |
| `Proforma_ID` | Ref -> Proformas | Si | Identificador de la proforma. Is a part of |
| `Orden` | Number | Si | Orden de presentación. |
| `Concepto` | Text | Si | Texto que se imprime. |
| `Monto_Sin_IGV` | Price | Si | Valor del concepto sin IGV. Valor sin IGV; la proforma imprime subtotal, IGV y total |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Proforma_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Proformas (via Proforma_ID). Dereference expression |
| `Contacto_ID` | Ref -> Contactos_Cliente · *virtual* | - | Fórmula: `[Proforma_ID].[Contacto_ID]`. Referencia indirecta: Contacto_ID de Proformas (via Proforma_ID). Dereference expression |

### Proforma_Planificacion

- **Tipo:** Transaccional (detalle interno)
- **Por qué existe:** Presupuesto de **costo** interno por tipo de costo (no se imprime). Se puede agregar y editar en Borrador y Enviada (borrar solo en Borrador); se congela al aceptar y es la base de comparación del costo real, del valor ganado y del margen.
- **Relaciones:** Proformas (N:1), Tipos_Costo (N:1)
- **Procesos:** Planificación de costos; control presupuesto vs. real
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Planif_ID` | Texto · **clave** | Si | Identificador de la línea de planificación. Presupuesto de COSTO interno (no se imprime). Se congela al aceptar |
| `Proforma_ID` | Ref -> Proformas | Si | Identificador de la proforma. Is a part of |
| `Tipo_Costo_ID` | Ref -> Tipos_Costo | Si | Tipo de costo. Define categoria y modalidad |
| `Descripcion` | Text | Si | Descripción. |
| `Cantidad` | Decimal | Si | Cantidad (horas en mano de obra propia). Mano de obra propia: horas |
| `Unidad` | Text | No | Unidad de medida. |
| `Costo_Unitario` | Decimal | Si | Costo unitario. SIEMPRE sin IGV (si la cotizacion trae IGV, dividir entre 1.18 antes de digitar); mano de obra propia: tarifa por hora |
| `Tiene_IGV` | Enum | Si | Valores: Si, No. Si el proveedor cargara IGV. Valor por defecto desde Tipos_Costo |
| `Es_Credito_Fiscal` | Enum | Si | Valores: Si, No. Valor inicial desde Tipos_Costo; editable por linea. Valid_If: Si solo cuando Tiene_IGV=Si. Con credito el IGV no es costo; sin credito se suma al costo |
| `Monto_Base` | Price · *virtual* | - | Costo SIN IGV de la linea (equivale a Monto_Base del gasto) |
| `Monto_IGV` | Price · *virtual* | - | IGV estimado de la linea (equivale a Monto_IGV del gasto) |
| `Costo_Total` | Price · *virtual* | - | Base + IGV (equivale a Total_Gasto del gasto) |
| `Costo_Imputable` | Price · *virtual* | - | Lo que cuenta contra el margen planificado: base si hay credito; base + IGV si no (misma regla que Gastos_Obra.Costo_Imputable) |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Proforma_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Proformas (via Proforma_ID). Dereference expression |
| `Contacto_ID` | Ref -> Contactos_Cliente · *virtual* | - | Fórmula: `[Proforma_ID].[Contacto_ID]`. Referencia indirecta: Contacto_ID de Proformas (via Proforma_ID). Dereference expression |
| `Categoria_ID` | Ref -> Categorias_Costo · *virtual* | - | Fórmula: `[Tipo_Costo_ID].[Categoria_ID]`. Referencia indirecta: Categoria_ID de Tipos_Costo (via Tipo_Costo_ID). Dereference expression |

## 6. Operación: obras

### Obras

- **Tipo:** Transaccional (entidad central)
- **Por qué existe:** La obra en ejecución nacida de una proforma aceptada. Congela precio y presupuesto de costo, y concentra (como columnas virtuales) costos, cobranza, facturación, avance y KPIs de control. Es el eje de casi todas las demás tablas.
- **Relaciones:** Proformas (1:1), Clientes, Trabajadores (responsable), Obras (principal/complementarias); Gastos_Obra, Registro_Horas, Abonos_Obra, Facturas_Obra, Avances_Obra, Asignaciones_Obra, Snap_*, Alertas (1:N)
- **Procesos:** Gestión de obra; costos; cobranza; avance; indicadores
- **Apps:** Campo (lectura), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Obra_ID` | Texto · **clave** | Si | Identificador de la obra. |
| `Codigo` | Texto · etiqueta | Si | Código visible (proforma + ubicación). Numero de proforma + ubicacion |
| `Proforma_ID` | Ref -> Proformas | Si | Identificador de la proforma. 1 proforma = 1 obra; Valid_If para no repetir |
| `Obra_Principal_ID` | Ref -> Obras | No | Obra principal cuando proviene de una proforma complementaria. Solo si proviene de proforma Complementaria |
| `Cliente_ID` | Ref -> Clientes | Si | Identificador del cliente (referencia). Heredado de la proforma |
| `Responsable_ID` | Ref -> Trabajadores | No | Responsable de la obra. Queda en blanco al crear la obra (`A_Aceptar_CrearObra`); se asigna en OXY Gestión. |
| `Estado` | Enum | Si | Estado del registro. Valores: Por iniciar, En ejecucion, Pausada, Terminada, Cerrada, Cancelada. Editable_If = FALSE; cambia por acciones |
| `Fecha_Inicio` | Date | No | Fecha de inicio. Se llena al pasar a En ejecucion |
| `Fecha_Fin_Estimada` | Date | No | Fecha estimada de término. |
| `Fecha_Fin_Real` | Date | No | Fecha real de término. Se llena al pasar a Terminada |
| `Fecha_Cierre` | Date | No | Fecha de cierre administrativo. Accion Cerrar obra |
| `Motivo_Cierre_Con_Saldo` | Text | No | Motivo si se cierra con saldo pendiente. Solo Gerencia |
| `Motivo_Cancelacion` | Text | No | Motivo de cancelación. |
| `Precio_Neto_Base` | Price | Si | Precio sin IGV, congelado al crear la obra. Precio SIN IGV, copia congelada al crear la obra. COLUMNA REAL |
| `IGV_Base` | Price | Si | IGV congelado. IGV de la proforma congelado |
| `Total_Cobrar_Base` | Price | Si | Total a cobrar (con IGV); base de la cobranza. Precio_Neto + IGV: lo que paga el cliente. Base de la cobranza. COLUMNA REAL |
| `Costo_Planificado_Base` | Price | Si | Presupuesto de costo congelado. Suma de Costo_Imputable de la planificacion, congelada. COLUMNA REAL |
| `Fecha_Cobranza_Completa` | Date | No | Fecha en que se completó la cobranza. La llena el job de cobranza |
| `Notificado_Cobro_Completo` | Enum | Si | Evita notificar dos veces. Valores: Si, No. Idempotencia del job |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Total_Gastos` | Price · *virtual* | - | Gastos vigentes en soles. Costo imputable de gastos |
| `Total_Personal` | Price · *virtual* | - | Costo de horas aprobadas. Mano de obra propia |
| `Costo_Real` | Price · *virtual* | - | Gastos + personal. |
| `Consumo_Pct` | Percent · *virtual* | - | Costo real / costo planificado. % del presupuesto de costo consumido |
| `Margen_Real_Parcial` | Price · *virtual* | - | Precio neto − costo real a la fecha. Margen con el costo acumulado a la fecha |
| `IGV_No_Recuperable` | Price · *virtual* | - | IGV que pasó a costo. IGV que pasa a costo (boletas, sin credito) |
| `Total_Abonos` | Price · *virtual* | - | Abonos vigentes en soles. |
| `Saldo` | Price · *virtual* | - | Total a cobrar − abonos. |
| `Estado_Cobranza` | Enum · *virtual* | - | Sin abonos / Parcial / Cobrada / Sobrepagada. Cobrada y Sobrepagada notifican igual |
| `Cobranza_Completa` | Yes/No · *virtual* | - | TRUE si el saldo está dentro de la tolerancia. Condicion de los bots |
| `Flujo_Caja` | Price · *virtual* | - | Abonos menos gastos YA PAGADOS (con Fecha_Pago_Real) menos personal |
| `Por_Pagar` | Price · *virtual* | - | Gastos vigentes sin Fecha_Pago_Real (base + IGV). Informativo; no hay vista de cuentas por pagar |
| `Flujo_Caja_Proyectado` | Price · *virtual* | - | Flujo de caja si se pagaran hoy todos los gastos pendientes (los pendientes se ubican por Fecha_Pago_Estimada) |
| `Avance_Actual` | Number · *virtual* | - | Último avance acumulado. Ultimo avance acumulado (0 si no hay) |
| `Valor_Ganado` | Price · *virtual* | - | Costo planificado × avance. Presupuesto de COSTO x avance |
| `CPI` | Decimal · *virtual* | - | Índice de desempeño de costo (>1 bien, <1 sobrecosto). Indice de desempeno de costo: >1 va bien, <1 sobrecosto |
| `Proyeccion_Costo_Final` | Price · *virtual* | - | Costo estimado al terminar. Costo estimado al terminar |
| `Margen_Proyectado` | Price · *virtual* | - | Margen estimado al terminar. Margen estimado al terminar |
| `Facturado_Acum` | Price · *virtual* | - | Total de facturas de venta vigentes. Facturas de venta vigentes |
| `Por_Facturar` | Price · *virtual* | - | Total a cobrar − facturado. |
| `Pct_Facturado` | Percent · *virtual* | - | Facturado / total a cobrar. |
| `Facturado_Sin_Cobrar` | Price · *virtual* | - | Facturado − abonos. |
| `Cartera_Vencida` | Price · *virtual* | - | Cartera vencida en soles. Saldo de facturas vencidas |
| `Rezago_Facturacion_pp` | Number · *virtual* | - | Avance % − facturado % (puntos). Avance fisico menos % facturado: positivo = falta facturar |
| `Dias_Sin_Gastos` | Number · *virtual* | - | Días desde el último gasto/horas; alerta > 7. Dias desde el ultimo gasto u hora; alerta si > 7. Validar con listas vacias |
| `Contacto_ID` | Ref -> Contactos_Cliente · *virtual* | - | Fórmula: `[Proforma_ID].[Contacto_ID]`. Referencia indirecta: Contacto_ID de Proformas (via Proforma_ID). Dereference expression |
| `Area_ID` | Ref -> Areas_Compania · *virtual* | - | Fórmula: `[Responsable_ID].[Area_ID]`. Referencia indirecta: Area_ID de Trabajadores (via Responsable_ID). Dereference expression |

### Asignaciones_Obra

- **Tipo:** Transaccional (relación)
- **Por qué existe:** Qué trabajadores están asignados a qué obra y con qué rol; limita quién puede registrar horas y ver la obra.
- **Relaciones:** Obras, Trabajadores (N:1)
- **Procesos:** Asignación de personal; seguridad por obra
- **Apps:** Campo (lectura), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Asignacion_ID` | Texto · **clave** | Si | Identificador de la asignación. |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. |
| `Trabajador_ID` | Ref -> Trabajadores | Si | Identificador único del trabajador. |
| `Rol_En_Obra` | Text | No | Rol del trabajador en la obra. Ej. Soldador, Supervisor |
| `Fecha_Inicio` | Date | Si | Fecha de inicio. |
| `Fecha_Fin` | Date | No | Fin de la asignación. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Area_ID` | Ref -> Areas_Compania · *virtual* | - | Fórmula: `[Trabajador_ID].[Area_ID]`. Referencia indirecta: Area_ID de Trabajadores (via Trabajador_ID). Dereference expression |

### Registro_Horas

- **Tipo:** Transaccional
- **Por qué existe:** Horas del personal propio por obra y día. Campo las registra; Gestión las aprueba y fija la tarifa, con lo que se calcula el costo de mano de obra propia (sin IGV).
- **Relaciones:** Obras, Trabajadores (N:1); Tarifas_Trabajador (origen de tarifa)
- **Procesos:** Registro y aprobación de horas; costo de personal
- **Apps:** Campo (sin costos), Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Horas_ID` | Texto · **clave** | Si | Identificador del registro. |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. |
| `Trabajador_ID` | Ref -> Trabajadores | Si | Identificador único del trabajador. Valid_If: asignados a la obra |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Horas` | Decimal | Si | Horas normales. |
| `Horas_Extra` | Decimal | No | Horas extra. |
| `Descripcion` | Text | No | Descripción. |
| `Estado` | Enum | Si | Estado del registro. Valores: Pendiente, Aprobado, Rechazado |
| `Aprobado_Por` | Email | No | Usuario de Gestión que aprobó. |
| `Costo_Hora` | Decimal | No | Tarifa aplicada. Campo NO ve estas columnas de costo |
| `Costo_Hora_Extra` | Decimal | No | Tarifa extra aplicada. |
| `Costo_Total` | Price | No | Horas*Costo_Hora + Horas_Extra*Costo_Hora_Extra |
| `Registrado_Por` | Email | Si | Usuario que registró. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Area_ID` | Ref -> Areas_Compania · *virtual* | - | Fórmula: `[Trabajador_ID].[Area_ID]`. Referencia indirecta: Area_ID de Trabajadores (via Trabajador_ID). Dereference expression |

### Gastos_Obra

- **Tipo:** Transaccional
- **Por qué existe:** Cada gasto o costo imputado a una obra (material, consumible, subcontrato, alquiler, transporte, viáticos, depreciación). Guarda base, IGV, total del gasto, crédito fiscal (por registro), costo imputable y las fechas de pago estimada y real. No se borra: se anula.
- **Relaciones:** Obras, Tipos_Costo, Proveedores (N:1); Log_Eventos (genera eventos)
- **Procesos:** Registro de gastos; control de costos; flujo de caja
- **Apps:** Campo (Material/Consumible), Gestión (todos)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Gasto_ID` | Texto · **clave** | Si | Identificador del gasto. |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. Valid_If: obras abiertas |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Tipo_Costo_ID` | Ref -> Tipos_Costo | Si | Tipo de costo. Valid_If: Origen_Costo<>Calculado; en Campo solo Visible_Campo=Si |
| `Proveedor_ID` | Ref -> Proveedores | No | Identificador del proveedor. Show_If tipo con Origen Externo; alta rapida |
| `Descripcion` | Text | No | Descripción. Herramienta propia: indicar cual herramienta |
| `Tipo_Comprobante` | Enum | Si | Factura, Boleta, Recibo por honorarios, Recibo simple o Sin comprobante. Valores: Factura, Boleta, Recibo por honorarios, Recibo simple, Sin comprobante. Sin comprobante en Interno manual no cuenta como falta de sustento |
| `Nro_Comprobante` | Text | No | Número del comprobante. Show_If hay comprobante |
| `Foto_Comprobante` | Image | No | Foto del comprobante. Required_If Tipo_Comprobante en Factura, Boleta, Recibo por honorarios |
| `Monto_Base` | Price | Si | Costo sin IGV. Costo SIN IGV. Boleta, recibo o sin comprobante: el total pagado |
| `Tiene_IGV` | Enum | Si | Si el comprobante discrimina IGV. Valores: Si, No |
| `Monto_IGV` | Price | Si | IGV del comprobante. Editable; advertencia si difiere de Base x IGV_PCT |
| `Total_Gasto` | Price | Si | Base + IGV: lo que se debe pagar al proveedor, este o no pagado. Base de Flujo_Caja cuando hay Fecha_Pago_Real |
| `Es_Credito_Fiscal` | Enum | Si | Valores: Si, No. Valor INICIAL (no App formula, para no pisar la decision manual). Editable_If: IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Admin","Gerencia")) Y la obra no esta Cerrada ni Cancelada. Valid_If: Si solo con Tipo_Comprobante=Factura y Tiene_IGV=Si. Show_If: solo Gestion (Campo no lo ve). Cada cambio escribe CREDITO_FISCAL_CAMBIADO en Log_Eventos |
| `Costo_Imputable` | Price | Si | Costo que cuenta contra el margen. Lo que cuenta contra el margen. Con credito = base; sin credito = base + IGV |
| `Fecha_Pago_Estimada` | Date | Si | Fecha en que se espera pagar al proveedor (base del flujo de caja proyectado). Valid_If >= Fecha. Show_If solo Gestion; Campo la deja igual a Fecha |
| `Fecha_Pago_Real` | Date | No | Fecha en que se pago. Vacia = pendiente de pago. Campo la fija igual a Fecha (gasto ya pagado); Gestion la deja vacia si queda a credito. Valid_If <= TODAY(). Se llena con la accion Marcar pagado. Show_If solo Gestion |
| `Estado` | Enum | Si | Estado del registro. Valores: Vigente, Anulado. No se borran, se anulan |
| `Motivo_Anulacion` | Text | No | Motivo de anulación (obligatorio al anular). Required_If Estado = Anulado |
| `Registrado_Por` | Email | Si | Usuario que registró. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Pagado` | Yes/No · *virtual* | - | TRUE = tiene Fecha_Pago_Real; FALSE = pendiente de pago (no hay columna de estado: se deriva) |
| `Revisar_Credito` | Yes/No · *virtual* | - | Factura con IGV registrada SIN credito fiscal: Gestion debe confirmar con Contabilidad (indicador informativo) |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Responsable_ID` | Ref -> Trabajadores · *virtual* | - | Fórmula: `[Obra_ID].[Responsable_ID]`. Referencia indirecta: Responsable_ID de Obras (via Obra_ID). Dereference expression |
| `Categoria_ID` | Ref -> Categorias_Costo · *virtual* | - | Fórmula: `[Tipo_Costo_ID].[Categoria_ID]`. Referencia indirecta: Categoria_ID de Tipos_Costo (via Tipo_Costo_ID). Dereference expression |

### Avances_Obra

- **Tipo:** Transaccional
- **Por qué existe:** Avance físico **diario** acumulado (0–100 %) con foto. Alimenta el valor ganado, el CPI y las proyecciones.
- **Relaciones:** Obras (N:1)
- **Procesos:** Control de avance; EVM
- **Apps:** Campo, Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Avance_ID` | Texto · **clave** | Si | Identificador del avance. Registro de avance fisico de la obra |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. Valid_If: obras abiertas |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Avance_Pct` | Number | Si | Avance físico acumulado (0–100). Avance ACUMULADO 0-100. Valid_If: >0, <=100 y >= ultimo avance vigente de la obra |
| `Descripcion` | Text | No | Descripción. |
| `Foto` | Image | No | Evidencia fotográfica. Evidencia |
| `Estado` | Enum | Si | Estado del registro. Valores: Vigente, Anulado. No se borran, se anulan |
| `Motivo_Anulacion` | Text | No | Motivo de anulación (obligatorio al anular). |
| `Registrado_Por` | Email | Si | Usuario que registró. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Responsable_ID` | Ref -> Trabajadores · *virtual* | - | Fórmula: `[Obra_ID].[Responsable_ID]`. Referencia indirecta: Responsable_ID de Obras (via Obra_ID). Dereference expression |

## 7. Facturación y cobranza

### Facturas_Obra

- **Tipo:** Transaccional
- **Por qué existe:** Facturas de **venta** que OXY emite al cliente (adelantos, valorizaciones, liquidación final). Aporta fecha de vencimiento, antigüedad de cartera y rezago de facturación.
- **Relaciones:** Obras (N:1); Abonos_Obra (1:N)
- **Procesos:** Facturación y cobranza; alertas de vencimiento
- **Apps:** Solo Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Factura_ID` | Texto · **clave** | Si | Factura de venta que paga. Facturas de VENTA que OXY emite al cliente. Solo Gestion |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. Valid_If: obras abiertas |
| `Tipo` | Enum | Si | Tipo de factura. Valores: Adelanto, Valorizacion, Liquidacion final, Otro. Adelanto, valorizacion, liquidacion final u otro |
| `Concepto` | Text | No | Texto que se imprime. Ej. Valorizacion N 2 |
| `Nro_Factura` | Text | Si | Serie-número. Serie-numero. Valid_If: unico |
| `Fecha_Emision` | Date | Si | Fecha de emisión. |
| `Plazo_Pago_Dias` | Number | Si | Días de crédito para calcular el vencimiento. Editable; se hereda del cliente |
| `Fecha_Vencimiento` | Date | Si | Emisión + plazo. COLUMNA REAL |
| `Monto_Neto` | Price | Si | Importe sin IGV. Sin IGV |
| `IGV` | Price | Si | IGV de la factura. Editable |
| `Total` | Price | Si | Neto + IGV. COLUMNA REAL. Valid_If: la suma de facturas vigentes de la obra no supera Total_Cobrar_Base (+ tolerancia) |
| `Doc_Factura` | File | No | Archivo de la factura. PDF o foto de la factura |
| `Estado` | Enum | Si | Estado del registro. Valores: Vigente, Anulado. No se borran, se anulan |
| `Motivo_Anulacion` | Text | No | Motivo de anulación (obligatorio al anular). Required_If Estado = Anulado |
| `Notificado_Vencida` | Enum | Si | Evita notificar dos veces. Valores: Si, No. Idempotencia del bot de vencimiento |
| `Registrado_Por` | Email | Si | Usuario que registró. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Cobrado` | Price · *virtual* | - | Abonos aplicados. Abonos aplicados a esta factura |
| `Saldo_Factura` | Price · *virtual* | - | Total − cobrado. |
| `Estado_Pago` | Enum · *virtual* | - | Pendiente / Parcial / Pagada / Anulada. |
| `Vencida` | Yes/No · *virtual* | - | TRUE si pasó el vencimiento con saldo. |
| `Dias_Vencida` | Number · *virtual* | - | Días de mora. |
| `Dias_Emitida` | Number · *virtual* | - | Antigüedad desde la emisión. Antiguedad desde la emision |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Responsable_ID` | Ref -> Trabajadores · *virtual* | - | Fórmula: `[Obra_ID].[Responsable_ID]`. Referencia indirecta: Responsable_ID de Obras (via Obra_ID). Dereference expression |

### Abonos_Obra

- **Tipo:** Transaccional
- **Por qué existe:** Pagos del cliente (en soles), incluidas detracciones y retenciones. Su suma se compara con el total a cobrar de la obra para medir la cobranza.
- **Relaciones:** Obras (N:1), Facturas_Obra (N:1 opcional), Medios_Pago (N:1)
- **Procesos:** Cobranza
- **Apps:** Solo Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Abono_ID` | Texto · **clave** | Si | Identificador del abono. Solo en la app de Gestion |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. |
| `Factura_ID` | Ref -> Facturas_Obra | No | Factura de venta que paga. Factura que paga este abono (opcional pero recomendado). Valid_If: facturas vigentes de la misma obra. Si el abono cubre varias, registrar un abono por factura |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Concepto` | Enum | Si | Texto que se imprime. Valores: Pago, Detraccion, Retencion. Detraccion/Retencion cuentan como abono para llegar al 100% |
| `Medio_Pago_ID` | Ref -> Medios_Pago | Si | Medio de pago. |
| `Nro_Operacion` | Text | No | Número de operación bancaria. |
| `Monto_Abono` | Price | Si | Monto depositado. Lo que el cliente realmente deposito |
| `Incluye_IGV` | Enum | Si | Valores: Si, No. Informativo: el abono se compara contra Total_Cobrar_Base (incluye IGV) |
| `Foto_Voucher` | Image | No | Foto del voucher. |
| `Estado` | Enum | Si | Estado del registro. Valores: Vigente, Anulado. No se borran, se anulan |
| `Motivo_Anulacion` | Text | No | Motivo de anulación (obligatorio al anular). Required_If Estado = Anulado |
| `Registrado_Por` | Email | Si | Usuario que registró. |
| `Creado_En` | DateTime | Si | Fecha y hora de creación. |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Responsable_ID` | Ref -> Trabajadores · *virtual* | - | Fórmula: `[Obra_ID].[Responsable_ID]`. Referencia indirecta: Responsable_ID de Obras (via Obra_ID). Dereference expression |

## 8. Log y control

### Log_Eventos

- **Tipo:** Log / auditoría
- **Por qué existe:** Bitácora de eventos de negocio escrita por los bots (gasto creado, proforma aceptada, cobranza completa…). Base de las notificaciones.
- **Relaciones:** Obras (referencia); todas las tablas transaccionales (origen)
- **Procesos:** Notificaciones; auditoría
- **Apps:** Gestión (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Evento_ID` | Texto · **clave** | Si | Identificador del evento. Escrito por bots; nadie lo edita |
| `Fecha_Hora` | DateTime | Si | Fecha y hora. |
| `Tipo_Evento` | Text | Si | Código del evento. GASTO_CREADO, GASTO_ANULADO, GASTO_PAGADO, GASTO_SOBRE_PLANIFICADO, CREDITO_FISCAL_CAMBIADO, HORAS_PENDIENTES, PROFORMA_ENVIADA, PROFORMA_ACEPTADA, PROFORMA_RECHAZADA, PROFORMA_ANULADA, PROFORMA_ELIMINADA, PROFORMA_VENCIDA, OBRA_CREADA, OBRA_ESTADO_CAMBIADO, OBRA_CERRADA, OBRA_ATRASADA, ABONO_CREADO, ABONO_ANULADO, COBRANZA_COMPLETA, COBRANZA_REABIERTA, RECORDATORIO_COBRANZA, FACTURA_POR_VENCER, FACTURA_VENCIDA |
| `Tabla` | Text | Si | Tabla de origen. |
| `Registro_ID` | Text | Si | Registro de origen. |
| `Obra_ID` | Text | No | Identificador de la obra. |
| `Usuario` | Email | No | Usuario que originó. |
| `Resumen` | Text | Si | Texto del evento. Ej. Juan registro S/ 350 - Material - Huanta |
| `Procesado` | Enum | Si | Si ya se notificó. Valores: Si, No. El proceso de notificaciones lo marca Si |
| `Procesado_En` | DateTime | No | Cuándo se procesó. |
| `Canal` | Enum | No | Canal de notificación. Valores: Correo, Push, Ambos |

### Alertas

- **Tipo:** KPIs / control
- **Por qué existe:** Alertas generadas por reglas (obra sin gastos, factura vencida, consumo alto, etc.), con severidad y estado de atención. La clave `Regla|Obra|Fecha` evita duplicados.
- **Relaciones:** Obras (N:1); Metas_KPI (umbrales)
- **Procesos:** Control diario; notificaciones
- **Apps:** Gestión, Dashboard

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Alerta_ID` | Texto · **clave** | Si | Clave `Regla\|Obra\|Fecha`. Regla\|Obra\|yyyy-MM-dd: evita duplicar la misma alerta el mismo dia |
| `Fecha_Hora` | DateTime | Si | Fecha y hora. |
| `Regla` | Text | Si | Regla que disparó. |
| `Severidad` | Enum | Si | Info, Ámbar o Rojo. Valores: Info, Ambar, Rojo |
| `Obra_ID` | Ref -> Obras | No | Identificador de la obra. |
| `Mensaje` | Text | Si | Texto de la alerta. |
| `Estado` | Enum | Si | Estado del registro. Valores: Abierta, Reconocida, Resuelta |
| `Reconocida_Por` | Email | No | Quien la reconoció. |
| `Reconocida_En` | DateTime | No | Cuándo se reconoció. |
| `Proforma_ID` | Ref -> Proformas · *virtual* | - | Fórmula: `[Obra_ID].[Proforma_ID]`. Referencia indirecta: Proforma_ID de Obras (via Obra_ID). Dereference expression |
| `Cliente_ID` | Ref -> Clientes · *virtual* | - | Fórmula: `[Obra_ID].[Cliente_ID]`. Referencia indirecta: Cliente_ID de Obras (via Obra_ID). Dereference expression |
| `Responsable_ID` | Ref -> Trabajadores · *virtual* | - | Fórmula: `[Obra_ID].[Responsable_ID]`. Referencia indirecta: Responsable_ID de Obras (via Obra_ID). Dereference expression |

### Metas_KPI

- **Tipo:** Configuración de KPIs
- **Por qué existe:** Umbrales ámbar/rojo editables de cada indicador. *Menor_Mejor*: alerta si valor > umbral; *Mayor_Mejor*: alerta si valor < umbral.
- **Relaciones:** Alertas, Snap_Obra_Dia.Semaforo
- **Procesos:** Alertas y semáforos
- **Apps:** Gestión

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `KPI` | Texto · **clave** | Si | Código del indicador. |
| `Sentido` | Enum | Si | Menor_Mejor o Mayor_Mejor. Valores: Menor_Mejor, Mayor_Mejor. Menor_Mejor: alerta si valor > umbral. Mayor_Mejor: alerta si valor < umbral |
| `Umbral_Ambar` | Decimal | Si | Valor que dispara ámbar. |
| `Umbral_Rojo` | Decimal | Si | Valor que dispara rojo. |
| `Descripcion` | Text | No | Descripción. |

### Jobs_Control

- **Tipo:** Control técnico
- **Por qué existe:** Un registro por tarea programada: ancla de los bots de una sola ejecución y monitor de "datos actualizados a las hh:mm".
- **Relaciones:** —
- **Procesos:** Todos los bots programados
- **Apps:** Gestión, Dashboard

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Job_ID` | Texto · **clave** | Si | Identificador del job (J01–J12). Ancla de los bots de una sola ejecucion |
| `Descripcion` | Text | Si | Descripción. |
| `Programacion` | Text | Si | Horario (zona America/Lima). Zona America/Lima |
| `Ultima_Ejecucion` | DateTime | No | Última ejecución. Cada job la actualiza al terminar |
| `Ultimo_Resultado` | Text | No | Resultado. |
| `Activo` | Yes/No | Si | Si es "No" el registro deja de ofrecerse en listas, sin borrarlo. |

## 9. Consolidación para el dashboard

### Snap_Obra_Dia

- **Tipo:** Consolidación para KPIs
- **Por qué existe:** Foto diaria por obra, actualizada cada hora (la última pasada del día es el cierre). Pre-agrega costos, cobranza, facturación, avance y alertas para que el dashboard no lea transacciones.
- **Relaciones:** Obras, Clientes (N:1)
- **Procesos:** Dashboard; alertas
- **Apps:** Dashboard (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Snap_ID` | Texto · **clave** | Si | Clave del snapshot. Obra_ID\|yyyy-MM-dd. Una fila por obra por dia, actualizada cada hora; la ultima pasada es el cierre |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Anio_Semana` | Text | Si | Año-semana (p. ej. 2026-W41). Ej. 2026-W41 |
| `Anio_Mes` | Text | Si | Año-mes (p. ej. 2026-10). Ej. 2026-10 |
| `Es_Fin_Semana` | Enum | Si | Marca para filtrar el cierre semanal. Valores: Si, No. Domingo |
| `Es_Fin_Mes` | Enum | Si | Marca para filtrar el cierre mensual. Valores: Si, No. Ultimo dia del mes |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. |
| `Cliente_ID` | Ref -> Clientes | Si | Identificador del cliente (referencia). |
| `Estado_Obra` | Text | Si | Estado de la obra al momento. |
| `Precio_Neto` | Price | Si | Suma de conceptos sin IGV. [Obra_ID].[Precio_Neto_Base] |
| `Total_Cobrar` | Price | Si | Subtotal + IGV. |
| `Costo_Planificado` | Price | Si | Presupuesto de costo neto. |
| `Gasto_Total` | Price | Si | [Obra_ID].[Total_Gastos] |
| `Personal_Total` | Price | Si | [Obra_ID].[Total_Personal] |
| `Costo_Real` | Price | Si | Gastos + personal. |
| `Consumo_Pct` | Percent | Si | Costo real / costo planificado. |
| `Margen_Plan` | Price | Si | Precio neto − costo planificado. |
| `Margen_Real_Parcial` | Price | Si | Precio neto − costo real a la fecha. |
| `IGV_No_Recuperable` | Price | Si | IGV que pasó a costo. |
| `Costo_MO_Interna` | Price | Si | Costo de personal propio. Equivale a Total_Personal |
| `Costo_MO_Tercerizada` | Price | Si | Gasto de mano de obra tercerizada. Gastos de tipos con Modalidad_MO = Tercerizado |
| `Gasto_Dia` | Price | Si | Costo imputable registrado hoy. Costo imputable registrado hoy |
| `Horas_Dia` | Decimal | Si | Horas del día. |
| `Abonos_Acum` | Price | Si | Abonos acumulados. |
| `Saldo` | Price | Si | Total a cobrar − abonos. |
| `Pct_Cobrado` | Percent | Si | Abonos / total a cobrar. |
| `Facturado_Acum` | Price | Si | Total de facturas de venta vigentes. |
| `Pct_Facturado` | Percent | Si | Facturado / total a cobrar. |
| `Cartera_Vencida` | Price | Si | Cartera vencida en soles. Saldo de facturas vencidas |
| `Flujo_Caja` | Price | Si | Abonos - gastos pagados a la fecha - personal |
| `Por_Pagar` | Price | Si | Gastos registrados sin pagar a la fecha de corte |
| `Avance_Pct` | Number | No | Avance físico acumulado (0–100). |
| `Valor_Ganado` | Price | No | Costo planificado × avance. |
| `CPI` | Decimal | No | Índice de desempeño de costo (>1 bien, <1 sobrecosto). |
| `Proyeccion_Costo_Final` | Price | No | Costo estimado al terminar. |
| `Margen_Proyectado` | Price | No | Margen estimado al terminar. |
| `Dias_En_Ejecucion` | Number | No | Días desde el inicio. |
| `Dias_Atraso` | Number | No | Días sobre la fecha estimada. |
| `Dias_Sin_Gastos` | Number | No | Días desde el último gasto/horas; alerta > 7. Dias desde el ultimo gasto o registro de horas |
| `Dias_Sin_Avance` | Number | No | Días desde el último avance. |
| `Gastos_Sin_Sustento` | Number | No | Cantidad sin comprobante. Cantidad sin comprobante (excluye depreciacion) |
| `Semaforo` | Text | Si | Verde / Ámbar / Rojo según Metas_KPI. Verde / Ambar / Rojo segun Metas_KPI |
| `Generado_En` | DateTime | Si | Momento de la última actualización. |

### Snap_Costo_Tipo_Semana

- **Tipo:** Consolidación para KPIs
- **Por qué existe:** Presupuesto vs. real por obra y tipo de costo, un registro por semana (domingo).
- **Relaciones:** Obras, Categorias_Costo, Tipos_Costo (N:1)
- **Procesos:** Dashboard (costos por tipo)
- **Apps:** Dashboard (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Snap_ID` | Texto · **clave** | Si | Clave del snapshot. Obra_ID\|Tipo_Costo_ID\|yyyy-MM-dd (domingo) |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Anio_Semana` | Text | Si | Año-semana (p. ej. 2026-W41). Ej. 2026-W41 |
| `Anio_Mes` | Text | Si | Año-mes (p. ej. 2026-10). Ej. 2026-10 |
| `Es_Fin_Semana` | Enum | Si | Marca para filtrar el cierre semanal. Valores: Si, No. Domingo |
| `Es_Fin_Mes` | Enum | Si | Marca para filtrar el cierre mensual. Valores: Si, No. Ultimo dia del mes |
| `Obra_ID` | Ref -> Obras | Si | Identificador de la obra. |
| `Categoria_ID` | Ref -> Categorias_Costo | Si | Categoría de costo (MO, MAT, EQP, VIA). |
| `Tipo_Costo_ID` | Ref -> Tipos_Costo | Si | Tipo de costo. |
| `Presupuesto` | Price | Si | Costo planificado. Costo_Imputable planificado |
| `Real` | Price | Si | Costo imputable real. Costo imputable |
| `Pct` | Percent | Si | Real / presupuesto. |
| `Generado_En` | DateTime | Si | Momento de la última actualización. |

### Snap_Global_Hora

- **Tipo:** Consolidación para KPIs
- **Por qué existe:** Pulso horario de la empresa (gastos del día, horas pendientes, obras activas, alertas abiertas).
- **Relaciones:** —
- **Procesos:** Dashboard (control del día)
- **Apps:** Dashboard (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Snap_ID` | Texto · **clave** | Si | Clave del snapshot. yyyy-MM-dd HH |
| `Fecha` | Date | Si | Fecha del registro o movimiento. |
| `Hora` | Number | Si | Hora (0–23). |
| `Gastos_Hoy_N` | Number | Si | Cantidad de gastos hoy. |
| `Gastos_Hoy` | Price | Si | Gasto de hoy en soles. |
| `Gastos_Sin_Foto_Hoy` | Number | Si | Gastos de hoy sin foto. |
| `Horas_Pend_Aprobar` | Number | Si | Horas por aprobar. |
| `Abonos_Hoy` | Price | Si | Abonos de hoy en soles. |
| `Obras_Activas` | Number | Si | Obras activas. |
| `Alertas_Abiertas` | Number | Si | Alertas abiertas. |
| `Generado_En` | DateTime | Si | Momento de la última actualización. |

### Snap_Global_Dia

- **Tipo:** Consolidación para KPIs
- **Por qué existe:** Resumen diario de toda la empresa (obras por estado, costo, horas, abonos, facturado, cartera vencida, pipeline de proformas). Base de las vistas semanal y mensual.
- **Relaciones:** —
- **Procesos:** Dashboard (tendencias)
- **Apps:** Dashboard (lectura)

| Campo | Tipo | Req. | Descripción |
|---|---|---|---|
| `Fecha` | Date (KEY) | Si | Fecha del registro o movimiento. Una fila por dia, actualizada cada hora |
| `Anio_Semana` | Text | Si | Año-semana (p. ej. 2026-W41). Ej. 2026-W41 |
| `Anio_Mes` | Text | Si | Año-mes (p. ej. 2026-10). Ej. 2026-10 |
| `Es_Fin_Semana` | Enum | Si | Marca para filtrar el cierre semanal. Valores: Si, No. Domingo |
| `Es_Fin_Mes` | Enum | Si | Marca para filtrar el cierre mensual. Valores: Si, No. Ultimo dia del mes |
| `Obras_Por_Iniciar` | Number | Si | Obras por iniciar. |
| `Obras_En_Ejecucion` | Number | Si | Obras en ejecución. |
| `Obras_Pausadas` | Number | Si | Obras pausadas. |
| `Obras_Terminadas` | Number | Si | Obras terminadas. |
| `Costo_Dia` | Price | Si | Costo del día en soles. |
| `Horas_Dia` | Decimal | Si | Horas del día. |
| `Horas_Extra_Dia` | Decimal | Si | Horas extra del día. |
| `Abonos_Dia` | Price | Si | Abonos del día en soles. |
| `Facturado_Dia` | Price | Si | Facturado del día en soles. |
| `Por_Cobrar` | Price | Si | Por cobrar en soles. |
| `Cartera_Vencida` | Price | Si | Cartera vencida en soles. |
| `Proformas_Abiertas_N` | Number | Si | Proformas enviadas sin respuesta. Lectura en vivo de las Enviadas al refrescar; los días pasados no se recalculan. |
| `Proformas_Abiertas` | Price | Si | Monto de proformas abiertas. Lectura en vivo de `Precio_Neto` de las Enviadas al refrescar; puede variar porque las líneas de una Enviada son editables. Los días pasados no se recalculan. |
| `Aceptadas_Dia` | Number | Si | Proformas aceptadas hoy. |
| `Rechazadas_Dia` | Number | Si | Proformas rechazadas hoy (por `Fecha_Rechazo`). |
| `Pct_Costo_Con_Factura_30d` | Percent | Si | % del costo con factura (30 días). |
| `IGV_No_Recuperable_30d` | Price | Si | IGV a costo en 30 días. |
| `Generado_En` | DateTime | Si | Momento de la última actualización. |

## 11. Parámetros iniciales (Configuracion, Compania y Metas_KPI)

Valores sembrados en la plantilla. Se editan en las tablas, sin tocar las apps.

**Configuracion**

| Clave | Valor | Nota |
|---|---|---|
| `VIGENCIA_PROFORMA_DIAS` | 15 | Dias de vigencia de una proforma enviada |
| `IGV_PCT` | 0.18 | Tasa de IGV usada en proformas y gastos |
| `MARGEN_MINIMO_PCT` | 0.10 | EJEMPLO, definir con Gerencia: margen planificado minimo para enviar una proforma sin aviso |
| `DIAS_RECORDATORIO_COBRANZA` | 30 | Dias sin abonos para recordatorio |
| `TOLERANCIA_COBRANZA` | 1.00 | Diferencia maxima (S/) para dar la cobranza por completa |
| `PLAZO_PAGO_DIAS_DEFECTO` | 30 | EJEMPLO, editable: dias de credito por defecto de un cliente |
| `DIAS_ALERTA_SIN_GASTOS` | 7 | Alerta si una obra en ejecucion pasa mas de estos dias sin gastos ni horas (ver Metas_KPI) |

**Compania** (una fila, `Compania_ID` = `OXY`)

Todos los campos de texto arrancan con `COMPLETAR` hasta que OXY escriba los datos reales; `Web` y `Emails_Cobranza` arrancan vacíos.

**Metas_KPI** (Menor_Mejor: alerta si el valor supera el umbral)

| KPI | Sentido | Ámbar | Rojo | Descripción |
|---|---|---|---|---|
| `CONSUMO_PLAN_PCT` | Menor_Mejor | 0.9 | 1 | Consumo del costo planificado (0.90 = 90%) |
| `CONSUMO_MENOS_AVANCE_PP` | Menor_Mejor | 10 | 20 | Puntos porcentuales de consumo por encima del avance |
| `MARGEN_CAIDA_VS_PLAN_PP` | Menor_Mejor | 5 | 10 | Puntos porcentuales que cae el margen real parcial frente al planificado |
| `CPI` | Mayor_Mejor | 0.95 | 0.85 | Indice de desempeno de costo |
| `DIAS_SIN_GASTOS` | Menor_Mejor | 7 | 14 | Obra en ejecucion sin gastos ni horas: alerta a mas de 7 dias (definido por el cliente) |
| `DIAS_SIN_AVANCE` | Menor_Mejor | 2 | 6 | Obra en ejecucion sin avance registrado. El avance es DIARIO: alerta desde 3 dias (ambar si > 2, rojo si > 6). Confirmado por el usuario |
| `DIAS_ATRASO` | Menor_Mejor | 0 | 7 | Dias sobre la fecha estimada de fin |
| `PCT_SIN_COMPROBANTE_30D` | Menor_Mejor | 0.2 | 0.35 | % del costo sin comprobante en 30 dias (excluye depreciacion) |
| `HORAS_PENDIENTES_HORAS` | Menor_Mejor | 48 | 120 | Horas transcurridas sin aprobar |
| `DIAS_FACTURA_VENCIDA` | Menor_Mejor | 0 | 30 | Dias de vencimiento de una factura con saldo |
| `REZAGO_FACTURACION_PP` | Menor_Mejor | 15 | 30 | EJEMPLO nuevo: avance fisico menos % facturado, en puntos porcentuales |
| `DIAS_PROFORMA_SIN_RESPUESTA` | Menor_Mejor | 7 | 15 | Proforma enviada sin respuesta |
