import datetime

from sqlalchemy import create_engine

# SQLALCHEMY_DATABASE_URL = f'mysql://piidm_online:piidm_online_password123@localhost:3306/piidm_online'
# SQLALCHEMY_DATABASE_URL = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
SQLALCHEMY_DATABASE_URL = f'sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
CONNECTION = engine.connect()


def fetch_students_not_paid_fee_on_time():
    # # Fetch students who have not paid fee in one month after admission.
    # query = f'''
    #         select student_id, name, admission_date, total_fee, total_fee_paid, total_pending_fee from student
    #         WHERE (JULIANDAY(DATE("now")) - JULIANDAY(student.admission_date)) > 31 and total_pending_fee > 0 and
    #         is_active = 1
    #     '''

    # Fetch students who have not paid fee in one month after batch_date.
    query = f'''
            select student_id, student.name, admission_date, batch_date, total_fee, total_fee_paid, total_pending_fee from student 
            join batch
            on student.batch_id = batch.batch_id 
            WHERE (JULIANDAY(DATE("now")) - JULIANDAY(batch.batch_date)) > 31 and total_pending_fee > 0 and 
            is_active = 1
        '''
    cursor = CONNECTION.execute(query)
    print(f'\nTotal students will get deactivated: {len(list(cursor))}')


def deactivate_student():
    # # Fetch students who have not paid fee in one month after admission.
    # query = f'''
    #         UPDATE student SET is_active = 0
    #         WHERE (JULIANDAY(DATE("now")) - JULIANDAY(student.admission_date)) > 31 and total_pending_fee > 0 and is_active = 1
    #     '''

    # Fetch students who have not paid fee in one month after batch_date.
    query = f'''
            UPDATE student SET is_active = 0
            from (SELECT batch_id, batch_date from batch) as b 
            WHERE student.batch_id = b.batch_id 
                and (JULIANDAY(DATE("now")) - JULIANDAY(b.batch_date)) > 31 and total_pending_fee > 0 and is_active = 1
        '''
    CONNECTION.execute(query)
    print(f'\nStudents got deactivated who have not paid fee on time.')


if __name__ == '__main__':
    print('\n\n')
    print('Executed on: ', datetime.datetime.now())
    fetch_students_not_paid_fee_on_time()
    deactivate_student()
    print('\n\n')
    print('-*-' * 20)
