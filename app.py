# ==========================================================
# PLAY BEACH TENNIS - SISTEMA DE GESTÃO ESPORTIVA (REVISÃO)
# ==========================================================
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from functools import wraps
from random import shuffle
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# --------------------------------------------
# 🔧 CONFIGURAÇÕES E INICIALIZAÇÃO
# --------------------------------------------
load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get("FLASK_SECRET")

bcrypt = Bcrypt(app)  # ← AGORA ESTÁ NO LUGAR CERTO

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}

app.config.update(
    MYSQL_HOST=os.environ.get("MYSQL_HOST"),
    MYSQL_USER=os.environ.get("MYSQL_USER"),
    MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD"),
    MYSQL_DB=os.environ.get("MYSQL_DB"),
    MYSQL_CURSORCLASS='DictCursor'
)
mysql = MySQL(app)

# --------------------------------------------
# 🔐 LOGIN API
# --------------------------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email", "").strip()
    senha = data.get("senha", "").strip()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cur.fetchone()
    cur.close()

    if not usuario or usuario["senha"] != senha:  # comparação direta
        return jsonify({"erro": "Credenciais inválidas"}), 401

    session["user_id"] = usuario["id"]
    session["user_nome"] = usuario["nome"]
    session["is_admin"] = usuario.get("is_admin", 0)

    return jsonify({"mensagem": "Login realizado com sucesso!"}), 200
# --------------------------------------------
# 🔐 PÁGINA RANKING ADMIN
# --------------------------------------------
@app.route('/ranking_admin')
def ranking_admin():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect('/login')
    return render_template('ranking_admin.html')


@app.route("/admin/ranking")
def admin_ranking():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect("/login")
    return render_template("admin/ranking_admin.html")

# --------------------------------------------
# 🔐 DECORADORES DE ACESSO
# --------------------------------------------
def login_required(f):
    """Requer que o usuário esteja logado para acessar a rota."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            # Redireciona para a página de login se não estiver logado
            return redirect(url_for('login_page')) 
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Requer que o usuário esteja logado E seja administrador."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            # Redireciona para o dashboard padrão se não for admin
            return redirect(url_for('dashboard')) 
        return f(*args, **kwargs)
    return decorated

# rota admin explícita (evita BuildError se templates usam url_for('dashboard_admin'))
@app.route('/admin')
@admin_required
def dashboard_admin():
    return render_template('dashboard_admin.html')

# ==========================================================
# 🌐 ROTAS DE PÁGINAS (FRONTEND)
# ==========================================================
@app.route('/')
def home(): 
    return render_template('index.html')

@app.route('/login')
def login_page(): 
    return render_template('login.html')

@app.route('/register')
def register_page(): 
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard(): 
    # Decide qual dashboard renderizar com base na sessão
    if session.get('is_admin'):
        return render_template('dashboard_admin.html')
    return render_template('dashboard_user.html')

@app.route('/ranking_usuario')
@login_required
def ranking_usuario():
    return render_template('ranking_usuario.html')

@app.route('/torneios_admin')
@admin_required
def torneios_admin_page():
    return render_template('torneios_admin.html')

@app.route('/partidas')
@admin_required
def partidas_page(): 
    return render_template('partidas.html')

@app.route('/financeiro')
@admin_required
def financeiro_page(): 
    return render_template('financeiro.html')

@app.route('/resultados')
def resultados_page(): 
    return render_template('resultados.html')

@app.route('/minhas-inscricoes')
@login_required
def minhas_inscricoes_page():
    return render_template('minhas_inscricoes.html')

@app.route('/perfil')
@login_required
def perfil_page():
    return render_template('perfil.html')

@app.route('/usuarios_admin')
@admin_required
def usuarios_admin_page():
    return render_template('usuarios_admin.html')

@app.route("/reservas")
@login_required
def reservas_page():
    return render_template("reservas.html")

@app.route('/reservas_admin')
@admin_required
def reservas_admin_page():
    return render_template("reservas_admin.html")

@app.route('/ranking')
@login_required
def ranking_page():
    # Página de ranking acessível para todos os logados
    return render_template('ranking.html')

# ==========================================================
# 💻 ROTAS DE API (BACKEND)
# ==========================================================

# --------------------------------------------
# 👤 LOGIN / REGISTRO / SESSÃO
# --------------------------------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    nome = data.get("nome", "").strip()
    cpf = data.get("cpf", "").strip()
    sexo = data.get("sexo", "").strip()
    idade = data.get("idade")
    telefone = data.get("telefone", "").strip()
    cidade = data.get("cidade", "").strip()
    estado = data.get("estado", "").strip()
    email = data.get("email", "").strip()
    senha = data.get("senha", "").strip()  # senha em texto puro

    # valida campos obrigatórios
    if not all([nome, cpf, sexo, idade, telefone, cidade, estado, email, senha]):
        return jsonify({"erro": "Preencha todos os campos obrigatórios"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (nome, cpf, sexo, idade, telefone, cidade, estado, email, senha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (nome, cpf, sexo, idade, telefone, cidade, estado, email, senha))
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensagem": "Usuário registrado com sucesso!"}), 200

    except Exception as e:
        print("Erro ao registrar:", e)
        return jsonify({"erro": "Erro ao registrar usuário"}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'mensagem': 'Sessão encerrada com sucesso!'})

@app.route('/api/session-info')
@login_required
def session_info():
    """Retorna informações básicas da sessão atual"""
    return jsonify({
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'is_admin': session.get('is_admin', False)
    })

@app.route("/reset/<token>", methods=["POST"])
def reset_password(token):
    senha = request.form["senha"]
    hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8")

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT email FROM reset_senha WHERE token=%s AND expiracao > NOW()", (token,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"error": "Token inválido ou expirado"})

    email = result["email"]
    cursor.execute("UPDATE usuarios SET senha=%s WHERE email=%s", (hash_senha, email))
    cursor.execute("DELETE FROM reset_senha WHERE token=%s", (token,))
    mysql.connection.commit()

    return jsonify({"success": True, "msg": "Senha atualizada!"})

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")

    email = request.form["email"]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
    usuario = cursor.fetchone()

    if not usuario:
        return render_template("forgot.html", msg="E-mail não encontrado!")

    # ❗ Simulação (não envia e-mail ainda)
    return redirect(url_for("reset", email=email))

@app.route("/reset", methods=["GET", "POST"])
def reset():
    email = request.args.get("email") or request.form.get("email")

    if request.method == "GET":
        # Apenas mostrar formulário de nova senha
        return render_template("reset.html", email=email)

    # Se chegou aqui → usuário enviou o formulário
    senha = request.form["senha"]
    confirmar = request.form["confirmar"]

    if senha != confirmar:
        return render_template("reset.html", email=email, msg="As senhas não coincidem!")

    hash_senha = bcrypt.generate_password_hash(senha).decode("utf-8")
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE usuarios SET senha=%s WHERE email=%s", (hash_senha, email))
    mysql.connection.commit()

    return render_template("login.html", msg="Senha atualizada com sucesso!")

# --------------------------------------------
# 🏆 TORNEIOS
# --------------------------------------------
# ==========================================================
# LISTAR TORNEIOS
# ==========================================================
@app.route('/api/torneios', methods=['GET'])
@login_required
def api_torneios():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            id,
            nome,
            status,
            data_evento,
            preco,
            vagas,
            premiacao
        FROM torneios
        ORDER BY id DESC
    """)
    torneios = cur.fetchall()
    cur.close()
    return jsonify(torneios)

# --------------------------------------------
# API que lista torneios para criação de partidas
# (usada por partidas.js -> /api/torneios/abertos)
# --------------------------------------------
@app.route('/api/torneios/abertos', methods=['GET'])
@login_required
def api_torneios_abertos():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, nome, status, data_evento
        FROM torneios
        WHERE status IN ('aberto', 'em_andamento')
        ORDER BY data_evento ASC
    """)
    torneios = cur.fetchall()
    cur.close()
    return jsonify(torneios)

# ==========================================================
# CRIAR TORNEIO
# ==========================================================
@app.route('/api/torneios', methods=['POST'])
@login_required
def criar_torneio():
    data = request.get_json()
    nome = data.get("nome", "").strip()
    data_evento = data.get("data_evento")
    preco = data.get("preco", 0)
    vagas = data.get("vagas", 0)
    premiacao = data.get("premiacao", 0)

    if not nome:
        return jsonify({"erro": "Informe o nome do torneio."}), 400

    cur = mysql.connection.cursor()

    # 🚫 Verificar se já existe um torneio igual antes de criar
    cur.execute("""
        SELECT id FROM torneios 
        WHERE nome = %s AND data_evento = %s
    """, (nome, data_evento))
    existente = cur.fetchone()

    if existente:
        cur.close()
        return jsonify({"erro": "Torneio já cadastrado com mesmo nome e mesma data."}), 409

    cur.execute("""
        INSERT INTO torneios (nome, data_evento, preco, vagas, premiacao, status)
        VALUES (%s, %s, %s, %s, %s, 'aberto')
    """, (nome, data_evento, preco, vagas, premiacao))
    mysql.connection.commit()
    cur.close()

    return jsonify({"mensagem": "Torneio criado com sucesso!"})

# ==========================================================
# LISTAR INSCRITOS DO TORNEIO
# ==========================================================
@app.route('/api/torneios/<int:torneio_id>/inscritos', methods=['GET'])
@admin_required
def listar_inscritos_do_torneio(torneio_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            i.id AS inscricao_id,
            u.id AS usuario_id,
            u.nome AS usuario_nome,
            u.cidade AS usuario_cidade,
            u.telefone AS usuario_telefone,
            i.nivel,
            i.categoria,
            i.tipo_partida,
            i.valor,
            i.forma_pagamento,
            i.data_inscricao,
            r.horario AS reserva_horario
        FROM inscricoes i
        JOIN usuarios u ON u.id = i.usuario_id
        LEFT JOIN reserva r ON r.id = i.reserva_id
        WHERE i.torneio_id = %s
        ORDER BY u.nome ASC
    """, (torneio_id,))

    inscritos = cur.fetchall()
    cur.close()

    # corrigir horário que vem como timedelta
    for ins in inscritos:
        if hasattr(ins["reserva_horario"], "strftime"):
            ins["reserva_horario"] = ins["reserva_horario"].strftime("%H:%M")

    return jsonify(inscritos)

# ==========================================================
# EDITAR TORNEIO (NÃO DUPLICAR)
# ==========================================================
@app.route('/api/torneios/<int:torneio_id>', methods=['PUT'])
@admin_required
def editar_torneio(torneio_id):
    data = request.get_json() or {}
    campos = ["nome", "data_evento", "preco", "vagas", "premiacao", "status"]

    atualizacoes = []
    valores = []

    # adiciona apenas campos enviados no body
    for campo in campos:
        if campo in data:
            atualizacoes.append(f"{campo}=%s")
            valores.append(data[campo])

    if not atualizacoes:
        return jsonify({"erro": "Nenhum campo informado"}), 400

    valores.append(torneio_id)

    cur = mysql.connection.cursor()
    cur.execute(f"""
        UPDATE torneios 
        SET {", ".join(atualizacoes)}
        WHERE id=%s
    """, tuple(valores))

    mysql.connection.commit()
    cur.close()

    return jsonify({"mensagem": "Torneio atualizado com sucesso!"})

# ==========================================================
# PÁGINA FORMULÁRIO DE EDIÇÃO
# ==========================================================
@app.route('/torneios_admin/editar/<int:torneio_id>')
@admin_required
def pagina_editar_torneio(torneio_id):
    cur = mysql.connection.cursor(dictionary=True)
    cur.execute("SELECT * FROM torneios WHERE id=%s", (torneio_id,))
    torneio = cur.fetchone()
    cur.close()

    if not torneio:
        return "Torneio não encontrado", 404

    return render_template("admin/editar_torneio.html", torneio=torneio)


# ==========================================================
# EXCLUIR TORNEIO
# ==========================================================
@app.route('/api/torneios/<int:torneio_id>', methods=['DELETE'])
@admin_required
def excluir_torneio(torneio_id):
    cur = mysql.connection.cursor()

    # Remove partidas e inscrições
    cur.execute("DELETE FROM partidas WHERE torneio_id = %s", (torneio_id,))
    cur.execute("DELETE FROM inscricoes WHERE torneio_id = %s", (torneio_id,))

    # Remove torneio
    cur.execute("DELETE FROM torneios WHERE id = %s", (torneio_id,))
    mysql.connection.commit()

    cur.close()
    return jsonify({"mensagem": "Torneio excluído com sucesso!"})


# ==========================================================
# ALTERAR STATUS DO TORNEIO
# ==========================================================
@app.route('/api/torneios/<int:torneio_id>/status', methods=['PUT'])
@admin_required
def alterar_status_torneio(torneio_id):
    cur = mysql.connection.cursor()

    cur.execute("SELECT status FROM torneios WHERE id=%s", (torneio_id,))
    row = cur.fetchone()

    if not row:
        return jsonify({"erro": "Torneio não encontrado"}), 404

    status = row['status']

    # alterna status
    novo_status = (
        "em_andamento" if status == "aberto" else
        "encerrado" if status == "em_andamento" else
        "aberto"
    )

    cur.execute("UPDATE torneios SET status=%s WHERE id=%s",
                (novo_status, torneio_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({"mensagem": f"Status alterado para {novo_status}!"})

@app.route('/api/minhas_inscricoes')
@login_required
def api_minhas_inscricoes():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.id, t.nome AS torneio, i.valor, i.forma_pagamento, i.nivel, i.data_inscricao
        FROM inscricoes i
        JOIN torneios t ON t.id = i.torneio_id
        WHERE i.usuario_id = %s
        ORDER BY i.data_inscricao DESC
    """, (session['user_id'],))
    inscricoes = cur.fetchall()
    cur.close()

    # garante datas formatadas (se quiser)
    for r in inscricoes:
        if r.get('data_inscricao') is not None:
            r['data_inscricao'] = str(r['data_inscricao'])

    return jsonify(inscricoes)

@app.route('/api/minhas_inscricoes', methods=['GET'])
@login_required
def minhas_inscricoes():
    user_id = session.get("user_id")
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            i.id,
            t.nome AS torneio,
            t.preco AS valor,
            i.forma_pagamento,
            i.categoria AS nivel,
            i.data_inscricao
        FROM inscricoes i
        JOIN torneios t ON t.id = i.torneio_id
        WHERE i.usuario_id = %s
        ORDER BY i.data_inscricao DESC
    """, (user_id,))

    rows = cur.fetchall()
    cur.close()

    return jsonify(rows)

# =========================
# PARTIDA - editar / excluir
# =========================
@app.route('/api/partidas/<int:partida_id>', methods=['PUT'])
@admin_required
def atualizar_partida(partida_id):
    data = request.get_json() or {}
    quadra = data.get('quadra')
    horario = data.get('horario')  # espera "HH:MM" ou None
    jogador1_id = data.get('jogador1_id')
    jogador1b_id = data.get('jogador1b_id')
    jogador2_id = data.get('jogador2_id')
    jogador2b_id = data.get('jogador2b_id')
    tipo_partida = data.get('tipo_partida')
    placar = data.get('placar')
    status = data.get('status')

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            UPDATE partidas
               SET quadra=%s, horario=%s, jogador1_id=%s, jogador1b_id=%s,
                   jogador2_id=%s, jogador2b_id=%s, tipo_partida=%s, placar=%s, status=%s
             WHERE id=%s
        """, (quadra, horario, jogador1_id or None, jogador1b_id or None,
              jogador2_id or None, jogador2b_id or None, tipo_partida or 'individual',
              placar or None, status or 'pendente', partida_id))
        mysql.connection.commit()
    except Exception as e:
        cur.close()
        return jsonify({'erro': f'Erro ao atualizar partida: {str(e)}'}), 500
    cur.close()
    return jsonify({'mensagem': 'Partida atualizada com sucesso!'})
    cur.close()
    
@app.route('/api/resultados', methods=['GET'])
@login_required
def api_listar_resultados():
    torneio_id = request.args.get('torneio_id')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = """
        SELECT
            p.id,
            p.torneio_id,
            t.nome AS torneio_nome,
            p.tipo_partida,
            p.quadra,
            p.horario,
            p.placar,
            p.jogador1_id,
            p.jogador1b_id,
            p.jogador2_id,
            p.jogador2b_id,
            u1.nome AS jogador1,
            u1b.nome AS jogador1b,
            u2.nome AS jogador2,
            u2b.nome AS jogador2b
        FROM partidas p
        JOIN torneios t ON p.torneio_id = t.id
        LEFT JOIN usuarios u1 ON p.jogador1_id = u1.id
        LEFT JOIN usuarios u1b ON p.jogador1b_id = u1b.id
        LEFT JOIN usuarios u2 ON p.jogador2_id = u2.id
        LEFT JOIN usuarios u2b ON p.jogador2b_id = u2b.id
        WHERE 1 = 1
    """

    params = []

    if torneio_id:
        query += " AND p.torneio_id = %s"
        params.append(torneio_id)

    if inicio:
        query += " AND DATE(p.horario) >= %s"
        params.append(inicio)

    if fim:
        query += " AND DATE(p.horario) <= %s"
        params.append(fim)

    query += " ORDER BY p.horario DESC"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(params))
    resultados = cur.fetchall()
    cur.close()

    # Converter horário para string
    for r in resultados:
        if r.get("horario") is not None:
            r["horario"] = str(r["horario"])

    return jsonify(resultados)

@app.route('/api/resultados', methods=['GET'])
def api_resultados():
    torneio_id = request.args.get('torneio_id')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = """
        SELECT 
            p.id,
            t.nome AS torneio,
            u1.nome AS jogador1,
            u2.nome AS jogador2,
            p.vencedor_id,
            uv.nome AS vencedor
        FROM partidas p
        JOIN torneios t ON t.id = p.torneio_id
        LEFT JOIN usuarios u1 ON u1.id = p.jogador1_id
        LEFT JOIN usuarios u2 ON u2.id = p.jogador2_id
        LEFT JOIN usuarios uv ON uv.id = p.vencedor_id
        WHERE 1=1
    """

    params = []

    if torneio_id:
        query += " AND t.id = %s"
        params.append(torneio_id)
    if inicio:
        query += " AND p.data_partida >= %s"
        params.append(inicio)
    if fim:
        query += " AND p.data_partida <= %s"
        params.append(fim)

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    dados = cur.fetchall()
    cur.close()
    return jsonify(dados)

# --------------------------------------------
# 🏅 RANKING DE CAMPEÕES
# --------------------------------------------
@app.route('/api/ranking_campeoes', methods=['GET'])
@login_required
def ranking_campeoes():
    """Conta quantos torneios cada atleta venceu (baseado na tabela partidas)."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            u.nome AS atleta,
            COUNT(DISTINCT p.torneio_id) AS torneios_ganhos
        FROM partidas p
        JOIN usuarios u ON p.vencedor_id = u.id
        WHERE p.vencedor_id IS NOT NULL
        GROUP BY u.id, u.nome
        ORDER BY torneios_ganhos DESC, atleta ASC
    """)
    ranking = cur.fetchall()
    cur.close()
    return jsonify(ranking)

@app.route("/api/ranking_campeoes")
def api_ranking_campeoes():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT 
            u.nome AS atleta,
            COALESCE(u.categoria, '-') AS categoria,
            COALESCE(u.nivel, '-') AS nivel,
            r.vitorias,
            r.derrotas,
            r.pontos,
            CASE 
                WHEN (r.vitorias + r.derrotas) = 0 THEN 0
                ELSE ROUND((r.vitorias / (r.vitorias + r.derrotas)) * 100, 1)
            END AS aproveitamento
        FROM ranking r
        JOIN usuarios u ON u.id = r.usuario_id
        ORDER BY r.pontos DESC, r.vitorias DESC;
    """)

    dados = cursor.fetchall()
    return jsonify(dados)


# ==========================
# RESERVAS (quadras / horários)
# ==========================
@app.route('/api/reservas', methods=['GET'])
@login_required
def listar_reservas():
    torneio_id = request.args.get('torneio_id')
    cur = mysql.connection.cursor()

    if torneio_id:
        cur.execute("SELECT * FROM reserva WHERE torneio_id=%s ORDER BY horario", (torneio_id,))
    else:
        cur.execute("SELECT * FROM reserva ORDER BY torneio_id, horario")

    rows = cur.fetchall()
    cur.close()

    # Convertendo timedelta/time para string
    for r in rows:
        if isinstance(r.get("horario"), (timedelta,)):
            total_seconds = r["horario"].total_seconds()
            horas = int(total_seconds // 3600)
            minutos = int((total_seconds % 3600) // 60)
            r["horario"] = f"{horas:02d}:{minutos:02d}"

        elif hasattr(r.get("horario"), "strftime"):
            r["horario"] = r["horario"].strftime("%H:%M")

    return jsonify(rows)

@app.route('/api/reservas/<int:reserva_id>', methods=['GET'])
@login_required
def get_reserva(reserva_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM reserva WHERE id=%s", (reserva_id,))
    row = cur.fetchone()
    cur.close()
    if not row:
        return jsonify({'erro': 'Reserva não encontrada'}), 404
    return jsonify(row)

@app.route('/api/reservas', methods=['POST'])
@admin_required
def criar_reserva():
    """Criar reserva de quadra (admin). body: torneio_id, quadra, horario, reservado (0/1), usuario_id (opcional)"""
    data = request.get_json() or {}
    torneio_id = data.get('torneio_id')
    quadra = data.get('quadra', 'Quadra 1')
    horario = data.get('horario')  # 'HH:MM:SS' or 'HH:MM'
    reservado = 1 if data.get('reservado') else 0
    usuario_id = data.get('usuario_id')

    if not torneio_id or not horario:
        return jsonify({'erro': 'torneio_id e horario são obrigatórios'}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO reserva (torneio_id, quadra, horario, reservado, usuario_id)
        VALUES (%s,%s,%s,%s,%s)
    """, (torneio_id, quadra, horario, reservado, usuario_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'mensagem': 'Reserva criada com sucesso!'})

@app.route('/api/reservas/<int:reserva_id>', methods=['PUT'])
@admin_required
def atualizar_reserva(reserva_id):
    """Atualiza campos da reserva (admin)."""
    data = request.get_json() or {}
    campos = []
    valores = []
    for c in ('torneio_id','quadra','horario','reservado','usuario_id'):
        if c in data:
            campos.append(f"{c}=%s")
            if c == 'reservado':
                valores.append(1 if data[c] else 0)
            else:
                valores.append(data[c])
    if not campos:
        return jsonify({'erro': 'Nenhum campo informado'}), 400
    valores.append(reserva_id)
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE reserva SET {', '.join(campos)} WHERE id=%s", tuple(valores))
    mysql.connection.commit()
    cur.close()
    return jsonify({'mensagem': 'Reserva atualizada com sucesso!'})

@app.route('/api/reservas/<int:reserva_id>', methods=['DELETE'])
@admin_required
def excluir_reserva(reserva_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM reserva WHERE id=%s", (reserva_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'mensagem': 'Reserva excluída com sucesso!'})

# rota para o usuário reservar/desmarcar (toggle) — usa sessão do usuário
@app.route('/api/reservas/<int:reserva_id>/toggle', methods=['POST'])
@login_required
def toggle_reserva(reserva_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT reservado, usuario_id FROM reserva WHERE id=%s", (reserva_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        return jsonify({'erro': 'Reserva não encontrada'}), 404

    # se livre, reserva para o user; se ocupada pelo mesmo usuário, libera; se ocupada por outro, erro
    if r['reservado'] == 0:
        cur.execute("UPDATE reserva SET reservado=1, usuario_id=%s WHERE id=%s", (session['user_id'], reserva_id))
        mysql.connection.commit()
        cur.close()
        return jsonify({'mensagem': 'Reserva efetuada com sucesso!'})
    else:
        if r['usuario_id'] == session['user_id']:
            cur.execute("UPDATE reserva SET reservado=0, usuario_id=NULL WHERE id=%s", (reserva_id,))
            mysql.connection.commit()
            cur.close()
            return jsonify({'mensagem': 'Reserva cancelada.'})
        else:
            cur.close()
            return jsonify({'erro': 'Reserva ocupada por outro usuário.'}), 403

# rota rápida para pegar reservas livres de um torneio
@app.route('/api/reservas/disponiveis', methods=['GET'])
@login_required
def reservas_disponiveis():
    torneio_id = request.args.get('torneio_id')
    cur = mysql.connection.cursor()
    if torneio_id:
        cur.execute("SELECT * FROM reserva WHERE torneio_id=%s AND reservado=0 ORDER BY horario", (torneio_id,))
    else:
        cur.execute("SELECT * FROM reserva WHERE reservado=0 ORDER BY torneio_id, horario")
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)
# --------------------------------------------
# 🧾 INSCRIÇÕES (Exemplo: Inscrever atleta)
# --------------------------------------------
@app.route('/api/inscricao', methods=['POST'])
@login_required
def inscrever_atleta():
    data = request.get_json() or {}

    torneio_id = data.get('torneio_id')
    forma_pagamento = str(data.get('forma_pagamento', '')).strip().lower()
    nivel = data.get('nivel', 'iniciante')
    tipo_partida = data.get("tipo_partida", "individual")
    categoria = data.get("categoria", "C")

    formas_validas = ["pix", "cartao_credito", "cartao_debito", "dinheiro", "transferencia"]
    if forma_pagamento not in formas_validas:
        return jsonify({"erro": "Forma de pagamento inválida."}), 400

    cur = mysql.connection.cursor()

    # 1️⃣ verifica inscrição duplicada
    cur.execute("""
        SELECT id FROM inscricoes
        WHERE usuario_id = %s AND torneio_id = %s
    """, (session['user_id'], torneio_id))
    row = cur.fetchone()
    if row:
        cur.close()
        return jsonify({"erro": "Você já está inscrito neste torneio."}), 400

    # 2️⃣ pega o preço do torneio
    cur.execute("SELECT preco FROM torneios WHERE id=%s", (torneio_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({'erro': 'Torneio não encontrado'}), 404

    valor = row['preco']   # <-- CORRETO

    try:
        cur.execute("""
            INSERT INTO inscricoes 
                (usuario_id, torneio_id, valor, forma_pagamento, nivel, tipo_partida, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session['user_id'],
            torneio_id,
            valor,
            forma_pagamento,
            nivel,
            tipo_partida,
            categoria
        ))
        mysql.connection.commit()

    except Exception as e:
        cur.close()
        return jsonify({'erro': f'Erro na inscrição: {str(e)}'}), 500

    finally:
        cur.close()

    return jsonify({'mensagem': f'Inscrição registrada com sucesso! Forma: {forma_pagamento}'})

# ================================================================
# ❌ REMOVER INSCRIÇÃO DO TORNEIO
# ================================================================
@app.route('/api/inscricoes/<int:inscricao_id>', methods=['DELETE'])
@login_required
def remover_inscricao(inscricao_id):
    cur = mysql.connection.cursor()

    try:
        # Remove a inscrição — tabela provavelmente é inscricoes
        cur.execute("DELETE FROM inscricoes WHERE id = %s", (inscricao_id,))
        mysql.connection.commit()
        
        return jsonify({"mensagem": "Inscrição removida com sucesso!"})
    
    except Exception as e:
        print("Erro ao remover inscrição:", e)
        return jsonify({"erro": "Erro ao remover inscrição."}), 500

    finally:
        cur.close()

@app.route("/api/partidas/<int:torneio_id>", methods=["GET"])
@login_required
def listar_partidas_torneio(torneio_id):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.torneio_id,
            t.nome AS torneio_nome,
            p.tipo_partida,
            p.quadra,
            p.horario,
            p.placar,
            p.jogador1_id,
            p.jogador1b_id,
            p.jogador2_id,
            p.jogador2b_id,
            u1.nome AS jogador1,
            u1b.nome AS jogador1b,
            u2.nome AS jogador2,
            u2b.nome AS jogador2b
        FROM partidas p
        JOIN torneios t ON p.torneio_id = t.id
        LEFT JOIN usuarios u1 ON p.jogador1_id = u1.id
        LEFT JOIN usuarios u1b ON p.jogador1b_id = u1b.id
        LEFT JOIN usuarios u2 ON p.jogador2_id = u2.id
        LEFT JOIN usuarios u2b ON p.jogador2b_id = u2b.id
        WHERE p.torneio_id = %s
        ORDER BY p.id ASC
    """, (torneio_id,))

    partidas = cur.fetchall()
    cur.close()

    # Converte datetime do MySQL para string tratável no frontend
    for p in partidas:
        if p.get("horario") is not None:
            p["horario"] = str(p["horario"])

    return jsonify(partidas)

@app.route('/api/partidas/manual', methods=['POST'])
@admin_required
def criar_partida_manual():
    data = request.get_json() or {}

    torneio_id = data.get('torneio_id')
    tipo = data.get('tipo_partida', 'individual')
    j1 = data.get('jogador1_id')
    j1b = data.get('jogador1b_id')
    j2 = data.get('jogador2_id')
    j2b = data.get('jogador2b_id')
    quadra = data.get('quadra')
    horario = data.get('horario')  # formato HH:MM ou None

    if not torneio_id or not j1 or not j2:
        return jsonify({'erro': 'Torneio e dois jogadores são obrigatórios.'}), 400

    cur = mysql.connection.cursor()

    try:
        # Pega nome do torneio
        cur.execute("SELECT nome FROM torneios WHERE id=%s", (torneio_id,))
        t = cur.fetchone()
        torneio_nome = t['nome'] if t else None

        # Salva a partida
        cur.execute("""
            INSERT INTO partidas (
                torneio_id, torneio_nome, tipo_partida,
                jogador1_id, jogador1b_id,
                jogador2_id, jogador2b_id,
                quadra, horario
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            torneio_id, torneio_nome, tipo,
            j1, j1b,
            j2, j2b,
            quadra, horario
        ))

        mysql.connection.commit()

    except Exception as e:
        cur.close()
        return jsonify({'erro': str(e)}), 500

    cur.close()
    return jsonify({'mensagem': 'Partida criada com sucesso!'})

# --------------------------------------------
# 🎾 PARTIDAS (Criação Automática)
# --------------------------------------------
@app.route('/api/partidas/auto', methods=['POST'])
@admin_required
def gerar_partidas_auto():
    """Gera partidas automáticas (individual ou duplas) respeitando i.tipo_partida."""
    data = request.get_json() or {}
    torneio_id = data.get('torneio_id')
    tipo = data.get('tipo_partida', 'individual')

    if not torneio_id:
        return jsonify({'erro': 'ID do torneio não informado'}), 400

    cur = mysql.connection.cursor()

    # busca inscritos que DECLARARAM esse tipo de partida (filtra por tipo)
    cur.execute("""
        SELECT u.id AS usuario_id, u.sexo
        FROM inscricoes i
        JOIN usuarios u ON u.id = i.usuario_id
        WHERE i.torneio_id = %s AND i.tipo_partida = %s
    """, (torneio_id, tipo))
    jogadores = cur.fetchall()
    jogadores = [dict(x) for x in jogadores]  # lista de dicts com usuario_id, sexo

    if len(jogadores) < 2:
        cur.close()
        return jsonify({'erro': 'Jogadores insuficientes para gerar partidas desse tipo'}), 400

    # nome do torneio
    cur.execute("SELECT nome FROM torneios WHERE id=%s", (torneio_id,))
    row = cur.fetchone()
    torneio_nome = row["nome"] if row else "Torneio"

    # embaralha
    from random import shuffle
    shuffle(jogadores)

    partidas_geradas = 0

    # INDIVIDUAL: emparelha 1x1 por ordem
    if tipo == "individual":
        for i in range(0, len(jogadores), 2):
            if i + 1 < len(jogadores):
                j1 = jogadores[i]["usuario_id"]
                j2 = jogadores[i+1]["usuario_id"]
                # evita mesma pessoa duas vezes (por segurança)
                if j1 == j2: 
                    continue
                cur.execute("""
                    INSERT INTO partidas 
                    (torneio_id, torneio_nome, tipo_partida, jogador1_id, jogador2_id, fase, quadra, status)
                    VALUES (%s,%s,%s,%s,%s,'primeira','Quadra 1','pendente')
                """, (torneio_id, torneio_nome, tipo, j1, j2))
                partidas_geradas += 1

    else:
        # para duplas: vamos formar equipes de 2 por time.
        # dupla_mista: preferir montar times M+F (se possível)
        ids = [p["usuario_id"] for p in jogadores]
        sexes = {p["usuario_id"]: p["sexo"] for p in jogadores}

        if tipo == "dupla_mista":
            # separe por sexo
            males = [i for i in ids if sexes.get(i) in ('M','m','masculino','Masculino')]
            females = [i for i in ids if sexes.get(i) in ('F','f','feminino','Feminino')]
            teams = []
            # formar times M+F
            while males and females:
                a = males.pop()
                b = females.pop()
                teams.append((a,b))
            # se sobrar gente (pares do mesmo sexo), combine por pares
            leftovers = males + females
            while len(leftovers) >= 2:
                a = leftovers.pop()
                b = leftovers.pop()
                teams.append((a,b))
        else:
            # dupla_masculina ou dupla_feminina — apenas agrupa por pares (já filtrado por i.tipo_partida)
            teams = []
            tmp = ids[:]
            while len(tmp) >= 2:
                a = tmp.pop()
                b = tmp.pop()
                teams.append((a,b))

        # agora combine times em partidas (cada partida = teamA vs teamB)
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                t1 = teams[i]
                t2 = teams[i+1]
                # insere partida com j1/j1b e j2/j2b
                cur.execute("""
                    INSERT INTO partidas 
                    (torneio_id, torneio_nome, tipo_partida,
                     jogador1_id, jogador1b_id,
                     jogador2_id, jogador2b_id,
                     fase, quadra, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,'primeira','Quadra 1','pendente')
                """, (torneio_id, torneio_nome, tipo, t1[0], t1[1], t2[0], t2[1]))
                partidas_geradas += 1

    mysql.connection.commit()
    cur.close()
    return jsonify({"mensagem": f"{partidas_geradas} partidas ({tipo.replace('_',' ')}) geradas com sucesso!"})

# ============================
# FUNÇÃO DE ATUALIZAÇÃO DO RANKING
# ============================
# ----- RANKING HELPERS (COLE APÓS mysql = MySQL(app)) -----
def garantir_registro_ranking(usuario_id):
    """Cria registro na tabela ranking se não existir."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM ranking WHERE usuario_id=%s", (usuario_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO ranking (usuario_id, pontos, vitorias, derrotas) VALUES (%s, 0, 0, 0)", (usuario_id,))
        mysql.connection.commit()
    cur.close()

def atualizar_ranking(usuario_id, venceu=True):
    """
    Atualiza a tabela de Franking:
    - vence -> +50 pontos e +1 vitoria
    - perde  -> +1 ponto e +1 derrota
    """
    if usuario_id is None:
        return

    garantir_registro_ranking(usuario_id)

    cur = mysql.connection.cursor()
    try:
        if venceu:
            cur.execute("""
                UPDATE ranking
                SET pontos = pontos + 50,
                    vitorias = vitorias + 1,
                    atualizacao = CURRENT_TIMESTAMP
                WHERE usuario_id = %s
            """, (usuario_id,))
        else:
            cur.execute("""
                UPDATE ranking
                SET pontos = pontos + 1,
                    derrotas = derrotas + 1,
                    atualizacao = CURRENT_TIMESTAMP
                WHERE usuario_id = %s
            """, (usuario_id,))
        mysql.connection.commit()
    finally:
        cur.close()
        
def atualizar_ranking_inscricao(jogador_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ranking (jogador_id, inscricoes, pontos)
        VALUES (%s, 1, 10)
        ON DUPLICATE KEY UPDATE
            inscricoes = inscricoes + 1,
            pontos = pontos + 10
    """, (jogador_id,))
    mysql.connection.commit()

def atualizar_ranking_vitoria(vencedor_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE ranking
        SET vitorias = vitorias + 1,
            pontos = pontos + 20
        WHERE jogador_id = %s
    """, (vencedor_id,))
    mysql.connection.commit()

@app.route('/api/partidas/<int:torneio_id>', methods=['GET'])
@login_required
def api_listar_partidas(torneio_id):
    query = """
        SELECT
            p.id,
            p.torneio_id,
            t.nome AS torneio_nome,
            p.tipo_partida,
            p.quadra,
            p.horario,
            p.placar,

            -- IDs dos jogadores (❗ necessários para selecionar vencedor)
            p.jogador1_id,
            p.jogador1b_id,
            p.jogador2_id,
            p.jogador2b_id,

            -- Nomes (visuais)
            u1.nome  AS jogador1,
            u1b.nome AS jogador1b,
            u2.nome  AS jogador2,
            u2b.nome AS jogador2b
        FROM partidas p
        JOIN torneios t         ON t.id        = p.torneio_id
        LEFT JOIN usuarios u1   ON u1.id       = p.jogador1_id
        LEFT JOIN usuarios u1b  ON u1b.id      = p.jogador1b_id
        LEFT JOIN usuarios u2   ON u2.id       = p.jogador2_id
        LEFT JOIN usuarios u2b  ON u2b.id      = p.jogador2b_id
        WHERE p.torneio_id = %s
        ORDER BY p.id ASC
    """

    cur = mysql.connection.cursor()
    cur.execute(query, (torneio_id,))
    partidas = cur.fetchall()
    cur.close()

    # converter horário para string, senão dá erro no JSON
    for p in partidas:
        if p.get("horario") is not None:
            p["horario"] = str(p["horario"])

    return jsonify(partidas)

@app.route('/api/partidas/<int:partida_id>/resultado', methods=['PUT'])
@admin_required
def atualizar_resultado(partida_id):
    data = request.get_json() or {}
    placar = data.get("placar")
    vencedor_id = data.get("vencedor_id")

    if not vencedor_id:
        return jsonify({"erro": "Informe vencedor_id"}), 400

    cur = mysql.connection.cursor()
    try:
        # pega jogadores da partida (inclui jogadores de dupla)
        cur.execute("""
            SELECT jogador1_id, jogador1b_id, jogador2_id, jogador2b_id
            FROM partidas
            WHERE id=%s
        """, (partida_id,))
        p = cur.fetchone()
        if not p:
            return jsonify({"erro": "Partida não encontrada"}), 404

        # atualiza partida
        cur.execute("""
            UPDATE partidas
            SET placar=%s, vencedor_id=%s, status='finalizada'
            WHERE id=%s
        """, (placar, vencedor_id, partida_id))
        mysql.connection.commit()

        # determina perdedor(es) — para ranking individual, escolhemos o outro jogador principal
        j1 = p.get('jogador1_id')
        j2 = p.get('jogador2_id')

    except Exception as e:
        cur.close()
        return jsonify({"erro": f"Erro ao gravar resultado: {str(e)}"}), 500

    cur.close()

    try:
        # atualiza ranking: vencedor ganha, perdedor perde
        atualizar_ranking(int(vencedor_id), venceu=True)

        # se for individual/perfil simples, identifica perdedor
        if j1 and j2:
            perdedor = j1 if int(j1) != int(vencedor_id) else j2
            atualizar_ranking(int(perdedor), venceu=False)
        # para duplas, você pode expandir a lógica para contar por equipe (não implementado aqui)
    except Exception as e:
        return jsonify({"mensagem": "Resultado salvo, mas falha ao atualizar ranking", "erro": str(e)}), 200

    return jsonify({"mensagem": "Resultado atualizado e ranking ajustado!"})

@app.route('/api/partidas/<int:partida_id>', methods=['DELETE'])
@admin_required
def excluir_partida(partida_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM partidas WHERE id=%s", (partida_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"mensagem": "Partida excluída com sucesso!"})
# --------------------------------------------
@app.route("/api/ranking")
def api_ranking():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT 
            u.nome AS nome,
            COALESCE(r.vitorias, 0) AS vitorias,
            COALESCE(r.pontos, 0) AS pontos
        FROM usuarios u
        LEFT JOIN ranking r ON r.usuario_id = u.id
        ORDER BY pontos DESC, vitorias DESC
    """)

    dados = cursor.fetchall()
    cursor.close()
    return jsonify(dados)
# --------------------------------------------

@app.route('/api/usuarios', methods=['GET'])
@admin_required
def listar_usuarios():
    """Lista todos os usuários cadastrados (somente admin)."""
    cur = mysql.connection.cursor()
    cur.execute("""
    SELECT id, nome, email, telefone, cidade, estado, cpf, sexo, idade, is_admin
    FROM usuarios
    ORDER BY id DESC
""")

    usuarios = cur.fetchall()
    cur.close()
    return jsonify(usuarios)

@app.route('/api/usuario/<int:usuario_id>', methods=['GET'])
@login_required
def get_usuario(usuario_id):
    cur = mysql.connection.cursor()
    # selecione apenas colunas existentes no seu schema
    cur.execute("""
        SELECT id, nome, email, sexo, telefone, cidade, estado
        FROM usuarios
        WHERE id = %s
    """, (usuario_id,))
    user = cur.fetchone()
    cur.close()
    if not user:
        return jsonify({'erro': 'Usuário não encontrado'}), 404
    return jsonify(user)

@app.route('/api/usuario/update', methods=['PUT'])
@login_required
def update_usuario():
    data = request.get_json()

    campos_validos = ['nome', 'email', 'sexo', 'data_nascimento', 'telefone', 'cidade', 'estado']
    atualizacoes = []
    valores = []

    for campo in campos_validos:
        if campo in data:
            atualizacoes.append(f"{campo} = %s")
            valores.append(data[campo])

    if not atualizacoes:
        return jsonify({'erro': 'Nenhum campo válido para atualizar'}), 400

    valores.append(session['user_id'])  # Atualiza o usuário logado
    query = f"UPDATE usuarios SET {', '.join(atualizacoes)} WHERE id = %s"

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(valores))
    mysql.connection.commit()
    cur.close()

    return jsonify({'mensagem': 'Perfil atualizado com sucesso!'})

@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    data = request.get_json() or {}

    nome = str(data.get("nome", "")).strip()
    email = str(data.get("email", "")).strip()
    telefone = str(data.get("telefone", "")).strip()
    cidade = str(data.get("cidade", "")).strip()
    estado = str(data.get("estado", "")).strip().upper()
    cpf = str(data.get("cpf", "")).strip()
    idade = data.get("idade") or None
    sexo = data.get("sexo")   # ⚠ não usar strip aqui
    senha = data.get("senha")

    cur = mysql.connection.cursor()

    # 🔥 Se sexo NÃO for enviado, não alterar o campo no banco
    if not sexo:  
        sql = """
            UPDATE usuarios SET
                nome=%s, email=%s, telefone=%s, cidade=%s, estado=%s,
                cpf=%s, idade=%s
            WHERE id=%s
        """
        cur.execute(sql, (nome, email, telefone, cidade, estado, cpf, idade, user_id))

    else:
        # Quando sexo vier preenchido, atualiza
        if not senha:
            sql = """
                UPDATE usuarios SET
                    nome=%s, email=%s, telefone=%s, cidade=%s, estado=%s,
                    cpf=%s, sexo=%s, idade=%s
                WHERE id=%s
            """
            cur.execute(sql, (nome, email, telefone, cidade, estado, cpf, sexo, idade, user_id))
        else:
            senha_hash = bcrypt.generate_password_hash(senha).decode("utf-8")
            sql = """
                UPDATE usuarios SET
                    nome=%s, email=%s, telefone=%s, cidade=%s, estado=%s,
                    cpf=%s, sexo=%s, idade=%s, senha=%s
                WHERE id=%s
            """
            cur.execute(sql, (nome, email, telefone, cidade, estado, cpf, sexo, idade, senha_hash, user_id))

    mysql.connection.commit()
    cur.close()
    return jsonify({"mensagem": "Usuário atualizado com sucesso!"})

@app.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
def excluir_usuario(usuario_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'mensagem': 'Usuário excluído com sucesso'})

# ==========================================================
# 💰 ROTAS DE FINANCEIRO
# ==========================================================
@app.route('/api/financeiro/inscricoes')
@admin_required
def api_financeiro_inscricoes():
    """Lista inscrições com informações financeiras"""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT i.id, u.nome AS atleta, t.nome AS torneio, i.forma_pagamento, i.valor, i.data_inscricao
        FROM inscricoes i
        JOIN usuarios u ON i.usuario_id = u.id
        JOIN torneios t ON i.torneio_id = t.id
        ORDER BY i.data_inscricao DESC
    """)
    data = cur.fetchall()
    cur.close()
    return jsonify(data)


@app.route('/api/financeiro/vendas', methods=['GET', 'POST'])
@admin_required
def api_financeiro_vendas():
    """Lista e cadastra vendas do evento"""
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        data = request.get_json()
        desc = data.get('descricao')
        valor = data.get('valor')
        forma = data.get('forma_pagamento')
        if not desc or not valor or not forma:
            return jsonify({'erro': 'Campos obrigatórios faltando'}), 400

        cur.execute("""
            INSERT INTO vendas (descricao, valor, forma_pagamento, data_venda)
            VALUES (%s, %s, %s, NOW())
        """, (desc, valor, forma))
        mysql.connection.commit()
        cur.close()
        return jsonify({'mensagem': 'Venda registrada com sucesso!'})

    cur.execute("""
        SELECT id, descricao, valor, forma_pagamento, data_venda
        FROM vendas
        ORDER BY data_venda DESC
    """)
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/api/financeiro/inscricoes', methods=['GET'])
@admin_required
def financeiro_inscricoes():
    torneio = request.args.get('torneio')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = """
        SELECT 
            i.id,
            u.nome AS atleta,
            t.nome AS torneio,
            i.valor,
            i.forma_pagamento,
            i.data_inscricao
        FROM inscricoes i
        JOIN usuarios u ON u.id = i.usuario_id
        JOIN torneios t ON t.id = i.torneio_id
        WHERE 1=1
    """
    params = []

    if torneio:
        query += " AND t.id = %s"
        params.append(torneio)
    if inicio:
        query += " AND i.data_inscricao >= %s"
        params.append(inicio)
    if fim:
        query += " AND i.data_inscricao <= %s"
        params.append(fim)

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    cur.close()
    return jsonify(data)

@app.route('/api/financeiro/fluxo')
@admin_required
def api_financeiro_fluxo():
    cur = mysql.connection.cursor()

    # Entradas
    cur.execute("""
        SELECT forma_pagamento, SUM(valor) AS total
        FROM inscricoes
        GROUP BY forma_pagamento
    """)
    inscricoes = {r['forma_pagamento']: float(r['total']) for r in cur.fetchall()}

    cur.execute("""
        SELECT forma_pagamento, SUM(valor) AS total
        FROM vendas
        GROUP BY forma_pagamento
    """)
    vendas = {r['forma_pagamento']: float(r['total']) for r in cur.fetchall()}

    # 💸 Saída: premiações
    cur.execute("SELECT SUM(premiacao) AS total_premiacoes FROM torneios WHERE status = 'encerrado'")
    row = cur.fetchone()
    total_premiacoes = float(row['total_premiacoes'] or 0)
    cur.close()

    # Garante que todas as formas existam
    formas = ["dinheiro","pix","cartao_credito","cartao_debito","transferencia"]
    result = {
        "inscricoes": {f: inscricoes.get(f, 0) for f in formas},
        "vendas": {f: vendas.get(f, 0) for f in formas},
        "premiacoes": total_premiacoes
    }

    return jsonify(result)

@app.route('/api/financeiro/fluxo', methods=['GET'])
@admin_required
def financeiro_fluxo():
    cur = mysql.connection.cursor()

    # somatórios por forma de pagamento
    formas = ["dinheiro", "pix", "cartao_credito", "cartao_debito", "transferencia"]
    resp = {"inscricoes": {}, "vendas": {}}

    for f in formas:
        cur.execute("SELECT COALESCE(SUM(valor),0) AS total FROM inscricoes WHERE forma_pagamento=%s", (f,))
        resp["inscricoes"][f] = float(cur.fetchone()['total'])

        cur.execute("SELECT COALESCE(SUM(valor),0) AS total FROM vendas WHERE forma_pagamento=%s", (f,))
        resp["vendas"][f] = float(cur.fetchone()['total'])

    cur.close()
    return jsonify(resp)

@app.route('/api/financeiro/vendas', methods=['GET'])
@admin_required
def financeiro_vendas():
    torneio = request.args.get('torneio')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = """
        SELECT 
            id, descricao, forma_pagamento, valor, data_venda
        FROM vendas
        WHERE 1=1
    """
    params = []

    if inicio:
        query += " AND data_venda >= %s"
        params.append(inicio)
    if fim:
        query += " AND data_venda <= %s"
        params.append(fim)

    cur = mysql.connection.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


@app.route('/api/financeiro/vendas', methods=['POST'])
@admin_required
def registrar_venda():
    data = request.get_json() or {}
    descricao = data.get("descricao")
    forma = data.get("forma_pagamento")
    valor = data.get("valor")

    if not descricao or not forma or not valor:
        return jsonify({"erro": "Dados incompletos"}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO vendas (descricao, forma_pagamento, valor)
        VALUES (%s, %s, %s)
    """, (descricao, forma, valor))
    mysql.connection.commit()
    cur.close()
    return jsonify({"mensagem": "Venda registrada!"})

@app.route('/api/ranking/recalcular', methods=['POST'])
@admin_required
def recalcular_ranking():
    cur = mysql.connection.cursor()
    try:
        # zera contadores
        cur.execute("UPDATE ranking SET pontos=0, vitorias=0, derrotas=0")

        # recalcula vitorias por vencedor
        cur.execute("""
            SELECT vencedor_id AS usuario_id, COUNT(*) AS vitorias
            FROM partidas
            WHERE vencedor_id IS NOT NULL
            GROUP BY vencedor_id
        """)
        wins = cur.fetchall()

        for w in wins:
            cur.execute("""
                INSERT INTO ranking (usuario_id, pontos, vitorias, derrotas)
                VALUES (%s, %s, %s, 0)
                ON DUPLICATE KEY UPDATE pontos = %s, vitorias = %s
            """, (w['usuario_id'], w['vitorias'] * 10, w['vitorias'], w['vitorias'] * 10, w['vitorias']))

        # opcional: recompute derrotas se você tiver lógica para isso
        mysql.connection.commit()
    finally:
        cur.close()

    return jsonify({'mensagem': 'Ranking recalculado com sucesso.'})


# ==========================================================
# 🚀 MAIN
# ==========================================================
if __name__ == '__main__':
    # Define o debug como True se não for em produção
    app.run(debug=True)