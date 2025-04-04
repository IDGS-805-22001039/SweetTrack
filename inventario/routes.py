from flask import render_template, request, redirect, url_for, flash, jsonify
from . import inventario_bp
from models import (
    db, AdministracionInsumos, TipoInsumo, Proveedores,
    InsumoProveedor, PedidosInsumos, InsumosRecibidos,
    MermaInsumos, Recetas, PedidoGalletas, InformeProduccion,
    EstadoPedido
)
from forms import (
    InsumoForm, ProveedorForm, PedidoInsumoForm,
    InsumoRecibidoForm, MermaInsumoForm, SolicitarLoteForm,
    CategoriaInsumoForm, NuevoInsumoForm, AsignarProveedorInsumoForm,
    NuevoLoteForm
)
from datetime import datetime, date, timedelta
from sqlalchemy import func, case
from . import utils as u
from flask_login import login_required, current_user
import uuid
import re

@inventario_bp.route('/')
def index():
    print("\n=== INICIO index ===")
    # Obtener todos los tipos de insumo con sus totales
    totales_por_tipo = u.calcular_totales_por_tipo()

    # Convertir los resultados a un diccionario para fácil acceso
    totales_dict = {tipo.id: {'nombre': tipo.nombre, 'total': float(tipo.total)} for tipo in totales_por_tipo}
    
    # Obtener todos los insumos con sus tipos
    insumos = u.obtener_insumos()
        
    # Procesar los resultados para el template
    insumos_procesados = [u.procesar_insumo(insumo) for insumo in insumos]

    # Obtener pedidos pendientes
    pedidos_pendientes = u.obtener_pedidos_pendientes()

    # Procesar los pedidos pendientes
    pedidos_procesados = [u.procesar_pedido(pedido) for pedido in pedidos_pendientes]
    
    # Contar pedidos pendientes
    total_pedidos_pendientes = len(pedidos_pendientes)
    
    # Contar mermas del mes actual
    mermas_mes = u.obtener_mermas_mes()
    
    # Obtener la fecha actual para comparaciones en la plantilla
    now = date.today()
    
    return render_template('inventario/index.html',
                         insumos=insumos_procesados,
                         tipos_insumo=totales_por_tipo,
                         totales=totales_dict,
                         pedidos_pendientes=pedidos_procesados,
                         total_pedidos_pendientes=total_pedidos_pendientes,
                         mermas_mes=mermas_mes,
                         now=now)

@inventario_bp.route('/insumos')
def insumos():
    # Obtener todos los insumos con sus tipos
    insumos = u.obtener_insumos()

    # Procesar los resultados para el template
    insumos_procesados = []
    for insumo in insumos:
        # Obtener el proveedor más reciente para este insumo
        insumo_proveedor = InsumoProveedor.query.filter_by(insumo_id=insumo.id).first()
        proveedor = Proveedores.query.get(insumo_proveedor.proveedor_id) if insumo_proveedor else None
        
        insumo_dict = {
            'id': insumo.id,
            'insumo_nombre': insumo.insumo_nombre,
            'tipo_insumo': insumo.TipoInsumo,
            'cantidad_existente': insumo.cantidad_existente,
            'unidad': insumo.unidad,
            'lote_id': insumo.lote_id,
            'fecha_registro': insumo.fecha_registro,
            'fecha_caducidad': insumo.fecha_caducidad,
            'proveedor': proveedor.nombre_empresa if proveedor else 'Sin proveedor'
        }
        insumos_procesados.append(insumo_dict)

    tipos_insumo = TipoInsumo.query.all()
    return render_template('inventario/insumos.html', insumos=insumos_procesados, tipos_insumo=tipos_insumo)

@inventario_bp.route('/insumos/agregar', methods=['GET'])
def agregar_insumo():
    print("\n=== INICIO agregar_insumo ===")
    # Redirigir a la página principal donde está el modal
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/insumos/editar/<int:id>', methods=['GET', 'POST'])
def editar_insumo(id):
    insumo = AdministracionInsumos.query.get_or_404(id)
    form = InsumoForm(obj=insumo)
    if request.method == 'POST' and form.validate():
        insumo.insumo_nombre = form.insumo_nombre.data
        insumo.tipo_insumo_id = form.tipo_insumo_id.data
        insumo.cantidad_existente = form.cantidad_existente.data
        insumo.unidad = form.unidad.data
        insumo.lote_id = form.lote_id.data
        insumo.fecha_registro = form.fecha_registro.data
        insumo.fecha_caducidad = form.fecha_caducidad.data
        db.session.commit()
        flash('Insumo actualizado exitosamente', 'success')
        return redirect(url_for('inventario.insumos'))
    return render_template('inventario/editar_insumo.html', form=form, insumo=insumo)

@inventario_bp.route('/insumos/eliminar/<int:id>')
def eliminar_insumo(id):
    insumo = AdministracionInsumos.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    flash('Insumo eliminado exitosamente', 'success')
    return redirect(url_for('inventario.insumos'))

@inventario_bp.route('/proveedores')
def proveedores():
    proveedores = Proveedores.query.all()
    return render_template('inventario/proveedores.html', proveedores=proveedores)

@inventario_bp.route('/pedidos')
def pedidos():
    # Obtener todos los pedidos con sus relaciones
    pedidos = u.obtener_pedidos_pendientes()

    # Procesar los resultados para el template
    pedidos_procesados = [u.procesar_pedido(pedido) for pedido in pedidos]

    return render_template('inventario/pedidos.html', pedidos=pedidos_procesados)

@inventario_bp.route('/pedidos/agregar', methods=['GET', 'POST'])
def agregar_pedido():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            insumo_id = request.form.get('insumo_id')
            proveedor_id = request.form.get('proveedor_id')
            cantidad_solicitada = request.form.get('cantidad_solicitada')
            fecha_pedido = request.form.get('fecha_pedido')
            estatus = request.form.get('estatus', 'pedido')

            # Validar que todos los campos requeridos estén presentes
            if not all([insumo_id, proveedor_id, cantidad_solicitada, fecha_pedido]):
                return jsonify({
                    'success': False,
                    'message': 'Todos los campos son requeridos'
                }), 400

            # Validar que la cantidad no exceda 100
            try:
                cantidad = int(cantidad_solicitada)
                if cantidad <= 0 or cantidad > 100:
                    return jsonify({
                        'success': False,
                        'message': 'La cantidad debe estar entre 1 y 100'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'La cantidad debe ser un número válido'
                }), 400

            # Validar que la fecha de pedido sea futura
            fecha_pedido = datetime.strptime(fecha_pedido, '%Y-%m-%d').date()
            if fecha_pedido < date.today():
                return jsonify({
                    'success': False,
                    'message': 'La fecha de pedido debe ser futura'
                }), 400

            # Crear el pedido
            pedido = PedidosInsumos(
                insumo_id=insumo_id,
                proveedor_id=proveedor_id,
                cantidad_solicitada=cantidad,
                fecha_pedido=fecha_pedido,
                estatus=estatus
            )

            db.session.add(pedido)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Pedido registrado correctamente'
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al registrar el pedido: {str(e)}'
            }), 500

    return render_template('inventario/agregar_pedido.html')

@inventario_bp.route('/pedidos/recibir/<int:id>', methods=['GET', 'POST'])
def recibir_pedido(id):
    pedido = PedidosInsumos.query.get_or_404(id)
    form = InsumoRecibidoForm()
    if request.method == 'POST' and form.validate():
        # Crear registro de insumo recibido
        insumo_recibido = InsumosRecibidos(
            lote_id=form.lote_id.data,
            fecha_recepcion=form.fecha_recepcion.data,
            fecha_caducidad=form.fecha_caducidad.data,
            cantidad=form.cantidad.data,
            precio_unitario=form.precio_unitario.data,
            insumo_id=pedido.insumo_id,
            proveedor_id=pedido.proveedor_id
        )
        db.session.add(insumo_recibido)
        
        # Actualizar cantidad existente y proveedor del insumo
        insumo = AdministracionInsumos.query.get(pedido.insumo_id)
        insumo.cantidad_existente += form.cantidad.data
        insumo.proveedor_id = pedido.proveedor_id  # Actualizar el proveedor_id
        insumo.lote_id = form.lote_id.data  # Actualizar el lote_id
        insumo.fecha_registro = form.fecha_recepcion.data  # Actualizar la fecha de registro
        insumo.fecha_caducidad = form.fecha_caducidad.data  # Actualizar la fecha de caducidad
        
        # Actualizar estado del pedido
        pedido.estatus = "recibido"
        
        db.session.commit()
        flash('Pedido recibido exitosamente', 'success')
        return redirect(url_for('inventario.pedidos'))
    return render_template('inventario/recibir_pedido.html', form=form, pedido=pedido)

@inventario_bp.route('/agregar_merma', methods=['GET', 'POST'])
def agregar_merma():
    form = MermaInsumoForm()
    if form.validate_on_submit():
        merma = MermaInsumos(
            insumo_id=form.insumo_id.data,
            cantidad_danada=form.cantidad_danada.data,
            motivo_merma=form.motivo_merma.data
        )
        db.session.add(merma)
        db.session.commit()
        flash('Merma registrada exitosamente', 'success')
        return redirect(url_for('inventario.mermas'))
    return render_template('inventario/agregar_merma.html', form=form)

# Rutas API para AJAX
@inventario_bp.route('/insumos/listar')
def listar_insumos():
    try:
        # Obtener todos los tipos de insumo
        tipos_insumo = TipoInsumo.query.all()
        
        # Para cada tipo, obtener sus insumos
        resultado = {}
        for tipo in tipos_insumo:
            insumos = u.obtener_insumos_por_tipo(tipo.id)
            if insumos:  # Solo incluir tipos que tengan insumos
                resultado[tipo.nombre] = insumos
                
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/proveedores/listar')
def listar_proveedores():
    proveedores = Proveedores.query.all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre_empresa,
        'contacto': p.nombre_promotor
    } for p in proveedores])

@inventario_bp.route('/insumo/<string:nombre>')
def get_insumo_unidad(nombre):
    try:
        insumo = AdministracionInsumos.query.filter_by(insumo_nombre=nombre).first()
        if insumo:
            return jsonify({
                'unidad': insumo.unidad
            })
        return jsonify({'error': 'Insumo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/lotes/<int:tipo_insumo_id>')
def get_lotes(tipo_insumo_id):
    try:
        # Obtener todos los lotes del tipo especificado
        lotes = u.obtener_lotes_por_tipo(tipo_insumo_id)
            
        # Formatear los datos de los lotes
        lotes_procesados = []
        for insumo in lotes:
            esta_caducado, dias_restantes = u.calcular_estado_caducidad(insumo.fecha_caducidad)
            
            # Determinar el estado y mensaje basado primero en la cantidad
            if insumo.cantidad_existente <= 0:
                estado = 'terminado'
                mensaje = 'Terminado'
                icono = '<i class="fas fa-check-circle"></i>'
            # Solo si hay cantidad verificamos caducidad
            elif esta_caducado:
                estado = 'caduco'
                mensaje = f'Caducado hace {abs(dias_restantes)} días'
                icono = '<i class="fas fa-exclamation-triangle"></i>'
            elif dias_restantes is not None and dias_restantes <= 30:
                estado = 'proximo_caducar'
                mensaje = f'Caduca en {dias_restantes} días'
                icono = '<i class="fas fa-exclamation-circle"></i>'
            else:
                estado = 'vigente'
                mensaje = 'Vigente'
                icono = '<i class="fas fa-check"></i>'
            
            lote = {
                'insumo_id': insumo.id,
                'lote_id': insumo.lote_id,
                'cantidad': insumo.cantidad_existente,
                'unidad': insumo.unidad,
                'proveedor': insumo.proveedor_nombre if insumo.proveedor_nombre else 'Sin proveedor',
                'fecha_registro': insumo.fecha_registro.strftime('%d/%m/%Y') if insumo.fecha_registro else None,
                'fecha_caducidad': insumo.fecha_caducidad.strftime('%d/%m/%Y') if insumo.fecha_caducidad else None,
                'estado': estado,
                'mensaje': mensaje,
                'icono': icono,
                'esta_caducado': esta_caducado,
                'dias_restantes': dias_restantes
            }
            lotes_procesados.append(lote)
        
        return jsonify({'lotes': lotes_procesados})
    except Exception as e:
        print(f"Error en get_lotes: {str(e)}")
        return jsonify({'error': 'Error al obtener los lotes'}), 500

@inventario_bp.route('/lote/<string:lote_id>')
def get_lote(lote_id):
    try:
        # Obtener el lote específico
        insumo = u.obtener_lote_por_id(lote_id)

        if not insumo:
            return jsonify({
                'error': 'Lote no encontrado'
            }), 404
        
        # Asegurarnos de que la fecha de caducidad sea un objeto date
        fecha_caducidad = insumo.fecha_caducidad
        if isinstance(fecha_caducidad, datetime):
            fecha_caducidad = fecha_caducidad.date()
        
        # Calcular estado de caducidad
        esta_caducado, dias_restantes = u.calcular_estado_caducidad(fecha_caducidad)
        
        # Formatear los datos del lote
        lote = {
            'insumo_id': insumo.id,
            'lote_id': insumo.lote_id,
            'insumo_nombre': insumo.insumo_nombre,
            'tipo_insumo': insumo.tipo_insumo_nombre,
            'cantidad': insumo.cantidad_existente,
            'unidad': insumo.unidad,
            'proveedor': insumo.proveedor_nombre if insumo.proveedor_nombre else 'Sin proveedor',
            'proveedor_contacto': insumo.proveedor_contacto if insumo.proveedor_contacto else 'N/A',
            'proveedor_telefono': insumo.proveedor_telefono if insumo.proveedor_telefono else 'N/A',
            'fecha_registro': insumo.fecha_registro.strftime('%d/%m/%Y') if insumo.fecha_registro else None,
            'fecha_caducidad': fecha_caducidad.strftime('%d/%m/%Y') if fecha_caducidad else None,
            'esta_caducado': esta_caducado,
            'dias_restantes': dias_restantes,
            'modal_attrs': {
                'role': 'dialog',
                'aria-labelledby': 'loteModalLabel',
                'aria-modal': 'true',
                'tabindex': '-1'
            },
            'title_attrs': {
                'id': 'loteModalLabel'
            }
        }
        
        return jsonify({'lote': lote})
    except Exception as e:
        print(f"Error en get_lote: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Error al obtener el lote',
            'detalle': str(e)
        }), 500

@inventario_bp.route('/mermas/agregar', methods=['POST'])
def agregar_merma_ajax():
    print("\n=== INICIO agregar_merma_ajax ===")
    try:
        print("1. Verificando si es una solicitud JSON...")
        if not request.is_json:
            print("ERROR: No es una solicitud JSON")
            return jsonify({
                'success': False,
                'message': 'Se requiere JSON'
            }), 400

        print("2. Obteniendo datos JSON...")
        data = request.get_json()
        print(f"Datos recibidos: {data}")

        print("3. Validando campos requeridos...")
        # Validar datos requeridos
        required_fields = ['insumo_id', 'cantidad_danada', 'motivo_merma']
        for field in required_fields:
            if field not in data:
                print(f"ERROR: Falta campo requerido: {field}")
                return jsonify({
                    'success': False,
                    'message': f'Falta el campo requerido: {field}'
                }), 400

        print("4. Registrando merma...")
        tipo_insumo_id, cantidad_restante = u.registrar_merma(
            data['insumo_id'],
            data['cantidad_danada'],
            data['motivo_merma']
        )

        return jsonify({
            'success': True,
            'message': 'Merma registrada exitosamente',
            'tipo_insumo_id': tipo_insumo_id,
            'cantidad_restante': cantidad_restante
        })
        
    except ValueError as e:
        print(f"ERROR DE VALIDACIÓN: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"ERROR INESPERADO: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback
        print(f"Traceback completo: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error al registrar la merma: {str(e)}'
        }), 500
    finally:
        print("=== FIN agregar_merma_ajax ===\n")

@inventario_bp.route('/insumos/tipo/<int:tipo_id>')
def get_insumos_por_tipo(tipo_id):
    try:
        # Obtener todos los lotes de insumos de este tipo
        lotes = db.session.query(
            AdministracionInsumos.id,
            AdministracionInsumos.insumo_nombre,
            AdministracionInsumos.lote_id,
            AdministracionInsumos.cantidad_existente,
            AdministracionInsumos.unidad,
            AdministracionInsumos.fecha_registro,
            AdministracionInsumos.fecha_caducidad,
            AdministracionInsumos.proveedor_id
        ).filter(
            AdministracionInsumos.tipo_insumo_id == tipo_id
        ).all()
        
        # Agrupar por nombre de insumo
        insumos_dict = {}
        for lote in lotes:
            insumo_nombre = lote[1]
            if insumo_nombre not in insumos_dict:
                insumos_dict[insumo_nombre] = {
                    'nombre': insumo_nombre,
                    'unidad': lote[4],  # Agregamos la unidad aquí
                    'lotes': []
                }
            
            # Obtener el proveedor
            proveedor = None
            if lote[7]:  # Si hay proveedor_id
                proveedor = Proveedores.query.get(lote[7])
            
            insumos_dict[insumo_nombre]['lotes'].append({
                'insumo_id': lote[0],  # Agregamos el insumo_id
                'lote_id': lote[2],
                'cantidad': lote[3],
                'unidad': lote[4],
                'fecha_registro': lote[5].strftime('%Y-%m-%d') if lote[5] else None,
                'fecha_caducidad': lote[6].strftime('%Y-%m-%d') if lote[6] else None,
                'proveedor': proveedor.nombre_empresa if proveedor else 'N/A'
            })
        
        # Obtener proveedores para este tipo de insumo
        proveedores = db.session.query(
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
            AdministracionInsumos.tipo_insumo_id == tipo_id
        ).distinct().all()
        
        # Generar nuevo ID de lote
        nuevo_lote = u.generar_nuevo_lote()
        
        return jsonify({
            'insumos': list(insumos_dict.values()),
            'proveedores': [{
                'id': p[0],
                'nombre': p[1],
                'precio': p[2]
            } for p in proveedores],
            'nuevo_lote': nuevo_lote
        })
        
    except Exception as e:
        print(f"Error al obtener insumos por tipo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/insumos/agregar/ajax', methods=['POST'])
def agregar_insumo_ajax():
    print("\n=== INICIO agregar_insumo_ajax ===")
    print("1. Verificando si es una solicitud JSON...")
    try:
        if not request.is_json:
            print("ERROR: No es una solicitud JSON")
            return jsonify({
                'success': False,
                'error': 'Se requiere JSON'
            }), 400

        print("2. Verificando token CSRF...")
        # Verificar token CSRF
        csrf_token = request.headers.get('X-CSRFToken')
        print(f"Token CSRF recibido: {csrf_token}")
        print(f"Headers completos: {dict(request.headers)}")
        if not csrf_token:
            print("ERROR: Token CSRF no encontrado")
            return jsonify({
                'success': False,
                'error': 'Token CSRF no encontrado'
            }), 400

        print("3. Obteniendo datos JSON...")
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        print("4. Validando campos requeridos...")
        # Validar campos requeridos
        required_fields = ['insumo_nombre', 'tipo_insumo_id', 'cantidad', 'unidad', 'lote_id', 'fecha_caducidad']
        for field in required_fields:
            print(f"Verificando campo: {field}")
            if field not in data:
                print(f"ERROR: Falta campo requerido: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Falta el campo requerido: {field}'
                }), 400

        print("5. Validando cantidad...")
        # Validar que la cantidad no exceda 100 unidades
        try:
            cantidad = float(data['cantidad'])
            print(f"Cantidad recibida: {cantidad}")
            if cantidad <= 0:
                print("ERROR: Cantidad menor o igual a 0")
                return jsonify({
                    'success': False,
                    'error': 'La cantidad debe ser mayor a 0'
                }), 400
            if cantidad > 100:
                print("ERROR: Cantidad excede 100 unidades")
                return jsonify({
                    'success': False,
                    'error': 'La cantidad máxima por lote es de 100 unidades'
                }), 400
        except ValueError as e:
            print(f"ERROR: Cantidad no es un número válido: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'La cantidad debe ser un número válido'
            }), 400

        print("6. Validando fecha de caducidad...")
        # Validar que la fecha de caducidad sea futura
        try:
            fecha_caducidad = datetime.strptime(data['fecha_caducidad'], '%Y-%m-%d').date()
            print(f"Fecha caducidad: {fecha_caducidad}")
            if fecha_caducidad <= date.today():
                print("ERROR: Fecha de caducidad no es futura")
                return jsonify({
                    'success': False,
                    'error': 'La fecha de caducidad debe ser futura'
                }), 400
        except ValueError as e:
            print(f"ERROR: Formato de fecha inválido: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
            }), 400
        
        print("7. Creando nuevo insumo...")
        # Crear el nuevo insumo
        insumo = AdministracionInsumos(
            insumo_nombre=data['insumo_nombre'],
            tipo_insumo_id=data['tipo_insumo_id'],
            cantidad_existente=cantidad,
            unidad=data['unidad'],
            lote_id=data['lote_id'],
            fecha_registro=date.today(),
            fecha_caducidad=fecha_caducidad
        )
        print(f"Insumo a crear: {insumo.__dict__}")
        
        print("8. Agregando insumo a la base de datos...")
        db.session.add(insumo)
        print("9. Confirmando cambios en la base de datos...")
        db.session.commit()
        print("10. Insumo agregado exitosamente")
        
        return jsonify({
            'success': True,
            'message': 'Insumo agregado exitosamente'
        })
    except Exception as e:
        print(f"ERROR INESPERADO: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback
        print(f"Traceback completo: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error al agregar el insumo: {str(e)}'
        }), 500
    finally:
        print("=== FIN agregar_insumo_ajax ===\n")

@inventario_bp.route('/galletas')
@login_required
def galletas():
    recetas = Recetas.query.filter_by(estatus=1).all()
    form = SolicitarLoteForm()
    return render_template('inventario/galletas.html', recetas=recetas, form=form)

@inventario_bp.route('/galletas/solicitar', methods=['POST'])
@login_required
def solicitar_galletas():
    try:
        receta_id = request.form.get('receta_id')
        cantidad = int(request.form.get('cantidad', 100))  # Por defecto 100 galletas

        if not receta_id:
            return jsonify({
                'success': False,
                'message': 'La receta es requerida'
            }), 400

        # Verificar que la receta existe
        receta = Recetas.query.get_or_404(receta_id)
        
        # Verificar si hay suficientes insumos para la receta
        insumos_suficientes, mensaje = verificar_insumos_disponibles_receta(receta_id, cantidad)
        
        if not insumos_suficientes:
            return jsonify({
                'success': False,
                'message': mensaje
            }), 400
        
        # Crear el pedido de galletas
        pedido = PedidoGalletas(
            usuario_id=current_user.id,
            receta_id=receta_id,
            cantidad=cantidad,
            estado_pedido_id=1,
            fecha_pedido=datetime.now(),
            estatus='Pedido'
        )
        
        db.session.add(pedido)
        db.session.commit()
        
        flash(f'Lote de {cantidad} galletas solicitado correctamente', 'success')
        return galletas()

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al registrar el pedido: {str(e)}'
        }), 500

@inventario_bp.route('/atender', methods=['GET', 'POST'])
def atender_pedidos():
    print("\n=== INICIO atender_pedidos ===")
    print(f"Método de la solicitud: {request.method}")
    
    if request.method == 'GET':
        print("1. Procesando solicitud GET")
        # -----------------------------------------
        # MÉTODO GET - OBTENCIÓN DE PEDIDOS PENDIENTES
        # -----------------------------------------
        
        # 1. Consulta para obtener pedidos pendientes con sus relaciones
        pedidos_pendientes = u.obtener_pedidos_pendientes()
        
        # 2. Obtención de proveedores para el modal
        proveedores = Proveedores.query.all()

        # 3. Procesamiento de resultados para el template
        pedidos_procesados = [u.procesar_pedido(pedido) for pedido in pedidos_pendientes]

        # 4. Obtención de fecha actual para el template
        now = date.today()

        # 5. Contar pedidos pendientes
        total_pedidos_pendientes = len(pedidos_pendientes)

        return render_template('inventario/atender.html', 
                             pedidos_pendientes=pedidos_procesados,
                             proveedores=proveedores,
                             now=now,
                             total_pedidos_pendientes=total_pedidos_pendientes)

    elif request.method == 'POST':
        print("1. Procesando solicitud POST")
        try:
            print("2. Verificando token CSRF")
            csrf_token = request.headers.get('X-CSRFToken')
            print(f"Token CSRF recibido: {csrf_token}")
            print(f"Headers completos: {dict(request.headers)}")
            
            if not csrf_token:
                print("ERROR: Token CSRF no encontrado")
                return jsonify({
                    'success': False,
                    'message': 'Token CSRF no encontrado'
                }), 400

            print("3. Obteniendo datos del formulario")
            pedido_id = request.form.get('pedido_id')
            accion = request.form.get('accion')
            print(f"pedido_id: {pedido_id}")
            print(f"accion: {accion}")
            print(f"Datos completos del formulario: {dict(request.form)}")

            if not pedido_id or not accion:
                print("ERROR: Faltan datos requeridos")
                return jsonify({
                    'success': False,
                    'message': 'Faltan datos requeridos'
                }), 400

            print("4. Procesando pedido...")
            cantidad_recibida = request.form.get('cantidad_recibida') if accion == 'recibir' else None
            fecha_caducidad = request.form.get('fecha_caducidad') if accion == 'recibir' else None
            
            if accion == 'atender':
                # Obtener el pedido
                pedido = PedidoGalletas.query.get_or_404(pedido_id)
                
                # Calcular fecha de caducidad (7 semanas desde hoy)
                fecha_produccion = date.today()
                fecha_caducidad = fecha_produccion + timedelta(weeks=7)
                
                # Obtener la cantidad de merma del formulario
                merma = int(request.form.get('merma', 0))
                motivo_merma = request.form.get('motivo_merma', '')
                
                # Calcular cantidad disponible (cantidad producida - merma)
                cantidad_disponible = pedido.cantidad - merma
                
                # Crear registro en informe_produccion
                informe = InformeProduccion(
                    receta_id=pedido.receta_id,
                    cantidad_producida=pedido.cantidad,
                    fecha_produccion=fecha_produccion,
                    caducidad=fecha_caducidad,
                    merma=merma,
                    motivo_merma=motivo_merma,
                    cantidad_disponible=cantidad_disponible
                )
                db.session.add(informe)
                
                # Actualizar estado del pedido a "Atendido" (estado_pedido_id = 2)
                pedido.estado_pedido_id = 2
                pedido.fecha_atencion = datetime.now()
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Pedido atendido correctamente. Se produjeron {pedido.cantidad} galletas con {merma} de merma. Caducidad: {fecha_caducidad.strftime("%d/%m/%Y")}'
                })
            else:
                mensaje = u.procesar_pedido_insumo(pedido_id, accion, cantidad_recibida, fecha_caducidad)
                return jsonify({
                    'success': True,
                    'message': mensaje
                })

        except ValueError as e:
            print(f"ERROR DE VALIDACIÓN: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            print(f"ERROR INESPERADO: {str(e)}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback
            print(f"Traceback completo: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': f'Error al procesar el pedido: {str(e)}'
            }), 500

    print("=== FIN atender_pedidos ===\n")

@inventario_bp.route('/atender/ultimo-lote')
def obtener_ultimo_lote():
    try:
        nuevo_lote = u.generar_nuevo_lote()
        return jsonify({
            'success': True,
            'nuevo_lote': nuevo_lote
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener el último lote: {str(e)}'
        }), 500

@inventario_bp.route('/insumos/caducados')
def get_insumos_caducados():
    try:
        # Obtener todos los insumos caducados
        insumos_caducados = u.obtener_insumos_caducados()
        
        insumos_procesados = []
        for insumo in insumos_caducados:
            esta_caducado, dias_restantes = u.calcular_estado_caducidad(insumo.fecha_caducidad)
            if esta_caducado and insumo.cantidad_existente > 0:
                insumos_procesados.append({
                    'insumo_id': insumo.id,
                    'lote_id': insumo.lote_id,
                    'nombre': insumo.insumo_nombre,
                    'cantidad': insumo.cantidad_existente,
                    'unidad': insumo.unidad,
                    'dias_caducado': abs(dias_restantes),
                    'fecha_caducidad': insumo.fecha_caducidad.strftime('%d/%m/%Y')
                })
        
        return jsonify({'insumos_caducados': insumos_procesados})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/merma/multiple', methods=['POST'])
#@login_required
def registrar_mermas_multiple():
    try:
        data = request.get_json()
        mermas = data.get('mermas', [])
        
        for merma in mermas:
            u.registrar_merma(
                insumo_id=merma['insumo_id'],
                lote_id=merma['lote_id'],
                cantidad=merma['cantidad'],
                motivo="Caducidad del producto"
            )
        
        return jsonify({'message': 'Mermas registradas exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@inventario_bp.route('/gestion-insumos', methods=['GET', 'POST'])
@login_required
def gestion_insumos():
    print("\n=== INICIO gestion_insumos ===")
    try:
        form_insumo = NuevoInsumoForm()
        form_categoria = CategoriaInsumoForm()

        # Cargar las opciones para los SelectField
        # Categorías
        categorias = TipoInsumo.query.order_by(TipoInsumo.nombre).all()
        form_insumo.categoria_id.choices = [(c.id, c.nombre) for c in categorias]
        print(f"Categorías cargadas: {len(form_insumo.categoria_id.choices)}")

        # Proveedores
        proveedores = Proveedores.query.order_by(Proveedores.nombre_empresa).all()
        form_insumo.proveedor_id.choices = [(p.id, p.nombre_empresa) for p in proveedores]
        print(f"Proveedores cargados: {len(form_insumo.proveedor_id.choices)}")

        if request.method == 'POST':
            form_type = request.form.get('form_type')
            print(f"Tipo de formulario: {form_type}")

            if form_type == 'categoria':
                print("Procesando formulario de categoría")
                if form_categoria.validate_on_submit():
                    try:
                        # Validar que el nombre solo contenga letras, espacios y acentos
                        nombre = form_categoria.nombre.data
                        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                            return jsonify({
                                'success': False,
                                'message': 'El nombre solo puede contener letras, espacios y acentos'
                            })

                        # Verificar si ya existe una categoría con ese nombre
                        categoria_existente = TipoInsumo.query.filter(
                            func.lower(TipoInsumo.nombre) == func.lower(nombre)
                        ).first()
                        
                        if categoria_existente:
                            return jsonify({
                                'success': False,
                                'message': 'Ya existe una categoría con ese nombre'
                            })

                        # Crear nueva categoría
                        nueva_categoria = TipoInsumo(
                            nombre=nombre
                        )
                        db.session.add(nueva_categoria)
                        db.session.commit()

                        return jsonify({
                            'success': True,
                            'message': 'Categoría registrada exitosamente',
                            'categoria': nueva_categoria
                        })
                    except Exception as e:
                        db.session.rollback()
                        return jsonify({
                            'success': False,
                            'message': f'Error al registrar la categoría: {str(e)}'
                        }), 500
                else:
                    print(f"Errores de validación: {form_categoria.errors}")
                    return jsonify({
                        'success': False,
                        'message': 'Por favor, completa todos los campos requeridos.'
                    })

            else:
                print("Procesando formulario de insumo")
                if form_insumo.validate_on_submit():
                    try:
                        # Crear nuevo insumo
                        nuevo_insumo = AdministracionInsumos(
                            insumo_nombre=form_insumo.nombre.data,
                            tipo_insumo_id=form_insumo.categoria_id.data,
                            cantidad_existente=form_insumo.cantidad.data,
                            unidad=form_insumo.unidad_medida.data,  # Guardamos la unidad aquí
                            lote_id=request.form.get('lote_id'),
                            fecha_registro=datetime.now(),
                            fecha_caducidad=form_insumo.fecha_caducidad.data
                        )
                        db.session.add(nuevo_insumo)
                        db.session.flush()  # Para obtener el ID del nuevo insumo
                        print(f"Insumo creado: {nuevo_insumo.insumo_nombre}")

                        # Crear relación con proveedor
                        if form_insumo.proveedor_id.data:
                            rel_proveedor = InsumoProveedor(
                                insumo_id=nuevo_insumo.id,
                                proveedor_id=form_insumo.proveedor_id.data,
                                precio=form_insumo.precio.data,
                                unidad=form_insumo.unidad_medida.data  # Agregamos la unidad aquí también
                            )
                            db.session.add(rel_proveedor)
                            print(f"Relación proveedor creada: Proveedor ID {form_insumo.proveedor_id.data}")

                        db.session.commit()
                        print("Transacción completada exitosamente")
                        return jsonify({'success': True, 'message': 'Insumo registrado exitosamente'})
                    
                    except Exception as e:
                        db.session.rollback()
                        print(f"ERROR al guardar en BD: {str(e)}")
                        return jsonify({
                            'success': False, 
                            'message': 'Error al guardar el insumo. Por favor, verifica todos los campos.'
                        })
                else:
                    print(f"Errores de validación: {form_insumo.errors}")
                    return jsonify({
                        'success': False,
                        'message': 'Por favor, completa todos los campos requeridos.'
                    })

        # Obtener insumos existentes para la tabla
        insumos = db.session.query(
            AdministracionInsumos,
            TipoInsumo,
            InsumoProveedor,
            Proveedores
        ).join(
            TipoInsumo,
            AdministracionInsumos.tipo_insumo_id == TipoInsumo.id
        ).outerjoin(
            InsumoProveedor,
            AdministracionInsumos.id == InsumoProveedor.insumo_id
        ).outerjoin(
            Proveedores,
            InsumoProveedor.proveedor_id == Proveedores.id
        ).all()

        return render_template('inventario/gestion_insumos.html',
                             form_insumo=form_insumo,
                             form_categoria=form_categoria,
                             insumos=insumos)

    except Exception as e:
        print(f"Error general: {str(e)}")
        db.session.rollback()
        flash('Error al procesar la solicitud', 'error')
        return redirect(url_for('inventario.index')), 400

@inventario_bp.route('/obtener-siguiente-lote')
@login_required
def obtener_siguiente_lote():
    try:
        # Obtener el último lote registrado
        ultimo_insumo = AdministracionInsumos.query.order_by(
            AdministracionInsumos.lote_id.desc()
        ).first()

        if ultimo_insumo and ultimo_insumo.lote_id:
            # Si existe un lote previo, extraer el número y aumentarlo
            try:
                ultimo_numero = int(ultimo_insumo.lote_id[1:])  # Quitar la 'L' y convertir a número
                siguiente_numero = ultimo_numero + 1
            except ValueError:
                siguiente_numero = 1
        else:
            # Si no hay lotes previos, empezar desde 1
            siguiente_numero = 1

        # Formatear el nuevo número de lote (L001, L002, etc.)
        nuevo_lote = f"L{siguiente_numero:03d}"
        
        print(f"Generando nuevo lote: {nuevo_lote}")  # Debug print
        
        return jsonify({
            'success': True,
            'lote': nuevo_lote
        })
    except Exception as e:
        print(f"Error al generar lote: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'message': str(e)
        })