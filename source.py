from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert

source_bp = Blueprint('source_bp', __name__, url_prefix='/api/source')


@source_bp.route('/add', methods=['POST'])
@token_required
def add_source(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            source = model.Source()
            source.name = item['name']
            records_to_add.append(source)
        bulk_insert(records_to_add)
    return {}


@source_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_source(current_user, delete_id):
    app.session.query(model.Source).filter(model.Source.source_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@source_bp.route('/all', methods=['GET'])
@token_required
def get_source(current_user):
    cursor = app.session.query(model.Source).all()
    sources = list(cursor)
    results = []
    for source in sources:
        res = {}
        for key in source.__table__.columns.keys():
            value = getattr(source, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200

