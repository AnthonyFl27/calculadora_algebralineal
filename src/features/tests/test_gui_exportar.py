"""Menú ☰ de exportación de la GUI (Tkinter): estado, guardado y tema."""

import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

import main as gui
from metodos.ejercicios import EJERCICIOS, METODOS_EJERCICIOS

NOMBRES = dict(METODOS_EJERCICIOS)
CALCULAR = {
    "vectores": "_calcular_vectores",
    "matrices": "_calcular_matrices",
    "ecuacion-matricial": "_calcular_ecuacion",
    "inversa": "_calcular_inversa",
}


class MenuExportarGuiTests(unittest.TestCase):

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
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)

    def tearDown(self):
        self.app.contenedor.destroy()
        self.app.sidebar.destroy()

    def abrir(self, clave, ejercicio=None):
        nombre = NOMBRES[clave]
        self.app.mostrar_vista(dict(gui.METODOS)[nombre], nombre, ejercicio)
        self.raiz.update()
        return self.app.vista_actual

    def estados(self):
        """Estado de las entradas PNG y PDF tras abrir el menú."""
        boton = self.app.menu_funciones
        boton._armar_menu()
        return [boton.menu.entrycget(i, "state") for i in (0, 1)]

    def exportar(self, formato, nombre="salida"):
        ruta = os.path.join(self.carpeta.name, f"{nombre}.{formato}")
        with patch("main.filedialog.asksaveasfilename", return_value=ruta), \
                patch("main.messagebox.showinfo") as info, \
                patch("main.messagebox.showerror") as error:
            self.app.menu_funciones.exportar(formato)
        error.assert_not_called()
        return ruta, info

    def test_no_aparece_en_inicio_ni_en_ejercicios(self):
        self.assertIsNone(self.app.menu_funciones)
        self.app.mostrar_ejercicios()
        self.raiz.update()
        self.assertIsNone(self.app.menu_funciones)

    def test_aparece_en_los_cuatro_metodos(self):
        for clave in NOMBRES:
            with self.subTest(clave):
                self.abrir(clave)
                self.assertIsInstance(self.app.menu_funciones, gui.BotonMenu)
                # Ícono de descarga: flecha (2 trazos), bandeja y punto.
                self.assertEqual(len(self.app.menu_funciones.find_all()), 4)

    def test_sistema_deshabilitado_hasta_resolver_y_tras_limpiar(self):
        for clave in ("gauss-jordan", "pivoteo"):
            with self.subTest(clave):
                vista = self.abrir(clave, EJERCICIOS[clave][0])
                self.assertEqual(self.estados(), ["disabled", "disabled"])
                with patch("main.messagebox.showwarning") as aviso:
                    self.app.menu_funciones.exportar("pdf")
                aviso.assert_called_once()

                vista.resolver_sistema()
                self.assertEqual(self.estados(), ["normal", "normal"])

                vista.limpiar_matriz()
                self.assertEqual(self.estados(), ["disabled", "disabled"])

    def test_exporta_pdf_y_png_de_sistema(self):
        vista = self.abrir("gauss-jordan", EJERCICIOS["gauss-jordan"][0])
        vista.resolver_sistema()
        ruta, info = self.exportar("pdf")
        with open(ruta, "rb") as archivo:
            self.assertTrue(archivo.read().startswith(b"%PDF-"))
        info.assert_called_once()

        ruta, _ = self.exportar("png")
        with open(ruta, "rb") as archivo:
            self.assertTrue(archivo.read().startswith(b"\x89PNG"))

    def test_incluir_pasos_cambia_el_archivo(self):
        vista = self.abrir("gauss-jordan", EJERCICIOS["gauss-jordan"][0])
        vista.resolver_sistema()
        boton = self.app.menu_funciones
        con, _ = self.exportar("png", "con")
        boton.incluir_pasos.set(False)
        sin, _ = self.exportar("png", "sin")
        self.assertLess(os.path.getsize(sin), os.path.getsize(con))

    def test_modo_decimal_se_conserva_al_exportar(self):
        vista = self.abrir("gauss-jordan", EJERCICIOS["gauss-jordan"][0])
        vista.modo.set("decimal")
        vista.resolver_sistema()
        modulo, resultado, modo, titulo = vista.obtener_exportable()
        self.assertEqual((modulo, modo, titulo), ("sistema", "decimal", "Gauss-Jordan"))

    def test_cancelar_el_dialogo_no_escribe_nada(self):
        vista = self.abrir("pivoteo", EJERCICIOS["pivoteo"][0])
        vista.resolver_sistema()
        with patch("main.filedialog.asksaveasfilename", return_value=""), \
                patch("main.messagebox.showinfo") as info, \
                patch("main.messagebox.showerror") as error:
            self.app.menu_funciones.exportar("pdf")
        info.assert_not_called()
        error.assert_not_called()

    def test_error_al_guardar_muestra_mensaje_amigable(self):
        vista = self.abrir("pivoteo", EJERCICIOS["pivoteo"][0])
        vista.resolver_sistema()
        ruta = os.path.join(self.carpeta.name, "no_existe", "x.pdf")
        with patch("main.filedialog.asksaveasfilename", return_value=ruta), \
                patch("main.messagebox.showerror") as error:
            self.app.menu_funciones.exportar("pdf")
        error.assert_called_once()
        self.assertIn("No se pudo guardar", error.call_args[0][1])

    def test_conversion_y_vectores_matrices(self):
        vista = self.abrir("conversion", EJERCICIOS["conversion"][0])
        self.assertEqual(self.estados(), ["disabled", "disabled"])
        vista.convertir()
        self.assertEqual(self.estados(), ["normal", "normal"])
        self.exportar("pdf", "conversion")

        for ejercicio in EJERCICIOS["vectores-matrices"]:
            with self.subTest(ejercicio["id"]):
                vista = self.abrir("vectores-matrices", ejercicio)
                self.assertEqual(self.estados(), ["disabled", "disabled"])
                getattr(vista, CALCULAR[ejercicio["categoria"]])()
                self.assertEqual(self.estados(), ["normal", "normal"])
                ruta, _ = self.exportar("png", ejercicio["id"])
                self.assertGreater(os.path.getsize(ruta), 0)

    def test_cambiar_de_tema_recolorea_el_menu(self):
        self.abrir("gauss-jordan")
        boton = self.app.menu_funciones
        self.app.aplicar_tema("oscuro")
        self.raiz.update()
        self.assertEqual(str(boton.cget("bg")).lower(),
                         gui.PALETAS["oscuro"]["fondo"])
        colores = {str(boton.itemcget(i, "fill")).lower()
                   for i in boton.find_withtag("trazo")}
        self.assertEqual(colores, {gui.PALETAS["oscuro"]["acento"]})
        self.assertIs(self.app.menu_funciones, boton)


if __name__ == "__main__":
    unittest.main()
