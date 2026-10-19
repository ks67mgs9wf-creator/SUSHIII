# Sushi Maré

Site de pedidos de sushi feito com Python (Flask), HTML e CSS. Os pedidos ficam salvos em banco de dados e o restaurante acompanha tudo em um painel com senha.

## Rodar no seu computador

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python gerar_imagens.py           # cria as ilustrações dos pratos em static/img/
export ADMIN_SENHA=escolha-uma-senha   # Windows (PowerShell): $env:ADMIN_SENHA="escolha-uma-senha"
python app.py
```

- Site: http://127.0.0.1:5000
- Painel do restaurante: http://127.0.0.1:5000/admin (precisa da `ADMIN_SENHA`)

Localmente os pedidos ficam no arquivo SQLite `instance/sushi.db`.

## Fotos dos pratos

Salve as fotos em `static/img/` com o número do prato (`1.jpg`, `2.png`, `3.webp`...). Os números estão em `app.py`. Fotos têm prioridade sobre as ilustrações; pratos sem imagem usam um emoji.

## Variáveis de ambiente

| Variável | Para que serve |
| --- | --- |
| `SECRET_KEY` | Chave longa e aleatória que protege as sessões |
| `ADMIN_SENHA` | Senha do painel `/admin` (sem ela o painel não abre) |
| `DATABASE_URL` | Endereço do PostgreSQL em produção (sem ela usa SQLite) |

## Publicar no Render

1. Crie um banco em **New + → PostgreSQL** e copie a *Internal Database URL*.
2. Crie um **Web Service** a partir deste repositório:
   - Build Command: `pip install -r requirements.txt && python gerar_imagens.py`
   - Start Command: `gunicorn app:app`
3. Em *Environment*, defina `SECRET_KEY`, `ADMIN_SENHA` e `DATABASE_URL`.
4. Se o build falhar ao instalar o `psycopg2-binary`, defina também `PYTHON_VERSION` = `3.12.7`.

## Estrutura

```
app.py               # rotas, banco de dados e painel
gerar_imagens.py     # gera as ilustrações dos pratos
requirements.txt
templates/           # index, confirmacao, admin, admin_login
static/style.css
static/img/          # imagens dos pratos
```
