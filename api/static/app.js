(function () {
  const $apiBase = document.getElementById("apiBase");
  const $apiLabel = document.getElementById("apiLabel");
  const $saveApi = document.getElementById("saveApi");
  const $messages = document.getElementById("messages");
  const $composer = document.getElementById("composer");
  const $prompt = document.getElementById("prompt");
  const $send = document.getElementById("send");

  const qsApi = new URLSearchParams(location.search).get("api");
  const saved = localStorage.getItem("CORE_API_BASE");
  const defaultBase = `${location.protocol}//${location.host}`;
  const apiBase = qsApi || saved || defaultBase;

  $apiBase.value = apiBase;
  $apiLabel.textContent = apiBase;

  const userId = ensureUserId();

  function ensureUserId() {
    const key = "WEB_USER_ID";
    let v = localStorage.getItem(key);
    if (!v) {
      v = "web-" + Math.random().toString(36).slice(2, 10);
      localStorage.setItem(key, v);
    }
    return v;
  }

  function addMsg(role, text) {
    const el = document.createElement("div");
    el.className = `msg ${role}`;
    el.textContent = text;
    $messages.appendChild(el);
    $messages.scrollTop = $messages.scrollHeight;
  }

  async function sendToCore(text) {
    const url = `${$apiBase.value.replace(/\/+$/,'')}/v1/chat`;
    const payload = { channel: "web", user_id: userId, text };
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`${res.status} ${await res.text()}`);
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
      const { parts } = await sendToCore(text);
      if (!parts || !parts.length) addMsg("assistant", "Пустой ответ от Core API");
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
