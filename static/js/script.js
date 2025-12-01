// ============================================================
// PLAY BEACH TENNIS - SCRIPT PRINCIPAL (USUÁRIO + ADMIN)
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

  // UTIL PARA REQUESTS
  async function apiFetch(url, opts = {}) {
    opts.headers = { "Content-Type": "application/json" };
    opts.credentials = "include";
    if (opts.body && typeof opts.body !== "string") opts.body = JSON.stringify(opts.body);
    const res = await fetch(url, opts);
    try { return await res.json(); } catch { return {}; }
  }

  // ============================================================
  // 🔐 LOGIN
  // ============================================================
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("email").value;
      const senha = document.getElementById("senha").value;
      const res = await apiFetch("/api/login", { method: "POST", body: { email, senha } });
      alert(res.mensagem || res.erro);
      if (res.mensagem) window.location.href = res.is_admin ? "/admin" : "/dashboard";
    });
  }

  // ============================================================
  // 📝 REGISTRO
  // ============================================================
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const campos = ["nome","cpf","sexo","idade","telefone","cidade","estado","email","senha"];
      const body = Object.fromEntries(campos.map(id => [id, document.getElementById(id).value.trim()]));
      const res = await apiFetch("/api/register", { method: "POST", body });
      alert(res.mensagem || res.erro);
      if (res.mensagem) window.location.href = "/login";
    });
  }

  // ============================================================
  // 🎯 PAINEL DO USUÁRIO → LISTAR TORNEIOS ABERTOS
  // ============================================================
  const listaTorneios = document.getElementById("listaTorneios");
  async function carregarTorneiosUsuario() {
    if (!listaTorneios) return;
    const torneios = await apiFetch("/api/torneios/abertos");
    listaTorneios.innerHTML = "";
    if (!torneios.length) return listaTorneios.innerHTML = "<p>Nenhum torneio aberto.</p>";

    torneios.forEach(t => {
      listaTorneios.innerHTML += `
        <div class="card fade-in" style="margin-bottom:10px;">
          <strong>${t.nome}</strong><br>
          📅 ${t.data_evento}<br>
          💰 R$ ${Number(t.preco).toFixed(2)}<br>
          🎟️ Vagas: ${t.vagas}<br>
          <span style="color:${t.status === 'aberto' ? 'green' : 'red'};font-weight:bold;">
              ${t.status.toUpperCase()}
          </span><br>
          ${t.status === 'aberto'
            ? `<button class="btn inscrever" data-id="${t.id}">Inscrever-se</button>`
            : `<span style="color:gray;">Encerrado</span>`}
        </div>`;
    });

    // Botão inscrever
    document.querySelectorAll(".inscrever").forEach(btn => {
      btn.addEventListener("click", async e => {
        const id = e.target.dataset.id;
        const r = await apiFetch("/api/inscricao", { method: "POST", body: { torneio_id: id } });
        alert(r.mensagem || r.erro);
      });
    });
  }
  if (listaTorneios) carregarTorneiosUsuario();

  // ============================================================
  // 📌 PAINEL DO USUÁRIO → MINHAS INSCRIÇÕES
  // ============================================================
  const minhasInscricoes = document.querySelector("#tabelaInscricoes tbody");
  async function carregarMinhasInscricoes() {
    if (!minhasInscricoes) return;
    const dados = await apiFetch("/api/minhas_inscricoes");
    minhasInscricoes.innerHTML = "";
    if (!dados.length) {
      return minhasInscricoes.innerHTML = "<tr><td colspan='5'>Nenhuma inscrição.</td></tr>";
    }
    dados.forEach(i => {
      minhasInscricoes.innerHTML += `
        <tr>
          <td>${i.torneio}</td>
          <td>R$ ${Number(i.valor).toFixed(2)}</td>
          <td>${i.forma_pagamento}</td>
          <td>${i.nivel}</td>
          <td>${i.data_inscricao}</td>
        </tr>`;
    });
  }
  if (minhasInscricoes) carregarMinhasInscricoes();

  // ============================================================
  // ⚙️ ADMIN → GERENCIAR TORNEIOS
  // ============================================================
  const tabelaTorneios = document.querySelector("#tabelaTorneios tbody");
  async function carregarTorneiosAdmin() {
    if (!tabelaTorneios) return;
    const torneios = await apiFetch("/api/torneios");
    tabelaTorneios.innerHTML = "";
    torneios.forEach(t => {
      const statusBadge =
        t.status === "encerrado" ? `<span style="color:red;">Encerrado</span>` :
        t.status === "em_andamento" ? `<span style="color:orange;">Em andamento</span>` :
        `<span style="color:green;">Aberto</span>`;

      tabelaTorneios.innerHTML += `
        <tr>
          <td>${t.id}</td>
          <td>${t.nome}</td>
          <td>${t.data_evento || "-"}</td>
          <td>R$ ${Number(t.preco).toFixed(2)}</td>
          <td>${statusBadge}</td>
          <td>
            ${t.status === "aberto"
              ? `<button class="btn iniciar" data-id="${t.id}">Iniciar</button>`
              : t.status === "em_andamento"
              ? `<button class="btn encerrar" data-id="${t.id}">Encerrar</button>`
              : `-`}
          </td>
        </tr>`;
    });

    // Iniciar
    document.querySelectorAll(".iniciar").forEach(btn => {
      btn.addEventListener("click", async e => {
        await apiFetch(`/api/torneios/${e.target.dataset.id}/status`, {
          method: "PUT", body: { status: "em_andamento" }
        });
        carregarTorneiosAdmin();
      });
    });

    // Encerrar
    document.querySelectorAll(".encerrar").forEach(btn => {
      btn.addEventListener("click", async e => {
        if (!confirm("Encerrar esse torneio?")) return;
        await apiFetch(`/api/torneios/${e.target.dataset.id}/status`, {
          method: "PUT", body: { status: "encerrado" }
        });
        carregarTorneiosAdmin();
      });
    });
  }
  if (tabelaTorneios) carregarTorneiosAdmin();

  // ============================================================
  // 🟢 NÃO CARREGA MAIS FINANCEIRO AQUI!
  // (O financeiro agora está 100% dentro do arquivo financeiro.html)
  // ============================================================

});
