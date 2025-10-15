from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_, desc
import model
from auth_middleware import token_required
from db_operations import bulk_insert

hr_bp = Blueprint('hr_bp', __name__, url_prefix='/api/hr')


def is_hr_phone_num_exists(phone_num):
    cursor = app.session.query(model.HR).filter(
            model.HR.phone_num == phone_num,
    )
    records = list(cursor)
    return records


def is_hr_email_exists(email):
    cursor = app.session.query(model.HR).filter(model.HR.email == email)
    records = list(cursor)
    return records


def fetch_hr_by_id(hr_id):
    record = app.session.query(model.HR).filter(model.HR.hr_id == hr_id).first()
    return record


def fetch_user_by_hr_id(user_id):
    record = app.session.query(model.User).filter(model.User.user_id == user_id).first()
    return record


def populate_hr_record(hr):
    hr_result = {}
    for key in hr.__table__.columns.keys():
        value = getattr(hr, key)
        if key == 'user_id':
            user = fetch_user_by_hr_id(value)
            is_active = getattr(user, 'is_active')
            hr_result['is_active'] = is_active
        hr_result[key] = value
    return hr_result


@hr_bp.route('/add', methods=['POST'])
@token_required
def add_hr(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                hr = model.HR()
                # Check if hr is already exist
                if is_hr_phone_num_exists(item['phone_num']):
                    return {'error': 'Phone number is already exist.'}, 409
                if is_hr_email_exists(item['email']):
                    return {'error': 'Email is already exist.'}, 409
                for key, value in item.items():
                    setattr(hr, key, value)
                records_to_add.append(hr)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@hr_bp.route('/update/<hr_id>', methods=['PUT'])
@token_required
def update_hr(current_user, hr_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            hr = fetch_hr_by_id(int(hr_id))

            # Check if hr is already exist
            if 'phone_num' in item and hr.phone_num != item['phone_num'] and is_hr_phone_num_exists(item['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if 'email' in item and hr.email != item['email'] and is_hr_email_exists(item['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in item.items():
                setattr(hr, key, value)
            records_to_add.append(hr)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@hr_bp.route('/update/deactivate/<hr_id>', methods=['PUT'])
@token_required
def deactivate_hr(current_user, hr_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        records_to_add = []
        hr = fetch_hr_by_id(int(hr_id))
        user = fetch_user_by_hr_id(int(hr.user_id))
        user.is_active = 1 if user.is_active == 0 else 0
        records_to_add.append(user)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@hr_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_hr_by_email_or_phone_num(current_user):
    hr = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.HR).filter(model.HR.deleted == 0)
    if email:
        query = query.filter(model.HR.email == email)
    else:
        query = query.filter(model.HR.phone_num == phone_num)
    hr = query.first()
    result = {}
    if hr:
        for key in hr.__table__.columns.keys():
            value = getattr(hr, key)
            result[key] = value
    return jsonify(result), 200


@hr_bp.route('/delete/<hr_id>', methods=['DELETE'])
@token_required
def soft_delete_hr(current_user, hr_id):
    try:
        hr = fetch_hr_by_id(int(hr_id))
        hr.deleted = 1
        insert_single_record(hr)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@hr_bp.route('/select/<hr_id>', methods=['GET'])
@token_required
def get_hr(current_user, hr_id):
    hr = app.session.query(model.HR).filter(model.HR.hr_id == int(hr_id),
                                                      model.HR.deleted == 0).first()
    hr_result = populate_hr_record(hr)
    return jsonify(hr_result), 200


@hr_bp.route('/all', methods=['GET'])
@token_required
def get_all_hr(current_user):
    query = app.session.query(model.HR).filter(model.HR.deleted == 0)
    cursor = query.all()
    hr = list(cursor)
    results = []
    for hr in hr:
        res = {}
        for key in hr.__table__.columns.keys():
            value = getattr(hr, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@hr_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_hr_advanced(current_user):
    total_hr = model.HR.query.filter(model.HR.deleted == 0).count()

    # filtering data
    query = app.session.query(model.HR)
    query = query.filter(model.HR.deleted == 0)

    if current_user.user_role_id == 2:  # role == hr
        hr_id = app.session.query(model.HR.hr_id).filter(model.HR.user_id == current_user.user_id).first()
        if hr_id:
            hr_id = hr_id[0]
        query = query.filter(model.HR.hr_id == hr_id)
        total_hr = model.HR.query.filter(model.HR.deleted == 0,
                                                model.HR.hr_id == hr_id).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(or_(
        model.HR.name.like(f'%{search_term}%'),
        model.HR.phone_num.like(f'%{search_term}%'),
        model.HR.email.like(f'{search_term}%'),
    )) if search_term else query

    total_filtered_hr = query.count()  # total filtered hr
    basic_stats = {
        'total_hr': total_filtered_hr
    }

    query = query.order_by(desc(model.HR.created_at)).offset(start).limit(length)

    hr = query.all()
    hr_results = []
    for hr in hr:
        hr_result = populate_hr_record(hr)
        hr_results.append(hr_result)
    # response
    return jsonify({
        'data': hr_results,
        'recordsFiltered': total_filtered_hr,
        'recordsTotal': total_hr,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
