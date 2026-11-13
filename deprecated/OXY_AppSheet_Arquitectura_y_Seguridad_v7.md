# OXY Industrial S.R.L. — Arquitectura y seguridad de las aplicaciones AppSheet

**Plan:** Core · **Datos:** un solo Google Sheet, `OXYData` · **Zona horaria de las apps y de los bots programados:** America/Lima (UTC-5).
**Aplicaciones:** `OXY Master`, `OXY Proformas`, `OXY Gestión`, `OXY Campo` y `OXY Dashboard`.
**Para quién es:** quien diseña y construye las aplicaciones en el editor de AppSheet. Este documento fija lo que es común a las cinco: qué hace cada una, quién entra, qué tablas lleva, cómo se reparten los bots y cómo se prueba lo que cruza de una a otra. El detalle de cada aplicación (datos, vistas, acciones y automatizaciones) está en su propio documento.

---

## 1. Documentos del conjunto

| Documento | Qué contiene |
|---|---|
| `OXY_DataModel_Especificacion` | La base de datos central (`OXYData`): tablas, columnas, relaciones y reglas de datos. Es la fuente de verdad de los datos. |
| `OXY_Propuesta_Dashboard_Indicadores` | La propuesta al cliente: indicadores, tablas de consolidación y procesos programados. Es la base para especificar OXY Dashboard. |
| `OXY_AppSheet_Arquitectura_y_Seguridad` | Este documento. |
| `OXY_AppSheet_Componentes_Comunes` | Convenciones de nombres, expresiones reutilizables, procedimientos generales del editor y plantilla de ficha de acción y de bot. |
| `OXY_App_Master_Especificacion` | Especificación de OXY Master. |
| `OXY_App_Proformas_Especificacion` | Especificación de OXY Proformas. |
| `OXY_App_Gestion_Especificacion` | Especificación de OXY Gestión. |
| `OXY_App_Campo_Especificacion` | Especificación de OXY Campo. |
| `OXY_App_Dashboard_Especificacion` | Especificación de OXY Dashboard. |
| `OXY_AppSheet_Historial_de_Cambios` | El historial de cambios de todos los documentos. Ningún otro documento guarda su propio historial. |
| `Pendientes` | Lo que falta por hacer y por decidir. |

---

## 2. Estructura de un documento de app

Cada documento de app tiene estas secciones, en este orden. Las secciones 3 a 6 son las cuatro que corresponden a las pestañas de trabajo del editor de AppSheet: datos, vistas, acciones y automatizaciones.

| N.º | Sección | Contenido |
|---|---|---|
| 1 | Propósito y alcance | Quién la usa, en qué dispositivo, qué hace y qué no hace |
| 2 | Acceso y seguridad | Roles permitidos, lista de usuarios, expresión de rol de la app y lo que llega al dispositivo |
| 3 | **Especificación de Datos** | Tablas incluidas con sus permisos (*Adds*, *Updates*, *Deletes*), slices y, por tabla, un bloque por columna: tipo, `Show?`, `Required?`, `Editable?`, `Valid if`, `Invalid value error`, `Initial value`, `App formula` y virtuales |
| 4 | **Especificación de Vistas** | Por vista: tipo, tabla o slice, ordenamiento, agrupamiento, columnas, acciones visibles, rol que la usa, menú y vista inicial, reglas de formato por estado |
| 5 | **Especificación de Acciones** | Una ficha por acción, con los roles permitidos |
| 6 | **Especificación de Automatizaciones** | Una ficha por bot (de evento y programado), con sus límites en Core |
| 7 | Notificaciones | Evento, destinatarios por rol, canal y qué app debe tener instalada el destinatario |
| 8 | Relación con otras apps | Qué lee y qué escribe de las demás, bots duplicados, retrasos de sincronización |
| 9 | Configuración de la app | Inicio de sesión obligatorio, zona horaria, sincronización, apariencia y rendimiento |
| 10 | Pruebas | Pruebas positivas y negativas por rol |
| 11 | Criterios de salida y orden de construcción | Lista de verificación para dar la app por terminada |
| 12 | Pendientes y decisiones de la app | Validaciones y decisiones que solo afectan a esta app |

Reglas de redacción de los documentos de app:

1. Cada columna, acción y bot se escribe con una propiedad por línea, con los nombres de propiedad del editor nuevo de AppSheet.
2. Un documento describe solo lo vigente: no guarda historial de cambios ni cita versiones de otros documentos.
3. Cada documento cita a los demás por su nombre, sin número de versión.

---

## 3. Catálogo de aplicaciones

| App | Para qué | Uso previsto | Roles permitidos | Documento |
|---|---|---|---|---|
| `OXY Master` | Altas, ediciones y bajas de las tablas maestras, los catálogos y la configuración del sistema (clientes, trabajadores, tarifas, tipos de costo, etc.) | Escritorio o celular | `Super`, `Administracion` | `OXY_App_Master_Especificacion` |
| `OXY Proformas` | Ciclo de vida de la proforma: borrador, envío, aceptación, rechazo, anulación, vencimiento. Al aceptar una proforma crea la obra; la obra se opera después en OXY Gestión | Escritorio o celular | `Super`, `Administracion`, `Supervisor`, `Planificacion` | `OXY_App_Proformas_Especificacion` |
| `OXY Gestión` | Ciclo de vida de la obra desde que se crea, más gastos, horas, avances, facturas de venta, abonos, cobranza y alertas. Aloja los procesos programados | Escritorio | `Super`, `Administracion`, `Supervisor`, `Operaciones` | `OXY_App_Gestion_Especificacion` |
| `OXY Campo` | Registro de gastos, horas y avances de las obras, y consulta de obras. Sin proformas, facturas ni abonos | Celular | `Super`, `Campo` | `OXY_App_Campo_Especificacion` |
| `OXY Dashboard` | Indicadores de solo lectura a partir de `Snap_*`, `Alertas` y `Metas_KPI`. Lo único que se escribe es la atención de alertas (reconocer y resolver) | Celular y escritorio | `Super`, `Administracion` | `OXY_App_Dashboard_Especificacion` |

No hay restricción de dispositivo: cada usuario decide cómo abre y cómo visualiza cada app.

---

## 4. Roles

Cada persona tiene un solo rol, que se guarda en `Trabajadores.Rol`. Los valores válidos son los seis de la tabla. Se escriben exactamente así (sin tilde) en `Trabajadores`, en la lista `Roles` de `_Listas` y en todas las expresiones.

| Rol | Apps a las que accede |
|---|---|
| `Super` | Las cinco |
| `Administracion` | OXY Master, OXY Proformas, OXY Gestión y OXY Dashboard; además OXY Campo, solo para recibir avisos |
| `Supervisor` | OXY Proformas y OXY Gestión; además OXY Campo, solo para recibir avisos |
| `Planificacion` | OXY Proformas |
| `Operaciones` | OXY Gestión |
| `Campo` | OXY Campo |

Matriz rol × app (✓ = puede abrir la app y ejecutar sus acciones; **avisos** = está en la lista de usuarios de la app solo para recibir push, y su rol no figura entre los permitidos, así que no ejecuta acciones):

| Rol | Master | Proformas | Gestión | Campo | Dashboard |
|---|---|---|---|---|---|
| `Super` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `Administracion` | ✓ | ✓ | ✓ | avisos | ✓ |
| `Supervisor` | – | ✓ | ✓ | avisos | – |
| `Planificacion` | – | ✓ | – | – | – |
| `Operaciones` | – | – | ✓ | – | – |
| `Campo` | – | – | – | ✓ | – |

`Super` es un rol técnico: no recibe avisos (sección 7).

---

## 5. Seguridad

### 5.1 Qué se controla y cómo

| Capa | Qué controla | Cómo se configura | Estado |
|---|---|---|---|
| 1. Inicio de sesión y lista de usuarios | Quién puede abrir la app | En cada app: **Require user sign-in** activo y lista de usuarios autorizados (⚠ V15 para la ruta en el editor) | En uso |
| 2. Rol en las acciones | Quién ve y ejecuta cada acción | `Only if this condition is true` de la acción, con la expresión de rol de 5.3 | En uso |
| 3. Filtro de seguridad por tabla | Qué filas llegan al dispositivo | *Data → Tables → tabla → Security filter* | No se usa en esta versión (ver `Pendientes`) |
| 4. Reglas por rol en columnas | `Show?` y `Editable?` según el rol | Fórmulas con el rol del usuario en la columna | No se usa en esta versión: la diferencia entre audiencias se resuelve con las tablas y las columnas que lleva cada app |

### 5.2 Acceso a los datos

1. Quien puede abrir una app lee todos los datos de las tablas que esa app incluye. La protección de los datos es qué tablas lleva cada app (sección 6) y la lista de usuarios de cada app.
2. Los roles solo gobiernan las acciones.
3. Una columna oculta con `Show?` igual llega al dispositivo. `Show?`, `Editable?` y `Only if` controlan la pantalla, no el dato.
4. Siguen vigentes las condiciones que no dependen del rol: por estado del registro (por ejemplo, la obra no está `Cerrada`) y por dueño del registro (por ejemplo, un gasto propio dentro de 24 horas).

### 5.3 Expresión de rol de las acciones

Toda acción lleva en su `Only if this condition is true` la expresión de rol de su app. Se escribe completa en cada acción, con la lista de roles que pueden ejecutarla. Falla de forma segura: si la cuenta no está en `Trabajadores` o está inactiva, devuelve falso.

Forma general:
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST(<roles>)))
```

Con la lista de roles de cada app:

**OXY Master**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Administracion")))
```
**OXY Proformas**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Administracion","Supervisor","Planificacion")))
```
**OXY Gestión**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Administracion","Supervisor","Operaciones")))
```
**OXY Campo**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Campo")))
```
**OXY Dashboard**
```
AND(LOOKUP(USEREMAIL(),"Trabajadores","Email","Activo"),IN(LOOKUP(USEREMAIL(),"Trabajadores","Email","Rol"),LIST("Super","Administracion")))
```

Reglas de uso:

1. Cuando una acción además depende del estado u otra condición, se combina con `AND(<expresión de rol>,<condición>)`.
2. En esta versión todas las acciones de una app admiten todos los roles de esa app; en cada ficha, la línea **Roles permitidos** repite la lista de la app. Para restringir una acción más adelante basta quitar roles de la lista de esa acción.
3. Esto incluye la acción de cerrar una obra con saldo pendiente: la ejecutan todos los roles de OXY Gestión.
4. El tope de facturación (la suma de facturas vigentes de una obra no puede superar el total a cobrar más la tolerancia) aplica a todos los roles, sin excepción.
5. Cada documento de app lleva una matriz acción × rol que es la fuente de las listas de roles de las fichas.
6. Las acciones auxiliares (`Position` = *Hide*) que solo llaman los grupos y los bots llevan `Only if` vacío: un bot programado no tiene usuario (`USEREMAIL()` vacío) y la expresión de rol lo bloquearía. La condición de rol la llevan los botones que las llaman.

### 5.4 Altas, bajas y cambios de rol

**Alta de una persona**
1. En OXY Master, crear la fila en `Trabajadores` con `Email` (la cuenta Google con la que inicia sesión), `Rol` y `Activo = Si`.
2. Agregar su cuenta a la lista de usuarios de cada app que le corresponde según la matriz de la sección 4, incluida OXY Campo para `Administracion` y `Supervisor`.

**Cambio de rol**
1. En OXY Master, editar `Trabajadores.Rol`.
2. Ajustar la lista de usuarios de las apps según la matriz de la sección 4.

**Baja de una persona**
1. En OXY Master, poner `Activo = No`. Desde ese momento ninguna acción le aparece.
2. Quitar su cuenta de la lista de usuarios de cada app donde estaba. Mientras siga en una lista, esa persona puede abrir la app y leer sus datos (5.2).

**Quién edita los roles.** Cualquier usuario de OXY Master con acceso a las acciones de `Trabajadores` (en esta versión, `Super` y `Administracion`). Esto permite que `Administracion` asigne el rol `Super`; es un riesgo aceptado.

### 5.5 Riesgos aceptados en esta versión

| Qué llega al dispositivo | Quién lo recibe | Riesgo |
|---|---|---|
| Todas las obras, con precio, IGV, total a cobrar y presupuesto de costo | Cada usuario de OXY Campo | Ve el precio y el presupuesto de obras que no son suyas |
| Todos los gastos y registros de horas, con los costos por hora | Cada usuario de OXY Campo | Ve gastos y tarifas aplicadas de otras personas |
| Datos de `Compania`: cuentas bancarias, condiciones y correos de cobranza | Cada usuario de OXY Campo | Ve cuentas bancarias de OXY |
| Planificación de costos de todas las proformas (`Proforma_Planificacion`) | Cada usuario de OXY Campo | Ve el costo planificado por tipo de costo de todas las obras |
| Borrado de filas en tablas maestras | Cualquier usuario de OXY Master | Una fila borrada deja en blanco las referencias que la usan (ver DA-09) |
| Todos los trabajadores (nombre, rol, correo) | Todas las apps que incluyen `Trabajadores` | Bajo |
| `Tarifas_Trabajador` | Usuarios de OXY Master y OXY Gestión | Ven las tarifas de todo el personal |
| Cualquier tabla de una app | Toda cuenta que esté en la lista de usuarios de esa app, aunque su rol no esté permitido o esté inactiva | Lee los datos hasta que se la quita de la lista |
| Todo el `OXYData` | Cualquiera con acceso de edición al Sheet | Puede saltarse todas las reglas (5.6) |

Ninguna de las barreras protege los datos de un dispositivo robado o de una persona que consulte la aplicación con otras herramientas: el control es quitarle el acceso (5.4) y bloquear el dispositivo.

### 5.6 Permisos del Sheet y de Drive

1. `OXYData` se comparte solo con el dueño de los datos. Los usuarios de las apps no necesitan acceso al Sheet: la app lee y escribe con la cuenta del dueño.
2. Las carpetas de archivos (`Proformas_Files`, `Gastos_Obra_Images`, `Avances_Obra_Images`, `Facturas_Obra_Files`, `Abonos_Obra_Images`) también se comparten solo con el dueño. Los archivos se abren desde la app.
3. Quien edite el Sheet directamente puede saltarse todas las reglas. Las ediciones directas se limitan al dueño y a la carga de datos demo. Todo cambio de estructura pasa primero por el modelo de datos.
4. Antes de cualquier cambio de estructura o carga masiva se hace una copia de `OXYData` con el nombre `OXYData_aaaammdd_hhmm`.

### 5.7 Pruebas de seguridad

Cuentas de prueba (ocho cuentas Google reales, cada una abierta en un teléfono o navegador distinto del que usa quien construye, con la sesión recién iniciada):

| Cuenta | Qué comprobar | Resultado esperado |
|---|---|---|
| `Super` | Abrir las cinco apps | Abre todas y ve las acciones de cada una |
| `Administracion` | Abrir cada app | Abre Master, Proformas, Gestión y Dashboard; abre Campo solo para recibir avisos y ninguna acción le aparece allí |
| `Supervisor` | Abrir cada app | Abre Proformas y Gestión; abre Campo solo para recibir avisos y ninguna acción le aparece allí; no abre Master ni Dashboard |
| `Planificacion` | Abrir cada app | Abre solo Proformas |
| `Operaciones` | Abrir cada app | Abre solo Gestión |
| `Campo` | Abrir cada app | Abre solo Campo; ve y ejecuta solo las acciones de Campo |
| `Campo` con `Activo = No` y todavía en la lista de Campo | Abrir OXY Campo | Abre y lee datos (riesgo aceptado, 5.5), pero ninguna acción le aparece |
| Cuenta que no está en `Trabajadores` y sí en una lista | Abrir esa app | Abre y lee datos (riesgo aceptado, 5.5), pero ninguna acción le aparece (⚠ V17) |
| Cuenta que no está en ninguna lista | Abrir cualquier app | No puede entrar |
| `Campo` agregado a la lista de OXY Gestión por error | Abrir OXY Gestión | Ninguna acción le aparece |

---

## 6. Tablas por app

Códigos: **L** lectura · **I** inserción (*Adds*) · **A** actualización (*Updates*) · **E** eliminación (*Deletes*) · **–** la tabla no está en la app. Solo hay eliminaciones donde se indica con **E**.

| Tabla | Master | Proformas | Gestión | Campo | Dashboard |
|---|---|---|---|---|---|
| `Areas_Compania` | L·I·A·E | – | L | L | – |
| `Trabajadores` | L·I·A | L | L | L | L |
| `Tarifas_Trabajador` | L·I·A·E | – | L | – | – |
| `Clientes` | L·I·A·E | L·I | L | – | – |
| `Contactos_Cliente` | L·I·A·E | L·I | L | – | – |
| `Proveedores` | L·I·A·E | – | L·I | L·I | – |
| `Categorias_Costo` | L·I·A·E | L | L | L | – |
| `Tipos_Costo` | L·I·A·E | L | L | L | – |
| `Medios_Pago` | L·I·A·E | – | L | – | – |
| `Configuracion` | L·A | L | L | – | – |
| `Compania` | L·A | L | L | L | – |
| `Metas_KPI` | L·I·A·E | – | L | – | L |
| `Proformas` | – | L·I·A | L | – | – |
| `Proforma_Conceptos` | – | L·I·A·E | – | – | – |
| `Proforma_Planificacion` | – | L·I·A·E | L | L | – |
| `Obras` | – | L·I | L·A | L | L |
| `Asignaciones_Obra` | – | – | L·I·A | L | – |
| `Registro_Horas` | – | – | L·I·A | L·I | – |
| `Gastos_Obra` | – | – | L·I·A | L·I·A | – |
| `Avances_Obra` | – | – | L·I·A | L·I·A | – |
| `Facturas_Obra` | – | – | L·I·A | – | – |
| `Abonos_Obra` | – | – | L·I·A | – | – |
| `Log_Eventos` | – | L·I | L·I | I | – |
| `Alertas` | – | – | L·I·A | – | L·A |
| `Jobs_Control` | – | – | L·I·A | – | L |
| `Snap_Obra_Dia`, `Snap_Costo_Tipo_Semana`, `Snap_Global_Hora`, `Snap_Global_Dia` | – | – | L·I·A·E | – | L |

Notas de la matriz:

1. **`Obras` en OXY Proformas** solo necesita lo que usan la aceptación de la proforma y sus botones de reparación: las altas, y la lectura para saber si la proforma ya tiene obra y cuál es la obra principal de una complementaria. En esa app la tabla se define sin columnas virtuales.
2. **`Obras` en OXY Gestión** lleva las columnas virtuales completas. En OXY Campo y OXY Dashboard, solo las que no dependan de tablas ausentes en esa app.
3. **`Clientes` y `Contactos_Cliente` en OXY Proformas** admiten altas, para crear un cliente al armar una proforma, pero no ediciones ni borrados.
4. **`Proformas` en OXY Gestión** es de solo lectura: las columnas virtuales que apuntan a la proforma (por ejemplo `Gastos_Obra.Proforma_ID`) necesitan la tabla en la app. Gestión también lee `Clientes` por la misma razón.
5. **`Compania`** solo admite *Updates* en OXY Master; no se agregan ni se borran filas.
6. **`Alertas`** se atiende (reconocer y resolver) en OXY Gestión y en OXY Dashboard.
7. **`Log_Eventos`** no lo edita nadie desde una pantalla: lo escriben las acciones auxiliares y los bots.
8. **`Snap_*`** y **`Jobs_Control`** los escriben los procesos programados (los aloja OXY Gestión, DA-07). El mantenimiento de retención usa *Delete row* en un bot, por lo que esas cuatro tablas permiten *Deletes* en OXY Gestión.
9. **Bajas de maestras:** OXY Master puede borrar filas de sus tablas (**E**), salvo `Trabajadores` (se da de baja con `Activo = No`), `Configuracion` y `Compania`, que no admiten borrados (DA-09).
10. **`Tipos_Costo` en OXY Campo:** solo se pueden elegir los de `Visible_Campo = "Si"`; se aplica como `Valid if` de la columna `Tipo_Costo_ID` de la app, no como filtro de seguridad.
11. **Obras de OXY Campo:** las vistas muestran solo las obras asignadas a la persona mediante un slice; es una comodidad de pantalla, no una restricción de datos (5.2).

---

## 7. Reparto de acciones y bots por app

### 7.1 Reglas

1. Una acción pertenece a la app donde se crea y solo aparece en ella.
2. Un bot de cambio de datos solo reacciona a los cambios hechos desde la app en la que existe (⚠ V18). Si una tabla la escriben dos apps, el bot se crea en las dos con la misma configuración.
3. Un bot programado se crea en la app que incluye todas las tablas que lee y escribe, y actúa sobre los datos sin importar quién use la app.
4. Un push solo llega a quien tiene instalada la app donde vive el bot. Un correo llega siempre.
5. Un bot programado que dispara a otro necesita *Trigger other bots* (⚠ V10).

### 7.2 Dónde vive cada componente

| Grupo | Componentes | App |
|---|---|---|
| Proformas | Todas las acciones y bots de proformas (`PRO-A01` a `PRO-A12`, `PRO-B01` a `PRO-B04`), incluido el bot programado de vencimiento | Proformas |
| Creación de la obra | Bot `B_Log_Obra_Creada` (`OBR-B01`), porque la obra se crea desde OXY Proformas | Proformas |
| Operación de la obra | Acciones de estado (`OBR-A01` a `OBR-A07`), auxiliar de atraso (`OBR-A08`) y bots `OBR-B02`, `OBR-B03` y `OBR-B04` | Gestión |
| Gastos | `GAS-A01`, `GAS-B01`, `GAS-B02` y `GAS-B05` | Gestión y Campo |
| Gastos (solo gestión) | `GAS-A02`, `GAS-B03`, `GAS-B04` | Gestión |
| Horas | `HOR-B01` | Gestión y Campo |
| Horas (solo gestión) | `HOR-A01` y `HOR-A02` | Gestión |
| Avances | `AVA-A01` | Gestión y Campo |
| Abonos y cobranza | Todas las de `ABO-*` | Gestión |
| Facturas | Todas las de `FAC-*` | Gestión |
| Alertas: atención | `ALE-A01` y `ALE-A02` | Gestión y Dashboard |
| Alertas: generación y aviso | `ALE-A03` a `ALE-A05` y `ALE-B01` a `ALE-B04` | Gestión |
| Notificaciones del log | `LOG-B01` y `LOG-B02` (solo reaccionan a eventos de procesos programados, que nacen con `Procesado = "No"`) | Gestión |
| Procesos de indicadores | Jobs `J01` a `J11` de la propuesta de Dashboard | Gestión (DA-07) |
| Tablas maestras | Altas y ediciones con las acciones del sistema; no hay acciones ni bots propios en esta versión | Master |

---

## 8. Traspasos entre apps

| N.º | Traspaso | Cómo funciona | Qué debe cumplirse |
|---|---|---|---|
| T1 | Aceptar una proforma y crear su obra | En OXY Proformas, `A_Aceptar` crea la fila de `Obras` y luego cambia el estado de la proforma. La obra se trabaja desde entonces en OXY Gestión | `Obras` con altas en OXY Proformas; `OBR-B01` vive en OXY Proformas; la obra aparece en OXY Gestión cuando esta sincroniza; `Responsable_ID` queda en blanco hasta que un usuario de OXY Gestión lo asigna (DA-03) |
| T2 | Registro de campo | OXY Campo registra gastos, horas y avances; OXY Gestión los ve, aprueba horas y marca pagos | Bots de gastos, horas y avances en las dos apps; los avisos push a `Administracion` y `Supervisor` llegan porque están en la lista de usuarios de OXY Campo (DA-06) |
| T3 | Alertas | Los procesos de OXY Gestión crean las alertas; se atienden en OXY Gestión y en OXY Dashboard | `ALE-A01` y `ALE-A02` en las dos apps |
| T4 | Tablas maestras y catálogos | Se editan solo en OXY Master; las demás apps las leen | El cambio llega a las demás apps cuando estas sincronizan |
| T5 | Indicadores | Los jobs de OXY Gestión escriben `Snap_*`, `Alertas` y `Jobs_Control`; OXY Dashboard los lee | `Jobs_Control.Ultima_Ejecucion` muestra "datos actualizados a las hh:mm" |

Cada app muestra los datos de otra solo después de sincronizar. Un cambio hecho en una app puede tardar en verse en otra; quien necesite verlo de inmediato actualiza la app.

---

## 9. Notificaciones

### 9.1 Destinatarios por rol

`Super` no recibe avisos. Todos los destinatarios se calculan en el momento del envío sobre `Trabajadores` (solo activos). El responsable de una obra recibe su aviso siempre por correo.

| Evento | Destinatarios | Canal |
|---|---|---|
| `GASTO_CREADO` | `Administracion` | Push |
| `GASTO_ANULADO`, `GASTO_SOBRE_PLANIFICADO` | `Administracion`, `Supervisor` | Push y correo |
| `CREDITO_FISCAL_CAMBIADO`, `GASTO_PAGADO`, `HORAS_PENDIENTES` | `Administracion`, `Supervisor` | Push |
| `PROFORMA_ENVIADA`, `PROFORMA_ACEPTADA`, `PROFORMA_RECHAZADA`, `PROFORMA_VENCIDA` | `Administracion`, `Supervisor`, `Planificacion` | Correo |
| `PROFORMA_ANULADA`, `PROFORMA_ELIMINADA` | Ninguno (solo registro) | – |
| `OBRA_CREADA` | Push: `Administracion`, `Supervisor`. Correo: `Operaciones`, `Supervisor` (la obra nace sin responsable) | Push y correo |
| `OBRA_ESTADO_CAMBIADO` | `Administracion`, `Supervisor`, `Operaciones` y el responsable de la obra | Push y correo |
| `OBRA_ATRASADA` | `Administracion`, `Supervisor`, `Operaciones` y el responsable de la obra | Correo |
| `OBRA_CERRADA` | `Administracion`, `Supervisor` | Push |
| `ABONO_CREADO`, `ABONO_ANULADO` | `Administracion`, `Supervisor` | Push y correo |
| `COBRANZA_COMPLETA`, `COBRANZA_REABIERTA` | `Administracion`, `Supervisor` | Correo y push |
| `RECORDATORIO_COBRANZA`, `FACTURA_POR_VENCER` | `Administracion`, `Supervisor` | Correo |
| `FACTURA_VENCIDA` | `Administracion`, `Supervisor` | Correo y push |
| Alertas (todas) | `Administracion`, `Supervisor` | Push |
| Alertas rojas | `Administracion`, `Supervisor` y el responsable de la obra | Correo |

### 9.2 Quién tiene que instalar qué app para recibir push

| Evento con push | Bot que lo envía vive en | Destinatarios que deben tenerla instalada |
|---|---|---|
| Eventos de gastos, horas y avances registrados desde Gestión | OXY Gestión | `Administracion`, `Supervisor` |
| Eventos de gastos y horas registrados desde Campo | OXY Campo | `Administracion`, `Supervisor`: instalar también OXY Campo (DA-06) |
| `OBRA_CREADA` | OXY Proformas | `Administracion`, `Supervisor` (el correo a `Operaciones` y `Supervisor` no requiere app) |
| `OBRA_ESTADO_CAMBIADO`, `OBRA_CERRADA` | OXY Gestión | `Administracion`, `Supervisor`, `Operaciones` |
| Cobranza, facturas y alertas | OXY Gestión | `Administracion`, `Supervisor` |

La cuota diaria de correos de Core es compartida por todos los bots de todas las apps. Un bot en `Monitor` con estado correcto solo prueba que AppSheet ejecutó los pasos, no que el aviso llegó.

---

## 10. Pruebas que cruzan apps

Las pruebas de cada ficha y los escenarios propios de cada app están en su documento. Estas pruebas cubren los traspasos de la sección 8 y se ejecutan con las cuentas de 5.7 y con los datos demo.

| N.º | Escenario | Apps | Pasos | Resultado esperado |
|---|---|---|---|---|
| X1 | Proforma aceptada que crea la obra | Proformas, Gestión | Aceptar una proforma `Enviada` en OXY Proformas. Sincronizar OXY Gestión | La proforma queda `Aceptada`; la obra `Por iniciar` con los totales congelados aparece en OXY Gestión; un evento `OBRA_CREADA`; avisos según 9.1 |
| X2 | Reparación de la aceptación | Proformas | Dejar una `Aceptada` sin obra y una `Enviada` con obra; usar los botones de reparación | La obra se crea o la proforma pasa a `Aceptada`, sin duplicar la obra |
| X3 | Gasto de Campo | Campo, Gestión | Registrar un gasto de Material en OXY Campo. Sincronizar OXY Gestión | El gasto aparece en OXY Gestión; hay un solo evento `GASTO_CREADO`; el aviso push llega a `Administracion` y `Supervisor` con OXY Campo instalada |
| X4 | Horas de Campo | Campo, Gestión | Registrar horas en OXY Campo y aprobarlas en OXY Gestión | La hora queda `Aprobada` con su costo; el total de personal de la obra cambia |
| X5 | Alerta atendida en dos apps | Gestión, Dashboard | Ejecutar un proceso de alertas en OXY Gestión; reconocer una alerta en OXY Gestión y resolver otra en OXY Dashboard | Una alerta por obra y regla; el estado cambia en las dos apps tras sincronizar |
| X6 | Catálogo editado en Master | Master, Proformas, Gestión, Campo | Editar un tipo de costo, un cliente y una tarifa en OXY Master; sincronizar las demás | Cada app ve el cambio; el `Valid if` de tipos de costo de OXY Campo respeta `Visible_Campo` |
| X7 | Baja y cambio de rol | Master y las demás | Cambiar el `Rol` de una cuenta y poner `Activo = No` a otra | La primera ve las acciones de su nuevo rol; la segunda deja de ver acciones en todas las apps |
| X8 | Bot de cambio de datos en dos apps | Gestión, Campo | Alta de gasto desde cada app (prueba de humo S02) | Cada bot reacciona solo a los cambios de su propia app (⚠ V18) |

---

## 11. Decisiones de arquitectura

| ID | Tema | Decisión | Efecto |
|---|---|---|---|
| DA-01 | Dispositivo de cada app | Sin restricción: cada usuario decide cómo abre y visualiza cada app | Las vistas se diseñan para celular y escritorio por igual |
| DA-02 | Clientes y contactos desde OXY Proformas | Solo altas; sin ediciones ni borrados | `Clientes` y `Contactos_Cliente` en L·I en OXY Proformas |
| DA-03 | Responsable de la obra | Lo asigna cualquier usuario con acceso a OXY Gestión (cualquiera de sus roles); ya no se toma de quien creó la proforma | `Obras.Responsable_ID` queda en blanco al crear la obra desde OXY Proformas y se completa en OXY Gestión |
| DA-04 | Bajas de maestras | OXY Master puede borrar filas | **E** en las tablas maestras, salvo `Trabajadores`, `Configuracion` y `Compania`; ver DA-09 |
| DA-05 | `GAS-B05` en OXY Campo | Se incluye `Proforma_Planificacion` en lectura en Campo | La planificación de costos queda visible para todos los usuarios de OXY Campo (ver riesgos) |
| DA-06 | Push de eventos que nacen en OXY Campo | Se agrega a `Administracion` y `Supervisor` a la lista de usuarios de OXY Campo solo para recibir el push | Sus roles no figuran entre los permitidos de OXY Campo, así que no ejecutan acciones allí |
| DA-07 | App que aloja los jobs de indicadores | OXY Gestión | Es la única app con las tablas que los jobs leen |
| DA-08 | Responsable de la obra al crearla | `Obras.Responsable_ID` queda en blanco al crear la obra | Sin valor inicial ni obligatoriedad al crear; si `A_Iniciar` lo exige y quién puede ser elegido queda por definir en la especificación de OXY Gestión |
| DA-09 | Borrado de filas en OXY Master | `Trabajadores` se da de baja con `Activo = No`; `Compania` y `Configuracion` no se borran | Esas tres tablas sin **E**; las demás maestras conservan **E** |


---

## 12. Registro de validaciones

Cada fila es una capacidad o expresión que se prueba en el editor antes de darla por buena. Una marca `⚠ V##` en cualquier documento remite a su fila. Al cerrar una fila se anota la fecha, quién la probó y el resultado; si falla, se aplica la alternativa y se anota. Estado inicial de todas: *Pendiente*.

Orden sugerido: V15 primero (si un rótulo del editor cambia, se corrigen los documentos antes de construir); después V18, V13, V01, V10, V19 y V22 (condicionan todos los bots).

| ID | Qué se valida | Dónde y con qué datos | Resultado esperado | Alternativa si falla | Estado |
|---|---|---|---|---|---|
| V01 | Si un paso de un bot falla, ¿los siguientes se ejecutan? | Bot de prueba con un paso que falla a propósito y un paso posterior | Se conoce el comportamiento; el orden "registrar primero, marcar después" de los bots programados lo tiene en cuenta | Si los pasos posteriores no corren, dejar cada paso en un bot propio encadenado | Pendiente |
| V02 | Un push de un bot *Adds* llega al teléfono de quien tiene la app instalada | Gasto de Campo; cuenta de `Administracion` con OXY Campo instalada | Llega el push | Avisar por correo | Pendiente |
| V03 | El campo *Para* acepta una lista calculada con `SELECT` | Correo de prueba a `Administracion` y `Supervisor` | Llega a todos los `Administracion` y `Supervisor` activos | Un paso por destinatario fijo | Pendiente |
| V04 | `Valid if` con `SELECT` sobre la misma tabla excluyendo la fila actual; `Numero` con `/ : * ? < > \|`, y cómo escribir `\` y `"` en una fórmula | Factura con número repetido; factura que supera el total a cobrar; proforma con `Numero` repetido; `Proforma_Previa_ID` de un `Borrador` nuevo | Rechaza el repetido y el exceso; la lista de previas no incluye a la propia proforma ni a las `Z-Eliminada` | Validar con un slice de detección y revisión diaria | Pendiente |
| V05 | Mensaje de confirmación calculado | Proforma con y sin aviso de margen | El mensaje cambia según la columna | Dos botones con `Only if` distintos | Pendiente |
| V06 | *Create a new file* en Core con plantilla de Google Docs; nombre `<Numero>_<Sello>` con *Disable timestamp*; marcas de tabla relacionada y `TEXT(...)` | Pulsar *Generar PDF* dos veces | Dos PDF `Proformas_Files/<Numero>_<Sello>.pdf`; `Doc_Proforma` apunta al último | Plantilla HTML o PDF manual | Pendiente |
| V07 | `[_THISROW_BEFORE]` y `[_THISROW_AFTER]` en condiciones *Updates* | Anular un gasto; cambiar `Es_Credito_Fiscal` | Solo se dispara con el cambio buscado | Un bot por tabla con la condición solo sobre el valor nuevo | Pendiente |
| V08 | `Valid if` de `Es_Credito_Fiscal` | Gasto con boleta marcado como crédito | Lo rechaza | Mensaje de aviso sin bloqueo | Pendiente |
| V09 | Valor inicial aplicado en una columna oculta | Gasto de Campo | `Es_Credito_Fiscal` se guarda con su valor inicial | Poblarlo con un bot de alta | Pendiente |
| V10 | *Trigger other bots* encadena el bot programado con LOG-B01, LOG-B02 y ALE-B04 | Ejecutar ABO-B03 | Llega el aviso del bot de notificación | Que el bot programado envíe él mismo el correo | Pendiente |
| V11 | Nombre exacto de la columna inversa `Related ...` | Plantilla del PDF | El PDF lista los conceptos | Ajustar la marca de la plantilla al nombre real | Pendiente |
| V12 | Duración `"024:00:00"` en `Only if` | Gasto de Campo de menos y de más de 24 horas | Anula solo dentro de 24 horas | `(NOW()-[Creado_En])*24<24` o `HOUR` | Pendiente |
| V13 | Bots programados disponibles en Core y ejecutables a mano | Bot diario y semanal de prueba | Se ejecutan y aparecen en `Monitor` | Disparar los procesos desde una acción manual diaria | Pendiente |
| V14 | Texto del push con expresiones `<<...>>` | Push de prueba | El texto sale con los valores | Texto fijo | Pendiente |
| V15 | Rutas y rótulos del editor nuevo: crear acciones, `Set these columns`, `Table to add rows to`, `Data change type` y lista de usuarios | Recorrer el editor una vez | Se anotan las rutas reales y se corrigen los documentos | — | Pendiente |
| V16 | *Security filter* con `SELECT` y `LOOKUP` anidados | — | — | — | No aplica en esta versión (no se usan filtros de seguridad; ver `Pendientes`) |
| V17 | Cuenta que está en la lista de usuarios de una app pero no en `Trabajadores` | Cuenta ajena en OXY Campo y en OXY Gestión | Abre la app y lee datos (riesgo aceptado), pero ninguna acción le aparece | Quitarla de la lista | Pendiente |
| V18 | Un bot de cambio de datos reacciona solo a los cambios hechos desde su app | Alta de gasto desde cada app | Cada bot reacciona a su app | Duplicar el bot en la otra app (ya previsto) | Confirmado por el propietario; verificar en la primera prueba |
| V19 | *Set row values* sobre un conjunto de filas desde un bot programado | `PRO-B01` | Cambia el estado de todas las filas del conjunto | Una acción auxiliar por fila con *Execute an action on a set of rows* | Pendiente |
| V20 | `LOOKUP` a `Metas_KPI` dentro de acciones y conjuntos de bots programados | `ALE-B01` | La severidad cambia al cambiar el umbral | Guardar los umbrales también en `Configuracion` | Pendiente |
| V21 | *Add row* con clave calculada como texto | `A_Log_Obra_Atrasada` | La fila queda con el `Evento_ID` calculado | `UNIQUEID()` y una columna de apoyo para la guarda | Pendiente |
| V22 | Paso condicional en un bot | `ALE-B04` con alerta ámbar y roja | El correo solo sale con la roja | Segundo bot con la condición en el evento | Pendiente |
| V23 | Columna virtual de tipo File (`Doc_Oficial`) se abre desde la app | Proforma con y sin personalizado | Abre el personalizado si existe; si no, el PDF | Dos columnas con `Show?` condicional | Pendiente |
| V24 | `LOOKUP` con clave fija (`"OXY"`) sobre la tabla de una fila `Compania`, desde una columna virtual, una condición de paso y el campo *To* de un bot; `Compania` con solo *Updates* | PDF de una proforma; `LOG-B01` con `Emails_Cobranza` lleno y vacío | Los datos salen en el PDF; el correo sale solo con `Emails_Cobranza` lleno | Dejar los datos de OXY como parámetros en una tabla de claves de texto | Pendiente |
| V25 | Columna *Ref* cuya tabla destino no está en la app (p. ej. `Obras.Responsable_ID`, `Proformas.Cliente_ID` en apps sin esa tabla) | Abrir cada app con la tabla destino ausente | La app abre y la columna se comporta como texto | Definir la columna como *Text* en esa app | Pendiente |
| V26 | Valor inicial `"PRF-"&UNIQUEID()` de `Proforma_ID` | Crear una proforma | La clave queda como `PRF-<id>` y es única | Usar `UNIQUEID()` solo | Pendiente |
| V27 | Bloqueo de líneas de una proforma según su estado | Editar un concepto y una línea de planificación en `Borrador`, `Enviada` y `Aceptada`; borrarlos en `Borrador` y en `Enviada` | Edita en `Borrador` y `Enviada`, no en `Aceptada`; borra solo en `Borrador` | Agregar la condición de estado al `Only if` de *Add* y *Edit* de esas tablas | Pendiente |
| V28 | `A_Aceptar_CrearObra` agrega la fila aunque la acción de sistema *Add* de `Obras` tenga `Only if` = `FALSE` | Aceptar una proforma | Se crea la obra | Dejar *Add* de `Obras` sin condición y no exponer vistas de `Obras` con botón de alta | Pendiente |
| V29 | Alta de líneas nuevas según el estado de la proforma (y `Doc_Proforma_Personalizado` / `A_Generar_PDF` en `Enviada`) | Agregar un concepto y una línea de planificación en `Borrador`, `Enviada` y `Aceptada`; en una `Enviada`, generar el PDF y subir el personalizado | Agrega en `Borrador` y `Enviada`; en `Aceptada` no se puede guardar; el PDF y el personalizado funcionan en `Enviada` y no en `Aceptada` | Agregar la condición de estado al `Only if` de *Add* de esas tablas | Pendiente |
