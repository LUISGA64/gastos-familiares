/**
 * Auto-logout por inactividad con modal de advertencia
 * Configuración: 15 minutos de inactividad total, advertencia a los 14 minutos
 */

(function() {
    'use strict';

    // Configuración (en milisegundos)
    const TIEMPO_INACTIVIDAD = 15 * 60 * 1000;  // 15 minutos
    const TIEMPO_ADVERTENCIA = 14 * 60 * 1000;  // 14 minutos
    const INTERVALO_CHECK = 1000;  // 1 segundo

    let tiempoUltimaActividad = Date.now();
    let modalAdvertenciaShown = false;
    let intervalId = null;
    let countdownIntervalId = null;

    // Eventos que resetean el contador de inactividad
    const eventosActividad = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];

    /**
     * Resetear el tiempo de última actividad
     */
    function resetearTiempoActividad() {
        tiempoUltimaActividad = Date.now();

        // Si el modal está visible y hay actividad, cerrarlo
        if (modalAdvertenciaShown) {
            cerrarModalAdvertencia();
        }
    }

    /**
     * Verificar tiempo de inactividad
     */
    function verificarInactividad() {
        const tiempoTranscurrido = Date.now() - tiempoUltimaActividad;

        // Si supera el tiempo de inactividad, cerrar sesión
        if (tiempoTranscurrido >= TIEMPO_INACTIVIDAD) {
            cerrarSesionPorInactividad();
        }
        // Si supera el tiempo de advertencia, mostrar modal
        else if (tiempoTranscurrido >= TIEMPO_ADVERTENCIA && !modalAdvertenciaShown) {
            mostrarModalAdvertencia();
        }
    }

    /**
     * Mostrar modal de advertencia
     */
    function mostrarModalAdvertencia() {
        modalAdvertenciaShown = true;

        // Crear modal si no existe
        if (!document.getElementById('modalInactividad')) {
            crearModalAdvertencia();
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('modalInactividad'));
        modal.show();

        // Iniciar cuenta regresiva
        iniciarCuentaRegresiva();
    }

    /**
     * Cerrar modal de advertencia
     */
    function cerrarModalAdvertencia() {
        modalAdvertenciaShown = false;

        // Cerrar modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalInactividad'));
        if (modal) {
            modal.hide();
        }

        // Detener cuenta regresiva
        if (countdownIntervalId) {
            clearInterval(countdownIntervalId);
            countdownIntervalId = null;
        }
    }

    /**
     * Crear elemento del modal de advertencia
     */
    function crearModalAdvertencia() {
        const modalHTML = `
            <div class="modal fade" id="modalInactividad" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-warning">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">
                                <i class="bi bi-exclamation-triangle"></i> ⏰ Sesión por Expirar
                            </h5>
                        </div>
                        <div class="modal-body text-center py-4">
                            <div class="mb-3">
                                <i class="bi bi-hourglass-split display-1 text-warning"></i>
                            </div>
                            <h5>Tu sesión está por expirar por inactividad</h5>
                            <p class="text-muted mb-4">
                                Has estado inactivo durante un tiempo. Por seguridad, cerraremos tu sesión automáticamente.
                            </p>
                            <div class="alert alert-warning mb-0">
                                <p class="mb-2">Tu sesión se cerrará en:</p>
                                <h2 class="mb-0">
                                    <span id="countdownSegundos" class="badge bg-danger fs-3">60</span> segundos
                                </h2>
                            </div>
                        </div>
                        <div class="modal-footer justify-content-center">
                            <button type="button" class="btn btn-success btn-lg" id="btnSeguirConectado">
                                <i class="bi bi-check-circle"></i> Seguir Conectado
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Insertar modal en el body
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Event listener para botón "Seguir Conectado"
        document.getElementById('btnSeguirConectado').addEventListener('click', function() {
            resetearTiempoActividad();
        });
    }

    /**
     * Iniciar cuenta regresiva en el modal
     */
    function iniciarCuentaRegresiva() {
        const tiempoRestante = TIEMPO_INACTIVIDAD - (Date.now() - tiempoUltimaActividad);
        let segundosRestantes = Math.floor(tiempoRestante / 1000);

        const elementoCountdown = document.getElementById('countdownSegundos');

        countdownIntervalId = setInterval(function() {
            segundosRestantes--;

            if (elementoCountdown) {
                elementoCountdown.textContent = segundosRestantes;

                // Cambiar color según el tiempo
                if (segundosRestantes <= 10) {
                    elementoCountdown.className = 'badge bg-danger fs-3 blink';
                } else if (segundosRestantes <= 30) {
                    elementoCountdown.className = 'badge bg-danger fs-3';
                }
            }

            if (segundosRestantes <= 0) {
                clearInterval(countdownIntervalId);
            }
        }, 1000);
    }

    /**
     * Cerrar sesión por inactividad
     */
    function cerrarSesionPorInactividad() {
        // Detener intervalos
        if (intervalId) clearInterval(intervalId);
        if (countdownIntervalId) clearInterval(countdownIntervalId);

        // Mostrar mensaje
        console.log('Sesión cerrada por inactividad');

        // Redirigir al logout
        window.location.href = '/logout/?inactividad=1';
    }

    /**
     * Inicializar sistema de auto-logout
     */
    function inicializar() {
        // Solo en páginas autenticadas (que tengan el navbar de usuario)
        if (!document.querySelector('[data-user-authenticated]')) {
            return;
        }

        // Registrar eventos de actividad
        eventosActividad.forEach(function(evento) {
            document.addEventListener(evento, resetearTiempoActividad, true);
        });

        // Iniciar verificación periódica
        intervalId = setInterval(verificarInactividad, INTERVALO_CHECK);

        console.log('Sistema de auto-logout iniciado: ' + (TIEMPO_INACTIVIDAD/60000) + ' minutos');
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }

    // Estilo para el parpadeo
    const style = document.createElement('style');
    style.textContent = `
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .blink {
            animation: blink 1s infinite;
        }
    `;
    document.head.appendChild(style);

})();
