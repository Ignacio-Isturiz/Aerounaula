document.addEventListener('DOMContentLoaded', function () {
    const vueloModal = new bootstrap.Modal(document.getElementById('vueloModal'));
    const formVuelo = document.getElementById('formVuelo');
    const modalTitle = document.getElementById('vueloModalLabel');

    // Referencias a los campos del modal
    const modalCodigo = document.getElementById('modal-codigo');
    const modalOrigen = document.getElementById('modal-origen');
    const modalOrigenCode = document.getElementById('modal-origen-code');
    const modalDestino = document.getElementById('modal-destino');
    const modalDestinoCode = document.getElementById('modal-destino-code');
    const modalAeronave = document.getElementById('modal-aeronave');
    const modalFechaSalida = document.getElementById('modal-fecha_salida');
    const modalFechaLlegada = document.getElementById('modal-fecha_llegada');
    const modalDuracion = document.getElementById('modal-duracion');
    const modalTipoVuelo = document.getElementById('modal-tipo_vuelo');
    const modalPrecio = document.getElementById('modal-precio');
    const modalEstado = document.getElementById('modal-estado');
    const modalImagenUrl = document.getElementById('modal-imagen_url');

    window.abrirModalCrear = function () {
        modalTitle.textContent = 'Crear Nuevo Vuelo';
        formVuelo.action = formVuelo.dataset.createUrl;
        formVuelo.reset();

        // Limpiar manualmente los campos
        modalCodigo.value = '';
        modalOrigen.value = '';
        modalOrigenCode.value = '';
        modalDestino.value = '';
        modalDestinoCode.value = '';
        modalAeronave.value = '';
        modalFechaSalida.value = '';
        modalFechaLlegada.value = '';
        modalDuracion.value = '';
        modalTipoVuelo.value = '';
        modalPrecio.value = '';
        modalEstado.value = '';
        modalImagenUrl.value = '';

        vueloModal.show();
    };

    window.abrirModalEditar = function (button) {
        modalTitle.textContent = 'Editar Vuelo';
        const vueloId = button.dataset.id;

        formVuelo.action = `/vuelos/editar/${vueloId}/`;

        modalCodigo.value = vueloId;
        modalOrigen.value = button.dataset.origen || '';
        modalOrigenCode.value = button.dataset.origenCode || '';
        modalDestino.value = button.dataset.destino || '';
        modalDestinoCode.value = button.dataset.destinoCode || '';
        modalAeronave.value = button.dataset.aeronave || '';
        modalFechaSalida.value = button.dataset.fecha ? button.dataset.fecha.substring(0, 16) : '';
        modalFechaLlegada.value = button.dataset.fechaLlegada ? button.dataset.fechaLlegada.substring(0, 16) : '';
        modalDuracion.value = button.dataset.duracion || '';
        modalTipoVuelo.value = button.dataset.tipoVuelo || '';
        modalPrecio.value = button.dataset.precio || '';
        modalEstado.value = button.dataset.estado || '';
        modalImagenUrl.value = button.dataset.imagen || '';

        vueloModal.show();
    };  
});
