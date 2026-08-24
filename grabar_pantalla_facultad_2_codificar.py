"""
grabar_pantalla_facultad_2_codificar.py -- PASO 2 de 2.

Arma el MP4 final a partir de los fotogramas que dejó
grabar_pantalla_facultad_1_capturar.js en frames/ (un .png por fotograma +
meta.json con fps/ancho/alto).

No mantiene los fotogramas en memoria a la vez: los lee, codifica y libera
uno por uno, escribiendo directo al archivo de salida -- pensado para una
máquina con poca RAM (ver CLAUDE.md, sección "video pixelado").

Uso:
    python grabar_pantalla_facultad_2_codificar.py
    python grabar_pantalla_facultad_2_codificar.py --crf 16 --out video.mp4

--crf: calidad de x264, MENOR número = más calidad y más peso. 16 es casi
sin pérdida (el estándar que ya usa este sitio en otros videos, ver
CLAUDE.md de torneo/pantalla-facultad.html); 18 (por defecto acá) es muy
buena calidad con harto menos peso, razonable para un video de subir a
Drive/WhatsApp; 23 es el estándar "streaming" de x264, se nota más la
compresión en gradientes suaves.
"""

from __future__ import annotations
import argparse
import json
import pathlib
import sys

import av
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default="frames", help="carpeta con los .png del paso 1")
    ap.add_argument("--out", default="torneo_portafolio_facultad.mp4")
    ap.add_argument("--crf", default="18")
    ap.add_argument("--preset", default="medium",
                     help="velocidad de codificación x264: ultrafast..veryslow. "
                          "'medium' es un balance razonable para este CPU.")
    args = ap.parse_args()

    carpeta = pathlib.Path(args.frames)
    meta_path = carpeta / "meta.json"
    if not meta_path.exists():
        sys.exit(f"No se encontró {meta_path} -- corre primero "
                  f"grabar_pantalla_facultad_1_capturar.js (paso 1).")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    fps, w, h = meta["fps"], meta["width"], meta["height"]

    archivos = sorted(carpeta.glob("frame_*.png"))
    if not archivos:
        sys.exit(f"No hay fotogramas .png en {carpeta}/")
    if len(archivos) != meta.get("frames"):
        print(f"Aviso: meta.json dice {meta.get('frames')} fotogramas pero hay "
              f"{len(archivos)} archivos .png -- seguirá con los que encontró.")

    print(f"{len(archivos)} fotogramas, {w}x{h} @ {fps}fps, crf={args.crf} preset={args.preset}")

    contenedor = av.open(args.out, mode="w")
    flujo = contenedor.add_stream("libx264", rate=fps)
    flujo.width = w
    flujo.height = h
    flujo.pix_fmt = "yuv420p"
    flujo.options = {"crf": str(args.crf), "preset": args.preset}

    for i, ruta in enumerate(archivos):
        img = Image.open(ruta).convert("RGB")
        frame = av.VideoFrame.from_image(img)
        for paquete in flujo.encode(frame):
            contenedor.mux(paquete)
        img.close()
        if i % 60 == 0:
            print(f"  codificando {i}/{len(archivos)}")

    for paquete in flujo.encode():
        contenedor.mux(paquete)
    contenedor.close()

    peso_mb = pathlib.Path(args.out).stat().st_size / (1024 * 1024)
    print(f"Listo: {args.out} ({peso_mb:.1f} MB)")


if __name__ == "__main__":
    main()
