document.addEventListener("DOMContentLoaded", function () {
  const chatBody = document.getElementById("chat-body");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("mensaje-input");

  function scrollToBottom() {
    chatBody.scrollTop = chatBody.scrollHeight;
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const mensaje = input.value.trim();
    if (!mensaje) return;

    // Mostrar mensaje del usuario
    const userBubble = document.createElement("div");
    userBubble.className = "bubble user";
    userBubble.textContent = mensaje;
    chatBody.appendChild(userBubble);

    // Mostrar escribiendo...
    const typingBubble = document.createElement("div");
    typingBubble.className = "bubble bot";
    typingBubble.id = "typing-indicator";
    typingBubble.innerHTML = `<span class="dot"></span><span class="dot"></span><span class="dot"></span>`;
    chatBody.appendChild(typingBubble);
    scrollToBottom();

    // Enviar mensaje al backend
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch(window.location.href, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams({ mensaje })
    })
    .then(res => res.text())
    .then(html => {
      // Parsear nueva respuesta
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const nuevaBurbuja = doc.querySelector(".bubble.bot.fade-hidden");

      // Eliminar "escribiendo..."
      typingBubble.remove();

      // Mostrar respuesta con animación
      if (nuevaBurbuja) {
        nuevaBurbuja.classList.remove("fade-hidden");
        nuevaBurbuja.classList.add("fade-in");
        chatBody.appendChild(nuevaBurbuja);

        // Sonido de respuesta
        const audio = new Audio("/static/sound/pop.mp3");
        audio.play();
      }

      scrollToBottom();
      input.value = "";
    });
  });

  scrollToBottom();
});
