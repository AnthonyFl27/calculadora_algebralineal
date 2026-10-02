/*
 * Prueba del menú ☰ de exportación de index.html (comportamiento, no
 * apariencia). No es parte de la calculadora: necesita jsdom y un servidor
 * en marcha.
 *
 *   npm install jsdom            (en una carpeta temporal)
 *   python server.py 8124      (desde la raíz del proyecto)
 *   node src/features/tests/prueba_web_menu.js
 */
const { JSDOM } = require(process.env.JSDOM_PATH || "jsdom");
const BASE = "http://127.0.0.1:8124";
const esperar = (ms) => new Promise(r => setTimeout(r, ms));
let fallos = 0;
const ok = (c, m) => { console.log((c ? "OK   " : "FALLA") + " " + m); if (!c) fallos++; };

(async () => {
  const dom = await JSDOM.fromURL(BASE + "/", {
    runScripts: "dangerously", resources: "usable", pretendToBeVisual: true,
    beforeParse(w) {
      w.fetch = (url, op) => fetch(new URL(url, BASE), op).then(r => { w.__ultima = {url, op}; return r; });
      w.URL.createObjectURL = () => "blob:x";
      w.URL.revokeObjectURL = () => {};
      w.HTMLAnchorElement.prototype.click = function () { w.__descarga = this.download; };
      w.matchMedia = w.matchMedia || (() => ({ matches: false, addEventListener() {}, addListener() {} }));
    },
  });
  const w = dom.window, d = w.document;
  await esperar(500);
  const nav = (n) => [...d.querySelectorAll(".nav-btn")].find(b => b.dataset.nombre === n).click();
  const boton = () => d.querySelector(".menu-funciones-boton");

  ok(!boton(), "Inicio: sin menú");
  nav("Gauss-Jordan"); await esperar(100);
  ok(boton(), "Gauss-Jordan: hay botón ☰");
  ok(boton().getAttribute("aria-disabled") === "true", "deshabilitado sin resultado");
  ok(boton().title.includes("Resuelve primero"), "tooltip");
  boton().click();
  ok(d.querySelector(".modal-box"), "clic sin resultado muestra aviso");
  d.querySelector(".modal-box .btn").click();

  const entradas = [...d.querySelectorAll(".grid-matriz input")];
  const v = [2,1,-1,8,-3,-1,2,-11,-2,1,2,-3];
  entradas.forEach((e, i) => e.value = String(v[i]));
  [...d.querySelectorAll("button")].find(b => b.textContent === "Resolver").click();
  await esperar(300);
  await esperar(100);
  ok(boton().getAttribute("aria-disabled") === "false", "habilitado tras resolver");
  boton().click();
  const lista = d.querySelector(".menu-funciones-lista");
  ok(!lista.hidden && boton().getAttribute("aria-expanded") === "true", "menú se despliega");
  const items = [...lista.querySelectorAll("button")].map(b => b.textContent);
  ok(items.join("|") === "Exportar como PNG|Exportar como PDF", "opciones: " + items);
  ok(lista.querySelector("input[type=checkbox]").checked, "Incluir pasos marcado");

  lista.querySelector("input").click();                 // desmarca
  [...lista.querySelectorAll("button")][1].click();     // PDF
  await esperar(400);
  const cuerpo = JSON.parse(w.__ultima.op.body);
  ok(cuerpo.formato === "pdf" && cuerpo.incluir_pasos === false && cuerpo.modulo === "sistema", "petición: " + JSON.stringify({...cuerpo, datos: "…"}));
  ok(/^gauss-jordan-.*\.pdf$/.test(w.__descarga || ""), "descarga: " + w.__descarga);
  ok(d.querySelector(".toast"), "toast de confirmación");
  ok(lista.hidden, "menú cerrado al elegir");

  boton().click();
  d.dispatchEvent(new w.KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
  lista.dispatchEvent(new w.KeyboardEvent("keydown", {key: "Escape", bubbles: true}));
  ok(lista.hidden, "Esc cierra");
  boton().click();
  d.body.click();
  ok(lista.hidden, "clic fuera cierra");

  // limpiar -> se deshabilita
  [...d.querySelectorAll("button")].find(b => b.textContent === "Limpiar").click();
  await esperar(50);
  ok(boton().getAttribute("aria-disabled") === "true", "Limpiar deshabilita");

  // Conversión
  nav("Conversión de bases"); await esperar(100);
  ok(boton() && boton().getAttribute("aria-disabled") === "true", "Conversión: menú presente y deshabilitado");
  d.querySelector("input[type=text]").value = "255";
  [...d.querySelectorAll("button")].find(b => /Convertir/.test(b.textContent)).click();
  await esperar(300);
  ok(boton().getAttribute("aria-disabled") === "false", "Conversión: habilitado");

  // Vectores y matrices: cambiar de pestaña deshabilita
  nav("Vectores y matrices"); await esperar(100);
  const ents = [...d.querySelectorAll(".tab-contenido.activa input[type=text]")];
  ents.forEach((e, i) => e.value = String(i + 1));
  [...d.querySelectorAll("button")].find(b => b.textContent === "Calcular").click();
  await esperar(300);
  ok(boton().getAttribute("aria-disabled") === "false", "Vectores: habilitado");
  [...d.querySelectorAll(".tab-btn")][1].click(); await esperar(50);
  ok(boton().getAttribute("aria-disabled") === "true", "cambiar pestaña deshabilita");

  nav("Ejercicios"); await esperar(100);
  ok(!boton(), "Ejercicios: sin menú");
  nav("Inicio"); await esperar(50);
  ok(!boton(), "Inicio: sin menú");
  console.log(fallos ? `\n${fallos} FALLOS` : "\nTODO OK");
  w.close(); process.exit(fallos ? 1 : 0);
})();
