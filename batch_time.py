from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

batch_time_bp = Blueprint('batch_time_bp', __name__, url_prefix='/api/batch_time')


@batch_time_bp.route('/add', methods=['POST'])
def add_batch_time():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            batch_time = model.BatchTime()
            batch_time.name = item['name']
            records_to_add.append(batch_time)
        bulk_insert(records_to_add)
    return {}


@batch_time_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_batch_time(delete_id):
    app.session.query(model.BatchTime).filter(model.BatchTime.batch_time_id == int(delete_id)).delete()
    app.session.commit()
    return {}


@batch_time_bp.route('/all', methods=['GET'])
def get_batch_time():
    cursor = app.session.query(model.BatchTime).all()
    batch_times = list(cursor)
    results = []
    for batch_time in batch_times:
        res = {}
        for key in batch_time.__table__.columns.keys():
            value = getattr(batch_time, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
