"""
Define routes for adminitrative roles only.
"""

from flask import render_template, url_for
from . import admin_bp
from .forms import SchoolInfoForm

ACTIVE = 'link--active'

@admin_bp.route('/dashboard')
def dashboard():
  return render_template(
    'dashboard.html',
    d_active=ACTIVE,
    title='Admin'
  )


# Handle update of school information.
@admin_bp.route('/school-info', methods=['GET', 'POST'])
def school_info():
  form = SchoolInfoForm()

  if form.validate_on_submit():
    return 'SCHOOL INFORMATION UPDATED SUCCESSFULLY!'
  
  return render_template(
    'school_info.html', 
    form=form,
    d_active=ACTIVE,
    title='Update School Information'
  )


@admin_bp.route('/manage-teachers')
def manage_teachers(): 
  return render_template(
    'manage_teachers.html', 
    t_active=ACTIVE,
    title='Manage Teachers'
  )