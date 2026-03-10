# Usar imagen oficial de Python
FROM python:3.12-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Crear directorio de uploads
RUN mkdir -p static/uploads/evidencias static/uploads/levantamientos

# Railway inyecta PORT automáticamente, usar 8080 como fallback
ENV PORT=8080

# Comando de inicio simple
CMD python app.py