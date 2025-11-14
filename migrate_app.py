from flask import Flask
from flask_migrate import Migrate
from Jansuvidha.app import app
from Jansuvidha.models import Base
from Jansuvidha.database import engine

class FakeDB:
    def __init__(self, engine, metadata):
        self.engine = engine
        self.metadata = metadata

fake_db = FakeDB(engine, Base.metadata)

migrate = Migrate(app, fake_db)