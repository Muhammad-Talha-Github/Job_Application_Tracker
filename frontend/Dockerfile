FROM node:22-alpine

WORKDIR /app

# Install from the lockfile to get the same frontend dependencies each build.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite embeds VITE_* values into the built JavaScript, so set this at image build time.
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

EXPOSE 5173

# Vite preview serves the built frontend and binds to the container network interface.
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "5173"]
