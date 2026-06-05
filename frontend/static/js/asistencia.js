

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

    document.getElementById('formClasePresencial').reset();
    document.getElementById('claseId').value = "";

    document.getElementById('btnCrearClase').style.display = 'inline-block';
    document.getElementById('btnEnviarQR').style.display = 'none';
    document.getElementById('btnEscanearQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Curso";
    document.getElementById('selectCurso').style.display = 'inline-block';
    document.getElementById('selectEscanear').style.display = 'none';
    document.getElementById('selectAsistencia').style.display = 'none';

    document.getElementById('formClasePresencial').action = '/asistencia';
    document.getElementById('formClasePresencial').target = '';

    document.getElementById('selectCurso').required = true;
    document.getElementById('selectAsistencia').required = false;
    document.getElementById('selectEscanear').required = false;





    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 2: Enviar qr
// ==========================================
function abrirModalEnviarQR() {

    document.getElementById('modalTitle').innerText = "Enviar QR";
    document.getElementById('modalSubtitle').innerText = "Enviar qr de asistencia a la clase seleccionada";

    document.getElementById('btnEnviarQR').style.display = 'inline-block';
    document.getElementById('btnCrearClase').style.display = 'none';
    document.getElementById('btnEscanearQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Clases";
    document.getElementById('selectAsistencia').style.display = 'inline-block';
    document.getElementById('selectEscanear').style.display = 'none';
    document.getElementById('selectCurso').style.display = 'none';

    document.getElementById('formClasePresencial').action = '/asistencia/pedir-asistencia';
    document.getElementById('formClasePresencial').target = '';

    document.getElementById('selectAsistencia').required = true;
    document.getElementById('selectCurso').required = false;
    document.getElementById('selectEscanear').required = false;



    // 5. Abrir Modal
    abrirModal('modalClase');
}

// ==========================================
// ESTADO 2: Enviar qr
// ==========================================
function abrirModalEscanearQR() {

    document.getElementById('modalTitle').innerText = "Escanear QR";
    document.getElementById('modalSubtitle').innerText = "Escanear qr de asistencia de la clase seleccionada";

    document.getElementById('btnEscanearQR').style.display = 'inline-block';
    document.getElementById('btnCrearClase').style.display = 'none';
    document.getElementById('btnEnviarQR').style.display = 'none';

    document.getElementById('text-select').innerText = "Clases";
    document.getElementById('selectAsistencia').style.display = 'none';
    document.getElementById('selectEscanear').style.display = 'inline-block';
    document.getElementById('selectCurso').style.display = 'none';


    document.getElementById('formClasePresencial').action = '/asistencia/verificar-asistencia';
    document.getElementById('formClasePresencial').target = 'qr-form-target';

    document.getElementById('selectEscanear').required = true;
    document.getElementById('selectCurso').required = false;
    document.getElementById('selectAsistencia').required = false;



    abrirModal('modalClase');
}

// Filtrar por curso en la URL
document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.querySelector('.filter-select');
    
    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            const value = this.value;
            const baseUrl = window.location.pathname;
            const params = new URLSearchParams(window.location.search);

            if (value !== "") {
                params.set('curso', value);
                params.set('page', 1);
            } else {
                params.delete('curso');
            }

            const queryString = params.toString();
            const newUrl = queryString ? baseUrl + '?' + queryString : baseUrl;

            window.location.href = newUrl;
        });
    }
});