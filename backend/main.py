from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime

class Helado:
    def __init__(self, sabor, stock=10, precio=0.80):
        self.sabor = sabor
        self.stock = stock
        self.precio = precio
        self.cantidad_vendida = 0

    def reset_stock(self, stock=10):
        self.stock = stock
        self.cantidad_vendida = 0

    def vender(self, cantidad=1):
        if self.stock >= cantidad:
            self.cantidad_vendida += cantidad
            self.stock -= cantidad
            return True, f"Venta registrada: {cantidad} helado(s) de sabor {self.sabor}. Stock restante: {self.stock}", self.precio * cantidad
        else:
            return False, f"No hay suficiente stock de {self.sabor}. Stock actual: {self.stock}", 0.0

    def calcular_total_ventas(self):
        return self.cantidad_vendida * self.precio

class SistemaVentas:
    def __init__(self):
        self.helados = {
            "Naranjilla Hielo": Helado("Naranjilla Hielo"),
            "Mora Hielo": Helado("Mora Hielo"),
            "Coco Hielo": Helado("Coco Hielo"),
            "Tres Sabores Hielo": Helado("Tres Sabores Hielo"),
            "Come y Bebe": Helado("Come y Bebe"),
            "Coco Mora": Helado("Coco Mora"),
            "Maracumango": Helado("Maracumango"),
            "Guanábana Mora": Helado("Guanábana Mora"),
            "Tres Sabores": Helado("Tres Sabores"),
            "Chocolate Coco": Helado("Chocolate Coco"),
            "Chocolate Hielo": Helado("Chocolate Hielo"),
            "Chocovainilla": Helado("Chocovainilla"),
            "Coco Crema": Helado("Coco Crema"),
            "Chicle": Helado("Chicle"),
            "Ron Pasas": Helado("Ron Pasas"),
            "Mora Crema": Helado("Mora Crema"),
            "Mora Chocovainilla": Helado("Mora Chocovainilla"),
            "Chocolate Crema": Helado("Chocolate Crema"),
            "Maracuyá": Helado("Maracuyá"),
            "Queso Crema": Helado("Queso Crema"),
        }
        self.ventas = []

    def registrar_venta(self, sabor, cantidad=1):
        if sabor in self.helados:
            success, message, total = self.helados[sabor].vender(cantidad)
            if success:
                venta = {
                    "sabor": sabor,
                    "cantidad": cantidad,
                    "precio": total,
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d"),
                    "stock_restante": self.helados[sabor].stock
                }
                self.ventas.append(venta)
                return success, message, total
            else:
                return False, message, 0.0
        else:
            return False, f"El sabor {sabor} no está disponible.", 0.0

    def calcular_total_ventas(self):
        return sum(venta["precio"] for venta in self.ventas)

    def mostrar_stock(self):
        return {helado.sabor: helado.stock for helado in self.helados.values()}

    def obtener_sabores_ordenados(self):
        return sorted(self.helados.keys())

    def limpiar_ventas(self):
        self.ventas.clear()
        
    def reset_stock(self):
        for helado in self.helados.values():
            helado.reset_stock()

app = FastAPI()
sistema_ventas = SistemaVentas()

class VentaRequest(BaseModel):
    sabor: str
    cantidad: int

@app.post("/vender")
def vender_helado(venta: VentaRequest):
    success, message, total = sistema_ventas.registrar_venta(venta.sabor, venta.cantidad)
    if success:
        venta_data = {
            "sabor": venta.sabor,
            "cantidad": venta.cantidad,
            "precio": total / venta.cantidad,  # Precio unitario
            "total": total,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d"),  # Aquí se asegura de mostrar solo la fecha
            "stock_restante": sistema_ventas.helados[venta.sabor].stock  # Stock restante
        }
        return {"message": message, "venta": venta_data, "total": total}
    else:
        raise HTTPException(status_code=400, detail=message)



@app.get("/total")
def total_ventas():
    total = sistema_ventas.calcular_total_ventas()
    return {"total_ventas": total, "ventas": sistema_ventas.ventas}


@app.get("/stock")
def stock_helados():
    stock = sistema_ventas.mostrar_stock()
    return stock

@app.get("/sabores")
def sabores():
    return sistema_ventas.obtener_sabores_ordenados()

@app.post("/limpiar-ventas")
def limpiar_ventas():
    sistema_ventas.limpiar_ventas()
    return {"message": "Todas las ventas han sido eliminadas."}

@app.post("/reset")
def reset_stock():
    sistema_ventas.limpiar_ventas()  # Limpia las ventas
    sistema_ventas.reset_stock()  # Resetea el stock de todos los helados
    return {"message": "Todos los stocks han sido reseteados a 10 y las ventas han sido reiniciadas."}


app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_html():
    with open("frontend/index.html") as f:
        return HTMLResponse(f.read())
