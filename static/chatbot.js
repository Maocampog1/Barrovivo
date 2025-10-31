// static/chatbot.js
function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text) n.textContent = text;
  return n;
}
function pushMsg(container, text, who="bot") {
  const div = el("div", `bv-msg bv-msg-${who}`);
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}
async function callChatAPI(message) {
  const r = await fetch("/api/chat/", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message})
  });
  return await r.json();
}
(function initBVChat() {
  const box = document.getElementById("bv-chat-box");
  const toggle = document.getElementById("bv-chat-toggle");
  const msgs = document.getElementById("bv-chat-messages");
  const form = document.getElementById("bv-chat-form");
  const input = document.getElementById("bv-chat-input");

  toggle.addEventListener("click", () => {
    box.hidden = !box.hidden;
    if (!box.hidden && msgs.childElementCount === 0) {
      pushMsg(msgs, "¡Bienvenido! Estoy aquí para ayudarte a encontrar la pieza de cerámica perfecta. Cuéntame qué buscas (ej: “matera amarilla para regalo”).", "bot");
    }
    if (!box.hidden) input.focus();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = (input.value || "").trim();
    if (!text) return;
    pushMsg(msgs, text, "user");
    input.value = "";
    pushMsg(msgs, "Estoy pensando…", "bot");
    const loader = msgs.lastChild;

    try {
      const data = await callChatAPI(text);
      msgs.removeChild(loader);
      if (!data.ok) { pushMsg(msgs, "No pude conectarme ahora. Intenta de nuevo.", "bot"); return; }
      pushMsg(msgs, data.text || "Listo.", "bot");

      if (Array.isArray(data.products) && data.products.length) {
        const ul = el("ul", "list-unstyled");
        data.products.forEach(p => {
          const li = el("li");
          const a = el("a");
          a.href = `/producto/${p.id}/`; // ajusta a tu URL real de detalle
          a.textContent = `${p.nombre} — $${Math.round(p.precio).toLocaleString()}`;
          li.appendChild(a);
          ul.appendChild(li);
        });
        const wrap = el("div", "bv-msg bv-msg-bot");
        wrap.appendChild(ul);
        msgs.appendChild(wrap);
        msgs.scrollTop = msgs.scrollHeight;
      } else {
        pushMsg(msgs, "No encontré coincidencias exactas. ¿Quieres probar otro color o tipo?", "bot");
      }
    } catch (err) {
      msgs.removeChild(loader);
      pushMsg(msgs, "Ocurrió un error. ¿Intentamos otra vez?", "bot");
    }
  });

  // Saludo automático al cargar
  setTimeout(() => {
    box.hidden = false;
    pushMsg(msgs, "¡Bienvenido! Estoy aquí para ayudarte a encontrar la pieza de cerámica perfecta. Cuéntame qué buscas.", "bot");
  }, 600);
})();
