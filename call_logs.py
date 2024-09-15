import datetime
import re
import requests
from flask import current_app as app, request, Blueprint, jsonify
import model
import helper
from auth_middleware import token_required
from db_operations import bulk_insert
from agent import fetch_agent_by_user_id

call_logs_bp = Blueprint('call_logs_bp', __name__, url_prefix='/api/call_logs')


def is_agent_exist(user_phone_num):
    return app.session.query(model.Agent).filter(
        model.Agent.phone_num == f'+91-{user_phone_num}'
    ).first()


def fetch_existing_call_logs(user_id, phone_num, call_time, call_type):
    record = app.session.query(model.CallLogs).filter(
        model.CallLogs.user_id == user_id,
        model.CallLogs.phone_num == phone_num,
        model.CallLogs.call_time == call_time,
        model.CallLogs.call_type == call_type,
    ).order_by(model.CallLogs.call_logs_id.asc()).first()
    return record


@call_logs_bp.route('/add', methods=['POST'])
@token_required
def add_call_logs(current_user):
    token = current_user.token
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        dict_agents_with_call_logs = {}
        user_id = None
        
        print('Total Call logs: ', len(data))
        # Sort by call_log datetime
        for item in data:
            # user_phone_num = str(item['user_phone_num'])
            # list_user_phone_num = re.findall('[0-9]+', user_phone_num)
            # user_phone_num = ''.join(list_user_phone_num)
            # user_phone_num = list_user_phone_num[-10:]
            user_id = int(item['user_id'])
            
            # Agent
            agent = fetch_agent_by_user_id(user_id)
            agent_id = agent.agent_id
            agent_name = agent.name
            if f'{agent_id}__{agent_name}' not in dict_agents_with_call_logs:
                dict_agents_with_call_logs[f'{agent_id}__{agent_name}'] = []
            

            phone_num = item['phone_num']
            phone_num = phone_num[-10:]  # only last 10 digits
            call_time = datetime.datetime.strptime(item['call_time'], '%d-%m-%Y %H:%M:%S')
            call_type = item['call_type']
            call_time_duration = item['call_time_duration']
            
            record = fetch_existing_call_logs(user_id, phone_num, call_time, call_type)
            if record is None:
                dict_call_logs = {
                    'phone_num': phone_num,
                    'call_time': call_time,
                    'call_type': call_type,
                    'call_time_duration': call_time_duration,
                    'user_id': user_id
                }
                dict_agents_with_call_logs[f'{agent_id}__{agent_name}'].append(dict_call_logs)

        new_dict_agents_with_call_logs = {}
        for agent_info, list_call_logs_by_agent in dict_agents_with_call_logs.items():
            list_call_logs_by_agent = sorted(list_call_logs_by_agent, key=lambda d: d['call_time'], reverse=True)
            new_dict_agents_with_call_logs[agent_info] = list_call_logs_by_agent
            print('Total call logs by agent: ', len(new_dict_agents_with_call_logs[agent_info]))
        

        records_to_add = []
        # Save call logs to remarks
        for agent_info, list_call_logs_by_agent in new_dict_agents_with_call_logs.items():
            agent_id, agent_name = agent_info.split('__')[0], agent_info.split('__')[1]
            for dict_call_log in list_call_logs_by_agent:
                phone_num = dict_call_log['phone_num']
                call_time = dict_call_log['call_time']
                call_type = dict_call_log['call_type']
                call_time_duration = dict_call_log['call_time_duration']
                user_id = dict_call_log['user_id']

                call_logs = model.CallLogs()
                call_logs.phone_num = phone_num
                call_logs.call_time = call_time
                call_logs.call_type = call_type
                call_logs.call_time_duration = call_time_duration
                call_logs.user_id = user_id
                records_to_add.append(call_logs)

                # Fetch lead_id
                headers = {'Authorization': f'Bearer {token}'}
                params = {'phone_num': f'+91-{phone_num}'}
                url = f'https://127.0.0.1:3002/api/leads/by_email_or_phone_num'
                lead_response = requests.get(url=url, headers=headers, params=params, verify=False)
                lead_response_status_code = lead_response.status_code
                lead_response_data = lead_response.json()
                print(lead_response, lead_response_status_code)
                
                if lead_response and lead_response_status_code == 200 and lead_response_data:
                    # Update remark, agent, updated_at for each load as per call log.
                    lead_id = lead_response_data['lead_id']
                    course_id = lead_response_data['course_id']
                    phone_num = lead_response_data['phone_num']
                    old_remarks = lead_response_data['remarks']
                    headers = {'Authorization': f'Bearer {token}'}
                    data = [{
                        'phone_num': phone_num, 
                        'lead_id': lead_id,
                        'course_id': course_id,
                        'remarks': f'By({agent_name}) {helper.format_datetime_1(call_time)} - {call_type} for {call_time_duration} duration. <br> {old_remarks}',
                        'updated_at': str(datetime.datetime.now()),
                        'updated_by_id': agent_id
                    }]
                    url = f'https://127.0.0.1:3002/api/leads/update/{lead_id}'
                    lead_response = requests.put(url=url, headers=headers, json=data, verify=False)
                    lead_response_status_code = lead_response.status_code
                    lead_response_data = lead_response.json()
        print('Call logs - records_to_add: ', len(records_to_add))
        bulk_insert(records_to_add)

    return {'message': 'Call Logs are saved.'}, 201

"""
curl -H 'Content-Type: application/json' \
     -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770' \
     -d '[{ "user_id":1,"phone_num":"1123232453", "call_time": "01-01-2024 00:00:00", "call_type": "INCOMING", "call_time_duration": "00:10:00"}]' \
     -X POST \
     http://127.0.0.1:3002/api/call_logs/add
"""

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
