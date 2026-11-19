FROM node:20-alpine AS build

ARG VITE_API_URL=http://127.0.0.1:8000
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# nginx corre como usuario no root: necesita escribir en la raiz, la cache y /var/run.
# El puerto interno pasa a 8080 porque el puerto 80 requiere root (o CAP_NET_BIND_SERVICE).
RUN sed -i 's|^pid[[:space:]]*/run/nginx.pid;|pid        /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
    && chown -R nginx:nginx /usr/share/nginx/html /var/cache/nginx /var/run \
    && chmod -R 755 /usr/share/nginx/html

USER nginx

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
