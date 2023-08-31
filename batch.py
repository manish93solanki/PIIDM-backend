from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert
import datetime

batch_bp = Blueprint('batch_bp', __name__, url_prefix='/api/batch')


def is_batch_name_exists(name):
    cursor = app.session.query(model.Batch).filter(
            model.Batch.name == name
    )
    records = list(cursor)
    return records


def fetch_batch_by_id(batch_id):
    record = app.session.query(model.Batch).filter(model.Batch.batch_id == batch_id).first()
    return record


def populate_batch_record(batch):
    batch_result = {}
    for key in batch.__table__.columns.keys():
        value = getattr(batch, key)
        if key in ('batch_date', ) and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)

        batch_result[key] = value

        if key == 'branch_id':
            branch = batch.branch
            batch_result[key] = {}
            for branch_key in branch.__table__.columns.keys():
                branch_value = getattr(branch, branch_key)
                batch_result[key][branch_key] = branch_value
            batch_result['branch'] = batch_result.pop(key)
        if key == 'course_id':
            course = batch.course
            batch_result[key] = {}
            for course_key in course.__table__.columns.keys():
                course_value = getattr(course, course_key)
                batch_result[key][course_key] = course_value
            batch_result['course'] = batch_result.pop(key)
        if key == 'course_mode_id':
            course_mode = batch.course_mode
            batch_result[key] = {}
            for course_mode_key in course_mode.__table__.columns.keys():
                course_mode_value = getattr(course_mode, course_mode_key)
                batch_result[key][course_mode_key] = course_mode_value
            batch_result['course_mode'] = batch_result.pop(key)
        if key == 'batch_time_id':
            batch_time = batch.batch_time
            batch_result[key] = {}
            for batch_time_key in batch_time.__table__.columns.keys():
                batch_time_value = getattr(batch_time, batch_time_key)
                batch_result[key][batch_time_key] = batch_time_value
            batch_result['batch_time'] = batch_result.pop(key)
        if key == 'trainer_id':
            trainer = batch.trainer
            batch_result[key] = {}
            for trainer_key in trainer.__table__.columns.keys():
                trainer_value = getattr(trainer, trainer_key)
                batch_result[key][trainer_key] = trainer_value
            batch_result['trainer'] = batch_result.pop(key)
    return batch_result


@batch_bp.route('/add', methods=['POST'])
@token_required
def add_batch(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        print('data: ', data)
        records_to_add = []
        for item in data:
            batch = model.Batch()
            # Check if batch is already exist
            if is_batch_name_exists(item['name']):
                return {'error': 'Batch name is already exist.'}, 409
            for key, value in item.items():
                if key in ('batch_date', ) and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(batch, key, value)
            records_to_add.append(batch)
        bulk_insert(records_to_add)
    return {}


@batch_bp.route('/update/<batch_id>', methods=['PUT'])
@token_required
def update_batch(current_user, batch_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            batch = fetch_batch_by_id(int(batch_id))
            # Check if batch is already exist
            if 'name' in item and batch.name != item['name'] and is_batch_name_exists(item['name']):
                return {'error': 'Batch name is already exist.'}, 409
            for key, value in item.items():
                if key in ('batch_date', ) and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(batch, key, value)
            records_to_add.append(batch)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@batch_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_batch(current_user, delete_id):
    app.session.query(model.Batch).filter(model.Batch.batch_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@batch_bp.route('/all', methods=['GET'])
@token_required
def get_batches(current_user):
    cursor = app.session.query(model.Batch).all()
    batches = list(cursor)
    results = []
    for batch in batches:
        res = {}
        for key in batch.__table__.columns.keys():
            value = getattr(batch, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@batch_bp.route('/select/<batch_id>', methods=['GET'])
@token_required
def get_batch(current_user, batch_id):
    batch = app.session.query(model.Batch).filter(model.Batch.batch_id == int(batch_id),
                                                      model.Batch.deleted == 0).first()
    batch_result = populate_batch_record(batch)
    print(batch_result)
    return jsonify(batch_result), 200


@batch_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_batch_advanced(current_user):
    total_batches = model.Batch.query.filter(model.Batch.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Batch)
    query = query.filter(model.Batch.deleted == 0)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.Batch.name.like(f'{search_term}%')) if search_term else query

    total_filtered_batch = query.count()  # total filtered batch
    basic_stats = {
        'total_batches': total_filtered_batch
    }

    query = query.offset(start).limit(length)

    batches = query.all()
    batch_results = []
    for batch in batches:
        batch_result = populate_batch_record(batch)
        batch_results.append(batch_result)
    # response
    return jsonify({
        'data': batch_results,
        'recordsFiltered': total_filtered_batch,
        'recordsTotal': total_batches,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
