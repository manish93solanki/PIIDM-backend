from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_, desc
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record

agent_bp = Blueprint('agent_bp', __name__, url_prefix='/api/agent')


def is_agent_phone_num_exists(phone_num):
    cursor = app.session.query(model.Agent).filter(
            model.Agent.phone_num == phone_num,
    )
    records = list(cursor)
    return records


def is_agent_email_exists(email):
    cursor = app.session.query(model.Agent).filter(model.Agent.email == email)
    records = list(cursor)
    return records


def fetch_agent_by_id(agent_id):
    record = app.session.query(model.Agent).filter(model.Agent.agent_id == agent_id).first()
    return record


def populate_agent_record(agent):
    agent_result = {}
    for key in agent.__table__.columns.keys():
        value = getattr(agent, key)
        agent_result[key] = value
    return agent_result


@agent_bp.route('/add', methods=['POST'])
@token_required
def add_agent(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                agent = model.Agent()
                # Check if agent is already exist
                if is_agent_phone_num_exists(item['phone_num']):
                    return {'error': 'Phone number is already exist.'}, 409
                if is_agent_email_exists(item['email']):
                    return {'error': 'Email is already exist.'}, 409
                for key, value in item.items():
                    setattr(agent, key, value)
                records_to_add.append(agent)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@agent_bp.route('/update/<agent_id>', methods=['PUT'])
@token_required
def update_agent(current_user, agent_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            agent = fetch_agent_by_id(int(agent_id))

            # Check if agent is already exist
            if 'phone_num' in item and agent.phone_num != item['phone_num'] and is_agent_phone_num_exists(item['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if 'email' in item and agent.email != item['email'] and is_agent_email_exists(item['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in item.items():
                setattr(agent, key, value)
            records_to_add.append(agent)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@agent_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_agent_by_email_or_phone_num(current_user):
    agent = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.Agent).filter(model.Agent.deleted == 0)
    if email:
        query = query.filter(model.Agent.email == email)
    else:
        query = query.filter(model.Agent.phone_num == phone_num)
    agent = query.first()
    result = {}
    if agent:
        for key in agent.__table__.columns.keys():
            value = getattr(agent, key)
            result[key] = value
    return jsonify(result), 200


@agent_bp.route('/delete/<agent_id>', methods=['DELETE'])
@token_required
def soft_delete_agent(current_user, agent_id):
    try:
        agent = fetch_agent_by_id(int(agent_id))
        agent.deleted = 1
        insert_single_record(agent)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@agent_bp.route('/select/<agent_id>', methods=['GET'])
@token_required
def get_agent(current_user, agent_id):
    agent = app.session.query(model.Agent).filter(model.Agent.agent_id == int(agent_id),
                                                      model.Agent.deleted == 0).first()
    agent_result = populate_agent_record(agent)
    return jsonify(agent_result), 200


@agent_bp.route('/all', methods=['GET'])
@token_required
def get_agents(current_user):
    query = app.session.query(model.Agent).filter(model.Agent.deleted == 0)
    module = request.args.get('module', None)
    if module and (module in ['lead', 'student']):
        cursor = query.all()
    else:
        if current_user.user_role_id == 2:
            cursor = query.filter(model.Agent.user_id == current_user.user_id).all()
        else:
            cursor = query.all()

    agents = list(cursor)
    results = []
    for agent in agents:
        res = {}
        for key in agent.__table__.columns.keys():
            value = getattr(agent, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@agent_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_agents_advanced(current_user):
    # try:
    total_agents = model.Agent.query.filter(model.Agent.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Agent)
    query = query.filter(model.Agent.deleted == 0)

    if current_user.user_role_id == 2:  # role == agent
        agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
        if agent_id:
            agent_id = agent_id[0]
        query = query.filter(model.Agent.agent_id == agent_id)
        total_agents = model.Agent.query.filter(model.Agent.deleted == 0,
                                                model.Agent.agent_id == agent_id).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(or_(
        model.Agent.name.like(f'{search_term}%'),
        model.Agent.phone_num.like(f'%{search_term}%'),
        model.Agent.email.like(f'{search_term}%'),
    )) if search_term else query

    total_filtered_agents = query.count()  # total filtered agents
    basic_stats = {
        'total_agents': total_filtered_agents
    }

    query = query.order_by(desc(model.Agent.created_at)).offset(start).limit(length)

    agents = query.all()
    agent_results = []
    for agent in agents:
        agent_result = populate_agent_record(agent)
        agent_results.append(agent_result)
    # response
    return jsonify({
        'data': agent_results,
        'recordsFiltered': total_filtered_agents,
        'recordsTotal': total_agents,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500
