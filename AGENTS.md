# Instrucciones para agentes — www (kosgroup.es)

Web corporativa estática de KOS Group (KEY OUTSOURCING SERVICES GROUP SL) en https://www.kosgroup.es. Sirve de
página pública de la empresa, entre otras cosas para verificar la organización en Apple y Google. **El repositorio es
público**: no escribas aquí secretos, IP o nombres de máquinas internas, ni nombres de clientes.

## Antes de empezar

`git fetch` y `git pull --rebase` de `main`. Si hay conflictos, **para y pregunta**. Para trabajar en otra rama, usa
`git worktree` y bórralo al terminar, junto con la rama local.

## Estructura

```
site/               HTML + CSS estáticos (sin JavaScript, sin cookies, sin recursos externos)
  index, servicios, soluciones, rinc, portame, integra, boss, nosotros, aviso-legal, privacidad, 404 (.html)
  img/              logo (y su versión pequeña -sm), ilustraciones ill-*.svg, iconos icons.svg (sprite <symbol>)
  media/            vídeo corporativo (kosgroup.mp4/.webm + kosgroup-poster.jpg) cuando exista
  sitemap.xml, robots.txt
tools/illustrations.py  genera las ilustraciones isométricas site/img/ill-*.svg (python -I tools/illustrations.py)
nginx/default.conf  nginx en el 8080: URL limpias, cabeceras de seguridad, apex -> www, /healthz
Dockerfile          nginxinc/nginx-unprivileged (usuario 101)
K8S/produccion/     Namespace `kosgroup`, Deployment y Service `www`
.github/workflows/  CI: imagen, prueba de humo, push a ghcr y tag fijado en K8S
```

## Normas

- Textos en español. Commits en inglés; PRs en español. Ramas de ≤ 15 caracteres.
- Contenido sacado de la presentación corporativa del grupo (sep. 2025), de rinc.es y de la documentación de Integra,
  reescrito en tono comercial: textos cortos y orientados a beneficio. Idea fuerza: conocemos el negocio desde dentro y
  diseñamos desde su necesidad real. **Sin clientes** (ni nombres, ni logos, ni casos), **sin precios** ni modalidades
  de cobro, **sin listado de sociedades del grupo** y sin nombres de proveedores u operadores integrados.
- **Sin correo electrónico ni teléfono en ninguna página** (ni `mailto:` ni `tel:`; el CI lo comprueba): el único dato
  de contacto público es el domicilio social. Los derechos de protección de datos se ejercen por escrito en él.
- Multipágina con URL limpias en la raíz (`/rinc`, no `/soluciones/rinc`: así no conviven `x.html` y `x/`). Cabecera y
  pie son iguales en todas las páginas salvo `aria-current="page"`: si cambias uno, cámbialo en todas.
- Logo: `site/img/kosgroup-logo.png`, extraído de esa presentación (PNG con transparencia); el favicon es el símbolo del
  hexágono recortado del mismo logo. Paleta: los colores del logo (azul `#1761A0`, gris `#9E9E9E`) y tonos suyos, más
  **un único acento naranja `#F7931E`** solo para llamadas a la acción, detalles y grafismos (botón naranja con texto
  marino `#0B2540`; texto naranja sobre blanco siempre en `#B4530A`, que da AA). No uses los colores de la plantilla de
  la presentación. Sin modo oscuro (el logo es para fondo claro).
- Imágenes: vector art propio (SVG isométricos generados por `tools/illustrations.py`, iconos de línea propios). No hay
  fotos; si se añaden, solo de Unsplash o Pexels, en webp de menos de 200 KB y anotando aquí su procedencia. Los SVG
  usan solo atributos de presentación (la CSP prohíbe estilos en línea) y no deben contener la cadena `659`.
- Sin cookies, analítica ni recursos de terceros (fuentes, CDN): la política de privacidad dice que no los hay. Si se
  añade algo así, hay que cambiar antes la política y el aviso legal.
- Los datos legales (razón social, CIF, domicilio) aparecen en el pie de cada página, en `aviso-legal.html`
  y en `privacidad.html`: cámbialos en todos a la vez. No inventes datos registrales.
- La CSP de `nginx/default.conf` prohíbe scripts y estilos en línea (también `style=` y `<style>` dentro de SVG); si
  los necesitas, ajusta la CSP en sus dos copias. El menú no usa JavaScript.
- Sin tests unitarios ni mutation testing (no hay código): la prueba es el paso de humo del CI.

## Despliegue

Push a `main` → el CI publica `ghcr.io/kos-group/www:<run_number>` y fija ese tag en `K8S/produccion/www.yaml`
(commit `[skip ci]`); la Application `kosgroup-www` de ArgoCD (en el repo `Avanware/infra`, cluster C) lo despliega.
El paquete de ghcr es privado: el namespace `kosgroup` necesita el pull secret `ghcr.io` (fuera de git; se copia del
namespace `workcheckin`). El enrutado de `www.kosgroup.es` y `kosgroup.es` y el certificado TLS están en la configuración de Traefik del cluster,
fuera de este repo.

Prueba local: `docker build -t www . && docker run --rm -p 8080:8080 www` y abre http://localhost:8080.
