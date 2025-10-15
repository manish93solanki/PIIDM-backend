from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

user_role_bp = Blueprint('user_role_bp', __name__, url_prefix='/api/user_role')


@user_role_bp.route('/add', methods=['POST'])
def add_user_role():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            user_role = model.UserRole()
            user_role.name = item['name']
            records_to_add.append(user_role)
        bulk_insert(records_to_add)
    return {}


@user_role_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_user_role(delete_id):
    app.session.query(model.UserRole).filter(model.UserRole.user_role_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@user_role_bp.route('/all', methods=['GET'])
def get_user_role():
    cursor = app.session.query(model.UserRole).filter(model.UserRole.deleted == 0).all()
    user_roles = list(cursor)
    results = []
    for user_role in user_roles:
        res = {}
        for key in user_role.__table__.columns.keys():
            value = getattr(user_role, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200

