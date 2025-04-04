function mostrarCaducados() {
    // Cerrar cualquier modal abierto
    const modalesAbiertos = document.querySelectorAll('.modal.show');
    modalesAbiertos.forEach(modalElement => {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    
    // Obtener los insumos caducados
    fetch('/inventario/insumos/caducados')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error
                });
                return;
            }

            const tbody = document.getElementById('caducadosTableBody');
            tbody.innerHTML = '';

            if (data.insumos_caducados && data.insumos_caducados.length > 0) {
                data.insumos_caducados.forEach(insumo => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <div class="form-check">
                                <input class="form-check-input insumo-check" type="checkbox" 
                                       data-insumo-id="${insumo.insumo_id}"
                                       data-lote-id="${insumo.lote_id}"
                                       data-cantidad="${insumo.cantidad}">
                            </div>
                        </td>
                        <td>${insumo.nombre}</td>
                        <td>${insumo.lote_id}</td>
                        <td>${insumo.cantidad} ${insumo.unidad}</td>
                        <td>${insumo.dias_caducado} días</td>
                        <td>${insumo.fecha_caducidad}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">
                            No hay insumos caducados
                        </td>
                    </tr>
                `;
            }

            const modal = new bootstrap.Modal(document.getElementById('caducadosModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los insumos caducados'
            });
        });
}

document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listener al checkbox de seleccionar todos los caducados
    const selectAllCheckbox = document.getElementById('selectAllCaducados');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            document.querySelectorAll('#caducadosTableBody input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = isChecked;
            });
        });
    }
});

function declararMermasCaducados() {
    const checkboxes = document.getElementsByClassName('insumo-check');
    const mermas = [];

    Array.from(checkboxes).forEach(checkbox => {
        if (checkbox.checked) {
            mermas.push({
                insumo_id: checkbox.dataset.insumoId,
                lote_id: checkbox.dataset.loteId,
                cantidad: parseFloat(checkbox.dataset.cantidad)
            });
        }
    });

    if (mermas.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Atención',
            text: 'Por favor, seleccione al menos un insumo'
        });
        return;
    }

    Swal.fire({
        title: '¿Está seguro?',
        text: `Se declararán ${mermas.length} insumos como merma`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, declarar mermas',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/inventario/merma/multiple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ mermas: mermas })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: 'Mermas registradas correctamente'
                }).then(() => {
                    location.reload();
                });
            })
            .catch(error => {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: error.message
                });
            });
        }
    });
}

function declararMerma(insumoId, loteId, cantidadDisponible, unidad) {
    // Cerrar cualquier modal abierto
    const modalesAbiertos = document.querySelectorAll('.modal.show');
    modalesAbiertos.forEach(modalElement => {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    
    // Configurar el modal de merma
    document.getElementById('mermaInsumoId').value = insumoId;
    document.getElementById('mermaLoteId').value = loteId;
    document.getElementById('cantidadDisponible').textContent = `${cantidadDisponible} ${unidad}`;
    document.getElementById('cantidadMerma').max = cantidadDisponible;
    
    // Mostrar el modal
    const modal = new bootstrap.Modal(document.getElementById('declararMermaModal'));
    modal.show();
} 