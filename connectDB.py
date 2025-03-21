import mariadb

# Database connection details
db_config = {
    "host": "database-1.ck100m4eavfj.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "MASTERPASSWORD1!",  # CHANGE THIS ASAP for security
    "database": "coding_platform",
    "port": 3306,
    "ssl_ca": "C:/Users/Rylan/Desktop/rds-ca.pem"  # Update this path to your SSL cert
}

try:
    # Connect to MariaDB using SSL
    connection = mariadb.connect(**db_config)
    cursor = connection.cursor()

    # Test query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Connected! Current time on DB server:", result[0])

    # Close connection
    cursor.close()
    connection.close()

except mariadb.Error as err:
    print(f"Error Code: {err.errno}")
    print(f"Error Message: {err.msg}")
