from sqlalchemy import create_engine

"""
SSH Tunnel port forwarding for MYSQL
ssh -p 65002 -fN -L 127.0.0.1:3307:127.0.0.1:3306 u776183671@89.117.157.123
"""

mysqlengine = create_engine('mysql+pymysql://u776183671_QNQO7:xLvfwq2NuC@127.0.0.1:3307/u776183671_7Ytda')
mysql_conn = mysqlengine.connect()

# sqliteengine = create_engine('sqlite:////Users/nitins1/Documents/codemania/personal/piidm-backend/piidm_online_sqlite.db')
sqliteengine = create_engine('sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db')
sqlite_conn = sqliteengine.connect()


def get_last_submission_id():
    global sqlite_conn, mysql_conn
    last_submission_id = 0  #16453 - starting ID

    # Collect latest submission_id from our database - sqlite
    cursor = sqlite_conn.execute('SELECT submission_id from submitted_lead order by submission_id desc limit 1')
    for row in cursor.mappings():
        last_submission_id = row['submission_id']

    # Collect latest submission_id from source - piidm.com database
    if last_submission_id == 0:
        cursor = mysql_conn.execute('SELECT id from wp_e_submissions order by id desc limit 1')
        for row in cursor.mappings():
            last_submission_id = row['id'] - 1

    print('last_submission_id: ', last_submission_id)
    return last_submission_id


def fetch_and_insert_data(last_submission_id):
    global mysql_conn, sqlite_conn
    cursor = mysql_conn.execute(f'SELECT * FROM wp_e_submissions where id > {last_submission_id}')

    for row in cursor.mappings():
        submission_data = dict(row)
        # print()
        submission_id = row['id']
        print('submission_id: ', submission_id)
        join_cursor = mysql_conn.execute(
            f'SELECT * FROM wp_e_submissions_values where submission_id = {submission_id} LIMIT 5')
        for row_2 in join_cursor.mappings():
            # print()
            # print(row_2)
            if row_2['key'] == 'name':
                submission_data['name'] = row_2['value'].replace('\'', ' ')
            elif row_2['key'] == 'email':
                submission_data['email'] = row_2['value']
            elif row_2['key'] == 'field_4b05454' or row_2['key'] == 'field_a7b7060' or row_2['key'] == 'field_827f28a' or row_2['key'] == 'field_8f939e3' or row_2['key'] == 'field_05c825a' or row_2['key'] == 'field_8a7b6de' or row_2['key'] == 'phone' :
                phone_num = row_2['value']
                if phone_num:
                    phone_num = phone_num.replace('+91', '')
                    phone_num = phone_num.lstrip('0')
                    phone_num = ''.join(c for c in phone_num if c.isdigit())
                submission_data['phone_num'] = phone_num
        # print(submission_data)

        sqlite_conn.execute(f'''
            INSERT INTO submitted_lead(
                'submission_id',
                'name',
                'phone_num',
                'email',
                'hash_id',
                'referer',
                'referer_title',
                'form_name',
                'campaign_id',
                'user_id',
                'user_ip',
                'user_agent',
                'actions_count',
                'actions_succeeded_count',
                'status',
                'submitted_status',
                'created_at_gmt',
                'updated_at_gmt',
                'deleted'
            ) 
            VALUES(
                {submission_data['id']},
                '{submission_data['name']}',
                '{submission_data['phone_num']}',
                '{submission_data['email']}',
                '{submission_data['hash_id']}',
                '{submission_data['referer']}',
                '{submission_data['referer_title'].replace("'s", " ")}',
                '{submission_data['form_name']}',
                {submission_data['campaign_id']},
                {submission_data['user_id']},
                '{submission_data['user_ip']}',
                '{submission_data['user_agent']}',
                {submission_data['actions_count']},
                {submission_data['actions_succeeded_count']},
                '{submission_data['status']}',
                1,
                '{submission_data['created_at_gmt']}',
                '{submission_data['updated_at_gmt']}',
                0
            )
        ''')


if __name__ == '__main__':
    last_submission_id = get_last_submission_id()
    fetch_and_insert_data(last_submission_id)
    # with sshtunnel.SSHTunnelForwarder(
    #         ('89.117.157.123', 65002),
    #         ssh_username='u776183671',
    #         ssh_password='Notime12#',
    #         remote_bind_address=('127.0.0.1', 3306),
    #         local_bind_address=('127.0.0.1', 3307)
    # ) as tunnel:
    #     connection = mysql.connector.connect(
    #         user='u776183671_QNQO7',
    #         password='xLvfwq2NuC',
    #         host='127.0.0.1',
    #         port=3307,
    #         database='u776183671_7Ytda',
    #     )
    #     mycursor = connection.cursor()
    #     query = "SELECT * FROM wp_e_submissions LIMIT 1"
    #     print(mycursor.execute(query))

    # connection = mysql.connector.connect(
    #     username='u776183671_QNQO7',
    #     password='xLvfwq2NuC',
    #     host='127.0.0.1',
    #     port=3307,
    #     database='u776183671_7Ytda',
    # )
    # cursor = connection.cursor()
    # query = "SELECT * FROM wp_e_submissions LIMIT 1"
    # cursor.execute(query)
    # result = cursor.fetchall()
    # print(result)
