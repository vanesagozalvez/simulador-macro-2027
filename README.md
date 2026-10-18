# Simulador macro Argentina 2027

Escenarios base, optimista y pesimista a partir de un modelo IS-LM-BP de dos sectores (versión 6). La web recalcula en el navegador al cambiar los supuestos.

## Estructura
- `src/engine.js`: motor trimestral (T4-2026 a T4-2027), port a JS de `python/build_xlsx.py`. Coincide con la planilla recalculada (diferencias menores a 0,1 millón por redondeo de la planilla de deuda).
- `src/data/`: respuestas por unidad de shock (`set_A.json`, `set_B.json`) y deuda mensual (MECON, 30/06/2026).
- `python/`: scripts originales. `make_sets.py` recalibra los juegos; `build_xlsx.py 1 salida.xlsx sens.json` arma la planilla.

## Uso
```bash
npm install
npm run dev      # desarrollo
npm run build    # genera dist/
```

## Deploy en Vercel
1. Subir a GitHub: `git init && git add . && git commit -m "Simulador macro 2027" && git branch -M main && git remote add origin <URL> && git push -u origin main`
2. En vercel.com: **Add New → Project**, importar el repositorio. Vercel detecta Vite (build `vite build`, salida `dist`); no requiere variables de entorno.

Parámetros ilustrativos, no estimados. Los datos de usuario no fueron verificados por el analista. Los resultados no son pronósticos.
