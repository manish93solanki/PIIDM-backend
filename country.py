from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

country_bp = Blueprint('country_bp', __name__, url_prefix='/api/country')


@country_bp.route('/add', methods=['POST'])
def add_country():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            country = model.Country()
            country.name = item['name']
            country.dial_code = item['dial_code']
            country.code = item['code']
            records_to_add.append(country)
        bulk_insert(records_to_add)
    return {}


@country_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_country(delete_id):
    app.session.query(model.Country).filter(model.Country.country_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@country_bp.route('/all', methods=['GET'])
def get_country():
    cursor = app.session.query(model.Country).all()
    countries = list(cursor)
    results = []
    for country in countries:
        res = {}
        for key in country.__table__.columns.keys():
            value = getattr(country, key)
            res[key] = value
        results.append(res)
    return jsonify(results), 200
