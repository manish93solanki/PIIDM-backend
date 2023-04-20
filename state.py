from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert

state_bp = Blueprint('state_bp', __name__, url_prefix='/api/state')


@state_bp.route('/add', methods=['POST'])
@token_required
def add_state(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            state = model.State()
            state.name = item['name']
            state.code = item['code']
            records_to_add.append(state)
        bulk_insert(records_to_add)
    return {}


@state_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_state(current_user, delete_id):
    app.session.query(model.State).filter(model.State.state_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@state_bp.route('/all', methods=['GET'])
@token_required
def get_state(current_user):
    cursor = app.session.query(model.State).all()
    countries = list(cursor)
    results = []
    for state in countries:
        res = {}
        for key in state.__table__.columns.keys():
            value = getattr(state, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
