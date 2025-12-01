document.addEventListener("DOMContentLoaded", async () => {

  const tabela = document.querySelector("#rankingTabela tbody");
  const pesquisa = document.getElementById("pesquisaJogador");
  const grafico = document.getElementById("graficoRanking");
  let dados = [];
  let chart;

  async function carregarRanking() {
    const res = await fetch("/api/ranking", { credentials: "include" });
    dados = await res.json();
    atualizarTabela(dados);
    atualizarGrafico(dados);
  }

  function medalha(i) {
    return i === 1 ? "🥇" : i === 2 ? "🥈" : i === 3 ? "🥉" : i;
  }

  function atualizarTabela(lista) {
    tabela.innerHTML = "";

    if (!lista.length) {
      tabela.innerHTML = `<tr><td colspan="4" class="empty">Nenhum jogador no ranking ainda.</td></tr>`;
      return;
    }

    lista
      .sort((a, b) => b.pontos - a.pontos)
      .forEach((j, i) => {
        tabela.innerHTML += `
          <tr>
            <td>${medalha(i + 1)}</td>
            <td>${j.nome}</td>
            <td>${j.vitorias}</td>
            <td style="font-weight:bold;color:#0E7C66;">${j.pontos}</td>
          </tr>
        `;
      });
  }

  function atualizarGrafico(lista) {
    if (chart) chart.destroy();
    const ctx = grafico.getContext("2d");

    const top = [...lista].sort((a, b) => b.pontos - a.pontos).slice(0, 6);

    chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: top.map(p => p.nome),
        datasets: [{
          label: "Pontuação",
          data: top.map(p => p.pontos),
          backgroundColor: "#0E7C66"
        }]
      },
      options: {
        plugins: { legend: { display: false } },
        responsive: true,
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  pesquisa.addEventListener("input", () => {
    const termo = pesquisa.value.toLowerCase();
    const filtrado = dados.filter(j => j.nome.toLowerCase().includes(termo));
    atualizarTabela(filtrado);
    atualizarGrafico(filtrado);
  });

  carregarRanking();
});
