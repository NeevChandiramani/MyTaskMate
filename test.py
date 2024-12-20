import sqlite3

# Connect to the SQLite database (creates the database file if it doesn't exist)
connection = sqlite3.connect('test_database.db')

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create a table
cursor.execute('''
CREATE TABLE IF NOT EXISTS test_table (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
)
''')

# Insert sample data
cursor.execute('INSERT INTO test_table (name, age) VALUES (?, ?)', ('John Doe', 30))
cursor.execute('INSERT INTO test_table (name, age) VALUES (?, ?)', ('Jane Smith', 25))

# Commit the transaction to save changes
connection.commit()

# Query the table
cursor.execute('SELECT * FROM test_table')
rows = cursor.fetchall()

# Print the query results
print("Data in the table:")
for row in rows:
    print(row)

# Close the connection
connection.close()
