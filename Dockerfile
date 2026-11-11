# Web estática de KOS Group: nginx sin privilegios (usuario 101, puerto 8080).
FROM nginxinc/nginx-unprivileged:1.31.7-alpine
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/
EXPOSE 8080
