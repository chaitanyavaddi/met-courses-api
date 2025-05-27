from fastapi import FastAPI, Request
 
import json
import sqlite3
 
 
def connect_db():
    conn = sqlite3.connect("users.db")
    return conn
 
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



#POST - /courses - name, duration, author
#GET - /courses - Get All courses from DB
#DELETE - /courses/{id} - Delete the course
#PATCH - /courses/{id} - Update the course details
    