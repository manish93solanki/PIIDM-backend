import datetime

from sqlalchemy import create_engine

# SQLALCHEMY_DATABASE_URL = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
SQLALCHEMY_DATABASE_URL = f'sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
CONNECTION = engine.connect()


def fix_pending_fee():
    # Fetch students who have not paid fee in one month after admission.
    query = f'''
            select student.student_id, student.name, student.total_fee, sum(receipt.installment_payment) as tfp,  
            (student.total_fee - sum(receipt.installment_payment)) as tpf from student join receipt 
            on student.student_id = receipt.student_id  group by student.student_id
        '''
    cursor = CONNECTION.execute(query)
    for record in cursor.mappings():
        query = f'''
            UPDATE student set total_fee_paid = {record["tfp"]},
                               total_pending_fee = {record["tpf"]},
                               is_active = 1
                           where student_id = {record["student_id"]}
        '''
        CONNECTION.execute(query)


if __name__ == '__main__':
    print('\n\n')
    print('Executed on: ', datetime.datetime.now())
    fix_pending_fee()
    print('\n\n')
    print('-*-' * 20)
