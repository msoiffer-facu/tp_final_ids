let html5QrcodeScanner = null;
let camarasDisponibles = [];
let estaProcesando = false;
let ultimoCodigoLeido = "";
let tiempoUltimoEscaneo = 0;

function abrirEscannerQR() {
    document.getElementById('qr-modal').style.display = 'flex';

    //Instanciar el lector sobre el div 'reader'
    html5QrCode = new Html5Qrcode("reader");

    //Pedir permisos y listar las cámaras del dispositivo
    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length > 0) {
            camarasDisponibles = devices;
            const select = document.getElementById('camera-select');
            select.innerHTML = ''; // Limpiar opciones anteriores

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

    // Ejecutamos el envío a Python (ya NO llamamos a cerrarEscannerQR)
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
    const payload = {
        datos_qr: textoQR,
        timestamp: new Date().toISOString()
    };

    // Cambiamos sutilmente el diseño del modal para avisar visualmente que está registrando
    const tituloModal = document.querySelector('#qr-modal h3');
    const tituloOriginal = tituloModal.innerText;
    tituloModal.innerText = "⏳ Procesando..."
    tituloModal.style.color = "#3b82f6";

    fetch('/api/asistencia/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            // Éxito
            tituloModal.innerText = "¡Asistencia Registrada!";
            tituloModal.style.color = "#10b981";
        } else {
            // Error de lógica del negocio (ej. alumno ya tenía presente)
            tituloModal.innerText = `${data.error}`;
            tituloModal.style.color = "#ef4444";
        }
    })
    .catch(err => {
        console.error(err);
        tituloModal.innerText = "Error de conexión";
        tituloModal.style.color = "#ef4444";
    })
    .finally(() => {
        setTimeout(() => {
            tituloModal.innerText = tituloOriginal;
            tituloModal.style.color = "#000";
            estaProcesando = false;
        }, 1500);
    });

// Esto de abajo sirve para probar si funciona la lo de que la camara siga funcionando despues de escanear un qr

    // try{
    //     tituloModal.innerText = "¡Asistencia Registrada!";
    //     tituloModal.style.color = "#10b981";
    // }
    // catch(error){
    //     console.error(err);
    //     tituloModal.innerText = "Error de conexión";
    //     tituloModal.style.color = "#ef4444";
    // }
    // finally{
    //     setTimeout(() => {
    //         tituloModal.innerText = tituloOriginal;
    //         tituloModal.style.color = "#000";
    //         estaProcesando = false;
    //     }, 1500);
    // }
}