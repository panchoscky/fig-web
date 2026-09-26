/* ============================================================================
   Apps Script COMPARTIDO de FIG — versión 2 (2026-09-25): agrega el login de
   directivos y las publicaciones en vivo.

   Se pega ENTERO en script.google.com (la planilla del sitio → Extensiones →
   Apps Script), reemplazando lo que haya. Mantiene los 3 usos viejos tal cual
   (postulaciones, ranking de El Rally del Toro, visitas) y suma:

     POST login           usuario + clave  → token de 30 días
     POST yo              token            → quién soy (la app lo usa al abrir)
     POST publicar        token + evento/comunicado (+ hasta 4 fotos)
     POST listar          token            → publicaciones de mi área, incluso ocultas
     POST visibilidad     token + id + visible
     POST tabla_trading   token + tabla del Alpha Trading Challenge (solo TRD)
     POST cambiar_clave   token + clave actual + clave nueva
     GET  ?tipo=publicaciones   lo visible, para el sitio y la app pública
     GET  ?tipo=tabla_trading   la última tabla de Trading subida

   EL CANDADO ESTÁ ACÁ, NO EN LAS APPS. Las apps son páginas públicas: lo que
   impide que un desconocido publique es que este script exige un token
   firmado, y ese token solo se entrega con usuario + clave correctos. El
   ÁREA de cada publicación la pone este script según el usuario — nunca la
   que mande la app.

   Los secretos NO están en este archivo (que vive en un repo público): están
   en Configuración del proyecto → Propiedades de la secuencia de comandos,
   y los genera `crear_usuarios_directivos.py` en el PC de Francisco:
     FIG_USUARIOS   JSON con cada usuario: nombre, área, correo, sal y hash
                    de la clave (la clave en sí no se guarda en ningún lado)
     FIG_PIMIENTA   secreto con que se calculan los hash
     FIG_SECRETO    secreto con que se firman los tokens
   Sacar a alguien = borrar su entrada de FIG_USUARIOS (su token deja de
   servir al tiro). Cerrar la sesión de TODOS = cambiar FIG_SECRETO.

   Las pestañas nuevas (Publicaciones, TablaTrading, Registro) las crea el
   script solo la primera vez que las necesita, con sus encabezados.
   Para ocultar algo a mano: columna `visible` de Publicaciones → FALSE.
   ========================================================================== */

var DIAS_TOKEN = 30;
var MAX_FOTOS = 4;
var MAX_FALLOS = 5;          // intentos de clave antes de bloquear...
var BLOQUEO_SEG = 15 * 60;   // ...por 15 minutos
var AREAS = ["PRT", "TRD", "VAL", "FIW", "ADM"];

var COLS_PUB = ["id", "fecha", "clase", "area", "usuario", "autor", "titulo",
                "fechaEvento", "lugar", "texto", "fotos", "visible"];


/* ---------------------------------------------------------------- entrada */

function doPost(e) {
  var d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return json_({ ok: false, error: "pedido ilegible" }); }
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // --- los 3 usos viejos del sitio, sin cambios (responden "OK" en texto) ---
  if (d.tipo === "postulacion") {
    ss.getSheetByName("Postulaciones").appendRow(
      [d.fecha, d.nombre, d.correo, d.carrera, d.anio, d.area, d.motivacion, d.linkedin]);
    return ContentService.createTextOutput("OK");
  }
  if (d.tipo === "rally") {
    ss.getSheetByName("Ranking").appendRow([d.fecha, d.nombre, d.valor]);
    return ContentService.createTextOutput("OK");
  }
  if (d.tipo === "visita") {
    ss.getSheetByName("Visitas").appendRow([d.fecha, d.pagina, d.origen]);
    return ContentService.createTextOutput("OK");
  }

  // --- directivos ---
  try {
    if (d.tipo === "login") return json_(login_(d));
    var u = usuarioDelToken_(d.token);
    if (!u) return json_({ ok: false, error: "sesion", mensaje: "Tu sesión venció o ya no tienes acceso. Vuelve a entrar." });
    if (d.tipo === "yo") return json_({ ok: true, usuario: publico_(u) });
    if (d.tipo === "publicar") return json_(publicar_(u, d));
    if (d.tipo === "listar") return json_(listar_(u));
    if (d.tipo === "visibilidad") return json_(visibilidad_(u, d));
    if (d.tipo === "tabla_trading") return json_(tablaTrading_(u, d));
    if (d.tipo === "cambiar_clave") return json_(cambiarClave_(u, d));
    return json_({ ok: false, error: "tipo desconocido" });
  } catch (err) {
    registrar_("?", "error", String(err));
    return json_({ ok: false, error: "interno", mensaje: "Algo falló en el servidor: " + err });
  }
}

function doGet(e) {
  var tipo = e.parameter && e.parameter.tipo;
  if (tipo === "rally") {
    var top = parseInt(e.parameter.top || "10", 10);
    var hoja = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Ranking");
    var filas = hoja.getDataRange().getValues().slice(1); // sin encabezado
    var scores = filas.map(function(f) {
      return { fecha: f[0], nombre: f[1], valor: f[2] };
    });
    scores.sort(function(a, b) { return b.valor - a.valor; });
    scores = scores.slice(0, top);
    return ContentService.createTextOutput(JSON.stringify(scores))
      .setMimeType(ContentService.MimeType.JSON);
  }
  if (tipo === "publicaciones") {
    return jsonCacheado_("publicaciones", function() {
      return publicaciones_().filter(function(p) { return p.visible; }).map(sinInterno_);
    });
  }
  if (tipo === "tabla_trading") {
    return jsonCacheado_("tabla_trading", ultimaTablaTrading_);
  }
  return ContentService.createTextOutput("Endpoint FIG activo");
}


/* ------------------------------------------------------------------ login */

function login_(d) {
  var id = normalizar_(d.usuario);
  var cache = CacheService.getScriptCache();
  var claveFallos = "fallos_" + id;
  var fallos = parseInt(cache.get(claveFallos) || "0", 10);
  if (fallos >= MAX_FALLOS) {
    registrar_(id, "login bloqueado", "");
    return { ok: false, error: "bloqueado", mensaje: "Demasiados intentos. Espera 15 minutos." };
  }
  var u = usuarios_()[id];
  if (!u || hashClave_(u.s, String(d.clave || "")) !== u.h) {
    cache.put(claveFallos, String(fallos + 1), BLOQUEO_SEG);
    registrar_(id, "login fallido", "");
    return { ok: false, error: "credenciales", mensaje: "Usuario o clave incorrectos." };
  }
  cache.remove(claveFallos);
  u.id = id;
  var exp = Date.now() + DIAS_TOKEN * 864e5;
  var cuerpo = id + "|" + (u.v || 1) + "|" + exp;
  registrar_(id, "login", "");
  return { ok: true, token: cuerpo + "|" + firma_(cuerpo), exp: exp, usuario: publico_(u) };
}

function usuarioDelToken_(token) {
  var p = String(token || "").split("|");
  if (p.length !== 4) return null;
  var cuerpo = p[0] + "|" + p[1] + "|" + p[2];
  if (firma_(cuerpo) !== p[3]) return null;
  if (Number(p[2]) < Date.now()) return null;
  var u = usuarios_()[p[0]];
  if (!u || String(u.v || 1) !== p[1]) return null;   // borrado, o cambió la clave
  u.id = p[0];
  return u;
}

function cambiarClave_(u, d) {
  var nueva = String(d.nueva || "");
  if (nueva.length < 8) return { ok: false, mensaje: "La clave nueva debe tener al menos 8 caracteres." };
  if (hashClave_(u.s, String(d.actual || "")) !== u.h) return { ok: false, mensaje: "La clave actual no es correcta." };
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var todos = usuarios_();
    var r = todos[u.id];
    r.s = Utilities.getUuid().replace(/-/g, "");
    r.h = hashClave_(r.s, nueva);
    r.v = (r.v || 1) + 1;                               // invalida los tokens viejos
    PropertiesService.getScriptProperties().setProperty("FIG_USUARIOS", JSON.stringify(todos));
  } finally { lock.releaseLock(); }
  registrar_(u.id, "cambio de clave", "");
  return { ok: true, mensaje: "Clave cambiada. Vuelve a entrar con la nueva." };
}


/* ---------------------------------------------------------- publicaciones */

function publicar_(u, d) {
  var clase = d.clase === "comunicado" ? "comunicado" : "evento";
  var titulo = limpiar_(d.titulo, 120);
  var texto = limpiar_(d.texto, 1500);
  if (!titulo) return { ok: false, mensaje: "Falta el título." };
  if (clase === "evento" && !/^\d{4}-\d{2}-\d{2}$/.test(String(d.fechaEvento || "")))
    return { ok: false, mensaje: "Falta la fecha del evento." };
  // El área la decide el usuario, no la app. Solo un admin elige otra.
  var area = u.a;
  if (u.admin && AREAS.indexOf(d.area) >= 0) area = d.area;

  var fotos = [];
  (d.fotos || []).slice(0, MAX_FOTOS).forEach(function(f, i) {
    if (!f || !f.b64) return;
    var blob = Utilities.newBlob(Utilities.base64Decode(f.b64), "image/jpeg",
      area + "-" + titulo.slice(0, 40) + "-" + (i + 1) + ".jpg");
    var archivo = carpetaFotos_().createFile(blob);
    archivo.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
    fotos.push(archivo.getId());
  });

  var id = Utilities.formatDate(new Date(), "America/Santiago", "yyyyMMdd-HHmmss") + "-" + u.id;
  hoja_("Publicaciones", COLS_PUB).appendRow([
    id, new Date().toISOString(), clase, area, u.id, u.n, titulo,
    clase === "evento" ? d.fechaEvento : "", limpiar_(d.lugar, 120), texto,
    JSON.stringify(fotos), true
  ]);
  CacheService.getScriptCache().remove("publicaciones");
  registrar_(u.id, "publicar " + clase, id + " · " + titulo);
  return { ok: true, id: id };
}

function listar_(u) {
  var todas = publicaciones_().filter(function(p) { return u.admin || p.area === u.a; });
  return { ok: true, publicaciones: todas.map(sinInterno_) };
}

function visibilidad_(u, d) {
  var hoja = hoja_("Publicaciones", COLS_PUB);
  var datos = hoja.getDataRange().getValues();
  for (var i = 1; i < datos.length; i++) {
    if (String(datos[i][0]) !== String(d.id)) continue;
    if (!u.admin && datos[i][3] !== u.a) return { ok: false, mensaje: "Esa publicación es de otra área." };
    hoja.getRange(i + 1, COLS_PUB.indexOf("visible") + 1).setValue(!!d.visible);
    CacheService.getScriptCache().remove("publicaciones");
    registrar_(u.id, d.visible ? "mostrar" : "ocultar", d.id);
    return { ok: true };
  }
  return { ok: false, mensaje: "No encontré esa publicación." };
}

function publicaciones_() {
  var hoja = hoja_("Publicaciones", COLS_PUB);
  var filas = hoja.getDataRange().getValues().slice(1);
  var tz = "America/Santiago";
  return filas.filter(function(f) { return f[0]; }).map(function(f) {
    var o = {};
    COLS_PUB.forEach(function(c, i) { o[c] = f[i]; });
    // Sheets convierte "2026-10-11" en fecha: se devuelve siempre como texto.
    if (o.fechaEvento instanceof Date) o.fechaEvento = Utilities.formatDate(o.fechaEvento, tz, "yyyy-MM-dd");
    if (o.fecha instanceof Date) o.fecha = o.fecha.toISOString();
    try { o.fotos = JSON.parse(o.fotos || "[]"); } catch (err) { o.fotos = []; }
    o.visible = o.visible === true || String(o.visible).toUpperCase() === "TRUE";
    return o;
  }).reverse();   // lo más nuevo primero
}

function sinInterno_(p) {
  return { id: p.id, fecha: p.fecha, clase: p.clase, area: p.area, autor: p.autor,
           titulo: p.titulo, fechaEvento: p.fechaEvento, lugar: p.lugar, texto: p.texto,
           fotos: p.fotos, visible: p.visible };
}


/* ---------------------------------------------------------- tabla Trading */

function tablaTrading_(u, d) {
  if (!u.admin && u.a !== "TRD") return { ok: false, mensaje: "Solo el área Trading sube esta tabla." };
  var columnas = (d.columnas || []).map(function(c) { return limpiar_(c, 40); });
  var filas = (d.filas || []).slice(0, 500).map(function(f) {
    return (f || []).slice(0, columnas.length).map(function(c) { return limpiar_(c, 80); });
  });
  if (!columnas.length || !filas.length) return { ok: false, mensaje: "La tabla viene vacía." };
  hoja_("TablaTrading", ["fecha", "usuario", "titulo", "tabla"]).appendRow([
    new Date().toISOString(), u.id, limpiar_(d.titulo, 120),
    JSON.stringify({ columnas: columnas, filas: filas })
  ]);
  CacheService.getScriptCache().remove("tabla_trading");
  registrar_(u.id, "tabla trading", filas.length + " filas");
  return { ok: true, filas: filas.length };
}

function ultimaTablaTrading_() {
  var filas = hoja_("TablaTrading", ["fecha", "usuario", "titulo", "tabla"]).getDataRange().getValues();
  if (filas.length < 2) return null;
  var f = filas[filas.length - 1];
  var t = JSON.parse(f[3]);
  return { fecha: f[0] instanceof Date ? f[0].toISOString() : f[0], titulo: f[2],
           columnas: t.columnas, filas: t.filas };
}


/* ---------------------------------------------------------------- apoyo */

function usuarios_() {
  var raw = PropertiesService.getScriptProperties().getProperty("FIG_USUARIOS");
  return raw ? JSON.parse(raw) : {};
}

function publico_(u) {
  return { id: u.id, nombre: u.n, area: u.a, admin: !!u.admin };
}

// "prt-fva", "PRT FVA" y "PRTFVA" son el mismo usuario.
function normalizar_(s) {
  return String(s || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
}

function secreto_(nombre) {
  var v = PropertiesService.getScriptProperties().getProperty(nombre);
  if (!v) throw new Error("falta la propiedad " + nombre + " (ver crear_usuarios_directivos.py)");
  return v;
}

function hex_(bytes) {
  return bytes.map(function(b) { return ("0" + ((b + 256) % 256).toString(16)).slice(-2); }).join("");
}

// Mismo cálculo que crear_usuarios_directivos.py: HMAC-SHA256(pimienta, sal + ":" + clave).
function hashClave_(sal, clave) {
  return hex_(Utilities.computeHmacSha256Signature(sal + ":" + clave, secreto_("FIG_PIMIENTA"),
    Utilities.Charset.UTF_8));
}

function firma_(texto) {
  return hex_(Utilities.computeHmacSha256Signature(texto, secreto_("FIG_SECRETO"),
    Utilities.Charset.UTF_8));
}

function limpiar_(s, max) {
  return String(s == null ? "" : s).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}

function hoja_(nombre, encabezados) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var h = ss.getSheetByName(nombre);
  if (!h) {
    h = ss.insertSheet(nombre);
    h.appendRow(encabezados);
    h.setFrozenRows(1);
  }
  return h;
}

function carpetaFotos_() {
  var nombre = "FIG - Fotos Directivos";
  var carpetas = DriveApp.getFoldersByName(nombre);
  return carpetas.hasNext() ? carpetas.next() : DriveApp.createFolder(nombre);
}

function registrar_(usuario, accion, detalle) {
  try {
    hoja_("Registro", ["fecha", "usuario", "accion", "detalle"])
      .appendRow([new Date().toISOString(), usuario, accion, String(detalle).slice(0, 300)]);
  } catch (err) { /* el registro nunca tumba un pedido */ }
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// Las lecturas públicas se guardan 60 s: el sitio las pide en cada visita y
// Sheets es lento. Cada escritura borra su entrada, así que lo nuevo se ve al tiro.
function jsonCacheado_(clave, calcular) {
  var cache = CacheService.getScriptCache();
  var hit = cache.get(clave);
  if (hit) return ContentService.createTextOutput(hit).setMimeType(ContentService.MimeType.JSON);
  var txt = JSON.stringify(calcular());
  if (txt.length < 90000) cache.put(clave, txt, 60);
  return ContentService.createTextOutput(txt).setMimeType(ContentService.MimeType.JSON);
}

/* Para probar desde el editor (▶ Ejecutar) que las propiedades quedaron bien:
   muestra cuántos usuarios hay y por área, sin mostrar ningún hash. */
function revisarConfiguracion() {
  var us = usuarios_();
  var porArea = {};
  Object.keys(us).forEach(function(k) { porArea[us[k].a] = (porArea[us[k].a] || 0) + 1; });
  secreto_("FIG_PIMIENTA"); secreto_("FIG_SECRETO");
  Logger.log(Object.keys(us).length + " usuarios · " + JSON.stringify(porArea));
  carpetaFotos_();   // de paso pide el permiso de Drive la primera vez
}
