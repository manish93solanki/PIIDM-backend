from flask import current_app as app, request, Blueprint, jsonify
import model
from db_operations import bulk_insert

course_bp = Blueprint('course_bp', __name__, url_prefix='/api/course')


@course_bp.route('/add', methods=['POST'])
def add_course():
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            course = model.Course()
            course.name = item['name']
            records_to_add.append(course)
        bulk_insert(records_to_add)
    return {}


@course_bp.route('/delete/<delete_id>', methods=['DELETE'])
def delete_course(delete_id):
    app.session.query(model.Course).filter(model.Course.course_id == int(delete_id)).delete()
    app.session.commit()
    return {}