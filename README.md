"# La Galletopedia" 

### Agregado tipo de venta en el modelo `DetalleVenta`

Se ha modificado el modelo `DetalleVenta` para incluir el campo `tipo_venta`, el cual ahora es un `ENUM` que permite especificar el tipo de venta. Los valores posibles para `tipo_venta` son:

- **Unidad**: Para ventas por unidad.
- **Gramaje**: Para ventas por peso (gramos).
- **Monto**: Para ventas por monto de dinero.

### Detalles del cambio

1. **Base de datos**: Se agregó un campo `tipo_venta` como `ENUM` en la tabla `DetalleVenta` para reflejar los tres tipos de venta.
2. **Modelo de SQLAlchemy**: 
   - Se añadió un campo `tipo_venta` con la definición del `ENUM` correspondiente.
   - Se actualizó la relación de `DetalleVenta` con la tabla `ModuloVentas`.
   
### modelo `DetalleVenta` actualizado:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Enum  


class TipoVenta(PyEnum):
    Unidad = "Unidad"
    Gramaje = "Gramaje"
    Monto = "Monto"

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    tipo_venta = db.Column(Enum(TipoVenta), nullable=False)  <-- aqui lo gregre papipto>
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float)
    venta_id = db.Column(db.Integer, db.ForeignKey('modulo_ventas.id'), nullable=False)

    venta = db.relationship('ModuloVentas', backref='detalles_venta')

    NO ESTA DEL TODO TERMINADO EL PUNTO DE VENTA, FALTA QUE REGISTRE LA VENTA#   S w e e t T r a c k  
 