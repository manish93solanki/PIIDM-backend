import uuid
import json
import requests
from rich import print
from sqlalchemy import create_engine
from tqdm import tqdm


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
    global TOKEN
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
        # print(response.text)
        return True


def update_data(url, data, token=False):
    global TOKEN
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

    response = requests.put(url, headers=headers, data=json.dumps(payload))
    if response.status_code not in (200, 201):
        print("==*==" * 20)
        print(response.text)
        print("==*==" * 20)
        return False
    else:
        # print(response.text)
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
    #     # print(response.json())
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
    #     # print(data)
    #     url = f'{base_url}/user/add'
    #     insert_data(url, data)  # insert records

    # create agent
    agent_query = 'select * from agent'
    agents = select_query(agent_query)
    # create user
    for agent in tqdm(agents):
        # print()
        email = agent['agent_email']
        if email == 'na':
            continue
        phone_num = agent['agent_contact_number']

        u_data = {
            'name': agent['agent_name'],
            'phone_num': generate_random_string(),
            'email': email,
            'password': 'agent123',
            'user_role_id': 2
        }
        # print(u_data)
        url = f'{base_url}/user/add'
        insert_data(url, u_data)  # insert records

        # get user by email or phone_num
        url = f'{base_url}/user/by_email_or_phone_num'
        user_query_params = {
            # 'phone_num': phone_num,
            'email': email
        }
        # # print('user_query_params: ', user_query_params)
        our_user = fetch_single_record(url, user_query_params)  # fetch all users
        if our_user:
            user_id = our_user['user_id']
            # user_phone_num = our_user['phone_num']
            # user_email = our_user['email']
            # if '@test.com' in user_email:
            #     user_email = email
            #     user_phone_num = our_user['phone_num']
            # else:
            #     user_phone_num = phone_num
            #     user_email = our_user['email']
            # print('user_id: ', user_id)

            data = [{
                'name': agent['agent_name'],
                'phone_num': generate_random_string(),
                'email': email,
                'user_id': user_id
            }]
            # print(data)
            url = f'{base_url}/agent/add'
            return_flag = insert_data(url, data, token=True)  # insert records
            if return_flag is False:
                # Due to duplicate phone_num in your_records so replaced with random phone_num
                data = [{
                    'name': agent['agent_name'],
                    'phone_num': generate_random_string(),
                    'email': email,
                    'user_id': user_id
                }]
                # print(data)
                url = f'{base_url}/agent/add'
                return_flag = insert_data(url, data, token=True)  # insert records
            # # Update user
            # url = f'{base_url}/user/update/{user_id}'
            # data = {
            #     'email': user_email,
            #     'phone_num': user_phone_num
            # }
            # return_flag = update_data(url, data, token=True)  # insert records
    # Create Leads
    lead_query = 'select * from leads'
    leads = select_query(lead_query)
    for lead in tqdm(leads):
        # print(lead)
        branch_id = 1 if lead['lead_branch'] == 'FC Road, Pune' else 2
        course_id = 1 if lead['lead_course'] == 'Classroom Digital Marketing' else 2
        admission_status = 1 if lead['lead_status'] == 'Confirmed' else 0
        is_deleted = 1 if lead['deleted_at'] else 0

        source_id = None
        if lead['lead_source'] == 'Google':
            source_id = 1
        elif lead['lead_source'] == 'Referal':
            source_id = 7
        elif lead['lead_source'] == 'Walk-in':
            source_id = 5
        elif lead['lead_source'] == 'Whatsapp':
            source_id = 3
        elif lead['lead_source'] == 'Facebook':
            source_id = 2
        elif lead['lead_source'] == 'Direct Call':
            source_id = 4
        else:
            source_id = 4

        batch_time_id = None
        if lead['lead_time'] == 'Morning':
            batch_time_id = 1
        elif lead['lead_time'] == 'Evening':
            batch_time_id = 3
        elif lead['lead_time'] == 'Afternoon':
            batch_time_id = 2
        else:
            batch_time_id = 1

        remark = lead['lead_remark']
        remark_query = f'select * from remarks where lead_id = {int(lead["id"])}'
        extra_remarks = select_query(remark_query)
        for extra_remark in extra_remarks:
            if remark and extra_remark:
                remark = remark + '<br>' + extra_remark['remark']

        lead_user_id = lead['user_id']
        # print('lead_user_id: ', lead_user_id)
        agent_query = f'select * from agent where user_id = {int(lead["user_id"])}'
        agents = select_query(agent_query)
        agent_email = ''
        if agents:
            for agent in agents:
                agent_email = agent['agent_email']
        else:
            agent_email = 'admin@test.com'

        if agent_email == 'na':
            agent_email = 'admin@test.com'

        # get user_id by agent email
        url = f'{base_url}/agent/by_email_or_phone_num'
        query_params = {
            'email': agent_email
        }
        # # print('user_query_params: ', user_query_params)
        our_agent = fetch_single_record(url, query_params)  # fetch all users
        our_agent_id = our_agent['agent_id']
        our_agent_user_id = our_agent['user_id']
        # print('our_agent_user_id: ', our_agent_user_id)
        # print('our_agent_id: ', our_agent_id)

        # Create lead
        data = [{
          'name': lead['lead_name'],
          'phone_num': '+91-' + lead['lead_contact_number'],
          # 'alternate_phone_num': '+91-' + lead['lead_alternate_contact_number'] if lead['lead_alternate_contact_number'] else lead['lead_alternate_contact_number'],
          'alternate_phone_num': '',
          'email': lead['lead_email'],
          'lead_date': str(lead['lead_date']),
          'remarks': remark,
          'country_id': 98,
          'area': lead['lead_area'],
          'city_id': 1,
          'branch_id': branch_id,
          'source_id': source_id,
          'course_id': course_id,
          'batch_time_id': batch_time_id,
          'next_action_date': str(lead['next_action']) if lead['next_action'] else lead['next_action'],
          'next_action_remarks': lead['lead_next_action_remark'],
          'details_sent': int(lead['detail_sent']),
          'visit_date': str(lead['visit_date']) if lead['visit_date'] else lead['visit_date'],
          'pitch_by': lead['pitch_by'],
          'demo_date': str(lead['demo_date']) if lead['demo_date'] else lead['demo_date'],
          'instructor': lead['Instructor'],
          'broadcast': lead['broadcast'],
          'agent_id': our_agent_id,
          'fee_offer': lead['fee_offer'],
          'admission_status': admission_status,
          'is_deleted': is_deleted
        }]
        # print('lead data: ', data)
        url = f'{base_url}/leads/add'
        insert_data(url, data, token=True)  # insert records

        # create user on admission confirmation
        if admission_status:
            email = lead['lead_email'] if lead['lead_email'] and '@' in lead['lead_email'] else generate_random_string() + '@test.com'
            user_role_id = 3
            password = "student123"
            data = {
                'name': lead['lead_name'],
                'phone_num': lead['lead_contact_number'],
                'email': email,
                'password': password,
                'user_role_id': user_role_id
            }
            # print(data)
            url = f'{base_url}/user/add'
            insert_data(url, data)  # insert records

            # get user_id of last inserted record
            url = f'{base_url}/user/by_email_or_phone_num'
            query_params = {
                'phone_num': lead['lead_contact_number']
            }
            our_user = fetch_single_record(url, query_params)
            our_user_id = our_user['user_id']
            # print('our_user_id : ', our_user_id, our_user)
            #
            # url = f'{base_url}/user/update/{our_user_id}'
            # data = {
            #     'email': email,
            #     'phone_num': lead['lead_contact_number']
            # }
            # update_data(url, data, token=True)  # insert records

            # create student
            student_query = f'select * from customers where lead_id = {int(lead["id"])}'
            students = select_query(student_query)
            for student in students:
                # student documents
                student_documents_query = f'select * from customer_documents where customer_id = {int(student["id"])}'
                student_documents = select_query(student_documents_query)
                # if not student_documents:
                #     continue

                # create receipts
                installments = []
                total_fee_paid = 0
                payments_formats = (
                    ('payment_amount_1', 'payment_date_1', 'payment_mode_1', 'transaction_no_1'),
                    ('payment_amount_2', 'payment_date_2', 'payment_mode_2', 'transaction_no_2'),
                    ('payment_amount_3', 'payment_date_3', 'payment_mode_3', 'transaction_no_3'),
                    ('payment_amount_4', 'payment_date_4', 'payment_mode_4', 'transaction_no_4'),
                )
                for p_index, payment_format in enumerate(payments_formats):
                    paymode_mode_id = 1
                    if student[payment_format[0]] and student[payment_format[2]]:
                        if 'cash' in student[payment_format[2]].lower():
                            paymode_mode_id = 1
                        elif 'debit card' in student[payment_format[2]].lower():
                            paymode_mode_id = 2
                        elif 'credit card' in student[payment_format[2]].lower():
                            paymode_mode_id = 3
                        elif 'other upi' in student[payment_format[2]].lower():
                            paymode_mode_id = 4
                        elif 'gpay' in student[payment_format[2]].lower():
                            paymode_mode_id = 5
                        elif 'phonepe' in student[payment_format[2]].lower():
                            paymode_mode_id = 6
                        elif 'paytm' in student[payment_format[2]].lower():
                            paymode_mode_id = 7
                        elif 'razorpay' in student[payment_format[2]].lower():
                            paymode_mode_id = 8
                        elif 'neft' in student[payment_format[2]].lower():
                            paymode_mode_id = 9
                        elif 'swipe' in student[payment_format[2]].lower():
                            paymode_mode_id = 10
                        elif 'cheque' in student[payment_format[2]].lower():
                            paymode_mode_id = 11
                        else:
                            paymode_mode_id = 1

                        r_data = {
                            'installment_num': p_index + 1,
                            'installment_payment': student[payment_format[0]],
                            'installment_payment_mode_id': paymode_mode_id,
                            'installment_payment_date': str(student[payment_format[1]]) if student[payment_format[1]] else student[payment_format[1]],
                            'installment_payment_transaction_number': student[payment_format[3]],
                        }
                        total_fee_paid += student[payment_format[0]]
                        installments.append(r_data)


                data = {
                    'name': student['customer_name'],
                    'phone_num': student['customer_contact_number'],
                    'alternate_phone_num': student['customer_alternate_contact_number'],
                    'email': student['customer_email'],
                    # 'dob': str(student_document['dob']) if student_document['dob'] else student_document['dob'],
                    'dob': '1990-01-01',
                    'admission_date': str(student['customer_admission_date']),
                    'area': student_documents[0]['area'] if student_documents else '',
                    'state': student_documents[0]['state'] if student_documents else '',
                    'pincode': student_documents[0]['pincode'] if student_documents else '',
                    'highest_education': student_documents[0]['highest_education'] if student_documents else '',
                    'occupation': student_documents[0]['occupation'] if student_documents else '',
                    'purpose_for_course': student_documents[0]['purpose'] if student_documents else '',
                    'referred_by': student_documents[0]['refferd_by'] if student_documents else '',
                    'front_image_path': student_documents[0]['file_front'] if student_documents else '',
                    'back_image_path': student_documents[0]['file_back'] if student_documents else '',
                    'passport_image_path': student_documents[0]['image_photo'] if student_documents else '',
                    'branch_id': branch_id,
                    'country_id': 98,
                    'city_id': 1,
                    'tutor_id': our_agent_id,
                    'course_id': course_id,
                    'course_content_id': 1,
                    'json_course_learning_progress': '',
                    'batch_time_id': batch_time_id,
                    'source_id': source_id,
                    'installments': installments,
                    'total_fee': student['customer_offer'],
                    'total_fee_paid': total_fee_paid,
                    'total_pending_fee': student['customer_offer'] - total_fee_paid,
                    'is_active': 1,
                    'is_document_verified': 1,
                    'user_id': our_user_id,
                    'deleted': 0,
                }
                # print('student data: ', data)
                url = f'{base_url}/students/add'
                insert_data(url, data, token=True)  # insert records










