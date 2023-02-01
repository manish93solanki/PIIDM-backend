import jwt
from flask import current_app as app, request, Blueprint, jsonify
from sqlalchemy import or_
import model
from db_operations import bulk_insert

user_bp = Blueprint('user_bp', __name__, url_prefix='/api/user')


@user_bp.route('/add', methods=['POST'])
def add_user():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            user = model.User()
            user.phone_num = item['phone_num']
            user.email = item['email']
            user.password = item['password']
            user.user_role_id = item['user_role_id']
            records_to_add.append(user)
        bulk_insert(records_to_add)
    return {}


@user_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_user(delete_id):
    app.session.query(model.User).filter(model.User.user_id == int(delete_id)).delete()
    app.session.commit()
    return {}


@user_bp.route('/all', methods=['GET'])
def get_user():
    cursor = app.session.query(model.User).all()
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
        print(data)
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
            model.User.phone_num == data['phone_num'],
            model.User.email == data['email']
        ))
        is_validated = query.count()
        if not is_validated:
            return dict(message='Invalid data', data=None, error=is_validated), 400
        user = query.first()
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
                    "message": "Successfully fetched auth token",
                    "data": user.token
                }
            except Exception as e:
                return {
                    "error": "Something went wrong",
                    "message": str(e)
                }, 500
        return {
            "message": "Error fetching auth token!, invalid email or password",
            "data": None,
            "error": "Unauthorized"
        }, 404
    except Exception as e:
        return {
            "message": "Something went wrong!",
            "error": str(e),
            "data": None
        }, 500
