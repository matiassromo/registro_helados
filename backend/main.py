from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from typing import List, Dict

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
                self.ventas.append({
                    "sabor": sabor,
                    "cantidad": cantidad,
                    "precio_unitario": self.helados[sabor].precio,
                    "total": cantidad * self.helados[sabor].precio,
                    "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "stock_restante": self.helados[sabor].stock
                })
            return success, message, total
        else:
            return False, f"El sabor {sabor} no está disponible.", 0.0

    def calcular_total_ventas(self):
        total = sum(helado.calcular_total_ventas() for helado in self.helados.values())
        return total

    def mostrar_stock(self):
        stock_info = {helado.sabor: helado.stock for helado in self.helados.values()}
        return stock_info

    def guardar_ventas_excel(self, filename="ventas_helados.xlsx"):
        if self.ventas:
            df = pd.DataFrame(self.ventas)
            stock_data = {sabor: helado.stock for sabor, helado in self.helados.items()}
            stock_df = pd.DataFrame(list(stock_data.items()), columns=['Sabor', 'Stock Restante'])
            with pd.ExcelWriter(filename) as writer:
                df.to_excel(writer, sheet_name='Ventas', index=False)
                stock_df.to_excel(writer, sheet_name='Stock', index=False)
            return True, f"Las ventas y el stock han sido guardados en {filename}"
        else:
            return False, "No hay ventas registradas para guardar."

    def reset_stock(self):
        for helado in self.helados.values():
            helado.reset_stock()

    def obtener_sabores_ordenados(self):
        return sorted(self.helados.keys())

app = FastAPI()
sistema_ventas = SistemaVentas()

class VentaRequest(BaseModel):
    sabor: str
    cantidad: int

@app.post("/vender")
def vender_helado(venta: VentaRequest):
    success, message, total = sistema_ventas.registrar_venta(venta.sabor, venta.cantidad)
    if success:
        return {"message": message, "total": total}
    else:
        raise HTTPException(status_code=400, detail=message)

@app.get("/total")
def total_ventas():
    total = sistema_ventas.calcular_total_ventas()
    return {"total_ventas": total}

@app.get("/stock")
def stock_helados():
    stock = sistema_ventas.mostrar_stock()
    return stock

@app.get("/sabores")
def obtener_sabores():
    sabores = sistema_ventas.obtener_sabores_ordenados()
    return {"sabores": sabores}

@app.post("/guardar")
def guardar_ventas():
    success, message = sistema_ventas.guardar_ventas_excel()
    if success:
        return {"message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@app.post("/reset")
def reset_stock():
    sistema_ventas.reset_stock()
    return {"message": "Todos los stocks han sido reseteados a 10."}

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("../frontend/index.html") as f:
        return HTMLResponse(content=f.read())
