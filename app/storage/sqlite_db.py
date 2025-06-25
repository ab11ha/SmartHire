import sqlite3

class SQLiteDB:
    def __init__(self, db_path="smart_hire.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                location TEXT,
                experience TEXT,
                skills TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applicants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                resume_text TEXT
            )
        ''')
        self.conn.commit()

    def insert_job(self, job_meta):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO jobs (title, location, experience, skills)
            VALUES (?, ?, ?, ?)
        ''', (
            job_meta['title'],
            job_meta['location'],
            job_meta['experience'],
            ','.join(job_meta['skills'])
        ))
        self.conn.commit()
        return cursor.lastrowid

    def insert_applicant(self, applicant_meta):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO applicants (name, email, resume_text)
            VALUES (?, ?, ?)
        ''', (
            applicant_meta['name'],
            applicant_meta['email'],
            applicant_meta['resume_text']
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_job_by_id(self, job_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id=?', (job_id,))
        row = cursor.fetchone()
        if not row: return None
        return {
            'title': row[1], 'location': row[2],
            'experience': row[3], 'skills': row[4].split(',')
        }

    def get_applicant_by_id(self, applicant_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM applicants WHERE id=?', (applicant_id,))
        row = cursor.fetchone()
        if not row: return None
        return {
            'name': row[1], 'email': row[2], 'resume_text': row[3]
        }
