/* FIG Directivos — la app de cada área (una sola base para las 5).
 *
 * La carcasa de cada área (directivos/<carpeta>/index.html, la genera
 * generar_apps_directivos.py) solo pone el color y window.FIG_AREA; todo lo
 * demás vive acá.
 *
 * Esta página es pública: cualquiera puede abrirla. Lo que impide publicar
 * sin permiso es el Apps Script (apps_script/Codigo.gs), que exige un token
 * firmado y pone él mismo el área de cada publicación. Acá solo se guarda el
 * token en el teléfono, nunca la clave.
 */
"use strict";
(function () {
  var AREA = window.FIG_AREA;                 // {codigo, nombre, carpeta}
  var AREAS = window.FIG_AREAS || {};          // codigo -> {nombre, carpeta}
  var CLAVE_TOKEN = "figDirToken";
  var ENDPOINT = "";
  var yo = null;
  var app = document.getElementById("app");

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function leerToken() { try { return localStorage.getItem(CLAVE_TOKEN) || ""; } catch (e) { return ""; } }
  function guardarToken(t) { try { t ? localStorage.setItem(CLAVE_TOKEN, t) : localStorage.removeItem(CLAVE_TOKEN); } catch (e) {} }
  function fotoUrl(id, ancho) { return "https://drive.google.com/thumbnail?id=" + encodeURIComponent(id) + "&sz=w" + (ancho || 400); }
  function fechaBonita(iso) {
    if (!iso) return "";
    var p = String(iso).slice(0, 10).split("-");
    var m = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"][+p[1] - 1];
    return m ? (+p[2]) + " " + m + " " + p[0] : iso;
  }

  /* --- servidor --- */
  function pedir(datos) {
    if (!ENDPOINT) return Promise.reject(new Error("el sitio no tiene configurado el endpoint"));
    datos.token = datos.token || leerToken();
    // text/plain = pedido "simple": el Apps Script no acepta el preflight CORS de application/json.
    return fetch(ENDPOINT, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(datos) })
      .then(function (res) {
        return res.text().then(function (t) {
          try { return JSON.parse(t); } catch (e) {
            // Google respondió una página de error en vez de datos: mostrar su título, que dice qué pasó.
            var titulo = (t.match(/<title>([^<]*)<\/title>/i) || [])[1] || "";
            var detalle = (t.replace(/<style[\s\S]*?<\/style>|<script[\s\S]*?<\/script>/gi, " ").replace(/<[^>]+>/g, " ")
              .replace(/\s+/g, " ").trim()).slice(0, 220);
            throw new Error("Google respondió con un error (HTTP " + res.status + "): " + (titulo ? titulo + " — " : "") + detalle);
          }
        });
      })
      .then(function (r) {
        if (r.error === "sesion") { guardarToken(""); yo = null; pantallaEntrada(r.mensaje); throw new Error(r.mensaje); }
        return r;
      });
  }

  /* --- entrada --- */
  function pantallaEntrada(aviso) {
    app.innerHTML =
      '<div class="entrada">' +
      '<div class="logo"><img src="../../logos/fig-blanco.png" alt=""></div>' +
      '<h1>FIG Directivos</h1><p class="sub">' + esc(AREA.nombre) + '</p>' +
      '<form id="fEntrar" autocomplete="on">' +
      '<label>Usuario<input name="usuario" required autocapitalize="characters" autocomplete="username" placeholder="' + esc(AREA.codigo) + '-XXX"></label>' +
      '<label>Clave<input name="clave" type="password" required autocomplete="current-password"></label>' +
      '<button class="btn" type="submit">Entrar</button>' +
      '<p class="msg err" id="mEntrar"' + (aviso ? "" : " hidden") + '>' + esc(aviso || "") + '</p>' +
      '</form><p class="pie">Tu usuario es el código de tu área + tus 3 letras de la página de Miembros.</p></div>';
    $("#fEntrar").addEventListener("submit", function (e) {
      e.preventDefault();
      var f = e.target, btn = $(".btn", f), m = $("#mEntrar");
      btn.disabled = true; m.hidden = true;
      pedir({ tipo: "login", usuario: f.usuario.value, clave: f.clave.value, token: "-" })
        .then(function (r) {
          if (!r.ok) throw new Error(r.mensaje || "No se pudo entrar.");
          guardarToken(r.token); yo = r.usuario; pantallaPrincipal();
        })
        .catch(function (err) { m.hidden = false; m.textContent = err.message; })
        .then(function () { btn.disabled = false; });
    });
  }

  /* --- principal --- */
  var ICONOS = {
    publicar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
    lista: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>',
    tabla: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M9 4v16"/></svg>',
    cuenta: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/></svg>'
  };

  function pantallaPrincipal() {
    var ajena = yo.area !== AREA.codigo && !yo.admin;
    var tabs = [["publicar", "Publicar"], ["lista", "Publicadas"]];
    if (yo.area === "TRD" || yo.admin) tabs.push(["tabla", "Tabla Trading"]);
    tabs.push(["cuenta", "Cuenta"]);
    app.innerHTML =
      '<header class="barra"><img src="../../logos/fig-blanco.png" alt=""><div class="t"><b>FIG Directivos · ' + esc(AREA.nombre) + '</b>' +
      '<small>' + esc(yo.nombre) + ' · ' + esc(yo.id) + (yo.admin ? " · admin" : "") + '</small></div></header>' +
      '<main id="vista"></main>' +
      '<nav class="pestanas" role="tablist">' + tabs.map(function (t) {
        return '<button role="tab" data-t="' + t[0] + '" aria-selected="false">' + ICONOS[t[0]] + t[1] + '</button>';
      }).join("") + '</nav>';
    $$(".pestanas button").forEach(function (b) { b.addEventListener("click", function () { ir(b.dataset.t); }); });
    if (ajena) {
      var otra = AREAS[yo.area] || {};
      $("#vista").innerHTML = '<div class="card"><h3>Esta app es la de ' + esc(AREA.nombre) + '</h3>' +
        '<p>Tu usuario es de ' + esc(otra.nombre || yo.area) + '. Instala la app de tu área para publicar:</p>' +
        '<div class="fila"><a class="btn chico" href="../' + esc(otra.carpeta || "") + '/">Abrir FIG Directivos · ' + esc(otra.nombre || yo.area) + '</a>' +
        '<button class="btn sec chico" id="bSalir">Salir</button></div></div>';
      $(".pestanas").hidden = true;
      $("#bSalir").onclick = salir;
      return;
    }
    ir("publicar");
  }

  function ir(t) {
    $$(".pestanas button").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.t === t ? "true" : "false"); });
    ({ publicar: vistaPublicar, lista: vistaLista, tabla: vistaTabla, cuenta: vistaCuenta })[t]();
    scrollTo(0, 0);
  }

  /* --- publicar --- */
  var fotos = [];   // [{b64, url}]
  function vistaPublicar() {
    fotos = [];
    var selArea = yo.admin ? '<label>Área<select name="area">' + Object.keys(AREAS).map(function (c) {
      return '<option value="' + c + '"' + (c === AREA.codigo ? " selected" : "") + '>' + esc(AREAS[c].nombre) + '</option>';
    }).join("") + '</select></label>' : "";
    $("#vista").innerHTML =
      '<h2>Publicar</h2><p class="sub">Sale al tiro en el sitio y en la app pública, con la etiqueta de ' + esc(AREA.nombre) + '.</p>' +
      '<form id="fPub">' +
      '<div class="seg" role="group"><button type="button" data-c="evento" aria-pressed="true">Evento</button>' +
      '<button type="button" data-c="comunicado" aria-pressed="false">Comunicado</button></div>' +
      selArea +
      '<label>Título<input name="titulo" required maxlength="120"></label>' +
      '<label class="soloEvento">Fecha del evento<input name="fechaEvento" type="date" required></label>' +
      '<label class="soloEvento"><span class="rot">Lugar <span class="opc">(opcional)</span></span><input name="lugar" maxlength="120"></label>' +
      '<label><span id="lTexto">Descripción</span><textarea name="texto" required maxlength="1500"></textarea></label>' +
      '<label><span class="rot">Fotos <span class="opc">(hasta 4, opcional)</span></span></label>' +
      '<div class="fotos" id="fotos"></div><input type="file" id="iFoto" accept="image/*" multiple hidden>' +
      '<button class="btn" type="submit">Publicar</button><p class="msg" id="mPub" hidden></p></form>';
    var clase = "evento", f = $("#fPub");
    $$(".seg button", f).forEach(function (b) {
      b.onclick = function () {
        clase = b.dataset.c;
        $$(".seg button", f).forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        $$(".soloEvento", f).forEach(function (el) { el.hidden = clase !== "evento"; });
        f.fechaEvento.required = clase === "evento";
        $("#lTexto").textContent = clase === "evento" ? "Descripción" : "Texto del comunicado";
      };
    });
    pintarFotos();
    $("#iFoto").addEventListener("change", function (e) {
      var nuevos = [].slice.call(e.target.files, 0, 4 - fotos.length);
      e.target.value = "";
      Promise.all(nuevos.map(comprimir)).then(function (lst) {
        lst.forEach(function (x) { if (x) fotos.push(x); });
        pintarFotos();
      });
    });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = $(".btn", f), m = $("#mPub");
      btn.disabled = true; m.hidden = true; btn.textContent = "Publicando…";
      pedir({
        tipo: "publicar", clase: clase, area: f.area ? f.area.value : AREA.codigo,
        titulo: f.titulo.value, fechaEvento: f.fechaEvento.value, lugar: f.lugar.value, texto: f.texto.value,
        fotos: fotos.map(function (x) { return { b64: x.b64 }; })
      }).then(function (r) {
        if (!r.ok) throw new Error(r.mensaje || "No se pudo publicar.");
        f.reset(); fotos = []; pintarFotos();
        m.className = "msg ok"; m.textContent = "Publicado. Ya se ve en el sitio y en la app de FIG.";
      }).catch(function (err) {
        m.className = "msg err"; m.textContent = err.message;
      }).then(function () { m.hidden = false; btn.disabled = false; btn.textContent = "Publicar"; });
    });
  }
  function pintarFotos() {
    var c = $("#fotos");
    if (!c) return;
    c.innerHTML = fotos.map(function (x, i) {
      return '<div class="f"><img src="' + x.url + '" alt=""><button type="button" data-i="' + i + '" aria-label="Quitar">×</button></div>';
    }).join("") + (fotos.length < 4 ? '<button type="button" class="mas" aria-label="Agregar foto">+</button>' : "");
    $$(".f button", c).forEach(function (b) { b.onclick = function () { fotos.splice(+b.dataset.i, 1); pintarFotos(); }; });
    var mas = $(".mas", c);
    if (mas) mas.onclick = function () { $("#iFoto").click(); };
  }
  // Máx. 1600 px, JPEG 0.75: una foto de teléfono (3-5 MB) queda en ~250 KB.
  function comprimir(archivo) {
    return new Promise(function (resolve) {
      var img = new Image(), url = URL.createObjectURL(archivo);
      img.onerror = function () { resolve(null); };
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight, k = Math.min(1, max / Math.max(w, h));
        var cv = document.createElement("canvas");
        cv.width = Math.round(w * k); cv.height = Math.round(h * k);
        cv.getContext("2d").drawImage(img, 0, 0, cv.width, cv.height);
        var dataUrl = cv.toDataURL("image/jpeg", 0.75);
        resolve({ b64: dataUrl.split(",")[1], url: dataUrl });
      };
      img.src = url;
    });
  }

  /* --- lo publicado --- */
  function vistaLista() {
    $("#vista").innerHTML = '<h2>Publicadas</h2><p class="sub">' + (yo.admin ? "Todas las áreas." : "Lo de " + esc(AREA.nombre) + ".") +
      ' Ocultar lo saca del sitio y de la app al tiro; no se borra.</p><div id="lst"><p class="vacio">Cargando…</p></div>';
    pedir({ tipo: "listar" }).then(function (r) {
      var l = r.publicaciones || [];
      if (!l.length) { $("#lst").innerHTML = '<p class="vacio">Todavía no hay nada publicado.</p>'; return; }
      $("#lst").innerHTML = l.map(function (p) {
        return '<div class="card' + (p.visible ? "" : " oculta") + '">' +
          '<div class="meta"><span class="chip area">' + esc(p.area) + '</span><span class="chip">' + esc(p.clase) + '</span>' +
          (p.visible ? "" : '<span class="chip">oculta</span>') + '</div>' +
          '<h3>' + esc(p.titulo) + '</h3><div class="meta">' + (p.fechaEvento ? esc(fechaBonita(p.fechaEvento)) + " · " : "") +
          esc(p.lugar || "") + (p.lugar ? " · " : "") + 'por ' + esc(p.autor) + '</div><p>' + esc(p.texto) + '</p>' +
          (p.fotos && p.fotos.length ? '<div class="mini">' + p.fotos.map(function (id) { return '<img src="' + fotoUrl(id, 160) + '" alt="" loading="lazy">'; }).join("") + '</div>' : "") +
          '<div class="fila"><span class="meta">' + esc(fechaBonita(p.fecha)) + '</span>' +
          '<button class="btn sec chico" data-id="' + esc(p.id) + '" data-v="' + (p.visible ? "0" : "1") + '">' + (p.visible ? "Ocultar" : "Mostrar") + '</button></div></div>';
      }).join("");
      $$("#lst button[data-id]").forEach(function (b) {
        b.onclick = function () {
          b.disabled = true;
          pedir({ tipo: "visibilidad", id: b.dataset.id, visible: b.dataset.v === "1" })
            .then(function (r) { if (!r.ok) throw new Error(r.mensaje); vistaLista(); })
            .catch(function (err) { b.disabled = false; alertaSuave(err.message); });
        };
      });
    }).catch(function (err) { $("#lst").innerHTML = '<p class="vacio">' + esc(err.message) + '</p>'; });
  }
  function alertaSuave(t) {
    var m = document.createElement("p"); m.className = "msg err"; m.textContent = t;
    $("#vista").insertBefore(m, $("#vista").firstChild);
    setTimeout(function () { m.remove(); }, 5000);
  }

  /* --- tabla del Alpha Trading Challenge --- */
  function parsearTabla(txt) {
    var lineas = String(txt).replace(/\r/g, "").split("\n").filter(function (l) { return l.trim(); });
    if (lineas.length < 2) return null;
    var sep = lineas[0].indexOf("\t") >= 0 ? "\t" : (lineas[0].indexOf(";") >= 0 ? ";" : ",");
    var filas = lineas.map(function (l) { return l.split(sep).map(function (c) { return c.trim(); }); });
    return { columnas: filas[0], filas: filas.slice(1) };
  }
  function htmlTabla(t) {
    return '<div class="tabla"><table><thead><tr>' + t.columnas.map(function (c) { return "<th>" + esc(c) + "</th>"; }).join("") +
      '</tr></thead><tbody>' + t.filas.map(function (f) {
        return "<tr>" + f.map(function (c) { return "<td>" + esc(c) + "</td>"; }).join("") + "</tr>";
      }).join("") + '</tbody></table></div>';
  }
  function vistaTabla() {
    $("#vista").innerHTML = '<h2>Tabla del Alpha Trading Challenge</h2>' +
      '<p class="sub">Copia la tabla desde Excel o Google Sheets (con la fila de títulos) y pégala acá. Reemplaza la tabla que se ve en el sitio y en la app.</p>' +
      '<form id="fTabla"><label>Título del corte<input name="titulo" placeholder="Ej. Semana 1 · al 17 de octubre" maxlength="120" required></label>' +
      '<label>Tabla<textarea name="tabla" required placeholder="Posición&#9;Equipo&#9;Universidad&#9;Rentabilidad"></textarea></label>' +
      '<div id="previa"></div><button class="btn" type="submit">Subir tabla</button><p class="msg" id="mTabla" hidden></p></form>' +
      '<h2 style="margin-top:28px">La que se ve ahora</h2><div id="actual"><p class="vacio">Cargando…</p></div>';
    var f = $("#fTabla");
    f.tabla.addEventListener("input", function () {
      var t = parsearTabla(f.tabla.value);
      $("#previa").innerHTML = t ? '<p class="sub" style="margin:0 0 6px">Vista previa · ' + t.filas.length + ' filas</p>' + htmlTabla(t) : "";
    });
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var t = parsearTabla(f.tabla.value), m = $("#mTabla"), btn = $(".btn", f);
      if (!t) { m.hidden = false; m.className = "msg err"; m.textContent = "Pega al menos la fila de títulos y una fila de datos."; return; }
      btn.disabled = true;
      pedir({ tipo: "tabla_trading", titulo: f.titulo.value, columnas: t.columnas, filas: t.filas })
        .then(function (r) {
          if (!r.ok) throw new Error(r.mensaje);
          m.className = "msg ok"; m.textContent = "Tabla subida (" + r.filas + " filas). Ya se ve en el sitio.";
          f.reset(); $("#previa").innerHTML = ""; cargarActual();
        })
        .catch(function (err) { m.className = "msg err"; m.textContent = err.message; })
        .then(function () { m.hidden = false; btn.disabled = false; });
    });
    cargarActual();
  }
  function cargarActual() {
    fetch(ENDPOINT + "?tipo=tabla_trading", { cache: "no-store" }).then(function (r) { return r.json(); })
      .then(function (t) {
        $("#actual").innerHTML = t && t.columnas ? '<p class="sub" style="margin:0 0 6px">' + esc(t.titulo) + '</p>' + htmlTabla(t)
          : '<p class="vacio">Todavía no se ha subido ninguna tabla.</p>';
      }).catch(function () { $("#actual").innerHTML = '<p class="vacio">No se pudo cargar.</p>'; });
  }

  /* --- cuenta --- */
  function vistaCuenta() {
    $("#vista").innerHTML = '<h2>Cuenta</h2><div class="card"><h3>' + esc(yo.nombre) + '</h3><div class="meta">Usuario ' + esc(yo.id) +
      ' · área ' + esc(yo.area) + (yo.admin ? " · admin" : "") + '</div></div>' +
      '<h2 style="margin-top:22px">Cambiar clave</h2><form id="fClave">' +
      '<label>Clave actual<input name="actual" type="password" required autocomplete="current-password"></label>' +
      '<label><span class="rot">Clave nueva <span class="opc">(mínimo 8 caracteres)</span></span><input name="nueva" type="password" minlength="8" required autocomplete="new-password"></label>' +
      '<button class="btn" type="submit">Cambiar clave</button><p class="msg" id="mClave" hidden></p></form>' +
      '<p style="margin-top:28px"><button class="btn sec" id="bSalir" style="width:100%">Cerrar sesión</button></p>';
    $("#bSalir").onclick = salir;
    $("#fClave").addEventListener("submit", function (e) {
      e.preventDefault();
      var f = e.target, m = $("#mClave");
      pedir({ tipo: "cambiar_clave", actual: f.actual.value, nueva: f.nueva.value }).then(function (r) {
        if (!r.ok) throw new Error(r.mensaje);
        guardarToken(""); pantallaEntrada(); var a = $("#mEntrar"); a.hidden = false; a.className = "msg ok"; a.textContent = r.mensaje;
      }).catch(function (err) { m.hidden = false; m.className = "msg err"; m.textContent = err.message; });
    });
  }
  function salir() { guardarToken(""); yo = null; pantallaEntrada(); }

  /* --- arranque --- */
  fetch("../../datos/club.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) {
    ENDPOINT = (d.config && d.config.figEndpoint) || "";
    if (!leerToken()) return pantallaEntrada();
    app.innerHTML = '<p class="vacio">Entrando…</p>';
    return pedir({ tipo: "yo" }).then(function (r) {
      if (!r.ok) return pantallaEntrada();
      yo = r.usuario; pantallaPrincipal();
    });
  }).catch(function () {
    if (!yo && !$("#fEntrar")) pantallaEntrada("Sin conexión. Revisa internet e inténtalo de nuevo.");
  });

  if ("serviceWorker" in navigator) {
    addEventListener("load", function () { navigator.serviceWorker.register("../sw.js").catch(function () {}); });
  }
})();
