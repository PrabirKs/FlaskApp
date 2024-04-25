from flask import Flask,Blueprint, jsonify, request
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, unset_jwt_cookies
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import URL
from sqlalchemy.sql import func
import bcrypt, base64
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = "prabir"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=100)
jwt = JWTManager(app)

#sqlALCHEMY set up
connection_string = 'DRIVER={SQL Server};SERVER=DESKTOP-A5FD6EQ\\SQLEXPRESS;DATABASE=TRADB;UID=sa;PWD=Prabir@123'
DATABASE_URL = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(DATABASE_URL, use_setinputsizes=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


#file size calculator
def format_file_size(bytes):
    if bytes < 1024:
        return str(bytes) + ' bytes'
    elif bytes < 1024 * 1024:
        return '{:.2f} KB'.format(bytes / 1024)
    else:
        return '{:.2f} MB'.format(bytes / (1024 * 1024))

#model 
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    jobs = relationship('Job', backref='user', lazy=True)

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    jobname = Column(String(100), nullable=False)
    creation_date = Column(DateTime, default=func.current_timestamp())
    status = Column(String(50), default="Pending")
    output_report = Column(String(20), default="xlsx")
    model = Column(String(100), default="TRA MODEL 1")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    files = relationship('JobFile', backref='job', lazy=True)

class JobFile(Base):
    __tablename__ = "jobfiles"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content = Column(LargeBinary, nullable=False)
    type = Column(String(50), nullable=False)
    creation_date = Column(DateTime, default=func.current_timestamp())
    size = Column(Integer)
    job_id = Column(Integer, ForeignKey('jobs.id'))
    
    

# Function to check database connection
def test_database_connection():
    try:
        engine.connect()
        return True
    except OperationalError:
        return False
   
@app.route("/")
def check():
    if test_database_connection():
        return "sucess db connection" 
    else:
        return "failed to connect db"

#register A USER
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'email and password are required'}), 400

    session = Session()
    existing_user = session.query(User).filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'email already exists'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = User(email=email, password=hashed_password)
    session.add(user)
    session.commit()
    session.close()

    return jsonify({'message': 'User registered successfully'}), 201

#LOG IN a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    session = Session()
    user = session.query(User).filter_by(email=email).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        session.close()
        return jsonify({'message': 'Invalid email or password'}), 401

    access_token = create_access_token(identity=user.id)
    session.close()
    return jsonify({'access_token': access_token, 'user' : email}), 200

@app.route('/logout', methods=['POST']) 
@jwt_required()
def logout():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id, expires_delta=False)
    # Remove access token from cookies
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    
    return response, 200
    
    
#Add a Jobs   
@app.route('/jobs', methods=['POST'])
@jwt_required()
def add_job():
    current_user_id = get_jwt_identity()
    jobname = request.form.get('jobname')
    output_report = request.form.get('select')
    model = request.form.get('selectModel')
    
    files = request.files.getlist('files')
    print(files)
    if not jobname:
        return jsonify({'message': 'Jobname is required'}), 400

    session = Session()

    # Check if the user exists
    user = session.query(User).filter_by(id=current_user_id).first()
    if not user:
        session.close()
        return jsonify({'message': 'User does not exist'}), 404

    # Create the job
    new_job = Job(
        jobname=jobname,
        user_id=current_user_id,
        model = model,
        output_report = output_report
    )
    session.add(new_job)
    session.commit()

    # Add files to the job
    for file_data in files:
        name = file_data.filename
        content = file_data.read()
        type = file_data.content_type
        size = len(content) if content else None

        # Ensure content is properly encoded as bytes
      
        new_file = JobFile(
            name=name,
            content=content,
            type=type,
            size=size,
            job_id=new_job.id
        )
        session.add(new_file)

    session.commit()
    session.close()

    return jsonify({'message': 'Job and files added successfully'}), 201

#Get Jobs
@app.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    current_user_id = get_jwt_identity()
    
    session = Session()
    
    # Retrieve jobs for the current user
    user_jobs = session.query(Job).filter_by(user_id=current_user_id).all()
    
    session.close()
    
    jobs_data = []
    jobs_len = len(user_jobs)
    for index, job in enumerate(user_jobs,start=1):
        job_data = {
            'id': jobs_len - index + 1,
            'jobname': job.jobname,
            'creation_date': job.creation_date.strftime('%Y-%m-%d %H:%M'),
            'status': job.status.lower(),
            'report_format': job.output_report,
            'model': job.model,
            'job_id':job.id
        }
        jobs_data.insert(0, job_data)
    
    return jsonify(jobs_data), 200

@app.route('/jobs/stop', methods=['POST'])
@jwt_required()
def stop_job():
    current_user_id = get_jwt_identity()
    job_id = request.json.get('job_id')  
    
    session = Session()

    # Retrieve the job by id and user_id to ensure the user has permission to cancel it
    job = session.query(Job).filter_by(id=job_id, user_id=current_user_id).first()

    if not job:
        session.close()
        return jsonify({'message': 'Job not found or user does not have permission'}), 404

    # Update the status of the job to "cancelled"
    job.status = 'Cancelled'
    session.commit()
    session.close()

    return jsonify({'message': 'Job cancelled successfully'}), 200

@app.route('/jobs/delete/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    current_user_id = get_jwt_identity()
    
    session = Session()
    
    # Check if the job exists
    job = session.query(Job).filter_by(id=job_id, user_id=current_user_id).first()
    if not job:
        session.close()
        return jsonify({'message': 'Job not found'}), 404

    # Delete the job
    session.delete(job)
    session.commit()
    
    session.close()
    
    return jsonify({'message': 'Job deleted successfully'}), 200

#Get All Files
@app.route('/files', methods=['GET'])
@jwt_required()
def get_files():
    current_user_id = get_jwt_identity()
    session = Session()

    # Query jobfiles table along with job and user details for the current user
    files_data = session.query(JobFile).join(Job).join(User).filter(User.id == current_user_id).all()

    files_info = []
    file_len = len(files_data)
    for index,job_file in enumerate(files_data,start=1):
        file_info = {
            'id':file_len-index+1,
            'name': job_file.name,
            'creation_date': job_file.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
            'size': format_file_size(job_file.size),
            'jobname': job_file.job.jobname,
            'user': job_file.job.user.email,
            'file_id': job_file.id
        }
        files_info.insert(0,file_info)

    session.close()

    return jsonify(files_info)

@app.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    current_user_id = get_jwt_identity()
    
    session = Session()
    
    # Check if the job exists
    file = session.query(JobFile).filter_by(id=file_id).first()
    if not file:
        session.close()
        return jsonify({'message': 'File not found'}), 404

    # Delete the job
    session.delete(file)
    session.commit()
    
    session.close()
    
    return jsonify({'message': 'File deleted successfully'}), 200

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    CORS(app)
    app.run(debug=True,port=8070)