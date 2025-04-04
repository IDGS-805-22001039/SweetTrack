var ctx = document.getElementById('utilidadChart').getContext('2d');
    var utilidadChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
            datasets: [{
                label: 'Utilidad Diaria',
                data: [1200, 1900, 3000, 2500, 2000, 3000, 4000],
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    document.addEventListener("DOMContentLoaded", function () {
        const decrementButton = document.querySelector(".contador form:nth-child(1) button");
        const incrementButton = document.querySelector(".contador form:nth-child(3) button");
        const counterValue = document.querySelector(".contador-valor");
    
        let cantidad = parseInt(counterValue.textContent) || 0;
    
        decrementButton.addEventListener("click", function (event) {
            event.preventDefault();
            if (cantidad > 0) {
                cantidad--;
                counterValue.textContent = cantidad;
            }
        });
    
        incrementButton.addEventListener("click", function (event) {
            event.preventDefault();
            cantidad++;
            counterValue.textContent = cantidad;
        });
    });
    
    

// let date = Date.now(); // Fecha actual
// let count = 1; // Contador de unidades
// let tipoVenta = ''; // Tipo de venta seleccionado
// let ticket = []; // Detalles del ticket
// let generarPdf = false; // Variable para el checkbox

// // Propiedades para el cálculo de precios
// let descuento = 0; // Descuento aplicado
// let pago = 0; // Pago realizado por el cliente
// let cambio = 0; // Cambio a devolver al cliente

// // Nueva propiedad para el subtotal
// function getSubtotal() {
//   return ticket.reduce((sum, item) => sum + item.precio, 0);
// }

// // Propiedad para el total con descuento
// function getTotalConDescuento() {
//   return getSubtotal() - descuento;
// }

// // Lista de galletas con ID, precios y las imágenes
// const galletas = [
//   {
//     id: 1,
//     nombre: 'Galleta de Sorpresa Nuez',
//     imagen: '../../../assets/img/galletaNuez.jpg',
//     precioPieza: 10,
//     precioKilo: 150,
//     precioSuelta: 8,
//     stock: 10, // Stock disponible
//   },
//   {
//     id: 2,
//     nombre: 'Galleta de Chispas',
//     imagen: '../../../assets/img/galletaChispas.jpg',
//     precioPieza: 12,
//     precioKilo: 160,
//     precioSuelta: 9,
//     stock: 8, // Stock disponible
//   },
//   {
//     id: 3,
//     nombre: 'Galleta de Vainilla',
//     imagen: '../../../assets/img/galletaVainilla.png',
//     precioPieza: 11,
//     precioKilo: 155,
//     precioSuelta: 8,
//     stock: 12, // Stock disponible
//   },
//   {
//     id: 4,
//     nombre: 'Galleta de Avena',
//     imagen: '../../../assets/img/galletaAvena.jpg',
//     precioPieza: 9,
//     precioKilo: 140,
//     precioSuelta: 7,
//     stock: 7, // Stock disponible
//   },
//   {
//     id: 5,
//     nombre: 'Galleta de Coco',
//     imagen: '../../../assets/img/galletaCoco.jpg',
//     precioPieza: 10,
//     precioKilo: 150,
//     precioSuelta: 8,
//     stock: 10, // Stock disponible
//   },
//   {
//     id: 6,
//     nombre: 'Galleta Integral',
//     imagen: '../../../assets/img/galletaIntegral.jpeg',
//     precioPieza: 13,
//     precioKilo: 170,
//     precioSuelta: 10,
//     stock: 5, // Stock disponible
//   },
//   {
//     id: 7,
//     nombre: 'Galleta Clásica',
//     imagen: '../../../assets/img/galletaClasica.jpg',
//     precioPieza: 10,
//     precioKilo: 150,
//     precioSuelta: 8,
//     stock: 20, // Stock disponible
//   },
//   {
//     id: 8,
//     nombre: 'Galleta de Chocolate',
//     imagen: '../../../assets/img/galletaChocolate.jpg',
//     precioPieza: 14,
//     precioKilo: 180,
//     precioSuelta: 11,
//     stock: 8, // Stock disponible
//   },
//   {
//     id: 9,
//     nombre: 'Galleta de Polvorón',
//     imagen: '../../../assets/img/galletaPolvoron.jpg',
//     precioPieza: 9,
//     precioKilo: 140,
//     precioSuelta: 7,
//     stock: 15, // Stock disponible
//   },
// ];

// // Cambiar el tipo de venta
// function seleccionarTipoVenta(tipo) {
//   tipoVenta = tipo;
// }

// // Incrementa el contador
// function increment() {
//   count++;
// }

// // Decrementa el contador
// function decrement() {
//   if (count > 1) count--;
// }

// // Seleccionar una galleta
// function seleccionarGalleta(galleta) {
//   if (!tipoVenta) {
//     alert('Por favor, seleccione el tipo de venta.');
//     return;
//   }

//   // Verificar si hay suficiente stock
//   if (galleta.stock < count) {
//     alert(`No hay suficiente stock de ${galleta.nombre}. Enviando alerta a producción...`);
//     alertaProduccion(galleta);
//     return;
//   }

//   // Calcula el precio basado en el tipo de venta
//   let precio;
//   switch (tipoVenta) {
//     case 'pieza':
//       precio = galleta.precioPieza * count;
//       break;
//     case 'kilo':
//       precio = galleta.precioKilo * count;
//       break;
//     case 'suelta':
//       precio = galleta.precioSuelta * count;
//       break;
//   }

//   // Agrega al ticket
//   ticket.push({
//     nombre: galleta.nombre,
//     cantidad: count,
//     precio,
//     imagen: galleta.imagen, // Se mantiene la imagen de la galleta
//   });

//   // Restar stock de la galleta
//   galleta.stock -= count;

//   // Reinicia el contador
//   count = 1;
// }

// // Función para alertar a producción
// function alertaProduccion(galleta) {
//   console.log(`Alerta a producción: La galleta ${galleta.nombre} necesita ser producida.`);
//   // Aquí podrías agregar lógica real para notificar a producción, como una llamada a un servicio
// }

// // Calcular descuento y total con descuento
// function calcularTotalConDescuento() {
//   getTotalConDescuento(); // Se recalcula automáticamente por el getter
// }

// // Calcular cambio
// function calcularCambio() {
//   cambio = pago - getTotalConDescuento();
// }

// function registrarVenta() {
//   if (ticket.length === 0) {
//     alert('No hay productos en el ticket para registrar.');
//     return;
//   }

//   // Si se marca el checkbox para generar el PDF
//   if (generarPdf) {
//     generarTicketPDF();
//   }

//   // Limpiar el ticket después de registrar
//   ticket = []; // Limpia el ticket
//   descuento = 0; // Reinicia el descuento
//   pago = 0; // Reinicia el pago
//   cambio = 0; // Reinicia el cambio
//   alert('Venta registrada exitosamente');
// }

// // Función para generar el PDF del ticket
// function generarTicketPDF() {
//   const doc = new jsPDF();

//   // Agregar imagen (Logo en la parte superior centrado)
//   const logo = '../../../assets/img/galleta2.png'; // Asegúrate de tener la ruta correcta de tu imagen
//   doc.addImage(logo, 'PNG', 75, 10, 60, 30); // Ajusta las coordenadas y tamaño del logo

//   // Título del ticket
//   doc.setFontSize(16);
//   doc.setFont('helvetica', 'bold');
//   doc.text('Ticket de Venta', 105, 50, { align: 'center' }); // Título centrado

//   // Fecha
//   doc.setFontSize(10);
//   doc.setFont('helvetica', 'normal');
//   doc.text(`Fecha: ${new Date().toLocaleString()}`, 20, 60);

//   // Línea de separación
//   doc.setLineWidth(0.5);
//   doc.line(20, 65, 190, 65); // Línea horizontal desde (x1, y1) hasta (x2, y2)

//   // Detalles del ticket (Productos)
//   let yPosition = 75; // Inicializa la posición vertical para los productos
//   doc.setFontSize(12);
//   doc.setFont('helvetica', 'normal');
//   doc.text('Productos:', 20, yPosition);

//   ticket.forEach((item) => {
//     yPosition += 8;
//     doc.text(`${item.cantidad} x ${item.nombre}`, 20, yPosition);
//     doc.text(`$${item.precio.toFixed(2)}`, 150, yPosition, {
//       align: 'right',
//     });
//   });

//   // Línea de separación
//   yPosition += 10;
//   doc.line(20, yPosition, 190, yPosition); // Línea horizontal

//   // Subtotal
//   yPosition += 5;
//   doc.text(`Subtotal: $${getSubtotal().toFixed(2)}`, 20, yPosition);

//   // Descuento
//   yPosition += 5;
//   doc.text(`Descuento: $${descuento.toFixed(2)}`, 20, yPosition);

//   // Total con descuento
//   yPosition += 5;
//   doc.text(`Total: $${getTotalConDescuento().toFixed(2)}`, 20, yPosition);

//   // Línea de separación
//   yPosition += 10;
//   doc.line(20, yPosition, 190, yPosition); // Línea horizontal

//   // Pago
//   yPosition += 5;
//   doc.text(`Pago: $${pago.toFixed(2)}`, 20, yPosition);

//   // Cambio
//   yPosition += 5;
//   doc.text(`Cambio: $${cambio.toFixed(2)}`, 20, yPosition);

//   // Línea de separación final
//   yPosition += 10;
//   doc.line(20, yPosition, 190, yPosition); // Línea horizontal

//   // Mensaje de agradecimiento
//   yPosition += 10;
//   doc.setFontSize(10);
//   doc.text('¡Gracias por su compra!', 105, yPosition, { align: 'center' });
//   // Línea de separación final
//   yPosition += 10;
//   doc.line(20, yPosition, 190, yPosition); // Línea horizontal
//   yPosition += 10;
//   doc.setFontSize(10);
//   doc.text('¡De todo corazon Don Galleto!', 105, yPosition, {
//     align: 'center',
//   });
//   // Descargar el PDF
//   doc.save('ticket_venta.pdf');
// }

// // Abrir modal de producción
// function produccion() {
//   modalService.openModal();
// }
