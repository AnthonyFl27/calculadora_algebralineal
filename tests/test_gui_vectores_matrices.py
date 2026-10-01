"""Pruebas de integración de la vista Tkinter de vectores y matrices."""

import tkinter as tk
import unittest
from unittest.mock import patch

import gui
from gui import VistaVectoresMatrices


def llenar_vector(entradas, valores):
    for entrada, valor in zip(entradas, valores):
        entrada.delete(0, tk.END)
        entrada.insert(0, str(valor))


def llenar_matriz(entradas, valores):
    for fila_entradas, fila_valores in zip(entradas, valores):
        llenar_vector(fila_entradas, fila_valores)


class VistaVectoresMatricesTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Tkinter no disponible: {error}")
        cls.raiz.withdraw()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "raiz"):
            cls.raiz.destroy()

    def setUp(self):
        self.marco = tk.Frame(self.raiz)
        self.marco.pack()
        self.vista = VistaVectoresMatrices(self.marco)

    def tearDown(self):
        self.marco.destroy()

    def salida(self):
        return self.vista.salida.get("1.0", tk.END)

    def test_operaciones_de_vectores_desde_la_vista(self):
        llenar_vector(self.vista.entradas_vectores[0], [1, 2, 3])
        llenar_vector(self.vista.entradas_vectores[1], [4, 5, 6])
        self.vista._calcular_vectores()
        self.assertIn("Resultado: (5, 7, 9)", self.salida())

        self.vista.operacion_vector.set("Resta")
        self.vista._crear_campos_vectores()
        llenar_vector(self.vista.entradas_vectores[0], [5, 7, 9])
        llenar_vector(self.vista.entradas_vectores[1], [1, 2, 3])
        self.vista._calcular_vectores()
        self.assertIn("Resultado: (4, 5, 6)", self.salida())

        self.vista.operacion_vector.set("Vector por escalar")
        self.vista._crear_campos_vectores()
        llenar_vector(self.vista.entradas_vectores[0], [1, 2, 3])
        self.vista.entrada_escalar_vector.insert(0, "1/2")
        self.vista._calcular_vectores()
        self.assertIn("Resultado: (1/2, 1, 3/2)", self.salida())

    def test_combinacion_lineal_positiva_y_negativa_desde_la_vista(self):
        self.vista.operacion_vector.set("Combinación lineal")
        self.vista._crear_campos_vectores()
        llenar_vector(self.vista.entradas_vectores[0], [1, 0, 0])
        llenar_vector(self.vista.entradas_vectores[1], [0, 1, 0])
        llenar_vector(self.vista.entradas_objetivo, [2, 3, 0])
        self.vista._calcular_vectores()
        self.assertIn("Sí es combinación lineal", self.salida())

        llenar_vector(self.vista.entradas_objetivo, [2, 3, 1])
        self.vista._calcular_vectores()
        self.assertIn("No es combinación lineal", self.salida())

    def test_operaciones_de_matrices_desde_la_vista(self):
        llenar_matriz(self.vista.entradas_matriz_a, [[1, 2], [3, 4]])
        llenar_matriz(self.vista.entradas_matriz_b, [[5, 6], [7, 8]])
        self.vista._calcular_matrices()
        self.assertIn("[  6   8 ]", self.salida())

        self.vista.operacion_matriz.set("Resta")
        self.vista._crear_campos_matrices()
        llenar_matriz(self.vista.entradas_matriz_a, [[5, 6], [7, 8]])
        llenar_matriz(self.vista.entradas_matriz_b, [[1, 2], [3, 4]])
        self.vista._calcular_matrices()
        self.assertIn("[ 4  4 ]", self.salida())

        self.vista.operacion_matriz.set("Matriz por escalar")
        self.vista._crear_campos_matrices()
        llenar_matriz(self.vista.entradas_matriz_a, [[1, 2], [3, 4]])
        self.vista.entrada_escalar_matriz.insert(0, "2")
        self.vista._calcular_matrices()
        self.assertIn("[ 2  4 ]", self.salida())

        self.vista.operacion_matriz.set("Multiplicación A × B")
        self.vista._crear_campos_matrices()
        llenar_matriz(self.vista.entradas_matriz_a, [[1, 2], [3, 4]])
        llenar_matriz(self.vista.entradas_matriz_b, [[2, 0], [1, 2]])
        self.vista._calcular_matrices()
        self.assertIn("[  4  4 ]", self.salida())

    def test_errores_matriciales_se_muestran_con_messagebox(self):
        self.vista.filas_b.delete(0, tk.END)
        self.vista.filas_b.insert(0, "1")
        self.vista._crear_campos_matrices()
        llenar_matriz(self.vista.entradas_matriz_a, [[1, 2], [3, 4]])
        llenar_matriz(self.vista.entradas_matriz_b, [[5, 6]])

        with patch("gui.messagebox.showerror") as mostrar_error:
            self.vista._calcular_matrices()
        mostrar_error.assert_called_once()
        self.assertIn("mismas dimensiones", mostrar_error.call_args.args[1])

        self.vista.operacion_matriz.set("Multiplicación A × B")
        self.vista._crear_campos_matrices()
        llenar_matriz(self.vista.entradas_matriz_a, [[1, 2], [3, 4]])
        llenar_matriz(self.vista.entradas_matriz_b, [[5, 6]])
        with patch("gui.messagebox.showerror") as mostrar_error:
            self.vista._calcular_matrices()
        mostrar_error.assert_called_once()
        self.assertIn("columnas de A", mostrar_error.call_args.args[1])

    def test_ecuacion_matricial_desde_la_vista(self):
        llenar_matriz(self.vista.entradas_ecuacion_a, [[2, 0], [0, 4]])
        llenar_matriz(self.vista.entradas_ecuacion_b, [[4], [8]])
        self.vista._calcular_ecuacion()
        self.assertIn("Solución única X", self.salida())
        self.assertIn("[ 2 ]", self.salida())

        llenar_matriz(self.vista.entradas_ecuacion_a, [[1, 1], [2, 2]])
        llenar_matriz(self.vista.entradas_ecuacion_b, [[2], [4]])
        self.vista._calcular_ecuacion()
        self.assertIn("infinitas soluciones", self.salida())

    def test_matriz_inversa_desde_la_vista(self):
        self.vista.inv_n.delete(0, tk.END)
        self.vista.inv_n.insert(0, "2")
        self.vista._crear_campos_inversa()
        llenar_matriz(self.vista.entradas_inversa, [[2, 1], [5, 3]])
        self.vista._calcular_inversa()
        self.assertIn("La matriz es invertible", self.salida())
        self.assertIn("[  3  -1 ]", self.salida())
        self.assertIn("A · A⁻¹ = I: correcto", self.salida())
        self.assertIn("Comprobación A⁻¹ · A:", self.salida())
        self.assertIn("A⁻¹ · A = I: correcto", self.salida())

        self.vista.metodo_inversa.set("Pivoteo")
        self.vista._calcular_inversa()
        self.assertIn("PIVOTEO", self.salida())

    def test_matriz_de_la_practica_no_tiene_inversa_en_la_vista(self):
        self.vista._crear_campos_inversa()
        llenar_matriz(
            self.vista.entradas_inversa,
            [[1, -2, -1], [-1, 5, 6], [5, -4, 5]],
        )
        self.vista._calcular_inversa()
        self.assertIn("La inversa NO existe", self.salida())

    def test_errores_de_la_inversa_se_muestran_con_messagebox(self):
        llenar_matriz(self.vista.entradas_inversa,
                      [["x", 0, 0], [0, 1, 0], [0, 0, 1]])
        with patch("gui.messagebox.showerror") as mostrar_error:
            self.vista._calcular_inversa()
        mostrar_error.assert_called_once()

        self.vista.inv_n.delete(0, tk.END)
        self.vista.inv_n.insert(0, "0")
        with patch("gui.messagebox.showerror") as mostrar_error:
            self.vista._crear_campos_inversa()
        mostrar_error.assert_called_once()


OPCIONES_COLOR = (
    "bg", "fg", "selectcolor", "activebackground", "activeforeground",
    "insertbackground", "highlightbackground",
)

# Opciones que existen pero que ese tipo de widget nunca dibuja.
NO_SE_DIBUJAN = {
    ("Canvas", "insertbackground"),
    ("Label", "activebackground"),
    ("Label", "activeforeground"),
    ("Menu", "selectcolor"),
}


def recorrer(widget):
    yield widget
    for hijo in widget.winfo_children():
        yield from recorrer(hijo)


class TemaOscuroClaroTests(unittest.TestCase):
    """Cambio de tema de la aplicación completa (sidebar + vista actual)."""

    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Tkinter no disponible: {error}")
        cls.raiz.withdraw()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "raiz"):
            cls.raiz.destroy()

    def setUp(self):
        for hijo in self.raiz.winfo_children():
            hijo.destroy()
        self.app = gui.Aplicacion(self.raiz)
        nombre, fabrica = [m for m in gui.METODOS
                           if m[0] == "Vectores y matrices"][0]
        self.app.mostrar_vista(fabrica, nombre)
        self.vista = self.app.vista_actual

    def tearDown(self):
        gui.activar_tema("claro")

    def colores_de(self, paleta):
        return {valor.lower() for valor in paleta.values()}

    def colores_en_uso(self):
        usados = {}
        for widget in recorrer(self.raiz):
            for opcion in OPCIONES_COLOR:
                if (widget.winfo_class(), opcion) in NO_SE_DIBUJAN:
                    continue
                try:
                    valor = str(widget.cget(opcion)).lower()
                    if (opcion == "highlightbackground"
                            and int(widget.cget("highlightthickness")) == 0):
                        continue  # el anillo de foco no se dibuja
                except tk.TclError:
                    continue
                if valor.startswith("#"):
                    usados.setdefault(valor, []).append(
                        f"{widget.winfo_class()}.{opcion}"
                    )
        return usados

    def test_arranca_en_claro_con_boton_de_tema(self):
        self.assertEqual(gui.TEMA_ACTUAL, "claro")
        self.assertIn("Modo oscuro", self.app.boton_tema.text)

    def test_cambio_conserva_datos_pestana_y_resultado(self):
        self.vista.pestanas.select(self.vista.tab_inversa)
        self.vista.inv_n.delete(0, tk.END)
        self.vista.inv_n.insert(0, "2")
        self.vista._crear_campos_inversa()
        llenar_matriz(self.vista.entradas_inversa, [[2, 1], [5, 3]])
        self.vista._calcular_inversa()
        salida = self.vista.salida.get("1.0", tk.END)
        pestana = self.vista.pestanas.select()

        self.app.alternar_tema()

        self.assertEqual(gui.TEMA_ACTUAL, "oscuro")
        self.assertIn("Modo claro", self.app.boton_tema.text)
        self.assertEqual(self.vista.salida.get("1.0", tk.END), salida)
        self.assertEqual(self.vista.pestanas.select(), pestana)
        self.assertEqual(
            [[e.get() for e in fila] for fila in self.vista.entradas_inversa],
            [["2", "1"], ["5", "3"]],
        )

    def test_en_oscuro_no_queda_ningun_color_del_tema_claro(self):
        self.app.alternar_tema()
        claro = self.colores_de(gui.PALETAS["claro"])
        oscuro = self.colores_de(gui.PALETAS["oscuro"])
        # Los colores que el tema claro y el oscuro comparten (texto blanco
        # del sidebar) son válidos en ambos.
        prohibidos = claro - oscuro
        # Además, los colores por defecto de Tk que no son de la paleta oscura.
        prohibidos |= {"#f5f5f5", "#ececec", "#c3c3c3"}
        usados = self.colores_en_uso()
        restos = {c: w for c, w in usados.items() if c in prohibidos}
        self.assertEqual(restos, {})

    def test_widgets_nuevos_nacen_con_el_tema_activo(self):
        self.app.alternar_tema()
        self.vista.operacion_matriz.set("Suma")
        self.vista._crear_campos_matrices()
        entrada = self.vista.entradas_matriz_a[0][0]
        self.assertEqual(str(entrada.cget("bg")).lower(),
                         gui.PALETAS["oscuro"]["superficie"])
        self.assertEqual(str(entrada.cget("fg")).lower(),
                         gui.PALETAS["oscuro"]["texto"])

    def test_vuelta_a_claro_restaura_los_colores_originales(self):
        antes = self.colores_en_uso()
        self.app.alternar_tema()
        self.app.alternar_tema()
        self.assertEqual(gui.TEMA_ACTUAL, "claro")
        self.assertEqual(self.colores_en_uso(), antes)

    def test_cambios_repetidos_no_acumulan_widgets(self):
        cantidad = len(list(recorrer(self.raiz)))
        for _ in range(6):
            self.app.alternar_tema()
        self.assertEqual(len(list(recorrer(self.raiz))), cantidad)
        self.assertEqual(gui.TEMA_ACTUAL, "claro")

    def test_boton_deshabilitado_usa_la_paleta_del_tema(self):
        boton = gui.RoundedButton(self.raiz, text="x", command=None)
        boton.set_state("disabled")
        self.app.alternar_tema()
        boton.aplicar_tema(gui.COLOR_FONDO)
        self.assertEqual(boton.bg, gui.COLOR_BOTON)
        self.assertEqual(gui.PALETAS[gui.TEMA_ACTUAL]["desact_texto"],
                         "#8c969e")

    def test_todas_las_vistas_se_recolorean_sin_errores(self):
        for nombre, fabrica in gui.METODOS:
            self.app.mostrar_vista(fabrica, nombre)
            self.app.aplicar_tema("oscuro")
            self.app.aplicar_tema("claro")
        self.assertEqual(gui.TEMA_ACTUAL, "claro")


if __name__ == "__main__":
    unittest.main()
