from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_

import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

course_category_bp = Blueprint('course_category_bp', __name__, url_prefix='/api/course_category')


def is_course_category_name_exists(name):
    cursor = app.session.query(model.CourseCategory).filter(model.CourseCategory.name == name)
    records = list(cursor)
    return records


def fetch_course_category_by_id(course_category_id):
    record = app.session.query(model.CourseCategory).filter(model.CourseCategory.course_category_id == course_category_id).first()
    return record


def populate_course_category_record(course_category):
    course_category_result = {}
    for key in course_category.__table__.columns.keys():
        value = getattr(course_category, key)
        course_category_result[key] = value
    return course_category_result


@course_category_bp.route('/add', methods=['POST'])
@token_required
def add_course_category(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                course_category = model.CourseCategory()
                # Check if course_category is already exist
                if is_course_category_name_exists(item['name']):
                    return {'error': 'CourseCategory name is already exist.'}, 409
                for key, value in item.items():
                    setattr(course_category, key, value)
                records_to_add.append(course_category)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_category_bp.route('/update/<course_category_id>', methods=['PUT'])
@token_required
def update_course_category(current_user, course_category_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            course_category = fetch_course_category_by_id(int(course_category_id))
            # Check if course_category is already exist
            if 'name' in item and course_category.name != item['name'] and is_course_category_name_exists(item['name']):
                return {'error': 'CourseCategory name is already exist.'}, 409
            for key, value in item.items():
                setattr(course_category, key, value)
            records_to_add.append(course_category)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_category_bp.route('/delete/<course_category_id>', methods=['DELETE'])
@token_required
def soft_delete_course_category(current_user, course_category_id):
    try:
        course_category = fetch_course_category_by_id(int(course_category_id))
        course_category.deleted = 1
        insert_single_record(course_category)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_category_bp.route('/select/<course_category_id>', methods=['GET'])
@token_required
def get_course_category(current_user, course_category_id):
    course_category = app.session.query(model.CourseCategory).filter(model.CourseCategory.course_category_id == int(course_category_id),
                                                      model.CourseCategory.deleted == 0).first()
    course_category_result = populate_course_category_record(course_category)
    return jsonify(course_category_result), 200


@course_category_bp.route('/select/course_category_by_name/<course_category_name>', methods=['GET'])
@token_required
def get_course_category_by_name(current_user, course_category_name):
    course_category = app.session.query(model.CourseCategory).filter(model.CourseCategory.name == course_category_name,
                                                    model.CourseCategory.deleted == 0).first()
    if course_category is None:
        # Ge default course_category
        course_category = app.session.query(model.CourseCategory).filter(model.CourseCategory.course_category_id == 1,
                                                        model.CourseCategory.deleted == 0).first()

    course_category_result = populate_course_category_record(course_category)
    return jsonify(course_category_result), 200


@course_category_bp.route('/all', methods=['GET'])
@token_required
def get_course_categories(current_user):
    cursor = app.session.query(model.CourseCategory).all()
    course_category = list(cursor)
    results = []
    for course_category in course_category:
        res = {}
        for key in course_category.__table__.columns.keys():
            value = getattr(course_category, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@course_category_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_course_category_advanced(current_user):
    # try:
    total_course_category = model.CourseCategory.query.filter(model.CourseCategory.deleted == 0).count()

    # filtering data
    query = app.session.query(model.CourseCategory)
    query = query.filter(model.CourseCategory.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.CourseCategory.name.like(f'%{search_term}%')) if search_term else query

    total_filtered_course_category = query.count()  # total filtered course_category
    basic_stats = {
        'total_course_category': total_filtered_course_category
    }

    query = query.offset(start).limit(length)

    course_category = query.all()
    course_category_results = []
    for course_category in course_category:
        course_category_result = populate_course_category_record(course_category)
        course_category_results.append(course_category_result)
    # response
    return jsonify({
        'data': course_category_results,
        'recordsFiltered': total_filtered_course_category,
        'recordsTotal': total_course_category,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500

