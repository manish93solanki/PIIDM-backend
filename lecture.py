from flask import current_app as app, request, Blueprint, jsonify
import model
import datetime
from auth_middleware import token_required
from db_operations import bulk_insert

lecture_bp = Blueprint('lecture_bp', __name__, url_prefix='/api/lecture')


def is_lecture_exist(name, trainer_id, course_id, course_mode_id, batch_time_id, batch_id, batch_date, user_id):
    cursor = app.session.query(model.Lecture).filter(
        model.Lecture.name == name,
        model.Lecture.trainer_id == trainer_id,
        model.Lecture.course_id == course_id,
        model.Lecture.course_mode_id == course_mode_id,
        model.Lecture.batch_time_id == batch_time_id,
        model.Lecture.batch_id == batch_id,
        model.Lecture.batch_date == batch_date,
        model.Lecture.user_id == user_id
    )
    records = list(cursor)
    return records


def populate_lecture_record(lecture):
    lecture_result = {}
    for key in lecture.__table__.columns.keys():
        value = getattr(lecture, key)
        if key in ('batch_date', ) and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)

        lecture_result[key] = value
        if key == 'trainer_id':
            trainer = lecture.trainer
            lecture_result[key] = {}
            for trainer_key in trainer.__table__.columns.keys():
                trainer_value = getattr(trainer, trainer_key)
                lecture_result[key][trainer_key] = trainer_value
            lecture_result['trainer'] = lecture_result.pop(key)
        if key == 'course_id':
            course = lecture.course
            lecture_result[key] = {}
            for course_key in course.__table__.columns.keys():
                course_value = getattr(course, course_key)
                lecture_result[key][course_key] = course_value
            lecture_result['course'] = lecture_result.pop(key)
        if key == 'course_mode_id':
            course_mode = lecture.course_mode
            lecture_result[key] = {}
            for course_mode_key in course_mode.__table__.columns.keys():
                course_mode_value = getattr(course_mode, course_mode_key)
                lecture_result[key][course_mode_key] = course_mode_value
            lecture_result['course_mode'] = lecture_result.pop(key)
        if key == 'batch_time_id':
            batch_time = lecture.batch_time
            lecture_result[key] = {}
            for batch_time_key in batch_time.__table__.columns.keys():
                batch_time_value = getattr(batch_time, batch_time_key)
                lecture_result[key][batch_time_key] = batch_time_value
            lecture_result['batch_time'] = lecture_result.pop(key)
        if key == 'batch_id':
            batch = lecture.batch
            lecture_result[key] = {}
            if batch:
                for batch_key in batch.__table__.columns.keys():
                    batch_value = getattr(batch, batch_key)
                    lecture_result[key][batch_key] = batch_value
            lecture_result['batch'] = lecture_result.pop(key)
    return lecture_result


def populate_attendance_record(attendance):
    attendance_result = {}
    for key in attendance.__table__.columns.keys():
        value = getattr(attendance, key)

        attendance_result[key] = value
        if key == 'lecture_id':
            lecture = attendance.lecture
            attendance_result[key] = {}
            for lecture_key in lecture.__table__.columns.keys():
                lecture_value = getattr(lecture, lecture_key)
                attendance_result[key][lecture_key] = lecture_value
            attendance_result['lecture'] = attendance_result.pop(key)
        if key == 'student_id':
            student = attendance.student
            attendance_result[key] = {}
            for student_key in student.__table__.columns.keys():
                student_value = getattr(student, student_key)
                attendance_result[key][student_key] = student_value
            attendance_result['student'] = attendance_result.pop(key)
    return attendance_result


@lecture_bp.route('/add', methods=['POST'])
@token_required
def add_lecture(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            if is_lecture_exist(item['name'], item['trainer_id'], item['course_id'], item['course_mode_id'], item['batch_time_id'], item['batch_id'], item['batch_date'], item['user_id']):
                return {'error': 'Phone number with selected course is already exist.'}, 409
            lecture = model.Lecture()
            lecture.name = item['name']
            lecture.trainer_id = item['trainer_id']
            lecture.course_id = item['course_id']
            lecture.course_mode_id = item['course_mode_id']
            lecture.batch_time_id = item['batch_time_id']
            lecture.batch_id = item['batch_id']
            lecture.user_id = item['user_id']
            lecture.batch_date = datetime.datetime.strptime(item['batch_date'], '%d/%m/%y')
            records_to_add.append(lecture)
        bulk_insert(records_to_add)

        # It's compulsory to add students to the lecture to have their attendance later.
        records_to_add = []
        for item in data:
            lecture_name = item['name']
            
            # Get recently added lecture 
            lecture = app.session.query(model.Lecture).filter(
                model.Lecture.name == lecture_name,
                model.Lecture.deleted == 0
            ).first()
            # Get students from the batch by lecture
            students = app.session.query(model.Student).filter(
                model.Student.batch_id==lecture.batch_id,
                model.Student.deleted==0
            ).all()
            for student in students:
                attendance = model.Attendance()
                attendance.lecture_id = lecture.lecture_id
                attendance.student_id = student.student_id
                records_to_add.append(attendance)
        
        bulk_insert(records_to_add)
    return {'message': 'Lecture is created.'}, 201

 
@lecture_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_lecture(current_user, delete_id):
    app.session.query(model.Lecture).filter(model.Lecture.lecture_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@lecture_bp.route('/all', methods=['GET'])
@token_required
def get_lecture(current_user):
    cursor = app.session.query(model.Lecture).filter(model.Lecture.deleted==0).all()
    lectures = list(cursor)
    results = []
    for lecture in lectures:
        lecture_result = populate_lecture_record(lecture)
        results.append(lecture_result)
    return jsonify(results), 200


@lecture_bp.route('/attendance/<lecture_id>', methods=['GET'])
@token_required
def get_attendance(current_user, lecture_id):
    lecture_id = int(lecture_id)

    # Get Attendance 
    attendances = app.session.query(model.Attendance).filter(
        model.Attendance.lecture_id==lecture_id,
        model.Attendance.deleted==0
    ).all()
    attendances = list(attendances)

    if not attendances:
        # No attendance for newly created lecture
        return {'error': 'Lecture was not created succesfully. Hence no attendance can be taken. Ask admin to manually delete the lecture and re-create it.'}, 409

    results = []
    for attendance in attendances:
        attendance_result = populate_attendance_record(attendance)
        results.append(attendance_result)
    return jsonify(results), 200


@lecture_bp.route('/attendance/update', methods=['PUT'])
@token_required
def update_attendance(current_user):
    if request.method == 'PUT':
        if not request.is_json:
            pass
        data = request.get_json()
        print('data: ', data)
        attendance_ids = [x['attendance_id'] for x in data]
        print('attendance_ids: ', attendance_ids)
        attendances = app.session.query(model.Attendance).filter(
            model.Attendance.attendance_id.in_(attendance_ids),
            model.Attendance.deleted==0
        ).all()

        records_to_add = []
        for item in data:
            for attendance in attendances:
                if attendance.attendance_id == item['attendance_id']:
                    attendance.attendance_status = item['attendance_status']
                    attendance.updated_at = datetime.datetime.now()
                    records_to_add.append(attendance)
                    break
        bulk_insert(records_to_add)
    return {'message': 'Attendance updated.'}, 201
