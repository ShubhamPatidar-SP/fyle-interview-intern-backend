from flask import Blueprint, request, jsonify
from core.libs.decorators import validate_principal
from core.models.assignments import Assignment

principal_blueprint = Blueprint('principal', __name__)

@principal_blueprint.route('/assignments', methods=['GET'])
@validate_principal
def list_principal_assignments():
    principal_id = request.headers.get('X-Principal')['principal_id']

    # Fetch and filter assignments for the principal
    assignments = Assignment.query.filter_by(teacher_id=principal_id, state='SUBMITTED' or 'GRADED').all()

    # Convert assignments to JSON format
    assignments_data = [
        {
            "content": assignment.content,
            "created_at": assignment.created_at.isoformat(),
            "grade": assignment.grade,
            "id": assignment.id,
            "state": assignment.state,
            "student_id": assignment.student_id,
            "teacher_id": assignment.teacher_id,
            "updated_at": assignment.updated_at.isoformat(),
        }
        for assignment in assignments
    ]

    return jsonify({"data": assignments_data})

@principal_blueprint.route('/teachers', methods=['GET'])
@validate_principal
def list_teachers():
    # Fetch all teachers
    teachers = Teacher.query.all()

    # Convert teachers to JSON format
    teachers_data = [
        {
            "created_at": teacher.created_at.isoformat(),
            "id": teacher.id,
            "updated_at": teacher.updated_at.isoformat(),
            "user_id": teacher.user_id,
        }
        for teacher in teachers
    ]

    return jsonify({"data": teachers_data})

@principal_blueprint.route('/assignments/grade', methods=['POST'])
@validate_principal
def grade_assignment():
    principal_id = request.headers.get('X-Principal')['principal_id']
    data = request.get_json()

    assignment_id = data.get('id')
    grade = data.get('grade')

    # Fetch the assignment
    assignment = Assignment.query.get(assignment_id)

    # Ensure the assignment belongs to the principal
    if assignment.teacher_id != principal_id:
        return jsonify({"error": "Assignment does not belong to the principal"}), 403

    # Update assignment grade and state
    assignment.grade = grade
    assignment.state = 'GRADED'

    # Save changes to the database
    db.session.commit()

    # Convert the graded assignment to JSON format
    graded_assignment_data = {
        "content": assignment.content,
        "created_at": assignment.created_at.isoformat(),
        "grade": assignment.grade,
        "id": assignment.id,
        "state": assignment.state,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id,
        "updated_at": assignment.updated_at.isoformat(),
    }

    return jsonify({"data": graded_assignment_data})
