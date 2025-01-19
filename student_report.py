from flask import current_app as app, request, Blueprint, jsonify
import model
import json
import datetime
from auth_middleware import token_required
from db_operations import bulk_insert
from sqlalchemy import or_, desc
import sqlalchemy

student_report_bp = Blueprint('student_report_bp', __name__, url_prefix='/api/students_report')


def is_student_report_exist(name, topic, trainer_id, course_mode_id, batch_time_id, json_batch_ids, batch_date, user_id):
    cursor = app.session.query(model.StudentReport).filter(
        model.StudentReport.name == name,
        model.StudentReport.topic == topic,
        model.StudentReport.trainer_id == trainer_id,
        # model.StudentReport.course_id == course_id,
        model.StudentReport.course_mode_id == course_mode_id,
        model.StudentReport.batch_time_id == batch_time_id,
        model.StudentReport.json_batch_ids == json_batch_ids,
        model.StudentReport.batch_date == batch_date,
        model.StudentReport.user_id == user_id
    )
    records = list(cursor)
    return records


def populate_student_report_record(student, attendance, placement, attendance_percentage):
    student_report_result = {
        'student_name': student.name,
        'attendance': f'{attendance_percentage}%' if attendance_percentage else '',
        'assignment': '',
        'exam': '',
        'score': '',
        'certificate': '',
        'mock_interview': '',
        'placement_status': placement.status if placement else None,
    }
    return student_report_result


def populate_attendance_record(attendance):
    attendance_result = {}
    for key in attendance.__table__.columns.keys():
        value = getattr(attendance, key)

        attendance_result[key] = value
        if key == 'student_report_id':
            student_report = attendance.student_report
            attendance_result[key] = {}
            for student_report_key in student_report.__table__.columns.keys():
                student_report_value = getattr(student_report, student_report_key)
                attendance_result[key][student_report_key] = student_report_value
            attendance_result['student_report'] = attendance_result.pop(key)
        if key == 'student_id':
            student = attendance.student
            attendance_result[key] = {}
            for student_key in student.__table__.columns.keys():
                student_value = getattr(student, student_key)
                attendance_result[key][student_key] = student_value
            attendance_result['student'] = attendance_result.pop(key)
    return attendance_result


@student_report_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_student_report_advanced(current_user):
    trainer = model.Trainer.query.filter(
        model.Trainer.user_id == current_user.user_id,
        model.Trainer.deleted == 0
    ).first()

    # request params
    batch = request.args.get('batch', None)
    mock_interview = request.args.get('mock_interview', None)
    score = request.args.get('score', None)
    placement_status = request.args.get('placement_status', None)
    certificate_status = request.args.get('certificate_status', None)

    # filtering data
    query = model.Student.query.filter(
        model.Student.trainer_id == trainer.trainer_id,
        model.Student.deleted == 0
    )
    query = query.join(model.Placement, model.Student.student_id == model.Placement.student_id, isouter=True)
    query = query.with_entities( model.Student, model.Placement)

    query = query.filter(model.Student.batch_id == int(batch)) if batch else query

    if placement_status:
        if placement_status == 'Not yet placed':
            query = query.filter(or_(
                model.Placement.status == placement_status,
                model.Placement.status.is_(None)
            ))
        else:
            query = query.filter(model.Placement.status == placement_status)
    """
    SELECT student.student_id, student.name, placement.status
    FROM student LEFT OUTER JOIN placement ON student.student_id = placement.student_id 
    WHERE (placement.status = 'Placed');
    """

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    # print('search_term: ', search_term)
    query = query.filter(model.Student.name.like(f'{search_term}%')) if search_term else query

    total_filtered_student_report = query.count()  # total filtered student_report
    basic_stats = {
        'total_student_reports': total_filtered_student_report
    }

    query = query.join(model.Attendance, model.Student.student_id == model.Attendance.student_id, isouter=True)
    query = query.with_entities(
        model.Student,
        model.Attendance,
        model.Placement,
        sqlalchemy.func.round(
            (sqlalchemy.func.sum(sqlalchemy.case([(model.Attendance.attendance_status == 2, 1)], else_=0)).cast(sqlalchemy.Float) * 100 / sqlalchemy.func.count(model.Attendance.attendance_status).cast(sqlalchemy.Float)), 2
        ).label('attendance_percentage')
    )
    query = query.group_by(
        model.Student.student_id,
        model.Placement.status
    )
    # print(query)
    query = query.order_by(desc(model.Student.name)).offset(start).limit(length)

    student_reports = query.all()
    student_report_results = []
    for student_report in student_reports:
        # print('student_report: ', student_report, type(student_report))
        placement = None
        if isinstance(student_report, sqlalchemy.engine.row.Row):
            student = student_report[0]
            attendance = student_report[1]
            placement = student_report[2]
            attendance_percentage = student_report[3]
        else:
            student = student_report
        student_report_result = populate_student_report_record(student, attendance, placement, attendance_percentage)
        student_report_results.append(student_report_result)
    # response
    return jsonify({
        'data': student_report_results,
        'recordsFiltered': total_filtered_student_report,
        'recordsTotal': total_filtered_student_report,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200