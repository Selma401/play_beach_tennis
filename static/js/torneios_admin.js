// torneios_admin.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formNovoTorneio");
  const tbody = document.getElementById("tabelaTorneiosBody");
  const msg = document.getElementById("msgCriarTorneio");
  const btnCancelarEdicao = document.getElementById("btnCancelarEdicao");

  let torneioEditandoId = null;   // null = criando | número = editando
  let cacheTorneios = [];

  async function api(url, opts = {}) {
    opts.headers = { "Content-Type": "application/json" };
    opts.credentials = "include";
    if (opts.body && typeof opts.body !== "string") {
      opts.body = JSON.stringify(opts.body);
    }
    const res = await fetch(url, opts);
    return res.json();
  }

  // ===============================================
  // 🔄 CARREGAR LISTA DE TORNEIOS
  // ===============================================
  async function carregarTorneios() {
    const lista = await api("/api/torneios");
    cacheTorneios = lista || [];

    tbody.innerHTML = "";
    if (!lista || !lista.length) {
      tbody.innerHTML = `<tr><td colspan="4" class="empty">Nenhum torneio cadastrado.</td></tr>`;
      return;
    }

    lista.forEach(t => {
      const tr = document.createElement("tr");

      const statusBadgeMap = {
        aberto: '<span class="badge badge-open">ABERTO</span>',
        em_andamento: '<span class="badge badge-live">EM ANDAMENTO</span>',
        encerrado: '<span class="badge badge-closed">ENCERRADO</span>'
      };
      const statusHtml = statusBadgeMap[t.status] || `<span class="badge">${t.status || "-"}</span>`;

      tr.innerHTML = `
        <td>${t.id}</td>
        <td>${t.nome}</td>
        <td>${statusHtml}</td>
        <td>
          <button class="btn btn-sm btn-editar" data-id="${t.id}">✏️ Editar</button>
          <button class="btn btn-sm btn-alterar-status" data-id="${t.id}">🔄 Status</button>
          <button class="btn btn-sm btn-excluir" data-id="${t.id}">🗑 Excluir</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    registrarEventos();
  }

  // ===============================================
  // 🎯 REGISTRAR EVENTOS DOS BOTÕES DA TABELA
  // ===============================================
  function registrarEventos() {

    // ✏️ EDITAR — Preencher formulário
    document.querySelectorAll(".btn-editar").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const id = Number(e.currentTarget.dataset.id);
        const t = cacheTorneios.find(x => x.id === id);
        if (!t) return;

        // bloqueia edição se encerrado
        if (t.status === "encerrado") {
          alert("Este torneio está encerrado e não pode ser editado.");
          return;
        }

        if (!confirm(`Deseja editar o torneio "${t.nome}"?`)) return;

        torneioEditandoId = id;
        msg.style.color = "#333";
        msg.textContent = `Editando torneio #${id}`;

        document.getElementById("nomeTorneioNovo").value = t.nome || "";
        document.getElementById("dataTorneioNovo").value = t.data_evento || "";
        document.getElementById("valorTorneioNovo").value = t.preco || "";
        document.getElementById("vagasTorneioNovo").value = t.vagas || "";
        document.getElementById("premiacaoTorneioNovo").value = t.premiacao || "";

        if (btnCancelarEdicao) {
          btnCancelarEdicao.style.display = "inline-block";
        }
      });
    });

    // 🔄 ALTERAR STATUS
    document.querySelectorAll(".btn-alterar-status").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = Number(e.currentTarget.dataset.id);
        const resp = await api(`/api/torneios/${id}/status`, { method: "PUT" });

        alert(resp.mensagem || resp.erro || "Status atualizado.");
        carregarTorneios();
      });
    });

    // 🗑 EXCLUIR
    document.querySelectorAll(".btn-excluir").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = Number(e.currentTarget.dataset.id);

        // 1) Verifica se tem inscritos
        const inscritos = await api(`/api/torneios/${id}/inscritos`);
        if (Array.isArray(inscritos) && inscritos.length > 0) {
          alert("Não é possível excluir este torneio porque há inscritos vinculados.");
          return;
        }

        // 2) Confirma exclusão
        if (!confirm("Deseja realmente excluir este torneio?")) return;

        // 3) Exclui
        const resp = await api(`/api/torneios/${id}`, { method: "DELETE" });
        alert(resp.mensagem || resp.erro || "Torneio excluído.");
        carregarTorneios();
      });
    });
  }

  // ===============================================
  // ❌ CANCELAR EDIÇÃO
  // ===============================================
  if (btnCancelarEdicao) {
    btnCancelarEdicao.addEventListener("click", () => {
      form.reset();
      torneioEditandoId = null;
      msg.style.color = "#333";
      msg.textContent = "Modo criação de torneio.";
      btnCancelarEdicao.style.display = "none";
    });
  }

  // ===============================================
  // 💾 SALVAR TORNEIO (CRIAR ou EDITAR)
  // ===============================================
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      msg.textContent = "";

      const dados = {
        nome: document.getElementById("nomeTorneioNovo").value.trim(),
        data_evento: document.getElementById("dataTorneioNovo").value,
        preco: parseFloat(document.getElementById("valorTorneioNovo").value || 0),
        vagas: parseInt(document.getElementById("vagasTorneioNovo").value || 0),
        premiacao: parseFloat(document.getElementById("premiacaoTorneioNovo").value || 0)
      };

      if (!dados.nome) {
        msg.style.color = "red";
        msg.textContent = "Informe o nome do torneio.";
        return;
      }

      msg.style.color = "#555";
      msg.textContent = torneioEditandoId ? "Atualizando..." : "Salvando...";

      let resp;
      if (torneioEditandoId) {
        // EDITAR
        resp = await api(`/api/torneios/${torneioEditandoId}`, {
          method: "PUT",
          body: dados
        });
      } else {
        // CRIAR
        resp = await api("/api/torneios", {
          method: "POST",
          body: dados
        });
      }

      msg.style.color = resp.erro ? "red" : "green";
      msg.textContent = resp.erro || (torneioEditandoId ? "Torneio atualizado!" : "Torneio cadastrado com sucesso!");

      if (!resp.erro) {
        form.reset();
        torneioEditandoId = null;
        if (btnCancelarEdicao) btnCancelarEdicao.style.display = "none";
        carregarTorneios();
      }
    });
  }

  carregarTorneios();
});
