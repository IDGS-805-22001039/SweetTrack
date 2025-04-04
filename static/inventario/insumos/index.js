document.addEventListener('DOMContentLoaded', function() {
    const tipoInsumoSelect = document.getElementById('filtroCategoria');
    const insumoSelect = document.getElementById('insumoSelect');
    const proveedorSelect = document.getElementById('proveedorSelect');
    const cantidadInput = document.getElementById('cantidadInsumo');
    const precioUnitarioInput = document.getElementById('precioUnitario');
    const totalInput = document.getElementById('totalPagar');
    const loteInput = document.getElementById('loteInsumo');

    // Función para calcular el total
    function calcularTotal() {
        const cantidad = parseFloat(cantidadInput.value) || 0;
        const precioUnitario = parseFloat(precioUnitarioInput.value) || 0;
        const total = cantidad * precioUnitario;
        totalInput.value = total.toFixed(2);
    }

    // Evento para calcular el total cuando cambia la cantidad o el precio
    if (cantidadInput) {
        cantidadInput.addEventListener('input', calcularTotal);
    }
    if (precioUnitarioInput) {
        precioUnitarioInput.addEventListener('input', calcularTotal);
    }

    if (tipoInsumoSelect) {
        tipoInsumoSelect.addEventListener('change', function() {
            const tipoId = this.value;
            if (!tipoId) return;

            // Limpiar selects
            if (insumoSelect) {
                insumoSelect.innerHTML = '<option value="">Seleccione un insumo</option>';
            }
            if (proveedorSelect) {
                proveedorSelect.innerHTML = '<option value="">Seleccione un proveedor</option>';
            }

            // Obtener datos del tipo de insumo usando query params
            fetch(`/inventario/insumos/tipo?tipo_id=${tipoId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la respuesta del servidor');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Datos recibidos:', data);
                    
                    // Actualizar el lote
                    if (loteInput && data.nuevo_lote) {
                        loteInput.value = data.nuevo_lote;
                    }
                    
                    // Llenar select de insumos
                    if (insumoSelect && data.insumos) {
                        data.insumos.forEach(insumo => {
                            const option = document.createElement('option');
                            option.value = insumo.nombre;
                            option.textContent = `${insumo.nombre} (${insumo.unidad})`;
                            option.dataset.unidad = insumo.unidad;
                            insumoSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al cargar los datos. Por favor, intente nuevamente.');
                });
        });
    }

    // Evento para cargar proveedores cuando se selecciona un insumo
    if (insumoSelect) {
        insumoSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const insumoId = this.value;
            
            if (!insumoId) {
                if (proveedorSelect) {
                    proveedorSelect.innerHTML = '<option value="">Seleccione un proveedor</option>';
                }
                return;
            }

            // Obtener datos del tipo de insumo para este insumo específico
            fetch(`/inventario/insumos/tipo?tipo_id=${tipoInsumoSelect.value}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la respuesta del servidor');
                    }
                    return response.json();
                })
                .then(data => {
                    // Encontrar el insumo seleccionado
                    const insumoSeleccionado = data.insumos.find(i => i.id == insumoId);
                    
                    if (insumoSeleccionado && proveedorSelect) {
                        // Limpiar select de proveedores
                        proveedorSelect.innerHTML = '<option value="">Seleccione un proveedor</option>';
                        
                        // Llenar select de proveedores
                        insumoSeleccionado.proveedores.forEach(proveedor => {
                            const option = document.createElement('option');
                            option.value = proveedor.id;
                            option.textContent = proveedor.nombre;
                            option.dataset.precio = proveedor.precio;
                            proveedorSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al cargar los proveedores. Por favor, intente nuevamente.');
                });
        });
    }

    // Evento para actualizar el precio unitario cuando se selecciona un proveedor
    if (proveedorSelect) {
        proveedorSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption && selectedOption.dataset.precio && precioUnitarioInput) {
                precioUnitarioInput.value = selectedOption.dataset.precio;
                calcularTotal();
            }
        });
    }
}); 