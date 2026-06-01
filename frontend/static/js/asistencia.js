

//----------------Funciones relacionadas con las ventanas modal-----------------------------

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

    document.getElementById('btnCrearClase').style.display = 'inline-block';
    document.getElementById('btnEnviarQR').style.display = 'none';
    document.getElementById('btnEscanearQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Curso";
    document.getElementById('selectCurso').style.display = 'inline-block';
    document.getElementById('selectAsistencia').style.display = 'none';



    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 2: Enviar qr
// ==========================================
function abrirModalEnviarQR() {
    // 1. Cargar los datos de la fila seleccionada
    // 2. Textos de visualización
    document.getElementById('modalTitle').innerText = "Enviar QR";
    document.getElementById('modalSubtitle').innerText = "Enviar qr de asistencia a la clase seleccionada";

    document.getElementById('btnEnviarQR').style.display = 'inline-block';
    document.getElementById('btnCrearClase').style.display = 'none';
    document.getElementById('btnEscanearQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Clases";
    document.getElementById('selectAsistencia').style.display = 'inline-block';
    document.getElementById('selectCurso').style.display = 'none';


    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 2: Enviar qr
// ==========================================
function abrirModalEscanearQR() {
    // 1. Cargar los datos de la fila seleccionada
    // 2. Textos de visualización
    document.getElementById('modalTitle').innerText = "Escanear QR";
    document.getElementById('modalSubtitle').innerText = "Escanear qr de asistencia de la clase seleccionada";

    // 4. Mostrar botones correspondientes (Editar y Cancelar/Cerrar
    document.getElementById('btnEscanearQR').style.display = 'inline-block';
    document.getElementById('btnCrearClase').style.display = 'none';
    document.getElementById('btnEnviarQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Clases";
    document.getElementById('selectAsistencia').style.display = 'inline-block';
    document.getElementById('selectCurso').style.display = 'none';


    // 5. Abrir Modal
    abrirModal('modalClase');
}