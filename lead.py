import datetime
import traceback
from flask import current_app as app, request, Blueprint, jsonify, send_file
import model
from auth_middleware import token_required
from db_operations import bulk_insert, insert_single_record
from sqlalchemy import or_, desc
from scripts import upload_leads_for_api

lead_bp = Blueprint('lead_bp', __name__, url_prefix='/api/leads')

DEFAULT_COUNTRY = 'India'
DEFAULT_STATE = 'Maharashtra'
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


def is_lead_phone_num_and_course_exists(phone_num, course_id):
    cursor = app.session.query(model.Lead).filter(
        or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num
        ),
        model.Lead.course_id == course_id
    )
    records = list(cursor)
    return records


def is_lead_alternate_phone_num_and_course_exists(alternate_phone_num, course_id):
    cursor = app.session.query(model.Lead).filter(
        or_(
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        ),
        model.Lead.course_id == course_id
    )
    records = list(cursor)
    return records


def is_lead_email_and_course_exists(email, course_id):
    cursor = app.session.query(model.Lead).filter(
        model.Lead.email == email,
        model.Lead.course_id == course_id
    )
    records = list(cursor)
    return records


def fetch_lead_by_id(lead_id):
    record = app.session.query(model.Lead).filter(model.Lead.lead_id == lead_id).first()
    return record


def fetch_lead_by_id_and_is_assigned_to_admin(lead_id):
    super_admin_user_id = app.session.query(model.User.user_id).filter(
        model.User.user_role_id == 1).first()  # get super_admin user_id
    super_admin_user_id = super_admin_user_id[0]
    super_admin_agent_id = app.session.query(model.Agent.agent_id).filter(
        model.Agent.user_id == super_admin_user_id).first()  # get super_admin user_id
    super_admin_agent_id = super_admin_agent_id[0]
    print('super_admin_agent_id: ', super_admin_agent_id)

    record = app.session.query(model.Lead).filter(model.Lead.lead_id == lead_id).\
        filter(model.Lead.agent_id == super_admin_agent_id).first()
    return record


def populate_lead_record(lead):
    lead_result = {}
    for key in lead.__table__.columns.keys():
        value = getattr(lead, key)
        if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date', 'lead_time') and value:
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
        if key == 'state_id':
            state = lead.state
            lead_result[key] = {}
            for state_key in state.__table__.columns.keys():
                state_value = getattr(state, state_key)
                lead_result[key][state_key] = state_value
            lead_result['state'] = lead_result.pop(key)
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
        if key == 'course_mode_id':
            course_mode = lead.course_mode
            lead_result[key] = {}
            for course_mode_key in course_mode.__table__.columns.keys():
                course_mode_value = getattr(course_mode, course_mode_key)
                lead_result[key][course_mode_key] = course_mode_value
            lead_result['course_mode'] = lead_result.pop(key)
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
        if key == 'pitch_by_id':
            pitch_by = lead.pitch_by
            if pitch_by:
                lead_result[key] = {}
                for pitch_by_key in pitch_by.__table__.columns.keys():
                    pitch_by_value = getattr(pitch_by, pitch_by_key)
                    lead_result[key][pitch_by_key] = pitch_by_value
            else:
                lead_result[key] = None
            lead_result['pitch_by'] = lead_result.pop(key)
        if key == 'trainer_id':
            trainer = lead.trainer
            lead_result[key] = {}
            for trainer_key in trainer.__table__.columns.keys():
                trainer_value = getattr(trainer, trainer_key)
                lead_result[key][trainer_key] = trainer_value
            lead_result['trainer'] = lead_result.pop(key)
        if key == 'submitted_lead_id':
            submitted_lead = lead.submitted_lead
            if submitted_lead:
                lead_result[key] = {}
                for submitted_lead_key in submitted_lead.__table__.columns.keys():
                    submitted_lead_value = getattr(submitted_lead, submitted_lead_key)
                    lead_result[key][submitted_lead_key] = submitted_lead_value
            else:
                lead_result[key] = None
            lead_result['submitted_lead'] = lead_result.pop(key)
    return lead_result


@lead_bp.route('/add', methods=['POST'])
@token_required
def add_lead(current_user):
    try:
        if request.method == 'POST':
            if not request.is_json:
                return {'error': 'Bad Request.'}, 400
            data = request.get_json()
            records_to_add = []
            for item in data:
                lead = model.Lead()
                # Check if lead is already exist
                if is_lead_phone_num_and_course_exists(item['phone_num'], item['course_id']):
                    return {'error': 'Phone number with selected course is already exist.'}, 409
                if 'alternate_phone_num' in item and item['alternate_phone_num'] \
                        and is_lead_alternate_phone_num_and_course_exists(item['alternate_phone_num'], item['course_id']):
                    return {'error': 'Alternate Phone number with selected course is already exist.'}, 409
                if 'email' in item and item['email'] \
                        and is_lead_email_and_course_exists(item['email'], item['course_id']):
                    return {'error': 'Email with selected course is already exist.'}, 409
                for key, value in item.items():
                    if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date') and value:
                        value = datetime.datetime.strptime(value, '%Y-%m-%d')
                    if key in ('lead_time',) and value:
                        value = datetime.datetime.strptime(value, '%H:%M').time()
                    setattr(lead, key, value)
                records_to_add.append(lead)
            bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Inserted.'}), 201
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/upload-excel', methods=['POST'])
@token_required
def upload_excel_leads(current_user):
    # TODO: Add course_id for unique constraints
    try:
        if request.method == 'POST':
            file = request.files['file']
            if not file.filename.endswith('.xlsx'):
                raise ValueError('Only Excel .xlsx is allowed.')
            file_data = file.read()
            missed_leads = upload_leads_for_api.run(file_data)
            return jsonify(missed_leads)
    except Exception as ex:
        print(traceback.format_exc())
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/update/<lead_id>', methods=['PUT'])
@token_required
def update_lead(current_user, lead_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        for_fresh_lead = request.args.get('for_fresh_lead', 0)
        data = request.get_json()
        records_to_add = []
        for item in data:
            if for_fresh_lead:
                lead = fetch_lead_by_id_and_is_assigned_to_admin(int(lead_id))
                if lead is None:
                    return jsonify({'error': 'Accept lead is already assigned to another agent.'}), 404
            else:
                lead = fetch_lead_by_id(int(lead_id))

            # Check if lead is already exist
            if 'phone_num' in item and item['phone_num'] and lead.phone_num != item['phone_num'] \
                    and is_lead_phone_num_and_course_exists(item['phone_num'], item['course_id']):
                return {'error': 'Phone number with selected course is already exist.'}, 409
            if 'alternate_phone_num' in item and item['alternate_phone_num'] \
                    and lead.alternate_phone_num != item['alternate_phone_num'] \
                    and is_lead_alternate_phone_num_and_course_exists(item['alternate_phone_num'], item['course_id']):
                return {'error': 'Alternate Phone number with selected course is already exist.'}, 409
            if 'email' in item and item['email'] and lead.email != item['email'] \
                    and is_lead_email_and_course_exists(item['email'], item['course_id']):
                return {'error': 'Email with selected course is already exist.'}, 409
            for key, value in item.items():
                if key in ('lead_date', 'next_action_date', 'visit_date', 'demo_date') and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d')
                setattr(lead, key, value)
            records_to_add.append(lead)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Successfully Updated.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/delete/<lead_id>', methods=['DELETE'])
@token_required
def soft_delete_lead(current_user, lead_id):
    try:
        lead = fetch_lead_by_id(int(lead_id))
        lead.phone_num = lead.phone_num + '::' + str(
            datetime.datetime.now()) + '::deleted' if lead.phone_num else lead.phone_num
        lead.alternate_phone_num = lead.alternate_phone_num + '::' + str(
            datetime.datetime.now()) + '::deleted' if lead.alternate_phone_num else lead.alternate_phone_num
        lead.email = lead.email + '::' + str(datetime.datetime.now()) + '::deleted' if lead.email else lead.email
        lead.deleted = 1
        insert_single_record(lead)
        return jsonify({'message': 'Successfully deleted..'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_lead_by_email_or_phone_num(current_user):
    # TODO: Add course_id for unique constraints
    lead = None
    phone_num = request.args.get('phone_num', '')
    alternate_phone_num = request.args.get('alternate_phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.Lead).filter(model.Lead.deleted == 0)

    if phone_num and alternate_phone_num and email:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num,
            model.Lead.email == email
        ))
    elif phone_num and alternate_phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        ))
    elif phone_num and email:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.email == email
        ))
    elif phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num
        ))
    elif alternate_phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        ))
    elif email:
        query = query.filter(
            model.Lead.email == email
        )

    # if email:
    #     # query = query.filter(model.Lead.email.like(f'%{email}%'))
    #     query = query.filter(model.Lead.email == email)
    # elif alternate_phone_num:
    #     # query = query.filter(model.Lead.phone_num.like(f'%{phone_num}%'))
    #     query = query.filter(or_(
    #         model.Lead.phone_num == phone_num,
    #         model.Lead.alternate_phone_num == phone_num,
    #         model.Lead.phone_num == alternate_phone_num,
    #         model.Lead.alternate_phone_num == alternate_phone_num
    #     ))
    # else:
    #     query = query.filter(or_(
    #         model.Lead.phone_num == phone_num,
    #         model.Lead.alternate_phone_num == phone_num
    #     ))

    lead = query.first()
    result = {}
    if lead:
        for key in lead.__table__.columns.keys():
            value = getattr(lead, key)
            if key == 'agent_id':
                agent = lead.agent
                result['agent'] = {}
                for agent_key in agent.__table__.columns.keys():
                    agent_value = getattr(agent, agent_key)
                    result['agent'][agent_key] = agent_value
            result[key] = value

            if key in ('lead_time',):
                result[key] = str(value)

    return jsonify(result), 200


@lead_bp.route('/by_email_or_phone_num_and_course_name', methods=['GET'])
@token_required
def get_lead_by_email_or_phone_num_and_course_name(current_user):
    # TODO: Add course_id for unique constraints
    lead = None
    phone_num = request.args.get('phone_num', '')
    alternate_phone_num = request.args.get('alternate_phone_num', '')
    email = request.args.get('email', '')
    course_name = request.args.get('course_name', '')
    course_name = course_name.replace('__', ' ')
    query = app.session.query(model.Lead).filter(model.Lead.deleted == 0)

    if phone_num and alternate_phone_num and email:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num,
            model.Lead.email == email
        ))
    elif phone_num and alternate_phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        ))
    elif phone_num and email:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num,
            model.Lead.email == email
        ))
    elif phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == phone_num,
            model.Lead.alternate_phone_num == phone_num
        ))
    elif alternate_phone_num:
        query = query.filter(or_(
            model.Lead.phone_num == alternate_phone_num,
            model.Lead.alternate_phone_num == alternate_phone_num
        ))
    elif email:
        query = query.filter(
            model.Lead.email == email
        )

    if course_name:
        course = app.session.query(model.Course).filter(model.Course.name == course_name,
                                                        model.Course.deleted == 0).first()
        if course is None:
            # Ge default course
            course = app.session.query(model.Course).filter(model.Course.course_id == 1,
                                                            model.Course.deleted == 0).first()
        print('course: ', course.course_id)
        query = query.filter(
            model.Lead.course_id == course.course_id
        )

    # if email:
    #     # query = query.filter(model.Lead.email.like(f'%{email}%'))
    #     query = query.filter(model.Lead.email == email)
    # elif alternate_phone_num:
    #     # query = query.filter(model.Lead.phone_num.like(f'%{phone_num}%'))
    #     query = query.filter(or_(
    #         model.Lead.phone_num == phone_num,
    #         model.Lead.alternate_phone_num == phone_num,
    #         model.Lead.phone_num == alternate_phone_num,
    #         model.Lead.alternate_phone_num == alternate_phone_num
    #     ))
    # else:
    #     query = query.filter(or_(
    #         model.Lead.phone_num == phone_num,
    #         model.Lead.alternate_phone_num == phone_num
    #     ))

    lead = query.first()
    result = {}
    if lead:
        for key in lead.__table__.columns.keys():
            value = getattr(lead, key)
            if key == 'agent_id':
                agent = lead.agent
                result['agent'] = {}
                for agent_key in agent.__table__.columns.keys():
                    agent_value = getattr(agent, agent_key)
                    result['agent'][agent_key] = agent_value
            result[key] = value

            if key in ('lead_time',):
                result[key] = str(value)

    return jsonify(result), 200


@lead_bp.route('/select/<lead_id>', methods=['GET'])
@token_required
def get_lead(current_user, lead_id):
    try:
        lead = app.session.query(model.Lead).filter(model.Lead.lead_id == int(lead_id), model.Lead.deleted == 0).first()
        lead_result = populate_lead_record(lead)
        return jsonify(lead_result), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@lead_bp.route('/select-all', methods=['GET'])
@token_required
def get_leads(current_user):
    try:
        from_date = request.args.get('from_date', None)
        to_date = request.args.get('to_date', None)
        name = request.args.get('name', None)
        phone_number = request.args.get('phone_number', None)
        branch = request.args.get('branch', None)
        course = request.args.get('course', None)
        course_mode = request.args.get('course_mode', None)
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
        query = query.filter(model.Lead.course_mode_id == int(course_mode)) if course_mode else query
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
@token_required
def get_paginated_leads(current_user, page_id):
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
@token_required
def get_paginated_leads_advanced(current_user):
    try:
        print('current_user: ', current_user)
        total_leads = model.Lead.query.filter(model.Lead.deleted == 0).count()

        # request params
        from_date = request.args.get('from_date', None)
        to_date = request.args.get('to_date', None)
        next_action_from_date = request.args.get('next_action_from_date', None)
        next_action_to_date = request.args.get('next_action_to_date', None)
        name = request.args.get('name', None)
        phone_number = request.args.get('phone_number', None)
        branch = request.args.get('branch', None)
        course = request.args.get('course', None)
        course_mode = request.args.get('course_mode', None)
        source = request.args.get('source', None)
        agent = request.args.get('agent', None)
        batch_time = request.args.get('batch_time', None)
        admission_status = request.args.get('admission_status', None)
        is_visited = request.args.get('is_visited', None)
        is_fresh_leads = request.args.get('is_fresh_leads', None)

        # filtering data
        query = app.session.query(model.Lead)
        query = query.filter(model.Lead.deleted == 0)
        query = query.filter(model.Lead.lead_date.between(from_date, to_date)) if from_date and to_date else query
        query = query.filter(model.Lead.next_action_date.between(next_action_from_date, next_action_to_date)) if next_action_from_date and next_action_to_date else query
        query = query.filter(model.Lead.name.like(f'{name}%')) if name else query
        query = query.filter(or_(
            model.Lead.phone_num == phone_number,
            model.Lead.alternate_phone_num == phone_number
        )) if phone_number else query
        query = query.filter(model.Lead.branch_id == int(branch)) if branch else query
        query = query.filter(model.Lead.course_id == int(course)) if course else query
        query = query.filter(model.Lead.course_mode_id == int(course_mode)) if course_mode else query
        query = query.filter(model.Lead.source_id == int(source)) if source else query
        query = query.filter(model.Lead.agent_id == int(agent)) if agent else query
        query = query.filter(model.Lead.batch_time_id == int(batch_time)) if batch_time else query
        query = query.filter(model.Lead.admission_status == int(admission_status)) if admission_status else query
        query = query.filter(model.Lead.visit_date.isnot(None)) if is_visited else query
        print(query)
        if current_user.user_role_id == 2:  # role == agent
            if is_fresh_leads:
                # For fresh leads, Fetch those leads which are assigned to admin
                # and have not taken admission yet.
                query = query.filter(model.Lead.admission_status == 0)

                super_admin_user_ids = app.session.query(model.User.user_id).filter(
                    model.User.user_role_id == 1).all()  # get super_admin user_id
                super_admin_user_ids = [x[0] for x in super_admin_user_ids]
                print('super_admin_user_ids: ', super_admin_user_ids)
                super_admin_agent_ids = app.session.query(model.Agent.agent_id).filter(
                    model.Agent.user_id.in_(super_admin_user_ids)).all()  # get super_admin user_id
                super_admin_agent_ids = [x[0] for x in super_admin_agent_ids]
                print('super_admin_agent_ids: ', super_admin_agent_ids)
                query = query.filter(model.Lead.agent_id.in_(super_admin_agent_ids))
            # else:
            #     agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.user_id == current_user.user_id).first()
            #     if agent_id:
            #         agent_id = agent_id[0]
            #     query = query.filter(model.Lead.agent_id == agent_id)

        # pagination
        start = request.args.get('start', type=int)
        length = request.args.get('length', type=int)
        search_term = request.args.get('search[value]', type=str)
        print('search_term: ', search_term)
        query = query.filter(or_(
            model.Lead.name.like(f'%{search_term}%'),
            model.Lead.phone_num.like(f'%{search_term}%'),
            model.Lead.alternate_phone_num.like(f'%{search_term}%'),
            model.Lead.email.like(f'{search_term}%'),
        )) if search_term else query

        total_filtered_leads = query.count()
        query = query.order_by(desc(model.Lead.lead_date), desc(model.Lead.created_at)).offset(start).limit(length)
        print(query)

        leads = query.all()
        # print('\n\n\n leads: ', leads)
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
        # import traceback
        # print(traceback.format_exc())
        return jsonify({'error': str(ex)}), 500
