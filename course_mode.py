from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_

import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

course_mode_bp = Blueprint('course_mode_bp', __name__, url_prefix='/api/course_mode')


def is_course_mode_name_exists(name):
    cursor = app.session.query(model.CourseMode).filter(model.CourseMode.name == name)
    records = list(cursor)
    return records


def fetch_course_mode_by_id(course_mode_id):
    record = app.session.query(model.CourseMode).filter(model.CourseMode.course_mode_id == course_mode_id).first()
    return record


def populate_course_mode_record(course_mode):
    course_mode_result = {}
    for key in course_mode.__table__.columns.keys():
        value = getattr(course_mode, key)
        course_mode_result[key] = value
    return course_mode_result


@course_mode_bp.route('/add', methods=['POST'])
@token_required
def add_course_mode(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                course_mode = model.CourseMode()
                # Check if course_mode is already exist
                if is_course_mode_name_exists(item['name']):
                    return {'error': 'CourseMode name is already exist.'}, 409
                for key, value in item.items():
                    setattr(course_mode, key, value)
                records_to_add.append(course_mode)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_mode_bp.route('/update/<course_mode_id>', methods=['PUT'])
@token_required
def update_course_mode(current_user, course_mode_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            course_mode = fetch_course_mode_by_id(int(course_mode_id))
            # Check if course_mode is already exist
            if 'name' in item and course_mode.name != item['name'] and is_course_mode_name_exists(item['name']):
                return {'error': 'CourseMode name is already exist.'}, 409
            for key, value in item.items():
                setattr(course_mode, key, value)
            records_to_add.append(course_mode)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_mode_bp.route('/delete/<course_mode_id>', methods=['DELETE'])
@token_required
def soft_delete_course_mode(current_user, course_mode_id):
    try:
        course_mode = fetch_course_mode_by_id(int(course_mode_id))
        course_mode.deleted = 1
        insert_single_record(course_mode)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_mode_bp.route('/select/<course_mode_id>', methods=['GET'])
@token_required
def get_course_mode(current_user, course_mode_id):
    course_mode = app.session.query(model.CourseMode).filter(model.CourseMode.course_mode_id == int(course_mode_id),
                                                      model.CourseMode.deleted == 0).first()
    course_mode_result = populate_course_mode_record(course_mode)
    return jsonify(course_mode_result), 200


@course_mode_bp.route('/all', methods=['GET'])
@token_required
def get_course_modes(current_user):
    cursor = app.session.query(model.CourseMode).all()
    course_modes = list(cursor)
    results = []
    for course_mode in course_modes:
        res = {}
        for key in course_mode.__table__.columns.keys():
            value = getattr(course_mode, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@course_mode_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_course_modes_advanced(current_user):
    # try:
    total_course_modes = model.CourseMode.query.filter(model.CourseMode.deleted == 0).count()

    # filtering data
    query = app.session.query(model.CourseMode)
    query = query.filter(model.CourseMode.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.CourseMode.name.like(f'{search_term}%')) if search_term else query

    total_filtered_course_modes = query.count()  # total filtered course_modes
    basic_stats = {
        'total_course_modes': total_filtered_course_modes
    }

    query = query.offset(start).limit(length)

    course_modes = query.all()
    course_mode_results = []
    for course_mode in course_modes:
        course_mode_result = populate_course_mode_record(course_mode)
        course_mode_results.append(course_mode_result)
    # response
    return jsonify({
        'data': course_mode_results,
        'recordsFiltered': total_filtered_course_modes,
        'recordsTotal': total_course_modes,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500

