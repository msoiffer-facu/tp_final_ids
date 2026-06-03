let html5QrcodeScanner = null;
let camarasDisponibles = [];
let estaProcesando = false;
let ultimoCodigoLeido = "";
let tiempoUltimoEscaneo = 0;

function cerrarModal(id) {
    const modal = document.getElementById(id);

    modal.classList.remove('modal--open');
    modal.setAttribute('aria-hidden', 'true');
}

const qrForm = document.getElementById('formClasePresencial');
const qrTokenInput = document.getElementById('qrTokenInput');
const qrFormTargetIframe = document.getElementById('qr-form-target');

if (qrFormTargetIframe) {
    qrFormTargetIframe.dataset.waiting = "false";
    qrFormTargetIframe.onload = () => {
        if (qrFormTargetIframe.dataset.waiting !== "true") {
            return;
        }

        qrFormTargetIframe.dataset.waiting = "false";
        const tituloModal = document.querySelector('#qr-modal h3');
        const tituloOriginal = tituloModal ? tituloModal.innerText : "Escanear Asistencia QR";
        let mensaje = "Error al procesar la asistencia";
        let esExito = false;

        try {
            const texto = qrFormTargetIframe.contentDocument.body.innerText || "";
            if (texto.toLowerCase().includes('se a verificado') || texto.toLowerCase().includes('registrada') || texto.toLowerCase().includes('verificado correctamente')) {
                mensaje = "¡Asistencia Registrada!";
                esExito = true;
            } else {
                mensaje = texto.trim() || mensaje;
            }
        } catch (err) {
            console.error('No se pudo leer la respuesta del iframe:', err);
        }

        if (tituloModal) {
            tituloModal.innerText = mensaje;
            tituloModal.style.color = esExito ? "#10b981" : "#ef4444";
        }

        setTimeout(() => {
            if (tituloModal) {
                tituloModal.innerText = tituloOriginal;
                tituloModal.style.color = "#000";
            }
            estaProcesando = false;
        }, 1500);
    };
}

function abrirEscannerQR() {
    document.getElementById('qr-modal').style.display = 'flex';

    cerrarModal('modalClase');

    //Instanciar el lector sobre el div 'reader'
    html5QrCode = new Html5Qrcode("reader");

    //Pedir permisos y listar las cámaras del dispositivo
    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length > 0) {
            camarasDisponibles = devices;
            const select = document.getElementById('camera-select');
            select.innerHTML = '';

            //Poner en el select las cámaras encontradas
            devices.forEach((device, index) => {
                const option = document.createElement('option');
                option.value = device.id;
                // Si la etiqueta viene vacía, le ponemos un nombre genérico
                option.text = device.label || `Cámara ${index + 1}`;
                select.appendChild(option);
            });

            // Cambiar de cámara en tiempo real si el usuario la cambia en el select
            select.onchange = () => {
                reiniciarCamara(select.value);
            };

            // 4. Iniciar automáticamente con la primera cámara de la lista
            encenderCamara(devices[0].id);

        } else {
            alert("No se detectaron cámaras en este dispositivo.");
            cerrarEscannerQR();
        }
    }).catch(err => {
        console.error("Error al obtener cámaras:", err);
        alert("Error de permisos: Asegúrate de permitir el acceso a la cámara.");
        cerrarEscannerQR();
    });
}

function encenderCamara(cameraId) {
    if (!html5QrCode) return;

    // Configuración del escaneo
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 }
    };

    // Encendemos el flujo de video local
    html5QrCode.start(
        cameraId,
        config,
        onScanSuccess, // Función si detecta un QR (reutiliza la que ya tenías)
        onScanFailure  // Función si falla el frame
    ).catch(err => {
        console.error("No se pudo iniciar la cámara seleccionada:", err);
    });
}

function reiniciarCamara(cameraId) {
    // Si ya está corriendo una cámara, la apagamos primero antes de encender la otra
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop().then(() => {
            encenderCamara(cameraId);
        }).catch(err => console.error("Error al detener cámara previa:", err));
    } else {
        encenderCamara(cameraId);
    }
}

// Esta función se ejecuta AUTOMÁTICAMENTE de forma local cuando JavaScript detecta un QR válido
function onScanSuccess(decodedText, decodedResult) {
    const ahora = Date.now();
    // Si ya está procesando una petición anterior, ignoramos este frame
    if (estaProcesando) return;

    // Si es el mismo código de antes y no pasaron más de 3 segundos, lo ignoramos
    if (decodedText === ultimoCodigoLeido && (ahora - tiempoUltimoEscaneo) < 3000) {
        return;
    }

    // Marcamos que empezamos a procesar este QR
    estaProcesando = true;
    ultimoCodigoLeido = decodedText;
    tiempoUltimoEscaneo = ahora;

    console.log(`Código detectado (Escaneo continuo): ${decodedText}`);

    // Ejecutamos el envío a Python
    enviarAsistenciaAlBackend(decodedText);
}

function onScanFailure(error) {
    // Esta función corre en cada frame de video donde NO se encuentra un QR.
}

function cerrarEscannerQR() {
    document.getElementById('qr-modal').style.display = 'none';

    if (html5QrCode) {
        if (html5QrCode.isScanning) {
            html5QrCode.stop().then(() => {
                html5QrCode = null;
            }).catch(err => console.error("Error al apagar la cámara al cerrar:", err));
        } else {
            html5QrCode = null;
        }
    }
}

function enviarAsistenciaAlBackend(textoQR) {
    const tituloModal = document.querySelector('#qr-modal h3');
    const tituloOriginal = tituloModal ? tituloModal.innerText : "Escanear Asistencia QR";
    const claseSeleccionada = document.getElementById('selectEscanear')?.value;

    if (!qrForm || !qrTokenInput) {
        console.error('Formulario QR no encontrado en la página');
        if (tituloModal) {
            tituloModal.innerText = "Error interno: formulario no disponible";
            tituloModal.style.color = "#ef4444";
        }
        estaProcesando = false;
        return;
    }

    if (!claseSeleccionada) {
        if (tituloModal) {
            tituloModal.innerText = "Selecciona la clase antes de escanear el QR.";
            tituloModal.style.color = "#ef4444";
        }
        estaProcesando = false;
        setTimeout(() => {
            if (tituloModal) {
                tituloModal.innerText = tituloOriginal;
                tituloModal.style.color = "#000";
            }
        }, 2500);
        return;
    }

    qrTokenInput.value = textoQR;
    if (qrFormTargetIframe) {
        qrFormTargetIframe.dataset.waiting = "true";
    }

    if (tituloModal) {
        tituloModal.innerText = "⏳ Procesando...";
        tituloModal.style.color = "#3b82f6";
    }

    qrForm.submit();
}