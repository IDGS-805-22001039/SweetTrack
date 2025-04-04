// Por ahora, dejemos el archivo vacío 

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalNuevoInsumo');
    const form = document.getElementById('formNuevoInsumo');
    const precioInput = form.querySelector('[name="precio"]');
    const cantidadInput = form.querySelector('[name="cantidad"]');
    const totalInput = document.getElementById('total');
    const fechaCaducidadInput = form.querySelector('[name="fecha_caducidad"]');

    // Cargar siguiente lote al abrir el modal
    modal.addEventListener('show.bs.modal', async function() {
        try {
            const response = await fetch('/inventario/obtener-siguiente-lote');
            const data = await response.json();
            if (data.success) {
                document.getElementById('siguienteLote').textContent = data.lote;
                document.getElementById('loteId').value = data.lote;
            }
        } catch (error) {
            console.error('Error al obtener siguiente lote:', error);
        }
    });

    // Función para calcular y mostrar el total del lote
    function calcularTotalLote() {
        const precio = parseFloat(precioInput.value) || 0;
        const cantidad = parseFloat(cantidadInput.value) || 0;
        
        if (precio > 0 && cantidad > 0) {
            const total = precio * cantidad;
            totalInput.value = total.toFixed(2);
            
            // Mostrar el desglose del cálculo
            const desglose = document.getElementById('desgloseCalculo');
            if (desglose) {
                desglose.innerHTML = `
                    <small class="text-muted">
                        Cálculo: $${precio.toFixed(2)} × ${cantidad} = $${total.toFixed(2)}
                    </small>
                `;
            }
        } else {
            totalInput.value = '0.00';
            if (document.getElementById('desgloseCalculo')) {
                document.getElementById('desgloseCalculo').innerHTML = '';
            }
        }
    }

    // Calcular total cuando cambie el precio o la cantidad
    precioInput.addEventListener('input', calcularTotalLote);
    cantidadInput.addEventListener('input', calcularTotalLote);

    // Validar precio
    precioInput.addEventListener('input', function() {
        const precio = parseFloat(this.value);
        if (precio <= 0) {
            this.classList.add('is-invalid');
            this.nextElementSibling.textContent = 'El precio debe ser mayor a 0';
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            calcularTotalLote();
        }
    });

    // Validar cantidad
    cantidadInput.addEventListener('input', function() {
        const cantidad = parseFloat(this.value);
        if (cantidad <= 0 || cantidad > 100) {
            this.classList.add('is-invalid');
            this.nextElementSibling.textContent = 'La cantidad debe estar entre 1 y 100';
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
            calcularTotalLote();
        }
    });

    // Validar fecha de caducidad
    fechaCaducidadInput.addEventListener('change', function() {
        const fechaSeleccionada = new Date(this.value);
        const hoy = new Date();
        hoy.setHours(0, 0, 0, 0);

        if (fechaSeleccionada <= hoy) {
            this.classList.add('is-invalid');
            this.nextElementSibling.textContent = 'La fecha debe ser posterior a hoy';
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        }
    });
});

// Función para guardar el insumo
function guardarInsumo() {
    const form = document.getElementById('formNuevoInsumo');
    
    // Validar todos los campos requeridos
    let isValid = true;
    const camposRequeridos = ['categoria_id', 'nombre', 'proveedor_id', 'precio', 'cantidad', 'unidad_medida', 'fecha_caducidad'];
    
    camposRequeridos.forEach(campo => {
        const input = form.querySelector(`[name="${campo}"]`);
        if (!input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        }
    });

    // Validaciones específicas
    const precio = parseFloat(form.querySelector('[name="precio"]').value);
    const cantidad = parseFloat(form.querySelector('[name="cantidad"]').value);
    const fecha = new Date(form.querySelector('[name="fecha_caducidad"]').value);
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (precio <= 0) {
        form.querySelector('[name="precio"]').classList.add('is-invalid');
        isValid = false;
    }

    if (cantidad <= 0 || cantidad > 100) {
        form.querySelector('[name="cantidad"]').classList.add('is-invalid');
        isValid = false;
    }

    if (fecha <= hoy) {
        form.querySelector('[name="fecha_caducidad"]').classList.add('is-invalid');
        isValid = false;
    }

    if (!isValid) {
        Swal.fire({
            icon: 'error',
            title: 'Error de validación',
            text: 'Por favor, complete todos los campos correctamente'
        });
        return;
    }

    // Enviar formulario
    const formData = new FormData(form);
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: data.message,
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                window.location.reload();
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message
            });
        }
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error al procesar la solicitud'
        });
    });
} 