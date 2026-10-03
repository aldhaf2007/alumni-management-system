import pymysql
try:
    connection = pymysql.connect(host='localhost', user='alumni_user', password='alumni_pass', database='alumni_db')
    print("Database connected successfully!")
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        print("Tables:")
        for row in cursor.fetchall():
            print(row[0])
            
        cursor.execute("SELECT * FROM profiles LIMIT 1;")
        
except Exception as e:
    print(f"Database error: {e}")
