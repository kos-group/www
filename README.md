# www.kosgroup.es

Web corporativa de KOS Group (KEY OUTSOURCING SERVICES GROUP SL): página estática servida con nginx.

```
docker build -t www .
docker run --rm -p 8080:8080 www
```

Despliegue e instrucciones de mantenimiento en [AGENTS.md](AGENTS.md).
