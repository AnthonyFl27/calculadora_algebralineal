"""Pruebas de integración del menú de inicio de la GUI (Tkinter)."""

import tkinter as tk
import unittest

import gui


class InicioTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Tkinter no disponible: {error}")
        cls.raiz.withdraw()

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def setUp(self):
        gui.activar_tema("claro", self.raiz)
        self.app = gui.Aplicacion(self.raiz)
        self.raiz.update()

    def tearDown(self):
        self.app.contenedor.destroy()
        self.app.sidebar.destroy()

    def activos(self):
        return [n for n, b in self.app.botones_sidebar.items() if b.activo]

    def test_inicio_tiene_la_tarjeta_de_ejercicios_bajo_un_separador(self):
        hijos = self.app.contenedor.winfo_children()
        self.assertTrue(any(isinstance(h, gui.Separador) for h in hijos))
        self.assertEqual(
            self.app.vista_actual.tarjeta_ejercicios.text,
            gui.NOMBRE_TARJETA_EJERCICIOS,
        )
        self.assertIn(gui.NOMBRE_EJERCICIOS, self.app.botones_sidebar)

    def test_abre_en_inicio_con_una_tarjeta_por_modulo(self):
        self.assertIsInstance(self.app.vista_actual, gui.VistaInicio)
        self.assertEqual(self.activos(), [gui.NOMBRE_INICIO])
        self.assertEqual(
            list(self.app.vista_actual.tarjetas), [n for n, _ in gui.METODOS]
        )

    def test_cada_tarjeta_abre_su_modulo_y_inicio_vuelve(self):
        for nombre in [n for n, _ in gui.METODOS]:
            self.app.vista_actual.tarjetas[nombre].command()
            self.raiz.update()
            self.assertEqual(self.activos(), [nombre])
            self.assertNotIsInstance(self.app.vista_actual, gui.VistaInicio)

            self.app.botones_sidebar[gui.NOMBRE_INICIO].command()
            self.raiz.update()
            self.assertEqual(self.activos(), [gui.NOMBRE_INICIO])

    def test_cambio_de_tema_recolorea_inicio(self):
        self.app.alternar_tema()
        oscuro = gui.PALETAS["oscuro"]
        for hijo in self.app.contenedor.winfo_children():
            if isinstance(hijo, gui.Separador):
                self.assertEqual(hijo.cget("bg"), oscuro["separador"])
            else:
                self.assertEqual(hijo.cget("bg"), oscuro["fondo"])
        self.assertEqual(
            self.app.vista_actual.tarjetas["Pivoteo"].bg, oscuro["boton"]
        )


if __name__ == "__main__":
    unittest.main()
