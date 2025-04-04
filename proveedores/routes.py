from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from forms import ProveedorForm
from services.proveedor_service import ProveedorService

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/')
@login_required
def index():
    from forms import ProveedorForm
    from services.proveedor_service import ProveedorService
    nombre = request.args.get('nombre')
    estatus = request.args.get('estatus')
    proveedores = ProveedorService.filtrar(nombre, estatus)
    form_crear = ProveedorForm()
    formularios_por_id = {
        p.id: ProveedorForm(obj=p) for p in proveedores
    }

    return render_template(
        'proveedores/intraProveedores.html',
        proveedores=proveedores,
        form=form_crear,
        formularios_por_id=formularios_por_id
    )

@proveedores_bp.route('/crear', methods=['POST'])
@login_required
def crear():
    form = ProveedorForm()
    if form.validate_on_submit():
        ProveedorService.crear(form.data)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"success": True}
        flash("Proveedor creado correctamente", "success")
        return redirect(url_for('proveedores.index'))
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {
                "success": False,
                "errors": form.errors
            }, 400
        flash("Por favor, corrige los errores", "danger")
        return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/editar/<int:id>', methods=['POST'])
@login_required
def editar(id):
    proveedor = ProveedorService.obtener(id)
    form = ProveedorForm(request.form)

    if form.validate_on_submit():
        ProveedorService.editar(id, form.data)
        flash("Proveedor actualizado correctamente", "success")
        return redirect(url_for('proveedores.index'))
    else:
        flash("Corrige los errores del formulario", "danger")
        return render_template('proveedores/editar_proveedor.html', form=form, proveedor=proveedor)

@proveedores_bp.route('/form-editar/<int:id>')
@login_required
def form_editar(id):
    proveedor = ProveedorService.obtener(id)
    form = ProveedorForm(obj=proveedor)
    return render_template("proveedores/_form_editar.html", form=form, proveedor=proveedor)

@proveedores_bp.route('/editar-vista/<int:id>', methods=['GET'])
@login_required
def editar_vista(id):
    proveedor = ProveedorService.obtener(id)
    if not proveedor:
        flash("Proveedor no encontrado", "danger")
        return redirect(url_for('proveedores.index'))

    form = ProveedorForm(obj=proveedor)
    return render_template('proveedores/editar_proveedor.html', form=form, proveedor=proveedor)

@proveedores_bp.route('/baja/<int:id>', methods=['POST'])
@login_required
def baja(id):
    ProveedorService.cambiar_estatus(id)
    flash("Estatus actualizado", "info")
    return redirect(url_for('proveedores.index'))
