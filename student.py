import datetime
from flask import current_app as app, request, Blueprint, jsonify, send_file
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record, delete_single_record
from sqlalchemy import or_, asc, func, desc

student_bp = Blueprint('student_bp', __name__, url_prefix='/api/students')


def is_student_phone_num_exists(phone_num):
    cursor = app.session.query(model.Student).filter(
        or_(
            model.Student.phone_num == phone_num,
            model.Student.alternate_phone_num == phone_num
        )
    )
    records = list(cursor)
    return records


def is_student_alternate_phone_num_exists(alternate_phone_num):
    cursor = app.session.query(model.Student).filter(
        or_(
            model.Student.phone_num == alternate_phone_num,
            model.Student.alternate_phone_num == alternate_phone_num
        ),
    )
    records = list(cursor)
    return records


def is_student_email_exists(email):
    cursor = app.session.query(model.Student).filter(model.Student.email == email)
    records = list(cursor)
    return records


def fetch_student_by_id(student_id):
    record = app.session.query(model.Student).filter(model.Student.student_id == student_id).first()
    return record


def fetch_receipts_by_student_id(student_id):
    records = app.session.query(model.Receipt).filter(model.Receipt.student_id == student_id).all()
    return records


def populate_student_record(student):
    student_result = {}
    for key in student.__table__.columns.keys():
        value = getattr(student, key)
        if key in ('admission_date', 'dob', ) and value:
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
        if key == 'state_id':
            state = student.state
            student_result[key] = {}
            for state_key in state.__table__.columns.keys():
                state_value = getattr(state, state_key)
                student_result[key][state_key] = state_value
            student_result['state'] = student_result.pop(key)
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
        if key == 'course_mode_id':
            course_mode = student.course_mode
            student_result[key] = {}
            for course_mode_key in course_mode.__table__.columns.keys():
                course_mode_value = getattr(course_mode, course_mode_key)
                student_result[key][course_mode_key] = course_mode_value
            student_result['course_mode'] = student_result.pop(key)
        if key == 'course_content_id':
            course_content = student.course_content
            student_result[key] = {}
            for course_content_key in course_content.__table__.columns.keys():
                course_content_value = getattr(course_content, course_content_key)
                student_result[key][course_content_key] = course_content_value
            student_result['course_content'] = student_result.pop(key)
        if key == 'batch_time_id':
            batch_time = student.batch_time
            student_result[key] = {}
            for batch_time_key in batch_time.__table__.columns.keys():
                batch_time_value = getattr(batch_time, batch_time_key)
                student_result[key][batch_time_key] = batch_time_value
            student_result['batch_time'] = student_result.pop(key)
        if key == 'agent_id':
            agent = student.agent
            student_result[key] = {}
            for agent_key in agent.__table__.columns.keys():
                agent_value = getattr(agent, agent_key)
                student_result[key][agent_key] = agent_value
            student_result['agent'] = student_result.pop(key)
        if key == 'trainer_id':
            trainer = student.trainer
            student_result[key] = {}
            for trainer_key in trainer.__table__.columns.keys():
                trainer_value = getattr(trainer, trainer_key)
                student_result[key][trainer_key] = trainer_value
            student_result['trainer'] = student_result.pop(key)
    return student_result


def get_all_receipts_by_student(student_id):
    cursor = app.session.query(model.Receipt).filter(
        model.Receipt.student_id == student_id, model.Receipt.deleted == 0
    ).order_by(asc(model.Receipt.installment_num)).all()
    records = list(cursor)
    return records


def populate_receipt_record(receipt):
    receipt_result = {}
    for key in receipt.__table__.columns.keys():
        value = getattr(receipt, key)
        if key in ('installment_payment_date',) and value:
            value = str(value)

        receipt_result[key] = value

        if key == 'installment_payment_mode_id':
            payment_mode = receipt.payment_mode
            receipt_result[key] = {}
            for payment_mode_key in payment_mode.__table__.columns.keys():
                payment_mode_value = getattr(payment_mode, payment_mode_key)
                receipt_result[key][payment_mode_key] = payment_mode_value
            receipt_result['installment_payment_mode'] = receipt_result.pop(key)
    return receipt_result


@student_bp.route('/add', methods=['POST'])
@token_required
def add_student(current_user):
    if request.method == 'POST':
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()

        student = app.session.query(model.Student).filter(
            model.Student.deleted == 1,
            model.Student.phone_num == data['phone_num']
        ).first()
        if student:
            # Add the deleted student again
            student.deleted = 0
            student.is_active = 1
            bulk_insert([student])
            receipts_records_to_readd = []
            receipts = app.session.query(model.Receipt).filter(model.Receipt.student_id == int(student.student_id),
                                                              model.Receipt.deleted == 1).all()
            for receipt in receipts:
                receipt.deleted = 0
                receipts_records_to_readd.append(receipt)
            bulk_insert(receipts_records_to_readd)
        else:
            # insert new
            student = model.Student()
            # Check if student is already exist
            if 'phone_num' in data and data['phone_num'] and student.phone_num != data['phone_num'] and is_student_phone_num_exists(data['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if 'alternate_phone_num' in data and data['alternate_phone_num'] and student.alternate_phone_num != data['alternate_phone_num'] and is_student_alternate_phone_num_exists(data['alternate_phone_num']):
                return {'error': 'Alternate Phone number is already exist.'}, 409
            if 'email' in data and data['email'] and student.email != data['email'] and is_student_email_exists(data['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in data.items():
                if key in ('admission_date', 'dob', ) and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(student, key, value)
            bulk_insert([student])

            student = app.session.query(model.Student).filter(model.Student.phone_num == data['phone_num']).first()

            # Add installment in receipt model
            receipts_records_to_add = []
            for instalment in data['installments']:
                if 'installment_num' in instalment and instalment['installment_num'] and \
                        'installment_payment' in instalment and instalment['installment_payment']:
                    installment_num = instalment['installment_num']
                    receipt = app.session.query(model.Receipt).filter(model.Receipt.student_id == int(student.student_id),
                                                                      model.Receipt.installment_num == int(installment_num),
                                                                      model.Receipt.deleted == 0).first()
                    if not receipt:
                        receipt = model.Receipt()

                    receipt.installment_num = instalment['installment_num']
                    receipt.installment_payment = instalment['installment_payment']
                    setattr(receipt, 'installment_payment_date',
                            datetime.datetime.strptime(instalment['installment_payment_date'], '%Y-%m-%d'))
                    receipt.installment_payment_mode_id = instalment['installment_payment_mode_id']
                    receipt.installment_payment_transaction_number = instalment['installment_payment_transaction_number']
                    receipt.student_id = student.student_id
                    receipts_records_to_add.append(receipt)
            bulk_insert(receipts_records_to_add)
    return {'message': 'Admission confirmed'}, 201


@student_bp.route('/update/<student_id>', methods=['PUT'])
@token_required
def update_student(current_user, student_id):
    if not request.is_json:
        return {'error': 'Bad Request.'}, 400
    data = request.get_json()

    student = fetch_student_by_id(int(student_id))

    # Check if student is already exist
    if 'phone_num' in data and data['phone_num'] and student.phone_num != data['phone_num'] and is_student_phone_num_exists(
            data['phone_num']):
        return {'error': 'Phone number is already exist.'}, 409
    if 'alternate_phone_num' in data and data['alternate_phone_num'] and student.alternate_phone_num != data[
        'alternate_phone_num'] and is_student_alternate_phone_num_exists(
        data['alternate_phone_num']):
        return {'error': 'Alternate Phone number is already exist.'}, 409
    if 'email' in data and data['email'] and student.email != data['email'] and is_student_email_exists(data['email']):
        return {'error': 'Email is already exist.'}, 409
    for key, value in data.items():
        if key in ('admission_date', 'dob', ) and value:
            value = datetime.datetime.strptime(value, '%Y-%m-%d')
        setattr(student, key, value)
    bulk_insert([student])
    print('\nstudent: ', student.student_id, '\n')

    # Add installment in receipt model
    if 'installments' in data:
        receipts_records_to_add = []
        for instalment in data['installments']:
            if 'installment_num' in instalment and instalment['installment_num'] and \
                    'installment_payment' in instalment and instalment['installment_payment']:
                installment_num = instalment['installment_num']
                receipt = app.session.query(model.Receipt).filter(model.Receipt.student_id == int(student.student_id),
                                                                  model.Receipt.installment_num == int(installment_num),
                                                                  model.Receipt.deleted == 0).first()
                if not receipt:
                    receipt = model.Receipt()

                receipt.installment_num = instalment['installment_num']
                receipt.installment_payment = instalment['installment_payment']
                setattr(receipt, 'installment_payment_date',
                        datetime.datetime.strptime(instalment['installment_payment_date'], '%Y-%m-%d'))
                receipt.installment_payment_mode_id = instalment['installment_payment_mode_id']
                receipt.installment_payment_transaction_number = instalment['installment_payment_transaction_number']
                receipt.student_id = student.student_id
                receipts_records_to_add.append(receipt)
        bulk_insert(receipts_records_to_add)
    return {'message': 'Successfully Updated.'}, 200


@student_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_student_by_email_or_phone_num(current_user):
    student = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.Student).filter(model.Student.deleted == 0)
    if email:
        query = query.filter(model.Student.email == email)
    else:
        query = query.filter(model.Student.phone_num == phone_num)
    student = query.first()
    result = {}
    if student:
        for key in student.__table__.columns.keys():
            value = getattr(student, key)
            result[key] = value
    return jsonify(result), 200


@student_bp.route('/delete/<student_id>', methods=['DELETE'])
@token_required
def soft_delete_student(current_user, student_id):
    student = fetch_student_by_id(int(student_id))
    student.deleted = 1
    student.total_fee = 0
    student.total_fee_paid = 0
    student.total_pending_fee = 0
    student.is_active = 0
    insert_single_record(student)

    # hard delete for receipts
    receipts = fetch_receipts_by_student_id(int(student_id))
    for receipt in receipts:
        receipt = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == receipt.receipt_id)
        delete_single_record(receipt)
    # Why do we not delete receipts post student deletion?
    # Because if any payment was done for deleted student then
    # we need to keep track of the receipts, and considering them as an income.
    return {'message': 'Successfully deleted..'}, 200


@student_bp.route('/select/<student_id>', methods=['GET'])
@token_required
def get_student(current_user, student_id):
    student = app.session.query(model.Student).filter(model.Student.student_id == int(student_id),
                                                      model.Student.deleted == 0).first()
    student_result = populate_student_record(student)
    student_result['installments'] = []

    # Get student receipts
    receipt_records = get_all_receipts_by_student(student.student_id)
    for receipt in receipt_records:
        receipt_result = populate_receipt_record(receipt)
        student_result['installments'].append(receipt_result)
    return jsonify(student_result), 200


# @student_bp.route('/select/user/<user_id>', methods=['GET'])
# @token_required
# def get_student_by_user_id(current_user, user_id):
#     student = app.session.query(model.Student).filter(model.Student.user_id == int(user_id),
#                                                       model.Student.deleted == 0).first()
#     student_result = populate_student_record(student)
#     student_result['installments'] = []
#
#     # Get student receipts
#     receipt_records = get_all_receipts_by_student(student.student_id)
#     for receipt in receipt_records:
#         receipt_result = populate_receipt_record(receipt)
#         student_result['installments'].append(receipt_result)
#     return jsonify(student_result), 200


@student_bp.route('/select-all', methods=['GET'])
@token_required
def get_students(current_user):
    students = app.session.query(model.Student).filter(model.Student.deleted == 0).all()
    student_results = []
    for student in students:
        student_result = populate_student_record(student)
        student_result['installments'] = []

        # Get student receipts
        receipt_records = get_all_receipts_by_student(student.student_id)
        for receipt in receipt_records:
            receipt_result = populate_receipt_record(receipt)
            student_result['installments'].append(receipt_result)
        student_results.append(student_result)
    return jsonify(student_results), 200


@student_bp.route('/select-paginate/<page_id>', methods=['GET'])
@token_required
def get_paginated_students(current_user, page_id):
    # students = app.session.query(model.Student).paginate(page=page_id, per_page=1)
    students = model.Student.query.filter(model.Student.deleted == 0).paginate(page=int(page_id), per_page=1)
    student_results = []
    for student in students:
        student_result = populate_student_record(student)
        student_result['installments'] = []

        # Get student receipts
        receipt_records = get_all_receipts_by_student(student.student_id)
        for receipt in receipt_records:
            receipt_result = populate_receipt_record(receipt)
            student_result['installments'].append(receipt_result)
        student_results.append(student_result)
    return jsonify(student_results), 200


@student_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_students_advanced(current_user):
    # try:
    total_students = model.Student.query.filter(model.Student.deleted == 0).count()

    # request params
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)
    name = request.args.get('name', None)
    phone_number = request.args.get('phone_number', None)
    branch = request.args.get('branch', None)
    
    course = request.args.get('course', None)
    course_mode = request.args.get('course_mode', None)
    source = request.args.get('source', None)
    batch_time = request.args.get('batch_time', None)
    is_active = request.args.get('is_active', None)

    # filtering data
    query = app.session.query(model.Student)
    query = query.filter(model.Student.deleted == 0)
    query = query.filter(
        model.Student.admission_date.between(from_date, to_date)) if from_date and to_date else query
    query = query.filter(model.Student.name.like(f'{name}%')) if name else query
    query = query.filter(or_(
        model.Student.phone_num == phone_number,
        model.Student.alternate_phone_num == phone_number
    )) if phone_number else query
    query = query.filter(model.Student.branch_id == int(branch)) if branch else query
    query = query.filter(model.Student.course_id == int(course)) if course else query
    query = query.filter(model.Student.course_mode_id == int(course_mode)) if course_mode else query
    query = query.filter(model.Student.source_id == int(source)) if source else query
    query = query.filter(model.Student.batch_time_id == int(batch_time)) if batch_time else query
    query = query.filter(model.Student.is_active == int(is_active)) if is_active else query

    # if current_user.user_role_id == 2:  # role == agent
    #     agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
    #     if agent_id:
    #         agent_id = agent_id[0]
    #     query = query.filter(model.Student.agent_id == agent_id)
    #     total_students = model.Student.query.filter(model.Student.deleted == 0,
    #                                                 model.Student.agent_id == agent_id).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(or_(
        model.Student.name.like(f'{search_term}%'),
        model.Student.phone_num.like(f'%{search_term}%'),
        model.Student.alternate_phone_num.like(f'%{search_term}%'),
        model.Student.email.like(f'{search_term}%'),
    )) if search_term else query

    total_filtered_students = query.count()  # total filtered students
    if current_user.user_role_id == 2:  # role == agent
        agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
        if agent_id:
            agent_id = agent_id[0]
        total_admissions = query.filter(model.Student.agent_id == agent_id).count()  # total_admissions
        total_dropouts = query.filter(model.Student.agent_id == agent_id, model.Student.is_active == 0).count()
        total_expected_earning = query.filter(model.Student.agent_id == agent_id).with_entities(func.sum(model.Student.total_fee)).scalar()
        total_earning = query.filter(model.Student.agent_id == agent_id).with_entities(func.sum(model.Student.total_fee_paid)).scalar()
        total_pending_fee = query.filter(model.Student.agent_id == agent_id).with_entities(func.sum(model.Student.total_pending_fee)).scalar()
    else:
        total_admissions = query.count()  # total_admissions
        total_dropouts = query.filter(model.Student.is_active == 0).count()
        total_expected_earning = query.with_entities(func.sum(model.Student.total_fee)).scalar()
        total_earning = query.with_entities(func.sum(model.Student.total_fee_paid)).scalar()
        total_pending_fee = query.with_entities(func.sum(model.Student.total_pending_fee)).scalar()

    basic_stats = {
        'total_admissions': total_admissions,
        'total_dropouts': total_dropouts,
        'total_expected_earning': total_expected_earning,
        'total_earning': total_earning,
        'total_pending_fee': total_pending_fee
    }

    query = query.order_by(desc(model.Student.admission_date)).offset(start).limit(length)
    print(query)

    students = query.all()
    student_results = []
    for student in students:
        student_result = populate_student_record(student)

        # Get student receipts
        student_result['installments'] = []
        receipt_records = get_all_receipts_by_student(student.student_id)
        for receipt in receipt_records:
            receipt_result = populate_receipt_record(receipt)
            student_result['installments'].append(receipt_result)
        student_results.append(student_result)
        # student_results.append({'name': student_result['name']})
    # response
    return jsonify({
        'data': student_results,
        'recordsFiltered': total_filtered_students,
        'recordsTotal': total_students,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500


@student_bp.route('/installments/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_students_installments_advanced(current_user):
    # try:
    total_students = model.Student.query.filter(model.Student.deleted == 0).count()

    # request params
    req_student_id = request.args.get('student_id', None)

    # filtering data
    query = app.session.query(model.Student)
    query = query.filter(model.Student.deleted == 0)
    query = query.filter(model.Student.student_id == int(req_student_id)) if req_student_id else query

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)

    total_filtered_students = query.count()  # total filtered students
    total_admissions = query.count()  # total_admissions
    total_dropouts = query.filter(model.Student.is_active == 0).count()
    total_expected_earning = query.with_entities(func.sum(model.Student.total_fee)).scalar()
    total_earning = query.with_entities(func.sum(model.Student.total_fee_paid)).scalar()
    total_pending_fee = query.with_entities(func.sum(model.Student.total_pending_fee)).scalar()
    basic_stats = {
        'total_admissions': total_admissions,
        'total_dropouts': total_dropouts,
        'total_expected_earning': total_expected_earning,
        'total_earning': total_earning,
        'total_pending_fee': total_pending_fee
    }

    query = query.offset(start).limit(length)
    print(query)

    student = query.first()
    student_result = []
    if student:
        student_result = populate_student_record(student)
        # Get student receipts
        installments = []
        receipt_records = get_all_receipts_by_student(student.student_id)
        for receipt in receipt_records:
            receipt_result = populate_receipt_record(receipt)

            installments.append(receipt_result)
        student_result = installments
    # response
    return jsonify({
        'data': student_result,
        'recordsFiltered': total_filtered_students,
        'recordsTotal': total_students,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500


@student_bp.route('/upload-image', methods=['POST'])
@token_required
def upload_image(current_user):
    image = request.files["image"]
    image_path = f'data/uploaded_images/{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}-{image.filename}'
    image.save(image_path)
    return jsonify({'message': 'Image uploaded successfully.', 'data': image_path}), 200


@student_bp.route('/get-image', methods=['GET'])
def get_image():
    image_path = request.args.get('image_path')
    return send_file(image_path, mimetype='image/gif')
