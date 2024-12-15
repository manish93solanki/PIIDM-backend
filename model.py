import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, \
    UniqueConstraint, text, Enum, VARCHAR, Text, Time
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.functions import coalesce, func
import datetime

db = SQLAlchemy()


class UserRole(db.Model):
    __tablename__ = 'user_role'

    user_role_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class User(db.Model):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), unique=True, nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=True)
    token = Column(VARCHAR(255), unique=True, nullable=True)
    password = Column(VARCHAR(255), nullable=False, default='admin123')
    user_role_id = Column(ForeignKey('user_role.user_role_id'), nullable=False)
    is_active = Column(Integer, nullable=True, default=1)  # 0 = deactivate, 1 = active
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    user_role = relationship('UserRole')


class Branch(db.Model):
    __tablename__ = 'branch'

    branch_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class Source(db.Model):
    __tablename__ = 'source'

    source_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class CourseCategory(db.Model):
    __tablename__ = 'course_category'

    course_category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class Course(db.Model):
    __tablename__ = 'course'

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    course_category_id = Column(ForeignKey('course_category.course_category_id'), nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    course_category = relationship('CourseCategory')


class CourseMode(db.Model):
    __tablename__ = 'course_mode'

    course_mode_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class CourseContent(db.Model):
    __tablename__ = 'course_content'

    course_content_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    instructor_name = Column(VARCHAR(255), nullable=False)
    json_modules = Column(Text, nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class CourseContentClassRecording(db.Model):
    __tablename__ = 'course_content_class_recording'

    course_content_class_recording_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=True)
    batch_id = Column(ForeignKey('batch.batch_id'), nullable=True)
    json_modules = Column(Text, nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    batch = relationship('Batch')
    trainer = relationship('Trainer')


class Agent(db.Model):
    __tablename__ = 'agent'

    agent_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), unique=True, nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship('User')


class Trainer(db.Model):
    __tablename__ = 'trainer'

    trainer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), unique=True, nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship('User')


class BatchTime(db.Model):
    __tablename__ = 'batch_time'

    batch_time_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class CallLogs(db.Model):
    __tablename__ = 'call_logs'

    call_logs_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.user_id'), nullable=True)
    name = Column(VARCHAR(255), nullable=True)   
    phone_num = Column(VARCHAR(255), nullable=True)
    call_time = Column(DateTime, nullable=True)
    call_time_duration = Column(VARCHAR(255), nullable=True)
    call_type = Column(VARCHAR(255), nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship('User')


class Country(db.Model):
    __tablename__ = 'country'

    country_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    dial_code = Column(VARCHAR(255), nullable=False)
    code = Column(VARCHAR(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class State(db.Model):
    __tablename__ = 'state'

    state_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    code = Column(VARCHAR(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class City(db.Model):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class Lead(db.Model):
    __tablename__ = 'lead'

    lead_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), nullable=False)
    alternate_phone_num = Column(VARCHAR(255), nullable=True)
    email = Column(VARCHAR(255), nullable=True)
    lead_date = Column(Date, nullable=False)
    lead_time = Column(Time, nullable=True, default=datetime.datetime.now().time())
    remarks = Column(Text, nullable=True)
    country_id = Column(ForeignKey('country.country_id'), nullable=False)
    state_id = Column(ForeignKey('state.state_id'), nullable=True)
    area = Column(VARCHAR(255), nullable=True)
    city_id = Column(ForeignKey('city.city_id'), nullable=False)
    branch_id = Column(ForeignKey('branch.branch_id'), nullable=False)
    source_id = Column(ForeignKey('source.source_id'), nullable=False)
    course_id = Column(ForeignKey('course.course_id'), nullable=False)
    course_mode_id = Column(ForeignKey('course_mode.course_mode_id'), nullable=True)
    batch_time_id = Column(ForeignKey('batch_time.batch_time_id'), nullable=False)
    next_action_date = Column(Date, nullable=True)
    next_action_remarks = Column(Text, nullable=True)
    details_sent = Column(Integer, nullable=True)
    visit_date = Column(Date, nullable=True)
    pitch_by_id = Column(ForeignKey('agent.agent_id'), nullable=True)
    auto_populate_visitdate_pitchby = Column(Integer, nullable=True, default=0)
    demo_date = Column(Date, nullable=True)
    referred_by = Column(VARCHAR(255), nullable=True)
    broadcast = Column(Integer, nullable=True)
    age = Column(Integer, nullable=True, default=1)  # 1 = 18-25, 2 = 26-35, 3 = 36-Above
    gender = Column(Integer, nullable=True, default=1)  # 1 = male, 2 = female
    reason_to_join = Column(Integer, nullable=True,
                            default=5)  # 1 = placement, 2 = skill update, 3 = business, 4 = freelancing, 5 = other
    who_is = Column(Integer, nullable=True,
                    default=1)  # 1 = student, 2 = working professional, 3 = business owner, 4 = housewife, 5 = job seeker
    lead_status = Column(Integer, nullable=True,
                         default=1)  # 1 = pending, 2 = invalid number, 3 = looking something else, 4 = joined somewhere, 5 = fake lead, 6 = not interested, 7 = not receiving, 8 = admission done
    lead_insertion_mechanism_type = Column(Integer, nullable=True, default=1)  # 1=manual, 2=auto
    agent_id = Column(ForeignKey('agent.agent_id'), nullable=False)
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=True)
    fee_offer = Column(Integer, nullable=True)
    admission_status = Column(Integer, nullable=False, default=0)
    deleted = Column(Integer, nullable=False, default=0)
    submitted_lead_id = Column(ForeignKey('submitted_lead.submitted_lead_id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    updated_by_id = Column(ForeignKey('agent.agent_id'), nullable=True)

    branch = relationship('Branch')
    source = relationship('Source')
    course = relationship('Course')
    course_mode = relationship('CourseMode')
    batch_time = relationship('BatchTime')
    agent = relationship('Agent', foreign_keys=[agent_id])
    pitch_by = relationship('Agent', foreign_keys=[pitch_by_id])
    updated_by = relationship('Agent', foreign_keys=[updated_by_id])
    trainer = relationship('Trainer')
    country = relationship('Country')
    state = relationship('State')
    city = relationship('City')
    submitted_lead = relationship('SubmittedLead')


class SubmittedLead(db.Model):
    __tablename__ = 'submitted_lead'

    submitted_lead_id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, nullable=True)
    name = Column(VARCHAR(255), nullable=True)
    phone_num = Column(VARCHAR(255), nullable=True)
    email = Column(VARCHAR(255), nullable=True)
    hash_id = Column(VARCHAR(255), nullable=True)
    referer = Column(VARCHAR(255), nullable=True)
    referer_title = Column(VARCHAR(255), nullable=True)
    form_name = Column(VARCHAR(255), nullable=True)
    campaign_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)
    user_ip = Column(VARCHAR(255), nullable=True)
    user_agent = Column(VARCHAR(255), nullable=True)
    actions_count = Column(Integer, nullable=True)
    actions_succeeded_count = Column(Integer, nullable=True)
    status = Column(VARCHAR(255), nullable=True)
    submitted_status = Column(Integer, nullable=True)  # 0=deleted, 1=new, 2=pending, 3=accepted, 4=rejected
    created_at_gmt = Column(DateTime, nullable=True)
    updated_at_gmt = Column(DateTime, nullable=True)
    remark = Column(VARCHAR(255), nullable=True)
    agent_id = Column(ForeignKey('agent.agent_id'), nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())

    agent = relationship('Agent')


class PaymentMode(db.Model):
    __tablename__ = 'payment_mode'

    payment_mode_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


class InstalmentNumber(enum.Enum):
    first = 1
    second = 2
    third = 3
    fourth = 4


class Receipt(db.Model):
    __tablename__ = 'receipt'

    receipt_id = Column(Integer, primary_key=True, autoincrement=True)
    installment_num = Column(Integer, nullable=True)
    installment_payment = Column(Integer, nullable=True)
    installment_payment_mode_id = Column(ForeignKey('payment_mode.payment_mode_id'), nullable=True)
    installment_payment_date = Column(Date, nullable=True)
    installment_payment_transaction_number = Column(VARCHAR(255), nullable=True)
    student_id = Column(ForeignKey('student.student_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    payment_mode = relationship('PaymentMode')
    student = relationship('Student')


class Student(db.Model):
    __tablename__ = 'student'

    student_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), nullable=False)
    alternate_phone_num = Column(VARCHAR(255), nullable=True)
    email = Column(VARCHAR(255), nullable=True)
    dob = Column(Date, nullable=True)
    admission_date = Column(Date, nullable=False)
    area = Column(Text, nullable=True)
    pincode = Column(VARCHAR(255), nullable=True)
    highest_education = Column(VARCHAR(255), nullable=True)
    occupation = Column(VARCHAR(255), nullable=True)
    purpose_for_course = Column(VARCHAR(255), nullable=True)
    who_you_are = Column(VARCHAR(255), nullable=True)
    referred_by = Column(VARCHAR(255), nullable=True)
    front_image_path = Column(VARCHAR(255), nullable=True)
    back_image_path = Column(VARCHAR(255), nullable=True)
    passport_image_path = Column(VARCHAR(255), nullable=True)
    branch_id = Column(ForeignKey('branch.branch_id'), nullable=False)
    country_id = Column(ForeignKey('country.country_id'), nullable=False)
    city_id = Column(ForeignKey('city.city_id'), nullable=False)
    state_id = Column(ForeignKey('state.state_id'), nullable=True)
    agent_id = Column(ForeignKey('agent.agent_id'), nullable=True)  # tutor is agent
    # tutor_id = Column(ForeignKey('agent.agent_id'), nullable=False)  # tutor is agent
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=True)
    course_id = Column(ForeignKey('course.course_id'), nullable=False)
    course_mode_id = Column(ForeignKey('course_mode.course_mode_id'), nullable=True)
    course_content_id = Column(ForeignKey('course_content.course_content_id'), nullable=False, default=1)
    course_content_class_recording_id = Column(ForeignKey('course_content_class_recording.course_content_class_recording_id'), nullable=False, default=1)
    json_course_learning_progress = Column(Text, nullable=True)
    json_course_learning_progress_class_recording = Column(Text, nullable=True)
    batch_time_id = Column(ForeignKey('batch_time.batch_time_id'), nullable=False)
    source_id = Column(ForeignKey('source.source_id'), nullable=False)
    batch_id = Column(ForeignKey('batch.batch_id'), nullable=True)
    total_fee = Column(Integer, nullable=False)
    total_fee_paid = Column(Integer, nullable=False)
    total_pending_fee = Column(Integer, nullable=False)
    # receipt_installment_1_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_2_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_3_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_4_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    is_document_verified = Column(Integer, nullable=False,
                                  default=0)  # 0=pending, 1=accept, 2=reject, 3=verification pending
    lead_id = Column(ForeignKey('lead.lead_id'), nullable=True)
    user_id = Column(ForeignKey('user.user_id'), nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    branch = relationship('Branch')
    source = relationship('Source')
    course = relationship('Course')
    course_mode = relationship('CourseMode')
    course_content = relationship('CourseContent')
    course_content_class_recording = relationship('CourseContentClassRecording')
    batch_time = relationship('BatchTime')
    batch = relationship('Batch')
    agent = relationship('Agent')
    country = relationship('Country')
    city = relationship('City')
    state = relationship('State')
    trainer = relationship('Trainer')
    user = relationship('User')
    # receipt = relationship('Receipt')


class Batch(db.Model):
    __tablename__ = 'batch'

    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    batch_num = Column(Integer, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    batch_date = Column(Date, nullable=False)
    total_seats = Column(Integer, nullable=False, default=40)
    seats_occupied = Column(Integer, nullable=False, default=0)
    seats_vacant = Column(Integer, nullable=False, default=40)
    course_id = Column(ForeignKey('course.course_id'), nullable=False)
    batch_time_id = Column(ForeignKey('batch_time.batch_time_id'), nullable=False)
    course_mode_id = Column(ForeignKey('course_mode.course_mode_id'), nullable=False)
    branch_id = Column(ForeignKey('branch.branch_id'), nullable=False)
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)

    course = relationship('Course')
    batch_time = relationship('BatchTime')
    course_mode = relationship('CourseMode')
    branch = relationship('Branch')
    trainer = relationship('Trainer')


class HR(db.Model):
    __tablename__ = 'hr'

    hr_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    phone_num = Column(VARCHAR(255), unique=True, nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    user = relationship('User')


class Placement(db.Model):
    __tablename__ = 'placement'

    placement_id = Column(Integer, primary_key=True, autoincrement=True)
    joined_course_for = Column(VARCHAR(255), nullable=True)  # 1=Job, 2=Skills, 3=Business, 4=Freelancing
    job_type = Column(VARCHAR(255), nullable=True)  # 1=Full Time, 2=Part Time, 3=Work from home
    end_date = Column(Date, nullable=True)
    education = Column(VARCHAR(255), nullable=True)
    technical_knowledge = Column(VARCHAR(255), nullable=True)
    project = Column(VARCHAR(255), nullable=True)
    mock_test = Column(VARCHAR(255), nullable=True)
    test = Column(VARCHAR(255), nullable=True)
    communication = Column(VARCHAR(255), nullable=True)
    preferred_location = Column(VARCHAR(255), nullable=True)
    remark = Column(VARCHAR(255), nullable=True)
    status = Column(Integer, nullable=True)   # 1=Not Interested, 2=On-Going, 3=Placed
    student_id = Column(ForeignKey('student.student_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    student = relationship('Student')


class Resume(db.Model):
    __tablename__ = 'resume'

    resume_id = Column(Integer, primary_key=True, autoincrement=True)
    upload_profile_picture = Column(VARCHAR(255), nullable=True)
    full_name = Column(VARCHAR(255), nullable=True)
    phone_num = Column(VARCHAR(255), unique=True, nullable=True)
    alternate_phone_num = Column(VARCHAR(255), unique=True, nullable=True)
    email = Column(VARCHAR(255), unique=True, nullable=True)
    area = Column(VARCHAR(255), nullable=True)
    hometown = Column(VARCHAR(255), nullable=True)
    city = Column(VARCHAR(255), nullable=True)
    state = Column(VARCHAR(255), nullable=True)
    pincode = Column(Integer, nullable=True)
    country = Column(VARCHAR(255), nullable=True)
    linkedin_link = Column(VARCHAR(255), unique=True, nullable=True)
    job_role = Column(VARCHAR(255), nullable=True)
    about_me = Column(VARCHAR(255), nullable=True)
    skill = Column(Text, nullable=True)
    tool = Column(Text, nullable=True)
    project_name_1 = Column(VARCHAR(255), nullable=True)
    project_link_1 = Column(VARCHAR(255), nullable=True)
    project_task_done_1 = Column(VARCHAR(255), nullable=True)
    project_name_2 = Column(VARCHAR(255), nullable=True)
    project_link_2 = Column(VARCHAR(255), nullable=True)
    project_task_done_2 = Column(VARCHAR(255), nullable=True)
    project_name_3 = Column(VARCHAR(255), nullable=True)
    project_link_3 = Column(VARCHAR(255), nullable=True)
    project_task_done_3 = Column(VARCHAR(255), nullable=True)
    project_name_4 = Column(VARCHAR(255), nullable=True)
    project_link_4 = Column(VARCHAR(255), nullable=True)
    project_task_done_4 = Column(VARCHAR(255), nullable=True)
    class_10_school_name = Column(VARCHAR(255), nullable=True)
    class_10_passed_out_year = Column(VARCHAR(255), nullable=True)
    class_12_school_name = Column(VARCHAR(255), nullable=True)
    class_12_passed_out_year = Column(VARCHAR(255), nullable=True)
    graduation_college_name = Column(VARCHAR(255), nullable=True)
    graduation_college_passed_out_year = Column(VARCHAR(255), nullable=True)
    post_graduation_college_name = Column(VARCHAR(255), nullable=True)
    post_graduation_college_passed_out_year = Column(VARCHAR(255), nullable=True)
    certificate_name_1 = Column(VARCHAR(255), nullable=True)
    certificate_passed_out_year_1 = Column(VARCHAR(255), nullable=True)
    certificate_name_2 = Column(VARCHAR(255), nullable=True)
    certificate_passed_out_year_2 = Column(VARCHAR(255), nullable=True)
    certificate_name_3 = Column(VARCHAR(255), nullable=True)
    certificate_passed_out_year_3 = Column(VARCHAR(255), nullable=True)
    certificate_name_4 = Column(VARCHAR(255), nullable=True)
    certificate_passed_out_year_4 = Column(VARCHAR(255), nullable=True)
    student_id = Column(ForeignKey('student.student_id'), nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    student = relationship('Student')


class Lecture(db.Model):
    __tablename__ = 'lecture'

    lecture_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=True)
    course_id = Column(ForeignKey('course.course_id'), nullable=False)
    course_mode_id = Column(ForeignKey('course_mode.course_mode_id'), nullable=True)
    batch_time_id = Column(ForeignKey('batch_time.batch_time_id'), nullable=False)
    batch_id = Column(ForeignKey('batch.batch_id'), nullable=True)
    zoom_link = Column(VARCHAR(255), nullable=True)
    batch_date = Column(Date, nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    user_id = Column(ForeignKey('user.user_id'), nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    course = relationship('Course')
    course_mode = relationship('CourseMode')
    batch_time = relationship('BatchTime')
    batch = relationship('Batch')
    trainer = relationship('Trainer')
    user = relationship('User')


class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id = Column(Integer, primary_key=True, autoincrement=True)
    lecture_id = Column(ForeignKey('lecture.lecture_id'), nullable=False)
    student_id = Column(ForeignKey('student.student_id'), nullable=False)
    attendance_status = Column(Integer, nullable=False, default=0)  # 0=no_attendance, 1=absent #2=present
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    lecture = relationship('Lecture')
    student = relationship('Student')

