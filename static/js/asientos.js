document.addEventListener('DOMContentLoaded', () => {
    const seatButtons = document.querySelectorAll('.seat-button');
    const modal = new bootstrap.Modal(document.getElementById('tipoPasajeroModal'));
    const modalAsientoNum = document.getElementById('modalAsientoNum');
    const selectTipoPasajero = document.getElementById('selectTipoPasajero');
    const btnGuardarTipo = document.getElementById('btnGuardarTipo');
    const hiddenInput = document.getElementById('asientos_seleccionados');

    let seleccionados = {};
    let asientoActualId = null;

    seatButtons.forEach(button => {
        button.addEventListener('click', () => {
            const asientoId = button.dataset.asientoId;
            const asientoNum = button.dataset.asientoNum;

            if (seleccionados[asientoId]) {
                delete seleccionados[asientoId];
                button.classList.remove('seleccionado');
            } else {
                asientoActualId = asientoId;
                modalAsientoNum.textContent = asientoNum;
                selectTipoPasajero.value = 'adulto';
                modal.show();
            }
        });
    });

    btnGuardarTipo.addEventListener('click', () => {
    if (asientoActualId) {
        const tipo = selectTipoPasajero.value;
        seleccionados[asientoActualId] = tipo;

        const button = document.querySelector(`.seat-button[data-asiento-id="${asientoActualId}"]`);
        button.classList.add('seleccionado');

        modal.hide();
        asientoActualId = null;

        const valorInput = Object.entries(seleccionados)
            .map(([id, tipo]) => `${id}:${tipo}`)
            .join(',');
        hiddenInput.value = valorInput;
    }
});

});