function verLotes(tipoInsumoId) {
    fetch(`/inventario/lotes/${tipoInsumoId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            const tbody = document.getElementById('lotesTableBody');
            tbody.innerHTML = '';
            
            data.lotes.forEach(lote => {
                const tr = document.createElement('tr');
                const estadoClase = {
                    'terminado': 'bg-secondary',
                    'caduco': 'bg-danger',
                    'proximo_caducar': 'bg-warning',
                    'vigente': 'bg-success'
                }[lote.estado] || 'bg-secondary';
                
                const estadoBadge = `<span class="badge ${estadoClase}">${lote.mensaje}</span>`;
                
                // Validar que insumo_id esté presente
                if (!lote.insumo_id) {
                    console.error('Error: insumo_id no encontrado para el lote:', lote.lote_id);
                    return;
                }
                
                tr.innerHTML = `
                    <td>${lote.lote_id}</td>
                    <td>${lote.cantidad} ${lote.unidad}</td>
                    <td>${lote.proveedor || 'Sin proveedor'}</td>
                    <td>${lote.fecha_registro || 'N/A'}</td>
                    <td>${lote.fecha_caducidad || 'N/A'}</td>
                    <td>${estadoBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-info me-1" 
                                onclick="verLoteEspecifico('${lote.lote_id}')"
                                title="Ver detalles">
                            <i class="bi bi-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" 
                                onclick="declararMerma(${lote.insumo_id}, '${lote.lote_id}', ${lote.cantidad}, '${lote.unidad}')"
                                ${lote.cantidad <= 0 ? 'disabled' : ''}
                                title="Declarar merma">
                            <i class="fas fa-exclamation-triangle"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // Mostrar el modal de Bootstrap
            const modal = new bootstrap.Modal(document.getElementById('lotesModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar los lotes');
        });
} 