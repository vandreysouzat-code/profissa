
import os
import sqlite3
from pathlib import Path
from functools import wraps
from datetime import datetime
from flask import (
    Flask, request, redirect, url_for, session,
    flash, render_template_string
)
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "instance" / "profissa.db"

PROFESSIONS = {
    "Prestador de serviÃ§os": ["Clientes", "ServiÃ§os", "OrÃ§amentos", "Tarefas"],
    "PsicÃ³logo": ["Clientes", "Agenda", "Tarefas"],
    "Fisioterapeuta": ["Clientes", "Agenda", "Tarefas"],
    "Advogado": ["Clientes", "Processos", "Tarefas", "Documentos"],
    "Contador": ["Clientes", "Documentos", "Tarefas", "RelatÃ³rios"],
    "Profissional de beleza": ["Clientes", "Agenda", "ServiÃ§os"],
    "Professor ou consultor": ["Clientes", "Agenda", "Tarefas"],
    "Outra profissÃ£o": ["Clientes", "Agenda", "ServiÃ§os", "Tarefas"]
}

FIELDS = {
    "Clientes": ("Nome do cliente", "Contato", "ObservaÃ§Ãµes"),
    "Agenda": ("Compromisso", "Data e horÃ¡rio", "ObservaÃ§Ãµes"),
    "ServiÃ§os": ("Nome do serviÃ§o", "PreÃ§o (R$)", "DescriÃ§Ã£o"),
    "OrÃ§amentos": ("Nome do orÃ§amento", "Valor (R$)", "Detalhes"),
    "Tarefas": ("Nome da tarefa", "Prazo", "Detalhes"),
    "Processos": ("Processo", "Prazo ou status", "ObservaÃ§Ãµes"),
    "Documentos": ("Nome do documento", "Tipo ou prazo", "ObservaÃ§Ãµes"),
    "RelatÃ³rios": ("Nome do relatÃ³rio", "PerÃ­odo", "ObservaÃ§Ãµes")
}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "PROFISSA_SECRET_KEY",
    "chave-local-desenvolvimento-nao-publicar"
)


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            profession TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module TEXT NOT NULL,
            title TEXT NOT NULL,
            detail TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)


def get_user():
    uid = session.get("user_id")
    if not uid:
        return None

    with connect() as db:
        return db.execute(
            "SELECT id,name,email,profession FROM users WHERE id=?",
            (uid,)
        ).fetchone()


def protected(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_user()
        if not user:
            session.clear()
            flash("Sua sessão expirou. Entre na sua conta novamente.", "info")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

PAGE = """
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | Profissa</title>
<style>
:root{font-family:Arial,Helvetica,sans-serif;color:#18251f;background:#f7f9f7}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:flex;flex-direction:column}
header{min-height:74px;padding:12px max(22px,calc((100% - 1100px)/2));display:flex;align-items:center;justify-content:space-between;gap:15px;background:white;border-bottom:1px solid #e3eae4}
.brand{font-size:26px;font-weight:800;text-decoration:none;color:#18251f}
.brand span{color:#168452}
nav{display:flex;gap:20px;align-items:center}
a{color:#168452;text-decoration:none;font-weight:650}
main{flex:1;width:min(1100px,calc(100% - 36px));margin:0 auto;padding:45px 0 70px}
.hero{text-align:center;padding:30px 0 65px}
.eyebrow{color:#168452;font-size:12px;font-weight:bold;letter-spacing:2px}
h1{font-size:clamp(36px,6vw,62px);letter-spacing:-2px;line-height:1.1;margin:20px 0}
.hero p{max-width:620px;margin:0 auto 28px;color:#68756d;font-size:18px;line-height:1.8}
.btn{display:inline-block;background:#168452;color:white;border:0;border-radius:8px;padding:13px 20px;font-weight:bold;cursor:pointer;font-size:14px}
.features,.grid,.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.card,.panel,.stat,.feature{background:white;border:1px solid #e3eae4;border-radius:12px;padding:23px}
.feature p,.muted{color:#68756d;line-height:1.7}
.formbox{max-width:470px;margin:0 auto;background:white;border:1px solid #e3eae4;border-radius:14px;padding:30px}
.formbox h1{font-size:34px;letter-spacing:-1px}
form.stack{display:flex;flex-direction:column;gap:16px}
label{display:flex;flex-direction:column;gap:7px;font-size:14px;font-weight:bold}
input,select,textarea{width:100%;padding:12px;border:1px solid #d9e2db;border-radius:8px;font:inherit;background:white}
input:focus,select:focus,textarea:focus{outline:2px solid #a7d8ba;border-color:#168452}
.full{width:100%}
.bottom{text-align:center;font-size:14px;color:#68756d;margin-top:22px}
.flash{padding:12px 15px;background:#e8f7ee;border-radius:8px;margin-bottom:12px;color:#17683f}
.flash.error{background:#fff0ee;color:#a52d20}
.welcome{display:flex;justify-content:space-between;align-items:center;gap:18px;margin-bottom:28px}
.welcome h1{font-size:40px;letter-spacing:-1px;margin:12px 0}
.pill{background:#e8f5ed;color:#17683f;border-radius:20px;padding:9px 13px;font-size:13px;font-weight:bold}
.stats{margin-bottom:35px}
.stat span{display:block;color:#68756d;font-size:13px}
.stat strong{display:block;font-size:29px;margin-top:10px}
.grid{grid-template-columns:repeat(4,minmax(0,1fr))}
.module{display:block;color:#18251f;min-height:145px}
.module strong{display:block;font-size:18px;margin:13px 0}
.module small{color:#68756d}
.module .symbol{display:grid;place-items:center;width:36px;height:36px;border-radius:9px;background:#e8f5ed;color:#168452}
.layout{display:grid;grid-template-columns:minmax(250px,.8fr) minmax(0,1.2fr);gap:18px;align-items:start}
.panel h2{margin-top:0}
.record{padding:16px 0;border-bottom:1px solid #edf1ed;overflow-wrap:anywhere}
.record:last-child{border:0}
.record-head{display:flex;justify-content:space-between;gap:10px;align-items:center}
.record p{color:#68756d;white-space:pre-wrap;overflow-wrap:anywhere}
.delete{background:#fff0ee;color:#a52d20;border:0;padding:8px;border-radius:6px;cursor:pointer}
footer{text-align:center;padding:23px;background:white;border-top:1px solid #e3eae4;color:#68756d;font-size:13px}
@media(max-width:750px){
.grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.layout{grid-template-columns:1fr}
.features,.stats{grid-template-columns:1fr}
.welcome{align-items:flex-start;flex-direction:column}
}
@media(max-width:450px){
header{padding:12px 15px}
nav{gap:12px}
main{width:calc(100% - 28px);padding-top:28px}
.formbox{padding:22px}
.grid{gap:10px}
.card,.panel,.stat,.feature{padding:17px}
}
</style>
</head>
<body>
<header>
<a class="brand" href="{{ url_for('home') }}">Profissa<span>.</span></a>
<nav>
{% if user %}
<a href="{{ url_for('dashboard') }}">Meu painel</a>
<form method="post" action="{{ url_for('logout') }}">
<button class="btn">Sair</button>
</form>
{% else %}
<a href="{{ url_for('login') }}">Entrar</a>
<a class="btn" href="{{ url_for('register') }}">Criar conta</a>
{% endif %}
</nav>
</header>
<main>
{% for category,message in get_flashed_messages(with_categories=true) %}
<div class="flash {{ category }}">{{ message }}</div>
{% endfor %}
{{ body|safe }}
</main>
<footer>Profissa Â· Seu trabalho, mais organizado.</footer>
</body>
</html>
"""


def page(title, body, **context):
    return render_template_string(
        PAGE,
        title=title,
        body=render_template_string(body, **context),
        user=get_user()
    )


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return page("Seu espaÃ§o profissional", """
    <section class="hero">
      <span class="eyebrow">UM NOVO JEITO DE TRABALHAR</span>
      <h1>Seu trabalho merece<br>um lugar melhor.</h1>
      <p>Organize clientes, compromissos e tarefas em uma plataforma
      pensada para acompanhar a sua profissÃ£o.</p>
      <a class="btn" href="{{ url_for('register') }}">Criar meu espaÃ§o</a>
      <p><a href="{{ url_for('login') }}">JÃ¡ tenho uma conta</a></p>
    </section>
    <section class="features">
      <article class="feature"><span class="eyebrow">01</span>
      <h2>Feito para vocÃª</h2><p>Uma experiÃªncia adaptada Ã  sua Ã¡rea.</p></article>
      <article class="feature"><span class="eyebrow">02</span>
      <h2>Tudo organizado</h2><p>InformaÃ§Ãµes reunidas em um sÃ³ lugar.</p></article>
      <article class="feature"><span class="eyebrow">03</span>
      <h2>Simples de usar</h2><p>Uma interface clara e prÃ¡tica.</p></article>
    </section>
    """)


@app.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        profession = request.form.get("profession", "")

        if len(name) < 2:
            flash("Informe seu nome.", "error")
        elif "@" not in email or "." not in email.split("@")[-1]:
            flash("Informe um e-mail vÃ¡lido.", "error")
        elif len(password) < 8:
            flash("A senha precisa ter pelo menos 8 caracteres.", "error")
        elif profession not in PROFESSIONS:
            flash("Selecione uma profissÃ£o vÃ¡lida.", "error")
        else:
            try:
                with connect() as db:
                    cur = db.execute(
                        "INSERT INTO users(name,email,password_hash,profession) "
                        "VALUES(?,?,?,?)",
                        (name, email, generate_password_hash(password), profession)
                    )
                    uid = cur.lastrowid

                session.clear()
                session["user_id"] = uid
                flash("Conta criada! Seu espaÃ§o profissional estÃ¡ pronto.", "success")
                return redirect(url_for("dashboard"))

            except sqlite3.IntegrityError:
                flash("Este e-mail jÃ¡ estÃ¡ cadastrado.", "error")

    return page("Criar conta", """
    <section class="formbox">
      <span class="eyebrow">COMECE POR AQUI</span>
      <h1>Crie seu espaÃ§o</h1>
      <p class="muted">Vamos adaptar o Profissa Ã  sua rotina.</p>
      <form method="post" class="stack">
        <label>Seu nome
          <input name="name" required minlength="2" maxlength="100" autocomplete="name">
        </label>
        <label>E-mail
          <input name="email" type="email" required autocomplete="email">
        </label>
        <label>Senha
          <input name="password" type="password" required minlength="8" autocomplete="new-password">
          <small>Use pelo menos 8 caracteres.</small>
        </label>
        <label>Sua profissÃ£o
          <select name="profession" required>
            <option value="">Selecione</option>
            {% for p in professions %}<option>{{ p }}</option>{% endfor %}
          </select>
        </label>
        <button class="btn full">Criar conta</button>
      </form>
      <p class="bottom">JÃ¡ tem uma conta? <a href="{{ url_for('login') }}">Entrar</a></p>
    </section>
    """, professions=list(PROFESSIONS))


@app.route("/entrar", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with connect() as db:
            user = db.execute(
                "SELECT id,password_hash FROM users WHERE email=?",
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

        flash("E-mail ou senha incorretos.", "error")

    return page("Entrar", """
    <section class="formbox">
      <span class="eyebrow">BEM-VINDO DE VOLTA</span>
      <h1>Entrar na conta</h1>
      <form method="post" class="stack">
        <label>E-mail
          <input type="email" name="email" required autocomplete="email">
        </label>
        <label>Senha
          <input type="password" name="password" required autocomplete="current-password">
        </label>
        <button class="btn full">Entrar</button>
      </form>
      <p class="bottom">NÃ£o tem conta? <a href="{{ url_for('register') }}">Criar conta</a></p>
    </section>
    """)


@app.route("/sair", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/painel")
@protected
def dashboard():
    user = get_user()
    if not user:
        session.clear()
        flash("Entre na sua conta para continuar.", "info")
        return redirect(url_for("login"))
    modules = PROFESSIONS[user["profession"]]

    with connect() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM records WHERE user_id=?",
            (user["id"],)
        ).fetchone()[0]

        recent = db.execute(
            "SELECT * FROM records WHERE user_id=? ORDER BY id DESC LIMIT 5",
            (user["id"],)
        ).fetchall()

        counts = {
            module: db.execute(
                "SELECT COUNT(*) FROM records WHERE user_id=? AND module=?",
                (user["id"], module)
            ).fetchone()[0]
            for module in modules
        }

    return page("Meu painel", """
    <div class="welcome">
      <div>
        <span class="eyebrow">SEU ESPAÃ‡O PROFISSIONAL</span>
        <h1>OlÃ¡, {{ name }}.</h1>
        <p class="muted">Organize sua rotina em um sÃ³ lugar.</p>
      </div>
      <span class="pill">{{ profession }}</span>
    </div>

    <div class="stats">
      <article class="stat"><span>Registros totais</span><strong>{{ total }}</strong></article>
      <article class="stat"><span>MÃ³dulos disponÃ­veis</span><strong>{{ modules|length }}</strong></article>
      <article class="stat"><span>Seu espaÃ§o</span><strong>Ativo</strong></article>
    </div>

    <h2>Suas ferramentas</h2>
    <p class="muted">Escolha um mÃ³dulo para comeÃ§ar.</p>
    <div class="grid">
      {% for m in modules %}
      <a class="card module" href="{{ url_for('module_page', module=m) }}">
        <span class="symbol" aria-hidden="true">âœ¦</span>
        <strong>{{ m }}</strong>
        <small>{{ counts[m] }} registro(s) Â· Abrir â†’</small>
      </a>
      {% endfor %}
    </div>

    <h2 style="margin-top:38px">Atividade recente</h2>
    {% if recent %}
      {% for r in recent %}
      <article class="card" style="margin:10px 0">
        <strong>{{ r["title"] }}</strong>
        <p class="muted">{{ r["module"] }} Â· {{ r["detail"] }}</p>
      </article>
      {% endfor %}
    {% else %}
      <div class="card">
        <strong>Sua organizaÃ§Ã£o comeÃ§a aqui.</strong>
        <p class="muted">Abra um mÃ³dulo e adicione seu primeiro registro.</p>
      </div>
    {% endif %}
    """, name=user["name"].split()[0], profession=user["profession"],
       modules=modules, total=total, counts=counts, recent=recent)


def format_brl(value):
    """Formata nÃºmeros como moeda brasileira sem depender da configuraÃ§Ã£o regional."""
    try:
        number = float(str(value).strip().replace(",", "."))
        formatted = f"{number:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except (ValueError, TypeError):
        return str(value)



def parse_brl(value):
    """Converte valores monet?rios sem remover indevidamente os centavos."""
    from decimal import Decimal, InvalidOperation

    text = str(value or "").strip().replace("R$", "").replace(" ", "")
    if not text:
        return None

    # Com v?rgula: formato brasileiro, por exemplo 1.234,56.
    if "," in text:
        text = text.replace(".", "").replace(",", ".")
    # Sem v?rgula: aceita o ponto como separador decimal, por exemplo 25.00.

    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise ValueError("Valor inv?lido.")

    if not amount.is_finite() or amount < 0:
        raise ValueError("O valor deve ser um n?mero nÃ£o negativo.")

    return amount.quantize(Decimal("0.01"))


@app.route("/modulo/<module>", methods=["GET", "POST"])
@protected
def module_page(module):
    user = get_user()

    if module not in PROFESSIONS[user["profession"]] or module not in FIELDS:
        flash("MÃ³dulo nÃ£o disponÃ­vel para sua profissÃ£o.", "error")
        return redirect(url_for("dashboard"))

    labels = FIELDS[module]
    editing_record = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        detail = request.form.get("detail", "").strip()
        notes = request.form.get("notes", "").strip()
        record_id_text = request.form.get("record_id", "").strip()

        if not title:
            flash("O nome do registro ? obrigat?rio.", "error")
        elif len(title) > 150 or len(detail) > 200 or len(notes) > 2000:
            flash("Um campo ultrapassou o tamanho permitido.", "error")
        else:
            valid = True

            if module in ("ServiÃ§os", "OrÃ§amentos") and detail:
                try:
                    detail = str(parse_brl(detail))
                except ValueError:
                    flash("Informe um valor v?lido, por exemplo: 25,00.", "error")
                    valid = False

            if module == "Agenda" and detail:
                try:
                    datetime.fromisoformat(detail)
                except ValueError:
                    flash("Confira a data e o hor?rio informados.", "error")
                    valid = False

            if valid:
                with connect() as db:
                    if record_id_text:
                        try:
                            record_id = int(record_id_text)
                        except ValueError:
                            flash("Registro inv?lido.", "error")
                            record_id = None

                        record = None
                        if record_id is not None:
                            record = db.execute(
                                "SELECT id FROM records "
                                "WHERE id=? AND user_id=? AND module=?",
                                (record_id, user["id"], module)
                            ).fetchone()

                        if not record:
                            flash("Registro nÃ£o encontrado ou sem permiss?o.", "error")
                        else:
                            db.execute(
                                "UPDATE records SET title=?, detail=?, notes=? "
                                "WHERE id=? AND user_id=? AND module=?",
                                (title, detail, notes, record_id, user["id"], module)
                            )
                            flash("Registro atualizado com sucesso.", "success")
                            return redirect(url_for("module_page", module=module))
                    else:
                        db.execute(
                            "INSERT INTO records(user_id,module,title,detail,notes) "
                            "VALUES(?,?,?,?,?)",
                            (user["id"], module, title, detail, notes)
                        )
                        flash("Registro salvo com sucesso.", "success")
                        return redirect(url_for("module_page", module=module))

    edit_id = request.args.get("edit_id", "").strip()
    if edit_id:
        try:
            edit_id = int(edit_id)
        except ValueError:
            edit_id = None

        if edit_id is not None:
            with connect() as db:
                editing_record = db.execute(
                    "SELECT * FROM records WHERE id=? AND user_id=? AND module=?",
                    (edit_id, user["id"], module)
                ).fetchone()

            if not editing_record:
                flash("Registro nÃ£o encontrado ou sem permiss?o.", "error")

    with connect() as db:
        if module == "Agenda":
            records = db.execute(
                "SELECT * FROM records WHERE user_id=? AND module=? "
                "ORDER BY CASE WHEN detail IS NULL OR detail='' THEN 1 ELSE 0 END, "
                "detail ASC, id DESC",
                (user["id"], module)
            ).fetchall()
        else:
            records = db.execute(
                "SELECT * FROM records WHERE user_id=? AND module=? ORDER BY id DESC",
                (user["id"], module)
            ).fetchall()

    return page(module, """
    <p><a href="{{ url_for('dashboard') }}">? Voltar ao painel</a></p>

    <div class="welcome">
      <div>
        <span class="eyebrow">SEU ESPAÃ‡O PROFISSIONAL</span>
        <h1>{{ module }}</h1>
        <p class="muted">Cadastre e organize seus registros.</p>
      </div>
    </div>

    <div class="layout">
      <section class="panel">
        <h2>{% if editing_record %}Editar registro{% else %}Novo registro{% endif %}</h2>

        <form method="post" class="stack">
          {% if editing_record %}
            <input type="hidden" name="record_id" value="{{ editing_record['id'] }}">
          {% endif %}

          <label>{{ labels[0] }}
            <input name="title" required maxlength="150"
                   value="{{ editing_record['title'] if editing_record else '' }}">
          </label>

          <label>{{ labels[1] }}
            {% if module == "Agenda" %}
              <input name="detail" type="datetime-local"
                     value="{{ editing_record['detail'] if editing_record else '' }}">
            {% elif module in ("ServiÃ§os", "OrÃ§amentos") %}
              <input name="detail" type="number" min="0" step="0.01"
                     placeholder="0,00"
                     value="{{ editing_record['detail'] if editing_record else '' }}">
            {% else %}
              <input name="detail" maxlength="200"
                     value="{{ editing_record['detail'] if editing_record else '' }}">
            {% endif %}
          </label>

          <label>{{ labels[2] }}
            <textarea name="notes" rows="4" maxlength="2000">{{ editing_record['notes'] if editing_record else '' }}</textarea>
          </label>

          <button class="btn full">
            {% if editing_record %}Salvar alteraÃ§Ãµes{% else %}Salvar registro{% endif %}
          </button>

          {% if editing_record %}
            <a href="{{ url_for('module_page', module=module) }}">Cancelar ediÃ§Ã£o</a>
          {% endif %}
        </form>
      </section>

      <section class="panel">
        <h2>Registros salvos ({{ records|length }})</h2>
        {% if records %}
          {% for r in records %}
          <article class="record">
            <div class="record-head">
              <strong>{{ r["title"] }}</strong>
              <div style="display:flex;gap:8px;flex-wrap:wrap">
                <a class="btn" style="padding:8px"
                   href="{{ url_for('module_page', module=module, edit_id=r['id']) }}">Editar</a>
                <form method="post"
                      action="{{ url_for('delete_record', record_id=r['id']) }}"
                      class="delete-form">
                  <button type="button" class="delete">Excluir</button>
                </form>
              </div>
            </div>

            {% if r["detail"] %}
              {% if module == "ServiÃ§os" or module == "OrÃ§amentos" %}
                <p><strong>{{ format_brl(r["detail"]) }}</strong></p>
              {% elif module == "Agenda" %}
                <p>{{ r["detail"].replace("T", " ?s ") }}</p>
              {% else %}
                <p>{{ r["detail"] }}</p>
              {% endif %}
            {% endif %}

            {% if r["notes"] %}
              <p>{{ r["notes"] }}</p>
            {% endif %}
            <small>{{ r["created_at"] }}</small>
          </article>
          {% endfor %}
        {% else %}
          <p class="muted">Nenhum registro ainda. Adicione o primeiro pelo formulÃ¡rio.</p>
        {% endif %}
      </section>
    </div>

    <div id="profissa-delete-modal" class="profissa-modal" hidden>
      <div class="profissa-modal-card" role="dialog" aria-modal="true"
           aria-labelledby="profissa-delete-title">
        <h2 id="profissa-delete-title">Excluir registro</h2>
        <p id="profissa-delete-message">Deseja excluir este registro?</p>
        <div class="profissa-modal-actions">
          <button type="button" class="btn"
                  onclick="fecharModalProfissa()">Cancelar</button>
          <button type="button" class="delete"
                  onclick="confirmarExclusaoProfissa()">Excluir</button>
        </div>
      </div>
    </div>

    <style>
      .profissa-modal[hidden] { display: none !important; }
      .profissa-modal {
        position: fixed; inset: 0; z-index: 10000;
        display: flex; align-items: center; justify-content: center;
        padding: 20px; background: rgba(10, 20, 15, .65);
      }
      .profissa-modal-card {
        width: min(100%, 420px); padding: 24px;
        border-radius: 16px; background: #fff; color: #18251f;
        box-shadow: 0 20px 60px rgba(0, 0, 0, .25);
      }
      .profissa-modal-actions {
        display: flex; justify-content: flex-end;
        flex-wrap: wrap; gap: 10px; margin-top: 24px;
      }
    </style>

    <script>
      let formularioExclusaoProfissa = null;

      document.querySelectorAll(".delete-form").forEach(function(form) {
        const button = form.querySelector("button.delete");
        if (button) {
          button.addEventListener("click", function() {
            formularioExclusaoProfissa = form;
            const title = form.closest(".record")
              ?.querySelector("strong")?.textContent || "este registro";
            document.getElementById("profissa-delete-message").textContent =
              'Tem certeza de que deseja excluir "' + title + '"?';
            document.getElementById("profissa-delete-modal").hidden = false;
          });
        }
      });

      function fecharModalProfissa() {
        document.getElementById("profissa-delete-modal").hidden = true;
        formularioExclusaoProfissa = null;
      }

      function confirmarExclusaoProfissa() {
        if (formularioExclusaoProfissa) formularioExclusaoProfissa.submit();
      }

      document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") fecharModalProfissa();
      });
    </script>
    """, module=module, labels=labels, records=records,
       editing_record=editing_record, format_brl=format_brl)


def format_brl(value):
    """Formata um valor num?rico como moeda brasileira."""
    try:
        from decimal import Decimal
        number = Decimal(str(value))
        formatted = f"{number:,.2f}"
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {formatted}"
    except Exception:
        return str(value)




@app.route("/registro/<int:record_id>/excluir", methods=["POST"])
@protected
def delete_record(record_id):
    user = get_user()

    with connect() as db:
        record = db.execute(
            "SELECT module FROM records WHERE id=? AND user_id=?",
            (record_id, user["id"])
        ).fetchone()

        if not record:
            flash("Registro nÃ£o encontrado.", "error")
            return redirect(url_for("dashboard"))

        db.execute(
            "DELETE FROM records WHERE id=? AND user_id=?",
            (record_id, user["id"])
        )

    flash("Registro excluÃ­do.", "success")
    return redirect(url_for("module_page", module=record["module"]))


app.jinja_env.globals["format_brl"] = format_brl

init_db()

if __name__ == "__main__":
    app.run(debug=True)

