from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

city_bp = Blueprint('city_bp', __name__, url_prefix='/api/city')


@city_bp.route('/add', methods=['POST'])
def add_city():
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
def delete_city(delete_id):
    app.session.query(model.City).filter(model.City.city_id == int(delete_id)).delete()
    app.session.commit()
    return {}


@city_bp.route('/all', methods=['GET'])
def get_city():
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
