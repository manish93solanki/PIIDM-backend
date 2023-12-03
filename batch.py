from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert
import datetime
from sqlalchemy import desc


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
            # increment batch_num by 1.
            last_batch_num = app.session.query(model.Batch.batch_num).order_by(desc(model.Batch.batch_num)).first()
            if last_batch_num is None:
                last_batch_num = 1000  # Starting batch_num
            elif last_batch_num and last_batch_num[0] is not None:
                last_batch_num = last_batch_num[0]  # Starting batch_num
            last_batch_num += 1

            batch = model.Batch()
            setattr(batch, 'batch_num', last_batch_num)

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


@batch_bp.route('/update_and_get_seats/<student_id>/<batch_id>', methods=['PUT'])
@token_required
def update_and_get_seats_batch(current_user, student_id, batch_id):
    try:
        batch_id = int(batch_id)
        records_to_update = []
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400

        # Validation - Raise exception if the same student is allocated with same/different batches having same course.
        user_id = app.session.query(model.Student.user_id).filter(model.Student.student_id == int(student_id)).first()
        user_id = user_id[0]
        students = app.session.query(model.Student).filter(model.Student.user_id == int(user_id)).all()
        old_batches_course_ids = []
        for student in students:
            if student.student_id != int(student_id):
                # Ignore batch_id of current student_id
                old_batch = fetch_batch_by_id(int(student.batch_id))
                old_batches_course_ids.append(old_batch.course_id)
        if old_batches_course_ids:
            # Update Old Batch details
            if batch_id and batch_id != 'null':
                new_batch = fetch_batch_by_id(int(batch_id))
                if new_batch.course_id in old_batches_course_ids:
                    return {'error': 'Selected batch has the same course which is already allocated to current student. '
                                     '<br> Please select different batch'}, 400

        # Update Batch and adjust seats
        add_and_sub_seat_by_1 = 1

        old_batch_id = app.session.query(model.Student.batch_id).filter(model.Student.student_id == int(student_id)).first()
        old_batch_id = old_batch_id[0]
        if old_batch_id:
            # Update Old Batch details
            batch = fetch_batch_by_id(int(old_batch_id))
            batch.seats_occupied -= int(add_and_sub_seat_by_1)
            batch.seats_vacant += int(add_and_sub_seat_by_1)
            records_to_update.append(batch)

        # Update Batch with new details
        if batch_id and batch_id != 'null':
            batch = fetch_batch_by_id(batch_id)
            batch.seats_occupied += int(add_and_sub_seat_by_1)
            batch.seats_vacant -= int(add_and_sub_seat_by_1)
            records_to_update.append(batch)

        if records_to_update:
            bulk_insert(records_to_update)

        current_batch = {}
        all_batches = get_all_batches()  # All batches
        if batch_id and batch_id != 'null':
            for dict_batch in all_batches:
                if dict_batch['batch_id'] == batch_id:
                    current_batch = dict_batch
                    break
        results = {'all_batches': all_batches, 'current_batch': current_batch}
        return jsonify(results), 200
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
    results = get_all_batches()
    return jsonify(results), 200


def get_all_batches():
    cursor = app.session.query(model.Batch).all()
    batches = list(cursor)
    results = []
    for batch in batches:
        res = {}
        for key in batch.__table__.columns.keys():
            value = getattr(batch, key)
            res[key] = value
        results.append(res)
    return results


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

    query = query.order_by(desc(model.Batch.batch_date)).offset(start).limit(length)

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
