from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

source_bp = Blueprint('source_bp', __name__, url_prefix='/api/source')


@source_bp.route('/add', methods=['POST'])
def add_source():
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
def delete_source(delete_id):
    app.session.query(model.Source).filter(model.Source.source_id == int(delete_id)).delete()
    app.session.commit()
    return {}

