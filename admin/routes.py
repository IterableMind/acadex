from flask import render_template, url_for, flash, redirect, current_app, jsonify, request
from . import admin_bp
from .forms import * 
from ..models import db, SchoolInfo, Teacher, User, Grade, Stream, Student, Subject, Roles, SchoolBranch
from .. models import TeacherSubjectAssignment, Exam, ExamMarks
from ..utils.utils import generate_username
from ..utils.generate_pdf import generate_report_cards_pdf
from ..utils.image_processor import preprocess_image as img_editor 
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import or_, and_, func
from werkzeug.exceptions import InternalServerError
from flask_login import login_required, current_user, logout_user



ACTIVE = 'link--active'
HORIZONTAL_ACTIVE = 'sub--link--active'
            

@admin_bp.route('/dashboard', methods = ['GET', 'POST'])
@login_required
def dashboard():
  students_count = 0
  try:
    students_count = Student.query.count()
  except SQLAlchemyError as e:
    current_app.logger.error('e')
    
  return render_template(
    'dashboard.html',
    students_count = students_count,
    form = SearchStudent(),
    d_active = ACTIVE, 
    title = 'Admin'
  )


"""
Handle school information update.
"""
@admin_bp.route('/update_sch_info', methods = ['GET', 'POST'])
@login_required
def update_sch_info():
    form = SchoolInfoForm()
    if form.validate_on_submit():
      try: 
        sch = SchoolInfo(
            name = form.name.data.upper(),
            address = form.address.data,
            registration_number = form.registration_number.data or None,
            contact_email = form.contact_email.data or None,
            contact_phone = form.contact_phone.data
        )

        db.session.add(sch)
        db.session.commit()

        prev_info = SchoolInfo.query.first() 

        if prev_info and prev_info.id != sch.id:   
            db.session.delete(prev_info)
            db.session.commit()

        flash('School information updated successfully!', 'success')
        return redirect(
            url_for('admin_bp.update_sch_info')
        )
      
      except Exception as e:
          db.session.rollback()
          flash('An unexpected error occurred. Please try again later.', 'error')
          current_app.logger.error(f"Exception: {e}") 

    return render_template(
        'update_sch_info.html', 
        form = form,
        d_active = ACTIVE, 
        title = 'Update School Information'
    )


@admin_bp.route('/view-teachers')
@login_required
def view_teachers():
    branches = SchoolBranch.query.all()
    try: 
        all_teachers = Teacher.query.all()[::-1]
        if not all_teachers:
            flash('No records of teachers are present!', 'info')
    except SQLAlchemyError as e: 
        current_app.logger.error(f"Database query error: {e}")
        flash(
            'Oops, something went wrong on our side! Please try again later.',
            'danger'
        )
        all_teachers = []  

    return render_template(
        'manage_teachers/view_teachers.html',
        t_active = ACTIVE,
        title = 'View Teachers',
        teachers = all_teachers,
        branches = branches
    ) 


@admin_bp.route('/add-teacher', methods = ['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    branches = [(branch.name, branch.name) for branch in SchoolBranch.query.all()]
    branches.insert(0, ("", "Select Branch"))  
    form.branch.choices = branches 

    if form.validate_on_submit():
        selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        try: 
            new_teacher = Teacher(
                teacher_name = form.teacher_name.data.strip(),
                tsc_no = form.tsc_no.data,
                id_no = form.id_no.data,
                phone_no = form.phone_no.data,
                branch = selected_branch,
                salary = form.salary.data,
                email = form.email.data.strip() if form.email.data else None,
                gender = form.gender.data
            )
            db.session.add(new_teacher)
            db.session.flush()  
             
            username = generate_username(new_teacher.teacher_name)  
            default_password = str(new_teacher.id_no)  
            
            new_user = User(
                teacher_id = new_teacher.id,
                username = username,
                is_password_updated = False  
            )
 
            new_user.set_password(default_password) # Hash pwd.
            db.session.add(new_user)
            db.session.commit()
             
            flash(
                f"""Teacher '{new_teacher.teacher_name}' 
                was added successfully! Username: {username}""", 
                'success'
            )
            return redirect(
                url_for('admin_bp.add_teacher')
            )
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash(
               'An error occurred while adding the teacher. Please try again.', 
               'danger'
            )
            # raise InternalServerError(f"Error: {str(e)}")   

    return render_template(
        'manage_teachers/add_teacher.html',
        t_active=ACTIVE,
        form=form,
        title='Add Teacher'
    )



@admin_bp.route('/assign_teacher_roles', methods=['GET', 'POST'])
@login_required
def assign_teacher_roles():
    try:
        subjects = Subject.query.all()
    except:
        pass
    return render_template(
        'manage_teachers/teachers_roles.html',
        t_active = ACTIVE,
        subjects = subjects,
        all_teachers = Teacher.query.all()[::-1]
    )


@admin_bp.route('/update_profile', methods = ['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateForm()
    if form.validate_on_submit(): 
        if form.current_password.data.strip():
            if not current_user.check_password(form.current_password.data):
                flash('Incorrect current password!', 'danger')
                # Re-render the update template.
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )
            
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
                    f'The phone number "{form.phone_no.data}" is already in use.', 
                    'danger'
                )
                current_app.logger.error(f'EXISTING PHONE NUMBER: {str(e)}')
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )    
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(
                    'Something went wrong! You phone number was not updated. Try again.',
                    'danger'
                )
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
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"CANNOT UPLOAD IMAGE: Unexpected error: {str(e)}")
                flash(
                    'Sorry, we cannot upload your picture right now. Please try again later.', 'danger'
                )
                return render_template(
                    'manage_teachers/update_profile.html', 
                    t_active = ACTIVE, 
                    form = form, 
                    title = 'Update Profile'
                )

    return render_template(
        'manage_teachers/update_profile.html',
        t_active = ACTIVE,
        form = form, 
        title = 'Update Profile'
    )


@admin_bp.route('/update_teacher_role', methods=['POST'])
@login_required
def update_teacher_role():
    stream = request.form.get('stream')
    roles_info = {
        'name': request.form.get('teacher-name'),
        'role': request.form.get('role')
    }

    def set_stream():
        # Update stream if present.
        if stream:
            roles_info['stream'] = stream

    if roles_info['role'] == 'Class Teacher':
        roles_info['grade'] = request.form.get('grade')
        set_stream()

    teacher = Teacher.query.filter_by(
        teacher_name = roles_info['name']
    ).first()
    
    exist_roles = Roles.query.filter_by(teacher_id = teacher.id).first()
    if exist_roles:
        db.session.delete(exist_roles)
        db.session.commit() 

    # no roles present
    role = Roles(role = roles_info['role'], teacher_id = teacher.id)
    db.session.add(role)
    db.session.flush()
    
    if roles_info.get('grade') != None:
        role.grade = roles_info['grade']
        set_stream()
    try: 
        db.session.commit() # comment either of the two changes.
        updated_tchr_roles = Roles.query.filter_by(
            teacher_id = teacher.id
        ).first() 

        if updated_tchr_roles.role == 'Class Teacher': 
            if roles_info.get('grade') != None:
                updated_tchr_roles.grade = roles_info['grade']
                if stream:
                    updated_tchr_roles.stream = stream
        db.session.commit()

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'An Error {e} occured!')

    flash(
        f'The role for {roles_info["name"]} was updated successfully!', 
        'success'
    )
    x = Roles.query.filter_by(teacher_id=teacher.id).first()
    return redirect(url_for('admin_bp.assign_teacher_roles'))


@admin_bp.route('/admin-view', methods=['GET', 'POST'])
@login_required
def teachers_classic_view(): 
    is_all_selected = False
    branch = request.form.get('branch')
    if branch == 'all':
        teachers = Teacher.query.all()
        is_all_selected = True
    else:
        branch_id = SchoolBranch.query.filter_by(name=branch).first().id
        teachers = Teacher.query.filter_by(branch_id=branch_id).all()
    return render_template(
        'manage_teachers/classic_teachers_view.html', 
        t_active = ACTIVE,
        teachers = teachers,
        all = is_all_selected,
        title = 'Classic Teachers View'
    )


# Delete the target teacher and his/her related details from the system.
@admin_bp.route('delete_teacher', methods=['POST'])
@login_required
def delete_teacher(): 
    try:
        tr = Teacher.query.filter_by(teacher_name = request.form.get
            ('delete-teacher-name')).first() 
        tr_role = Roles.query.filter_by(teacher_id = tr.id).first() 
        
        # Delete the subjects awarded to the teacher
        for t in TeacherSubjectAssignment.query.all():
            if t.teacher_id == tr.id:
                db.session.delete(t)

        User.query.filter_by(teacher_id = tr.id).delete()
        if tr_role: db.session.delete(tr_role) 

        db.session.delete(tr)
        db.session.commit() 
        flash(f'{tr.teacher_name} was succefully deleted!', 'info')
        return redirect(url_for('admin_bp.assign_teacher_roles'))
    
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
    flash('Sorry, something went wrong on our side!', 'danger')
    return redirect(url_for('admin_bp.assign_teacher_roles'))


# Set up school status in terms of grades and streams.
@admin_bp.route('/school-setup', methods = ['GET', 'POST'])
@login_required
def school_setup(): 
    form = GradeForm()
    if form.validate_on_submit(): 
        grades_info = {
            'grade': form.grade_name.data,
            'stream1': form.stream1.data,
            'stream2': form.stream2.data,
            'stream3': form.stream3.data,
        } 
        streams = [
            grades_info['stream1'], 
            grades_info['stream2'],
            grades_info['stream3']
        ]
        grade = Grade.query.filter_by(grade_name = grades_info['grade']).first()
        current_streams = Stream.query.filter_by(grade_id = grade.id).all()

        if any(streams):
            # Muilt Streams
            try:
                if streams[0]:
                    stream1 = Stream(stream_name = streams[0], grade_id = grade.id)
                    if len(current_streams) > 1 and current_streams[0]:
                        current_streams[0].stream_name = streams[0]
                    else:
                        db.session.add(stream1)
                if streams[1]:
                    stream2 = Stream(stream_name = streams[1], grade_id = grade.id)
                    if len(current_streams) > 2 and current_streams[1]:
                        current_streams[1].stream_name = streams[1]
                    else:
                        db.session.add(stream2)
                if streams[2]:
                    stream3 = Stream(stream_name = streams[2], grade_id = grade.id)
                    if len(current_streams) > 2 and current_streams[2]:
                        current_streams[2].stream_name = streams[2]
                    else:
                        db.session.add(stream3)
                db.session.commit() 

            except SQLAlchemyError as e: 
                db.session.rollback()
                current_app.logger(f'An error occured: {e}')
        else:
            for stream in Stream.query.filter_by(grade_id = grade.id).all():
                db.session.delete(stream)
            db.session.commit()

        flash('Grade information updated successfully!', 'success')
        return redirect(url_for('admin_bp.school_setup')) 
    
    return render_template(
        'school_setup.html',
        form = form,
        d_active = ACTIVE, 
        title = 'Grades/Streams setup'
    )


# Endpoint to fetch streams of the selected grade.
@admin_bp.route('/get_streams', methods = ['GET', 'POST'])
@login_required
def get_streams():
    targeted_grade = request.json 
    grade = Grade.query.filter_by(grade_name = targeted_grade.get(
            'selectedValue')).first()
    streams = Stream.query.filter_by(grade_id = grade.id).all()
    streams_list = [str(s) for s in streams]
    return jsonify(streams_list)


@admin_bp.route('/studentdash')
@login_required
def student_dash():
    form = SearchStudent()
    student_info = {}

    try:
        # Query student counts by grade and gender 
        results = db.session.query(
            Student.grade,
            Student.gender,
            func.count(Student.id)
        ).group_by(Student.grade, Student.gender).all()

        # Process results into a dictionary
        for grade, gender, count in results:
            if grade not in student_info:
                student_info[grade] = {"boys": 0, "girls": 0}
            if gender == "Male":
                student_info[grade]["boys"] = count
            elif gender == "Female":
                student_info[grade]["girls"] = count
            student_info[grade]['total'] = student_info[grade]["girls"] + student_info[grade]["boys"]
 
    except SQLAlchemyError as e:
        current_app.logger.error(e)

    return render_template(
        'manage_students/student_dash.html',
        s_active=ACTIVE,
        form=form, 
        student_info=student_info  
    )


@admin_bp.route('/add_student', methods = ['GET', 'POST'])
@login_required
def add_student(): 
    form = StudentRegistrationForm()
    branches = [(branch.name, branch.name) for branch in SchoolBranch.query.all()]
    branches.insert(0, ("", "Select Branch"))  
    form.branch.choices = branches 
    if form.validate_on_submit(): 
        selected_branch = SchoolBranch.query.filter_by(name=form.branch.data).first()
        student = Student(
            fullname = form.fullname.data,
            grade = form.grade.data, 
            adm_no = form.adm_no.data, 
            gender = form.gender.data,
            stream = form.stream.data,
            branch = selected_branch,
            parent_name = form.parent_name.data, 
            contact_phone = form.contact_phone.data, 
            health_info = form.health_info.data
        )
        strm = request.form.get('streams')
        if strm:
            student.stream = strm
        try:
            photo_file = form.photo.data
            if photo_file:
                student.photo = img_editor(photo_file)
            db.session.add(student)
            db.session.commit()
            flash('Student was added successfully!', 'info')
            return redirect(url_for('admin_bp.add_student'))
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(e)
            flash('Something went wrong!', 'danger')
            return redirect(url_for('admin_bp.add_student'))

    return render_template(
        'manage_students/add_student.html',
        s_active = ACTIVE,
        form = form
    )


@admin_bp.route('/update_student_biodata', methods=['POST'])
@login_required
def update_student_biodata():
    adm_no = request.form.get('adm_no')
    stream = request.form.get('stream')
    branch_name = request.form.get('branch')

    # Fetch the student
    target_student = Student.query.filter_by(adm_no=adm_no).first()

    if not target_student:
        flash('Student not found!', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    # Query branch from name
    branch = SchoolBranch.query.filter_by(name=branch_name).first()
    if not branch:
        flash('Invalid branch provided.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    # Update student data
    target_student.fullname = request.form.get('fullname')
    target_student.gender = request.form.get('gender')
    target_student.grade = request.form.get('grade') 
    target_student.parent_name = request.form.get('parent_name')
    target_student.contact_phone = request.form.get('contact_phone')
    target_student.branch_id = branch.id

    target_student.health_info = request.form.get('health_info')

    if stream:
        target_student.stream = stream

    # Commit to DB
    try:
        db.session.commit()
        flash('Student information updated successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating student biodata: {e}")
        flash('An error occurred while updating the student.', 'danger')

    # Re-render the searched student page
    form = SearchStudent()
    return render_template(
        'manage_students/searched_student.html',
        form=form,
        student_info=target_student,
        branches = SchoolBranch.query.all(),
        grades = Grade.query.all(),
        s_active=ACTIVE
    ) 

# Update the student passport
@admin_bp.route('/update_student_passport', methods=['POST'])
@login_required
def update_student_passport(): 
    student_adm_no = request.form.get('adm_no')
    target_student = Student.query.filter_by(adm_no=student_adm_no).first()
    
    if not target_student:
        flash('Student not found!', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    photo_file = request.files.get('passport')
    if photo_file:
        target_student.photo = img_editor(photo_file)
        try:
            db.session.commit()
            flash('Passport updated successfully.', 'info')
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('Oops! Something went wrong! Couldn\'t update passport!', 'danger')

    # After updating, render the searched_student.html with updated data
    form = SearchStudent()
    return render_template(
        'manage_students/searched_student.html', 
        form=form,
        student_info=target_student,
        s_active=ACTIVE
    )


@admin_bp.route('/get_students', methods=['POST', 'GET'])
@login_required
def get_students():
    data = request.json
    grade = data.get('grade')
    stream = data.get('stream')

    if stream:
        students = Student.query.filter_by(grade=grade, stream=stream).all()
    else:
        students = Student.query.filter_by(grade=grade).all()

    student_list = [{
        "adm_no": s.adm_no,
        "fullname": s.fullname,
        "grade": s.grade,
        "stream": s.stream,
        "gender": s.gender,
        "parent_name": s.parent_name,
        "contact_phone": s.contact_phone
    } for s in students]

    return jsonify(student_list) 


 

@admin_bp.route('/display_students_per_grade')
@login_required
def display_students_per_grade():
    students = Student.query.order_by(Student.grade).all()
    return render_template(
        'manage_students/display_students_per_grade.html',
        g_active=ACTIVE,
        form = SearchStudent(),
        students = students
    )


@admin_bp.route('/search_student', methods = ['GET', 'POST'])
@login_required
def search_student():
    form = SearchStudent()
    branches = SchoolBranch.query.all()
    search_data = request.form.get('search_input').strip()
    if search_data:
        try:
            student = Student.query.filter(
                or_(
                    Student.adm_no.ilike(search_data),    
                    Student.fullname.ilike(search_data)  
                )
            ).first() 

            if student is None:
                flash('Oops! There is no student with the credentials you entered!', 
                    'danger') 
                return redirect(url_for('admin_bp.dashboard'))
            
            return render_template(
                'manage_students/searched_student.html', 
                form = form,
                student_info = student,
                branches = branches,
                grades = Grade.query.all(),
                s_active = ACTIVE,
            )
        
        except SQLAlchemyError as e:
            flash(
                'Oops! Something went wrong from our side! Please try again!', 
                'danger'
            )
            current_app.logger.error(f"Error searching for student: {e}")
            return render_template(
                'manage_students/student_dash.html', 
                form = form, 
                s_active = ACTIVE,
            )
        

@admin_bp.route('/view_subjects', methods=['GET', 'POST'])
@login_required
def view_subjects():
    try:
        all_subjects = Subject.query.all()
        grades = Grade.query.all()
    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        flash('Failured to load subjects! There may be no subjects or an internal error occured!')
    return render_template(
        'view_subjects.html',
        all_subjects = all_subjects,
        grades = grades,
        view_active = HORIZONTAL_ACTIVE,
        sub_active = ACTIVE
    )



@admin_bp.route('/add_subject', methods = ['GET', 'POST'])
@login_required
def add_subject():
    error_sms = 'Oops, something went wrong on our side please try again later!'
    all_subjects = Subject.query.all()[::-1]
    form = SubjectForm()
    if form.validate_on_submit():
        selected_grades = [
            field.label.text for name, field in form._fields.items()
            if field.type == 'BooleanField' and field.data and name != 'all_classes'
        ] 
        sub = Subject(
            subject = form.subject.data.strip(),
            grades = selected_grades,
            short_form = form.sub_short_form.data
        )

        if sub.subject.isdigit():
            flash(f'Oops! Subject name cannot be numbers!', 'danger')
            return redirect(url_for('admin_bp.add_subject')) 

        if sub.subject.lower() in [s.subject.lower() for s in all_subjects]:
            flash(f'{sub.subject} already exists in the system!', 'danger')
            return redirect(url_for('admin_bp.add_subject'))

        try:
            db.session.add(sub)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin_bp.add_subject'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(error_sms, 'danger')
            current_app.logger.error(f'Subject Insertion Error {e} occurred!')
        except:
            db.session.rollback()
            flash(error_sms, 'danger')
            current_app.logger.error('Unknown error occurred!')

    return render_template(
        'add_subject.html', 
        form = form,
        all_subjects = all_subjects,
        sub_active = ACTIVE,
        add_active = HORIZONTAL_ACTIVE
    )


@admin_bp.route('/delete_subject', methods=['POST'])
@login_required
def delete_subject():
    subject_name = request.form.get('delete-subject-name')

    try:
        # Find the subject
        subject = Subject.query.filter_by(subject=subject_name).first()
        if not subject:
            flash(f'Subject "{subject_name}" not found!', 'warning')
            return redirect(url_for('admin_bp.add_subject'))

        # Delete all assignments related to this subject
        TeacherSubjectAssignment.query.filter_by(subject_id=subject.id).delete()

        # Now delete the subject
        db.session.delete(subject)
        db.session.commit()

        flash(f'{subject_name} was deleted successfully!', 'info')

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Something went wrong {e}')
        flash(f'Error deleting {subject_name}', 'danger')

    return redirect(url_for('admin_bp.add_subject'))

 
@admin_bp.route('/assign_subjects', methods=['POST'])
@login_required
def assign_subjects():
    data = request.get_json()  # Get JSON data
    teacher_name = data.get("teacher")  # Get teacher's name
    subject_info = data.get("subjectInfo")  # Get subjects list

    # Retrieve the teacher from the database
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    for item in subject_info:
        subject_name = item.get("subject")
        grade = item.get("grade")
        stream = item.get("streams", None)  

        # Retrieve subject from the database
        subject = Subject.query.filter_by(subject=subject_name).first()
        if not subject:
            return jsonify({"message": f"Subject '{subject_name}' not found"}), 404

        # Check if the grade has streams in the database
        grade_has_streams = Stream.query.filter_by(grade_id=Grade.query.filter_by(grade_name=grade).first().id).count() > 0

        # Validation: If grade has streams, a stream must be provided
        if grade_has_streams and not stream:
            return jsonify({"message": f"You must select a stream for {grade}!"}), 400

        # Check if the subject in the given grade & stream is already assigned to another teacher
        existing_assignment = TeacherSubjectAssignment.query.filter_by(
            subject_id=subject.id, grade=grade, stream=stream
        ).first()

        if existing_assignment:
            # If assigned to another teacher, remove the previous assignment
            if existing_assignment.teacher_id != teacher.id:
                db.session.delete(existing_assignment)
            # If assigned to the same teacher, pass.
            if existing_assignment.teacher_id == teacher.id:
                db.session.delete(existing_assignment)

        # Create a new assignment for the current teacher
        new_assignment = TeacherSubjectAssignment(
            teacher_id=teacher.id, subject_id=subject.id, grade=grade, stream=stream
        )
        db.session.add(new_assignment)

    # Commit all changes
    db.session.commit() 

    return jsonify({"message": f"Subjects assigned/updated successfully for {teacher_name}!"})




@admin_bp.route('/get_teacher_subjects/<teacher_id>', methods=['GET'])
def get_teacher_subjects(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return jsonify({"message": "Teacher not found"}), 404

    assignments = TeacherSubjectAssignment.query.filter_by(teacher_id=teacher_id).all()
    
    result = []
    for assignment in assignments:
        result.append({
            "subject": assignment.subject.subject,
            "grade": assignment.grade,
            "stream": assignment.stream
        })

    return jsonify({"teacher": teacher.teacher_name, "subjects": result})


@admin_bp.route('/printouts')
@login_required
def printouts():
    return render_template(
        'printouts.html',
        p_active = ACTIVE
    )


@admin_bp.route('/download_marklist', methods=['GET', 'POST'])
@login_required
def download_marklist():
    target_grade_info = {
       'grade' : request.form.get('hidden-grade'),
       'stream': request.form.get('hidden-stream')
    }
    if target_grade_info['stream']:
        students = Student.query.filter(
            and_ (
                Student.grade == target_grade_info['grade'],
                Student.stream == target_grade_info['stream']
            )
        ).all()
        print(students)

    return 'This is where the magic happens!'



@admin_bp.route('/add_new_exam', methods=['GET', 'POST'])
@login_required
def add_new_exam():
    form = ExamForm()
    
    if form.validate_on_submit():
        new_exam = Exam(
            name=form.exam_name.data,
            term=form.term.data,
            year=form.year.data,  
            created_at=form.exam_date.data
        )
        
        if Exam.query.filter_by(name=form.exam_name.data).first():
            flash('Examination with that name already exist in the System!', 'danger')
            return redirect(url_for('admin_bp.add_new_exam'))
        try:
            # Check first if there is an open exam.
            exams = Exam.query.all()
            if exams:
                for ex in exams:
                    if ex.status == 'open':
                        flash('Sorry you have unpublished exam!.', 'danger')
                        return redirect(url_for('admin_bp.add_new_exam')) # Work on a better redirect later.
            db.session.add(new_exam)
            db.session.commit()
        except SQLAlchemyError as e:
            current_app.logger.error(e)
            db.session.rollback()
            flash('Sorry we can\'t add new exam now! Try later.', 'danger')
            return redirect(url_for('admin_bp.add_new_exam'))
        
        flash("Exam added successfully!", "success")
        print('EXAM ADDED SUCCESSFULLY!')
        return redirect(url_for('admin_bp.add_new_exam'))
    
    return render_template(
        'manage_exams/add_new_exam.html',
        form=form,
        ex_active=ACTIVE
    ) 



@admin_bp.route('/admin_marks_entry')
@login_required
def admin_marks_entry():
    # Get the latest open exam
    open_exam = Exam.query.filter_by(status='open').first()
    if not open_exam:
        flash('All exams have been published! Create new exam or unpublish exam to enter marks.', 'warning')
        return redirect(url_for('admin_bp.add_new_exam'))

    # Fetch all grades
    all_grades = Grade.query.all()
    
    # Prepare dict for grades missing marks
    grades_without_marks = {}

    for grade in all_grades:
        # Get only subjects that include this grade in their assigned list
        subjects = [
            subject for subject in Subject.query.all()
            if subject.grades and grade.grade_name in subject.grades
        ]

        missing_subjects = [] 
        for subject in subjects:
            # Get all students in this grade
            students_in_grade = Student.query.filter_by(grade=grade.grade_name).all()

            # Check if all students in the grade have marks for this subject
            marks_exist = all(
                ExamMarks.query.filter_by(
                    exam_id=open_exam.id,
                    subject_id=subject.id,
                    student_id=student.id
                ).first() is not None
                for student in students_in_grade
            )

            if not marks_exist:
                missing_subjects.append(subject.subject)

        if missing_subjects:
            grades_without_marks[grade.grade_name] = missing_subjects

    return render_template(
        'manage_exams/admin_marks_entry.html', 
        open_exam=open_exam,
        ex_active=ACTIVE,
        grades_without_marks=grades_without_marks
    )


@admin_bp.route('/get_students_for_grade')
@login_required
def get_students_for_grade():
    grade = request.args.get('grade')
    students = Student.query.filter_by(grade=grade).all()
    student_list = [{"id": student.id, "name": student.fullname} for student in students]
    return jsonify({"students": student_list})


"""
 Handles the uploading and saving of students marks for a 
 particular examination.
"""
@admin_bp.route('/save_marks', methods=['POST'])
@login_required
def save_marks():
    grade = request.form.get('grade') 
    subject_name = request.form.get('subject')
 
    marks_data = {key: value for key, value in request.form.items() 
                  if key.startswith("marks[")
    }

    exam = Exam.query.filter_by(status='open').first()
    subject = Subject.query.filter_by(subject=subject_name).first()
    
    for adm_no_key, mark in marks_data.items():
        # Extract admission number manually
        if adm_no_key.startswith("marks[") and adm_no_key.endswith("]"):
            adm_no = adm_no_key[6:-1]  # Remove "marks[" at start and "]" at end

            student = Student.query.filter_by(adm_no=adm_no, grade=grade).first()
            if student:
                existing_record = ExamMarks.query.filter_by(
                    exam_id=exam.id, student_id=student.id, subject_id=subject.id
                ).first()

                if existing_record:
                    existing_record.marks = mark # update marks.
                else:
                    new_mark = ExamMarks(
                        exam_id=exam.id,
                        student_id=student.id,
                        subject_id=subject.id,
                        marks=mark
                    )
                    db.session.add(new_mark)

    db.session.commit() 
    flash("Marks saved successfully!", "success")
    return redirect(url_for('admin_bp.admin_marks_entry'))


@admin_bp.route('/manage_exams', methods=['GET', 'POST'])
@login_required
def manage_exams():
    all_exams = Exam.query.all()
    return render_template(
        'manage_exams/manage_exams.html',
        all_exams = all_exams,
        ex_active = ACTIVE
    ) 


@admin_bp.route('/toggle_exam_status', methods=['POST'])
@login_required
def toggle_exam_status():
    target_exam = request.form.get('exam-name')
    target_exam_status = request.form.get('exam-status')
    try:
        exams = Exam.query.all()
        EXAM = Exam.query.filter_by(name=target_exam).first()
        if target_exam_status == 'open':
            EXAM.status = 'closed'
        if target_exam_status == 'closed':
            for ex in exams:
                ex.status = 'closed'
            EXAM.status = 'open'
        db.session.commit()
        return redirect(url_for('admin_bp.manage_exams'))

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        flash('Something went wrong! Try later', 'warning')
        db.session.rollback()


@admin_bp.route('/delete_exam', methods=['GET', 'POST'])
@login_required
def delete_exam():
    exam_name = request.form.get('delete-exam-name')
    exam = Exam.query.filter_by(name=exam_name).first()
    try:
        # Delete related exam marks in the database.
        marks = ExamMarks.query.filter_by(exam_id=exam.id).all()
        for mark in marks: db.session.delete(mark)
        # Delete actual exam
        db.session.delete(exam)
        db.session.commit()
        flash(f'{exam_name} was deleted successfully.', 'info') 

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback
        flash('Oops! Can\'t delete exam. Please try again later', 'danger')
    return redirect(url_for('admin_bp.manage_exams'))


@admin_bp.route('/edit_exam_data', methods=['GET', 'POST'])
@login_required
def edit_exam_data():
    submited_data = {
        'original_exam_name' : request.form.get('hidden-exam-name'),
        'new_exam_name' : request.form.get('exam-name').strip(),
        'new_exam_term_info' : request.form.get('term-info').strip()
    }
    try:
        target_exam = Exam.query.filter_by(name=
            submited_data['original_exam_name']
        ).first()

        if target_exam:
            # Check if there is an exam with the new name
            if Exam.query.filter_by(name=submited_data['new_exam_name']).first():
                flash(f'There is already an exam with the name {submited_data["new_exam_name"]}', 'danger')
            else:
                target_exam.name = submited_data['new_exam_name']
                if target_exam.term != submited_data['new_exam_term_info']:
                    target_exam.term = submited_data['new_exam_term_info']
                db.session.commit()
                flash('Examinatin Info updated successfully!', 'info')

    except SQLAlchemyError as e:
        current_app.logger.error(e)
        db.session.rollback()
        flash('Oops something went wrong! We can\'t update exam information right now!', 'warning')
    return redirect(url_for('admin_bp.manage_exams'))



@admin_bp.route('/generate_report_forms', methods=['GET', 'POST'])
@login_required
def generate_report_forms(): 
    exams = Exam.query.all()
    is_any_exam_published = False

    for exam in exams:
        if exam.status == 'closed':
            is_any_exam_published = True
            break 
    
    if not is_any_exam_published:
        # No published exam
        flash('No published exam! Please publish an exam first before generating report cards',
              'danger'
        )
        return redirect(url_for('admin_bp.manage_exams'))
        
    return render_template(
        'manage_exams/report_forms/report_forms_base.html',
        exams = exams,
        ex_active = ACTIVE,
        is_any_exam_published = is_any_exam_published
    )


@admin_bp.route('/process_report_forms', methods=['GET', 'POST'])
@login_required
def process_report_forms():
    exams = Exam.query.all()  # Get all exams
    report_cards = []
    is_rank_enabled = False

    if request.method == 'POST':
        grade = request.form.get('grade')
        exam_name = request.form.get('exam')
        stream = request.form.get('streams') 
        rank = request.form.get('rank')
        download_report = request.form.get('download')
        dates = {
            'closing_date' : request.form.get('closing-date'),
            'opening_date' : request.form.get('opening-date')
        }
        

        if rank == 'yes': 
            is_rank_enabled = True

        
        # Get the selected exam
        exam = Exam.query.filter_by(name=exam_name).first()

        if not exam:
            flash("Exam not found!", "danger")
            return redirect(url_for('admin_bp.process_report_forms'))

        # Get all students in the selected grade
        students = Student.query.filter_by(grade=grade).all()
        tot_subs = TeacherSubjectAssignment.query.filter_by(grade=grade).count()
    
        if stream:
            # Get teacher-subject assignments for this grade
            teacher_assignments = TeacherSubjectAssignment.query.join(Teacher).join(Subject).filter(
                (TeacherSubjectAssignment.grade == grade) &
                (TeacherSubjectAssignment.stream == stream)
            ).all()
        else:
            teacher_assignments = TeacherSubjectAssignment.query.join(Teacher).join(Subject).filter(
                TeacherSubjectAssignment.grade == grade
            ).all()

        # Store teacher assignments in a dictionary {subject_name: teacher_name}
        teacher_dict = {assignment.subject.subject: assignment.teacher.teacher_name for assignment in teacher_assignments}

        # Fetch marks for each student
        for student in students:
            marks = ExamMarks.query.join(Subject).filter(
                ExamMarks.exam_id == exam.id,
                ExamMarks.student_id == student.id
            ).all()

            def get_initials(name):
                return ".".join([part[0].upper() for part in name.split()])
            
            student_report = {
                "student": student,
                "marks": {
                    mark.subject.subject: {
                        "score": mark.marks,
                        "teacher": get_initials( teacher_dict.get(mark.subject.subject, "--"))  # Get teacher or default to "N/A"
                    }
                    for mark in marks
                    
                },
                "total": sum([mark.marks for mark in marks]),
                "attempted_any_exam": any([mark.marks for mark in marks])
            }
            

            report_cards.append(student_report)
            
            if is_rank_enabled:
                report_cards = sorted(report_cards, key=lambda report: report["total"], reverse=True) 
                for index, s in enumerate(report_cards):
                    s['position'] = index + 1
   
    if download_report:
        # Generate report cards if download btn is clicked
        report_cards = [card for card in report_cards if card['attempted_any_exam']]
        generate_report_cards_pdf(
            exam, 
            report_cards, 
            is_rank_enabled,
            dates=dates,
            grade=grade
        )
        flash(f'{grade} report forms generated successfully. Go to download folder to print them.', 'info')
        return redirect(url_for('admin_bp.generate_report_forms'))

    return render_template(
        "manage_exams/report_forms/report_forms_base.html",
        exams=exams,
        target_exam=exam,
        ex_active=ACTIVE,
        dates = dates,
        tot_subs = tot_subs,
        is_rank_enabled = is_rank_enabled,
        report_cards=report_cards
    )


@admin_bp.route('/manage_branch', methods=['GET', 'POST'])
def manage_branch():
    form = BranchForm()
    branches = SchoolBranch.query.all()
    branch_id = request.form.get("branch_id")
    if branch_id:
        form.branch_id.data = branch_id 
    if form.validate_on_submit():
        if branch_id:
            # UPDATE flow
            branch_info = SchoolBranch.query.get(branch_id)
            if branch_info:
                branch_info.name = form.name.data
                branch_info.branch_manager = form.manager.data
                branch_info.branch_head = form.branch_head.data
                branch_info.branch_level = form.branch_level.data
                try:
                    db.session.commit()
                    flash('Branch info updated successfully.', 'info')
                    return redirect(url_for('admin_bp.manage_branch'))
                except SQLAlchemyError as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    flash('Error updating branch. Please try again.', 'danger')
        else:
            # ADD flow
            new_branch = SchoolBranch(
                name = form.name.data,
                branch_manager = form.manager.data,
                branch_head = form.branch_head.data,
                branch_level = form.branch_level.data
            )
            try:
                db.session.add(new_branch)
                db.session.commit()
                flash('Branch was added successfully.', 'info')
                return redirect(url_for('admin_bp.manage_branch'))
            except SQLAlchemyError as e:
                current_app.logger.error(e)
                db.session.rollback()
                flash('Oops! Something went wrong. Please try again.', 'danger')
                
    return render_template(
        'add_branch.html', 
        b_active = ACTIVE,
        branches = branches,
        form = form
    )


# Logout user
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))