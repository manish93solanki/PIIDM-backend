from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

payment_mode_bp = Blueprint('payment_mode_bp', __name__, url_prefix='/api/payment_mode')


@payment_mode_bp.route('/add', methods=['POST'])
def add_payment_mode():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            payment_mode = model.PaymentMode()
            payment_mode.name = item['name']
            records_to_add.append(payment_mode)
        bulk_insert(records_to_add)
    return {}


@payment_mode_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_payment_mode(delete_id):
    app.session.query(model.PaymentMode).filter(model.PaymentMode.payment_mode_id == int(delete_id)).delete()
    return {}


@payment_mode_bp.route('/all', methods=['GET'])
def get_payment_mode():
    cursor = app.session.query(model.PaymentMode).all()
    payment_modes = list(cursor)
    results = []
    for payment_mode in payment_modes:
        res = {}
        for key in payment_mode.__table__.columns.keys():
            value = getattr(payment_mode, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
