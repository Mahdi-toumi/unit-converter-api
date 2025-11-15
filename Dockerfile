# =============================================================================
# Stage 1: Builder - Installation des dépendances
# =============================================================================
FROM python:3.11-slim AS  builder

# Métadonnées de l'image
LABEL maintainer="toumi.mahdi.cr7@gmail.com"
LABEL description="Unit Converter API - Builder Stage"

# Définir le répertoire de travail
WORKDIR /app

# Copier uniquement requirements.txt pour utiliser le cache Docker
COPY requirements.txt .

# Créer un environnement virtuel et installer les dépendances
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Image finale légère
# =============================================================================
FROM python:3.11-slim

# Métadonnées de l'image
LABEL maintainer="toumi.mahdi.cr7@gmail.com"
LABEL description="Unit Converter API - Production Image"
LABEL version="1.0.0"

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Définir le répertoire de travail
WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copier le code de l'application
COPY --chown=appuser:appuser app/ ./app/

# Passer à l'utilisateur non-root
USER appuser

# Configurer le PATH pour utiliser le venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Exposer le port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
