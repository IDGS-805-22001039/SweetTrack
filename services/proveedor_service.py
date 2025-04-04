from models import Proveedores, db

class ProveedorService:
    @staticmethod
    def filtrar(busqueda=None, estatus=None):
        query = Proveedores.query
        if busqueda:
            like = f"%{busqueda}%"
            query = query.filter(
                db.or_(
                    Proveedores.nombre_empresa.ilike(like),
                    Proveedores.nombre_promotor.ilike(like),
                    Proveedores.telefono.ilike(like),
                    Proveedores.email.ilike(like),
                    Proveedores.calle.ilike(like),
                    Proveedores.colonia.ilike(like),
                    Proveedores.cp.ilike(like),
                    Proveedores.numero.ilike(like),
                )
            )
        if estatus in ['0', '1']:
            query = query.filter(Proveedores.estatus == int(estatus))
        return query.all()

    @staticmethod
    def crear(data):
        data_limpia = {k: v for k, v in data.items() if k != 'csrf_token'}
        proveedor = Proveedores(**data_limpia, estatus=1)
        db.session.add(proveedor)
        db.session.commit()
        return proveedor

    @staticmethod
    def editar(id, data):
        proveedor = Proveedores.query.get_or_404(id)
        for field, value in data.items():
            if field != 'csrf_token':
                setattr(proveedor, field, value)
        db.session.commit()
        return proveedor
    
    @staticmethod
    def obtener(id):
        return Proveedores.query.get_or_404(id)

    @staticmethod
    def cambiar_estatus(id):
        proveedor = Proveedores.query.get_or_404(id)
        proveedor.estatus = 0 if proveedor.estatus == 1 else 1
        db.session.commit()
        return proveedor