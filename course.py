from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_

import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

course_bp = Blueprint('course_bp', __name__, url_prefix='/api/course')


def is_course_name_exists(name):
    cursor = app.session.query(model.Course).filter(model.Course.name == name)
    records = list(cursor)
    return records


def fetch_course_by_id(course_id):
    record = app.session.query(model.Course).filter(model.Course.course_id == course_id).first()
    return record


def populate_course_record(course):
    course_result = {}
    for key in course.__table__.columns.keys():
        value = getattr(course, key)
        course_result[key] = value
    return course_result


@course_bp.route('/add', methods=['POST'])
@token_required
def add_course(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                course = model.Course()
                # Check if course is already exist
                if is_course_name_exists(item['name']):
                    return {'error': 'Course name is already exist.'}, 409
                for key, value in item.items():
                    setattr(course, key, value)
                records_to_add.append(course)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_bp.route('/update/<course_id>', methods=['PUT'])
@token_required
def update_course(current_user, course_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            course = fetch_course_by_id(int(course_id))
            # Check if course is already exist
            if 'name' in item and course.name != item['name'] and is_course_name_exists(item['name']):
                return {'error': 'Course name is already exist.'}, 409
            for key, value in item.items():
                setattr(course, key, value)
            records_to_add.append(course)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_bp.route('/delete/<course_id>', methods=['DELETE'])
@token_required
def soft_delete_course(current_user, course_id):
    try:
        course = fetch_course_by_id(int(course_id))
        course.deleted = 1
        insert_single_record(course)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_bp.route('/select/<course_id>', methods=['GET'])
@token_required
def get_course(current_user, course_id):
    course = app.session.query(model.Course).filter(model.Course.course_id == int(course_id),
                                                      model.Course.deleted == 0).first()
    course_result = populate_course_record(course)
    return jsonify(course_result), 200


@course_bp.route('/all', methods=['GET'])
@token_required
def get_courses(current_user):
    cursor = app.session.query(model.Course).all()
    courses = list(cursor)
    results = []
    for course in courses:
        res = {}
        for key in course.__table__.columns.keys():
            value = getattr(course, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@course_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_courses_advanced(current_user):
    # try:
    total_courses = model.Course.query.filter(model.Course.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Course)
    query = query.filter(model.Course.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.Course.name.like(f'{search_term}%')) if search_term else query

    total_filtered_courses = query.count()  # total filtered courses
    basic_stats = {
        'total_courses': total_filtered_courses
    }

    query = query.offset(start).limit(length)

    courses = query.all()
    course_results = []
    for course in courses:
        course_result = populate_course_record(course)
        course_results.append(course_result)
    # response
    return jsonify({
        'data': course_results,
        'recordsFiltered': total_filtered_courses,
        'recordsTotal': total_courses,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500

