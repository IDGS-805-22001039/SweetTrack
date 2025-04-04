$(document).ready(function() {
    // Inicializar el datepicker
    $('#fecha_corte').datepicker({
        format: 'yyyy-mm-dd',
        autoclose: true,
        language: 'es',
        todayHighlight: true
    });

    // Función para descargar en PDF
    $('#descargar-pdf').on('click', function() {
        // Obtener la fecha seleccionada
        var fecha = $('#fecha_corte').val();
        
        // Crear un nuevo documento PDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Título del informe
        doc.setFontSize(18);
        doc.text('Corte de Ventas - ' + fecha, 14, 20);
        
        // Información general
        doc.setFontSize(12);
        doc.text('Total Ventas: $' + $('.card-text').eq(0).text(), 14, 30);
        doc.text('Número de Ventas: ' + $('.card-text').eq(1).text(), 14, 40);
        doc.text('Total Productos: ' + $('.card-text').eq(2).text(), 14, 50);
        
        // Tabla de ventas
        const table = document.querySelector('.table');
        const rows = table.querySelectorAll('tr');
        
        const tableData = [];
        const headers = [];
        
        // Obtener encabezados
        rows[0].querySelectorAll('th').forEach(header => {
            headers.push(header.textContent);
        });
        
        // Obtener datos
        for (let i = 1; i < rows.length; i++) {
            const rowData = [];
            rows[i].querySelectorAll('td').forEach(cell => {
                rowData.push(cell.textContent);
            });
            tableData.push(rowData);
        }
        
        // Agregar tabla al PDF
        doc.autoTable({
            head: [headers],
            body: tableData,
            startY: 60,
            theme: 'grid',
            styles: { fontSize: 8 },
            headStyles: { fillColor: [66, 139, 202] }
        });
        
        // Guardar el PDF
        doc.save('corte_ventas_' + fecha + '.pdf');
    });

    // Función para descargar en Excel
    $('#descargar-excel').on('click', function() {
        // Obtener la fecha seleccionada
        var fecha = $('#fecha_corte').val();
        
        // Crear un nuevo libro de Excel
        const wb = XLSX.utils.book_new();
        
        // Obtener datos de la tabla
        const table = document.querySelector('.table');
        const rows = table.querySelectorAll('tr');
        
        const tableData = [];
        
        // Obtener encabezados y datos
        rows.forEach(row => {
            const rowData = [];
            row.querySelectorAll('th, td').forEach(cell => {
                rowData.push(cell.textContent);
            });
            tableData.push(rowData);
        });
        
        // Crear una hoja de cálculo
        const ws = XLSX.utils.aoa_to_sheet(tableData);
        
        // Agregar la hoja al libro
        XLSX.utils.book_append_sheet(wb, ws, 'Corte de Ventas');
        
        // Guardar el archivo Excel
        XLSX.writeFile(wb, 'corte_ventas_' + fecha + '.xlsx');
    });
}); 