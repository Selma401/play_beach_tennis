// ==========================================================
// static/js/partidas.js
// Lógica da tela de Gerenciamento de Partidas
// ==========================================================

// Usa apiFetch global se existir (main.js), senão faz um fetch simples
async function api(path, opts = {}) {
  if (typeof apiFetch === "function") {
    return await apiFetch(path, opts);
  }
  opts.headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
  opts.credentials = "include";
  if (opts.body && typeof opts.body !== "string") {
    opts.body = JSON.stringify(opts.body);
  }
  const res = await fetch(path, opts);
  try { return await res.json(); } catch { return {}; }
}

document.addEventListener("DOMContentLoaded", async () => {
  // -----------------------------
  // ELEMENTOS PRINCIPAIS
  // -----------------------------
  const selTorneioGerar   = document.getElementById("selTorneioParaGerar");
  const selTorneioLista   = document.getElementById("selTorneioLista");
  const tipoPartidaSelect = document.getElementById("tipo");

  const formPartidaManual = document.getElementById("formPartidaManual");
  const btnNovoManual     = document.getElementById("btnNovoManual");
  const btnGerarAuto      = document.getElementById("gerarAuto");

  const jogador1  = document.getElementById("jogador1");
  const jogador1b = document.getElementById("jogador1b");
  const jogador2  = document.getElementById("jogador2");
  const jogador2b = document.getElementById("jogador2b");
  const quadra    = document.getElementById("quadra");
  const horario   = document.getElementById("horario");
  const tabelaBody = document.querySelector("#tabelaPartidas tbody");

  // Reservas
  const filtroReservaTorneio = document.getElementById("res_torneio_filter");
  const btnCarregarReservas  = document.getElementById("btn_carregar_res");
  const reservasBody         = document.querySelector("#tbl_reservas tbody");

  // Modal de resultado
  const modalResultado = document.getElementById("modalResultado");
  const resPartidaId   = document.getElementById("res_partida_id");
  const set1Input      = document.getElementById("set1");
  const set2Input      = document.getElementById("set2");
  const set3Input      = document.getElementById("set3");
  const resVencedor    = document.getElementById("res_vencedor");
  const btnSalvarResultado = document.getElementById("btnSalvarResultado");
  const btnFecharResultado = document.getElementById("btnFecharResultado");

  // Tabs
  const tabButtons   = document.querySelectorAll(".tab-btn");
  const tabPartidas  = document.getElementById("tab-partidas");
  const tabReservas  = document.getElementById("tab-reservas");

  // -----------------------------
  // CARREGAR TORNEIOS
  // -----------------------------
  async function carregarTorneios() {
    // usa /api/torneios/abertos para focar nos torneios em andamento/abertos
    const torneios = await api("/api/torneios/abertos") || [];
    const selects = [selTorneioGerar, selTorneioLista, filtroReservaTorneio];

    selects.forEach(sel => {
      if (!sel) return;
      const label = sel === filtroReservaTorneio ? "Todos" : "Selecione torneio";
      sel.innerHTML = `<option value="">${label}</option>`;

      if (!Array.isArray(torneios) || !torneios.length) return;

      torneios.forEach(t => {
        const opt = document.createElement("option");
        opt.value = t.id;
        // se vier status na API, mostra; se não, só o nome
        opt.textContent = t.status ? `${t.nome} (${t.status})` : t.nome;
        sel.appendChild(opt);
      });
    });
  }

  // -----------------------------
  // CARREGAR JOGADORES PARA FORM MANUAL
  // -----------------------------
  async function carregarJogadores() {
    const usuarios = await api("/api/usuarios") || [];
    const selects = [jogador1, jogador1b, jogador2, jogador2b];

    selects.forEach(sel => {
      if (!sel) return;
      sel.innerHTML = `<option value="">Selecione...</option>`;

      if (!Array.isArray(usuarios) || !usuarios.length) return;

      usuarios.forEach(u => {
        const opt = document.createElement("option");
        opt.value = u.id;
        opt.textContent = u.sexo ? `${u.nome} (${u.sexo})` : u.nome;
        sel.appendChild(opt);
      });
    });
  }

  // -----------------------------
  // BOTÃO "CRIAR MANUAL"
  // -----------------------------
  if (btnNovoManual && formPartidaManual) {
    btnNovoManual.addEventListener("click", async () => {
      const visivel = formPartidaManual.style.display === "block";
      formPartidaManual.style.display = visivel ? "none" : "block";
      if (!visivel) {
        await carregarJogadores();
      }
    });
  }

  // -----------------------------
  // SALVAR PARTIDA MANUAL
  // -----------------------------
  if (formPartidaManual) {
    formPartidaManual.addEventListener("submit", async (e) => {
      e.preventDefault();

      const torneioId = selTorneioGerar.value;
      if (!torneioId) {
        alert("Selecione um torneio para criar a partida.");
        return;
      }

      const tipo = tipoPartidaSelect.value;
      const data = {
        torneio_id: torneioId,
        tipo_partida: tipo,
        jogador1_id: jogador1.value || null,
        jogador1b_id: jogador1b.value || null,
        jogador2_id: jogador2.value || null,
        jogador2b_id: jogador2b.value || null,
        quadra: (quadra.value || "").trim(),
        horario: (horario.value || "").trim()
      };

      if (!data.jogador1_id || !data.jogador2_id || !data.quadra || !data.horario) {
        alert("Preencha Jogador 1, Jogador 2, Quadra e Horário.");
        return;
      }

      const res = await api("/api/partidas/manual", {
        method: "POST",
        body: data
      });

      alert(res.mensagem || res.erro || "Erro ao salvar partida.");

      if (res && res.mensagem) {
        formPartidaManual.reset();
        formPartidaManual.style.display = "none";
        selTorneioLista.value = torneioId;
        await carregarPartidas();
      }
    });
  }

  // -----------------------------
  // GERAR PARTIDAS AUTOMÁTICAS
  // -----------------------------
  if (btnGerarAuto) {
    btnGerarAuto.addEventListener("click", async () => {
      const torneioId = selTorneioGerar.value;
      const tipo = tipoPartidaSelect.value;

      if (!torneioId) {
        alert("Selecione um torneio para gerar partidas.");
        return;
      }

      if (!confirm("Deseja gerar partidas automaticamente para o torneio selecionado?")) return;

      const res = await api("/api/partidas/auto", {
        method: "POST",
        body: { torneio_id: torneioId, tipo_partida: tipo }
      });

      alert(res.mensagem || res.erro || "Erro ao gerar partidas.");

      if (res && res.mensagem) {
        selTorneioLista.value = torneioId;
        await carregarPartidas();
      }
    });
  }

  // -----------------------------
  // CARREGAR PARTIDAS DO TORNEIO
  // -----------------------------
  async function carregarPartidas() {
    const torneioId = selTorneioLista.value;
    tabelaBody.innerHTML = "";

    if (!torneioId) {
      tabelaBody.innerHTML = `<tr><td colspan="8">Selecione um torneio para ver as partidas.</td></tr>`;
      return;
    }

    const partidas = await api(`/api/partidas/${torneioId}`) || [];

    if (!Array.isArray(partidas) || !partidas.length || partidas.erro) {
      tabelaBody.innerHTML = `<tr><td colspan="8">Nenhuma partida encontrada.</td></tr>`;
      return;
    }

    partidas.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td>${p.torneio_nome || "-"}</td>
        <td>${(p.tipo_partida || "").replaceAll("_", " ")}</td>
        <td>
          ${(p.jogador1 || "-")}${p.jogador1b ? " / " + p.jogador1b : ""} 
          VS 
          ${(p.jogador2 || "-")}${p.jogador2b ? " / " + p.jogador2b : ""}
        </td>
        <td>${p.placar || "-"}</td>
        <td>
          <input 
            type="text" 
            class="input-edit campo-quadra" 
            value="${p.quadra || ""}" 
          />
        </td>
        <td>
          <input 
            type="time" 
            class="input-edit campo-horario" 
            value="${p.horario && p.horario !== "-" ? p.horario : ""}" 
          />
        </td>
        <td>
          <button 
            class="btn icon save-logistica" 
            data-acao="salvar-log" 
            data-id="${p.id}">
            💾
          </button>

          <button 
            class="btn icon primary" 
            data-acao="abrir-resultado"
            data-id="${p.id}"
            data-tipo="${p.tipo_partida || ""}"
            data-j1="${p.jogador1 || ""}"
            data-j1b="${p.jogador1b || ""}"
            data-j2="${p.jogador2 || ""}"
            data-j2b="${p.jogador2b || ""}"
            data-j1id="${p.jogador1_id || ""}"
            data-j2id="${p.jogador2_id || ""}"
            data-placar="${p.placar || ""}">
            🏆
          </button>

          <button 
            class="btn icon danger" 
            data-acao="excluir" 
            data-id="${p.id}">
            🗑️
          </button>
        </td>
      `;
      tabelaBody.appendChild(tr);
    });
  }

  // Quando mudar torneio na lista, recarrega partidas
  if (selTorneioLista) {
    selTorneioLista.addEventListener("change", carregarPartidas);
  }

  // -----------------------------
  // EVENTOS DOS BOTÕES DA TABELA (delegação)
  // -----------------------------
  if (tabelaBody) {
    tabelaBody.addEventListener("click", async (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;

      const acao = btn.dataset.acao;
      const id   = btn.dataset.id;
      if (!id) return;

      const linha = btn.closest("tr");

      // Salvar quadra/horário
      if (acao === "salvar-log") {
        const quadraInput  = linha.querySelector(".campo-quadra");
        const horarioInput = linha.querySelector(".campo-horario");

        const data = {
          quadra: (quadraInput.value || "").trim(),
          horario: (horarioInput.value || "").trim()
        };

        const res = await api(`/api/partidas/${id}`, {
          method: "PUT",
          body: data
        });

        alert(res.mensagem || res.erro || "Erro ao salvar logística.");
        return;
      }

      // Excluir partida
      if (acao === "excluir") {
        if (!confirm("Deseja realmente excluir esta partida?")) return;
        const res = await api(`/api/partidas/${id}`, { method: "DELETE" });
        alert(res.mensagem || res.erro || "Erro ao excluir partida.");
        await carregarPartidas();
        return;
      }

      // Abrir modal de resultado
      if (acao === "abrir-resultado") {
        abrirModalResultado(btn.dataset);
      }
    });
  }

  // -----------------------------
  // MODAL DE RESULTADO
  // -----------------------------
  function abrirModalResultado(data) {
    if (!modalResultado) return;

    console.log("DATA MODAL:", data);

    modalResultado.style.display = "flex";

    resPartidaId.value = data.id || "";
    // limpa sets sempre que abrir
    set1Input.value = "";
    set2Input.value = "";
    set3Input.value = "";

    // popular select de vencedor
    resVencedor.innerHTML = `<option value="">Selecione vencedor</option>`;

    const tipo = data.tipo || "";
    const j1id = data.j1id || "";
    const j2id = data.j2id || "";
    const j1   = data.j1   || "";
    const j1b  = data.j1b  || "";
    const j2   = data.j2   || "";
    const j2b  = data.j2b  || "";

    if (tipo.startsWith("dupla")) {
      // Duplas: exibe "A / B" e "C / D"
      const nome1 = j1b ? `${j1} / ${j1b}` : j1;
      const nome2 = j2b ? `${j2} / ${j2b}` : j2;

      if (j1id) resVencedor.innerHTML += `<option value="${j1id}">${nome1}</option>`;
      if (j2id) resVencedor.innerHTML += `<option value="${j2id}">${nome2}</option>`;
    } else {
      // Individual
      if (j1id) resVencedor.innerHTML += `<option value="${j1id}">${j1}</option>`;
      if (j2id) resVencedor.innerHTML += `<option value="${j2id}">${j2}</option>`;
    }
  }

  if (btnFecharResultado && modalResultado) {
    btnFecharResultado.addEventListener("click", () => {
      modalResultado.style.display = "none";
      resPartidaId.value = "";
      set1Input.value = "";
      set2Input.value = "";
      set3Input.value = "";
      resVencedor.innerHTML = "";
    });
  }

  if (btnSalvarResultado) {
    btnSalvarResultado.addEventListener("click", async () => {
      const id         = resPartidaId.value;
      const vencedorId = resVencedor.value;
      const s1 = (set1Input.value || "").trim();
      const s2 = (set2Input.value || "").trim();
      const s3 = (set3Input.value || "").trim();

      if (!id) {
        alert("Partida inválida.");
        return;
      }
      if (!vencedorId || !s1) {
        alert("Informe pelo menos o Set 1 e selecione o vencedor.");
        return;
      }

      const placar = [s1, s2, s3].filter(x => x).join(" | ");

      const res = await api(`/api/partidas/${id}/resultado`, {
        method: "PUT",
        body: { vencedor_id: vencedorId, placar }
      });

      alert(res.mensagem || res.erro || "Erro ao salvar resultado.");

      if (res && res.mensagem) {
        modalResultado.style.display = "none";
        await carregarPartidas();
      }
    });
  }

  // -----------------------------
  // RESERVAS DE QUADRA
  // -----------------------------
  async function carregarReservas() {
    const torneioId = filtroReservaTorneio.value;
    const url = torneioId ? `/api/reservas?torneio_id=${torneioId}` : `/api/reservas`;
    const dados = await api(url) || [];

    reservasBody.innerHTML = "";

    if (!Array.isArray(dados) || !dados.length || dados.erro) {
      reservasBody.innerHTML = `<tr><td colspan="6">Nenhuma reserva encontrada.</td></tr>`;
      return;
    }

    dados.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.id}</td>
        <td>${r.torneio_nome || r.torneio_id || "-"}</td>
        <td>${r.quadra}</td>
        <td>${r.horario || "-"}</td>
        <td>${r.reservado ? "Sim" : "Não"}</td>
        <td>
          ${r.reservado ? "" : `<button class="btn-editar" data-acao="reservar" data-id="${r.id}">Reservar</button>`}
          <button class="btn-excluir" data-acao="excluir-reserva" data-id="${r.id}">Excluir</button>
        </td>
      `;
      reservasBody.appendChild(tr);
    });
  }

  if (btnCarregarReservas) {
    btnCarregarReservas.addEventListener("click", carregarReservas);
  }

  if (reservasBody) {
    reservasBody.addEventListener("click", async (e) => {
      const btn = e.target.closest("button");
      if (!btn) return;
      const id   = btn.dataset.id;
      const acao = btn.dataset.acao;

      if (acao === "reservar") {
        const res = await api(`/api/reservas/${id}/toggle`, { method: "POST" });
        alert(res.mensagem || res.erro || "Erro ao reservar.");
        await carregarReservas();
      }

      if (acao === "excluir-reserva") {
        if (!confirm("Excluir reserva?")) return;
        const res = await api(`/api/reservas/${id}`, { method: "DELETE" });
        alert(res.mensagem || res.erro || "Erro ao excluir reserva.");
        await carregarReservas();
      }
    });
  }

  // -----------------------------
  // SISTEMA DE TABS (Partidas / Reservas)
  // -----------------------------
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const alvo = btn.dataset.tab;
      if (alvo === "reservas") {
        tabPartidas.style.display = "block"; // se quiser esconder, mude para "none"
        tabReservas.style.display = "block";
        carregarReservas();
      } else {
        tabPartidas.style.display = "block";
        tabReservas.style.display = "none";
      }
    });
  });

  // -----------------------------
  // INICIALIZAÇÃO
  // -----------------------------
  await carregarTorneios();
  // não chama carregarPartidas direto porque ainda não tem torneio selecionado
});
