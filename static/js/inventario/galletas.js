document.addEventListener('DOMContentLoaded', function() {
    // Cargar las galletas al inicio
    cargarGalletas();

    // Configurar filtros
    document.getElementById('busqueda').addEventListener('input', filtrarGalletas);
    document.getElementById('estadoStock').addEventListener('change', filtrarGalletas);
});

function cargarGalletas() {
    const galletasGrid = document.getElementById('galletasGrid');
    galletasGrid.innerHTML = ''; // Limpiar el grid

    // Obtener las galletas del servidor
    fetch('/inventario/galletas', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        data.recetas.forEach(receta => {
            const card = crearCardGalleta(receta);
            galletasGrid.appendChild(card);
        });
    })
    .catch(error => {
        console.error('Error al cargar las galletas:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudieron cargar las galletas'
        });
    });
}

function crearCardGalleta(receta) {
    const col = document.createElement('div');
    col.className = 'col-md-4 mb-4';
    
    // Calcular el porcentaje de stock
    const porcentajeStock = (receta.stock_disponible / receta.galletas_por_lote) * 100;
    
    // Determinar el color de la barra de progreso
    let progressColor = 'success';
    if (porcentajeStock < 30) progressColor = 'danger';
    else if (porcentajeStock < 70) progressColor = 'warning';

    // Formatear la fecha de caducidad
    const fechaCaducidad = receta.caducidad_proxima ? 
        new Date(receta.caducidad_proxima).toLocaleDateString() : 'N/A';

    col.innerHTML = `
        <div class="galleta-card">
            <div class="status-icon">
                ${receta.stock_disponible <= 0 ? 
                    '<i class="fas fa-exclamation-circle text-danger"></i>' : 
                    porcentajeStock < 30 ? 
                        '<i class="fas fa-exclamation-triangle text-warning"></i>' : 
                        '<i class="fas fa-check-circle text-success"></i>'
                }
            </div>
            <h3>${receta.nombre}</h3>
            <div class="info-row">
                <span>Stock Disponible:</span>
                <span>${receta.stock_disponible} / ${receta.galletas_por_lote}</span>
            </div>
            <div class="progress">
                <div class="progress-bar bg-${progressColor}" 
                     role="progressbar" 
                     style="width: ${porcentajeStock}%">
                </div>
            </div>
            <div class="info-row">
                <span>Última Merma:</span>
                <span>${receta.merma_reciente}</span>
            </div>
            <div class="info-row">
                <span>Caducidad:</span>
                <span class="${receta.caducidad_proxima && new Date(receta.caducidad_proxima) < new Date() ? 'caducidad-alerta' : ''}">
                    ${fechaCaducidad}
                </span>
            </div>
            <div class="info-row">
                <span>Precio:</span>
                <span>$${receta.precio.toFixed(2)}</span>
            </div>
            <div class="mt-3">
                <button class="btn btn-success w-100" 
                        onclick="verLotes(${receta.id})"
                        ${receta.stock_disponible <= 0 ? 'disabled' : ''}>
                    <i class="fas fa-box me-2"></i>Ver Lotes
                </button>
            </div>
        </div>
    `;

    return col;
}

function filtrarGalletas() {
    const busqueda = document.getElementById('busqueda').value.toLowerCase();
    const estadoStock = document.getElementById('estadoStock').value;
    const cards = document.querySelectorAll('.galleta-card');

    cards.forEach(card => {
        const nombre = card.querySelector('h3').textContent.toLowerCase();
        const stock = parseInt(card.querySelector('.info-row span:last-child').textContent.split('/')[0]);
        let mostrar = true;

        // Filtrar por búsqueda
        if (busqueda && !nombre.includes(busqueda)) {
            mostrar = false;
        }

        // Filtrar por estado de stock
        if (estadoStock !== 'todos') {
            if (estadoStock === 'bajo' && stock >= 30) {
                mostrar = false;
            } else if (estadoStock === 'normal' && stock < 30) {
                mostrar = false;
            }
        }

        card.closest('.col-md-4').style.display = mostrar ? '' : 'none';
    });
}

function verLotes(recetaId) {
    // Cerrar cualquier modal abierto
    const modalesAbiertos = document.querySelectorAll('.modal.show');
    modalesAbiertos.forEach(modalElement => {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    
    // Obtener los datos de los lotes
    fetch(`/inventario/galletas/${recetaId}/lotes`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al cargar los lotes');
            }
            return response.json();
        })
        .then(data => {
            if (!data.success) {
                throw new Error(data.message || 'Error al cargar los lotes');
            }

            // Mostrar el modal de lotes
            const modal = new bootstrap.Modal(document.getElementById('modalLotes'));
            document.getElementById('nombreGalleta').textContent = data.receta.nombre;
            
            // Llenar la tabla de lotes
            const tbody = document.getElementById('lotesBody');
            tbody.innerHTML = '';
            
            data.lotes.forEach(lote => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${lote.lote_id}</td>
                    <td>${new Date(lote.fecha_produccion).toLocaleDateString()}</td>
                    <td>${new Date(lote.caducidad).toLocaleDateString()}</td>
                    <td>${lote.cantidad_producida}</td>
                    <td>${lote.cantidad_disponible}</td>
                    <td>${lote.merma}</td>
                    <td>
                        <span class="badge bg-${lote.cantidad_disponible <= 0 ? 'danger' : 
                            lote.cantidad_disponible < 30 ? 'warning' : 'success'}">
                            ${lote.cantidad_disponible <= 0 ? 'Agotado' : 
                              lote.cantidad_disponible < 30 ? 'Bajo' : 'Normal'}
                        </span>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            modal.show();
        })
        .catch(error => {
            console.error('Error al cargar los lotes:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los lotes'
            });
        });
}

function solicitarLote() {
    // Cerrar cualquier modal abierto
    const modalesAbiertos = document.querySelectorAll('.modal.show');
    modalesAbiertos.forEach(modalElement => {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }
    });
    
    const modal = new bootstrap.Modal(document.getElementById('modalSolicitarLote'));
    modal.show();
}

// Manejar el envío del formulario de solicitud de lote
document.getElementById('formSolicitarLote').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    fetch('/inventario/pedidos/galletas/agregar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            Swal.fire({
                icon: 'success',
                title: 'Éxito',
                text: 'Lote solicitado correctamente'
            }).then(() => {
                // Cerrar el modal y recargar las galletas
                bootstrap.Modal.getInstance(document.getElementById('modalSolicitarLote')).hide();
                cargarGalletas();
            });
        } else {
            throw new Error(data.message || 'Error al solicitar el lote');
        }
    })
    .catch(error => {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message
        });
    });
}); 