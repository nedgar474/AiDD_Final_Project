# AI Contribution: Generated initial scaffold, verified by team.
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from campus_resource_hub.src.app import create_app

app = create_app('development')

if __name__ == '__main__':
    with app.app_context():
        from campus_resource_hub.src.extensions import db
        db.create_all()  # Create database tables for our data models
    app.run(debug=True)