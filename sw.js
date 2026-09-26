/* Service worker de la app instalable de FIG.
 *
 * Regla de fondo: el ranking cambia cada semana, así que las páginas y los
 * datos se piden SIEMPRE a la red primero; el caché es solo el respaldo sin
 * conexión. Nunca se muestra un ranking viejo si hay internet.
 *   - páginas (navegación) y datos/*.json → red primero, caché si falla
 *   - letras, logos, fotos, íconos         → caché primero, se refresca por detrás
 *   - otros dominios (métricas, etc.)      → no se tocan
 * Para forzar que todos los teléfonos descarten lo guardado, subir VERSION.
 */
const VERSION = "fig-v2";
const BASE = new URL("./", self.location).pathname;
const PRECARGA = ["./", "app/", "offline.html", "iconos/icono-192.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(PRECARGA)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

const guardar = (req, res) => {
  if (res && res.ok && res.type === "basic") {
    const copia = res.clone();
    caches.open(VERSION).then((c) => c.put(req, copia));
  }
  return res;
};

async function redPrimero(req, esPagina) {
  try {
    return guardar(req, await fetch(req));
  } catch {
    const enCache = await caches.match(req, { ignoreSearch: esPagina });
    if (enCache) return enCache;
    if (esPagina) return caches.match("offline.html");
    throw new Error("sin conexión y sin copia guardada");
  }
}

async function cachePrimero(req) {
  const enCache = await caches.match(req);
  const deRed = fetch(req).then((res) => guardar(req, res)).catch(() => null);
  return enCache || (await deRed) || Response.error();
}

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin || !url.pathname.startsWith(BASE)) return;

  if (req.mode === "navigate") {
    e.respondWith(redPrimero(req, true));
  } else if (url.pathname.endsWith(".json")) {
    e.respondWith(redPrimero(req, false));
  } else if (/\.(woff2?|ttf|png|jpe?g|webp|svg|gif|ico)$/i.test(url.pathname)) {
    e.respondWith(cachePrimero(req));
  }
});
