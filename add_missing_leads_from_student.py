import uuid
import json
import requests
from rich import print
from sqlalchemy import create_engine
from tqdm import tqdm


def sqlite_engine():
    conn_string = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
    # conn_string = f'sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db'
    return create_engine(conn_string)


def select_query(engine, query):
    result = engine.execute(query)
    return list(result.mappings())


def insert_query(engine, query):
    engine.execute(query)


def update_query(engine, query):
    engine.execute(query)


if __name__ == '__main__':
    sqlite_conn = sqlite_engine()

    query = f'''
        select * from student where student.phone_num NOT IN (select lead.phone_num from lead) 
    '''
    students = select_query(sqlite_conn, query)
    print('Total Students: ', len(students))
    cnt = 0
    for student in students:
        lead_query = f"select * from lead where phone_num = \"{student['phone_num']}\""
        lead_data_1 = select_query(sqlite_conn, lead_query)

        lead_query = f"select * from lead where lead_id = {student['lead_id']}"
        lead_data_2 = select_query(sqlite_conn, lead_query)
        print(student['phone_num'], student['name'], student['alternate_phone_num'], student['email'], not(bool(lead_data_1) or bool(lead_data_2)))
        if not (bool(lead_data_1) or bool(lead_data_2)):
            u_query = f'''
                insert into lead (lead_id, name, phone_num, alternate_phone_num, email, lead_date, area,
                    branch_id, country_id, city_id, agent_id, course_id, batch_time_id, source_id,
                    details_sent, broadcast, admission_status, deleted, created_at, updated_at)
                values ({student['lead_id']}, "{student['name']}", "{student['phone_num']}", 
                        null,
                        null,
                        "{student['admission_date']}", "{student['area']}",
                        {student['branch_id']}, {student['country_id']}, {student['city_id']},
                        {student['tutor_id']}, {student['course_id']}, {student['batch_time_id']},
                        {student['source_id']}, 2, 2,
                        1, 0, '2023-03-13 22:37:30', '2023-03-13 22:37:30')
                '''
            print(u_query)
            insert_query(sqlite_conn, u_query)