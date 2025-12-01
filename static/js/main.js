/* ================================================
   🎾 PLAY BEACH TENNIS - SCRIPT PRINCIPAL (v2)
   ================================================ */

console.log("🏖️ Play Beach Tennis — JS carregado com sucesso!");

// ------------------------------------------------
// ⚙️ LOADER GLOBAL (SPINNER)
// ------------------------------------------------
function createLoader() {
  const loader = document.createElement("div");
  loader.id = "global-loader";
  loader.innerHTML = `
    <div class="loader-backdrop"></div>
    <div class="loader-box">
      <div class="spinner"></div>
      <p>Carregando...</p>
    </div>
  `;
  document.body.appendChild(loader);
}

function showLoader() {
  const l = document.getElementById("global-loader");
  if (l) l.style.display = "flex";
}

function hideLoader() {
  const l = document.getElementById("global-loader");
  if (l) l.style.display = "none";
}

createLoader();

// ====================== LOGIN ======================
document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("loginForm");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("email").value.trim();
      const senha = document.getElementById("senha").value.trim();

      if (!email || !senha) {
        showToast("Preencha email e senha!", "error");
        return;
      }

      try {
        showLoader();

        const res = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email, senha })
        });

        const data = await res.json().catch(() => ({}));

        hideLoader();

        if (!res.ok || data.erro) {
          showToast(data.erro || "Usuário ou senha inválidos", "error");
          return;
        }

        showToast(data.mensagem || "Login realizado com sucesso!", "success");

        // Decide rota conforme backend te retorna
        if (data.is_admin) {
          window.location.href = "/torneios_admin";
        } else {
          window.location.href = "/dashboard";
        }

      } catch (err) {
        hideLoader();
        console.error("Erro no login:", err);
        showToast("Erro ao conectar ao servidor.", "error");
      }
    });
  }
});

// ------------------------------------------------
// 🔐 LOGOUT GLOBAL
// ------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const logoutBtn = document.getElementById("logoutBtn");

  if (logoutBtn) {
    logoutBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      if (!confirm("Deseja realmente sair do sistema?")) return;

      showLoader();
      try {
        const res = await fetch("/api/logout", {
          method: "POST",
          credentials: "include"
        });
        if (res.ok) {
          hideLoader();
          alert("Sessão encerrada. Até logo!");
          window.location.href = "/login";
        } else {
          hideLoader();
          alert("Não foi possível encerrar a sessão. Tente novamente.");
        }
      } catch (err) {
        hideLoader();
        console.error("Erro ao fazer logout:", err);
        alert("Erro ao conectar ao servidor.");
      }
    });
  }
});

// ------------------------------------------------
// 📡 FUNÇÃO GLOBAL PARA FETCH COM LOADER + ERROS
// ------------------------------------------------
async function apiFetch(url, opts = {}) {
  opts.headers = { "Content-Type": "application/json" };
  opts.credentials = "include";
  if (opts.body && typeof opts.body !== "string") opts.body = JSON.stringify(opts.body);

  showLoader();
  try {
    const res = await fetch(url, opts);
    const json = await res.json().catch(() => ({}));
    hideLoader();

    if (!res.ok) throw new Error(json.erro || `Erro ${res.status}`);
    return json;
  } catch (err) {
    hideLoader();
    console.error(`Erro ao acessar ${url}:`, err);
    showToast(`Erro: ${err.message}`, "error");
    return null;
  }
}

// ------------------------------------------------
// 🧭 MENU ATIVO AUTOMÁTICO
// ------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll("nav ul.menu li a");
  const current = window.location.pathname;

  links.forEach(link => {
    if (link.getAttribute("href") === current) {
      link.style.background = "#00a56d";
      link.style.color = "#fff";
      link.style.borderRadius = "8px";
    }
  });
});

// ------------------------------------------------
// 💬 ALERTAS SUAVES (TOASTS)
// ------------------------------------------------
function showToast(mensagem, tipo = "info") {
  const box = document.createElement("div");
  box.textContent = mensagem;
  box.className = `toast ${tipo}`;
  document.body.appendChild(box);

  setTimeout(() => {
    box.classList.add("show");
    setTimeout(() => {
      box.classList.remove("show");
      setTimeout(() => box.remove(), 300);
    }, 2500);
  }, 100);
}

// ------------------------------------------------
// 💅 ESTILOS DINÂMICOS
// ------------------------------------------------
const style = document.createElement("style");
style.textContent = `
.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #007b55;
  color: white;
  padding: 10px 16px;
  border-radius: 6px;
  opacity: 0;
  transform: translateY(20px);
  transition: 0.3s;
  z-index: 10000;
}
.toast.show {
  opacity: 1;
  transform: translateY(0);
}
.toast.error { background: #c0392b; }
.toast.success { background: #27ae60; }
.toast.info { background: #2980b9; }

/* === LOADER === */
#global-loader {
  display: none;
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  height: 100vh;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.loader-backdrop {
  position: absolute;
  top: 0; left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
}
.loader-box {
  z-index: 10000;
  text-align: center;
}
.spinner {
  border: 5px solid #ccc;
  border-top: 5px solid #007b55;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);

// ------------------------------
// 🔥 Controle de carregamento por página
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {

  // Dashboard do usuário → lista de torneios
  if (document.getElementById("listaTorneios")) {
    if (typeof carregarTorneios === "function") carregarTorneios();
  }

  // Dashboard do usuário → minhas inscrições
  if (document.getElementById("tabelaInscricoes")) {
    if (typeof carregarMinhasInscricoes === "function") carregarMinhasInscricoes();
  }

  // Admin → gerenciamento de torneios
  if (document.getElementById("tabelaTorneios")) {
    if (typeof carregarTorneiosAdmin === "function") carregarTorneiosAdmin();
  }

  // Admin → financeiro
  if (document.getElementById("totalInscricoes")) {
    if (typeof carregarFinanceiro === "function") carregarFinanceiro();
  }

  // Ranking
  if (document.getElementById("graficoRanking")) {
    if (typeof carregarRanking === "function") carregarRanking();
  }

  // Resultados
  if (document.getElementById("graficoCampeoes")) {
    if (typeof carregarRanking === "function") carregarRanking();
  }
});