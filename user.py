import jwt
from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_
import model
from auth_middleware import token_required
from db_operations import bulk_insert

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')


def is_user_phone_num_exists(phone_num):
    cursor = app.session.query(model.User).filter(model.User.phone_num == phone_num)
    records = list(cursor)
    return records


def is_user_email_exists(email):
    cursor = app.session.query(model.User).filter(model.User.email == email)
    records = list(cursor)
    return records


def fetch_user_by_id(user_id):
    record = app.session.query(model.User).filter(model.User.user_id == user_id).first()
    return record


@user_bp.route('/add', methods=['POST'])
def add_user():
    user_id = []
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        user = model.User()
        if is_user_phone_num_exists(data['phone_num']):
            return {'error': 'Phone number is already exist.'}, 409
        if is_user_email_exists(data['email']):
            return {'error': 'Email is already exist.'}, 409
        user.name = data['name']
        user.phone_num = data['phone_num']
        user.email = data['email']
        user.password = data['password']
        user.user_role_id = data['user_role_id']
        records_to_add.append(user)
        bulk_insert(records_to_add)

        user = app.session.query(model.User).filter(model.User.phone_num == user.phone_num).first()
        user_id = user.user_id
    return {'message': 'User is created.', 'user_id': user_id}


@user_bp.route('/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    if request.method == 'PUT':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        user = fetch_user_by_id(int(user_id))
        if 'phone_num' in data and user.phone_num != data['phone_num'] and is_user_phone_num_exists(data['phone_num']):
            return {'error': 'Phone number is already exist.'}, 409
        if 'email' in data and user.email != data['email'] and is_user_email_exists(data['email']):
            return {'error': 'Email is already exist.'}, 409
        for key, value in data.items():
            setattr(user, key, value)
        records_to_add.append(user)
        bulk_insert(records_to_add)

    return {'message': 'User is updated.'}


@user_bp.route('/change_password/<user_id>', methods=['PUT'])
@token_required
def change_password(current_user, user_id):
    try:
        if not request.is_json:
            return {'error': 'Bad Request.'}, 400
        data = request.get_json()
        records_to_add = []
        user = fetch_user_by_id(int(user_id))

        # Check if user is already exist
        user.password = data['password']
        records_to_add.append(user)
        bulk_insert(records_to_add)
        return jsonify({'message': 'Password update successfully.'}), 200
    except Exception as ex:
        return jsonify({'error': str(ex)}), 500


@user_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, delete_id):
    app.session.query(model.User).filter(model.User.user_id == int(delete_id)).delete()
    app.session.commit()
    return {}


@user_bp.route('/by_email_or_phone_num', methods=['GET'])
@token_required
def get_user_by_email_or_phone_num(current_user):
    user = None
    phone_num = request.args.get('phone_num', '')
    email = request.args.get('email', '')
    query = app.session.query(model.User).filter(model.User.deleted == 0)
    if email:
        query = query.filter(model.User.email == email)
    else:
        query = query.filter(model.User.phone_num == phone_num)
    user = query.first()
    result = {}
    if user:
        for key in user.__table__.columns.keys():
            value = getattr(user, key)
            result[key] = value
    return jsonify(result), 200


@user_bp.route('/all', methods=['GET'])
@token_required
def get_user(current_user):
    cursor = app.session.query(model.User).filter(model.User.deleted == 0).all()
    users = list(cursor)
    results = []
    for user in users:
        res = {}
        for key in user.__table__.columns.keys():
            value = getattr(user, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200


@user_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        # validate input
        query = app.session.query(model.User)
        query = query.filter(model.User.deleted == 0)
        query = query.filter(model.User.password == data['password'])
        query = query.filter(or_(
            model.User.phone_num.op('regexp')(rf'\+\d+\-{data["username"]}'),
            model.User.email == data['username']
        ))
        is_validated = query.count()
        if not is_validated:
            error_message = 'Mobile/Email or password is incorrect.'
            return dict(message='Invalid data', data=None, error=error_message), 400
        user = query.first()
        # Agent ID
        agent_id = app.session.query(model.Agent.agent_id).filter(model.Agent.deleted == 0, model.Agent.user_id == user.user_id).first()
        if agent_id:
            agent_id = agent_id[0]
        # Student ID
        student_id = None
        student_is_active = None
        student_is_document_verified = None
        student = app.session.query(model.Student).filter(model.Student.deleted == 0, model.Student.user_id == user.user_id).first()
        if student:
            student_id = student.student_id
            student_is_active = student.is_active
            student_is_document_verified = student.is_document_verified
            if not student_is_active:
                return {
                    "error": "Your Account is blocked/deactivated.<br>Please contact admin.."
                }, 500
        if user:
            try:
                # token should expire after 24 hrs
                user.token = jwt.encode(
                    {"user_id": user.user_id},
                    app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                bulk_insert([user])
                return {
                    "message": "Login Successfully...",
                    "token": user.token,
                    "profile_name": user.name,
                    "user_id": user.user_id,
                    "user_role_id": user.user_role_id,
                    "agent_id": agent_id,
                    "student_id": student_id,
                    "student_is_active": student_is_active,
                    "student_is_document_verified": student_is_document_verified
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        return {
            "message": "Error fetching auth token!, invalid email/mobile or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500


@user_bp.route("/logout", methods=["PUT"])
@token_required
def logout(current_user):
    try:
        user = app.session.query(model.User).filter(
            model.User.deleted == 0,
            model.User.user_id == current_user.user_id
        ).first()
        user.token = None
        bulk_insert([user])
        return {
            'message': 'Logout Successfully'
        }, 200
    except Exception as ex:
        return {
            'error': f'Issue with logout., {str(ex)}'
        }, 500
