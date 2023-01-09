from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

agent_bp = Blueprint('agent_bp', __name__, url_prefix='/api/agent')


@agent_bp.route('/add', methods=['POST'])
def add_agent():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            agent = model.Agent()
            agent.name = item['name']
            agent.phone_num = item['phone_num']
            agent.email = item['email']
            records_to_add.append(agent)
        bulk_insert(records_to_add)
    return {}


@agent_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_agent(delete_id):
    app.session.query(model.Agent).filter(model.Agent.agent_id == int(delete_id)).delete()
    app.session.commit()
    return {}