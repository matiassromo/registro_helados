document.addEventListener('DOMContentLoaded', async function() {
    await cargarSabores();
    actualizarTotal();
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
    for (const sabor of data.sabores) {
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

async function guardarVentas() {
    const response = await fetch('/guardar', { method: 'POST' });
    if (response.ok) {
        const data = await response.json();
        alert(data.message);
    } else {
        const errorData = await response.json();
        alert('Error: ' + errorData.detail);
    }
}

async function resetStock() {
    const response = await fetch('/reset', { method: 'POST' });
    const data = await response.json();
    alert(data.message);
    actualizarTotal();
}
