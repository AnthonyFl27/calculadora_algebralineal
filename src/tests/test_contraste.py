"""Contraste mínimo 4.5:1 (WCAG AA) de los pares texto/fondo, en ambos temas
de las dos interfaces. Los controles deshabilitados quedan fuera (WCAG los
exime)."""

import re
import unittest
from pathlib import Path

import main as gui

MINIMO = 4.5
RAIZ = Path(__file__).resolve().parent.parent


def _canales(color):
    color = color.lstrip("#")
    return [int(color[i:i + 2], 16) for i in (0, 2, 4)]


def luminancia(color):
    def lineal(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lineal(c) for c in _canales(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    claro, oscuro = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (claro + 0.05) / (oscuro + 0.05)


def sobre(rgba, base):
    """Color resultante de un rgba(r, g, b, a) sobre un fondo opaco."""
    r, g, b, a = rgba
    return "#" + "".join(
        f"{round(c * a + f * (1 - a)):02x}"
        for c, f in zip((r, g, b), _canales(base))
    )


def variables_css(tema):
    """Variables CSS del bloque `:root` (claro) o del tema oscuro."""
    html = (RAIZ / "web" / "index.html").read_text(encoding="utf-8")
    inicio = html.index(":root {" if tema == "claro" else 'html[data-theme="dark"] {')
    bloque = html[inicio:html.index("}", inicio)]
    return dict(re.findall(r"(--[\w-]+):\s*([^;]+);", bloque))


def como_rgba(valor):
    m = re.fullmatch(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", valor.strip())
    return tuple(float(x) for x in m.groups()) if m else None


class ContrasteWebTests(unittest.TestCase):

    def comprobar(self, tema):
        v = variables_css(tema)
        # Las variables del tema oscuro heredan las que no redefinen.
        if tema == "oscuro":
            v = {**variables_css("claro"), **v}
        fondos = [v[n] for n in (
            "--color-fondo", "--superficie", "--superficie-2",
            "--superficie-3", "--chip-fondo")]
        textos = ("--texto", "--texto-titulo", "--texto-acento",
                  "--texto-suave-1", "--texto-suave-2", "--texto-suave-3",
                  "--texto-tenue", "--exito-texto", "--error-texto",
                  "--alerta-texto", "--acento-texto")
        pares = [(n, v[n], f) for n in textos for f in fondos]

        for fondo_var, texto_var in (
            ("--exito-fondo", "--exito-texto"),
            ("--alerta-fondo", "--alerta-texto"),
            ("--error-fondo", "--error-texto"),
            ("--pivote-fondo", "--pivote-texto"),
            ("--pivote-fondo-fuerte", "--pivote-texto"),
        ):
            for base in (v["--superficie"], v["--color-fondo"]):
                pares.append((f"{texto_var} sobre {fondo_var}", v[texto_var],
                              sobre(como_rgba(v[fondo_var]), base)))
        pares += [
            ("op-inter", v["--op-inter-texto"], v["--op-inter-fondo"]),
            ("texto sidebar", v["--color-texto-sb"], v["--color-sidebar"]),
            ("texto sidebar suave", v["--texto-sb-suave"], v["--color-sidebar"]),
            ("texto en botón", v["--color-texto-sb"], v["--color-boton"]),
            ("texto en botón activo", v["--color-texto-sb"], v["--color-boton-act"]),
        ]
        for nombre, fg, bg in pares:
            with self.subTest(tema=tema, par=nombre, fg=fg, bg=bg):
                self.assertGreaterEqual(contraste(fg, bg), MINIMO)

    def test_tema_claro(self):
        self.comprobar("claro")

    def test_tema_oscuro(self):
        self.comprobar("oscuro")


class ContrasteGuiTests(unittest.TestCase):

    def test_ambos_temas(self):
        for tema, p in gui.PALETAS.items():
            pares = [("texto", p["texto"], p["fondo"]),
                     ("texto en áreas de texto", p["texto"], p["superficie"]),
                     ("texto sidebar", p["texto_sb"], p["sidebar"]),
                     ("texto en botón", p["texto_sb"], p["boton"]),
                     ("texto en botón activo", p["texto_sb"], p["boton_act"])]
            for nivel in ("basico", "intermedio", "avanzado"):
                pares.append((f"dificultad {nivel}", p["dif_" + nivel], p["fondo"]))
            pares.append(("ícono de exportar", p["acento"], p["fondo"]))
            for nombre, fg, bg in pares:
                with self.subTest(tema=tema, par=nombre):
                    self.assertGreaterEqual(contraste(fg, bg), MINIMO)


if __name__ == "__main__":
    unittest.main()
