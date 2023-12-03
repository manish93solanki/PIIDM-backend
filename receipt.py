import datetime
from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record, delete_single_record
from sqlalchemy import or_, func, desc

receipt_bp = Blueprint('receipt_bp', __name__, url_prefix='/api/receipts')


def fetch_receipt_by_id(receipt_id):
    record = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == receipt_id).first()
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


def populate_receipt_record(receipt):
    receipt_result = {}
    for key in receipt.__table__.columns.keys():
        value = getattr(receipt, key)
        if key in ('installment_payment_date', ) and value:
            value = str(value)

        receipt_result[key] = value

        if key == 'installment_payment_mode_id':
            payment_mode = receipt.payment_mode
            receipt_result[key] = {}
            for payment_mode_key in payment_mode.__table__.columns.keys():
                payment_mode_value = getattr(payment_mode, payment_mode_key)
                receipt_result[key][payment_mode_key] = payment_mode_value
            receipt_result['installment_payment_mode'] = receipt_result.pop(key)

        if key == 'student_id':
            receipt_result['student'] = populate_student_record(receipt.student)
    return receipt_result


def fetch_student_by_student_id(student_id):
    record = app.session.query(model.Student).filter(model.Student.student_id == student_id).first()
    return record


@receipt_bp.route('/delete/<receipt_id>', methods=['DELETE'])
@token_required
def soft_delete_receipt(current_user, receipt_id):
    receipt = fetch_receipt_by_id(int(receipt_id))
    receipt.deleted = 1
    insert_single_record(receipt)
    return {'message': 'Successfully deleted..'}, 200


@receipt_bp.route('/hard_delete/<receipt_id>', methods=['DELETE'])
@token_required
def hard_delete_receipt(current_user, receipt_id):
    # receipt = fetch_receipt_by_id(int(receipt_id))
    receipt = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == receipt_id)
    delete_single_record(receipt)
    return {'message': 'Successfully deleted..'}, 200


@receipt_bp.route('/select/<receipt_id>', methods=['GET'])
@token_required
def get_receipt(current_user, receipt_id):
    receipt = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == int(receipt_id),
                                                      model.Receipt.deleted == 0).first()
    receipt_result = populate_receipt_record(receipt)
    return jsonify(receipt_result), 200


@receipt_bp.route('/select-all', methods=['GET'])
@token_required
def get_receipts(current_user):
    receipts = app.session.query(model.Receipt).filter(model.Receipt.deleted == 0).all()
    receipt_results = []
    for receipt in receipts:
        receipt_result = populate_receipt_record(receipt)
        receipt_results.append(receipt_result)
    return jsonify(receipt_results), 200


@receipt_bp.route('/select-paginate/<page_id>', methods=['GET'])
@token_required
def get_paginated_receipts(current_user, page_id):
    # receipts = app.session.query(model.Receipt).paginate(page=page_id, per_page=1)
    receipts = model.Receipt.query.filter(model.Receipt.deleted == 0).paginate(page=int(page_id), per_page=1)
    receipt_results = []
    for receipt in receipts:
        receipt_result = populate_receipt_record(receipt)
        receipt_results.append(receipt_result)
    return jsonify(receipt_results), 200


@receipt_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_students_advanced(current_user):
    # try:
    total_receipts = model.Receipt.query.filter(model.Receipt.deleted == 0).count()

    # request params
    branch = request.args.get('branch', None)
    course = request.args.get('course', None)
    payment_mode = request.args.get('payment_mode', None)
    source = request.args.get('source', None)
    agent = request.args.get('agent', None)
    from_date = request.args.get('from_date', None)
    to_date = request.args.get('to_date', None)

    # filtering data
    query = app.session.query(model.Receipt).join(model.Student)
    query = query.filter(model.Receipt.deleted == 0)
    query = query.filter(
        model.Receipt.installment_payment_date.between(from_date, to_date)) if from_date and to_date else query
    query = query.filter(model.Student.branch_id == int(branch)) if branch else query
    query = query.filter(model.Student.course_id == int(course)) if course else query
    query = query.filter(model.Receipt.installment_payment_mode_id == int(payment_mode)) if payment_mode else query
    query = query.filter(model.Student.branch_id == int(branch)) if branch else query
    query = query.filter(model.Student.agent_id == int(agent)) if agent else query

    if current_user.user_role_id == 2:  # role == agent
        agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
        if agent_id:
            agent_id = agent_id[0]
        filtered_student_ids = app.session.query(model.Student.student_id).filter(model.Student.agent_id == agent_id)
        # only those students which are associated with given agent
        query = query.filter(model.Receipt.student_id.in_(filtered_student_ids))
        total_receipts = model.Receipt.query.filter(model.Receipt.deleted == 0,
                                                    model.Receipt.student_id.in_(filtered_student_ids)).count()

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
    query = query.filter(model.Receipt.student_id.in_(student_sub_query)) if search_term else query

    total_filtered_receipts = query.count() # total filtered receipts
    total_earning = query.with_entities(func.sum(model.Receipt.installment_payment)).scalar()
    # TODO: Need a student subquery to get total_pending_fee, total_expected_earning in future
    # total_earning = query.with_entities(func.sum(model.Receipt.total_fee_paid)).scalar()
    # total_pending_fee = query.with_entities(func.sum(model.Receipt.total_pending_fee)).scalar()
    basic_stats = {
        'total_earning': total_earning
    }

    query = query.order_by(desc(model.Receipt.receipt_id)).offset(start).limit(length)
    # print(query)

    receipts = query.all()
    receipt_results = []
    for receipt in receipts:
        receipt_result = populate_receipt_record(receipt)
        receipt_results.append(receipt_result)
    # response
    return jsonify({
        'data': receipt_results,
        'recordsFiltered': total_filtered_receipts,
        'recordsTotal': total_receipts,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500
