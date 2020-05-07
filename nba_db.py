import os
import psycopg2
import psycopg2.extras
import urllib.parse


class NBADB:

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

    def __del__(self): #destructor
        # DONT FORGET TO DISCONNECT
        self.connection.close()


    def createTables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS players (id SERIAL PRIMARY KEY, name VARCHAR(255), number INTEGER, rating INTEGER, position VARCHAR(3), team VARCHAR(255))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS myteam (id SERIAL PRIMARY KEY, name VARCHAR(255), number INTEGER, rating INTEGER, position VARCHAR(3), team VARCHAR(255), team_id INTEGER)")
        sql = ( "INSERT INTO players ( name, number, rating, position, team) VALUES (%s, %s, %s, %s, %s)")
        self.cursor.execute( sql, ["Rudy Gobert", "27", "89", "C", "Jazz"] )
        self.connection.commit()


    def addPlayerToMyTeam(self, name, number, rating, position, team, team_id):
        # no need for semicolons in the python file
        # question marks are formatting placeholders. ALWAYS inject your data binding (data sanitization)
        sql = "INSERT INTO myteam ( name, number, rating, position, team, team_id ) VALUES ( %s, %s, %s, %s, %s, %s)"
        # cursor.execute is almost always what we will use to interact with the database
        self.cursor.execute( sql , [name, number, rating, position, team, team_id] )
        self.connection.commit()  # applies the changes


    def deletePlayer(self, id):
        sql = "DELETE FROM myteam WHERE id = %s"
        self.cursor.execute( sql, [id] )
        self.connection.commit()

    def getPlayer(self, id):
        sql = "SELECT * FROM myteam WHERE id = %s"
        self.cursor.execute( sql, [id] )
        return self.cursor.fetchone()

    def checkTeamExists(self, team):
        sql = "SELECT * FROM myteam WHERE team_id = %s"
        self.cursor.execute( sql, [team])
        return self.cursor.fetchone()

    def getAllPlayers(self):
        self.cursor.execute("SELECT * FROM players ORDER BY rating DESC")  # use fetch on select and basically commit on everything else
        return self.cursor.fetchall()  # returns a list of tupals or an empty list if it is empty


    def getTeamRoster(self, team):
        print( "getTeamRoster teamname to get: " + team)
        sql = "SELECT * FROM players WHERE team = %s"
        self.cursor.execute( sql, [team] ) #id MUST be in a list
        return self.cursor.fetchall()

    def getMyTeamRoster(self, team_id ):
        sql = "SELECT * FROM myteam WHERE team_id = %s ORDER BY rating DESC"
        self.cursor.execute( sql, [team_id] )
        return self.cursor.fetchall()

    def getLatestPlayer(self):
        self.cursor.execute( "SELECT * FROM myteam WHERE id = (SELECT MAX(ID) FROM myteam)")
        return self.cursor.fetchall()

    def updateTeamName(self, name, team_id):
        sql = "UPDATE myteam SET team = %s WHERE team_id = %s"
        self.cursor.execute(sql, [name, team_id])
        self.connection.commit()




