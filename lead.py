import datetime
import traceback
from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert, insert_single_record
from sqlalchemy import or_

lead_bp = Blueprint('lead_bp', __name__, url_prefix='/api/leads')

DEFAULT_COUNTRY = 'India'
DEFAULT_CITY = 'Pune'
DEFAULT_BRANCH = 'FC Road, Pune'
DEFAULT_SOURCE = 'Google'
DEFAULT_COURSE = 'Online Digital Marketing'
DEFAULT_BATCH_TIME = 'Morning'
DEFAULT_AGENT = 'Morning'


def is_lead_phone_num_exists(phone_num):
    cursor = app.session.query(model.Lead).filter(
        or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num
        )
    )
    records = list(cursor)
    return records


def is_lead_alternate_phone_num_exists(alternate_phone_num):
    cursor = app.session.query(model.Lead).filter(
        or_(
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        )
    )
    records = list(cursor)
    return records


def is_lead_email_exists(email):
    cursor = app.session.query(model.Lead).filter(model.Lead.email == email)
    records = list(cursor)
    return records


def fetch_lead_by_id(lead_id):
    record = app.session.query(model.Lead).filter(model.Lead.lead_id == lead_id).first()
    return record


def populate_lead_record(lead):
    lead_result = {}
    for key in lead.__table__.columns.keys():
        value = getattr(lead, key)
        if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date') and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)

        lead_result[key] = value

        if key == 'branch_id':
            branch = lead.branch
            lead_result[key] = {}
            for branch_key in branch.__table__.columns.keys():
                branch_value = getattr(branch, branch_key)
                lead_result[key][branch_key] = branch_value
            lead_result['branch'] = lead_result.pop(key)
        if key == 'country_id':
            country = lead.country
            lead_result[key] = {}
            for country_key in country.__table__.columns.keys():
                country_value = getattr(country, country_key)
                lead_result[key][country_key] = country_value
            lead_result['country'] = lead_result.pop(key)
        if key == 'city_id':
            city = lead.city
            lead_result[key] = {}
            for city_key in city.__table__.columns.keys():
                city_value = getattr(city, city_key)
                lead_result[key][city_key] = city_value
            lead_result['city'] = lead_result.pop(key)
        if key == 'source_id':
            source = lead.source
            lead_result[key] = {}
            for source_key in source.__table__.columns.keys():
                source_value = getattr(source, source_key)
                lead_result[key][source_key] = source_value
            lead_result['source'] = lead_result.pop(key)
        if key == 'course_id':
            course = lead.course
            lead_result[key] = {}
            for course_key in course.__table__.columns.keys():
                course_value = getattr(course, course_key)
                lead_result[key][course_key] = course_value
            lead_result['course'] = lead_result.pop(key)
        if key == 'batch_time_id':
            batch_time = lead.batch_time
            lead_result[key] = {}
            for batch_time_key in batch_time.__table__.columns.keys():
                batch_time_value = getattr(batch_time, batch_time_key)
                lead_result[key][batch_time_key] = batch_time_value
            lead_result['batch_time'] = lead_result.pop(key)
        if key == 'agent_id':
            agent = lead.agent
            lead_result[key] = {}
            for agent_key in agent.__table__.columns.keys():
                agent_value = getattr(agent, agent_key)
                lead_result[key][agent_key] = agent_value
            lead_result['agent'] = lead_result.pop(key)
    return lead_result


@lead_bp.route('/add', methods=['POST'])
def add_lead():
    # try:
    if request.method == 'POST':
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            lead = model.Lead()
            # Check if lead is already exist
            if is_lead_phone_num_exists(item['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if is_lead_alternate_phone_num_exists(item['alternate_phone_num']):
                return {'error': 'Alternate Phone number is already exist.'}, 409
            if is_lead_email_exists(item['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in item.items():
                if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date') and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(lead, key, value)
            # if 'country_id' not in item.keys():  # Set default, if not exist
            #     country_id = app.session.query(model.Country.country_id).filter(model.Country.name == DEFAULT_COUNTRY)
            #     setattr(lead, 'country_id', country_id)
            # if 'city_id' not in item.keys():  # Set default, if not exist
            #     city_id = app.session.query(model.City.city_id).filter(model.City.name == DEFAULT_CITY)
            #     setattr(lead, 'city_id', city_id)
            # if 'branch_id' not in item.keys():  # Set default, if not exist
            #     branch_id = app.session.query(model.Branch.branch_id).filter(model.Branch.name == DEFAULT_BRANCH)
            #     setattr(lead, 'branch_id', branch_id)
            # if 'source_id' not in item.keys():  # Set default, if not exist
            #     source_id = app.session.query(model.Source.source_id).filter(model.Source.name == DEFAULT_SOURCE)
            #     setattr(lead, 'source_id', source_id)
            # if 'course_id' not in item.keys():  # Set default, if not exist
            #     course_id = app.session.query(model.Course.course_id).filter(model.Course.name == DEFAULT_COURSE)
            #     setattr(lead, 'course_id', course_id)
            # if 'batch_time_id' not in item.keys():  # Set default, if not exist
            #     batch_time_id = app.session.query(model.BatchTime.batch_time_id).filter(
            #         model.BatchTime.name == DEFAULT_BATCH_TIME)
            #     setattr(lead, 'batch_time_id', batch_time_id)
            # if 'agent_id' not in item.keys():  # Set default, if not exist
            #     agent_id = app.session.query(model.Agent.batch_time_id).filter(model.Agent.name == DEFAULT_AGENT)
            #     setattr(lead, 'agent_id', agent_id)
            records_to_add.append(lead)
        bulk_insert(records_to_add)
    return jsonify({'message': 'Successfully Inserted.'}), 201
    # except Exception as ex:
    #     return jsonify({'error': str(ex)}), 500


@lead_bp.route('/update/<lead_id>', methods=['PUT'])
def update_lead(lead_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        for item in data:
            lead = fetch_lead_by_id(int(lead_id))

            # Check if lead is already exist
            if lead.phone_num != item['phone_num'] and is_lead_phone_num_exists(item['phone_num']):
                return {'error': 'Phone number is already exist.'}, 409
            if lead.alternate_phone_num != item['alternate_phone_num'] and is_lead_alternate_phone_num_exists(item['alternate_phone_num']):
                return {'error': 'Alternate Phone number is already exist.'}, 409
            if lead.email != item['email'] and is_lead_email_exists(item['email']):
                return {'error': 'Email is already exist.'}, 409
            for key, value in item.items():
                if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date') and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(lead, key, value)
            records_to_add.append(lead)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 204
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/delete/<lead_id>', methods=['DELETE'])
def soft_delete_lead(lead_id):
    try:
        lead = fetch_lead_by_id(int(lead_id))
        lead.deleted = 1
        insert_single_record(lead)
        return jsonify({'message': 'Successfully deleted..'}), 204
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/select/<lead_id>', methods=['GET'])
def get_lead(lead_id):
    try:
        lead = app.session.query(model.Lead).filter(model.Lead.lead_id == int(lead_id), model.Lead.deleted == 0).first()
        lead_result = populate_lead_record(lead)
        return jsonify(lead_result), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/select-all', methods=['GET'])
def get_leads():
    try:
        from_date = request.args.get('from_date', None)
        to_date = request.args.get('to_date', None)
        name = request.args.get('name', None)
        phone_number = request.args.get('phone_number', None)
        branch = request.args.get('branch', None)
        course = request.args.get('course', None)
        batch_time = request.args.get('batch_time', None)
        status = request.args.get('status', None)

        query = app.session.query(model.Lead)
        query = query.filter(model.Lead.deleted == 0)
        query = query.filter(model.Lead.lead_date.between(from_date, to_date)) if from_date and to_date else query
        query = query.filter(model.Lead.name.like(f'{name}%')) if name else query
        query = query.filter(or_(
            model.Lead.phone_num == phone_number,
            model.Lead.alternate_phone_num == phone_number
        )) if phone_number else query
        query = query.filter(model.Lead.branch_id == int(branch)) if branch else query
        query = query.filter(model.Lead.course_id == int(course)) if course else query
        query = query.filter(model.Lead.batch_time_id == int(batch_time)) if batch_time else query
        # query = query.filter(model.Lead.is_enrolled == int(status)) if status else query

        print(query)
        cursor = query.all()
        leads = list(cursor)

        lead_results = []
        for lead in leads:
            lead_result = populate_lead_record(lead)
            lead_results.append(lead_result)
        return jsonify(lead_results), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/select-paginate/<page_id>', methods=['GET'])
def get_paginated_leads(page_id):
    try:
        # leads = app.session.query(model.Lead).paginate(page=page_id, per_page=1)
        leads = model.Lead.query.filter(model.Lead.deleted == 0).paginate(page=int(page_id), per_page=1)
        lead_results = []
        for lead in leads:
            lead_result = populate_lead_record(lead)
            lead_results.append(lead_result)
        return jsonify(lead_results), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/select-paginate-advanced', methods=['GET'])
def get_paginated_leads_advanced():
    try:
        total_leads = model.Lead.query.filter(model.Lead.deleted == 0).count()

        # request params
        from_date = request.args.get('from_date', None)
        to_date = request.args.get('to_date', None)
        name = request.args.get('name', None)
        phone_number = request.args.get('phone_number', None)
        branch = request.args.get('branch', None)
        course = request.args.get('course', None)
        batch_time = request.args.get('batch_time', None)
        status = request.args.get('status', None)

        # filtering data
        query = app.session.query(model.Lead)
        query = query.filter(model.Lead.deleted == 0)
        query = query.filter(model.Lead.lead_date.between(from_date, to_date)) if from_date and to_date else query
        query = query.filter(model.Lead.name.like(f'{name}%')) if name else query
        query = query.filter(or_(
            model.Lead.phone_num == phone_number,
            model.Lead.alternate_phone_num == phone_number
        )) if phone_number else query
        query = query.filter(model.Lead.branch_id == int(branch)) if branch else query
        query = query.filter(model.Lead.course_id == int(course)) if course else query
        query = query.filter(model.Lead.batch_time_id == int(batch_time)) if batch_time else query

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        search_term = request.args.get('search[value]', type=str)
        print('search_term: ', search_term)
        query = query.filter(or_(
            model.Lead.name.like(f'{search_term}%'),
            model.Lead.phone_num.like(f'{search_term}%'),
            model.Lead.alternate_phone_num.like(f'{search_term}%'),
            model.Lead.email.like(f'{search_term}%'),
        )) if search_term else query

        total_filtered_leads = query.count()
        query = query.offset(start).limit(length)
        print(query)

        leads = query.all()
        lead_results = []
        for lead in leads:
            lead_result = populate_lead_record(lead)
            lead_results.append(lead_result)
            # lead_results.append({'name': lead_result['name']})
        # response
        return jsonify({
            'data': lead_results,
            'recordsFiltered': total_filtered_leads,
            'recordsTotal': total_leads,
            'draw': request.args.get('draw', type=int),
        }), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500

