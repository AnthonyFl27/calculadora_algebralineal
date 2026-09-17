"""Pruebas de integración de la vista Tkinter de vectores y matrices."""

import tkinter as tk
import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
