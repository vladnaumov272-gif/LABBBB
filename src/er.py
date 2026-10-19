import sqlite3
conn = sqlite3.connect('lib.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('judge', 'participant'))
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Participants (
    participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Competitions (
    competition_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date DATE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER,
    competition_id INTEGER,
    result REAL,
    FOREIGN KEY (participant_id) REFERENCES Participants(participant_id),
    FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id)
)
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Rankings (
    ranking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER,
    participant_id INTEGER,
    position INTEGER,
    FOREIGN KEY (competition_id) REFERENCES Competitions(competition_id),
    FOREIGN KEY (participant_id) REFERENCES Participants(participant_id)
)
''')
cursor.execute("INSERT INTO Participants VALUES(1,1,'Ivan Ivanov',01.01.2000)")
cursor.execute("INSERT INTO Results VALUES(1,1,1,1000)")
cursor.execute("SELECT * FROM Participants")
print(cursor.fetchall())
conn.commit()
conn.close()