# Importing SQLite module for database operations
import sqlite3
# Importing the database path/config from config.py
from config import DATABASE

# Defining default skills and statuses as lists of tuples
skills = [(_,) for _ in ['Python', 'SQL', 'API', 'Discord']]
statuses = [(_,) for _ in ['Prototyping', 'In Development', 'Completed', 'Updated', 'Abandoned/Not supported']]

# Class to manage all DB operations
class DB_Manager:
    def __init__(self, database):
        self.database = database  # Store database path

    # Method to create all necessary tables
    def create_tables(self):
        conn = sqlite3.connect(self.database)  # Connect to the database
        with conn:
            # Create 'projects' table
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                                project_id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                project_name TEXT NOT NULL,
                                description TEXT,
                                url TEXT,
                                status_id INTEGER,
                                FOREIGN KEY(status_id) REFERENCES status(status_id)
                            )''')
            # Create 'skills' table
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                                skill_id INTEGER PRIMARY KEY,
                                skill_name TEXT UNIQUE
                            )''')
            # Create 'project_skills' table (many-to-many relation)
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                                project_id INTEGER,
                                skill_id INTEGER,
                                FOREIGN KEY(project_id) REFERENCES projects(project_id),
                                FOREIGN KEY(skill_id) REFERENCES skills(skill_id)
                            )''')
            # Create 'status' table
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                                status_id INTEGER PRIMARY KEY,
                                status_name TEXT UNIQUE
                            )''')
            conn.commit()  # Save changes
        print("Database created successfully")

    # Private method to execute many INSERT-like queries
    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    # Private method to fetch data from DB
    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    # Public accessor to __select_data
    def select_data(self, sql, data=tuple()):
        return self.__select_data(sql, data)

    # Insert default skills and statuses (only if they don't already exist)
    def default_insert(self):
        self.__executemany('INSERT OR IGNORE INTO skills (skill_name) VALUES (?)', skills)
        self.__executemany('INSERT OR IGNORE INTO status (status_name) VALUES (?)', statuses)

    # Insert a new project (or ignore if duplicate)
    def insert_project(self, data):
        sql = 'INSERT OR IGNORE INTO projects (user_id, project_name, url, status_id) VALUES (?, ?, ?, ?)'
        self.__executemany(sql, data)

    # Insert a skill for a project
    def insert_skill(self, user_id, project_name, skill):
        # Get the project ID using project name and user ID
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        # Get skill ID by skill name
        skill_id = self.__select_data('SELECT skill_id FROM skills WHERE skill_name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        # Insert relationship into project_skills
        sql = 'INSERT OR IGNORE INTO project_skills VALUES (?, ?)'
        self.__executemany(sql, data)

    # Get all statuses as a list
    def get_statuses(self):
        return self.__select_data('SELECT status_name FROM status')

    # Get a status ID from a status name
    def get_status_id(self, status_name):
        res = self.__select_data('SELECT status_id FROM status WHERE status_name = ?', (status_name,))
        return res[0][0] if res else None

    # Get all projects by user ID
    def get_projects(self, user_id):
        return self.__select_data('SELECT * FROM projects WHERE user_id = ?', (user_id,))

    # Get the project ID using project name and user ID
    def get_project_id(self, project_name, user_id):
        return self.__select_data(
            'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', (project_name, user_id))[0][0]

    # Get all skills from the DB
    def get_skills(self):
        return self.__select_data('SELECT * FROM skills')

    # Get the list of skills used in a project
    def get_project_skills(self, project_name):
        res = self.__select_data('''SELECT skill_name FROM projects 
                                    JOIN project_skills ON projects.project_id = project_skills.project_id 
                                    JOIN skills ON skills.skill_id = project_skills.skill_id 
                                    WHERE project_name = ?''', (project_name,))
        return ', '.join([x[0] for x in res])

    # Get detailed info about a project
    def get_project_info(self, user_id, project_name):
        sql = '''SELECT project_name, description, url, status_name FROM projects 
                 JOIN status ON status.status_id = projects.status_id 
                 WHERE project_name = ? AND user_id = ?'''
        return self.__select_data(sql, (project_name, user_id))

    # Update a field (e.g., project_name) in a project
    def update_projects(self, param, data):
        self.__executemany(
            f"UPDATE projects SET {param} = ? WHERE project_name = ? AND user_id = ?", [data])

    # Delete a project by user_id and project_id
    def delete_project(self, user_id, project_id):
        sql = "DELETE FROM projects WHERE user_id = ? AND project_id = ?"
        self.__executemany(sql, [(user_id, project_id)])

    # Delete a skill from a specific project
    def delete_skill(self, project_id, skill_id):
        sql = "DELETE FROM project_skills WHERE skill_id = ? AND project_id = ?"
        self.__executemany(sql, [(skill_id, project_id)])


# === TESTING SECTION ===
if __name__ == '__main__':
    manager = DB_Manager(DATABASE)  # Create DB_Manager instance

    # Step 1: Create tables and insert default data
    manager.create_tables()
    manager.default_insert()

    # Step 2: Add a new project to the database
    user_id = 1
    project_name = "Aplikasi Discord Bot"
    project_url = "https://github.com/user/discord-bot"
    status_id = manager.get_status_id("In Development")
    manager.insert_project([(user_id, project_name, project_url, status_id)])

    # Step 3: Assign skills to the project
    manager.insert_skill(user_id, project_name, "Python")
    manager.insert_skill(user_id, project_name, "Discord")

    # Step 4: Print all status names
    print("\nStatus List:")
    for status in manager.get_statuses():
        print("-", status[0])

    # Step 5: Print all skill names
    print("\nSkill List:")
    for skill in manager.get_skills():
        print("-", skill[1])

    # Step 6: Print all projects of the user
    print("\nProjects for user 1:")
    for project in manager.get_projects(user_id):
        print(project)

    # Step 7: Print detailed info about the specific project
    print("\nProject Info:")
    print(manager.get_project_info(user_id, project_name))

    # Step 8: Print the skills used in the project
    print("\nProject Skills:")
    print(manager.get_project_skills(project_name))

    # --- The following steps are commented out for testing later ---
    # # Step 9: Update the project's name
    # new_project_name = "Discord Automation Bot"
    # manager.update_projects("project_name", (new_project_name, project_name, user_id))
    # print("\nAfter Project Name Update:")
    # print(manager.get_project_info(user_id, new_project_name))

    # # Step 10: Remove a specific skill from the project
    # project_id = manager.get_project_id(new_project_name, user_id)
    # skill_id = manager.select_data("SELECT skill_id FROM skills WHERE skill_name = 'Discord'")[0][0]
    # manager.delete_skill(project_id, skill_id)
    # print("\nAfter Deleting 'Discord' Skill:")
    # print(manager.get_project_skills(new_project_name))

    # # Step 11: Delete the project
    # manager.delete_project(user_id, project_id)
    # print("\nAfter Deleting Project:")
    # print(manager.get_projects(user_id))
