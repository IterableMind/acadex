"""
Define routes for adminitrative roles only.
"""

from flask import render_template, url_for, flash, redirect, current_app, request
from . import admin_bp
from .forms import SchoolInfoForm, SearchStudent, TeacherForm, UpdateForm, StreamForm, GradeForm 
from ..models import db, SchoolInfo, Teacher, User, Grade, Stream
from ..utils.utils import generate_username
from ..utils.image_processor import preprocess_image as img_editor 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from werkzeug.exceptions import InternalServerError
from flask_login import login_required, current_user, logout_user


ACTIVE = 'link--active'

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
  form = SearchStudent()

  if form.validate_on_submit():
     return 'SEARCH STUDENT SUBMITTED SUCCESSFULLY'

  return render_template(
    'dashboard.html',
    form=form,
    d_active=ACTIVE, 
    title='Admin'
  )


@admin_bp.route('/school-info', methods=['GET', 'POST'])
@login_required
def school_info():
    form = SchoolInfoForm()
    
    if form.validate_on_submit():
      try: 
          school = SchoolInfo(
              name=form.name.data.upper(),
              address=form.address.data,
              registration_number=form.registration_number.data or None,
              contact_email=form.contact_email.data or None,
              contact_phone=form.contact_phone.data
          )

          db.session.add(school)
          db.session.commit()

          existing_school = SchoolInfo.query.first() 
          if existing_school and existing_school.id != school.id:   
              db.session.delete(existing_school)
              db.session.commit()

          flash('School information updated successfully!', 'success')
          return redirect(url_for('admin_bp.school_info'))
      
      except Exception as e:
          db.session.rollback()
          flash('An unexpected error occurred. Please try again later.', 'error')
          current_app.logger.error(f"Exception: {e}") 

    # Render the form page
    return render_template(
        'school_info.html', 
        form=form,
        d_active=ACTIVE, 
        title='Update School Information'
    )


@admin_bp.route('/view-teachers')
@login_required
def view_teachers():
    try: 
        all_teachers = Teacher.query.all()
        if not all_teachers:
            flash('No records of teachers are present!', 'info')
    except SQLAlchemyError as e:
        # Log the error and flash a message
        current_app.logger.error(f"Database query error: {e}")
        flash('Oops, something went wrong on our side! Please try again later.', 'danger')
        all_teachers = []  

    return render_template(
        'manage_teachers/view_teachers.html',
        t_active=ACTIVE,
        title='View Teachers',
        teachers=all_teachers
    ) 


@admin_bp.route('/add-teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    
    if form.validate_on_submit():
        try:
            # Step 1: Create a new Teacher record
            new_teacher = Teacher(
                teacher_name=form.teacher_name.data,
                tsc_no=form.tsc_no.data,
                id_no=form.id_no.data,
                phone_no=form.phone_no.data,
                email=form.email.data if form.email.data else None,
                gender=form.gender.data
            )
            db.session.add(new_teacher)
            db.session.flush()  
            
            # Step 2: Create a corresponding User record
            username = generate_username(new_teacher.teacher_name)  
            default_password = str(new_teacher.id_no)  
            
            new_user = User(
                teacher_id=new_teacher.id,
                username=username,
                is_password_updated=False  
            )
            new_user.set_password(default_password)  
            
            db.session.add(new_user)
            
            # Step 3: Commit both records
            db.session.commit()
            
            # Step 4: Provide feedback to the user
            flash(f"""Teacher '{new_teacher.teacher_name}' 
                   added successfully! Username: {username}""", 'success')
            return redirect(url_for('admin_bp.add_teacher'))
        
        except Exception as e:
            db.session.rollback() 
            flash(
               'An error occurred while adding the teacher. Please try again.', 
               'danger'
            )
            raise InternalServerError(f"Error: {str(e)}")   

    return render_template(
        'manage_teachers/add_teacher.html',
        t_active=ACTIVE,
        form=form,
        title='Add Teacher'
    )


@admin_bp.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateForm()

    if form.validate_on_submit(): 
        if form.current_password.data:
            if not current_user.check_password(form.current_password.data):
                flash('Incorrect current password!', 'danger')
                # Re-render the update template.
                return render_template('manage_teachers/update_profile.html', t_active=ACTIVE, form=form, title='Update Profile')

            if form.new_password.data:
                current_user.set_password(form.new_password.data)
                flash('Password updated successfully!', 'info')
                db.session.commit()

        # update phone number.
        if form.phone_no.data:
            try:
                current_user.teacher.phone_no = form.phone_no.data
                db.session.commit()
                flash('Phone number updated successfully!', 'info')

            except IntegrityError as e:
                db.session.rollback()
                flash(
                    f'The phone number "{form.phone_no.data}" is already in use.', 'danger'
                )
                current_app.logger.error(f'EXISTING PHONE NUMBER: {str(e)}')
                return render_template('manage_teachers/update_profile.html', t_active=ACTIVE, form=form, title='Update Profile')
                
            except SQLAlchemyError as e:
                db.session.rollback()
                flash('Something went wrong! You phone number was not updated. Try again.')
                current_app.logger.error( InternalServerError(f"Error: {str(e)}"))

        # upload profile picture
        uploaded_img = form.profile_picture.data
        if uploaded_img:
            try:
                current_user.teacher.passport_filename = img_editor(uploaded_img)
                db.session.commit()
                flash('Profile picture uploaded successfully!', 'info')
            except ValueError:
                flash('Please upload a file of type JPG, JPEG, PNG, or GIF.', 'danger')
                return render_template('manage_teachers/update_profile.html', t_active=ACTIVE, form=form, title='Update Profile')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"CANNOT UPLOAD IMAGE: Unexpected error: {str(e)}")
                flash('Sorry, we cannot upload your picture right now. Please try again later.', 'danger')
                return render_template('manage_teachers/update_profile.html', t_active=ACTIVE, form=form, title='Update Profile')

    return render_template(
        'manage_teachers/update_profile.html',
        t_active=ACTIVE,
        form=form, 
        title='Update Profile'
    )


@admin_bp.route('/classic-view')
@login_required
def teachers_classic_view():
    return render_template(
        'manage_teachers/classic_teachers_view.html', 
        t_active=ACTIVE,
        teachers=Teacher.query.all(),
        title='Classic Teachers View'
    )


@admin_bp.route('/school-setup', methods=['GET', 'POST'])
@login_required
def school_setup(): 
    form = GradeForm()
    return render_template(
        'school_setup.html',
        form=form,
        d_active=ACTIVE, 
        title='Schoo Setup'
    )






# Logout user
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))