from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuarios, TipoUsuario
import forms

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.tipo_usuario_id != 1:  # Si no es cliente (es staff o admin)
            return redirect(url_for('intranet'))
        return redirect(url_for('main.index'))
    
    form = forms.formLogin(request.form)
    if request.method == 'POST' and form.validate():
        correo_o_usuario = form.email.data
        contraseña = form.password.data
        
        usuario = db.session.query(Usuarios).filter(
            (Usuarios.email == correo_o_usuario) | 
            (Usuarios.nombre == correo_o_usuario)
        ).first()
        
        if usuario and check_password_hash(usuario.password_hash, contraseña):
            # Verificar si la cuenta está activa
            if usuario.estatus == 0:
                flash('Tu cuenta ha sido desactivada. Por favor, contacta al administrador si deseas reactivarla.', 'error')
                return redirect(url_for('auth.login'))
                
            login_user(usuario)
            session['clave'] = usuario.clave  # Establecer la clave en la sesión
            session['_user_type'] = usuario.tipo_usuario_id  # Establecer el tipo de usuario
            flash('¡Inicio de sesión exitoso!', 'success')
            
            if usuario.tipo_usuario_id != 1:  # Si no es cliente (es staff o admin)
                return redirect(url_for('intranet'))
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = forms.formRegistro(request.form)
    if request.method == 'POST' and form.validate():
        nombre = form.nombre.data
        email = form.email.data
        password = form.password.data
        tipo_usuario_id = form.tipo_usuario_id.data
        
        # Verificar si el usuario ya existe
        user = Usuarios.query.filter_by(email=email).first()
        if user:
            flash('El correo electrónico ya está registrado.', 'error')
            return redirect(url_for('auth.registro'))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuarios(
            nombre=nombre,
            email=email,
            tipo_usuario_id=tipo_usuario_id
        )
        nuevo_usuario.set_password(password)
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Registro exitoso! Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al registrar el usuario. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('auth.registro'))
    
    tipos_usuario = TipoUsuario.query.all()
    return render_template('auth/registro.html', form=form, tipos_usuario=tipos_usuario)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil')
@login_required
def perfil():
    return render_template('auth/perfil.html')

@auth_bp.route('/eliminar-cuenta', methods=['GET', 'POST'])
@login_required
def eliminar_cuenta():
    form = forms.FlaskForm()  # Crear un formulario vacío para el token CSRF
    
    if request.method == 'POST':
        # Cambiar el estatus del usuario a 0 (inactivo)
        current_user.estatus = 0
        try:
            db.session.commit()
            logout_user()
            flash('Tu cuenta ha sido eliminada exitosamente.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Error al eliminar la cuenta. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('auth.perfil'))
    
    return render_template('auth/eliminar_cuenta.html', form=form)

@auth_bp.route('/detalles', methods=['GET', 'POST'])
@login_required
def detalles():
    form = forms.formCambiarPassword(request.form)
    
    if request.method == 'POST' and form.validate():
        # Verificar la contraseña actual
        if not check_password_hash(current_user.password_hash, form.password_actual.data):
            flash('La contraseña actual es incorrecta.', 'error')
            return redirect(url_for('auth.detalles'))
        
        # Actualizar la contraseña
        current_user.set_password(form.password_nueva.data)
        try:
            db.session.commit()
            flash('Tu contraseña ha sido actualizada exitosamente.', 'success')
            return redirect(url_for('auth.detalles'))
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar la contraseña. Por favor, intente nuevamente.', 'error')
            return redirect(url_for('auth.detalles'))
    
    return render_template('auth/detalles.html', form=form) 