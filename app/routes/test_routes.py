from flask import Blueprint, jsonify, request
from app.dbSql import get_db

test_routes = Blueprint('test_routes', __name__)

@test_routes.route('/save', methods=['POST'])
def save():
    # Get form data
    task_name = request.form.get('TaskName')
    selected_format = request.form.get('select')
    
    # Connect to the database
    db = get_db()
    cursor = db.cursor()

    # Insert task name into the Task table
    cursor.execute('INSERT INTO Task (taskname, report_format) VALUES (?, ?)', (task_name, selected_format))

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
        cursor.execute('INSERT INTO TaskFiles (filename, content, type, taskname, taskId) VALUES (?, ?, ?, ?, ?)',
                       (filename, content, file_type, task_name, task_id))
    db.commit()

    # Close the cursor and database connection
    cursor.close()

    # Return a response indicating success
    response_data = {
        'message': 'Task name and files stored successfully',
        'TaskName': task_name,
        'SelectedFormat': selected_format,
        'NumberOfFiles': len(files),
        'TaskId': task_id
    }
    
    return jsonify(response_data)

@test_routes.route('/tasks')
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
        for task in tasks:
            task_data = {
                'id': task[0],
                'taskname': task[1],
                'creation_date': task[2].strftime('%Y-%m-%d %H:%M:%S.%f'),
                'status': task[3],
                'report_format': task[4]
            }
            tasks_data.append(task_data)

        # Return tasks data as JSON array
        return jsonify(tasks_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500