FROM python:3.13-slim

# System deps (postgres + python-ldap build deps) + gettext for i18n
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gettext \
    libpq-dev \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Leverage Docker layer cache
COPY pyproject.toml uv.lock ./
# NOTE: use non-frozen sync so dependency changes in pyproject.toml are installed
# even if uv.lock hasn't been updated yet.
RUN uv sync

COPY . .

ENV DJANGO_SETTINGS_MODULE=settings \
    PYTHONUNBUFFERED=1

EXPOSE 8000

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
