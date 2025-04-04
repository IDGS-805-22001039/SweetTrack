// Log de inicialización del archivo
console.log('=== INICIO recetas.js ===');

window.addEventListener('DOMContentLoaded', function() {
    cargarRecetas();
});


// Funciones para manejar recetas
function cargarRecetas() {
    // Solo cargar recetas si estamos en la página de recetas
    if (!document.querySelector('.recetas-container')) {
        return;
    }

    const tbody = document.querySelector('#tablaRecetas tbody');
    if (!tbody) {
        console.log('La tabla de recetas no está disponible en esta página');
        return;
    }

    fetch('/recetas/listar')
        .then(response => response.json())
        .then(data => {
            // Actualizar la tabla de recetas
            tbody.innerHTML = '';
            
            data.forEach(receta => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${receta.nombre}</td>
                    <td>${receta.gramaje_por_galleta}g</td>
                    <td>${receta.galletas_por_lote}</td>
                    <td>$${receta.costo_por_galleta.toFixed(2)}</td>
                    <td>$${receta.precio_venta.toFixed(2)}</td>
                    <td>
                        <button class="btn btn-sm btn-info" onclick="verPasos(${receta.id})">
                            <i class="fas fa-list"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="editarReceta(${receta.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error al cargar recetas:', error));
}

function cargarInsumosDisponibles(recetaId) {
    console.log('Cargando insumos disponibles para receta:', recetaId);
    
    // Determinar la URL según el contexto
    const url = recetaId && recetaId !== 'crear' 
        ? `/recetas/ingredientes_disponibles/${recetaId}`
        : '/inventario/insumos/listar';
    
    console.log('URL de la petición:', url);
    
    // Obtener el selector y el botón
    const selector = document.getElementById(`selector-insumos-${recetaId}`);
    const btnAgregar = document.getElementById(`btn-agregar-${recetaId}`);
    
    if (!selector) {
        console.error('No se encontró el selector de insumos para receta:', recetaId);
        return;
    }
    
    // Limpiar el selector
    selector.innerHTML = '';
    
    // Agregar opción por defecto
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Seleccione un insumo';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    selector.appendChild(defaultOption);
    
    // Deshabilitar el botón inicialmente
    if (btnAgregar) {
        btnAgregar.disabled = true;
    }
    
    // Hacer la petición al servidor
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);
            
            // Procesar los datos según el endpoint usado
            const tiposInsumos = data.tipos_insumos || data;
            
            // Crear los grupos de opciones
            Object.entries(tiposInsumos).forEach(([tipo, insumos]) => {
                if (insumos && insumos.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = tipo;
                
                insumos.forEach(insumo => {
                    const option = document.createElement('option');
                        option.value = insumo.nombre || insumo.insumo_nombre;
                        option.textContent = `${insumo.nombre || insumo.insumo_nombre} (${insumo.cantidad_disponible || insumo.cantidad_existente} ${insumo.unidad})`;
                    option.dataset.unidad = insumo.unidad;
                        option.dataset.cantidad = insumo.cantidad_disponible || insumo.cantidad_existente;
                    option.dataset.insumo_id = insumo.id;
                    option.dataset.en_receta = insumo.en_receta;
                    option.dataset.cantidad_actual = insumo.cantidad_actual;
                    
                    // Si el insumo ya está en la receta, deshabilitarlo
                    if (insumo.en_receta) {
                        option.disabled = true;
                        option.textContent += ' (Ya en receta)';
                    }
                    
                    optgroup.appendChild(option);
                });
                
                selector.appendChild(optgroup);
                }
            });
            
            // Agregar evento para habilitar/deshabilitar el botón
            selector.addEventListener('change', function() {
                if (btnAgregar) {
                    btnAgregar.disabled = !this.value;
                }
            });
        })
        .catch(error => {
            console.error('Error al cargar insumos:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los insumos disponibles. Por favor, intente de nuevo.'
            });
        });
}

function agregarIngredienteRapido(recetaId) {
    console.log('Agregando ingrediente rápido para receta:', recetaId);
    
    const selector = document.getElementById(`selector-insumos-${recetaId}`);
    const ingredientesContainer = document.getElementById(`ingredientes-actuales-${recetaId}`);
    const btnAgregar = document.getElementById(`btn-agregar-rapido-${recetaId}`);
    
    if (!selector || !ingredientesContainer || !btnAgregar) {
        console.error('Elementos necesarios no encontrados:', {
            selector: selector ? 'encontrado' : 'no encontrado',
            ingredientesContainer: ingredientesContainer ? 'encontrado' : 'no encontrado',
            btnAgregar: btnAgregar ? 'encontrado' : 'no encontrado'
        });
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se encontraron los elementos necesarios para agregar el ingrediente'
        });
        return;
    }
    
    const selectedOption = selector.options[selector.selectedIndex];
    
    // Validar selección
    if (!selectedOption.value || selectedOption.disabled) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor seleccione un ingrediente válido'
        });
        return;
    }
    
    // Obtener el campo de cantidad
    const cantidadInput = document.getElementById(`cantidad-${recetaId}`);
    if (!cantidadInput) {
        console.error('Campo de cantidad no encontrado');
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor seleccione un ingrediente primero'
        });
        return;
    }
    
    const cantidad = parseFloat(cantidadInput.value);
    if (isNaN(cantidad) || cantidad <= 0) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor ingrese una cantidad válida mayor a 0'
        });
        cantidadInput.focus();
        return;
    }
    
    // Verificar si el ingrediente ya está agregado
    const ingredienteId = selectedOption.dataset.insumo_id;
    const ingredientesActuales = ingredientesContainer.querySelectorAll('.ingrediente-item');
    for (const ingrediente of ingredientesActuales) {
        if (ingrediente.dataset.ingredienteId === ingredienteId) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Este ingrediente ya está agregado a la receta'
            });
            return;
        }
    }
    
    // Crear nuevo elemento de ingrediente
    const nuevoIngrediente = document.createElement('div');
    nuevoIngrediente.className = 'row mb-3 ingrediente-item';
    nuevoIngrediente.dataset.ingredienteId = ingredienteId;
    nuevoIngrediente.innerHTML = `
        <div class="col-md-4">
            <label>Insumo</label>
            <input type="text" class="form-control" value="${selectedOption.value}" readonly>
            <input type="hidden" name="insumo_id[]" value="${ingredienteId}">
        </div>
        <div class="col-md-3">
            <label>Cantidad</label>
            <input type="number" step="0.01" name="cantidad_necesaria[]" class="form-control" value="${cantidad}" required>
        </div>
        <div class="col-md-3">
            <label>Unidad</label>
            <input type="text" name="unidad[]" class="form-control" value="${selectedOption.dataset.unidad}" readonly>
        </div>
        <div class="col-md-2">
            <label>&nbsp;</label>
            <button type="button" class="btn btn-danger btn-sm d-block w-100" onclick="eliminarIngrediente(this, '${recetaId}')">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Agregar el nuevo ingrediente al contenedor
    ingredientesContainer.appendChild(nuevoIngrediente);
    
    // Resetear el selector y la cantidad
    selector.selectedIndex = 0;
    cantidadInput.value = '';
    btnAgregar.disabled = true;
    
    // Mostrar mensaje de éxito
    Swal.fire({
        icon: 'success',
        title: 'Éxito',
        text: 'Ingrediente agregado correctamente',
        timer: 1500,
        showConfirmButton: false
    });
}

function eliminarIngrediente(button, recetaId) {
    console.log('Eliminando ingrediente de receta:', recetaId);
    
    // Obtener el contenedor del ingrediente
    const ingredienteItem = button.closest('.ingrediente-item');
    if (!ingredienteItem) {
        console.error('No se encontró el elemento del ingrediente');
        return;
    }
    
    // Eliminar el ingrediente del DOM
    ingredienteItem.remove();
    
    // Actualizar los insumos disponibles
    actualizarInsumosDisponibles(recetaId);
    
    // Mostrar mensaje de éxito
    Swal.fire({
        icon: 'success',
        title: 'Ingrediente eliminado',
        text: 'El ingrediente ha sido eliminado correctamente',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 2000
    });
}

function actualizarInsumosDisponibles(recetaId) {
    console.log('Actualizando insumos disponibles para receta:', recetaId);
    
    const selector = document.getElementById(`selector-insumos-${recetaId}`);
    if (!selector) {
        console.error('No se encontró el selector de insumos');
        return;
    }
    
    // Limpiar el selector
    selector.innerHTML = '';
    
    // Agregar opción por defecto
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Seleccione un insumo';
    defaultOption.disabled = true;
    defaultOption.selected = true;
    selector.appendChild(defaultOption);
    
    // Obtener los insumos disponibles
    fetch(`/recetas/ingredientes_disponibles/${recetaId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Insumos disponibles recibidos:', data);
            
            if (!data.success) {
                throw new Error(data.message || 'Error al obtener los insumos');
            }
            
            // Crear los grupos de opciones
            Object.entries(data.tipos_insumos).forEach(([tipo, insumos]) => {
                if (insumos && insumos.length > 0) {
                    const optgroup = document.createElement('optgroup');
                    optgroup.label = tipo;
                    
                    insumos.forEach(insumo => {
                        const option = document.createElement('option');
                        option.value = insumo.nombre;
                        option.textContent = insumo.nombre;
                        option.dataset.unidad = insumo.unidad;
                        option.dataset.cantidad = insumo.cantidad_disponible;
                        option.dataset.insumo_id = insumo.id;
                        option.dataset.en_receta = insumo.en_receta;
                        option.dataset.cantidad_actual = insumo.cantidad_actual;
                        
                        // Si el insumo ya está en la receta, deshabilitarlo
                        if (insumo.en_receta) {
                            option.disabled = true;
                            option.textContent += ' (Ya en receta)';
                        }
                        
                        optgroup.appendChild(option);
                    });
                    
                    selector.appendChild(optgroup);
                }
            });
            
            // Obtener el botón de agregar
            const btnAgregar = document.getElementById(`btn-agregar-rapido-${recetaId}`);
            
            // Agregar evento change al selector
            selector.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                const unidad = selectedOption.dataset.unidad;
                
                // Eliminar el contenedor de cantidad existente si hay uno
                const existingContainer = document.getElementById(`cantidad-container-${recetaId}`);
                if (existingContainer) {
                    existingContainer.remove();
                }
                
                if (this.value && !selectedOption.disabled) {
                    // Crear el campo de cantidad
                    const cantidadDiv = document.createElement('div');
                    cantidadDiv.className = 'input-group mb-3';
                    cantidadDiv.id = `cantidad-container-${recetaId}`;
                    cantidadDiv.innerHTML = `
                        <input type="number" step="0.01" class="form-control" id="cantidad-${recetaId}" placeholder="Cantidad" min="0" value="1">
                        <span class="input-group-text">${unidad}</span>
                    `;
                    
                    // Agregar el contenedor de cantidad al DOM
                    const formGroup = this.closest('.form-group');
                    if (formGroup) {
                        formGroup.appendChild(cantidadDiv);
                    } else {
                        // Si no hay form-group, agregar después del selector
                        this.parentNode.insertBefore(cantidadDiv, this.nextSibling);
                    }
                    
                    // Habilitar el botón de agregar
                    if (btnAgregar) {
                        btnAgregar.disabled = false;
                    }
                } else {
                    // Deshabilitar el botón de agregar
                    if (btnAgregar) {
                        btnAgregar.disabled = true;
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error al obtener insumos disponibles:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los insumos disponibles'
            });
        });
}

function enviarFormularioReceta(event, recetaId = null) {
    event.preventDefault();
    console.log('=== INICIO enviarFormularioReceta ===');
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Crear objeto para los datos
    const jsonData = {
        nombre: formData.get('nombre'),
        gramaje_por_galleta: parseFloat(formData.get('gramaje_por_galleta')),
        galletas_por_lote: parseInt(formData.get('galletas_por_lote')),
        costo_por_galleta: parseFloat(formData.get('costo_por_galleta')),
        precio_venta: parseFloat(formData.get('precio_venta')),
        pasos: formData.get('pasos'),
        ingredientes: []
    };

    console.log('Datos del formulario procesados:', jsonData);

    // Validar que los campos numéricos no sean null
    if (isNaN(jsonData.costo_por_galleta) || isNaN(jsonData.precio_venta) || 
        isNaN(jsonData.gramaje_por_galleta) || isNaN(jsonData.galletas_por_lote)) {
        console.error('Campos numéricos inválidos:', {
            costo: jsonData.costo_por_galleta,
            precio: jsonData.precio_venta,
            gramaje: jsonData.gramaje_por_galleta,
            galletas: jsonData.galletas_por_lote
        });
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor, complete todos los campos numéricos correctamente'
        });
        return;
    }

    // Obtener todos los ingredientes
    const ingredientesItems = form.querySelectorAll('.ingrediente-item');
    console.log('Número de ingredientes encontrados:', ingredientesItems.length);

    ingredientesItems.forEach((item, index) => {
        const insumoId = item.querySelector('input[name="insumo_id[]"]');
        const cantidad = item.querySelector('input[name="cantidad_necesaria[]"]');
        const unidad = item.querySelector('input[name="unidad[]"]');
        const nombre = item.querySelector('input[type="text"]');
        
        console.log(`Procesando ingrediente ${index + 1}:`, {
            insumoId: insumoId?.value,
            cantidad: cantidad?.value,
            unidad: unidad?.value,
            nombre: nombre?.value
        });

        if (insumoId && cantidad && unidad && nombre) {
            jsonData.ingredientes.push({
                insumo_id: insumoId.value,
                insumo_nombre: nombre.value,
                cantidad_necesaria: parseFloat(cantidad.value),
                unidad: unidad.value
            });
        } else {
            console.error(`Faltan datos en el ingrediente ${index + 1}`);
        }
    });

    // Validar que haya al menos un ingrediente
    if (jsonData.ingredientes.length === 0) {
        console.error('No hay ingredientes en la receta');
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Debe agregar al menos un ingrediente a la receta'
        });
        return;
    }

    console.log('Datos finales a enviar:', jsonData);
    enviarDatosReceta(jsonData, recetaId);
    console.log('=== FIN enviarFormularioReceta ===');
}

async function enviarDatosReceta(jsonData, recetaId = null) {
    console.log('=== INICIO enviarDatosReceta ===');
    console.log('Datos a enviar:', jsonData);
    
    const url = recetaId ? `/recetas/editar/${recetaId}` : '/recetas/crear';
    const method = recetaId ? 'PUT' : 'POST';
    
    try {
        // Validar que los datos requeridos estén presentes
        if (!jsonData.nombre || !jsonData.gramaje_por_galleta || !jsonData.galletas_por_lote || 
            !jsonData.costo_por_galleta || !jsonData.precio_venta || !jsonData.pasos) {
            console.error('Faltan campos requeridos:', {
                nombre: jsonData.nombre,
                gramaje: jsonData.gramaje_por_galleta,
                galletas: jsonData.galletas_por_lote,
                costo: jsonData.costo_por_galleta,
                precio: jsonData.precio_venta,
                pasos: jsonData.pasos
            });
            throw new Error('Faltan campos requeridos en la receta');
        }

        // Validar que haya al menos un ingrediente
        if (!jsonData.ingredientes || jsonData.ingredientes.length === 0) {
            console.error('No hay ingredientes en la receta');
            throw new Error('La receta debe tener al menos un ingrediente');
        }

        // Validar que los campos numéricos sean válidos
        if (isNaN(jsonData.gramaje_por_galleta) || isNaN(jsonData.galletas_por_lote) || 
            isNaN(jsonData.costo_por_galleta) || isNaN(jsonData.precio_venta)) {
            console.error('Campos numéricos inválidos:', {
                gramaje: jsonData.gramaje_por_galleta,
                galletas: jsonData.galletas_por_lote,
                costo: jsonData.costo_por_galleta,
                precio: jsonData.precio_venta
            });
            throw new Error('Los campos numéricos deben ser válidos');
        }

        // Validar cada ingrediente
        jsonData.ingredientes.forEach((ingrediente, index) => {
            if (!ingrediente.insumo_id || !ingrediente.cantidad_necesaria || !ingrediente.unidad) {
                console.error(`Faltan datos en el ingrediente ${index + 1}:`, ingrediente);
                throw new Error(`Faltan datos en el ingrediente ${index + 1}`);
            }
            if (isNaN(ingrediente.cantidad_necesaria)) {
                console.error(`Cantidad inválida en ingrediente ${index + 1}:`, ingrediente);
                throw new Error(`La cantidad del ingrediente ${index + 1} debe ser un número válido`);
            }
        });

        console.log('Enviando petición a:', url);
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify(jsonData)
        });

        const data = await response.json();
        console.log('Respuesta del servidor:', data);
        
        if (!response.ok) {
            console.error('Error del servidor:', {
                status: response.status,
                statusText: response.statusText,
                data: data
            });
            throw new Error(data.error || 'Error al procesar la receta');
        }

        if (data.success) {
            console.log('Receta procesada exitosamente');
            Swal.fire({
                icon: 'success',
                title: '¡Éxito!',
                text: recetaId ? 'Receta actualizada correctamente' : 'Receta creada correctamente'
            }).then(() => {
                // Cerrar el modal antes de recargar
                const modal = bootstrap.Modal.getInstance(document.getElementById(`modalEditarReceta${recetaId}`));
                if (modal) {
                    modal.hide();
                }
                location.reload();
            });
        } else {
            console.error('Error en la respuesta:', data);
            throw new Error(data.error || 'Error al procesar la receta');
        }
    } catch (error) {
        console.error('Error al enviar datos de receta:', error);
        console.error('Datos enviados:', jsonData);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'Error al procesar la receta'
        });
    }
    console.log('=== FIN enviarDatosReceta ===');
}

// Función para validar texto en español
function validarTextoEspanol(texto, permitirNumeros = false) {
    const patronBase = permitirNumeros ? 
        /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,()]*$/ : 
        /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s.,()]*$/;
    return patronBase.test(texto);
}

// Función para limpiar texto
function limpiarTexto(texto, permitirNumeros = false) {
    const patron = permitirNumeros ? 
        /[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,()]/g : 
        /[^a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s.,()]/g;
    return texto.replace(patron, '');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si estamos en la página de recetas
    if (!document.querySelector('.recetas-container')) {
        return;
    }

    // Validar modales al abrirse
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const form = this.querySelector('form[data-form-type="receta"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            const nombre = form.querySelector('input[name="nombre"]');
            const pasos = form.querySelector('textarea[name="pasos"]');

            // Función para validar y actualizar estado del botón
            function validarYActualizarBoton() {
                const nombreValido = validarTextoEspanol(nombre.value, false);
                const pasosValidos = validarTextoEspanol(pasos.value, true);
                
                if (!nombreValido || !pasosValidos) {
                    submitBtn.disabled = true;
                    submitBtn.title = 'Hay caracteres no permitidos en el formulario';
                    
                    // Mostrar indicadores visuales
                    if (!nombreValido) {
                        nombre.classList.add('is-invalid');
                        if (!nombre.nextElementSibling?.classList.contains('invalid-feedback')) {
                            const feedback = document.createElement('div');
                            feedback.className = 'invalid-feedback';
                            feedback.textContent = 'Solo se permiten letras, espacios y signos básicos de puntuación';
                            nombre.parentNode.appendChild(feedback);
                        }
                    } else {
                        nombre.classList.remove('is-invalid');
                    }
                    
                    if (!pasosValidos) {
                        pasos.classList.add('is-invalid');
                        if (!pasos.nextElementSibling?.classList.contains('invalid-feedback')) {
                            const feedback = document.createElement('div');
                            feedback.className = 'invalid-feedback';
                            feedback.textContent = 'Solo se permiten letras, números, espacios y signos básicos de puntuación';
                            pasos.parentNode.appendChild(feedback);
                        }
                    } else {
                        pasos.classList.remove('is-invalid');
                    }
                } else {
                    submitBtn.disabled = false;
                    submitBtn.title = '';
                    nombre.classList.remove('is-invalid');
                    pasos.classList.remove('is-invalid');
                }
            }

            // Validar al abrir el modal
            validarYActualizarBoton();

            // Validar en tiempo real
            nombre.addEventListener('input', validarYActualizarBoton);
            pasos.addEventListener('input', validarYActualizarBoton);

            // Validar al pegar
            [nombre, pasos].forEach(elemento => {
                elemento.addEventListener('paste', function(e) {
                    setTimeout(validarYActualizarBoton, 0);
                });
            });

            // Validar antes de enviar
            form.addEventListener('submit', function(event) {
                event.preventDefault();
                
                const nombreValido = validarTextoEspanol(nombre.value, false);
                const pasosValidos = validarTextoEspanol(pasos.value, true);

                if (!nombreValido || !pasosValidos) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error de validación',
                        text: 'Por favor, corrija los campos marcados en rojo antes de continuar',
                        showConfirmButton: true
                    });
                    return;
                }

                // Si todo está válido, continuar con el envío
                const recetaId = this.dataset.recetaId;
                enviarFormularioReceta(event, recetaId);
            });
        });

        // Limpiar validaciones al cerrar el modal
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form[data-form-type="receta"]');
            if (form) {
                form.reset();
                form.querySelectorAll('.is-invalid').forEach(element => {
                    element.classList.remove('is-invalid');
                });
                form.querySelectorAll('.invalid-feedback').forEach(element => {
                    element.remove();
                });
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.title = '';
                }
            }
        });
    });

    // Función para manejar la validación de campos de texto
    function manejarValidacionTexto(elemento, permitirNumeros) {
        // Prevenir entrada de caracteres especiales
        elemento.addEventListener('keypress', function(e) {
            const char = String.fromCharCode(e.keyCode || e.which);
            const valido = permitirNumeros ? 
                /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,()]$/.test(char) : 
                /^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s.,()]$/.test(char);
            
            if (!valido) {
                e.preventDefault();
                Swal.fire({
                    icon: 'warning',
                    title: 'Caracter no permitido',
                    text: 'Solo se permiten letras, espacios y signos básicos de puntuación',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 2000
                });
            }
        });

        // Limpiar al pegar
        elemento.addEventListener('paste', function(e) {
            e.preventDefault();
            const texto = (e.clipboardData || window.clipboardData).getData('text');
            const textoLimpio = limpiarTexto(texto, permitirNumeros);
            document.execCommand('insertText', false, textoLimpio);
        });

        // Validar al perder el foco
        elemento.addEventListener('blur', function() {
            const textoLimpio = limpiarTexto(this.value, permitirNumeros);
            if (this.value !== textoLimpio) {
                this.value = textoLimpio;
                Swal.fire({
                    icon: 'info',
                    title: 'Texto ajustado',
                    text: 'Se han removido caracteres no permitidos',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 2000
                });
            }
        });
    }

    // Aplicar validación a campos de nombre y pasos
    document.querySelectorAll('input[name="nombre"]').forEach(input => {
        manejarValidacionTexto(input, false);
    });

    document.querySelectorAll('textarea[name="pasos"]').forEach(textarea => {
        manejarValidacionTexto(textarea, true);
    });

    // Cargar insumos disponibles para cada modal
    document.querySelectorAll('[id^="modalEditarReceta"]').forEach(modal => {
        const recetaId = modal.id.replace('modalEditarReceta', '');
        cargarInsumosDisponibles(recetaId);
    });

    // Cargar insumos para el modal de crear
    cargarInsumosDisponibles('crear');

    // Inicializar los selectores de insumos
    document.querySelectorAll('[id^="selector-insumos-"]').forEach(selector => {
        selector.addEventListener('change', function() {
            const recetaId = this.id.split('-')[2];
            actualizarInsumosDisponibles(recetaId);
        });
    });

        // Cargar recetas cuando se carga la página
        cargarRecetas();
    });

function editarReceta(recetaId) {
    console.log('=== INICIO editarReceta ===');
    console.log('ID de receta recibido:', recetaId);
    
    // Verificar que el ID de la receta es válido
    if (!recetaId) {
        console.error('Error: No se proporcionó un ID de receta válido');
        return;
    }
    
    // Obtener los datos de la receta
    console.log('Realizando petición a /recetas/obtener');
    fetch('/recetas/obtener', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({ receta_id: recetaId })
    })
    .then(response => {
        console.log('Estado de la respuesta:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Datos de la receta recibidos:', data);
        
        if (!data.success) {
            throw new Error(data.message || 'Error al obtener la receta');
        }
        
        const receta = data.receta;
        console.log('Datos de la receta procesados:', receta);
        
        // Obtener el modal y sus elementos
        const modalElement = document.getElementById(`modalEditarReceta${recetaId}`);
        if (!modalElement) {
            throw new Error('No se encontró el modal de edición');
        }
        
        // Llenar los campos del formulario
        const nombreInput = modalElement.querySelector('#nombre');
        const gramajeInput = modalElement.querySelector('#gramaje_por_galleta');
        const galletasInput = modalElement.querySelector('#galletas_por_lote');
        const costoInput = modalElement.querySelector('#costo_por_galleta');
        const precioInput = modalElement.querySelector('#precio_venta');
        const pasosInput = modalElement.querySelector('#pasos');
        const ingredientesContainer = modalElement.querySelector('#ingredientes-actuales');
        
        console.log('Elementos del formulario:', {
            nombre: nombreInput,
            gramaje: gramajeInput,
            galletas: galletasInput,
            costo: costoInput,
            precio: precioInput,
            pasos: pasosInput,
            ingredientesContainer: ingredientesContainer
        });
        
        if (nombreInput) nombreInput.value = receta.nombre;
        if (gramajeInput) gramajeInput.value = receta.gramaje_por_galleta;
        if (galletasInput) galletasInput.value = receta.galletas_por_lote;
        if (costoInput) costoInput.value = receta.costo_por_galleta;
        if (precioInput) precioInput.value = receta.precio_venta;
        if (pasosInput) pasosInput.value = receta.pasos;
        
        // Limpiar y llenar el contenedor de ingredientes
        if (ingredientesContainer) {
            ingredientesContainer.innerHTML = '';
            
            // Crear un conjunto para rastrear los ingredientes ya agregados
            const ingredientesAgregados = new Set();
            
            // Agregar los ingredientes actuales
            console.log('Ingredientes actuales:', receta.ingredientes);
            receta.ingredientes.forEach(ingrediente => {
                // Verificar si el ingrediente ya fue agregado
                if (ingredientesAgregados.has(ingrediente.nombre)) {
                    console.log(`Ingrediente duplicado ignorado: ${ingrediente.nombre}`);
                    return;
                }
                
                console.log('Procesando ingrediente:', ingrediente);
                const ingredienteItem = document.createElement('div');
                ingredienteItem.className = 'row mb-3 ingrediente-item';
                ingredienteItem.dataset.ingredienteId = ingrediente.insumo_id;
                ingredienteItem.innerHTML = `
                    <div class="col-md-4">
                        <label>Insumo</label>
                        <input type="text" class="form-control" value="${ingrediente.nombre}" readonly>
                        <input type="hidden" name="insumo_id[]" value="${ingrediente.insumo_id}">
                    </div>
                    <div class="col-md-3">
                        <label>Cantidad</label>
                        <input type="number" step="0.01" name="cantidad_necesaria[]" class="form-control" value="${ingrediente.cantidad}" required>
                    </div>
                    <div class="col-md-3">
                        <label>Unidad</label>
                        <input type="text" name="unidad[]" class="form-control" value="${ingrediente.unidad}" readonly>
                    </div>
                    <div class="col-md-2">
                        <label>&nbsp;</label>
                        <button type="button" class="btn btn-danger btn-sm d-block w-100" onclick="eliminarIngrediente(this, '${recetaId}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                ingredientesContainer.appendChild(ingredienteItem);
                
                // Marcar el ingrediente como agregado
                ingredientesAgregados.add(ingrediente.nombre);
            });
        }
        
        // Obtener los insumos disponibles que no están en la receta
        console.log('Solicitando insumos disponibles...');
        fetch(`/recetas/ingredientes_disponibles/${recetaId}`)
            .then(response => {
                console.log('Estado de la respuesta de insumos:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Insumos disponibles recibidos:', data);
                
                // Actualizar el selector de insumos disponibles
                actualizarInsumosDisponibles(recetaId);
                
                // Mostrar el modal
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            })
            .catch(error => {
                console.error('Error al obtener insumos disponibles:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudieron cargar los insumos disponibles'
                });
            });
    })
    .catch(error => {
        console.error('Error al obtener la receta:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo cargar la receta. Por favor, intente de nuevo.'
        });
    });
}

// Log de finalización del archivo
console.log('=== FIN recetas.js ===');