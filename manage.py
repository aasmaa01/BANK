from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask.cli import AppGroup

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.cli.command("run")
def run():
    app.run(debug=True)
