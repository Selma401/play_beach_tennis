// ==========================================================
// Excluir Torneio (Admin)
// ==========================================================
async function excluirTorneio(id) {
    if (!confirm("Tem certeza que deseja excluir este torneio?")) return;

    const res = await fetch(`/api/torneios/${id}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include"
    });

    const data = await res.json();
    alert(data.mensagem || data.erro || "Erro ao excluir torneio");

    // Recarrega a lista de torneios na tela, se existir
    if (typeof carregarTorneiosAdmin === "function") carregarTorneiosAdmin();
}

// ==========================================================
// Ver inscritos (Admin)
// ==========================================================
async function verInscritos(torneioId) {
    const res = await fetch(`/api/inscricoes/${torneioId}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        credentials: "include"
    });

    const data = await res.json();

    if (data.mensagem) {
        alert(data.mensagem);
        return;
    }

    let lista = `👥 INSCRITOS NO TORNEIO #${torneioId}\n\n`;
    data.forEach((i, idx) => {
        lista += `${idx + 1}. ${i.atleta} (${i.cidade}) — ${i.nivel}, ${i.forma_pagamento}\n`;
    });

    alert(lista);
}

async function verInscritos(torneioId) {
    const res = await fetch(`/api/torneios/${torneioId}/inscritos`, {
        credentials: "include"
    });
    const data = await res.json();

    if (data.erro) {
        alert("Erro: " + data.erro);
        return;
    }

    if (data.mensagem) {
        alert(data.mensagem);
        return;
    }

    let lista = "👥 INSCRITOS NO TORNEIO\n\n";
    data.forEach((i, idx) => {
        lista += `${idx + 1}. ${i.atleta} — ${i.cidade}\n`;
        lista += `   • Nível: ${i.nivel}\n`;
        lista += `   • Pagamento: ${i.forma_pagamento}\n`;
        lista += `   • Valor: R$ ${i.valor}\n`;
        lista += `   • Data: ${new Date(i.data_inscricao).toLocaleDateString()}\n\n`;
    });

    alert(lista);
}

// ==========================================================
// Renderização de Torneios (exemplo com botão Ver Inscritos)
// ==========================================================
function renderTorneioRow(t) {
    return `
        <tr>
            <td>${t.nome}</td>
            <td>${t.data_evento}</td>
            <td>${t.status}</td>
            <td>R$ ${t.preco || 0}</td>
            <td>${t.vagas}</td>
            <td>
                <button class="btn" onclick="verInscritos(${t.id})">👥 Ver inscritos</button>
                <button class="btn danger" onclick="excluirTorneio(${t.id})">🗑️ Excluir</button>
            </td>
        </tr>
    `;
}
