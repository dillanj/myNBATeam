import os
import psycopg2
import psycopg2.extras
import urllib.parse

#diff between fetchone() & fetchall()

class USERDB:

    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):  # destructor
        # DONT FORGET TO DISCONNECT
        self.connection.close()


    def createTables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), password VARCHAR(255), team_id INTEGER)")
        self.connection.commit()

    def addUser(self, name, email, password ):
        # no need for semicolons in the python file
        # question marks are formatting placeholders. ALWAYS inject your data binding (data sanitization)
        sql = "INSERT INTO users ( name, email, password ) VALUES ( %s, %s, %s )"
        # cursor.execute is almost always what we will use to interact with the database
        self.cursor.execute(sql, [name, email, password])
        self.connection.commit()  # applies the changes

    def getUserPassword(self, email):
        sql = "SELECT password FROM users WHERE email = %s"
        self.cursor.execute(sql, [email])
        return self.cursor.fetchone()

    def getUserByEmail(self, email):
        sql = "SELECT * FROM users WHERE email = %s"
        self.cursor.execute( sql, [email])
        return self.cursor.fetchone()

    # def getUserById(self, id ):
    #     sql = "SELECT * FROM users WHERE id = %s"
    #     self.cursor.execute( sql, [id])
    #     return self.cursor.fetchone()