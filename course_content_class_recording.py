from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_

import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

course_content_class_recording_bp = Blueprint('course_content_class_recording_bp', __name__, url_prefix='/api/course_content_class_recording')


def is_course_content_class_recording_name_exists(name):
    cursor = app.session.query(model.CourseContentClassRecording).filter(
        model.CourseContentClassRecording.name == name,
        model.CourseContentClassRecording.deleted == 0
    )
    records = list(cursor)
    return records


def fetch_course_content_class_recording_by_id(course_content_class_recording_id):
    record = app.session.query(model.CourseContentClassRecording).filter(
        model.CourseContentClassRecording.course_content_class_recording_id == course_content_class_recording_id,
        model.CourseContentClassRecording.deleted == 0
    ).first()
    return record


def populate_course_content_class_recording_record(course_content_class_recording):
    course_content_class_recording_result = {}
    for key in course_content_class_recording.__table__.columns.keys():
        value = getattr(course_content_class_recording, key)
        course_content_class_recording_result[key] = value
    return course_content_class_recording_result


@course_content_class_recording_bp.route('/add', methods=['POST'])
@token_required
def add_course_content_class_recording(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                course_content_class_recording = model.CourseContentClassRecording()
                # Check if course_content_class_recording is already exist
                if is_course_content_class_recording_name_exists(item['name']):
                    return {'error': 'Course Content Class Recording name is already exist.'}, 409
                for key, value in item.items():
                    setattr(course_content_class_recording, key, value)
                records_to_add.append(course_content_class_recording)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_class_recording_bp.route('/update/<course_content_class_recording_id>', methods=['PUT'])
@token_required
def update_course_content_class_recording(current_user, course_content_class_recording_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            course_content_class_recording = fetch_course_content_class_recording_by_id(int(course_content_class_recording_id))
            # Check if course_content_class_recording is already exist
            if 'name' in item and course_content_class_recording.name != item['name'] and is_course_content_class_recording_name_exists(item['name']):
                return {'error': 'Course Content Class Recording name is already exist.'}, 409
            for key, value in item.items():
                setattr(course_content_class_recording, key, value)
            records_to_add.append(course_content_class_recording)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_class_recording_bp.route('/delete/<course_content_class_recording_id>', methods=['DELETE'])
@token_required
def soft_delete_course_content_class_recording(current_user, course_content_class_recording_id):
    try:
        course_content_class_recording = fetch_course_content_class_recording_by_id(int(course_content_class_recording_id))
        course_content_class_recording.deleted = 1
        insert_single_record(course_content_class_recording)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@course_content_class_recording_bp.route('/select/<course_content_class_recording_id>', methods=['GET'])
@token_required
def get_course_content_class_recording(current_user, course_content_class_recording_id):
    course_content_class_recording = app.session.query(model.CourseContentClassRecording).filter(model.CourseContentClassRecording.course_content_class_recording_id == int(course_content_class_recording_id),
                                                      model.CourseContentClassRecording.deleted == 0).first()
    course_content_class_recording_result = populate_course_content_class_recording_record(course_content_class_recording)
    return jsonify(course_content_class_recording_result), 200


@course_content_class_recording_bp.route('/all', methods=['GET'])
@token_required
def get_course_content_class_recordings(current_user):
    cursor = app.session.query(model.CourseContentClassRecording).all()
    course_content_class_recordings = list(cursor)
    results = []
    for course_content_class_recording in course_content_class_recordings:
        res = {}
        for key in course_content_class_recording.__table__.columns.keys():
            value = getattr(course_content_class_recording, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@course_content_class_recording_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_course_content_class_recordings_advanced(current_user):
    # try:
    total_course_content_class_recordings = model.CourseContentClassRecording.query.filter(model.CourseContentClassRecording.deleted == 0).count()

    # filtering data
    query = app.session.query(model.CourseContentClassRecording)
    query = query.filter(model.CourseContentClassRecording.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.CourseContentClassRecording.name.like(f'{search_term}%')) if search_term else query

    total_filtered_course_content_class_recordings = query.count()  # total filtered course_content_class_recordings
    basic_stats = {
        'total_course_content_class_recordings': total_filtered_course_content_class_recordings
    }

    query = query.offset(start).limit(length)

    course_content_class_recordings = query.all()
    course_content_class_recording_results = []
    for course_content_class_recording in course_content_class_recordings:
        course_content_class_recording_result = populate_course_content_class_recording_record(course_content_class_recording)
        course_content_class_recording_results.append(course_content_class_recording_result)
    # response
    return jsonify({
        'data': course_content_class_recording_results,
        'recordsFiltered': total_filtered_course_content_class_recordings,
        'recordsTotal': total_course_content_class_recordings,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500

