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
nginx/default.conf  nginx en el 8080: URL limpias, cabeceras de seguridad, apex -> www, /healthz
Dockerfile          nginxinc/nginx-unprivileged (usuario 101)
K8S/produccion/     Namespace `kosgroup`, Deployment y Service `www`
.github/workflows/  CI: imagen, prueba de humo, push a ghcr y tag fijado en K8S
```

## Normas

- Textos en español. Commits en inglés; PRs en español. Ramas de ≤ 15 caracteres.
- Sin cookies, analítica ni recursos de terceros (fuentes, CDN): la política de privacidad dice que no los hay. Si se
  añade algo así, hay que cambiar antes la política y el aviso legal.
- Los datos legales (razón social, CIF, domicilio, contacto) aparecen en el pie de cada página, en `aviso-legal.html`
  y en `privacidad.html`: cámbialos en todos a la vez. No inventes datos registrales.
- La CSP de `nginx/default.conf` prohíbe scripts y estilos en línea; si los necesitas, ajusta la CSP.
- Sin tests unitarios ni mutation testing (no hay código): la prueba es el paso de humo del CI.

## Despliegue

Push a `main` → el CI publica `ghcr.io/kos-group/www:<run_number>` y fija ese tag en `K8S/produccion/www.yaml`
(commit `[skip ci]`); la Application `kosgroup-www` de ArgoCD (en el repo `Avanware/infra`, cluster C) lo despliega.
El paquete de ghcr es privado: el namespace `kosgroup` necesita el pull secret `ghcr.io` (fuera de git; se copia del
namespace `workcheckin`). El enrutado de `www.kosgroup.es` y `kosgroup.es` y el certificado TLS están en la configuración de Traefik del cluster,
fuera de este repo.

Prueba local: `docker build -t www . && docker run --rm -p 8080:8080 www` y abre http://localhost:8080.
