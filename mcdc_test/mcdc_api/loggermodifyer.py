import os
from flask_restful import Resource, abort

class LoggerDeletionInteraction(Resource):
    def get(self):
        try:
            with open("app.log", 'r') as file:
                log_content = file.read()
                return log_content
        except FileNotFoundError:
            return "Log file not found."
        except Exception as e:
            return f"Error reading log file: {str(e)}" 
        
    def delete(self):
        try:
            os.remove("app.log")
            return {"message": "File deleted successfully."}, 200
        except FileNotFoundError:
            abort(404, message=f"File \"app.log\" not found.")
        except Exception as e:
            abort(500, message=f"Failed to delete file \"app.log\". Error: {str(e)}")