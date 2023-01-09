from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

branch_bp = Blueprint('branch_bp', __name__, url_prefix='/api/branch')


@branch_bp.route('/add', methods=['POST'])
def add_branch():
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
def delete_branch(delete_id):
    app.session.query(model.Branch).filter(model.Branch.branch_id == int(delete_id)).delete()
    app.session.commit()
    return {}
