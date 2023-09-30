from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_, desc
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

placement_bp = Blueprint('placement_bp', __name__, url_prefix='/api/placements')


def is_placement_phone_num_exists(phone_num):
    cursor = app.session.query(model.Placement).filter(
        model.Placement.phone_num == phone_num,
    )
    records = list(cursor)
    return records


def is_placement_email_exists(email):
    cursor = app.session.query(model.Placement).filter(model.Placement.email == email)
    records = list(cursor)
    return records


def fetch_placement_by_id(placement_id):
    record = app.session.query(model.Placement).filter(model.Placement.placement_id == placement_id).first()
    return record


def populate_placement_record(placement):
    placement_result = {}
    for key in placement.__table__.columns.keys():
        value = getattr(placement, key)
        placement_result[key] = value

        if key == 'student_id':
            student = placement.student
            placement_result[key] = {}
            for student_key in student.__table__.columns.keys():
                student_value = getattr(student, student_key)
                placement_result[key][student_key] = student_value
                if student_key == 'branch_id':
                    branch = student.branch
                    placement_result[key][student_key] = {}
                    for branch_key in branch.__table__.columns.keys():
                        branch_value = getattr(branch, branch_key)
                        placement_result[key][student_key][branch_key] = branch_value
                    placement_result[key]['branch'] = placement_result[key].pop(student_key)
                if student_key == 'country_id':
                    country = student.country
                    placement_result[key][student_key] = {}
                    for country_key in country.__table__.columns.keys():
                        country_value = getattr(country, country_key)
                        placement_result[key][student_key][country_key] = country_value
                    placement_result[key]['country'] = placement_result[key].pop(student_key)
                if student_key == 'state_id':
                    state = student.state
                    placement_result[key][student_key] = {}
                    for state_key in state.__table__.columns.keys():
                        state_value = getattr(state, state_key)
                        placement_result[key][student_key][state_key] = state_value
                    placement_result[key]['state'] = placement_result[key].pop(student_key)
                if student_key == 'city_id':
                    city = student.city
                    placement_result[key][student_key] = {}
                    for city_key in city.__table__.columns.keys():
                        city_value = getattr(city, city_key)
                        placement_result[key][student_key][city_key] = city_value
                    placement_result[key]['city'] = placement_result[key].pop(student_key)
                if student_key == 'source_id':
                    source = student.source
                    placement_result[key][student_key] = {}
                    for source_key in source.__table__.columns.keys():
                        source_value = getattr(source, source_key)
                        placement_result[key][student_key][source_key] = source_value
                    placement_result[key]['source'] = placement_result[key].pop(student_key)
                if student_key == 'course_id':
                    course = student.course
                    placement_result[key][student_key] = {}
                    for course_key in course.__table__.columns.keys():
                        course_value = getattr(course, course_key)
                        placement_result[key][student_key][course_key] = course_value
                    placement_result[key]['course'] = placement_result[key].pop(student_key)
                if student_key == 'course_mode_id':
                    course_mode = student.course_mode
                    placement_result[key][student_key] = {}
                    for course_mode_key in course_mode.__table__.columns.keys():
                        course_mode_value = getattr(course_mode, course_mode_key)
                        placement_result[key][student_key][course_mode_key] = course_mode_value
                    placement_result[key]['course_mode'] = placement_result[key].pop(student_key)
                if student_key == 'course_content_id':
                    course_content = student.course_content
                    placement_result[key][student_key] = {}
                    for course_content_key in course_content.__table__.columns.keys():
                        course_content_value = getattr(course_content, course_content_key)
                        placement_result[key][student_key][course_content_key] = course_content_value
                    placement_result[key]['course_content'] = placement_result[key].pop(student_key)
                if student_key == 'batch_time_id':
                    batch_time = student.batch_time
                    placement_result[key][student_key] = {}
                    for batch_time_key in batch_time.__table__.columns.keys():
                        batch_time_value = getattr(batch_time, batch_time_key)
                        placement_result[key][student_key][batch_time_key] = batch_time_value
                    placement_result[key]['batch_time'] = placement_result[key].pop(student_key)
                if student_key == 'batch_id':
                    batch = student.batch
                    placement_result[key][student_key] = {}
                    if batch:
                        for batch_key in batch.__table__.columns.keys():
                            batch_value = getattr(batch, batch_key)
                            placement_result[key][student_key][batch_key] = batch_value
                    placement_result[key]['batch'] = placement_result[key].pop(student_key)
                if student_key == 'agent_id':
                    agent = student.agent
                    placement_result[key][student_key] = {}
                    for agent_key in agent.__table__.columns.keys():
                        agent_value = getattr(agent, agent_key)
                        placement_result[key][student_key][agent_key] = agent_value
                    placement_result[key]['agent'] = placement_result[key].pop(student_key)
                if student_key == 'trainer_id':
                    trainer = student.trainer
                    placement_result[key][student_key] = {}
                    for trainer_key in trainer.__table__.columns.keys():
                        trainer_value = getattr(trainer, trainer_key)
                        placement_result[key][student_key][trainer_key] = trainer_value
                    placement_result[key]['trainer'] = placement_result[key].pop(student_key)
            placement_result['student'] = placement_result.pop(key)
    return placement_result


@placement_bp.route('/add', methods=['POST'])
@token_required
def add_placement(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                placement = model.Placement()
                # Check if placement is already exist
                if is_placement_phone_num_exists(item['phone_num']):
                    return {'error': 'Phone number is already exist.'}, 409
                if is_placement_email_exists(item['email']):
                    return {'error': 'Email is already exist.'}, 409
                for key, value in item.items():
                    setattr(placement, key, value)
                records_to_add.append(placement)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@placement_bp.route('/update/<placement_id>', methods=['PUT'])
@token_required
def update_placement(current_user, placement_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            placement = fetch_placement_by_id(int(placement_id))
            for key, value in item.items():
                setattr(placement, key, value)
            records_to_add.append(placement)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@placement_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_placement_by_email_or_phone_num(current_user):
    placement = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.Placement).filter(model.Placement.deleted == 0)
    if email:
        query = query.filter(model.Placement.email == email)
    else:
        query = query.filter(model.Placement.phone_num == phone_num)
    placement = query.first()
    result = {}
    if placement:
        for key in placement.__table__.columns.keys():
            value = getattr(placement, key)
            result[key] = value
    return jsonify(result), 200


@placement_bp.route('/delete/<placement_id>', methods=['DELETE'])
@token_required
def soft_delete_placement(current_user, placement_id):
    try:
        placement = fetch_placement_by_id(int(placement_id))
        placement.deleted = 1
        insert_single_record(placement)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@placement_bp.route('/select/<placement_id>', methods=['GET'])
@token_required
def get_placement(current_user, placement_id):
    placement = app.session.query(model.Placement).filter(model.Placement.placement_id == int(placement_id),
                                                          model.Placement.deleted == 0).first()
    placement_result = populate_placement_record(placement)
    return jsonify(placement_result), 200


@placement_bp.route('/all', methods=['GET'])
@token_required
def get_placements(current_user):
    query = app.session.query(model.Placement).filter(model.Placement.deleted == 0)
    cursor = query.all()
    placements = list(cursor)
    results = []
    for placement in placements:
        res = {}
        for key in placement.__table__.columns.keys():
            value = getattr(placement, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@placement_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_placements_advanced(current_user):
    # Sync students - Insertion
    placements = []
    # Fetch students who paid the fees fully
    students_paid_fees_fully = app.session.query(model.Student.student_id).filter(model.Student.total_pending_fee <= 0,
                                                                                  model.Student.deleted == 0).all()
    students_paid_fees_fully_ids = [x.student_id for x in students_paid_fees_fully]
    # Fetch students who are already in placement section
    students_already_in_placements = app.session.query(model.Placement.student_id).filter(
        model.Placement.student_id.in_(students_paid_fees_fully_ids), model.Placement.deleted == 0
    )
    students_already_in_placements_ids = [x.student_id for x in students_already_in_placements]
    # Get students who are new for the placements
    new_students_for_placements_ids = list(set(students_paid_fees_fully_ids) - set(students_already_in_placements_ids))

    students = app.session.query(model.Student).filter(
        model.Student.student_id.in_(new_students_for_placements_ids), model.Student.deleted == 0
    ).all()
    for student in students:
        placement = model.Placement()
        placement.student_id = student.student_id
        placement.joined_course_for = student.purpose_for_course
        placement.education = student.highest_education
        placements.append(placement)
    bulk_insert(placements)

    total_placements = model.Placement.query.filter(model.Placement.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Placement).join(model.Student)
    query = query.filter(model.Placement.deleted == 0)

    if current_user.user_role_id == 2:  # role == placement
        placement_id = app.session.query(model.Placement.placement_id).filter(
            model.Placement.user_id == current_user.user_id,
            model.Placement.deleted == 0
        ).first()
        if placement_id:
            placement_id = placement_id[0]
        query = query.filter(model.Placement.placement_id == placement_id)
        total_placements = model.Placement.query.filter(model.Placement.deleted == 0,
                                                        model.Placement.placement_id == placement_id).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(or_(
        model.Student.name.like(f'%{search_term}%'),
        model.Student.phone_num.like(f'%{search_term}%'),
        model.Student.email.like(f'{search_term}%'),
    )) if search_term else query

    total_filtered_placements = query.count()  # total filtered placements
    basic_stats = {
        'total_placements': total_filtered_placements
    }

    query = query.order_by(desc(model.Placement.created_at)).offset(start).limit(length)

    placements = query.all()
    placement_results = []
    for placement in placements:
        placement_result = populate_placement_record(placement)
        placement_results.append(placement_result)
    # response
    return jsonify({
        'data': placement_results,
        'recordsFiltered': total_filtered_placements,
        'recordsTotal': total_placements,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
