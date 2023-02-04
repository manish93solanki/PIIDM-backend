from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert

branch_bp = Blueprint('branch_bp', __name__, url_prefix='/api/branch')


@branch_bp.route('/add', methods=['POST'])
@token_required
def add_branch(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            branch = model.Branch()
            branch.name = item['name']
            records_to_add.append(branch)
        bulk_insert(records_to_add)
    return {}


@branch_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_branch(current_user, delete_id):
    app.session.query(model.Branch).filter(model.Branch.branch_id == int(delete_id)).delete()
    app.session.commit()
    return {}


@branch_bp.route('/all', methods=['GET'])
@token_required
def get_branch(current_user):
    cursor = app.session.query(model.Branch).all()
    branches = list(cursor)
    results = []
    for branch in branches:
        res = {}
        for key in branch.__table__.columns.keys():
            value = getattr(branch, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
