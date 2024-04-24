from flask import Blueprint, jsonify, request
from app.dbSql import get_db
from app.service.sizeConverter import format_file_size
job_routes = Blueprint('job_routes', __name__)

@job_routes.route('/save', methods=['POST'])
def save():
    # Get form data
    task_name = request.form.get('TaskName')
    selected_format = request.form.get('select')
    model = request.form.get('selectModel')
    # Connect to the database
    db = get_db()
    cursor = db.cursor()

    if(selected_format != 'undefined'):
    # Insert task name into the Task table
        cursor.execute('INSERT INTO Task (taskname, report_format, model) VALUES (?, ?, ?)', (task_name, selected_format,model))
    else:
        print("2")
        cursor.execute('INSERT INTO Task (taskname, model) VALUES (?, ?)', (task_name,model))
    db.commit()

    # Get the ID of the inserted task
    cursor.execute('SELECT id FROM Task WHERE taskname = ?', (task_name,))
    task_id = cursor.fetchone()[0]

    # Insert files into the TaskFiles table using the retrieved task ID
    files = request.files.getlist('files')
    for file in files:
        filename = file.filename
        content = file.read()
        file_type = file.content_type
        file_size = len(content)
        cursor.execute('INSERT INTO TaskFiles (filename, content, type, taskname, taskId, size) VALUES (?, ?, ?, ?, ?, ?)',
                       (filename, content, file_type, task_name, task_id, file_size))
    db.commit()

    # Close the cursor and database connection
    cursor.close()

    # Return a response indicating success
    response_data = {
        'message': 'Task name and files stored successfully',
        'TaskName': task_name,
        'SelectedFormat': selected_format,
        'NumberOfFiles': len(files),
        'TaskId': task_id,
        'model':model
    }
    
    return jsonify(response_data)

@job_routes.route('/tasks')
def get_tasks():
    try:
        # Connect to the database
        db = get_db()
        cursor = db.cursor()

        # Fetch all tasks from the Task table
        cursor.execute('SELECT * FROM Task')
        tasks = cursor.fetchall()

        # Close the cursor and database connection
        cursor.close()

        # Prepare tasks data in JSON format
        tasks_data = []
        for index,task in enumerate(tasks,start=1):
            task_data = {
                'id': index,
                'jobname': task[1],
                'creation_date': task[2].strftime('%Y-%m-%d %H:%M'),
                'status': task[3],
                'report_format': task[4],
                'model':task[5]
            }
            tasks_data.append(task_data)

        # Return tasks data as JSON array
        return jsonify(tasks_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@job_routes.route('/files')
def get_files():
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM TaskFiles')
        files = cursor.fetchall()

        cursor.close()

        files_db = []
        for index,file in enumerate(files,start=1):
            file_data = {
                'id': index,
                'filename': file[1],
                'type': file[3],
                'jobname': file[4],
                'creation_date': file[5].strftime('%Y-%m-%d %H:%M'),
                'task_Id': file[6],
                'size' : format_file_size(int(file[7]))
            }
            files_db.append(file_data)

        # Return files data as JSON array
        return jsonify(files_db), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500