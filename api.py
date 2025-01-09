import cherrypy
import sqlite3
import json

class Record:
    def __init__(self):
        self.db_name = 'records.db'
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            conn.commit()

    def get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  
        return conn

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return {"message": "Welcome to the Records API. Use /create, /read, /update, and /delete to manage records."}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create(self, name):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO records (name) VALUES (?)', (name,))
            conn.commit()
            record_id = cursor.lastrowid
            return {'status': 'success', 'record': {'id': record_id, 'name': name}}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def read(self, record_id):
        record_id = int(record_id)
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM records WHERE id = ?', (record_id,))
            record = cursor.fetchone()
            if record:
                return {'status': 'success', 'record': dict(record)}
            else:
                return {'status': 'error', 'message': 'Record not found'}, 404

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def update(self, record_id, name):
        record_id = int(record_id)
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE records SET name = ? WHERE id = ?', (name, record_id))
            if cursor.rowcount == 0:
                return {'status': 'error', 'message': 'Record not found'}, 404
            conn.commit()
            return {'status': 'success', 'record': {'id': record_id, 'name': name}}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(self, record_id):
        record_id = int(record_id)
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
            if cursor.rowcount == 0:
                return {'status': 'error', 'message': 'Record not found'}, 404
            conn.commit()
            return {'status': 'success', 'message': 'Record deleted'}

if __name__ == '__main__':
    app = Record()
    cherrypy.tree.mount(app)
    cherrypy.config.update({'server.socket_host': '127.0.0.1',
                             'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()