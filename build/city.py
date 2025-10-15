from flask import current_app as app, request, Blueprint, jsonify
import model
from auth_middleware import token_required
from db_operations import bulk_insert

city_bp = Blueprint('city_bp', __name__, url_prefix='/api/city')


@city_bp.route('/add', methods=['POST'])
@token_required
def add_city(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            city = model.City()
            city.name = item['name']
            records_to_add.append(city)
        bulk_insert(records_to_add)
    return {}


@city_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_city(current_user, delete_id):
    app.session.query(model.City).filter(model.City.city_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@city_bp.route('/all', methods=['GET'])
@token_required
def get_city(current_user):
    cursor = app.session.query(model.City).all()
    cities = list(cursor)
    results = []
    for city in cities:
        res = {}
        for key in city.__table__.columns.keys():
            value = getattr(city, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
