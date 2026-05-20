# --- ÉTAPE 1 : BUILD (Lourd, mais temporaire) ---
FROM node:20-alpine AS builder

WORKDIR /app

# Cache des dépendances
COPY package*.json ./
RUN npm ci

# Copie du code source et compilation
COPY . .
RUN npm run build

# --- ÉTAPE 2 : PRODUCTION (Ultra-léger) ---
FROM nginx:alpine

# Copie uniquement des fichiers statiques générés (HTML, CSS, JS)
COPY --from=builder /app/dist /usr/share/nginx/html

# Modification à la volée de la configuration Nginx par défaut 
# pour supporter le Vue Router (Redirection de toutes les requêtes vers index.html)
RUN sed -i 's/index  index.html index.htm;/index  index.html index.htm;\n        try_files $uri $uri\/ \/index.html;/g' /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
