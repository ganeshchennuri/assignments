from ma import ma
from models import Task

class TaskSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'done')
        ordered = True
    
task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)