#!/usr/bin/env node
/*
 * grabar_pantalla_facultad_1_capturar.js
 *
 * PASO 1 de 2 para grabar el video de torneo/pantalla-facultad.html.
 * Captura la animación fotograma a fotograma manejando el Chrome que ya
 * está instalado en esta máquina por su protocolo de depuración (CDP) --
 * sin Playwright ni Puppeteer, con el WebSocket y fetch nativos de Node
 * (mismo patrón "CDP crudo" que se usó para verificar miembros/index.html,
 * ver CLAUDE.md). No instala ni descarga ningún navegador nuevo.
 *
 * Pensado para una máquina con poca RAM (ver CLAUDE.md, "video pixelado"):
 * cada fotograma se escribe a disco y se descarta de memoria ANTES de
 * capturar el siguiente -- nunca se acumulan fotogramas en RAM.
 *
 * Uso:
 *   1) Desde la raíz de fig-web, en OTRA terminal, levantar un server local
 *      (hace falta porque la página hace fetch() a ../datos/torneo.json,
 *      que el navegador bloquea si se abre como archivo suelto file://):
 *        python -m http.server 8000
 *   2) node grabar_pantalla_facultad_1_capturar.js
 *      Flags opcionales:
 *        --fps=30        (por defecto 30 -- 60 duplica tiempo y peso, ver
 *                          CLAUDE.md sobre el hardware de esta máquina)
 *        --formato=16x9  (mismo selector de formato que trae la página:
 *                          16x9|16x10|4x3|1x1|4x5|9x16)
 *        --port=8000     (puerto del server local del paso 1)
 *        --out=frames    (carpeta donde deja los .png)
 *
 * Salida: carpeta frames/ con frame_00000.png, frame_00001.png, ... y un
 * meta.json (fps/ancho/alto) que lee el paso 2 para armar el MP4.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawn } = require("child_process");

const ARGS = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    const m = a.match(/^--([^=]+)=(.*)$/);
    return m ? [m[1], m[2]] : [a.replace(/^--/, ""), true];
  })
);
const FPS = parseInt(ARGS.fps || "30", 10);
const FORMATO = ARGS.formato || "16x9";
const PORT = parseInt(ARGS.port || "8000", 10);
const OUT_DIR = ARGS.out || "frames";
const CDP_PORT = 9333;
const URL = `http://localhost:${PORT}/torneo/pantalla-facultad.html?formato=${FORMATO}`;

const RUTAS_NAVEGADOR = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
];

function encontrarNavegador() {
  for (const p of RUTAS_NAVEGADOR) if (fs.existsSync(p)) return p;
  throw new Error(
    "No se encontró Chrome ni Edge en las rutas conocidas -- editar RUTAS_NAVEGADOR en este script."
  );
}

function esperar(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

let idc = 0;
function enviarCDP(ws, method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++idc;
    const oyente = (ev) => {
      const msg = JSON.parse(ev.data.toString());
      if (msg.id === id) {
        ws.removeEventListener("message", oyente);
        if (msg.error) reject(new Error(method + ": " + JSON.stringify(msg.error)));
        else resolve(msg.result);
      }
    };
    ws.addEventListener("message", oyente);
    ws.send(JSON.stringify({ id, method, params }));
  });
}

async function main() {
  if (fs.existsSync(OUT_DIR)) {
    for (const f of fs.readdirSync(OUT_DIR)) {
      if (f.endsWith(".png") || f === "meta.json") fs.unlinkSync(path.join(OUT_DIR, f));
    }
  } else {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }

  // el server local es responsabilidad de quien corre el script (ver uso
  // arriba) -- se verifica antes de lanzar el navegador para fallar rápido
  // con un mensaje claro en vez de colgarse esperando window.__ready
  try {
    const r = await fetch(`http://localhost:${PORT}/torneo/pantalla-facultad.html`);
    if (!r.ok) throw new Error("status " + r.status);
  } catch (e) {
    throw new Error(
      `No se pudo conectar a http://localhost:${PORT}/ -- levantar antes ` +
        `"python -m http.server ${PORT}" desde la raíz de fig-web. (${e.message})`
    );
  }

  const chromePath = encontrarNavegador();
  const perfilTmp = path.join(os.tmpdir(), "fig-grabador-" + Date.now());
  console.log("Navegador:", chromePath);
  console.log("Página:", URL);

  const proc = spawn(
    chromePath,
    [
      "--headless=new",
      `--remote-debugging-port=${CDP_PORT}`,
      "--window-size=1920,1080",
      "--force-device-scale-factor=1",
      "--hide-scrollbars",
      "--disable-gpu",
      "--disable-extensions",
      "--no-first-run",
      "--no-default-browser-check",
      `--user-data-dir=${perfilTmp}`,
    ],
    { stdio: "ignore" }
  );
  proc.on("error", (e) => {
    console.error("No se pudo lanzar el navegador:", e.message);
    process.exit(1);
  });

  let info = null;
  for (let i = 0; i < 120; i++) {
    await esperar(500);
    try {
      const r = await fetch(`http://localhost:${CDP_PORT}/json/version`);
      if (r.ok) {
        info = await r.json();
        break;
      }
    } catch (e) {
      /* aún no levanta, reintentar */
    }
  }
  if (!info) {
    proc.kill();
    throw new Error("El navegador no respondió en el puerto de depuración tras 60s.");
  }
  console.log("CDP listo:", info.Browser);

  const nuevaPestana = await fetch(
    `http://localhost:${CDP_PORT}/json/new?${encodeURIComponent(URL)}`,
    { method: "PUT" }
  ).then((r) => r.json());
  const ws = new WebSocket(nuevaPestana.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve);
    ws.addEventListener("error", reject);
  });

  await enviarCDP(ws, "Page.enable");
  await enviarCDP(ws, "Runtime.enable");
  await enviarCDP(ws, "Emulation.setDeviceMetricsOverride", {
    width: 1920,
    height: 1080,
    deviceScaleFactor: 1,
    mobile: false,
  });

  console.log("Esperando datos de la página (window.__ready)...");
  let listo = false;
  for (let i = 0; i < 120; i++) {
    const r = await enviarCDP(ws, "Runtime.evaluate", {
      expression: "window.__ready===true",
      returnByValue: true,
    });
    if (r.result && r.result.value === true) {
      listo = true;
      break;
    }
    await esperar(500);
  }
  if (!listo) {
    throw new Error(
      "La página nunca llegó a window.__ready -- revisar que el server local " +
        "esté sirviendo datos/torneo.json (ver el paso 1 del uso, arriba)."
    );
  }

  console.log("Esperando a que carguen las tipografías (document.fonts.ready)...");
  await enviarCDP(ws, "Runtime.evaluate", {
    expression: "document.fonts ? document.fonts.ready.then(function(){return true}) : true",
    awaitPromise: true,
    returnByValue: true,
  });

  await enviarCDP(ws, "Runtime.evaluate", {
    expression: "window.__manual && window.__manual()",
  });

  const totalR = await enviarCDP(ws, "Runtime.evaluate", {
    expression: "window.__total",
    returnByValue: true,
  });
  const TOTAL = totalR.result.value;
  console.log("Duración del video:", (TOTAL / 1000).toFixed(1), "s");

  const paso = 1000 / FPS;
  const nFrames = Math.ceil(TOTAL / paso) + 1;
  console.log(`Capturando ${nFrames} fotogramas a ${FPS} fps (uno a la vez, a disco)...`);

  for (let i = 0; i < nFrames; i++) {
    const ms = Math.min(i * paso, TOTAL);
    await enviarCDP(ws, "Runtime.evaluate", { expression: `window.__seek(${ms})` });
    const shot = await enviarCDP(ws, "Page.captureScreenshot", { format: "png" });
    const buf = Buffer.from(shot.data, "base64");
    fs.writeFileSync(path.join(OUT_DIR, `frame_${String(i).padStart(5, "0")}.png`), buf);
    if (i % 30 === 0) console.log(`  ${i}/${nFrames}`);
  }

  fs.writeFileSync(
    path.join(OUT_DIR, "meta.json"),
    JSON.stringify({ fps: FPS, frames: nFrames, width: 1920, height: 1080, formato: FORMATO }, null, 2)
  );

  console.log("Captura terminada:", nFrames, "fotogramas en", OUT_DIR + "/");
  console.log("Siguiente paso: python grabar_pantalla_facultad_2_codificar.py");

  ws.close();
  proc.kill();
  fs.rmSync(perfilTmp, { recursive: true, force: true });
}

main().catch((e) => {
  console.error("ERROR:", e.message);
  process.exit(1);
});
