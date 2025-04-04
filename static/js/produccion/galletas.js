/**
 * Funciones para la gestión de solicitudes de galletas
 */

// Función para verificar los insumos disponibles para una receta
async function verificarInsumosReceta(recetaId, cantidad = 100) {
    try {
        // Usar el endpoint de previsualización en lugar del de verificación
        const response = await fetch(`/produccion/previsualizarProduccion/${recetaId}/${cantidad}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        });

        const data = await response.json();
        
        if (data.success) {
            if (data.hay_suficientes_insumos) {
                Swal.fire({
                    icon: 'success',
                    title: '¡Insumos Disponibles!',
                    text: `Puedes producir ${data.cantidad_ajustada} galletas de ${data.receta.nombre}.`
                });
                return true;
            } else {
                // Formatear mensaje de insumos faltantes
                let mensaje = `No hay suficientes insumos para producir ${data.cantidad_ajustada} galletas de ${data.receta.nombre}.\n\n`;
                mensaje += "Insumos faltantes:\n";
                
                data.insumos.forEach(insumo => {
                    if (!insumo.hay_suficientes) {
                        mensaje += `- ${insumo.nombre}: Necesario ${insumo.cantidad_necesaria} ${insumo.unidad}, Disponible ${insumo.cantidad_disponible} ${insumo.unidad}\n`;
                    }
                });
                
                Swal.fire({
                    icon: 'error',
                    title: 'Insumos Insuficientes',
                    text: mensaje
                });
                return false;
            }
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message || 'Ocurrió un error al verificar los insumos disponibles.'
            });
            return false;
        }
    } catch (error) {
        console.error('Error al verificar insumos:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error al verificar los insumos disponibles.'
        });
        return false;
    }
}

// Función para obtener el token CSRF
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Función para manejar el envío del formulario
async function solicitarGalletas(event) {
    event.preventDefault();
    
    const recetaId = document.getElementById('receta_id').value;
    const cantidad = document.getElementById('cantidad').value;
    
    if (!recetaId) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor seleccione una receta.'
        });
        return;
    }
    
    // Verificar insumos antes de enviar el formulario
    const insumosDisponibles = await verificarInsumosReceta(recetaId, cantidad);
    
    if (insumosDisponibles) {
        event.target.submit();
    }
}

// Función para actualizar la cantidad de galletas
function actualizarCantidadGalletas() {
    const recetaId = document.getElementById('receta_id').value;
    const cantidad = document.getElementById('cantidad').value;
    const submitBtn = document.querySelector('#formSolicitarGalletas button[type="submit"]');
    
    if (recetaId && cantidad) {
        verificarInsumosReceta(recetaId, cantidad);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('formSolicitarGalletas');
    const cantidadInput = document.getElementById('cantidad');
    const recetaSelect = document.getElementById('receta_id');
    const btnVerificar = document.getElementById('btnVerificarInsumos');
    
    if (form) {
        form.addEventListener('submit', solicitarGalletas);
    }
    
    if (cantidadInput) {
        cantidadInput.addEventListener('change', actualizarCantidadGalletas);
    }
    
    if (recetaSelect) {
        recetaSelect.addEventListener('change', actualizarCantidadGalletas);
    }
    
    if (btnVerificar) {
        btnVerificar.addEventListener('click', function() {
            const recetaId = document.getElementById('receta_id').value;
            const cantidad = document.getElementById('cantidad').value;
            verificarInsumosReceta(recetaId, cantidad);
        });
    }
}); 