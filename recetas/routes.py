from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models import db, Recetas, AdministracionInsumos, IngredientesReceta, TipoInsumo
from flask_login import login_required
import base64

recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas')

@recetas_bp.route('/')
@login_required
def index():
    try:
        # Obtener todas las recetas activas
        recetas = Recetas.query.filter_by(estatus=1).all()
        
        # Obtener todos los insumos con sus tipos
        insumos = db.session.query(
            AdministracionInsumos
        ).join(
            TipoInsumo
        ).order_by(
            TipoInsumo.nombre,
            AdministracionInsumos.insumo_nombre
        ).all()
        
        # Agrupar insumos por tipo
        tipos_insumos = {}
        for insumo in insumos:
            tipo_nombre = insumo.tipo_insumo.nombre
            if tipo_nombre not in tipos_insumos:
                tipos_insumos[tipo_nombre] = []
            tipos_insumos[tipo_nombre].append({
                'id': insumo.id,
                'nombre': insumo.insumo_nombre,
                'unidad': insumo.unidad
            })
        
        return render_template('recetas/intraRecetas.html',
                             recetas=recetas,
                             tipos_insumos=tipos_insumos)

    except Exception as e:
        print(f"ERROR en index de recetas: {str(e)}")
        return redirect(url_for('main.index'))

@recetas_bp.route('/listar')
@login_required
def listar():
    try:
        recetas = Recetas.query.filter_by(estatus=1).all()
        return jsonify([{
            'id': receta.id,
            'nombre': receta.nombre,
            'gramaje_por_galleta': receta.gramaje_por_galleta,
            'galletas_por_lote': receta.galletas_por_lote,
            'costo_por_galleta': receta.costo_por_galleta,
            'precio_venta': receta.precio_venta
        } for receta in recetas])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recetas_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    try:
        data = request.get_json()
        
        # Crear la receta
        receta = Recetas(
            nombre=data['nombre'],
            gramaje_por_galleta=data['gramaje_por_galleta'],
            galletas_por_lote=data['galletas_por_lote'],
            costo_por_galleta=data['costo_por_galleta'],
            precio_venta=data['precio_venta'],
            pasos=data['pasos'],
            imagen=data.get('imagen'),
            estatus=1
        )
        db.session.add(receta)
        db.session.flush()  # Para obtener el ID de la receta

        # Agregar los ingredientes
        for ingrediente_data in data['ingredientes']:
            # Buscar el insumo por nombre
            insumo = AdministracionInsumos.query.filter_by(
                insumo_nombre=ingrediente_data['insumo_nombre']
            ).first()
            
            if not insumo:
                raise ValueError(f"No se encontró el insumo: {ingrediente_data['insumo_nombre']}")
            
            ingrediente = IngredientesReceta(
                receta_id=receta.id,
                insumo_id=insumo.id,
                cantidad_necesaria=ingrediente_data['cantidad_necesaria'],
                unidad=ingrediente_data['unidad']
            )
            db.session.add(ingrediente)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Receta creada exitosamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@recetas_bp.route('/editar/<int:id>', methods=['PUT'])
@login_required
def editar(id):
    try:
        receta = Recetas.query.get_or_404(id)
        data = request.get_json()

        # Actualizar datos básicos de la receta
        receta.nombre = data['nombre']
        receta.gramaje_por_galleta = data['gramaje_por_galleta']
        receta.galletas_por_lote = data['galletas_por_lote']
        receta.costo_por_galleta = data['costo_por_galleta']
        receta.precio_venta = data['precio_venta']
        receta.pasos = data['pasos']
        if 'imagen' in data:
            receta.imagen = data['imagen']

        # Eliminar ingredientes existentes
        IngredientesReceta.query.filter_by(receta_id=id).delete()

        # Agregar los nuevos ingredientes
        for ingrediente_data in data['ingredientes']:
            # Buscar el insumo por nombre
            insumo = AdministracionInsumos.query.filter_by(
                insumo_nombre=ingrediente_data['insumo_nombre']
            ).first()
            
            if not insumo:
                raise ValueError(f"No se encontró el insumo: {ingrediente_data['insumo_nombre']}")
            
            ingrediente = IngredientesReceta(
                receta_id=id,
                insumo_id=insumo.id,
                cantidad_necesaria=ingrediente_data['cantidad_necesaria'],
                unidad=ingrediente_data['unidad']
            )
            db.session.add(ingrediente)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Receta actualizada exitosamente'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@recetas_bp.route('/eliminar/<int:id>', methods=['DELETE'])
@login_required
def eliminar(id):
    try:
        receta = Recetas.query.get_or_404(id)
        receta.estatus = 0
        db.session.commit()
        return jsonify({'success': True, 'message': 'Receta eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@recetas_bp.route('/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado():
    try:
        data = request.get_json()
        receta = Recetas.query.get_or_404(data['receta_id'])
        receta.estatus = data['estado']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Estado de receta actualizado exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@recetas_bp.route('/obtener', methods=['POST'])
@login_required
def obtener_receta():
    try:
        data = request.get_json()
        receta = Recetas.query.get_or_404(data['receta_id'])
        
        ingredientes = [{
            'insumo_nombre': i.insumo.insumo_nombre,
            'cantidad': i.cantidad_necesaria,
            'unidad': i.unidad
        } for i in receta.ingredientes]
        
        return jsonify({
            'success': True,
            'receta': {
                'id': receta.id,
                'nombre': receta.nombre,
                'gramaje_por_galleta': receta.gramaje_por_galleta,
                'galletas_por_lote': receta.galletas_por_lote,
                'costo_por_galleta': receta.costo_por_galleta,
                'precio_venta': receta.precio_venta,
                'pasos': receta.pasos,
                'imagen': receta.imagen,
                'ingredientes': ingredientes
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@recetas_bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja(id):
    try:
        receta = Recetas.query.get_or_404(id)
        receta.estatus = 0 if receta.estatus == 1 else 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Estado de receta actualizado correctamente',
            'redirect_url': url_for('recetas.index')  # URL para redirección
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el estado: {str(e)}'
        }), 500

@recetas_bp.route('/eliminar_ingrediente/<int:receta_id>/<int:insumo_id>', methods=['DELETE'])
@login_required
def eliminar_ingrediente(receta_id, insumo_id):
    try:
        # Buscar el ingrediente específico
        ingrediente = IngredientesReceta.query.filter_by(
            receta_id=receta_id,
            insumo_id=insumo_id
        ).first()
        
        if not ingrediente:
            return jsonify({
                'status': 'error',
                'message': 'Ingrediente no encontrado'
            }), 404
            
        # Eliminar el ingrediente
        db.session.delete(ingrediente)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Ingrediente eliminado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@recetas_bp.route('/ingredientes_disponibles/<int:receta_id>', methods=['GET'])
@login_required
def ingredientes_disponibles(receta_id):
    try:
        # Obtener la receta
        receta = Recetas.query.get_or_404(receta_id)
        
        # Obtener los IDs de los ingredientes que ya están en la receta
        ingredientes_actuales = [i.insumo_id for i in receta.ingredientes]
        
        # Obtener todos los insumos disponibles
        insumos_disponibles = db.session.query(
            AdministracionInsumos, TipoInsumo
        ).join(
            TipoInsumo
        ).order_by(
            TipoInsumo.nombre,
            AdministracionInsumos.insumo_nombre
        ).all()
        
        # Agrupar insumos por tipo y evitar duplicados
        tipos_insumos = {}
        insumos_agregados = set()  # Para rastrear insumos ya agregados
        
        # Primero agregar los insumos que ya están en la receta
        for ingrediente in receta.ingredientes:
            insumo = ingrediente.insumo
            tipo_nombre = insumo.tipo_insumo.nombre
            if tipo_nombre not in tipos_insumos:
                tipos_insumos[tipo_nombre] = []
            
            if insumo.insumo_nombre not in insumos_agregados:
                tipos_insumos[tipo_nombre].append({
                    'id': insumo.id,
                    'nombre': insumo.insumo_nombre,
                    'unidad': insumo.unidad,
                    'cantidad_disponible': insumo.cantidad_existente,
                    'en_receta': True,
                    'cantidad_actual': ingrediente.cantidad_necesaria
                })
                insumos_agregados.add(insumo.insumo_nombre)
        
        # Luego agregar los insumos que no están en la receta
        for insumo, tipo in insumos_disponibles:
            tipo_nombre = tipo.nombre
            if tipo_nombre not in tipos_insumos:
                tipos_insumos[tipo_nombre] = []
            
            if insumo.insumo_nombre not in insumos_agregados:
                tipos_insumos[tipo_nombre].append({
                    'id': insumo.id,
                    'nombre': insumo.insumo_nombre,
                    'unidad': insumo.unidad,
                    'cantidad_disponible': insumo.cantidad_existente,
                    'en_receta': False,
                    'cantidad_actual': 0
                })
                insumos_agregados.add(insumo.insumo_nombre)
        
        return jsonify({
            'success': True,
            'tipos_insumos': tipos_insumos
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

        print(f"Error al crear receta: {str(e)}")