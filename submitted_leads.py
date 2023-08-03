import datetime
import traceback
from flask import current_app as app, request, Blueprint, jsonify, send_file
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record
from sqlalchemy import or_, desc

submitted_lead_bp = Blueprint('submitted_lead_bp', __name__, url_prefix='/api/submitted_leads')


def is_submitted_lead_phone_num_exists(phone_num):
    cursor = app.session.query(model.SubmittedLead).filter(
        or_(
            model.SubmittedLead.phone_num == phone_num,
            model.SubmittedLead.alternate_phone_num == phone_num
        )
    )
    records = list(cursor)
    return records


def is_submitted_lead_email_exists(email):
    cursor = app.session.query(model.SubmittedLead).filter(model.SubmittedLead.email == email)
    records = list(cursor)
    return records


def fetch_submitted_lead_by_id(submitted_lead_id):
    record = app.session.query(model.SubmittedLead).filter(model.SubmittedLead.submitted_lead_id == submitted_lead_id).first()
    return record


def populate_submitted_lead_record(submitted_lead):
    submitted_lead_result = {}
    for key in submitted_lead.__table__.columns.keys():
        value = getattr(submitted_lead, key)
        if key in ('created_at_gmt', ) and value:
            # print('------> ', key, value)
            value = str(value)  # datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
            # print('value: ', value)
        submitted_lead_result[key] = value
    return submitted_lead_result


@submitted_lead_bp.route('/delete/<submitted_lead_id>', methods=['DELETE'])
@token_required
def soft_delete_submitted_lead(current_user, submitted_lead_id):
    try:
        submitted_lead = fetch_submitted_lead_by_id(int(submitted_lead_id))
        submitted_lead.phone_num = submitted_lead.phone_num + '::' + str(
            datetime.datetime.now()) + '::deleted' if submitted_lead.phone_num else submitted_lead.phone_num
        submitted_submitted_lead.email = submitted_submitted_lead.email + '::' + str(datetime.datetime.now()) + '::deleted' if submitted_submitted_lead.email else submitted_submitted_lead.email
        submitted_submitted_lead.deleted = 1
        insert_single_record(submitted_submitted_lead)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@submitted_lead_bp.route('/select/<submitted_lead_id>', methods=['GET'])
@token_required
def get_submitted_lead(current_user, submitted_lead_id):
    try:
        submitted_lead = app.session.query(model.SubmittedLead).filter(model.SubmittedLead.submitted_lead_id == int(submitted_lead_id), model.SubmittedLead.deleted == 0).first()
        submitted_lead_result = populate_submitted_lead_record(submitted_lead)
        return jsonify(submitted_lead_result), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@submitted_lead_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_submitted_leads_advanced(current_user):
    try:
        print('current_user: ', current_user)
        total_submitted_leads = model.SubmittedLead.query.filter(model.SubmittedLead.deleted == 0).count()

        # request params

        # filtering data
        query = app.session.query(model.SubmittedLead)
        query = query.filter(model.SubmittedLead.deleted == 0)
        print(query)

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        search_term = request.args.get('search[value]', type=str)
        print('search_term: ', search_term)
        query = query.filter(or_(
            model.SubmittedLead.name.like(f'%{search_term}%'),
            model.SubmittedLead.phone_num.like(f'%{search_term}%'),
            model.SubmittedLead.email.like(f'{search_term}%'),
        )) if search_term else query

        total_filtered_submitted_leads = query.count()
        query = query.order_by(desc(model.SubmittedLead.created_at_gmt)).offset(start).limit(length)
        print(query)

        submitted_leads = query.all()
        # print('\n\n\n submitted_leads: ', submitted_leads)
        submitted_lead_results = []
        for submitted_lead in submitted_leads:
            submitted_lead_result = populate_submitted_lead_record(submitted_lead)
            submitted_lead_results.append(submitted_lead_result)
            # submitted_lead_results.append({'name': submitted_lead_result['name']})
        # response
        return jsonify({
            'data': submitted_lead_results,
            'recordsFiltered': total_filtered_submitted_leads,
            'recordsTotal': total_submitted_leads,
            'draw': request.args.get('draw', type=int),
        }), 200
    except Exception as ex:
        # import traceback
        # print(traceback.format_exc())
        return jsonify({'error': str(ex)}), 500
