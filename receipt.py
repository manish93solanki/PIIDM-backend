import datetime
from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert, insert_single_record
from sqlalchemy import or_

receipt_bp = Blueprint('receipt_bp', __name__, url_prefix='/api/receipts')


def fetch_receipt_by_id(receipt_id):
    record = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == receipt_id).first()
    return record


def populate_receipt_record(receipt):
    receipt_result = {}
    for key in receipt.__table__.columns.keys():
        value = getattr(receipt, key)
        if key in ('installment_payment_date', ) and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)
        if key in ('installment_payment_mode', ) and value:
            value = value.value
        receipt_result[key] = value
    return receipt_result


@receipt_bp.route('/delete/<receipt_id>', methods=['DELETE'])
def soft_delete_receipt(receipt_id):
    receipt = fetch_receipt_by_id(int(receipt_id))
    receipt.deleted = 1
    insert_single_record(receipt)
    return {'message': 'Successfully deleted..'}, 200


@receipt_bp.route('/select/<receipt_id>', methods=['GET'])
def get_receipt(receipt_id):
    receipt = app.session.query(model.Receipt).filter(model.Receipt.receipt_id == int(receipt_id),
                                                      model.Receipt.deleted == 0).first()
    receipt_result = populate_receipt_record(receipt)
    return jsonify(receipt_result), 200


@receipt_bp.route('/select-all', methods=['GET'])
def get_receipts():
    receipts = app.session.query(model.Receipt).filter(model.Receipt.deleted == 0).all()
    receipt_results = []
    for receipt in receipts:
        receipt_result = populate_receipt_record(receipt)
        receipt_results.append(receipt_result)
    return jsonify(receipt_results), 200


@receipt_bp.route('/select-paginate/<page_id>', methods=['GET'])
def get_paginated_receipts(page_id):
    # receipts = app.session.query(model.Receipt).paginate(page=page_id, per_page=1)
    receipts = model.Receipt.query.filter(model.Receipt.deleted == 0).paginate(page=int(page_id), per_page=1)
    receipt_results = []
    for receipt in receipts:
        receipt_result = populate_receipt_record(receipt)
        receipt_results.append(receipt_result)
    return jsonify(receipt_results), 200
