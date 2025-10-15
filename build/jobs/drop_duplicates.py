import datetime
from sqlalchemy import create_engine

# SQLALCHEMY_DATABASE_URL = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
# SQLALCHEMY_DATABASE_URL = f'sqlite:////Users/nitinsolanki/Downloads/piidm_online_sqlite.db'
SQLALCHEMY_DATABASE_URL = f'sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
CONNECTION = engine.connect()


def remove_duplicate_leads_by_phone_num(phone_num):
    keep_lead_id = None
    query = f'''
        select lead_id, name, phone_num, admission_status, updated_at, agent_id  from `lead` 
        where phone_num = '{phone_num}' and admission_status = 1
    '''
    cursor = CONNECTION.execute(query)
    for record in cursor.mappings():
        if record['admission_status'] == 1:
            keep_lead_id = record['lead_id']

    if keep_lead_id:
        query = f'''
            select lead_id, name, phone_num, admission_status, updated_at, agent_id  from `lead` 
            where phone_num = '{phone_num}'
        '''
        cursor = CONNECTION.execute(query)
        delete_lead_ids = []
        for record in cursor.mappings():
            if record['admission_status'] == 0:
                delete_lead_ids.append(record['lead_id'])

        for del_lead_id in delete_lead_ids:
            query = f'''
                delete from `lead` where lead_id = {del_lead_id}
            '''
            CONNECTION.execute(query)
        print('keep_lead_id: ', keep_lead_id, 'delete_lead_ids: ', delete_lead_ids, record['phone_num'])
    else:
        query = f'''
             select lead_id, lead_date, name, phone_num, admission_status, updated_at, agent_id  from `lead` 
             where phone_num = '{phone_num}' order by lead_date desc, agent_id desc
        '''
        cursor = CONNECTION.execute(query)
        delete_lead_ids = []
        i = 0
        for record in cursor.mappings():
            print(record['lead_id'])
            if i == 0:
                keep_lead_id = record['lead_id']
            else:
                delete_lead_ids.append(record['lead_id'])
            i += 1

        for del_lead_id in delete_lead_ids:
            query = f'''
                delete from `lead` where lead_id = {del_lead_id}
            '''
            CONNECTION.execute(query)
        print('keep_lead_id: ', keep_lead_id, 'delete_lead_ids: ', delete_lead_ids, record['phone_num'])


def all_duplicate_leads_by_phone_num():
    # Fetch students who have not paid fee in one month after admission.
    query = f'''
            select l.lead_id, l.phone_num from `lead` l
              join ( select phone_num 
                       from `lead`
                      group by phone_num
                     having count(*) > 1 ) s
                on l.phone_num = s.phone_num;
        '''
    cursor = CONNECTION.execute(query)
    for record in cursor.mappings():
        remove_duplicate_leads_by_phone_num(record['phone_num'])


if __name__ == '__main__':
    print('\n\n')
    print('Executed on: ', datetime.datetime.now())
    all_duplicate_leads_by_phone_num()
    print('\n\n')
    print('-*-' * 20)
