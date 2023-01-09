from sqlalchemy.exc import IntegrityError

from flask import current_app as app


def insert_single_record(insert_record):
    return_status = True
    try:
        id_ = app.session.merge(insert_record)
        app.session.commit()
    except IntegrityError as exc:
        app.session.rollback()
        app.session.flush()
        if 'UniqueViolation' not in str(exc):
            raise
        if 'UNIQUE constraint failed' not in str(exc):
            raise
        return_status = 'UniqueViolation'
    except Exception as exc:
        print(str(exc))
        app.session.rollback()
        app.session.flush()
        raise
    # finally:
    #     app.session.close()
    return return_status, id_


def bulk_insert(bulk_insert_records):
    try:
        app.session.bulk_save_objects(bulk_insert_records)
        app.session.commit()
    except IntegrityError as exc:
        print('====> ', str(exc))
        app.session.rollback()
        app.session.flush()
        if 'UniqueViolation' not in str(exc):
            raise
        if 'UNIQUE constraint failed' not in str(exc):
            raise

        # Since bulk installation failed with UniqueViolation, will attempt individual record insertion.
        for insert_record in bulk_insert_records:
            insert_single_record(insert_record)

    except Exception as exc:
        print(str(exc))
        app.session.rollback()
        app.session.flush()
        raise
    # finally:
    #     app.session.close()
