from datetime import datetime, date
from sqlalchemy import func, case
from models import (
    db, AdministracionInsumos, TipoInsumo, Proveedores,
    InsumoProveedor, PedidosInsumos, InsumosRecibidos,
    MermaInsumos, Recetas, PedidoGalletas, InformeProduccion
)

def calcular_estado_caducidad(fecha_caducidad):
    """
    Calcula si un insumo está caducado y los días restantes.
    
    Args:
        fecha_caducidad (date): Fecha de caducidad del insumo
        
    Returns:
        tuple: (esta_caducado, dias_restantes)
        - esta_caducado: True si está caducado, False si no
        - dias_restantes: número de días restantes (negativo si está caduco)
    """
    if not fecha_caducidad:
        print("No hay fecha de caducidad")
        return False, None

    try:
        # Asegurarnos de que trabajamos con objetos date
        if isinstance(fecha_caducidad, str):
            fecha_caducidad = datetime.strptime(fecha_caducidad, "%Y-%m-%d").date()
        elif isinstance(fecha_caducidad, datetime):
            fecha_caducidad = fecha_caducidad.date()
            
        # Usar la fecha actual del sistema
        fecha_actual = date.today()
        
        # Calcular la diferencia de días
        diferencia_dias = (fecha_caducidad - fecha_actual).days
        
        # Si la diferencia es negativa, está caducado
        return diferencia_dias < 0, diferencia_dias
        
    except Exception as e:
        print(f"Error al calcular caducidad: {str(e)}")
        return False, None

def calcular_totales_por_tipo():
    """
    Calcula los totales de cantidad existente por tipo de insumo
    """
    totales = db.session.query(
        TipoInsumo.id,
        TipoInsumo.nombre,
        func.coalesce(func.sum(AdministracionInsumos.cantidad_existente), 0).label('total')
    ).outerjoin(
        AdministracionInsumos,
        TipoInsumo.id == AdministracionInsumos.tipo_insumo_id
    ).group_by(
        TipoInsumo.id,
        TipoInsumo.nombre
    ).all()

    return totales

def generar_nuevo_lote():
    """
    Genera un nuevo ID de lote basado en el último lote registrado.
    
    Returns:
        str: Nuevo ID de lote (ejemplo: "L001")
    """
    ultimo_lote = db.session.query(
        AdministracionInsumos.lote_id
    ).order_by(
        AdministracionInsumos.lote_id.desc()
    ).first()

    if ultimo_lote and ultimo_lote.lote_id:
        ultimo_numero = int(ultimo_lote.lote_id[1:])
        nuevo_lote = f"L{(ultimo_numero + 1):03d}"
    else:
        nuevo_lote = "L001"

    return nuevo_lote

def procesar_insumo(insumo):
    """
    Procesa un insumo para obtener su estado y mensajes relacionados.
    
    Args:
        insumo: Objeto AdministracionInsumos
        
    Returns:
        dict: Diccionario con la información procesada del insumo
    """
    esta_caducado, dias_restantes = calcular_estado_caducidad(insumo.fecha_caducidad)
    
    if esta_caducado:
        estado = 'caduco'
        mensaje = f'Caducado hace {abs(dias_restantes)} días'
    elif dias_restantes is not None and dias_restantes <= 30:
        estado = 'proximo_caducar'
        mensaje = f'Caduca en {dias_restantes} días'
    else:
        estado = 'vigente'
        mensaje = f'Vigente, caduca en {dias_restantes} días' if dias_restantes is not None else 'Sin fecha de caducidad'
    
    # Obtener el proveedor más reciente para este insumo
    insumo_proveedor = InsumoProveedor.query.filter_by(insumo_id=insumo.id).first()
    proveedor = Proveedores.query.get(insumo_proveedor.proveedor_id) if insumo_proveedor else None
    
    return {
        'id': insumo.id,
        'insumo_nombre': insumo.insumo_nombre,
        'tipo_insumo_nombre': insumo.tipo_insumo.nombre if insumo.tipo_insumo else 'Sin tipo',
        'tipo_insumo_id': insumo.tipo_insumo_id,
        'cantidad_existente': insumo.cantidad_existente,
        'unidad': insumo.unidad,
        'lote_id': insumo.lote_id,
        'fecha_registro': insumo.fecha_registro,
        'fecha_caducidad': insumo.fecha_caducidad,
        'estado_caducidad': estado,
        'dias_restantes': dias_restantes,
        'mensaje_caducidad': mensaje,
        'proveedor': proveedor.nombre_empresa if proveedor else 'Sin proveedor'
    }

def procesar_pedido(pedido):
    """
    Procesa un pedido para obtener su información formateada.
    
    Args:
        pedido: Objeto PedidosInsumos o PedidoGalletas
        
    Returns:
        dict: Diccionario con la información procesada del pedido
    """
    if isinstance(pedido, PedidosInsumos):
        return {
            'id': pedido.id,
            'insumo_nombre': pedido.insumo.insumo_nombre,
            'tipo_insumo': pedido.insumo.tipo_insumo.nombre,
            'cantidad_solicitada': pedido.cantidad_solicitada,
            'unidad': pedido.insumo.unidad,
            'proveedor': pedido.proveedor.nombre_empresa,
            'fecha_solicitud': pedido.fecha_pedido,
            'estatus': pedido.estatus
        }
    elif isinstance(pedido, PedidoGalletas):
        return {
            'id': pedido.id,
            'receta_nombre': pedido.receta.nombre,
            'cantidad': pedido.cantidad,
            'estado': pedido.estado_pedido.nombre,
            'fecha_pedido': pedido.fecha_pedido,
            'estatus': pedido.estatus
        }
    else:
        raise ValueError(f'Tipo de pedido no soportado: {type(pedido)}')

def procesar_receta(receta):
    """
    Procesa una receta para obtener su información formateada.
    
    Args:
        receta: Objeto Recetas
        
    Returns:
        dict: Diccionario con la información procesada de la receta
    """
    # Calcular el stock disponible
    stock_disponible = receta.galletas_por_lote - receta.pedidos_pendientes
    
    # Obtener la merma más reciente
    merma_reciente = db.session.query(
        InformeProduccion.merma,
        InformeProduccion.fecha_produccion
    ).filter(
        InformeProduccion.receta_id == receta.id
    ).order_by(
        InformeProduccion.fecha_produccion.desc()
    ).first()

    # Obtener la caducidad más próxima de los lotes disponibles
    fecha_actual = date.today()
    caducidad_proxima = db.session.query(
        InformeProduccion.caducidad,
        InformeProduccion.cantidad_disponible
    ).filter(
        InformeProduccion.receta_id == receta.id,
        InformeProduccion.cantidad_disponible > 0
    ).order_by(
        InformeProduccion.caducidad.asc()
    ).first()

    # Si no hay caducidad próxima, buscar la más reciente
    if not caducidad_proxima:
        caducidad_proxima = db.session.query(
            InformeProduccion.caducidad,
            InformeProduccion.cantidad_disponible
        ).filter(
            InformeProduccion.receta_id == receta.id,
            InformeProduccion.cantidad_disponible > 0
        ).order_by(
            InformeProduccion.caducidad.desc()
        ).first()

    # Procesar fecha de caducidad
    fecha_caducidad = None
    esta_caducada = False
    if caducidad_proxima and caducidad_proxima.caducidad:
        try:
            if isinstance(caducidad_proxima.caducidad, str):
                fecha_caducidad = datetime.strptime(caducidad_proxima.caducidad, '%Y-%m-%d').date()
            elif isinstance(caducidad_proxima.caducidad, datetime):
                fecha_caducidad = caducidad_proxima.caducidad.date()
            elif isinstance(caducidad_proxima.caducidad, date):
                fecha_caducidad = caducidad_proxima.caducidad
            
            # Verificar si está caducada
            esta_caducada = fecha_caducidad < fecha_actual
        except Exception as e:
            print(f"Error al procesar fecha de caducidad: {str(e)}")

    # Calcular el porcentaje de stock
    porcentaje_stock = (stock_disponible / receta.galletas_por_lote) * 100 if receta.galletas_por_lote > 0 else 0

    return {
        'id': receta.id,
        'nombre': receta.nombre,
        'gramaje': receta.gramaje_por_galleta,
        'galletas_por_lote': receta.galletas_por_lote,
        'costo': receta.costo_por_galleta,
        'precio': receta.precio_venta,
        'imagen': receta.imagen,
        'estatus': receta.estatus,
        'stock_disponible': max(0, stock_disponible),
        'porcentaje_stock': porcentaje_stock,
        'merma_reciente': merma_reciente.merma if merma_reciente else 0,
        'fecha_merma': merma_reciente.fecha_produccion.strftime('%Y-%m-%d') if merma_reciente else None,
        'caducidad_proxima': fecha_caducidad.strftime('%Y-%m-%d') if fecha_caducidad else None,
        'esta_caducada': esta_caducada
    }

def obtener_insumos():
    """
    Obtiene todos los insumos con sus tipos
    """
    return db.session.query(
        AdministracionInsumos
    ).join(
        TipoInsumo,
        AdministracionInsumos.tipo_insumo_id == TipoInsumo.id
    ).all()

def obtener_pedidos_pendientes():
    """
    Obtiene todos los pedidos pendientes con sus relaciones
    """
    return db.session.query(PedidosInsumos).join(
        AdministracionInsumos,
        PedidosInsumos.insumo_id == AdministracionInsumos.id
    ).join(
        Proveedores,
        PedidosInsumos.proveedor_id == Proveedores.id
    ).join(
        TipoInsumo,
        AdministracionInsumos.tipo_insumo_id == TipoInsumo.id
    ).filter(
        PedidosInsumos.estatus == 'pedido'
    ).all()

def obtener_mermas_mes():
    """
    Obtiene el conteo de mermas del mes actual
    """
    fecha_actual = datetime.now()
    primer_dia_mes = fecha_actual.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return MermaInsumos.query.filter(
        MermaInsumos.id >= primer_dia_mes
    ).count()

def obtener_insumos_por_tipo(tipo_insumo_id):
    """
    Obtiene los insumos existentes para un tipo específico, agrupados por nombre
    y sumando sus cantidades existentes
    """
    insumos = db.session.query(
        AdministracionInsumos.insumo_nombre,
        AdministracionInsumos.unidad,
        func.sum(AdministracionInsumos.cantidad_existente).label('cantidad_total')
    ).filter(
        AdministracionInsumos.tipo_insumo_id == tipo_insumo_id
    ).group_by(
        AdministracionInsumos.insumo_nombre,
        AdministracionInsumos.unidad
    ).all()
    
    return [{
        'nombre': insumo[0],
        'unidad': insumo[1],
        'cantidad': float(insumo[2] or 0)
    } for insumo in insumos]

def obtener_proveedores_por_tipo(tipo_insumo_id):
    """
    Obtiene los proveedores que ofrecen un tipo específico de insumo
    """
    return db.session.query(
        Proveedores.id,
        Proveedores.nombre_empresa,
        InsumoProveedor.precio
    ).join(
        InsumoProveedor,
        Proveedores.id == InsumoProveedor.proveedor_id
    ).join(
        AdministracionInsumos,
        InsumoProveedor.insumo_id == AdministracionInsumos.id
    ).filter(
        AdministracionInsumos.tipo_insumo_id == tipo_insumo_id
    ).distinct().all()

def obtener_lotes_por_tipo(tipo_insumo_id):
    """
    Obtiene todos los lotes de un tipo específico de insumo
    """
    return db.session.query(
        AdministracionInsumos.id,
        AdministracionInsumos.insumo_nombre,
        AdministracionInsumos.cantidad_existente,
        AdministracionInsumos.unidad,
        AdministracionInsumos.lote_id,
        AdministracionInsumos.fecha_registro,
        AdministracionInsumos.fecha_caducidad,
        Proveedores.nombre_empresa.label('proveedor_nombre')
    ).join(
        InsumoProveedor,
        AdministracionInsumos.id == InsumoProveedor.insumo_id
    ).join(
        Proveedores,
        InsumoProveedor.proveedor_id == Proveedores.id
    ).filter(
        AdministracionInsumos.tipo_insumo_id == tipo_insumo_id
    ).all()

def obtener_lote_por_id(lote_id):
    """
    Obtiene un lote específico por su ID
    """
    return db.session.query(
        AdministracionInsumos.id,
        AdministracionInsumos.insumo_nombre,
        AdministracionInsumos.cantidad_existente,
        AdministracionInsumos.unidad,
        AdministracionInsumos.lote_id,
        AdministracionInsumos.fecha_registro,
        AdministracionInsumos.fecha_caducidad,
        TipoInsumo.nombre.label('tipo_insumo_nombre'),
        Proveedores.nombre_empresa.label('proveedor_nombre'),
        Proveedores.nombre_promotor.label('proveedor_contacto'),
        Proveedores.telefono.label('proveedor_telefono')
    ).join(
        TipoInsumo,
        AdministracionInsumos.tipo_insumo_id == TipoInsumo.id
    ).outerjoin(
        InsumoProveedor,
        AdministracionInsumos.id == InsumoProveedor.insumo_id
    ).outerjoin(
        Proveedores,
        InsumoProveedor.proveedor_id == Proveedores.id
    ).filter(
        AdministracionInsumos.lote_id == lote_id
    ).first()

def obtener_recetas():
    """
    Obtiene todas las recetas con su información
    """
    return db.session.query(
        Recetas.id,
        Recetas.nombre,
        Recetas.gramaje_por_galleta,
        Recetas.galletas_por_lote,
        Recetas.costo_por_galleta,
        Recetas.precio_venta,
        Recetas.imagen,
        Recetas.estatus,
        func.count(case((PedidoGalletas.estatus == 'pendiente', 1))).label('pedidos_pendientes')
    ).outerjoin(
        PedidoGalletas,
        Recetas.id == PedidoGalletas.receta_id
    ).group_by(
        Recetas.id,
        Recetas.nombre,
        Recetas.gramaje_por_galleta,
        Recetas.galletas_por_lote,
        Recetas.costo_por_galleta,
        Recetas.precio_venta,
        Recetas.imagen,
        Recetas.estatus
    ).all()

def crear_pedido_galletas(receta_id, usuario_id):
    """
    Crea un nuevo pedido de galletas
    """
    pedido = PedidoGalletas(
        usuario_id=usuario_id,
        receta_id=receta_id,
        cantidad=100,
        fecha_pedido=datetime.now(),
        estado_pedido_id=1,
        estatus='pendiente'
    )
    db.session.add(pedido)
    db.session.commit()
    return pedido

def procesar_pedido_insumo(pedido_id, accion, cantidad_recibida=None, fecha_caducidad=None):
    """
    Procesa un pedido de insumo (recibir o cancelar)
    """
    pedido = PedidosInsumos.query.get_or_404(pedido_id)
    
    if accion == 'recibir':
        if not cantidad_recibida or not fecha_caducidad:
            raise ValueError('Faltan datos de recepción')
            
        cantidad_recibida = float(cantidad_recibida)
        if cantidad_recibida <= 0:
            raise ValueError('La cantidad recibida debe ser mayor a 0')
            
        fecha_caducidad = datetime.strptime(fecha_caducidad, '%Y-%m-%d').date()
        if fecha_caducidad <= date.today():
            raise ValueError('La fecha de caducidad debe ser futura')
            
        nuevo_lote = generar_nuevo_lote()
        
        insumo_recibido = InsumosRecibidos(
            lote_id=nuevo_lote,
            fecha_recepcion=date.today(),
            fecha_caducidad=fecha_caducidad,
            cantidad=cantidad_recibida,
            precio_unitario=0,
            insumo_id=pedido.insumo_id,
            proveedor_id=pedido.proveedor_id
        )
        db.session.add(insumo_recibido)
        
        insumo = AdministracionInsumos.query.get(pedido.insumo_id)
        insumo.cantidad_existente += cantidad_recibida
        insumo.lote_id = nuevo_lote
        insumo.fecha_registro = date.today()
        insumo.fecha_caducidad = fecha_caducidad
        
        pedido.estatus = "recibido"
        mensaje = 'Pedido recibido exitosamente'
        
    elif accion == 'cancelar':
        pedido.estatus = "cancelado"
        mensaje = 'Pedido cancelado exitosamente'
        
    else:
        raise ValueError('Acción no válida')
        
    db.session.commit()
    return mensaje

def registrar_merma(insumo_id, cantidad_danada, motivo_merma):
    """
    Registra una nueva merma
    """
    insumo = AdministracionInsumos.query.get_or_404(insumo_id)
    
    try:
        cantidad_merma = float(cantidad_danada)
        if cantidad_merma <= 0:
            raise ValueError('La cantidad a mermar debe ser mayor a 0')
        if cantidad_merma > insumo.cantidad_existente:
            raise ValueError('La cantidad a mermar no puede ser mayor a la disponible')
    except ValueError as e:
        raise ValueError('La cantidad debe ser un número válido')
        
    merma = MermaInsumos(
        insumo_id=insumo.id,
        cantidad_danada=cantidad_merma,
        motivo_merma=motivo_merma
    )
    db.session.add(merma)
    
    insumo.cantidad_existente -= cantidad_merma
    
    # Si la cantidad llega a 0, marcar como terminado
    if insumo.cantidad_existente <= 0:
        insumo.estado = 'terminado'
    
    db.session.commit()
    
    return insumo.tipo_insumo_id, insumo.cantidad_existente 