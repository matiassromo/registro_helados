document.addEventListener('DOMContentLoaded', async function() {
    await cargarSabores();
    actualizarTotal();
    actualizarTablaVentas([]);
});

document.getElementById('vender-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const sabor = document.getElementById('sabor').value;
    const cantidad = document.getElementById('cantidad').value;

    const response = await fetch('/vender', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sabor, cantidad }),
    });
    
    if (response.ok) {
        const data = await response.json();
        alert(data.message);
        document.getElementById('total-venta').textContent = 'Total de la venta: $' + data.total.toFixed(2);
        actualizarTablaVentas(data.ventas); // Actualiza la tabla con la nueva venta
    } else {
        const errorData = await response.json();
        alert('Error: ' + errorData.detail);
    }

    actualizarTotal();
});

async function cargarSabores() {
    const response = await fetch('/sabores');
    const data = await response.json();
    const saborSelect = document.getElementById('sabor');
    saborSelect.innerHTML = ''; 
    for (const sabor of data) {
        const option = document.createElement('option');
        option.value = sabor;
        option.textContent = sabor;
        saborSelect.appendChild(option);
    }
}

async function actualizarTotal() {
    const response = await fetch('/total');
    const data = await response.json();
    document.getElementById('total-ventas').textContent = 'Total de ventas acumulado: $' + data.total_ventas.toFixed(2);
}

async function actualizarTablaVentas() {
    const response = await fetch('/total');
    const data = await response.json();

    const tablaCuerpo = document.getElementById('ventas-tabla-cuerpo');
    tablaCuerpo.innerHTML = '';

    if (data.ventas && data.ventas.length > 0) {
        data.ventas.forEach(venta => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${venta.sabor}</td>
                <td>${venta.cantidad}</td>
                <td>$${venta.precio.toFixed(2)}</td>
                <td>${venta.fecha_hora}</td>
                <td>${venta.stock_restante}</td>
            `;
            tablaCuerpo.appendChild(fila);
        });
    }

    document.getElementById('total-ventas').textContent = `Total de ventas acumulado: $${data.total_ventas.toFixed(2)}`;
}



async function limpiarVentas() {
    const response = await fetch('/limpiar-ventas', { method: 'POST' });
    if (response.ok) {
        const data = await response.json();
        alert(data.message);
        actualizarTablaVentas([]); // Limpiar la tabla en la UI
    } else {
        const errorData = await response.json();
        alert('Error: ' + errorData.detail);
    }
}

async function resetStock() {
    const confirmReset = confirm("¿Estás seguro de que deseas resetear el stock y reiniciar las ventas?");
    if (confirmReset) {
        const response = await fetch('/reset', { method: 'POST' });
        const data = await response.json();
        alert(data.message);

        // Actualiza los totales en la UI
        document.getElementById('total-venta').textContent = 'Total de la venta: $0.00';
        document.getElementById('total-ventas').textContent = 'Total de ventas acumulado: $0.00';

        // Limpia la tabla de ventas
        actualizarTablaVentas([]);
    } else {
        alert("El stock no ha sido reseteado.");
    }
}



