# Helios Server (pt-BR) — Instalação e Execução

Este repositório contém uma versão do **Helios Server** adaptada para **pt-BR** e com um setup de desenvolvimento via **Docker Compose**.

> TL;DR:
> 1) gere `.env` com `env-wizard.html` (ou crie manualmente)
> 2) `docker compose up -d --build`
> 3) acesse via **NGINX** (porta 80/443) ou exponha o **Django** diretamente (porta 8000)

** Importante: ** Lembre-se de alterar docker/nginx/default.conf para o domínio correto.

---

## Pré‑requisitos

- **Docker** e **Docker Compose** (plugin `docker compose`) - https://docs.docker.com/compose/install/linux/
- (Opcional) `curl` para testes locais


---

## 1) Configuração do `.env` (obrigatório)

O serviço `app` (Django/Helios) carrega variáveis via arquivo `.env`.

### Opção A — `env-wizard.html` (recomendado)

1. Abra o arquivo `env-wizard.html` no navegador (arquivo local mesmo).
2. Preencha os campos.
3. Clique em **Baixar .env**.
4. Salve o arquivo baixado como `.env` na raiz do repositório (mesma pasta do `docker-compose.yml`).

### Opção B — criar manualmente

Crie um arquivo `.env` na raiz do repo. Ele deve conter, no mínimo:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `CELERY_BROKER_URL`

O wizard já monta `DATABASE_URL` e `CELERY_BROKER_URL` no formato esperado.

> Importante: **não commite** `.env` com credenciais reais.

---

## 2) Subir com Docker (padrão)

Na raiz do projeto:

```bash
docker compose up -d --build
```

Verifique status e logs:

```bash
docker compose ps
docker compose logs -f --tail=200
```

### O que o Compose sobe

- `db` → PostgreSQL
- `rabbitmq` → RabbitMQ (com UI de management)
- `app` → Django/Helios (+ migrations no entrypoint)
- `nginx` → reverse proxy TLS (opcional)

---

## 3) NGINX (opcional)

Por padrão, o `docker-compose.yml` expõe **80/443** no host via container `nginx`.
Na pasta há dois arquivos, você pode renomear, copiar, editar, etc.
 - `docker-compose-nginx.yml` com ** nginx **
 - `docker-compose-no_nginx.yml` sem ** nginx **

### Quando usar

- Quando você quer um ponto único de entrada (HTTP/HTTPS)
- Quando precisa terminar TLS (certificados) no proxy
- Quando vai rodar com domínio (ex.: `e-democracia.ufsc.br`)

### Como funciona

O NGINX está configurado em:

- `docker/nginx/default.conf`

Ele faz:

- redirect **HTTP → HTTPS**
- proxy para `app:8000`

### Certificados

O compose monta `./certs` em `/etc/nginx/certs` (read-only).
Você precisa fornecer:

- `certs/fullchain.pem`
- `certs/privkey.pem`

> Dica: se estiver em dev local e não quiser lidar com TLS, você pode **não usar o NGINX** e expor a porta do Django (abaixo).

---

## 4) Rodar SEM NGINX (expondo Django diretamente)

Se você não quiser usar o container `nginx`, existem duas opções.

### Opção A — subir apenas os serviços necessários

```bash
docker compose up -d --build db rabbitmq app
```

Depois, exponha a porta 8000 do Django alterando o `docker-compose.yml` (serviço `app`):

```yaml
  app:
    # ...
    ports:
      - "8000:8000"
```

E suba novamente:

```bash
docker compose up -d --build app
```

Acesse:

- http://localhost:8000/

### Opção B — manter o compose intacto e apenas não iniciar o NGINX

Você pode simplesmente não iniciar o serviço `nginx`:

```bash
docker compose up -d --build db rabbitmq app
```

(Para acesso, ainda será necessário expor a porta 8000 conforme a Opção A.)

---

## 5) Alterações no código: como funcionam

### Importante: sem bind-mount por padrão

O `docker-compose.yml` **não** usa bind-mount do código para dentro do container.
Isso significa:

- o container usa o código **copiado na imagem** durante o `docker build`
- ao alterar arquivos no repo, você precisa **rebuildar a imagem**

### Fluxo típico após mudanças no código

```bash
docker compose build app
docker compose up -d app
```

Ou de forma direta:

```bash
docker compose up -d --build
```

### Quando mudar dependências (pyproject/uv.lock)

Se você alterar dependências, rode:

```bash
docker compose build --no-cache app
```

---

## 6) Reset “do zero” (somente deste projeto)

Para remover containers, rede, **volumes do projeto** e imagens locais do compose:

```bash
docker compose down --volumes --remove-orphans --rmi local
```

Depois, subir novamente:

```bash
docker compose up -d --build
```

---

## 7) Criar usuário administrador (Django)

Após subir os containers, você pode criar um superusuário do Django (admin):

```bash
docker compose exec app uv run python manage.py createsuperuser
```

Isso cria um usuário com acesso ao Django admin.

### Tornar um usuário do CAS “admin” para criar eleições (HELIOS_ADMIN_ONLY=1)

Quando `HELIOS_ADMIN_ONLY=1`, apenas usuários marcados como administradores no Helios conseguem **criar eleições**.

Passo a passo (via interface):

1. Faça login via CAS normalmente (isso garante que o usuário seja criado/atualizado no banco do Helios).
2. Acesse o Django Admin em:
   - `/admin`
3. No Admin, vá em:
   - **Helios Authentication** → **Users**
4. Selecione o usuário em questão.
5. Marque o campo **admin_p** e salve.
6. Faça logout/login novamente e tente criar uma eleição.

## 8) Troubleshooting rápido

### Ver logs de um serviço

```bash
docker compose logs -f --tail=200 app
```

### Verificar resposta do NGINX

```bash
curl -I http://localhost/
curl -k -I https://localhost/
```

### RabbitMQ Management

A imagem `rabbitmq:3-management` expõe a UI internamente (porta 15672 no container).
Se você quiser acessar pelo host, adicione `ports:` no serviço `rabbitmq`.

---

## Instalação sem Docker (legado)

O passo a passo original (uv + Postgres local + RabbitMQ local) ainda é possível, mas este repo está sendo mantido com foco em **Docker Compose**.

Se você quiser rodar sem Docker:

1. Instale Python 3.13 + `uv`
2. Instale PostgreSQL e RabbitMQ
3. Rode `uv sync`
4. Rode `./reset.sh`
5. Rode `uv run python manage.py runserver`
