import uuid
import json
import requests
from rich import print
from sqlalchemy import create_engine
from tqdm import tqdm


TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770'


def generate_random_string():
    random_string = uuid.uuid4().hex[:10].upper()
    return random_string


def mysql_engine():
    global engine
    conn_string = f'mysql://piidm_online:piidm_online_password123@localhost:3306/u776183671_piidm_13_03'
    return create_engine(conn_string)


def sqlite_engine():
    conn_string = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
    return create_engine(conn_string)


def select_query(engine, query):
    result = engine.execute(query)
    return list(result.mappings())


def update_query(engine, query):
    engine.execute(query)


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
    mysql_conn = mysql_engine()
    sqlite_conn = sqlite_engine()

    query = f'''
        select * from student 
    '''
    students = select_query(sqlite_conn, query)
    print('Total Student: ', len(students))
    cnt = 0
    for student in students:
        student_phone_num = student['phone_num'].split('-')[1]
        student_phone_num = student_phone_num.replace(' ', '')
        student_id = student['student_id']

        query = f'''
            select customers.id, customer_documents.customer_id, customers.customer_contact_number,
            customers.customer_name, customer_documents.image_photo, 
            customer_documents.file_front,
            customer_documents.file_back from customers
            join customer_documents
            on customers.id = customer_documents.customer_id
            where customers.customer_contact_number = {student_phone_num}
        '''
        customer_data = select_query(mysql_conn, query)
        if customer_data:
            print(student_phone_num, student['name'])
            c_image_photo = customer_data[0]['image_photo']
            c_image_photo = f"data/uploaded_images/{c_image_photo.split('/')[-1]}" if c_image_photo else ''
            c_file_front = customer_data[0]['file_front']
            c_file_front = f"data/uploaded_images/{c_file_front.split('/')[-1]}" if c_file_front else ''
            c_file_back = customer_data[0]['file_back']
            c_file_back = f"data/uploaded_images/{c_file_back.split('/')[-1]}" if c_file_back else ''
            u_query = f'''
                update student
                set 
                    front_image_path = "{c_file_front}",
                    back_image_path = "{c_file_back}",
                    passport_image_path = "{c_image_photo}"
                where student_id = "{student_id}"
                '''
            update_query(sqlite_conn, u_query)
            cnt += 1
    print('Total Updated: ', cnt)
    print('Missed: ', len(students) - cnt)





