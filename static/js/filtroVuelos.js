// Configura fecha mínima en el filtro de búsqueda
    const fechaIdaFilter = document.getElementById('fecha_ida');
    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0');
    const day = today.getDate().toString().padStart(2, '0');
    const minDate = `${year}-${month}-${day}`;

    if (fechaIdaFilter) {
        fechaIdaFilter.min = minDate;
    }  