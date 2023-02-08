import uuid
import json
import requests
from rich import print
from sqlalchemy import create_engine

engine = None
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770'


def generate_random_string():
    random_string = uuid.uuid4().hex[:10].upper()
    return random_string


def sql_engine():
    global engine
    conn_string = f'mysql://piidm_dev:piidm_dev_password123@localhost:3306/u776183671_piidm'
    engine = create_engine(conn_string)


def select_query(query):
    global engine
    result = engine.execute(query)
    return list(result.mappings())


def insert_data(url, data, token=False):
    payload = data
    if token:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TOKEN}'
        }
    else:
        headers = {
            'Content-Type': 'application/json'
        }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in (200, 201):
        print("==*==" * 20)
        print(response.text)
        print("==*==" * 20)
        return False
    else:
        print(response.text)
        return True


def fetch_single_record(url, data):
    global TOKEN
    payload = data
    headers = {
        'Authorization': f'Bearer {TOKEN}'
    }
    response = requests.get(url, headers=headers, params=payload)
    if response.status_code != 200:
        print("==*==" * 20)
        print(response.json())
        print("==*==" * 20)
    # else:
    #     print(response.json())
    return response.json()


if __name__ == '__main__':
    base_url = 'http://127.0.0.1:3002/api'
    sql_engine()
    # user_query = 'select * from users'
    # users = select_query(user_query)
    # # create user
    # for user in users:
    #     if user['user_type'] == 'admin':
    #         continue
    #     email_phone = user['email']
    #     email = email_phone if '@' in email_phone else generate_random_string() + '@test.com'
    #     phone_num = email_phone if '@' not in email_phone else generate_random_string()
    #     user_role_id = 2 if user['user_type'] == 'agent' else 3
    #     password = "agent_123" if user['user_type'] == 'agent' else "student123"
    #     data = {
    #         'name': user['name'],
    #         'phone_num': phone_num,
    #         'email': email,
    #         'password': password,
    #         'user_role_id': user_role_id,
    #     }
    #     print(data)
    #     url = f'{base_url}/user/add'
    #     insert_data(url, data)  # insert records

    # # create agent
    # agent_query = 'select * from agent'
    # agents = select_query(agent_query)
    # # create user
    # for agent in agents:
    #     print()
    #     email = agent['agent_email']
    #     if email == 'na':
    #         continue
    #     phone_num = agent['agent_contact_number']
    #
    #     # get user by email or phone_num
    #     url = f'{base_url}/user/by_email_or_phone_num'
    #     user_query_params = {
    #         'phone_num': phone_num,
    #         'email': email
    #     }
    #     # print('user_query_params: ', user_query_params)
    #     our_user = fetch_single_record(url, user_query_params)  # fetch all users
    #     if our_user:
    #         user_id = our_user['user_id']
    #         print('user_id: ', user_id)
    #
    #         data = [{
    #             'name': agent['agent_name'],
    #             'phone_num': phone_num,
    #             'email': email,
    #             'user_id': user_id
    #         }]
    #         print(data)
    #         url = f'{base_url}/agent/add'
    #         return_flag = insert_data(url, data, token=True)  # insert records
    #         if return_flag is False:
    #             # Due to duplicate phone_num in your_records so replaced with random phone_num
    #             data = [{
    #                 'name': agent['agent_name'],
    #                 'phone_num': generate_random_string(),
    #                 'email': email,
    #                 'user_id': user_id
    #             }]
    #             print(data)
    #             url = f'{base_url}/agent/add'
    #             return_flag = insert_data(url, data, token=True)  # insert records

