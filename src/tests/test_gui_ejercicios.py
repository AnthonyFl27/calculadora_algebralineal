"""Los ejercicios del catálogo se cargan en las vistas de la GUI y se pueden
resolver con los controles normales (sin errores)."""

import tkinter as tk
import unittest
from unittest.mock import patch

import main as gui
from metodos.ejercicios import EJERCICIOS, METODOS_EJERCICIOS

NOMBRES = dict(METODOS_EJERCICIOS)
PESTANAS = {
    "vectores": "tab_vectores",
    "matrices": "tab_matrices",
    "ecuacion-matricial": "tab_ecuacion",
    "inversa": "tab_inversa",
}
CALCULAR = {
    "vectores": "_calcular_vectores",
    "matrices": "_calcular_matrices",
    "ecuacion-matricial": "_calcular_ecuacion",
    "inversa": "_calcular_inversa",
}


def textos_de(datos):
    """Todos los valores de texto de los datos de un ejercicio, en orden."""
    if isinstance(datos, dict):
        return [t for v in datos.values() for t in textos_de(v)]
    if isinstance(datos, list):
        return [t for v in datos for t in textos_de(v)]
    return [datos] if isinstance(datos, str) else []


def texto_de_entradas(widget):
    """Contenido de todos los Entry de un widget, recorriendo el árbol."""
    valores = []
    for hijo in widget.winfo_children():
        if isinstance(hijo, tk.Entry):
            valores.append(hijo.get())
        valores.extend(texto_de_entradas(hijo))
    return valores


def etiquetas(widget):
    """Textos de todos los Label de un widget, recorriendo el árbol."""
    textos = []
    for hijo in widget.winfo_children():
        if isinstance(hijo, tk.Label):
            textos.append(hijo.cget("text"))
        textos.extend(etiquetas(hijo))
    return textos


class EjerciciosGuiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.raiz = tk.Tk()
        except tk.TclError as error:
            raise unittest.SkipTest(f"Tkinter no disponible: {error}")
        cls.raiz.withdraw()
        cls.app = gui.Aplicacion(cls.raiz)

    @classmethod
    def tearDownClass(cls):
        cls.raiz.destroy()

    def fabrica(self, clave):
        nombre = NOMBRES[clave]
        return nombre, dict(gui.METODOS)[nombre]

    def abrir(self, clave, ejercicio):
        nombre, fabrica = self.fabrica(clave)
        self.app.mostrar_vista(fabrica, nombre, ejercicio)
        self.raiz.update()
        return self.app.vista_actual

    def test_cada_ejercicio_carga_sus_datos_y_se_resuelve(self):
        for clave, lista in EJERCICIOS.items():
            for ejercicio in lista:
                with self.subTest(ejercicio["id"]), \
                        patch("main.messagebox.showerror") as error, \
                        patch("main.messagebox.showwarning") as aviso:
                    vista = self.abrir(clave, ejercicio)

                    # Los datos quedaron en los campos.
                    en_campos = texto_de_entradas(self.app.contenedor)
                    for texto in textos_de(ejercicio["datos"]):
                        self.assertIn(texto, en_campos)
                        en_campos.remove(texto)

                    # Se resuelve con los controles normales.
                    if clave in ("gauss-jordan", "pivoteo"):
                        vista.resolver_sistema()
                    elif clave == "conversion":
                        vista.convertir()
                    else:
                        getattr(vista, CALCULAR[ejercicio["categoria"]])()

                    error.assert_not_called()
                    aviso.assert_not_called()
                    self.assertTrue(vista.salida.get("1.0", tk.END).strip())

    def test_vectores_y_matrices_abre_la_pestana_de_la_operacion(self):
        for ejercicio in EJERCICIOS["vectores-matrices"]:
            with self.subTest(ejercicio["id"]):
                vista = self.abrir("vectores-matrices", ejercicio)
                activa = vista.pestanas.nametowidget(vista.pestanas.select())
                self.assertIs(activa, getattr(vista, PESTANAS[ejercicio["categoria"]]))

    # ---- Flujo de la sección: Inicio -> elección -> lista -> probar ----

    def activos(self):
        return [n for n, b in self.app.botones_sidebar.items() if b.activo]

    def test_flujo_completo_desde_inicio(self):
        self.app.mostrar_inicio()
        self.raiz.update()
        self.app.vista_actual.tarjeta_ejercicios.command()
        self.raiz.update()

        vista = self.app.vista_actual
        self.assertIsInstance(vista, gui.VistaEjercicios)
        self.assertEqual(self.activos(), [gui.NOMBRE_EJERCICIOS])
        self.assertEqual(list(vista.opciones), [c for c, _ in METODOS_EJERCICIOS])

        for clave, nombre in METODOS_EJERCICIOS:
            vista.opciones[clave].command()
            self.raiz.update()
            self.assertIn(f"Ejercicios de {nombre}", etiquetas(self.app.contenedor))

            with patch("main.messagebox.showerror"):
                vista.al_probar(clave, EJERCICIOS[clave][0])
            self.raiz.update()
            self.assertEqual(self.activos(), [nombre])
            self.assertNotIsInstance(self.app.vista_actual, gui.VistaEjercicios)

            self.app.mostrar_ejercicios()
            self.raiz.update()
            vista = self.app.vista_actual

    def probar_desde_la_lista(self, clave, indice):
        """Pulsa el botón 'Probar ejercicio' de la lista, como un usuario."""
        self.app.mostrar_ejercicios()
        vista = self.app.vista_actual
        vista.opciones[clave].command()
        self.raiz.update()

        def botones(widget):
            for hijo in widget.winfo_children():
                if isinstance(hijo, gui.RoundedButton) and hijo.text == "Probar ejercicio":
                    yield hijo
                yield from botones(hijo)

        lista = list(botones(self.app.contenedor))
        self.assertEqual(len(lista), len(EJERCICIOS[clave]))
        lista[indice].command()
        self.raiz.update()

    def test_boton_probar_ejercicio_carga_los_datos(self):
        self.probar_desde_la_lista("gauss-jordan", 1)
        vista = self.app.vista_actual
        self.assertEqual(
            [e.get() for fila in vista.entradas for e in fila],
            [c for fila in EJERCICIOS["gauss-jordan"][1]["datos"]["matriz"]
             for c in fila],
        )

        self.probar_desde_la_lista("vectores-matrices", 10)
        vista = self.app.vista_actual
        self.assertEqual(
            vista.pestanas.nametowidget(vista.pestanas.select()), vista.tab_inversa
        )

    def test_atras_e_inicio(self):
        self.app.mostrar_ejercicios()
        vista = self.app.vista_actual
        vista.mostrar_lista("pivoteo", "Pivoteo")
        self.raiz.update()
        vista.mostrar_eleccion()
        self.raiz.update()
        self.assertEqual(list(vista.opciones), [c for c, _ in METODOS_EJERCICIOS])
        vista.al_inicio()
        self.raiz.update()
        self.assertIsInstance(self.app.vista_actual, gui.VistaInicio)
        self.assertEqual(self.activos(), [gui.NOMBRE_INICIO])

    def test_cambio_de_tema_recolorea_la_lista(self):
        self.app.mostrar_ejercicios()
        self.app.vista_actual.mostrar_lista("gauss-jordan", "Gauss-Jordan")
        self.raiz.update()
        etiquetas = []

        def buscar(widget):
            for hijo in widget.winfo_children():
                if isinstance(hijo, gui.EtiquetaDificultad):
                    etiquetas.append(hijo)
                buscar(hijo)

        buscar(self.app.contenedor)
        self.assertTrue(etiquetas)
        self.app.alternar_tema()
        oscuro = gui.PALETAS["oscuro"]
        for etiqueta in etiquetas:
            self.assertEqual(etiqueta.cget("fg"), oscuro["dif_" + etiqueta.nivel])
            self.assertEqual(etiqueta.cget("bg"), oscuro["fondo"])
        self.assertEqual(self.app.vista_actual.lienzo.cget("bg"), oscuro["fondo"])
        self.app.alternar_tema()

    def test_sin_ejercicio_las_vistas_abren_como_siempre(self):
        for nombre, fabrica in gui.METODOS:
            self.app.mostrar_vista(fabrica, nombre)
            self.assertNotEqual(self.app.vista_actual, None)


if __name__ == "__main__":
    unittest.main()
