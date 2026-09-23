"""Genera los íconos de la app instalable (PWA) desde logos/fig-oro.png.

Salida en iconos/:
  icono-192.png, icono-512.png   — uso general (el disco llena casi todo el cuadro)
  icono-mascara-512.png          — "maskable": Android lo recorta en círculo o gota,
                                   así que el disco va dentro de la zona segura (80%)
  apple-touch-icon.png (180)     — iPhone; sin transparencia, iOS la pinta negra

Uso: python generar_iconos_app.py
"""
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent
FONDO = (10, 17, 40, 255)  # #0A1128, el navy base del sitio
LOGO = Image.open(RAIZ / "logos" / "fig-oro.png").convert("RGBA")
# El PNG trae aire alrededor del disco: recortarlo para escalar el disco real.
LOGO = LOGO.crop(LOGO.getbbox())
SALIDA = RAIZ / "iconos"
SALIDA.mkdir(exist_ok=True)


def icono(lado, fraccion, nombre):
    lienzo = Image.new("RGBA", (lado, lado), FONDO)
    d = round(lado * fraccion)
    logo = LOGO.resize((d, d), Image.LANCZOS)
    lienzo.alpha_composite(logo, ((lado - d) // 2, (lado - d) // 2))
    lienzo.convert("RGB").save(SALIDA / nombre, optimize=True)
    print(f"  iconos/{nombre}  {lado}px")


icono(192, 0.84, "icono-192.png")
icono(512, 0.84, "icono-512.png")
icono(512, 0.66, "icono-mascara-512.png")
icono(180, 0.80, "apple-touch-icon.png")
