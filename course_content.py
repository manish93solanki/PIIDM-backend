from flask import current_app as app, request, Blueprint, jsonify, send_file
from sqlalchemy import or_
import datetime
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

course_content_bp = Blueprint('course_content_bp', __name__, url_prefix='/api/course_content')


def is_course_content_name_exists(name):
    cursor = app.session.query(model.CourseContent).filter(
        model.CourseContent.name == name,
        model.CourseContent.deleted == 0
    )
    records = list(cursor)
    return records


def fetch_course_content_by_id(course_content_id):
    record = app.session.query(model.CourseContent).filter(
        model.CourseContent.course_content_id == course_content_id,
        model.CourseContent.deleted == 0
    ).first()
    return record


def populate_course_content_record(course_content):
    course_content_result = {}
    for key in course_content.__table__.columns.keys():
        value = getattr(course_content, key)
        course_content_result[key] = value
    return course_content_result


@course_content_bp.route('/add', methods=['POST'])
@token_required
def add_course_content(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                course_content = model.CourseContent()
                # Check if course_content is already exist
                if is_course_content_name_exists(item['name']):
                    return {'error': 'Course Content name is already exist.'}, 409
                for key, value in item.items():
                    setattr(course_content, key, value)
                records_to_add.append(course_content)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_bp.route('/update/<course_content_id>', methods=['PUT'])
@token_required
def update_course_content(current_user, course_content_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            course_content = fetch_course_content_by_id(int(course_content_id))
            # Check if course_content is already exist
            if 'name' in item and course_content.name != item['name'] and is_course_content_name_exists(item['name']):
                return {'error': 'Course Content name is already exist.'}, 409
            for key, value in item.items():
                setattr(course_content, key, value)
            records_to_add.append(course_content)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_bp.route('/delete/<course_content_id>', methods=['DELETE'])
@token_required
def soft_delete_course_content(current_user, course_content_id):
    try:
        course_content = fetch_course_content_by_id(int(course_content_id))
        course_content.deleted = 1
        insert_single_record(course_content)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_bp.route('/select/<course_content_id>', methods=['GET'])
@token_required
def get_course_content(current_user, course_content_id):
    course_content = app.session.query(model.CourseContent).filter(model.CourseContent.course_content_id == int(course_content_id),
                                                      model.CourseContent.deleted == 0).first()
    course_content_result = populate_course_content_record(course_content)
    return jsonify(course_content_result), 200


@course_content_bp.route('/all', methods=['GET'])
@token_required
def get_course_contents(current_user):
    cursor = app.session.query(model.CourseContent).all()
    course_contents = list(cursor)
    results = []
    for course_content in course_contents:
        res = {}
        for key in course_content.__table__.columns.keys():
            value = getattr(course_content, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@course_content_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_course_contents_advanced(current_user):
    # try:
    total_course_contents = model.CourseContent.query.filter(model.CourseContent.deleted == 0).count()

    # filtering data
    query = app.session.query(model.CourseContent)
    query = query.filter(model.CourseContent.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.CourseContent.name.like(f'{search_term}%')) if search_term else query

    total_filtered_course_contents = query.count()  # total filtered course_contents
    basic_stats = {
        'total_course_contents': total_filtered_course_contents
    }

    query = query.offset(start).limit(length)

    course_contents = query.all()
    course_content_results = []
    for course_content in course_contents:
        course_content_result = populate_course_content_record(course_content)
        course_content_results.append(course_content_result)
    # response
    return jsonify({
        'data': course_content_results,
        'recordsFiltered': total_filtered_course_contents,
        'recordsTotal': total_course_contents,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500


@course_content_bp.route('/upload-image', methods=['POST'])
@token_required
def upload_image(current_user):
    image = request.files["image"]
    image_path = f'data/uploaded_course_feature_images/{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}-{image.filename}'
    image.save(image_path)
    return jsonify({'message': 'Image uploaded successfully.', 'data': image_path}), 201


@course_content_bp.route('/get-image', methods=['GET'])
def get_image():
    image_path = request.args.get('image_path')
    return send_file(image_path, mimetype='image/gif')

