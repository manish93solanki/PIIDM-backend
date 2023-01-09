import datetime
from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert, insert_single_record
from sqlalchemy import or_

student_bp = Blueprint('student_bp', __name__, url_prefix='/api/students')

DEFAULT_COUNTRY = 'India'
DEFAULT_CITY = 'Pune'
DEFAULT_BRANCH = 'FC Road, Pune'
DEFAULT_SOURCE = 'Google'
DEFAULT_COURSE = 'Online Digital Marketing'
DEFAULT_BATCH_TIME = 'Morning'
DEFAULT_AGENT = 'Morning'


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
        )
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


def populate_student_record(student):
    student_result = {}
    for key in student.__table__.columns.keys():
        value = getattr(student, key)
        if key in ('admission_date', ) and value:
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


def get_all_receipts_by_student(student_id):
    cursor = app.session.query(model.Receipt).filter(model.Receipt.student_id == student_id,
                                                     model.Receipt.deleted == 0).all()
    records = list(cursor)
    return records


def populate_receipt_record(receipt):
    receipt_result = {}
    for key in receipt.__table__.columns.keys():
        value = getattr(receipt, key)
        if key in ('installment_payment_date', ) and value:
            value = str(value)
        if key in ('installment_payment_mode', ) and value:
            value = value.value
        receipt_result[key] = value
    return receipt_result


@student_bp.route('/add', methods=['POST'])
def add_student():
    if request.method == 'POST':
        if not request.is_json:
            return {'message': 'Bad Request.'}, 400
        data = request.get_json()
        student = model.Student()
        # Check if student is already exist
        if is_student_phone_num_exists(data['phone_num']):
            return {'message': 'Phone number is already exist.'}, 409
        if is_student_alternate_phone_num_exists(data['alternate_phone_num']):
            return {'message': 'Alternate Phone number is already exist.'}, 409
        if is_student_email_exists(data['email']):
            return {'message': 'Email is already exist.'}, 409
        for key, value in data.items():
            if key in ('admission_date',) and value:
                value = datetime.datetime.strptime(value, '%Y-%m-%d')
            setattr(student, key, value)
        return_status, student = insert_single_record(student)
        if not return_status:
            return {'message': 'Error, Something wrong in student details.'}, 500

        # Add installment in receipt model
        receipts_records_to_add = []
        for instalment in data['installments']:
            if 'installment_payment' in instalment and instalment['installment_payment']:
                receipt = model.Receipt()
                receipt.installment_payment = instalment['installment_payment']
                setattr(receipt, 'installment_payment_date',
                        datetime.datetime.strptime(instalment['installment_payment_date'], '%Y-%m-%d'))
                receipt.installment_payment_mode = instalment['installment_payment_mode']
                receipt.student_id = student.student_id
                receipts_records_to_add.append(receipt)
        bulk_insert(receipts_records_to_add)
    return {'message': 'Successfully Inserted.'}, 200


@student_bp.route('/update/<student_id>', methods=['PUT'])
def update_student(student_id):
    if not request.is_json:
        return {'message': 'Bad Request.'}, 400
    data = request.get_json()
    student = fetch_student_by_id(int(student_id))

    # Check if student is already exist
    if student.phone_num != data['phone_num'] and is_student_phone_num_exists(data['phone_num']):
        return {'message': 'Phone number is already exist.'}, 409
    if student.alternate_phone_num != data['alternate_phone_num'] and is_student_alternate_phone_num_exists(
            data['alternate_phone_num']):
        return {'message': 'Alternate Phone number is already exist.'}, 409
    if student.email != data['email'] and is_student_email_exists(data['email']):
        return {'message': 'Email is already exist.'}, 409
    for key, value in data.items():
        if key in ('admission_date', ) and value:
            value = datetime.datetime.strptime(value, '%Y-%m-%d')
        setattr(student, key, value)
    return_status, student = insert_single_record(student)
    if not return_status:
        return {'message': 'Error, Something wrong in student details.'}, 500

    # Add installment in receipt model
    receipts_records_to_add = []
    for instalment in data['installments']:
        if 'installment_payment' in instalment and instalment['installment_payment']:
            receipt = model.Receipt()
            receipt.installment_payment = instalment['installment_payment']
            setattr(receipt, 'installment_payment_date',
                    datetime.datetime.strptime(instalment['installment_payment_date'], '%Y-%m-%d'))
            receipt.installment_payment_mode = instalment['installment_payment_mode']
            receipt.student_id = student.student_id
            receipts_records_to_add.append(receipt)
    bulk_insert(receipts_records_to_add)
    return {'message': 'Successfully Updated.'}, 200


@student_bp.route('/delete/<student_id>', methods=['DELETE'])
def soft_delete_student(student_id):
    student = fetch_student_by_id(int(student_id))
    student.deleted = 1
    student.is_active = 0
    insert_single_record(student)
    # Why do we not delete receipts post student deletion?
    # Because if any payment was done for deleted student then
    # we need to keep track of the receipts, and considering them as an income.
    return {'message': 'Successfully deleted..'}, 200


@student_bp.route('/select/<student_id>', methods=['GET'])
def get_student(student_id):
    student = app.session.query(model.Student).filter(model.Student.student_id == int(student_id),
                                                      model.Student.deleted == 0).first()
    student_result = populate_student_record(student)
    student_result['installments'] = []

    # Get student receipts
    receipt_records = get_all_receipts_by_student(student.student_id)
    for receipt in receipt_records:
        receipt_result = populate_receipt_record(receipt)
        student_result['installments'].append(receipt_result)
        print(student_result['installments'])
    return jsonify(student_result), 200


@student_bp.route('/select-all', methods=['GET'])
def get_students():
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
def get_paginated_students(page_id):
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
