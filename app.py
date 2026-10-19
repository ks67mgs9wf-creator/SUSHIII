import hmac
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from flask import Flask, abort, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Banco: SQLite local por padrão; em produção defina DATABASE_URL (PostgreSQL)
uri = os.environ.get("DATABASE_URL", "sqlite:///sushi.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = uri
db = SQLAlchemy(app)

PAGAMENTOS = ["Pix", "Cartão na entrega", "Dinheiro"]
STATUS = ["Novo", "Em preparo", "Saiu para entrega", "Entregue", "Cancelado"]


def agora_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(40), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    pagamento = db.Column(db.String(40), nullable=False)
    observacoes = db.Column(db.Text, default="")
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="Novo", nullable=False)
    criado_em = db.Column(db.DateTime, default=agora_utc, nullable=False)
    itens = db.relationship("ItemPedido", backref="pedido", cascade="all, delete-orphan")

    @property
    def numero(self):
        return self.id


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    qtd = db.Column(db.Integer, nullable=False)
    preco_unit = db.Column(db.Float, nullable=False)


with app.app_context():
    db.create_all()

CATEGORIAS = ["Niguiris", "Uramakis", "Hossomakis", "Temakis", "Combinados"]

MENU = [
    {"id": 1, "cat": "Niguiris", "nome": "Niguiri de salmão", "desc": "2 unidades, salmão fresco sobre arroz temperado.", "preco": 14.90, "emoji": "🍣"},
    {"id": 2, "cat": "Niguiris", "nome": "Niguiri de atum", "desc": "2 unidades, atum selecionado e wasabi.", "preco": 16.90, "emoji": "🍣"},
    {"id": 3, "cat": "Niguiris", "nome": "Niguiri de camarão", "desc": "2 unidades, camarão cozido no ponto.", "preco": 15.90, "emoji": "🍤"},
    {"id": 4, "cat": "Uramakis", "nome": "Philadelphia", "desc": "8 unidades, salmão, cream cheese e cebolinha.", "preco": 27.90, "emoji": "🍙"},
    {"id": 5, "cat": "Uramakis", "nome": "Skin crocante", "desc": "8 unidades, pele de salmão crocante e cebolinha.", "preco": 24.90, "emoji": "🍙"},
    {"id": 6, "cat": "Uramakis", "nome": "Hot roll", "desc": "8 unidades, empanado e frito, com molho tarê.", "preco": 29.90, "emoji": "🔥"},
    {"id": 7, "cat": "Hossomakis", "nome": "Hossomaki de pepino", "desc": "8 unidades, leve e refrescante.", "preco": 18.90, "emoji": "🥒"},
    {"id": 8, "cat": "Hossomakis", "nome": "Hossomaki de salmão", "desc": "8 unidades, salmão envolto em nori.", "preco": 22.90, "emoji": "🍙"},
    {"id": 9, "cat": "Temakis", "nome": "Temaki de salmão", "desc": "Cone de nori com salmão, arroz e cream cheese.", "preco": 26.90, "emoji": "🌯"},
    {"id": 10, "cat": "Temakis", "nome": "Temaki de kani", "desc": "Cone de nori com kani, manga e maionese.", "preco": 21.90, "emoji": "🌯"},
    {"id": 11, "cat": "Combinados", "nome": "Combo Maré (20 peças)", "desc": "Niguiris, uramakis e hossomakis variados.", "preco": 69.90, "emoji": "🌊"},
    {"id": 12, "cat": "Combinados", "nome": "Combo Família (40 peças)", "desc": "Seleção do chef para 3 ou 4 pessoas.", "preco": 129.90, "emoji": "🍱"},
]
PASTA_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img")
for _item in MENU:
    # Se existir static/img/<id>.jpg (ou .png/.webp), a foto aparece no lugar do emoji
    _item["foto"] = None
    for _ext in ("jpg", "jpeg", "png", "webp", "svg"):
        if os.path.exists(os.path.join(PASTA_IMG, f"{_item['id']}.{_ext}")):
            _item["foto"] = f"img/{_item['id']}.{_ext}"
            break
MENU_POR_ID = {item["id"]: item for item in MENU}


@app.template_filter("brl")
def brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("hora")
def hora(dt):
    return dt.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/Sao_Paulo")).strftime("%d/%m %H:%M")


def carrinho_detalhado():
    itens, total = [], 0.0
    for item_id, qtd in session.get("carrinho", {}).items():
        item = MENU_POR_ID.get(int(item_id))
        if item:
            subtotal = item["preco"] * qtd
            itens.append({**item, "qtd": qtd, "subtotal": subtotal})
            total += subtotal
    return itens, total


@app.route("/")
def index():
    itens, total = carrinho_detalhado()
    secoes = [(c, [i for i in MENU if i["cat"] == c]) for c in CATEGORIAS]
    qtd_total = sum(i["qtd"] for i in itens)
    return render_template("index.html", secoes=secoes, itens=itens, total=total,
                           qtd_total=qtd_total, erro=session.pop("erro", None))


@app.post("/adicionar/<int:item_id>")
def adicionar(item_id):
    if item_id in MENU_POR_ID:
        carrinho = session.get("carrinho", {})
        carrinho[str(item_id)] = carrinho.get(str(item_id), 0) + 1
        session["carrinho"] = carrinho
    return redirect(url_for("index") + "#carrinho")


@app.post("/diminuir/<int:item_id>")
def diminuir(item_id):
    carrinho = session.get("carrinho", {})
    chave = str(item_id)
    if chave in carrinho:
        carrinho[chave] -= 1
        if carrinho[chave] <= 0:
            del carrinho[chave]
    session["carrinho"] = carrinho
    return redirect(url_for("index") + "#carrinho")


@app.post("/pedido")
def pedido():
    itens, total = carrinho_detalhado()
    nome = request.form.get("nome", "").strip()
    telefone = request.form.get("telefone", "").strip()
    endereco = request.form.get("endereco", "").strip()
    if not itens:
        session["erro"] = "Adicione pelo menos um item ao pedido."
        return redirect(url_for("index") + "#carrinho")
    if not (nome and telefone and endereco):
        session["erro"] = "Preencha nome, telefone e endereço."
        return redirect(url_for("index") + "#carrinho")
    pagamento = request.form.get("pagamento", "Pix")
    if pagamento not in PAGAMENTOS:
        pagamento = "Pix"

    novo = Pedido(
        nome=nome[:120], telefone=telefone[:40], endereco=endereco[:255],
        pagamento=pagamento,
        observacoes=request.form.get("observacoes", "").strip()[:500],
        total=round(total, 2),
        itens=[ItemPedido(nome=i["nome"], qtd=i["qtd"], preco_unit=i["preco"]) for i in itens],
    )
    db.session.add(novo)
    db.session.commit()

    session["carrinho"] = {}
    return render_template("confirmacao.html", pedido=novo, itens=itens)


def admin_ok():
    return session.get("admin") is True


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    senha_correta = os.environ.get("ADMIN_SENHA")
    erro = None
    if request.method == "POST":
        digitada = request.form.get("senha", "")
        if senha_correta and hmac.compare_digest(digitada.encode(), senha_correta.encode()):
            session["admin"] = True
            return redirect(url_for("admin"))
        erro = "Senha incorreta." if senha_correta else "Defina a variável de ambiente ADMIN_SENHA no servidor."
    return render_template("admin_login.html", erro=erro)


@app.route("/admin")
def admin():
    if not admin_ok():
        return redirect(url_for("admin_login"))
    filtro = request.args.get("status")
    consulta = Pedido.query.order_by(Pedido.id.desc())
    if filtro in STATUS:
        consulta = consulta.filter_by(status=filtro)
    return render_template("admin.html", pedidos=consulta.limit(200).all(),
                           status_lista=STATUS, filtro=filtro)


@app.post("/admin/pedido/<int:pedido_id>/status")
def admin_status(pedido_id):
    if not admin_ok():
        abort(403)
    pedido_obj = db.get_or_404(Pedido, pedido_id)
    novo = request.form.get("status")
    if novo in STATUS:
        pedido_obj.status = novo
        db.session.commit()
    return redirect(url_for("admin"))


@app.post("/admin/sair")
def admin_sair():
    session.pop("admin", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
