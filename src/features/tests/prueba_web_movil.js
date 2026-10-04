/*
 * Prueba de la vista móvil de index.html (spec 008). No es parte de la
 * calculadora: necesita playwright-core, un Chromium y un servidor en marcha.
 * Comprueba comportamiento y medidas (scrollWidth, tamaños táctiles, drawer,
 * tema); la apariencia se valida a ojo en un teléfono real.
 *
 *   npm install playwright-core        (en una carpeta temporal)
 *   python server.py 8124              (desde la raíz del proyecto)
 *   PLAYWRIGHT_PATH=<carpeta>/node_modules/playwright-core \
 *   CHROMIUM_PATH=<ruta al ejecutable de chromium> \
 *   node src/features/tests/prueba_web_movil.js
 *
 * Variables opcionales: BASE (por defecto http://127.0.0.1:8124).
 */
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright-core");
const BASE = process.env.BASE || "http://127.0.0.1:8124";
const ANCHOS = [320, 360, 375, 390, 412, 430, 600, 768, 1024];
const MODULOS = ["Inicio", "Gauss-Jordan", "Pivoteo", "Conversión de bases", "Vectores y matrices", "Ejercicios"];
const METODOS_EJERCICIOS = ["Gauss-Jordan", "Pivoteo", "Conversión de bases", "Vectores y matrices"];

let fallos = 0;
const ok = (c, m) => { console.log((c ? "OK   " : "FALLA") + " " + m); if (!c) fallos++; };
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

async function abrir(browser, ancho, alto, extra) {
  const ctx = await browser.newContext(Object.assign(
    { viewport: { width: ancho, height: alto || 740 }, hasTouch: ancho <= 768 }, extra));
  const p = await ctx.newPage();
  p.errores = [];
  p.on("pageerror", (e) => p.errores.push(e.message));
  await p.goto(BASE + "/");
  await esperar(500);
  return p;
}

async function ir(p, nombre) {
  if (await p.isVisible("#btn-menu")) { await p.click("#btn-menu"); await esperar(280); }
  await p.click(`.nav-btn[data-nombre="${nombre}"]`);
  await esperar(300);
}

/* Exceso horizontal de la página y elementos fuera de pantalla que no están
   dentro de un contenedor con scroll horizontal propio. */
function medir(p) {
  return p.evaluate(() => {
    const W = document.documentElement.clientWidth;
    const cortados = [];
    for (const e of document.querySelectorAll("#panel *")) {
      const r = e.getBoundingClientRect();
      if (r.width === 0 || (r.right <= W + 1 && r.left >= -1)) continue;
      let pa = e.parentElement, dentro = false;
      while (pa && pa.id !== "panel") {
        const o = getComputedStyle(pa).overflowX;
        if (o === "auto" || o === "scroll") { dentro = true; break; }
        pa = pa.parentElement;
      }
      if (!dentro) cortados.push(e.tagName.toLowerCase() + "." + e.className + " [" + Math.round(r.left) + "," + Math.round(r.right) + "]");
    }
    return { exceso: document.documentElement.scrollWidth - W, cortados: cortados.slice(0, 4) };
  });
}

/* Rellena los campos visibles: celdas de matriz con diagonal 2 y resto 1
   (sistemas y matrices no singulares), vectores con 1, escalares con 3. */
function rellenar(p) {
  return p.evaluate(() => {
    const visible = (e) => e.getBoundingClientRect().width > 0;
    for (const g of document.querySelectorAll("#panel .grid-matriz, #panel .tabla-genérica")) {
      if (!visible(g)) continue;
      const celdas = [...g.querySelectorAll("input")];
      const cols = getComputedStyle(g).gridTemplateColumns.split(" ").length;
      const sistema = g.classList.contains("grid-matriz");
      const n = sistema ? cols - 1 : cols; // el sistema incluye el separador
      celdas.forEach((c, i) => {
        const fila = Math.floor(i / (sistema ? n : cols)), col = i % (sistema ? n : cols);
        c.value = fila === col ? "2" : "1";
      });
    }
    for (const c of document.querySelectorAll("#panel .columna-vector input")) if (visible(c)) c.value = c.parentElement.textContent.includes("Escalar") ? "3" : "1";
    for (const c of document.querySelectorAll('#panel input[placeholder="Número"]')) c.value = "255";
  });
}

async function calcular(p, etiquetas) {
  for (const t of etiquetas) {
    const b = await p.$(`#panel button:text-is("${t}")`);
    if (b && await b.isVisible()) { await b.click(); await esperar(700); return true; }
  }
  return false;
}

async function barrido(browser, ancho, tema) {
  const p = await abrir(browser, ancho);
  if (tema === "dark") await p.evaluate(() => document.documentElement.setAttribute("data-theme", "dark"));
  const verificar = async (et) => {
    const hayModal = await p.$(".modal-box");
    const m = await medir(p);
    ok(!hayModal && m.exceso <= 0 && m.cortados.length === 0,
      `${ancho}px ${tema} · ${et}` + (hayModal ? " (apareció un modal de error)" : m.exceso > 0 || m.cortados.length ? " " + JSON.stringify(m) : ""));
    if (hayModal) await p.click(".modal-box button");
  };

  for (const mod of MODULOS) {
    await ir(p, mod);
    await verificar(mod);
    if (mod === "Gauss-Jordan" || mod === "Pivoteo") {
      await rellenar(p);
      await calcular(p, ["Mostrar pasos"]);
      await verificar(mod + " con pasos");
      await calcular(p, ["Comprobar resultado"]);
      await verificar(mod + " con comprobación");
    } else if (mod === "Conversión de bases") {
      await rellenar(p);
      await calcular(p, ["Convertir"]);
      await verificar(mod + " con resultado");
    } else if (mod === "Vectores y matrices") {
      for (const t of await p.$$eval(".tab-btn", (e) => e.map((x) => x.textContent))) {
        await p.click(`.tab-btn:has-text("${t}")`);
        await esperar(150);
        await rellenar(p);
        await calcular(p, ["Calcular", "Resolver", "Calcular inversa"]);
        await verificar(`${mod} / ${t}`);
      }
    } else if (mod === "Ejercicios") {
      for (const metodo of METODOS_EJERCICIOS) {
        await p.click(`.inicio-tarjeta:has-text("${metodo}")`);
        await esperar(250);
        await verificar("Ejercicios de " + metodo);
        await p.click(".ejercicios-barra button >> nth=0");
        await esperar(250);
        if (!(await p.$(".inicio-tarjeta"))) await ir(p, "Ejercicios");
      }
    }
  }
  ok(p.errores.length === 0, `${ancho}px ${tema} · sin errores de JS ${p.errores.join("; ")}`);
  await p.context().close();
}

async function pruebaDrawer(browser) {
  const p = await abrir(browser, 360);
  const foco = () => p.evaluate(() => document.activeElement.id);
  ok(!(await p.isVisible("#sidebar")), "drawer cerrado al inicio");
  await p.click("#btn-menu"); await esperar(300);
  ok(await p.isVisible("#sidebar") && (await p.getAttribute("#btn-menu", "aria-expanded")) === "true", "drawer abre (aria-expanded=true)");
  ok(await p.evaluate(() => document.activeElement.classList.contains("nav-btn")), "foco dentro del drawer al abrir");
  await p.keyboard.press("Escape"); await esperar(300);
  ok(!(await p.isVisible("#sidebar")) && (await foco()) === "btn-menu", "Esc cierra y el foco vuelve al botón de menú");
  await p.click("#btn-menu"); await esperar(300);
  await p.mouse.click(345, 400); await esperar(300);
  ok(!(await p.isVisible("#sidebar")) && (await foco()) === "btn-menu", "tocar fuera (overlay) cierra y devuelve el foco");
  await p.click("#btn-menu"); await esperar(300);
  await p.click('.nav-btn[data-nombre="Pivoteo"]'); await esperar(300);
  ok(!(await p.isVisible("#sidebar")) && (await foco()) === "btn-menu", "elegir un módulo cierra y devuelve el foco");
  ok((await p.evaluate(() => localStorage.getItem("sidebar-colapsado"))) === null, "la vista móvil no guarda sidebar-colapsado");

  // Escritorio ↔ móvil: el estado plegado se conserva.
  await p.setViewportSize({ width: 1100, height: 800 }); await esperar(250);
  ok(!(await p.isVisible("#btn-menu")), "escritorio: sin botón de menú");
  await p.click(".btn-colapsar"); await esperar(200);
  await p.setViewportSize({ width: 360, height: 740 }); await esperar(300);
  ok(await p.evaluate(() => !document.getElementById("sidebar").classList.contains("colapsado")) &&
     (await p.evaluate(() => localStorage.getItem("sidebar-colapsado"))) === "1", "móvil: sin clase colapsado y valor guardado intacto");
  await p.setViewportSize({ width: 1100, height: 800 }); await esperar(300);
  ok(await p.evaluate(() => document.getElementById("sidebar").classList.contains("colapsado")), "al ensanchar se restaura el sidebar plegado");
  await p.context().close();
}

async function pruebaMatriz8x8(browser) {
  const p = await abrir(browser, 320);
  await ir(p, "Gauss-Jordan");
  await p.fill(".controles input >> nth=0", "8");
  await p.fill(".controles input >> nth=1", "8");
  await p.click('button:text-is("Crear matriz")');
  const celdas = await p.$$(".grid-matriz input");
  for (let i = 0; i < celdas.length; i++) { const f = Math.floor(i / 9), c = i % 9; await celdas[i].fill(f === c ? "3" : c === 8 ? "-0.5" : "1"); }
  const m = await p.evaluate(() => {
    const e = document.querySelector(".marco-matriz");
    e.scrollLeft = 0;
    const izq = document.querySelector(".grid-matriz input").getBoundingClientRect().left >= e.getBoundingClientRect().left - 0.5;
    e.scrollLeft = e.scrollWidth;
    const der = [...document.querySelectorAll(".grid-matriz input")][8].getBoundingClientRect().right <= e.getBoundingClientRect().right + 1;
    return { sw: e.scrollWidth, cw: e.clientWidth, izq, der, pagina: document.documentElement.scrollWidth - document.documentElement.clientWidth };
  });
  ok(m.sw > m.cw && m.pagina <= 0, `8×8 a 320px: scroll solo del contenedor (${m.sw}/${m.cw}, página +${m.pagina})`);
  ok(m.izq && m.der, "8×8 a 320px: columnas izquierda y derecha alcanzables");
  await p.click('button:text-is("Mostrar pasos")'); await esperar(900);
  const r = await medir(p);
  ok(r.exceso <= 0, "8×8 resuelto con pasos: sin scroll de página");
  await p.context().close();
}

async function pruebaTactil(browser) {
  const p = await abrir(browser, 320, 700, { isMobile: true });
  const sinProblemas = (et) => p.evaluate((et) => {
    const mal = [];
    for (const e of document.querySelectorAll("#panel input[type=text], #panel input[type=number], #panel select")) {
      const r = e.getBoundingClientRect(); if (r.width === 0) continue;
      if (parseFloat(getComputedStyle(e).fontSize) < 16) mal.push("fuente<16");
      if (r.height < 43.5) mal.push("alto<44");
    }
    for (const e of document.querySelectorAll("#panel button, #topbar button, #panel .menu-funciones-boton, #panel label")) {
      const r = e.getBoundingClientRect(); if (r.width === 0) continue;
      if (e.tagName === "LABEL" && !e.querySelector("input[type=radio],input[type=checkbox]")) continue;
      if (r.height < 43.5 || r.width < 43.5) mal.push(e.tagName + " " + (e.textContent || "").trim().slice(0, 14) + " " + Math.round(r.width) + "x" + Math.round(r.height));
    }
    return mal;
  }, et);
  for (const mod of ["Gauss-Jordan", "Conversión de bases", "Vectores y matrices"]) {
    await ir(p, mod);
    const mal = await sinProblemas(mod);
    ok(mal.length === 0, `táctil · ${mod}: campos 16px y objetivos ≥44px ${JSON.stringify(mal.slice(0, 3))}`);
  }
  await ir(p, "Gauss-Jordan");
  const attrs = await p.evaluate(() => { const i = document.querySelector(".grid-matriz input"); const g = (a) => i.getAttribute(a); return g("autocomplete") === "off" && g("autocapitalize") === "off" && g("autocorrect") === "off" && g("spellcheck") === "false" && g("enterkeyhint") === "next" && g("inputmode") === null; });
  ok(attrs, "celdas con autocomplete/autocapitalize/autocorrect/spellcheck/enterkeyhint y sin inputmode");
  const celdas = await p.$$(".grid-matriz input");
  await celdas[0].fill("1/2"); await celdas[1].fill("-3");
  ok((await celdas[0].inputValue()) === "1/2" && (await celdas[1].inputValue()) === "-3", "se pueden teclear 1/2 y -3");
  await rellenar(p); await calcular(p, ["Mostrar pasos"]);
  ok(!(await p.isVisible(".stepper-cabecera")), "stepper: puntos ocultos en móvil");
  const antes = await p.textContent(".stepper-contador");
  await p.click('.stepper-nav button:has-text("Siguiente")');
  ok((await p.textContent(".stepper-contador")) !== antes, "stepper: botón Siguiente avanza el contador");

  // Superpuestos a 320px
  await p.evaluate(() => window.scrollTo(0, 400)); await esperar(200);
  const baja = await p.evaluate(() => document.querySelector(".menu-funciones-boton").getBoundingClientRect().top >= document.getElementById("topbar").getBoundingClientRect().bottom);
  ok(baja, "botón de exportar queda bajo la barra superior al hacer scroll");
  await p.click(".menu-funciones-boton"); await esperar(250);
  const lista = await p.evaluate(() => { const r = document.querySelector(".menu-funciones-lista").getBoundingClientRect(); return r.left >= 0 && r.right <= document.documentElement.clientWidth; });
  ok(lista, "menú de exportar dentro de la pantalla");
  for (const [formato, ext] of [["PNG", ".png"], ["PDF", ".pdf"]]) {
    const [dl] = await Promise.all([p.waitForEvent("download", { timeout: 8000 }).catch(() => null), p.click(`.menu-funciones-lista button:has-text("${formato}")`)]);
    ok(!!dl && dl.suggestedFilename().endsWith(ext), `descarga ${formato} disparada ${dl ? dl.suggestedFilename() : ""}`);
    await esperar(300);
    const toast = await p.evaluate(() => { const t = document.querySelector(".toast"); if (!t) return null; const r = t.getBoundingClientRect(); return r.left >= 15.5 && r.right <= 304.5 && r.bottom <= window.innerHeight - 15.5 && !!t.querySelector("a"); });
    ok(toast, `aviso de ${formato} dentro de la pantalla y con enlace "Abrir"`);
    await p.evaluate(() => document.querySelectorAll(".toast").forEach((t) => t.remove()));
    if (formato === "PNG") { await p.click(".menu-funciones-boton"); await esperar(250); }
  }
  await p.fill(".controles input >> nth=0", "0"); await p.click('button:text-is("Crear matriz")'); await esperar(300);
  const modal = await p.evaluate(() => { const r = document.querySelector(".modal-box").getBoundingClientRect(); return r.left >= 15.5 && r.right <= document.documentElement.clientWidth - 15.5; });
  ok(modal, "modal a ≥16px de los bordes");
  await p.context().close();
}

async function pruebaTema(browser) {
  const p = await abrir(browser, 360, 740, { colorScheme: "light" });
  await ir(p, "Gauss-Jordan");
  await rellenar(p); await calcular(p, ["Mostrar pasos"]);
  const estado = () => p.evaluate(() => ({
    celdas: [...document.querySelectorAll(".grid-matriz input")].map((i) => i.value).join(","),
    hijos: document.querySelector(".resultado-panel").childNodes.length,
    tema: document.documentElement.getAttribute("data-theme"),
  }));
  const antes = await estado();
  await p.click("#btn-menu"); await esperar(280);
  await p.click(".btn-tema"); await esperar(300);
  const despues = await estado();
  ok(despues.tema === "dark" && despues.celdas === antes.celdas && despues.hijos === antes.hijos, "cambiar a oscuro conserva datos y resultados");
  ok((await p.evaluate(() => localStorage.getItem("tema-calculadora"))) === "dark", "el tema se guarda en localStorage");
  await p.reload(); await esperar(500);
  ok((await p.evaluate(() => document.documentElement.getAttribute("data-theme"))) === "dark", "al recargar sigue el tema oscuro");
  await p.click("#btn-menu"); await esperar(280); await p.click(".btn-tema"); await esperar(250);
  ok((await p.evaluate(() => document.documentElement.getAttribute("data-theme"))) === "light", "se puede volver a claro");
  await p.context().close();
}

/* Contraste del texto visible en móvil, en ambos temas (mínimo 4.5:1, 3:1 en
   texto grande). Se ignoran controles deshabilitados y marcadores de posición. */
async function pruebaContraste(browser) {
  for (const tema of ["light", "dark"]) {
    const p = await abrir(browser, 360);
    await p.evaluate((t) => document.documentElement.setAttribute("data-theme", t), tema);
    for (const mod of ["Inicio", "Gauss-Jordan", "Conversión de bases", "Vectores y matrices", "Ejercicios"]) {
      await ir(p, mod);
      if (mod === "Gauss-Jordan") { await rellenar(p); await calcular(p, ["Mostrar pasos"]); await calcular(p, ["Comprobar resultado"]); }
      const bajos = await p.evaluate(() => {
        const parse = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(",").map(Number); return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 }; };
        const lum = ({ r, g, b }) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
        const mezclar = (fg, bg) => ({ r: fg.r * fg.a + bg.r * (1 - fg.a), g: fg.g * fg.a + bg.g * (1 - fg.a), b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1 });
        const fondo = (e) => { const capas = []; for (let n = e; n; n = n.parentElement) { const c = parse(getComputedStyle(n).backgroundColor); if (c && c.a > 0) { capas.push(c); if (c.a === 1) break; } } let base = { r: 255, g: 255, b: 255, a: 1 }; for (const c of capas.reverse()) base = mezclar(c, base); return base; };
        const mal = [];
        for (const e of document.querySelectorAll("#panel *, #topbar *, #sidebar *")) {
          if (e.disabled || e.closest("[disabled]")) continue;
          const propio = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
          const r = e.getBoundingClientRect();
          if (!propio || r.width === 0 || r.height === 0) continue;
          if (e.closest("#sidebar") && !document.getElementById("sidebar").classList.contains("abierto")) continue;
          const cs = getComputedStyle(e);
          if (cs.visibility === "hidden" || cs.opacity === "0") continue;
          const bg = fondo(e), fg = mezclar(parse(cs.color), bg);
          const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
          const grande = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.66 && parseInt(cs.fontWeight) >= 700);
          if (ratio < (grande ? 3 : 4.5)) mal.push(e.tagName.toLowerCase() + "." + e.className + " '" + e.textContent.trim().slice(0, 18) + "' " + ratio.toFixed(2));
        }
        return mal.slice(0, 5);
      });
      ok(bajos.length === 0, `contraste ${tema} · ${mod} ${JSON.stringify(bajos)}`);
    }
    await p.context().close();
  }
}

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined, args: ["--no-sandbox"],
  });
  for (const ancho of ANCHOS) await barrido(browser, ancho, "light");
  for (const ancho of [320, 390]) await barrido(browser, ancho, "dark");
  await pruebaDrawer(browser);
  await pruebaMatriz8x8(browser);
  await pruebaTactil(browser);
  await pruebaTema(browser);
  await pruebaContraste(browser);
  await browser.close();
  console.log(fallos === 0 ? "\nTodo correcto." : `\n${fallos} comprobación(es) fallaron.`);
  process.exit(fallos === 0 ? 0 : 1);
})();
