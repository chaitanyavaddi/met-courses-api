from fastapi import FastAPI, Request
import json
import os

# JSON Database helper functions
def load_json_db():
    db_path = "db.json"  # Root level db.json
    try:
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                data = json.load(f)
                # If empty JSON {}, populate with default data
                if not data or len(data) == 0:
                    return get_default_data()
                return data
    except:
        pass
    
    # Default structure with sample users
    return get_default_data()

def get_default_data():
    return {
        "users": [
            {"id": 1, "username": "john_doe", "password": "password123"},
            {"id": 2, "username": "jane_smith", "password": "mypass456"},
            {"id": 3, "username": "admin", "password": "admin123"},
            {"id": 4, "username": "student1", "password": "study789"},
            {"id": 5, "username": "teacher", "password": "teach2024"}
        ],
        "courses": [
            {"id": 1, "name": "Python Basics", "author": "John Doe", "duration": "4 weeks", "user_id": 1},
            {"id": 2, "name": "Web Development", "author": "Jane Smith", "duration": "6 weeks", "user_id": 2},
            {"id": 3, "name": "Data Science", "author": "Admin User", "duration": "8 weeks", "user_id": 3},
            {"id": 4, "name": "Machine Learning", "author": "Teacher", "duration": "10 weeks", "user_id": 5}
        ],
        "next_user_id": 6,
        "next_course_id": 5
    }

def save_json_db(data):
    db_path = "db.json"  # Root level db.json
    try:
        with open(db_path, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

def connect_db():
    # Simulate SQLite connection but return JSON data
    class MockConnection:
        def __init__(self):
            self.data = load_json_db()
        
        def cursor(self):
            return MockCursor(self.data)
        
        def commit(self):
            save_json_db(self.data)
        
        def close(self):
            pass
    
    return MockConnection()

class MockCursor:
    def __init__(self, data):
        self.data = data
        self.results = []
        self.rowcount = 0
    
    def execute(self, query, params=()):
        query = query.strip().upper()
        
        if query.startswith("SELECT * FROM USERS"):
            self.results = [(user["id"], user["username"], user["password"]) 
                          for user in self.data["users"]]
        
        elif query.startswith("INSERT INTO USERS"):
            username, password = params
            new_user = {
                "id": self.data["next_user_id"],
                "username": username,
                "password": password
            }
            self.data["users"].append(new_user)
            self.data["next_user_id"] += 1
            self.results = []
        
        elif query.startswith("SELECT ID FROM USERS WHERE USERNAME"):
            username = params[0]
            for user in self.data["users"]:
                if user["username"] == username:
                    self.results = [(user["id"],)]
                    return
            self.results = []
        
        elif query.startswith("UPDATE USERS SET PASSWORD"):
            password, username = params
            for user in self.data["users"]:
                if user["username"] == username:
                    user["password"] = password
                    self.rowcount = 1
                    return
            self.rowcount = 0
        
        elif query.startswith("DELETE FROM USERS"):
            username, password = params
            for i, user in enumerate(self.data["users"]):
                if user["username"] == username and user["password"] == password:
                    # Also delete user's courses
                    user_id = user["id"]
                    self.data["courses"] = [c for c in self.data["courses"] if c["user_id"] != user_id]
                    del self.data["users"][i]
                    self.rowcount = 1
                    return
            self.rowcount = 0
        
        elif query.startswith("INSERT INTO COURSES"):
            name, author, duration, user_id = params
            new_course = {
                "id": self.data["next_course_id"],
                "name": name,
                "author": author,
                "duration": duration,
                "user_id": user_id
            }
            self.data["courses"].append(new_course)
            self.data["next_course_id"] += 1
            self.results = []
        
        elif query.startswith("SELECT * FROM COURSES WHERE USER_ID"):
            user_id = params[0]
            self.results = [(course["id"], course["name"], course["author"], course["duration"], course["user_id"])
                          for course in self.data["courses"] if course["user_id"] == user_id]
    
    def fetchall(self):
        return self.results
    
    def fetchone(self):
        return self.results[0] if self.results else None

app = FastAPI()

@app.get("/users")
def read_users():
    #1. get conn object
    conn = connect_db()

    #2. use cursor menthod
    cursor = conn.cursor()

    #3. use execute() and pass SQL as argument
    cursor.execute("SELECT * FROM users")

    #4. use fetchall() to get all records
    data = cursor.fetchall()

    conn.close()

    output = []

    for entry in data:
        output.append({
            "username": entry[1],
            "password": entry[2]
        })
    return data
 
@app.post("/signup")
def signup(username, password):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    conn.commit()
    
    data = cursor.fetchall()

    output = ["Signup successful"]

    for entry in data:
        output.append({
            "username": entry[1],
            "password": entry[2]
        })

    conn.close()

    return output
 
@app.post("/login/{username}/{password}")
def login(username,password):
    #1. get conn object
    conn = connect_db()

    #2. use cursor menthod
    cursor = conn.cursor()

    #3. use execute() and pass SQL as argument
    cursor.execute("SELECT * FROM users")

    #4. use fetchall() to get all records
    data = cursor.fetchall()

    for entry in data:
        if username == entry[1] and password == entry[2]:
            return "Login Successful"
    else:
        return "Login Failed"

    conn.close()
 
@app.patch("/update/{username}/{password}")
def update(username,password):
   conn = connect_db()

   cursor = conn.cursor()

   cursor.execute("UPDATE users SET password = ? where username=?", (password, username))
 
   conn.commit()

   conn.close()

   return "Successfully updated password"
   
@app.delete("/delete/{username}/{password}")
def delete(username,password):
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE username=? AND password=?", (username, password))   

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    if deleted:
        return "Deleted Successfully" 
    else:
        return "Unsuccessful"
    

@app.post("/courses")
def add_user_course(username,
                     name, 
                     author,
                     duration):
    
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    
    user = cursor.fetchone()

    user_id = user[0]

    cursor.execute("INSERT INTO courses (name, author, duration, user_id) VALUES (?, ?, ?, ?)", (name, author, duration, user_id))

    conn.commit()

    conn.close()

    return {"message": "Courses Created"}


@app.get("/user/courses")
def user_courses(username):
    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))

    user = cursor.fetchone()

    if not user:
        return "User doesn;t exist"

    user_id = user[0]

    cursor.execute("SELECT * FROM courses WHERE user_id = ?", (user_id,))

    rows = cursor.fetchall()

    conn.close()

    return rows