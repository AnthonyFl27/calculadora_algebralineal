"""
gui.py
Interfaz gráfica de panel único con sidebar para resolver sistemas de
ecuaciones lineales.

La lógica matemática vive en los módulos de método (gauss_jordan.py,
etc.). Aquí solo se capturan datos y se muestran resultados.
"""

import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

from metodos.general_metodos import matriz_texto, texto_comprobacion
from metodos.gauss_jordan import resolver as resolver_gauss_jordan
from metodos.pivote import resolver as resolver_pivote
from metodos.conversion import (
    NOMBRES_BASE,
    resolver as resolver_conversion,
    procedimiento_texto as procedimiento_conversion_texto,
)


# ======================================================
# ESTILOS CENTRALIZADOS
# ======================================================

FUENTE_TITULO = ("Arial", 20, "bold")
FUENTE_SUBTIT = ("Arial", 14, "bold")
FUENTE_NORMAL = ("Arial", 10)
FUENTE_SEPARADOR = ("Arial", 12, "bold")
FUENTE_MONO = ("Courier New", 10)

COLOR_FONDO = "#f5f5f5"
COLOR_SIDEBAR = "#2c3e50"
COLOR_BOTON = "#34495e"
COLOR_BOTON_ACT = "#1abc9c"
COLOR_TEXTO_SB = "#ffffff"

PAD = 8


def _ajustar_color(color, factor):
    """Aclara (factor > 1) u oscurece (factor < 1) un color hex."""
    color = color.lstrip("#")
    if len(color) != 6:
        return color
    rgb = [int(color[i:i + 2], 16) for i in (0, 2, 4)]
    rgb = [max(0, min(255, int(c * factor))) for c in rgb]
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def _puntos_redondeado(w, h, r, resolucion=10, paso=8):
    """Ruta (lista plana de coordenadas) de un rectángulo redondeado."""
    pts = []

    def arco(cx, cy, a0, a1):
        for i in range(resolucion):
            ang = math.radians(a0 + (a1 - a0) * i / resolucion)
            pts.extend((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    def borde(x0, y0, x1, y1):
        largo = math.hypot(x1 - x0, y1 - y0)
        m = max(1, int(largo / paso))
        for i in range(m):
            t = i / m
            pts.extend((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))

    borde(r, 0, w - r, 0)
    arco(w - r, r, 270, 360)
    borde(w, r, w, h - r)
    arco(w - r, h - r, 0, 90)
    borde(w - r, h, r, h)
    arco(r, h - r, 90, 180)
    borde(0, h - r, 0, r)
    arco(r, r, 180, 270)
    pts.extend((r, 0))  # cerrar el contorno
    return pts


def _puntos_tapa(w, h, r, alto, resolucion=10, paso=8):
    """Ruta de la tapa superior (brillo) del botón."""
    pts = []

    def arco(cx, cy, a0, a1):
        for i in range(resolucion):
            ang = math.radians(a0 + (a1 - a0) * i / resolucion)
            pts.extend((cx + r * math.cos(ang), cy + r * math.sin(ang)))

    def borde(x0, y0, x1, y1):
        largo = math.hypot(x1 - x0, y1 - y0)
        m = max(1, int(largo / paso))
        for i in range(m):
            t = i / m
            pts.extend((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))

    borde(r, 0, w - r, 0)
    arco(w - r, r, 270, 360)
    borde(w, r, w, alto)
    borde(w, alto, 0, alto)
    borde(0, alto, 0, r)
    arco(r, r, 180, 270)
    pts.extend((r, 0))
    return pts


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, **kwargs):
        self.bg = kwargs.get('bg', COLOR_BOTON)
        self.fg = kwargs.get('fg', COLOR_TEXTO_SB)
        self.active_bg = kwargs.get('active_background', COLOR_BOTON_ACT)
        self.font = kwargs.get('font', FUENTE_NORMAL)
        self.text = text
        self.command = command
        self.state = kwargs.get('state', 'normal')
        self.cursor = kwargs.get('cursor', 'hand2')
        self.radio = kwargs.get('radio', 12)
        self.activo = False

        # Ancho en píxeles: explícito si se pasa, o automático según texto/fuente.
        fuente = tkfont.Font(font=self.font)
        if kwargs.get('width'):
            self.width = kwargs['width']
        else:
            self.width = fuente.measure(self.text) + 30
        self.height = kwargs.get('height') or (fuente.metrics('linespace') + 12)

        super().__init__(
            parent,
            width=self.width,
            height=self.height,
            bg=COLOR_FONDO,
            highlightthickness=0,
            bd=0
        )
        self.config(cursor=self.cursor)

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_configure)

        self.draw_button()

    def cambiar_color(self, color):
        self.bg = color
        self.activo = (color == COLOR_BOTON_ACT)
        self.draw_button()

    def set_state(self, estado):
        self.state = estado
        self.draw_button()

    def _on_configure(self, event):
        self.width = event.width
        self.height = event.height
        if event.width > 1:
            self.draw_button()

    def draw_button(self):
        self.delete("all")

        w, h = self.width, self.height
        r = min(self.radio, w / 2, h / 2)

        if self.state == "disabled":
            fill = "#b0b0b0"
            borde = "#8e8e8e"
            resalte = "#cfcfcf"
            texto = "#9e9e9e"
        else:
            fill = self.bg
            borde = _ajustar_color(self.bg, 0.82)
            resalte = _ajustar_color(self.bg, 1.22)
            texto = self.fg

        # Cuerpo: un único polígono suave (sin costuras) con borde nítido.
        self.create_polygon(
            *_puntos_redondeado(w, h, r),
            fill=fill,
            outline=borde,
            width=1,
            smooth=True
        )

        # Brillo superior para un acabado más "real".
        alto = max(r, h * 0.42)
        self.create_polygon(
            *_puntos_tapa(w, h, r, alto),
            fill=resalte,
            outline="",
            smooth=True
        )

        # Texto.
        self.create_text(
            w / 2,
            h / 2,
            text=self.text,
            font=self.font,
            fill=texto,
            anchor="center"
        )

    def _on_click(self, event):
        if self.state == "normal" and self.command:
            self.command()
        self.draw_button()

    def _on_enter(self, event):
        if self.state == "normal":
            self.bg = self.active_bg
            self.draw_button()

    def _on_leave(self, event):
        if self.state == "normal":
            self.bg = self.active_bg if self.activo else COLOR_BOTON
            self.draw_button()

class VistaBase:
    """Clase base de las vistas montadas en el panel derecho."""

    def __init__(self, padre):
        self.padre = padre
        self.construir()

    def construir(self):
        raise NotImplementedError

    def limpiar_salida(self):
        self.salida.config(state="normal")
        self.salida.delete("1.0", tk.END)
        self.salida.config(state="disabled")

    def escribir(self, texto):
        self.salida.config(state="normal")
        self.salida.insert(tk.END, texto)
        self.salida.config(state="disabled")


# ======================================================
# VISTA GENÉRICA DE SISTEMA LINEAL
# ======================================================

class VistaSistemaLineal(VistaBase):
    """Formulario compartido por los métodos que resuelven A·X = B.

    Recibe la función del motor (`funcion_resolver`) para que distintos
    métodos reutilicen la misma interfaz cambiando solo el resolvedor.
    """

    def __init__(self, padre, funcion_resolver, titulo):
        self.funcion_resolver = funcion_resolver
        self.titulo = titulo
        super().__init__(padre)

    def construir(self):
        self.entradas = []
        self.ultimo_resultado = None

        # -------------------------------
        # TÍTULO
        # -------------------------------

        tk.Label(
            self.padre,
            text=self.titulo,
            font=FUENTE_TITULO,
            bg=COLOR_FONDO
        ).pack(pady=12)

        # -------------------------------
        # CONFIGURACIÓN
        # -------------------------------

        controles = tk.Frame(self.padre, bg=COLOR_FONDO)
        controles.pack(pady=5)

        tk.Label(
            controles,
            text="Ecuaciones:",
            bg=COLOR_FONDO
        ).grid(row=0, column=0, padx=5)

        self.entrada_ecuaciones = tk.Entry(
            controles,
            width=5,
            justify="center"
        )
        self.entrada_ecuaciones.grid(row=0, column=1, padx=5)
        self.entrada_ecuaciones.insert(0, "3")

        tk.Label(
            controles,
            text="Variables:",
            bg=COLOR_FONDO
        ).grid(row=0, column=2, padx=5)

        self.entrada_variables = tk.Entry(
            controles,
            width=5,
            justify="center"
        )
        self.entrada_variables.grid(row=0, column=3, padx=5)
        self.entrada_variables.insert(0, "3")

        RoundedButton(
            controles,
            text="Crear matriz",
            command=self.crear_matriz,
            width=120
        ).grid(row=0, column=4, padx=8)

        RoundedButton(
            controles,
            text="Limpiar",
            command=self.limpiar_matriz,
            width=120
        ).grid(row=0, column=5, padx=8)

        # -------------------------------
        # MATRIZ
        # -------------------------------

        self.marco_matriz = tk.Frame(self.padre, bg=COLOR_FONDO)
        self.marco_matriz.pack(pady=15)

        # -------------------------------
        # OPCIÓN DE FORMATO
        # -------------------------------

        formato = tk.Frame(self.padre, bg=COLOR_FONDO)
        formato.pack(pady=5)

        tk.Label(
            formato,
            text="Mostrar resultados en:",
            bg=COLOR_FONDO
        ).pack(side="left", padx=5)

        self.modo = tk.StringVar(value="fraccion")

        tk.Radiobutton(
            formato,
            text="Fracciones",
            variable=self.modo,
            value="fraccion",
            bg=COLOR_FONDO
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            formato,
            text="Decimales",
            variable=self.modo,
            value="decimal",
            bg=COLOR_FONDO
        ).pack(side="left", padx=5)

        # -------------------------------
        # BOTONES
        # -------------------------------

        botones = tk.Frame(self.padre, bg=COLOR_FONDO)
        botones.pack(pady=10)

        RoundedButton(
            botones,
            text="Resolver",
            command=self.resolver_sistema,
            width=200,
            font=FUENTE_SUBTIT
        ).grid(row=0, column=0, padx=8)

        RoundedButton(
            botones,
            text="Mostrar pasos",
            command=self.mostrar_pasos,
            width=200,
            font=FUENTE_SUBTIT
        ).grid(row=0, column=1, padx=8)

        self.boton_comprobar = RoundedButton(
            botones,
            text="Comprobar resultado",
            command=self.comprobar_resultado,
            width=200,
            font=FUENTE_SUBTIT,
            state="disabled"
        )
        self.boton_comprobar.grid(row=0, column=2, padx=8)

        # -------------------------------
        # ÁREA DE RESULTADO
        # -------------------------------

        self.salida = tk.Text(
            self.padre,
            width=105,
            height=22,
            font=FUENTE_MONO,
            bg="white",
            state="disabled"
        )
        self.salida.pack(padx=15, pady=8)

        self.crear_matriz()

    # ==================================================
    # CREAR MATRIZ
    # ==================================================

    def crear_matriz(self):

        try:
            ecuaciones = int(self.entrada_ecuaciones.get())
            variables = int(self.entrada_variables.get())

            if ecuaciones < 1 or variables < 1:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Error",
                "Ingrese números enteros mayores que cero."
            )
            return

        # Borrar matriz anterior.
        for widget in self.marco_matriz.winfo_children():
            widget.destroy()

        self.entradas = []
        self.ultimo_resultado = None
        self.boton_comprobar.set_state("disabled")

        # Encabezados de variables.
        for j in range(variables):
            tk.Label(
                self.marco_matriz,
                text=f"x{j + 1}",
                font=FUENTE_NORMAL,
                bg=COLOR_FONDO
            ).grid(
                row=0,
                column=j,
                padx=5,
                pady=5
            )

        # Separador.
        tk.Label(
            self.marco_matriz,
            text="│",
            font=FUENTE_SEPARADOR,
            bg=COLOR_FONDO
        ).grid(
            row=0,
            column=variables,
            padx=8
        )

        tk.Label(
            self.marco_matriz,
            text="b",
            font=FUENTE_NORMAL,
            bg=COLOR_FONDO
        ).grid(
            row=0,
            column=variables + 1,
            padx=5
        )

        # Campos.
        for i in range(ecuaciones):

            fila_entradas = []

            for j in range(variables):

                entrada = tk.Entry(
                    self.marco_matriz,
                    width=8,
                    justify="center"
                )

                entrada.grid(
                    row=i + 1,
                    column=j,
                    padx=5,
                    pady=4
                )

                fila_entradas.append(entrada)

            tk.Label(
                self.marco_matriz,
                text="│",
                font=FUENTE_SEPARADOR,
                bg=COLOR_FONDO
            ).grid(
                row=i + 1,
                column=variables,
                padx=8
            )

            entrada_resultado = tk.Entry(
                self.marco_matriz,
                width=8,
                justify="center"
            )

            entrada_resultado.grid(
                row=i + 1,
                column=variables + 1,
                padx=5,
                pady=4
            )

            fila_entradas.append(entrada_resultado)
            self.entradas.append(fila_entradas)

        self.limpiar_salida()

    # ==================================================
    # LIMPIAR MATRIZ
    # ==================================================

    def limpiar_matriz(self):

        for fila in self.entradas:
            for entrada in fila:
                entrada.delete(0, tk.END)

        self.ultimo_resultado = None
        self.boton_comprobar.set_state("disabled")
        self.limpiar_salida()

    # ==================================================
    # LEER MATRIZ
    # ==================================================

    def obtener_matriz(self):

        matriz = []

        for fila_entradas in self.entradas:

            fila = []

            for entrada in fila_entradas:

                texto = entrada.get().strip()

                if texto == "":
                    raise ValueError

                fila.append(float(texto))

            matriz.append(fila)

        return matriz

    def comprobar_resultado(self):

        if self.ultimo_resultado is None:

            messagebox.showwarning(
                "Aviso",
                "Primero resuelva el sistema para poder comprobarlo."
            )
            return

        self.limpiar_salida()

        self.escribir(
            "========================================\n"
            "COMPROBACIÓN (A_original @ X vs B_original)\n"
            "========================================\n\n"
        )

        self.escribir(
            texto_comprobacion(
                self.ultimo_resultado["comprobacion"],
                self.modo.get()
            )
        )

    # ==================================================
    # RESOLVER
    # ==================================================

    def resolver_sistema(self):

        try:
            matriz = self.obtener_matriz()

        except ValueError:
            messagebox.showerror(
                "Error",
                "Complete todos los campos de la matriz con números."
            )
            return

        self.ultimo_resultado = self.funcion_resolver(
            matriz,
            self.modo.get()
        )
        self.boton_comprobar.set_state("normal")

        resultado = self.ultimo_resultado

        self.limpiar_salida()

        self.escribir(
            "========================================\n"
            "RESULTADO\n"
            "========================================\n"
        )

        if resultado["tipo"] == "unica":

            self.escribir(
                "Sistema compatible determinado.\n"
                "Tiene una única solución.\n\n"
            )

        elif resultado["tipo"] == "infinitas":

            self.escribir(
                "Sistema compatible indeterminado.\n"
                "Tiene infinitas soluciones.\n\n"
            )

        else:

            self.escribir(
                "Sistema incompatible o inconsistente.\n"
                "No tiene solución.\n\n"
            )

        self.escribir(resultado["soluciones"])

    # ==================================================
    # MOSTRAR PASOS
    # ==================================================

    def mostrar_pasos(self):

        if self.ultimo_resultado is None:

            try:
                matriz = self.obtener_matriz()

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Complete todos los campos de la matriz con números."
                )
                return

            self.ultimo_resultado = self.funcion_resolver(
                matriz,
                self.modo.get()
            )
            self.boton_comprobar.set_state("normal")

        resultado = self.ultimo_resultado
        modo = self.modo.get()

        self.limpiar_salida()

        self.escribir(
            "========================================\n"
            "MATRIZ AUMENTADA INICIAL\n"
            "========================================\n\n"
        )

        self.escribir(
            matriz_texto(
                resultado["matriz_inicial"],
                modo
            )
        )

        self.escribir(
            "\n\n========================================\n"
            f"PROCEDIMIENTO {self.titulo.upper()}\n"
            "========================================\n"
        )

        for paso in resultado["pasos"]:

            self.escribir(
                "\n" + paso["operacion"] + "\n\n"
            )

            self.escribir(
                matriz_texto(
                    paso["matriz"],
                    modo
                )
            )

        self.escribir(
            "\n\n========================================\n"
            "MATRIZ FINAL\n"
            "========================================\n\n"
        )

        self.escribir(
            matriz_texto(
                resultado["matriz_final"],
                modo
            )
        )

        self.escribir(
            "\n\n========================================\n"
            "RESULTADO\n"
            "========================================\n\n"
        )

        if resultado["tipo"] == "unica":

            self.escribir(
                "Sistema compatible determinado.\n"
                "Tiene una única solución.\n\n"
            )

        elif resultado["tipo"] == "infinitas":

            self.escribir(
                "Sistema compatible indeterminado.\n"
                "Tiene infinitas soluciones.\n\n"
            )

        else:

            self.escribir(
                "Sistema incompatible o inconsistente.\n"
                "No tiene solución.\n\n"
            )

        self.escribir(resultado["soluciones"])


# ======================================================
# VISTA DE CONVERSIÓN DE BASES
# ======================================================

class VistaConversion(VistaBase):
    """Formulario para convertir entre decimal, binario, octal y hex."""

    BASES_A_OTRA = ["binario", "octal", "hexadecimal"]
    BASES_A_DECIMAL = ["binario", "octal", "decimal"]

    NOMBRE_A_BASE = {
        "binario": 2,
        "octal": 8,
        "decimal": 10,
        "hexadecimal": 16,
    }

    def construir(self):

        # -------------------------------
        # TÍTULO
        # -------------------------------

        tk.Label(
            self.padre,
            text="Conversión de bases",
            font=FUENTE_TITULO,
            bg=COLOR_FONDO
        ).pack(pady=12)

        # -------------------------------
        # DIRECCIÓN
        # -------------------------------

        direccion_marco = tk.Frame(self.padre, bg=COLOR_FONDO)
        direccion_marco.pack(pady=5)

        tk.Label(
            direccion_marco,
            text="Dirección:",
            bg=COLOR_FONDO
        ).pack(side="left", padx=5)

        self.direccion = tk.StringVar(value="a_otra_base")

        tk.Radiobutton(
            direccion_marco,
            text="Decimal → otra base",
            variable=self.direccion,
            value="a_otra_base",
            bg=COLOR_FONDO,
            command=self._actualizar_opciones_base
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            direccion_marco,
            text="Otra base → Decimal",
            variable=self.direccion,
            value="a_decimal",
            bg=COLOR_FONDO,
            command=self._actualizar_opciones_base
        ).pack(side="left", padx=5)

        # -------------------------------
        # BASE Y NÚMERO
        # -------------------------------

        controles = tk.Frame(self.padre, bg=COLOR_FONDO)
        controles.pack(pady=10)

        tk.Label(
            controles,
            text="Base:",
            bg=COLOR_FONDO
        ).grid(row=0, column=0, padx=5)

        self.base = tk.StringVar(value=self.BASES_A_OTRA[0])

        self.menu_base = tk.OptionMenu(
            controles,
            self.base,
            *self.BASES_A_OTRA
        )
        self.menu_base.grid(row=0, column=1, padx=5)

        tk.Label(
            controles,
            text="Número:",
            bg=COLOR_FONDO
        ).grid(row=0, column=2, padx=5)

        self.entrada_numero = tk.Entry(
            controles,
            width=25,
            justify="center"
        )
        self.entrada_numero.grid(row=0, column=3, padx=5)

        RoundedButton(
            controles,
            text="Convertir",
            command=self.convertir,
            width=150,
            font=FUENTE_SUBTIT
        ).grid(row=0, column=4, padx=10)

        # -------------------------------
        # ÁREA DE RESULTADO
        # -------------------------------

        self.salida = tk.Text(
            self.padre,
            width=105,
            height=26,
            font=FUENTE_MONO,
            bg="white",
            state="disabled"
        )
        self.salida.pack(padx=15, pady=8)

    def _actualizar_opciones_base(self):

        opciones = (
            self.BASES_A_OTRA
            if self.direccion.get() == "a_otra_base"
            else self.BASES_A_DECIMAL
        )

        menu = self.menu_base["menu"]
        menu.delete(0, "end")

        for opcion in opciones:
            menu.add_command(
                label=opcion,
                command=lambda v=opcion: self.base.set(v)
            )

        self.base.set(opciones[0])

    def convertir(self):

        numero_texto = self.entrada_numero.get().strip()
        base_nombre = self.base.get()
        base_numero = self.NOMBRE_A_BASE[base_nombre]

        if self.direccion.get() == "a_otra_base":
            base_entrada, base_salida = 10, base_numero
        else:
            base_entrada, base_salida = base_numero, 10

        try:
            resultado = resolver_conversion(
                numero_texto, base_entrada, base_salida
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self.limpiar_salida()

        self.escribir(
            "========================================\n"
            "PROCEDIMIENTO\n"
            "========================================\n\n"
        )

        self.escribir(procedimiento_conversion_texto(resultado))

        self.escribir(
            "\n\n========================================\n"
            "RESULTADO\n"
            "========================================\n\n"
        )

        self.escribir(
            f"{resultado['numero_entrada']} "
            f"({NOMBRES_BASE[resultado['base_entrada']]}) = "
            f"{resultado['resultado']} "
            f"({NOMBRES_BASE[resultado['base_salida']]})"
        )


# ======================================================
# REGISTRO DE MÉTODOS
# ======================================================

METODOS = [
    (
        "Gauss-Jordan",
        lambda p: VistaSistemaLineal(
            p, resolver_gauss_jordan, "Gauss-Jordan"
        ),
    ),
    (
        "Pivoteo",
        lambda p: VistaSistemaLineal(
            p, resolver_pivote, "Pivoteo"
        ),
    ),
    (
        "Conversión de bases",
        lambda p: VistaConversion(p),
    ),
]


# ======================================================
# APLICACIÓN
# ======================================================

class Aplicacion:

    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Calculadora de Matrices")
        raiz.geometry("1000x720")
        raiz.configure(bg=COLOR_FONDO)

        # Layout: sidebar fija + panel expandible.
        raiz.grid_rowconfigure(0, weight=1)
        raiz.grid_columnconfigure(0, weight=0)
        raiz.grid_columnconfigure(1, weight=1)

        self.botones_sidebar = {}

        self.sidebar = tk.Frame(raiz, width=200, bg=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.contenedor = tk.Frame(raiz, bg=COLOR_FONDO)
        self.contenedor.grid(row=0, column=1, sticky="nsew")

        self._construir_sidebar()

        nombre, fabrica = METODOS[0]
        self.mostrar_vista(fabrica, nombre)

    def _construir_sidebar(self):

        tk.Label(
            self.sidebar,
            text="Calculadora",
            font=FUENTE_SUBTIT,
            bg=COLOR_SIDEBAR,
            fg=COLOR_TEXTO_SB
        ).pack(fill="x", padx=PAD, pady=PAD * 2)

        for nombre, fabrica in METODOS:

            boton = RoundedButton(
                self.sidebar,
                text=nombre,
                font=FUENTE_NORMAL,
                bg=COLOR_BOTON,
                active_background=COLOR_BOTON_ACT,
                cursor="hand2",
                width=180,
                command=lambda n=nombre, f=fabrica: self.mostrar_vista(f, n)
            )
            boton.pack(fill="x", padx=PAD, pady=4)
            self.botones_sidebar[nombre] = boton

    def mostrar_vista(self, fabrica, nombre=None):

        for widget in self.contenedor.winfo_children():
            widget.destroy()

        self.vista_actual = fabrica(self.contenedor)
        self._resaltar_boton(nombre)

    def _resaltar_boton(self, nombre):

        for n, boton in self.botones_sidebar.items():
            boton.cambiar_color(
                COLOR_BOTON_ACT if n == nombre else COLOR_BOTON
            )


# ======================================================
# INICIAR PROGRAMA
# ======================================================

if __name__ == "__main__":
    raiz = tk.Tk()
    app = Aplicacion(raiz)
    raiz.mainloop()
