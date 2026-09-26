/* Service worker de las apps "FIG Directivos" (las 5 áreas comparten este).
 *
 * Vive en /directivos/, así que su alcance es /directivos/ y no choca con el
 * sw.js público de la raíz (el alcance más específico gana). Deja abrir la
 * app sin conexión para ver la pantalla, pero nunca guarda respuestas del
 * Apps Script (son de otro dominio y se ignoran): publicar exige internet.
 * Red primero para páginas, app.js/app.css y datos; caché primero para íconos.
 */
const VERSION = "fig-directivos-v2";

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(["offline.html"])).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k.startsWith("fig-directivos") && k !== VERSION).map((k) => caches.delete(k))))
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

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (/\.(png|jpe?g|webp|svg|ico)$/i.test(url.pathname)) {
    e.respondWith(caches.match(req).then((c) => c || fetch(req).then((r) => guardar(req, r))));
    return;
  }
  e.respondWith(
    fetch(req).then((r) => guardar(req, r)).catch(async () => {
      const c = await caches.match(req, { ignoreSearch: req.mode === "navigate" });
      if (c) return c;
      if (req.mode === "navigate") return caches.match(new URL("offline.html", self.registration.scope).href);
      return Response.error();
    })
  );
});
