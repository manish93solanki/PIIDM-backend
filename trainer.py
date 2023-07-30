from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_, desc
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

trainer_bp = Blueprint('trainer_bp', __name__, url_prefix='/api/trainer')


def is_trainer_phone_num_exists(phone_num):
    cursor = app.session.query(model.Trainer).filter(
            model.Trainer.phone_num == phone_num,
    )
    records = list(cursor)
    return records


def is_trainer_email_exists(email):
    cursor = app.session.query(model.Trainer).filter(model.Trainer.email == email)
    records = list(cursor)
    return records


def fetch_trainer_by_id(trainer_id):
    record = app.session.query(model.Trainer).filter(model.Trainer.trainer_id == trainer_id).first()
    return record


def populate_trainer_record(trainer):
    trainer_result = {}
    for key in trainer.__table__.columns.keys():
        value = getattr(trainer, key)
        trainer_result[key] = value
    return trainer_result


@trainer_bp.route('/add', methods=['POST'])
@token_required
def add_trainer(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                trainer = model.Trainer()
                # Check if trainer is already exist
                if is_trainer_phone_num_exists(item['phone_num']):
                    return {'error': 'Phone number is already exist.'}, 409
                if is_trainer_email_exists(item['email']):
                    return {'error': 'Email is already exist.'}, 409
                for key, value in item.items():
                    setattr(trainer, key, value)
                records_to_add.append(trainer)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@trainer_bp.route('/update/<trainer_id>', methods=['PUT'])
@token_required
def update_trainer(current_user, trainer_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            trainer = fetch_trainer_by_id(int(trainer_id))

            # Check if trainer is already exist
            if 'phone_num' in item and trainer.phone_num != item['phone_num'] and is_trainer_phone_num_exists(item['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if 'email' in item and trainer.email != item['email'] and is_trainer_email_exists(item['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in item.items():
                setattr(trainer, key, value)
            records_to_add.append(trainer)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@trainer_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_trainer_by_email_or_phone_num(current_user):
    trainer = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.Trainer).filter(model.Trainer.deleted == 0)
    if email:
        query = query.filter(model.Trainer.email == email)
    else:
        query = query.filter(model.Trainer.phone_num == phone_num)
    trainer = query.first()
    result = {}
    if trainer:
        for key in trainer.__table__.columns.keys():
            value = getattr(trainer, key)
            result[key] = value
    return jsonify(result), 200


@trainer_bp.route('/delete/<trainer_id>', methods=['DELETE'])
@token_required
def soft_delete_trainer(current_user, trainer_id):
    try:
        trainer = fetch_trainer_by_id(int(trainer_id))
        trainer.deleted = 1
        insert_single_record(trainer)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@trainer_bp.route('/select/<trainer_id>', methods=['GET'])
@token_required
def get_trainer(current_user, trainer_id):
    trainer = app.session.query(model.Trainer).filter(model.Trainer.trainer_id == int(trainer_id),
                                                      model.Trainer.deleted == 0).first()
    trainer_result = populate_trainer_record(trainer)
    return jsonify(trainer_result), 200


@trainer_bp.route('/all', methods=['GET'])
@token_required
def get_trainers(current_user):
    query = app.session.query(model.Trainer).filter(model.Trainer.deleted == 0)
    cursor = query.all()
    trainers = list(cursor)
    results = []
    for trainer in trainers:
        res = {}
        for key in trainer.__table__.columns.keys():
            value = getattr(trainer, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@trainer_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_trainers_advanced(current_user):
    # try:
    total_trainers = model.Trainer.query.filter(model.Trainer.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Trainer)
    query = query.filter(model.Trainer.deleted == 0)

    if current_user.user_role_id == 2:  # role == trainer
        trainer_id = app.session.query(model.Trainer.trainer_id).filter(model.Trainer.user_id == current_user.user_id).first()
        if trainer_id:
            trainer_id = trainer_id[0]
        query = query.filter(model.Trainer.trainer_id == trainer_id)
        total_trainers = model.Trainer.query.filter(model.Trainer.deleted == 0,
                                                model.Trainer.trainer_id == trainer_id).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(or_(
        model.Trainer.name.like(f'%{search_term}%'),
        model.Trainer.phone_num.like(f'%{search_term}%'),
        model.Trainer.email.like(f'{search_term}%'),
    )) if search_term else query

    total_filtered_trainers = query.count()  # total filtered trainers
    basic_stats = {
        'total_trainers': total_filtered_trainers
    }

    query = query.order_by(desc(model.Trainer.created_at)).offset(start).limit(length)

    trainers = query.all()
    trainer_results = []
    for trainer in trainers:
        trainer_result = populate_trainer_record(trainer)
        trainer_results.append(trainer_result)
    # response
    return jsonify({
        'data': trainer_results,
        'recordsFiltered': total_filtered_trainers,
        'recordsTotal': total_trainers,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500
