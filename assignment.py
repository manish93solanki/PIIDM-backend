from flask import current_app as app, request, Blueprint, jsonify
import model
import json
import datetime
from auth_middleware import token_required
from db_operations import bulk_insert
from sqlalchemy import desc
from flask import send_file, abort
import mimetypes
import os

assignment_bp = Blueprint('assignment_bp', __name__, url_prefix='/api/assignment')


def is_assignment_exist(title, description, trainer_id, json_batch_ids, assignment_date, total_marks, user_id):
    cursor = app.session.query(model.Assignment).filter(
        model.Assignment.title == title,
        model.Assignment.description == description,
        model.Assignment.trainer_id == trainer_id,
        model.Assignment.json_batch_ids == json_batch_ids,
        model.Assignment.assignment_date == assignment_date,
        model.Assignment.total_marks == total_marks,
        model.Assignment.user_id == user_id
    )
    records = list(cursor)
    return records


def populate_assignment_record(assignment):
    assignment_result = {}
    for key in assignment.__table__.columns.keys():
        value = getattr(assignment, key)
        if key in ('assignment_date', ) and value:
            # value = datetime.datetime.strftime('%Y-%m-%d')
            value = str(value)

        assignment_result[key] = value
        if key == 'trainer_id':
            trainer = assignment.trainer
            assignment_result[key] = {}
            for trainer_key in trainer.__table__.columns.keys():
                trainer_value = getattr(trainer, trainer_key)
                assignment_result[key][trainer_key] = trainer_value
            assignment_result['trainer'] = assignment_result.pop(key)
        # if key == 'batch_id':
        #     batch = assignment.batch
        #     assignment_result[key] = {}
        #     if batch:
        #         for batch_key in batch.__table__.columns.keys():
        #             batch_value = getattr(batch, batch_key)
        #             assignment_result[key][batch_key] = batch_value
        #     assignment_result['batch'] = assignment_result.pop(key)
    return assignment_result


def populate_submission_record(submission):
    submission_result = {}
    for key in submission.__table__.columns.keys():
        value = getattr(submission, key)

        submission_result[key] = value
        if key == 'assignment_id':
            assignment = submission.assignment
            submission_result[key] = {}
            for assignment_key in assignment.__table__.columns.keys():
                assignment_value = getattr(assignment, assignment_key)
                submission_result[key][assignment_key] = assignment_value
            submission_result['assignment'] = submission_result.pop(key)
        if key == 'student_id':
            student = submission.student
            submission_result[key] = {}
            for student_key in student.__table__.columns.keys():
                student_value = getattr(student, student_key)
                submission_result[key][student_key] = student_value
            submission_result['student'] = submission_result.pop(key)
    return submission_result


@assignment_bp.route('/add', methods=['POST'])
@token_required
def add_assignment(current_user):
    if request.method == 'POST':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        print(data)
        for item in data:
            if is_assignment_exist(item['title'], item['description'], item['trainer_id'], item['json_batch_ids'], item['assignment_date'], item['total_marks'], item['user_id']):
                return {'error': 'Given assignment is already created.'}, 409
            assignment = model.Assignment()
            assignment.title = item['title']
            assignment.description = item['description']
            assignment.trainer_id = item['trainer_id']
            assignment.json_batch_ids = item['json_batch_ids']
            assignment.total_marks = item['total_marks']
            assignment.user_id = item['user_id']
            assignment.is_assigned_to_students = 0 # not assigned by default
            assignment.assignment_date = datetime.datetime.strptime(item['assignment_date'], '%d/%m/%Y')
            records_to_add.append(assignment)
        bulk_insert(records_to_add)
    return {'message': 'Assignment is created.'}, 201


@assignment_bp.route('/update/<assignment_id>', methods=['PUT'])
@token_required
def update_assignment(current_user, assignment_id):
    # batch_ids can not be changed.
    if request.method == 'PUT':
        if not request.is_json:
            pass
        data = request.get_json()
        records_to_add = []
        for item in data:
            assignment = model.Assignment.query.filter(model.Assignment.assignment_id == int(assignment_id)).first()
            assignment.title = item['title']
            assignment.description = item['description']
            assignment.total_marks = item['total_marks']
            assignment.trainer_id = item['trainer_id']
            assignment.user_id = item['user_id']
            assignment.is_assigned_to_students = 0 # not assigned by default
            assignment.assignment_date = datetime.datetime.strptime(item['assignment_date'], '%d/%m/%Y')
            assignment.updated_at = datetime.datetime.now().replace(microsecond=0)
            records_to_add.append(assignment)
        print(records_to_add)
        bulk_insert(records_to_add)
    return {'message': 'Assignment is updated.'}, 200


# @assignment_bp.route('/update/<assignment_id>', methods=['PUT'])
# @token_required
# def update_assignment(current_user, assignment_id):
#     try:
#         if not request.is_json:
#             return {'error': 'Bad Request.'}, 400
#         data = request.get_json()
#         records_to_add = []
#         for item in data:
#             assignment = model.Assignment.query.filter(model.Assignment.assignment_id == int(assignment_id)).first()
#             for key, value in item.items():
#                 if key == 'title':
#                     setattr(assignment, 'title', item['title'])
#                 setattr(assignment, key, value)
#             records_to_add.append(assignment)
#         bulk_insert(records_to_add)
#         return jsonify({'message': 'Successfully Updated.'}), 200
#     except Exception as ex:
#         return jsonify({'error': str(ex)}), 500

 
@assignment_bp.route('/delete/<delete_id>', methods=['DELETE'])
@token_required
def delete_assignment(current_user, delete_id):
    app.session.query(model.Assignment).filter(model.Assignment.assignment_id == int(delete_id)).delete()
    # app.session.commit()
    return {}


@assignment_bp.route('/all', methods=['GET'])
@token_required
def get_assignment(current_user):
    query = app.session.query(model.Assignment).filter(model.Assignment.deleted==0)

    if current_user.user_role_id == 4:  # role == trainer
        trainer_id = app.session.query(model.Trainer.trainer_id).filter(model.Trainer.user_id == current_user.user_id, model.Trainer.deleted == 0).first()
        if trainer_id:
            trainer_id = trainer_id[0]
        query = query.filter(model.Assignment.trainer_id == trainer_id)

    assignments = list(query.all())
    results = []
    for assignment in assignments:
        assignment_result = populate_assignment_record(assignment)
        results.append(assignment_result)
    return jsonify(results), 200


@assignment_bp.route('/select-paginate-advanced', methods=['GET'])
@token_required
def get_paginated_assignment_advanced(current_user):
    total_assignments = model.Assignment.query.filter(model.Assignment.deleted == 0).count()

    # filtering data
    query = app.session.query(model.Assignment)
    query = query.filter(model.Assignment.deleted == 0)

    if current_user.user_role_id == 4:  # role == trainer
        trainer_id = app.session.query(model.Trainer.trainer_id).filter(model.Trainer.user_id == current_user.user_id, model.Trainer.deleted == 0).first()
        if trainer_id:
            trainer_id = trainer_id[0]
        query = query.filter(model.Assignment.trainer_id == trainer_id)
        total_assignments = model.Assignment.query.filter(model.Assignment.trainer_id == trainer_id, model.Assignment.deleted == 0).count()

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search_term = request.args.get('search[value]', type=str)
    print('search_term: ', search_term)
    query = query.filter(model.Assignment.name.like(f'{search_term}%')) if search_term else query

    total_filtered_assignment = query.count()  # total filtered assignment
    basic_stats = {
        'total_assignments': total_filtered_assignment
    }

    query = query.order_by(desc(model.Assignment.assignment_date)).offset(start).limit(length)

    assignments = query.all()
    assignment_results = []
    for assignment in assignments:
        assignment_result = populate_assignment_record(assignment)
        assignment_results.append(assignment_result)
    # response
    return jsonify({
        'data': assignment_results,
        'recordsFiltered': total_filtered_assignment,
        'recordsTotal': total_assignments,
        'draw': request.args.get('draw', type=int),
        'basic_stats': basic_stats
    }), 200



@assignment_bp.route('/assign/<assignment_id>', methods=['POST'])
@token_required
def assign_assignment(current_user, assignment_id):
    assignment_id = int(assignment_id)

    submission = app.session.query(model.Submission).filter(
        model.Submission.assignment_id==assignment_id,
        model.Submission.deleted == 0
    ).first()
    if submission:
        return {'error': 'Assignment is already assigned to students.'}, 409

    # It's compulsory to add students to the assignment to have their attendance later.
    records_to_add = []

    # Get recently added assignment
    assignment = app.session.query(model.Assignment).filter(
        model.Assignment.assignment_id==assignment_id,
        model.Assignment.deleted == 0
    ).first()
    batch_ids = json.loads(assignment.json_batch_ids)
    for batch_id in batch_ids:
        # Get students from the batch by assignment
        students = app.session.query(model.Student).filter(
            model.Student.batch_id==batch_id,
            model.Student.deleted==0
        ).all()
        for student in students:
            submission = model.Submission()
            submission.assignment_id = assignment.assignment_id
            submission.student_id = student.student_id
            records_to_add.append(submission)

    bulk_insert(records_to_add)

    records_to_add = []
    assignment = app.session.query(model.Assignment).filter(
        model.Assignment.assignment_id==assignment_id,
        model.Assignment.deleted == 0
    ).first()
    # Update assignment to be assigned to students
    print('assignment: ', assignment)
    assignment.is_assigned_to_students = 1
    assignment.updated_at = datetime.datetime.now()
    records_to_add.append(assignment)
    bulk_insert(records_to_add)
    return {'message': 'Assigned to students.'}, 201


@assignment_bp.route('/submission/view/<assignment_id>', methods=['GET'])
@token_required
def get_submission(current_user, assignment_id):
    assignment_id = int(assignment_id)

    # Get Submission
    submissions = app.session.query(model.Submission).filter(
        model.Submission.assignment_id==assignment_id,
        model.Submission.deleted==0
    ).all()
    submissions = list(submissions)

    if not submissions:
        # No submissions for newly created assignment
        return {'error': 'Assignment was not created succesfully. Hence no submissions can be taken. Ask admin to manually delete the assignment and re-create it.'}, 409

    results = []
    for submission in submissions:
        submission_result = populate_submission_record(submission)
        results.append(submission_result)
    return jsonify(results), 200


@assignment_bp.route('/submission/update/<assignment_id>', methods=['PUT'])
@token_required
def update_submission(current_user, assignment_id):
    if request.method == 'PUT':
        if not request.is_json:
            pass
        data = request.get_json()
        submission_ids = [x['submission_id'] for x in data]
        submissions = app.session.query(model.Submission).filter(
            model.Submission.submission_id.in_(submission_ids),
            model.Submission.assignment_id == int(assignment_id),
            model.Submission.deleted==0
        ).all()

        records_to_add = []
        for item in data:
            for submission in submissions:
                if submission.submission_id == item['submission_id']:
                    submission.marks_obtained = item['marks_obtained']
                    submission.feedback = item['feedback']
                    submission.submission_status = item['submission_status']
                    submission.updated_at = datetime.datetime.now()
                    records_to_add.append(submission)
                    break
        bulk_insert(records_to_add)
    return {'message': 'Submission updated.'}, 201


@assignment_bp.route('/submission/view-file', methods=['GET'])
def view_file():
    file_path = request.args.get('file_path')
    if not file_path or not os.path.isfile(file_path):
        return abort(404, description="File not found.")

    mime_type, _ = mimetypes.guess_type(file_path)
    # Only allow pdf, plain text, and word documents
    allowed_types = [
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    if mime_type not in allowed_types:
        return abort(415, description="Unsupported file type.")

    return send_file(file_path, mimetype=mime_type)


# /***  APIs for student ***/

@assignment_bp.route('/student/view/<assignment_id>', methods=['GET'])
@token_required
def view_assignment(current_user, assignment_id):
    # Not in use now.
    if current_user.user_role_id != 3:  # role == student
        return {'error': 'You are not allowed to view the assignment'}, 403
    assignment = app.session.query(model.Assignment).filter(
        model.Assignment.assignment_id == int(assignment_id),
        model.Assignment.deleted == 0
    ).first()
    if not assignment:
        return {'error': 'Assignment not found.'}, 404
    assignment_result = populate_assignment_record(assignment)
    return jsonify(assignment_result), 200


@assignment_bp.route('/student/view_by_course/<course_id>', methods=['GET'])
@token_required
def view_assignment_by_course(current_user, course_id):
    # View all assignments for a student in a given course.
    if current_user.user_role_id != 3:  # role == student
        return {'error': 'You are not allowed to view the assignment'}, 403
    
    student = app.session.query(model.Student).filter(
        model.Student.user_id == current_user.user_id,
        model.Student.course_id == int(course_id),
        model.Student.deleted == 0,
    ).first()
    if not student:
        return {'error': 'Student does not exist.'}, 403

    # Find assignments for the student's batch and given course_id
    assignments = app.session.query(model.Assignment).filter(
        model.Assignment.deleted == 0,
        model.Assignment.json_batch_ids.like(f'%{student.batch_id}%'),
    ).all()

    if not assignments:
        return {'error': 'No assignments found for this course.'}, 404

    results = [populate_assignment_record(a) for a in assignments]
    return jsonify(results), 200


@assignment_bp.route('/student/submission/view/<assignment_id>', methods=['GET'])
@token_required
def get_submission_by_student(current_user, assignment_id):
    if current_user.user_role_id != 3:  # role == student
        return {'error': 'You are not allowed to view the assignment'}, 403
    student = app.session.query(model.Student).filter(model.Student.user_id == current_user.user_id).first()
    if not student:
        return {'error': 'Student does not exist.'}, 403
    
    assignment_id = int(assignment_id)
    student_id = int(student.student_id)

    # Get Submission
    submission = app.session.query(model.Submission).filter(
        model.Submission.assignment_id==assignment_id,
        model.Submission.student_id==student_id,
        model.Submission.deleted==0
    ).first()

    if not submission:
        return {'error': 'No submission found for the given assignment and student.'}, 404

    submission_result = populate_submission_record(submission)
    return jsonify(submission_result), 200


@assignment_bp.route('/student/submission/upload/<assignment_id>', methods=['POST'])
@token_required
def upload_submission(current_user, assignment_id):
    if current_user.user_role_id != 3:  # role == student
        return {'error': 'You are not allowed to view the assignment'}, 403
    student = app.session.query(model.Student).filter(model.Student.user_id == current_user.user_id).first()
    if not student:
        return {'error': 'Student does not exist.'}, 403
    
    assignment_id = int(assignment_id)
    student_id = int(student.student_id)

    records_to_update = []
    file_ = request.files["file"]
    file_path = f'data/uploaded_assignment_submissions/{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}-{file_.filename}'
    file_.save(file_path)
    submission = app.session.query(model.Submission).filter(
        model.Submission.assignment_id == assignment_id,
        model.Submission.student_id == student_id,
        model.Submission.deleted == 0
    ).first()
    if not submission:
        return {'error': 'No submission found for the given assignment and student.'}, 404
    
    if submission.submission_status == 2:  # If the submission was rejected, we allow re-submission
        submission.submission_status = 3

    submission.document_uploaded_path = file_path
    submission.updated_at = datetime.datetime.now()
    records_to_update.append(submission)
    bulk_insert(records_to_update)
    return jsonify({'message': 'Assignment submitted successfully.'}), 201
