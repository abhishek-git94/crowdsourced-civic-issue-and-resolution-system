from mongoengine import connect

def init_db(app):
    db_uri = app.config.get('MONGODB_SETTINGS', {}).get('host')
    connect(host=db_uri)
