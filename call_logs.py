import datetime

from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert

call_logs_bp = Blueprint('call_logs_bp', __name__, url_prefix='/api/call_logs')


def is_agent_exist(user_phone_num):
    return app.session.query(model.Agent).filter(
        model.Agent.phone_num == f'+91-{user_phone_num}'
    ).first()


def fetch_existing_call_logs(phone_num, call_time, call_type):
    record = app.session.query(model.CallLogs).filter(
        model.CallLogs.phone_num == phone_num,
        model.CallLogs.call_time == call_time,
        model.CallLogs.call_type == call_type,
    ).order_by(model.CallLogs.call_logs_id.asc()).first()
    return record


@call_logs_bp.route('/add', methods=['POST'])
# @token_required
def add_call_logs():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        has_agent = False
        records_to_add = []
        user_id = None
        for item in data:
            user_phone_num = str(item['user_phone_num'])
            missing_zeros = 10 - len(user_phone_num)
            zeros_prefix = '0' * missing_zeros
            user_phone_num = f'{zeros_prefix}{user_phone_num}'
            if has_agent is False:
                agent = is_agent_exist(user_phone_num)
                user_id = agent.user_id
                if agent:
                    has_agent = True
            if has_agent is False:
                return {'message': 'User is invalid.'}, 201
            phone_num = item['phone_num']
            phone_num = phone_num[-10:]  # only last 10 digits
            call_time = datetime.datetime.strptime(item['call_time'], '%d-%m-%Y %H:%M:%S')
            call_type = item['call_type']
            record = fetch_existing_call_logs(phone_num, call_time, call_type)
            if record is None:
                call_logs = model.CallLogs()
                call_logs.phone_num = phone_num
                call_logs.call_time = call_time
                call_logs.call_type = call_type
                call_logs.call_time_duration = item['call_time_duration']
                call_logs.user_id = user_id
                records_to_add.append(call_logs)
        bulk_insert(records_to_add)
    return {'message': 'Call Logs are saved.'}, 201


@call_logs_bp.route('/delete/<delete_id>', methods=['DELETE'])
# @token_required
def delete_call_logs(current_user, delete_id):
    app.session.query(model.CallLogs).filter(model.CallLogs.call_logs_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@call_logs_bp.route('/all', methods=['GET'])
# @token_required
def get_call_logs(current_user):
    cursor = app.session.query(model.CallLogs).all()
    call_logs = list(cursor)
    results = []
    for call_logs in call_logs:
        res = {}
        for key in call_logs.__table__.columns.keys():
            value = getattr(call_logs, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
