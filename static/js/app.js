// --- Hero slideshow ---
(function() {
    let slides = document.querySelectorAll('.slide');
    let index = 0;
    if (slides.length > 0) {
        setInterval(() => {
            slides[index].classList.remove('active');
            index = (index + 1) % slides.length;
            slides[index].classList.add('active');
        }, 4000);
    }
})();

// --- Cart sidebar toggle ---
function toggleCarrito() {
    const sidebar = document.getElementById('carrito-lateral');
    const overlay = document.getElementById('cart-overlay');
    if (sidebar) sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
}

// --- Add from product detail page ---
function agregarDesdeDetalle(idProducto) {
    agregarAlCarritoAsync(idProducto);
}

// --- Add product to cart (async) ---
function agregarAlCarritoAsync(idProducto) {
    fetch(`/carrito/agregar/${idProducto}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            const contadorCarrito = document.querySelector(".carrito-count");
            if (contadorCarrito) {
                contadorCarrito.innerText = data.cantidad_total_carrito;
            }
            const placeholderVacio = document.getElementById('cart-empty-placeholder');
            if (placeholderVacio || data.cantidad_total_carrito === 1) {
                sessionStorage.setItem('abrir_carrito_al_cargar', 'true');
                location.reload();
                return;
            }
            const txtCantidad = document.getElementById(`cantidad-${idProducto}`);
            if (txtCantidad) {
                txtCantidad.innerText = data.nueva_cantidad;
                const txtSubtotal = document.getElementById(`subtotal-${idProducto}`);
                if (txtSubtotal) {
                    txtSubtotal.innerText = "$" + Number(data.nuevo_subtotal).toLocaleString('es-CO', { minimumFractionDigits: 0 });
                }
                const txtTotal = document.getElementById("cart-total-value");
                if (txtTotal) {
                    txtTotal.innerText = "$" + Number(data.total_carrito).toLocaleString('es-CO', { minimumFractionDigits: 0 });
                }
            } else {
                sessionStorage.setItem('abrir_carrito_al_cargar', 'true');
                location.reload();
            }
        }
    })
    .catch(error => console.error("Error al añadir bolso:", error));
}

// --- Increment/decrement quantity in cart sidebar ---
function alterarCantidad(idProducto, accion) {
    const url = accion === 'sumar' ? `/carrito/agregar/${idProducto}` : `/carrito/restar/${idProducto}`;
    fetch(url, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            const contadorGlobal = document.querySelector(".carrito-count");
            if (contadorGlobal) contadorGlobal.innerText = data.cantidad_total_carrito;

            if (data.producto_removido) {
                const tarjetaProducto = document.getElementById(`item-card-${idProducto}`);
                if (tarjetaProducto) tarjetaProducto.remove();
                if (data.cantidad_total_carrito === 0) {
                    location.reload();
                }
            } else {
                const txtCantidad = document.getElementById(`cantidad-${idProducto}`);
                if (txtCantidad) txtCantidad.innerText = data.nueva_cantidad;
                const txtSubtotal = document.getElementById(`subtotal-${idProducto}`);
                if (txtSubtotal) {
                    txtSubtotal.innerText = "$" + Number(data.nuevo_subtotal).toLocaleString('es-CO', { minimumFractionDigits: 0 });
                }
            }
            const txtTotal = document.getElementById("cart-total-value");
            if (txtTotal) {
                txtTotal.innerText = "$" + Number(data.total_carrito).toLocaleString('es-CO', { minimumFractionDigits: 0 });
            }
        }
    })
    .catch(error => console.error("Error al alterar cantidad en la bolsa:", error));
}

// --- Auto-open cart after reload ---
document.addEventListener("DOMContentLoaded", () => {
    if (sessionStorage.getItem('abrir_carrito_al_cargar') === 'true') {
        sessionStorage.removeItem('abrir_carrito_al_cargar');
        toggleCarrito();
    }
});

// --- Remove product from cart (async) ---
function eliminarDelCarritoAsync(idProducto) {
    fetch(`/carrito/eliminar/${idProducto}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            const contadorGlobal = document.querySelector(".carrito-count");
            if (contadorGlobal) contadorGlobal.innerText = data.cantidad_total_carrito;

            const tarjetaProducto = document.getElementById(`item-card-${idProducto}`);
            if (tarjetaProducto) tarjetaProducto.remove();

            if (data.cantidad_total_carrito === 0) {
                location.reload();
                return;
            }

            const txtTotal = document.getElementById("cart-total-value");
            if (txtTotal) {
                txtTotal.innerText = "$" + Number(data.total_carrito).toLocaleString('es-CO', { minimumFractionDigits: 0 });
            }
            const txtTotalPagina = document.getElementById("cart-page-total");
            if (txtTotalPagina) {
                txtTotalPagina.innerText = "$" + Number(data.total_carrito).toLocaleString('es-CO', { minimumFractionDigits: 0 });
            }
        }
    })
    .catch(error => console.error("Error al eliminar bolso:", error));
}
