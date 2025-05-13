function setMinFechaSalida() {
  const ahora = new Date();
  ahora.setSeconds(0);
  const iso = ahora.toISOString().slice(0, 16);
  document.getElementById("fecha_salida").min = iso;
}

function abrirModalCrear() {
  const form = document.getElementById("formVuelo");
  form.action = form.dataset.createUrl;
  document.getElementById("vueloModalLabel").innerText = "Crear Vuelo";
  form.reset();
  setMinFechaSalida();
  new bootstrap.Modal(document.getElementById('vueloModal')).show();
}

function abrirModalEditar(button) {
  const form = document.getElementById("formVuelo");
  form.action = `/vuelos/editar/${button.dataset.id}/`;
  document.getElementById("vueloModalLabel").innerText = "Editar Vuelo";
  document.getElementById("id_vuelo").value = button.dataset.id;
  document.getElementById("origen").value = button.dataset.origen;
  document.getElementById("destino").value = button.dataset.destino;
  document.getElementById("fecha_salida").value = button.dataset.fecha;
  document.getElementById("precio").value = button.dataset.precio;
  document.getElementById("estado").value = button.dataset.estado;
  document.getElementById("imagen_url").value = button.dataset.imagen;
  setMinFechaSalida();
  new bootstrap.Modal(document.getElementById('vueloModal')).show();
}

document.addEventListener('DOMContentLoaded', () => {
  const fechaInput = document.getElementById('fecha_salida');
  if (fechaInput) {
    const ahora = new Date();
    ahora.setSeconds(0, 0);
    const minFecha = ahora.toISOString().slice(0, 16);
    fechaInput.min = minFecha;
  }
});
