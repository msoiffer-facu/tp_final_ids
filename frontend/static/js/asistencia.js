function abrirModal(id) {
    const modal = document.getElementById(id);

    modal.classList.add('modal--open');
    modal.setAttribute('aria-hidden', 'false');
}

function cerrarModal(id) {
    const modal = document.getElementById(id);

    modal.classList.remove('modal--open');
    modal.setAttribute('aria-hidden', 'true');
}

// function abrirModalAgregar()  { abrirModal('modalAgregar'); }
// function cerrarModalAgregar() { cerrarModal('modalAgregar'); }
function cerrarModalClase(){ cerrarModal('modalClase');}

// Cerrar modales al hacer click fuera o con ESC
window.addEventListener('click', function (event) {
    document.querySelectorAll('.modal--open').forEach(m => {
        if (event.target === m) cerrarModal(m.id);
    });
});

window.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal--open').forEach(m => cerrarModal(m.id));
    }
});

function abrirModalCrear() {
    // 1. Limpiar datos previos
    document.getElementById('formClasePresencial').reset();
    document.getElementById('claseId').value = "";

    // 2. Textos comerciales de creación
    document.getElementById('modalTitle').innerText = "Agregar clase presencial";
    document.getElementById('modalSubtitle').innerText = "Registra una nueva clase presencial y su horario";

    // 3. Habilitar inputs para poder escribir
    document.getElementById('curso').disabled = false;
    document.getElementById('fecha').disabled = false;

    // 4. Mostrar solo botones de creación
    document.getElementById('btnHabilitarEdicion').style.display = 'none';
    document.getElementById('btnCancelar').style.display = 'inline-block';
    document.getElementById('btnGuardarCambios').style.display = 'none';
    document.getElementById('btnCrearClase').style.display = 'inline-block';

    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 2: ABRIR PARA VER DETALLES (Campos llenos y bloqueados)
// ==========================================
function verRegistro(id, cursoNombre, fechaHoraCruda) {
    // 1. Cargar los datos de la fila seleccionada
    document.getElementById('claseId').value = id;
    document.getElementById('curso').value = cursoNombre;
    try {
        // 1. Separamos la fecha de la hora por el espacio
        // ['15/05/26', '15:35']
        const partes = fechaHoraCruda.split(' '); 
        const fechaParte = partes[0]; // '15/05/26'
        const horaParte = partes[1];  // '15:35'

        // 2. Separamos día, mes y año por las barras
        // ['15', '05', '26']
        const componentesFecha = fechaParte.split('/');
        const dia = componentesFecha[0];
        const mes = componentesFecha[1];
        const anioCorto = componentesFecha[2];

        // 3. Convertimos el año de 2 dígitos a 4 (ej: '26' -> '2026')
        const anioCompleto = "20" + anioCorto; 

        // 4. Armamos el rompecabezas en formato ISO: YYYY-MM-DDTHH:mm
        const fechaFormateada = `${anioCompleto}-${mes}-${dia}T${horaParte}`;

        // 5. Lo inyectamos en el input
        document.getElementById('fecha').value = fechaFormateada;

    } catch (error) {
        console.error("Error al procesar el formato de fecha:", error);
        // Si algo falla, dejamos el input vacío para que no rompa el código
        document.getElementById('fecha').value = "";
    }

    // 2. Textos de visualización
    document.getElementById('modalTitle').innerText = "Detalles de la clase";
    document.getElementById('modalSubtitle').innerText = "Información de la clase presencial seleccionada";

    // 3. Bloquear inputs (Solo lectura)
    document.getElementById('curso').disabled = true;
    document.getElementById('fecha').disabled = true;

    // 4. Mostrar botones correspondientes (Editar y Cancelar/Cerrar)
    document.getElementById('btnHabilitarEdicion').style.display = 'inline-block';
    document.getElementById('btnCancelar').style.display = 'none';
    document.getElementById('btnGuardarCambios').style.display = 'none';
    document.getElementById('btnCrearClase').style.display = 'none';

    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 3: CAMBIAR A MODO EDICIÓN (Dentro del modal)
// ==========================================
function activarModoEdicion() {
    // 1. Cambiar textos a edición
    document.getElementById('modalTitle').innerText = "Editar clase presencial";
    document.getElementById('modalSubtitle').innerText = "Modifica los campos necesarios y guarda los cambios";

    // 2. Desbloquear campos para permitir edición
    document.getElementById('curso').disabled = false;
    document.getElementById('fecha').disabled = false;

    // 3. Swapear botones a "Guardar Cambios"
    document.getElementById('btnHabilitarEdicion').style.display = 'none';
    document.getElementById('btnCancelar').style.display = 'inline-block';
    document.getElementById('btnGuardarCambios').style.display = 'inline-block';
    document.getElementById('btnCrearClase').style.display = 'none';
}