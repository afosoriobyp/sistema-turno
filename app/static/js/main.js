/**
 * JavaScript principal para el Sistema de Gestión de Turnos
 * 
 * Este archivo contiene funciones JavaScript reutilizables
 * para toda la aplicación.
 */

/**
 * Inicializa la conexión con Socket.IO cuando el documento está listo
 */
document.addEventListener('DOMContentLoaded', function () {
    console.log('Sistema de Turnos - Iniciado');
});

/**
 * Formatea una fecha al formato local
 * @param {Date} fecha - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatearFecha(fecha) {
    if (!(fecha instanceof Date)) {
        fecha = new Date(fecha);
    }

    return fecha.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Formatea una hora al formato HH:MM:SS
 * @param {Date} fecha - Fecha con hora
 * @returns {string} Hora formateada
 */
function formatearHora(fecha) {
    if (!(fecha instanceof Date)) {
        fecha = new Date(fecha);
    }

    return fecha.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Valida un número de cédula (formato básico)
 * @param {string} cedula - Número de cédula
 * @returns {boolean} true si es válida
 */
function validarCedula(cedula) {
    // Eliminar espacios y guiones
    cedula = cedula.replace(/[\s-]/g, '');

    // Verificar que solo contenga números y tenga longitud adecuada
    return /^\d{7,12}$/.test(cedula);
}

/**
 * Valida un correo electrónico
 * @param {string} email - Correo electrónico
 * @returns {boolean} true si es válido
 */
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida un número de teléfono
 * @param {string} telefono - Número de teléfono
 * @returns {boolean} true si es válido
 */
function validarTelefono(telefono) {
    // Eliminar espacios, paréntesis y guiones
    telefono = telefono.replace(/[\s()-]/g, '');

    // Verificar que tenga entre 7 y 15 dígitos
    return /^\d{7,15}$/.test(telefono);
}

/**
 * Muestra un mensaje de confirmación al usuario
 * @param {string} mensaje - Mensaje a mostrar
 * @returns {boolean} true si el usuario confirma
 */
function confirmar(mensaje) {
    return confirm(mensaje);
}

/**
 * Muestra un mensaje de alerta al usuario
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo de alerta (info, success, warning, error)
 */
function mostrarAlerta(mensaje, tipo = 'info') {
    alert(mensaje);
}

/**
 * Reproduce un sonido de notificación
 */
function reproducirSonidoNotificacion() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.error('Error al reproducir sonido:', error);
    }
}

/**
 * Realiza una petición HTTP POST con JSON
 * @param {string} url - URL del endpoint
 * @param {object} data - Datos a enviar
 * @returns {Promise} Promesa con la respuesta
 */
async function postJSON(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    } catch (error) {
        console.error('Error en petición POST:', error);
        throw error;
    }
}

/**
 * Realiza una petición HTTP GET
 * @param {string} url - URL del endpoint
 * @returns {Promise} Promesa con la respuesta
 */
async function getJSON(url) {
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error('Error en petición GET:', error);
        throw error;
    }
}

/**
 * Capitaliza la primera letra de un string
 * @param {string} str - String a capitalizar
 * @returns {string} String capitalizado
 */
function capitalizar(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Convierte un estado de turno a texto legible
 * @param {string} estado - Estado del turno
 * @returns {string} Texto legible del estado
 */
function estadoATexto(estado) {
    const estados = {
        'pendiente': 'Pendiente',
        'en_atencion': 'En Atención',
        'atendido': 'Atendido',
        'cancelado': 'Cancelado'
    };

    return estados[estado] || estado;
}

/**
 * Convierte una categoría a texto legible con emoji
 * @param {string} categoria - Categoría de atención
 * @returns {string} Texto legible con emoji
 */
function categoriaATexto(categoria) {
    const categorias = {
        'adulto_mayor': '👴 Adulto Mayor',
        'discapacidad': '♿ Discapacidad',
        'embarazada': '🤰 Mujer Embarazada',
        'ninguna': '👤 Atención Regular'
    };

    return categorias[categoria] || categoria;
}

/**
 * Calcula el tiempo transcurrido desde una fecha
 * @param {Date|string} fecha - Fecha inicial
 * @returns {string} Tiempo transcurrido en formato legible
 */
function tiempoTranscurrido(fecha) {
    if (!(fecha instanceof Date)) {
        fecha = new Date(fecha);
    }

    const ahora = new Date();
    const diferencia = ahora - fecha;

    const minutos = Math.floor(diferencia / 60000);
    const horas = Math.floor(minutos / 60);
    const dias = Math.floor(horas / 24);

    if (dias > 0) {
        return `${dias} día${dias > 1 ? 's' : ''}`;
    } else if (horas > 0) {
        return `${horas} hora${horas > 1 ? 's' : ''}`;
    } else if (minutos > 0) {
        return `${minutos} minuto${minutos > 1 ? 's' : ''}`;
    } else {
        return 'Hace un momento';
    }
}

/**
 * Descarga datos como archivo JSON
 * @param {object} data - Datos a descargar
 * @param {string} filename - Nombre del archivo
 */
function descargarJSON(data, filename) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });

    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
}

/**
 * Copia texto al portapapeles
 * @param {string} texto - Texto a copiar
 */
async function copiarAlPortapapeles(texto) {
    try {
        await navigator.clipboard.writeText(texto);
        console.log('Texto copiado al portapapeles');
    } catch (error) {
        console.error('Error al copiar al portapapeles:', error);
    }
}

/**
 * Detecta si el usuario está en un dispositivo móvil
 * @returns {boolean} true si es móvil
 */
function esDispositivoMovil() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Genera un color aleatorio en formato hexadecimal
 * @returns {string} Color en formato #RRGGBB
 */
function colorAleatorio() {
    return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}

/**
 * Formatea un número con separadores de miles
 * @param {number} numero - Número a formatear
 * @returns {string} Número formateado
 */
function formatearNumero(numero) {
    return numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function para limitar la frecuencia de ejecución
 * @param {function} func - Función a ejecutar
 * @param {number} wait - Tiempo de espera en ms
 * @returns {function} Función con debounce
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Limpia y sanitiza un string para prevenir XSS
 * @param {string} str - String a limpiar
 * @returns {string} String sanitizado
 */
function sanitizarHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Exportar funciones para uso global
window.SistemaTurnos = {
    formatearFecha,
    formatearHora,
    validarCedula,
    validarEmail,
    validarTelefono,
    confirmar,
    mostrarAlerta,
    reproducirSonidoNotificacion,
    postJSON,
    getJSON,
    capitalizar,
    estadoATexto,
    categoriaATexto,
    tiempoTranscurrido,
    descargarJSON,
    copiarAlPortapapeles,
    esDispositivoMovil,
    colorAleatorio,
    formatearNumero,
    debounce,
    sanitizarHTML
};

console.log('Sistema de Turnos JS - Cargado');
