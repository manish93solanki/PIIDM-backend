import datetime
from flask import current_app as app, request, Blueprint, jsonify, send_file
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record, delete_single_record
from sqlalchemy import or_, func, desc

resume_bp = Blueprint('resume_bp', __name__, url_prefix='/api/resumes')


def is_resume_phone_num_exists(phone_num):
    cursor = app.session.query(model.Resume).filter(
        or_(
            model.Resume.phone_num == phone_num,
            model.Resume.alternate_phone_num == phone_num
        )
    ).order_by(model.Resume.resume_id.asc())
    records = list(cursor)
    return records


def is_resume_alternate_phone_num_exists(alternate_phone_num):
    cursor = app.session.query(model.Resume).filter(
        or_(
            model.Resume.phone_num == alternate_phone_num,
            model.Resume.alternate_phone_num == alternate_phone_num
        ),
    ).order_by(model.Resume.resume_id.asc())
    records = list(cursor)
    return records


def is_resume_email_exists(email):
    cursor = app.session.query(model.Resume).filter(
        model.Resume.email == email
    ).order_by(model.Resume.resume_id.asc())
    records = list(cursor)
    return records


def is_resume_linkedin_exists(linkedin_link):
    cursor = app.session.query(model.Resume).filter(
        model.Resume.linkedin_link == linkedin_link
    ).order_by(model.Resume.resume_id.asc())
    records = list(cursor)
    return records


def fetch_resume_by_id(resume_id):
    record = app.session.query(model.Resume).filter(model.Resume.resume_id == resume_id).first()
    return record


def populate_student_record(student):
    student_result = {}
    for key in student.__table__.columns.keys():
        value = getattr(student, key)
        if key in ('admission_date',) and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)

        student_result[key] = value

        if key == 'branch_id':
            branch = student.branch
            student_result[key] = {}
            for branch_key in branch.__table__.columns.keys():
                branch_value = getattr(branch, branch_key)
                student_result[key][branch_key] = branch_value
            student_result['branch'] = student_result.pop(key)
        if key == 'country_id':
            country = student.country
            student_result[key] = {}
            for country_key in country.__table__.columns.keys():
                country_value = getattr(country, country_key)
                student_result[key][country_key] = country_value
            student_result['country'] = student_result.pop(key)
        if key == 'city_id':
            city = student.city
            student_result[key] = {}
            for city_key in city.__table__.columns.keys():
                city_value = getattr(city, city_key)
                student_result[key][city_key] = city_value
            student_result['city'] = student_result.pop(key)
        if key == 'source_id':
            source = student.source
            student_result[key] = {}
            for source_key in source.__table__.columns.keys():
                source_value = getattr(source, source_key)
                student_result[key][source_key] = source_value
            student_result['source'] = student_result.pop(key)
        if key == 'course_id':
            course = student.course
            student_result[key] = {}
            for course_key in course.__table__.columns.keys():
                course_value = getattr(course, course_key)
                student_result[key][course_key] = course_value
            student_result['course'] = student_result.pop(key)
        if key == 'batch_time_id':
            batch_time = student.batch_time
            student_result[key] = {}
            for batch_time_key in batch_time.__table__.columns.keys():
                batch_time_value = getattr(batch_time, batch_time_key)
                student_result[key][batch_time_key] = batch_time_value
            student_result['batch_time'] = student_result.pop(key)
        if key == 'tutor_id':
            agent = student.agent
            student_result[key] = {}
            for agent_key in agent.__table__.columns.keys():
                agent_value = getattr(agent, agent_key)
                student_result[key][agent_key] = agent_value
            student_result['tutor'] = student_result.pop(key)
    return student_result


def populate_resume_record(resume):
    resume_result = {}
    for key in resume.__table__.columns.keys():
        value = getattr(resume, key)
        resume_result[key] = value
        if key == 'student_id':
            resume_result['student'] = populate_student_record(resume.student)
    return resume_result


def fetch_student_by_student_id(student_id):
    record = app.session.query(model.Student).filter(model.Student.student_id == student_id).first()
    return record


@resume_bp.route('/get-image', methods=['GET'])
def get_image():
    image_path = request.args.get('image_path')
    return send_file(image_path, mimetype='image/gif')


@resume_bp.route('/upload-image', methods=['POST'])
@token_required
def upload_image(current_user):
    image = request.files["image"]
    # image_path = f'data/uploaded_images/students/profile_pictures/{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}-{image.filename}'
    image_path = f'data/uploaded_images/students/profile_pictures/{datetime.datetime.now().strftime("%Y-%m-%dT%SZ")}-{image.filename}'
    image.save(image_path)
    return jsonify({'message': 'Image uploaded successfully.', 'data': image_path}), 200


@resume_bp.route('/add', methods=['POST'])
@token_required
def add_resume(current_user):
    if request.method == 'POST':
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        print(data)

        resume = app.session.query(model.Resume).filter(
            model.Resume.deleted == 0,
            model.Resume.student_id == data['student_id']
        ).first()

        if resume is None:
            # For new resume
            resume = model.Resume()

        # Check if student with course is already exist
        if 'phone_num' in data and data['phone_num'] and resume.phone_num != data['phone_num'] \
                and is_resume_phone_num_exists(data['phone_num']):
            return {'error': 'Phone number is already exist.'}, 409
        if 'alternate_phone_num' in data and data['alternate_phone_num'] \
                and resume.alternate_phone_num != data['alternate_phone_num'] \
                and is_resume_alternate_phone_num_exists(data['alternate_phone_num']):
            return {'error': 'Alternate Phone number is already exist.'}, 409
        if 'email' in data and data['email'] and resume.email != data['email'] \
                and is_resume_email_exists(data['email']):
            return {'error': 'Email is already exist.'}, 409
        if 'linkedin_link' in data and data['linkedin_link'] and resume.linkedin_link != data['linkedin_link'] \
                and is_resume_linkedin_exists(data['linkedin_link']):
            return {'error': 'LinkedIn link is already exist.'}, 409

        for key in resume.__table__.columns.keys():
            if key in ('resume_id', 'deleted', 'created_at', 'updated_at'):
                continue
            value = data[key]
            setattr(resume, key, value)
        bulk_insert([resume])
    return {'message': 'Resume details are added successfully.'}, 201


@resume_bp.route('/delete/<resume_id>', methods=['DELETE'])
@token_required
def soft_delete_resume(current_user, resume_id):
    resume = fetch_resume_by_id(int(resume_id))
    resume.deleted = 1
    insert_single_record(resume)
    return {'message': 'Successfully deleted..'}, 200


@resume_bp.route('/hard_delete/<resume_id>', methods=['DELETE'])
@token_required
def hard_delete_resume(current_user, resume_id):
    # resume = fetch_resume_by_id(int(resume_id))
    resume = app.session.query(model.Resume).filter(model.Resume.resume_id == resume_id)
    delete_single_record(resume)
    return {'message': 'Successfully deleted..'}, 200


@resume_bp.route('/student/select/<student_id>', methods=['GET'])
@token_required
def get_resume_details_by_student_id(current_user, student_id):
    resume = app.session.query(model.Resume).filter(model.Resume.student_id == int(student_id),
                                                    model.Resume.deleted == 0).first()
    if resume:
        resume_result = populate_resume_record(resume)
        print(resume_result)
        return jsonify(resume_result), 200
    return jsonify({}, 200)


@resume_bp.route('/select/<resume_id>', methods=['GET'])
@token_required
def get_resume(current_user, resume_id):
    resume = app.session.query(model.Resume).filter(model.Resume.resume_id == int(resume_id),
                                                    model.Resume.deleted == 0).first()
    resume_result = populate_resume_record(resume)
    return jsonify(resume_result), 200


@resume_bp.route('/select-all', methods=['GET'])
@token_required
def get_resumes(current_user):
    resumes = app.session.query(model.Resume).filter(model.Resume.deleted == 0).all()
    resume_results = []
    for resume in resumes:
        resume_result = populate_resume_record(resume)
        resume_results.append(resume_result)
    return jsonify(resume_results), 200


@resume_bp.route('/select-paginate/<page_id>', methods=['GET'])
@token_required
def get_paginated_resumes(current_user, page_id):
    # resumes = app.session.query(model.Resume).paginate(page=page_id, per_page=1)
    resumes = model.Resume.query.filter(model.Resume.deleted == 0).paginate(page=int(page_id), per_page=1)
    resume_results = []
    for resume in resumes:
        resume_result = populate_resume_record(resume)
        resume_results.append(resume_result)
    return jsonify(resume_results), 200


@resume_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_students_advanced(current_user):
    # try:
    total_resumes = model.Resume.query.filter(model.Resume.deleted == 0).count()

    # request params
    branch = request.args.get('branch', None)
    course = request.args.getlist('course[]')
    payment_mode = request.args.get('payment_mode', None)
    source = request.args.get('source', None)
    agent = request.args.get('agent', None)
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)

    # filtering data
    query = app.session.query(model.Resume).join(model.Student)
    query = query.filter(model.Resume.deleted == 0)
    query = query.filter(
        model.Resume.installment_payment_date.between(from_date, to_date)) if from_date and to_date else query
    query = query.filter(model.Student.branch_id == int(branch)) if branch else query
    query = query.filter(model.Student.course_id.in_(course)) if course else query
    query = query.filter(model.Resume.installment_payment_mode_id == int(payment_mode)) if payment_mode else query
    query = query.filter(model.Student.branch_id == int(branch)) if branch else query
    query = query.filter(model.Student.agent_id == int(agent)) if agent else query

    if current_user.user_role_id == 2:  # role == agent
        agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
        if agent_id:
            agent_id = agent_id[0]
        filtered_student_ids = app.session.query(model.Student.student_id).filter(model.Student.agent_id == agent_id)
        # only those students which are associated with given agent
        query = query.filter(model.Resume.student_id.in_(filtered_student_ids))
        total_resumes = model.Resume.query.filter(model.Resume.deleted == 0,
                                                  model.Resume.student_id.in_(filtered_student_ids)).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    student_sub_query = app.session.query(model.Student.student_id).filter(or_(
        model.Student.name.like(f'%{search_term}%'),
        model.Student.phone_num.like(f'%{search_term}%'),
        model.Student.alternate_phone_num.like(f'%{search_term}%'),
        model.Student.email.like(f'{search_term}%'),
    )).subquery() if search_term else query
    query = query.filter(model.Resume.student_id.in_(student_sub_query)) if search_term else query

    total_filtered_resumes = query.count()  # total filtered resumes
    total_earning = query.with_entities(func.sum(model.Resume.installment_payment)).scalar()
    # TODO: Need a student subquery to get total_pending_fee, total_expected_earning in future
    # total_earning = query.with_entities(func.sum(model.Resume.total_fee_paid)).scalar()
    # total_pending_fee = query.with_entities(func.sum(model.Resume.total_pending_fee)).scalar()
    basic_stats = {
        'total_earning': total_earning
    }

    query = query.order_by(desc(model.Resume.resume_id)).offset(start).limit(length)
    # print(query)

    resumes = query.all()
    resume_results = []
    for resume in resumes:
        resume_result = populate_resume_record(resume)
        resume_results.append(resume_result)
    # response
    return jsonify({
        'data': resume_results,
        'recordsFiltered': total_filtered_resumes,
        'recordsTotal': total_resumes,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500
