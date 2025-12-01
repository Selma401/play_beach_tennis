// ================================
//  Gestão de Usuários — Painel Admin
// ================================

document.addEventListener("DOMContentLoaded", () => {

  const tbody = document.querySelector("#tabelaUsuarios tbody");

  // Modal
  const modal = document.getElementById("modal-edicao");
  const form = document.getElementById("formEdicao");
  const cancel = document.getElementById("cancelarEdicao");

  const f_id = document.getElementById("edit-id");
  const f_nome = document.getElementById("edit-nome");
  const f_email = document.getElementById("edit-email");
  const f_telefone = document.getElementById("edit-telefone");
  const f_cidade = document.getElementById("edit-cidade");
  const f_estado = document.getElementById("edit-estado");
  const f_cpf = document.getElementById("edit-cpf");
  const f_sexo = document.getElementById("edit-sexo");

  // ===== Função API =====
  async function api(url, opts = {}) {
    opts.credentials = "include";
    const r = await fetch(url, opts);
    return r.json();
  }

  // ===============================
  // Carregar usuários
  // ===============================
  async function carregarUsuarios() {
    const usuarios = await api("/api/usuarios");

    tbody.innerHTML = "";

    if (!usuarios.length) {
      tbody.innerHTML = `<tr><td colspan="10" class="empty">Nenhum usuário cadastrado.</td></tr>`;
      return;
    }

    usuarios.forEach((u, i) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td>${u.nome}</td>
        <td>${u.cpf || "-"}</td>
        <td>${u.sexo || "-"}</td>
        <td>${u.idade || "-"}</td>
        <td>${u.telefone || "-"}</td>
        <td>${u.cidade || "-"}</td>
        <td>${u.estado || "-"}</td>
        <td>${u.email}</td>
        <td>
          <button class="btn-editar" data-id="${u.id}" data-user='${JSON.stringify(u)}'>✏ Editar</button>
          <button class="btn-excluir" data-id="${u.id}" onclick="excluirUsuario(${u.id})">🗑 Excluir</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  // ===============================
  // Abrir Modal de Edição
  // ===============================
  window.abrirEdicao = async (id) => {
    const u = await api(`/api/usuarios/${id}`);

    f_id.value = u.id;
    f_nome.value = u.nome;
    f_email.value = u.email;
    f_telefone.value = u.telefone || "";
    f_cidade.value = u.cidade || "";
    f_estado.value = u.estado || "";
    f_cpf.value = u.cpf || "";
    f_sexo.value = u.sexo || "";

    modal.style.display = "block";
  };

  // Fechar modal
  cancel.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // ===============================
  // Salvar alterações
  // ===============================
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const usuario = {
      nome: f_nome.value,
      email: f_email.value,
      telefone: f_telefone.value,
      cidade: f_cidade.value,
      estado: f_estado.value,
      cpf: f_cpf.value,
      sexo: f_sexo.value
    };

    await api(`/api/usuarios/${f_id.value}`, {
      method: "PUT",
      body: JSON.stringify(usuario),
      headers: { "Content-Type": "application/json" }
    });

    modal.style.display = "none";
    carregarUsuarios();
  });

  // ===============================
  // Excluir usuário
  // ===============================
  window.excluirUsuario = async (id) => {
    if (!confirm("Deseja realmente excluir este usuário?")) return;

    await api(`/api/usuarios/${id}`, { method: "DELETE" });
    carregarUsuarios();
  };

  // Iniciar
  carregarUsuarios();
});
