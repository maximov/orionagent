(function () {
  const qsApi = new URLSearchParams(location.search).get("api");
  const saved = localStorage.getItem("CORE_API_BASE");
  const defaultBase = `${location.protocol}//${location.host}`;
  const API_BASE = qsApi || saved || defaultBase;

  const $apiBase = document.getElementById("apiBase");
  const $apiLabel = document.getElementById("apiLabel");
  const $saveApi = document.getElementById("saveApi");
  const $messages = document.getElementById("messages");
  const $composer = document.getElementById("composer");
  const $prompt = document.getElementById("prompt");
  const $send = document.getElementById("send");

  $apiBase.value = API_BASE;
  $apiLabel.textContent = API_BASE;

  const userId = getOrCreateUserId();

  function getOrCreateUserId() {
    const key = "WEB_USER_ID";
    let id = localStorage.getItem(key);
    if (!id) {
      id = "web-" + Math.random().toString(36).slice(2, 10);
      localStorage.setItem(key, id);
    }
    return id;
  }

  function addMsg(role, text) {
    const el = document.createElement("div");
    el.className = `msg ${role}`;
    el.textContent = text;
    $messages.appendChild(el);
    $messages.scrollTop = $messages.scrollHeight;
  }

  async function sendToCore(text) {
    const payload = { channel: "web", user_id: userId, text };
    const url = `${$apiBase.value.replace(/\/+$/,'')}/v1/chat`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const t = await res.text();
      throw new Error(`${res.status} ${t}`);
    }
    return res.json();
  }

  $composer.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = ($prompt.value || "").trim();
    if (!text) return;
    addMsg("user", text);
    $prompt.value = "";
    $send.disabled = true;

    try {
      const data = await sendToCore(text);
      const parts = (data && data.parts) || [];
      if (!parts.length) addMsg("assistant", "Пустой ответ от Core API");
      parts.forEach((p) => addMsg("assistant", p));
    } catch (err) {
      addMsg("assistant", `Ошибка: ${err.message}`);
    } finally {
      $send.disabled = false;
      $prompt.focus();
    }
  });

  $saveApi.addEventListener("click", () => {
    const v = ($apiBase.value || "").trim();
    if (!v) return;
    localStorage.setItem("CORE_API_BASE", v);
    $apiLabel.textContent = v;
    addMsg("system", `API изменён: ${v}`);
  });
})();
