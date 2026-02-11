# Helios Server pt-BR (helios-server)
Este repositório é uma variação do **Helios Election System** com foco em **uso em português (pt-BR)** e com um fluxo moderno de execução via **Docker Compose**.


O Helios é um sistema de votação eletrônica com **verificabilidade ponta-a-ponta (E2E verifiable)**. Em termos práticos: ele permite conduzir eleições/plebiscitos/referendos onde o eleitor pode **verificar** que seu voto foi registrado corretamente e que a apuração foi feita de forma íntegra, sem que o sistema precise descriptografar votos individuais.

> Este projeto é voltado para uso institucional. Se você está avaliando adoção, leia com calma as seções de **Segurança**, **Operação** e **Configuração**.

---

## O que o Helios faz (visão geral)

### Para eleitores
- Votar em uma eleição/referendo via interface web.
- Receber um **rastreador do voto** (tracking number / hash) para verificação.
- Verificar (via booth/verifier) que o voto registrado corresponde ao que foi criptografado.

### Para administradores
- Criar eleições e configurar:
  - nome, descrição, datas (início/fim), privacidade
  - tipo de eleição e perguntas (ex.: aprovação, escolha única etc.)
  - elegibilidade e autenticação
- Importar lista de eleitores (quando aplicável).
- Gerenciar trustees (quando aplicável).
- Encerrar votação e iniciar apuração.
- Publicar resultados e enviar e-mails.

### O que acontece “por baixo do capô”
- Os votos são **criptografados no cliente** (no browser) com a chave pública da eleição.
- O servidor armazena votos criptografados e evidências necessárias para auditoria.
- A apuração combina votos criptografados e apenas o **resultado final** é descriptografado.
- Trustees podem participar do processo de descriptografia do resultado, conforme configuração.
- ** ALTAMENTE DESRECOMENDADO USAR TRUSTEES ** pois isso só adicionaria pontos de falha e problemas na interpretação em auditorias, por exemplo

---

## Casos de uso típicos
- Eleições internas (universidades, conselhos, comissões)
- Plebiscitos e consultas públicas com controle de elegibilidade
- Votações com exigência de auditoria e verificabilidade

---

## Componentes (alto nível)

- **Django/Helios (app)**: aplicação web principal
- **PostgreSQL (db)**: persistência
- **Celery + RabbitMQ (rabbitmq)**: processamento assíncrono (ex.: importação/validação de eleitores, envio de e-mails)
- **NGINX (nginx, opcional)**: reverse proxy e TLS

---

## Execução via Docker (recomendado)

### 1) Gere o `.env`
Use o gerador:
- `env-wizard.html` → abre no navegador → **Baixar .env** → salvar como `.env` na raiz do repo.

### 2) Suba os serviços

```bash
docker compose up -d --build
```

Acompanhe:

```bash
docker compose ps
docker compose logs -f --tail=200
```

### 3) Acesso
- Com NGINX: **https://localhost/** (porta 443) e redirect de http→https
- Sem NGINX: você pode expor a porta do Django (8000) no `docker-compose.yml` e acessar via **http://localhost:8000/**

### 4) Criar usuário admin (Django)

```bash
docker compose exec app uv run python manage.py createsuperuser
```

Mais detalhes no [`INSTALL.md`](INSTALL.md).

---

## NGINX é opcional

O container `nginx` é útil quando você quer:
- Terminação TLS (certificados)
- Um ponto único de entrada HTTP/HTTPS
- Configuração de cabeçalhos e proxy

Se você não usar NGINX, pode expor a porta do Django diretamente. Para ambientes produtivos, recomenda-se usar um proxy (NGINX/Traefik) e TLS.

---

## Sobre pt-BR / i18n

Esta variação está sendo conduzida com foco em **pt-BR**. Em alguns pontos, textos foram deixados **hardcoded** em português (ao invés de depender apenas de catálogos `gettext`).

Se você pretende suportar múltiplos idiomas, revise cuidadosamente o uso de `gettext` versus strings hardcoded.

---

## Como aplicar alterações no código

Por padrão, o `docker-compose.yml` **não usa bind-mount** do código para dentro do container `app`. Isso significa:

- alterou o código? → **rebuild**

```bash
docker compose build app
docker compose up -d app
```

Ou:

```bash
docker compose up -d --build
```

---

## Segurança e operação (notas rápidas)

- **Não commite** `.env` com segredos.
- Em produção, use:
  - segredos gerenciados (Vault/SSM/etc.)
  - TLS com certificados válidos
  - backups do PostgreSQL
  - logs e monitoramento
- Valide políticas institucionais e requisitos legais antes de operar eleições reais.

---

## Estrutura do repositório (pontos de interesse)

- `docker-compose.yml` — orquestração local/ambiente
- `Dockerfile` / `docker/entrypoint.sh` — build e boot da app
- `docker/nginx/default.conf` — proxy TLS (quando usar NGINX)
- `env-wizard.html` — gerador de `.env`
- `helios/` — app principal
- `helios_auth/` — autenticação/usuários
- `heliosbooth/` — UI de votação (cliente)
- `heliosverifier/` — verificador/auditoria

---

## Licença e upstream

O Helios é um projeto conhecido e amplamente referenciado na área de votação verificável. Esta árvore é derivada do upstream e adiciona customizações (Docker + pt-BR).

Consulte o repositório upstream para histórico, papers e documentação adicional.
