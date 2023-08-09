import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, Boolean, CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, \
    UniqueConstraint, text, Enum, VARCHAR, Text
from sqlalchemy.orm import relationship, column_property, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.functions import coalesce, func

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


class Course(db.Model):
    __tablename__ = 'course'

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
    deleted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())


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
    reason_to_join = Column(Integer, nullable=True, default=5)  # 1 = placement, 2 = skill update, 3 = business, 4 = freelancing, 5 = other
    who_is = Column(Integer, nullable=True, default=1)  # 1 = student, 2 = working professional, 3 = business owner, 4 = housewife, 5 = job seeker
    lead_status = Column(Integer, nullable=True, default=1)  # 1 = pending, 2 = invalid number, 3 = looking something else, 4 = joined somewhere, 5 = fake lead, 6 = not interested, 7 = not receiving, 8 = admission done
    lead_insertion_mechanism_type = Column(Integer, nullable=True, default=1)  # 1=manual, 2=auto
    agent_id = Column(ForeignKey('agent.agent_id'), nullable=False)
    trainer_id = Column(ForeignKey('trainer.trainer_id'), nullable=True)
    fee_offer = Column(Integer, nullable=True)
    admission_status = Column(Integer, nullable=False, default=0)
    deleted = Column(Integer, nullable=False, default=0)
    submitted_lead_id = Column(ForeignKey('submitted_lead.submitted_lead_id'), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

    branch = relationship('Branch')
    source = relationship('Source')
    course = relationship('Course')
    course_mode = relationship('CourseMode')
    batch_time = relationship('BatchTime')
    agent = relationship('Agent', foreign_keys=[agent_id])
    pitch_by = relationship('Agent', foreign_keys=[pitch_by_id])
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
    json_course_learning_progress = Column(Text, nullable=True)
    batch_time_id = Column(ForeignKey('batch_time.batch_time_id'), nullable=False)
    source_id = Column(ForeignKey('source.source_id'), nullable=False)
    total_fee = Column(Integer, nullable=False)
    total_fee_paid = Column(Integer, nullable=False)
    total_pending_fee = Column(Integer, nullable=False)
    # receipt_installment_1_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_2_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_3_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    # receipt_installment_4_id = Column(ForeignKey('receipt.receipt_id'), nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    is_document_verified = Column(Integer, nullable=False, default=0)  # 0=pending, 1=accept, 2=reject, 3=verification pending
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
    batch_time = relationship('BatchTime')
    agent = relationship('Agent')
    country = relationship('Country')
    city = relationship('City')
    state = relationship('State')
    trainer = relationship('Trainer')
    user = relationship('User')
    # receipt = relationship('Receipt')
