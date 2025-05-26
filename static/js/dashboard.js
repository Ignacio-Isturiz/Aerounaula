document.addEventListener("DOMContentLoaded", function () {
  const boton = document.getElementById("chatbot-button");
  const modal = document.getElementById("chatbot-modal");

  boton.addEventListener("click", () => {
    modal.style.display = modal.style.display === "none" || modal.style.display === "" ? "block" : "none";
  });
});