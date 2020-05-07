from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json
from http import cookies
from passlib.hash import bcrypt
import sys

from session_store import SessionStore
from nba_db import NBADB
from users_db import USERDB

gSessionStore = SessionStore() # has to be global because the rest of the class will be loaded each time

#this class is used once per request

class MyRequestHandler(BaseHTTPRequestHandler):


    ################ COOKIES AND SESSIONS #######################

    def loadCookie(self):
        # loads the cookie that the client sent
        # always loads the cookie first, even if it isn't new; that way we can send it back to client in sendCookie
        if "Cookie" in self.headers:
            self.cookie = cookies.SimpleCookie( self.headers["Cookie"] )
        else:
            #if there isn't a cookie, create one
            self.cookie = cookies.SimpleCookie()
        return

    def sendCookie(self):
        #server send this for client to hand back next time
        for morsel in self.cookie.values():
            self.send_header( "Set-Cookie", morsel.OutputString() )
        return


    def loadSession(self):
        self.loadCookie()
        if "sessionId" in self.cookie:
            sessionId = self.cookie["sessionId"].value #retrieves the value at that key
            self.session = gSessionStore.getSessionData( sessionId )
            if self.session == None:
                # session Id no longer found in the session store (no longer remembers it)
                # in which case create a brand new session id
                sessionId = gSessionStore.createSession()
                self.session = gSessionStore.getSessionData( sessionId )
                self.cookie["sessionId"] = sessionId
        else:
            # no session Id found in the cookie
            # create a brand new session id.
            sessionId = gSessionStore.createSession()
            self.session = gSessionStore.getSessionData( sessionId )
            self.cookie["sessionId"] = sessionId
        return

    # def handleRetrieveUserId(self):
    #     self.send_response(200)
    #     # all headers go here:
    #     self.send_header("Content-type", "application/json")
    #     self.end_headers()
    #     userId = self.session["userId"]
    #     self.wfile.write(bytes(json.dumps(userId), "utf-8"))

    # def handleRetrieveUserName(self):
    #     db = USERDB()
    #     userId = self.session["userId"]
    #     name = db.getUserNameById( userId )
    #     self.send_response(200)
    #     self.send_header("Content-type", "application/json")
    #     self.end_headers()
    #     self.wfile.write(bytes(json.dumps(name), "utf-8"))

    def handleSignOut(self):
        print("got to handleSignOut()")
        del self.session["userId"]
        self.send_response(201)
        self.end_headers()






    ################ HANDLING USERS#############################
    def handleRegisterUser(self):
        # called by POST METHOD
        length = self.headers["Content-length"]  # tells the server how many bytes were sent
        body = self.rfile.read(int(length)).decode("utf-8")  # reading the entire chunk of data. the rfile gives us access to it. utf decoding translates it to a string
        print("the text body:", body)
        parsed_body = parse_qs(body)  # takes the body and makes it a dictionary of lists of values. hence the [0] below
        print("the parsed body:", parsed_body)

        name = parsed_body["fullName"][0]
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        #encrypt password here
        encrypted_password = bcrypt.hash(password)
        print( "Enc password: " + encrypted_password )

        # send these values to the DB
        db = USERDB()
        user = db.getUserByEmail( email )
        if user == None: # if user is none, the user hasn't registered with that email before
            db.addUser( name, email, encrypted_password )
            self.send_response(201)
            self.end_headers()
        else:
            #user already exists in database....
            self.send_response(422)
            self.end_headers()



    def handleAuthentication(self):
        # called by POST METHOD
        print( "got to authenication method")
        length = self.headers["Content-length"]
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        print("parsed body: " , parsed_body)

        # save the player to myTeam table
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]


        db = USERDB()
        user = db.getUserByEmail(email)
        if user == None:
            self.handle401()
        else:
            #cross-check given password
            saved_password = db.getUserPassword(email)
            saved_password = saved_password["password"]
            print("saved password", saved_password )

            if bcrypt.verify( password, saved_password ):
                print("Successfully logged in")
                # user is logged in, REMEMBER THE STATE. REMEMBER THE USER ID IN THE SESSION
                self.session["userId"] = user['id']
                self.send_response(201)
                # send the user info back to the client
                self.end_headers()
                self.wfile.write(bytes(json.dumps(user), "utf-8"))


            else:
                print("bcrypt.verify() is not working as thought ")
                self.handle401()


    def isLoggedIn(self):
        if "userId" in self.session:
            return True
        else:
            return False



    ################ HANDLING TEAMS/PLAYERS ####################


    def handleAllPlayers(self):
        #called by GET method
        # grabs all players in the players table, sorting them by rank in desc order
        #return 401 if not logged in!!
        if self.isLoggedIn():
            self.send_response(200)
            # all headers go here:
            self.send_header("Content-type", "application/json")
            self.end_headers()

            db = NBADB()  # create local instance of the database query so we reconnect everytime and aren't leaving connectins open
            roster = db.getAllPlayers()
            if roster == None:
                self.handleNotFound()
            else:
                self.wfile.write(bytes(json.dumps(roster), "utf-8"))
        else:
            self.handle401()

    def handleRosterRetrieve(self, id):
        # called by GET method
        #selects a specific player
        if self.isLoggedIn():
            db = NBADB()
            roster = db.getTeamRoster(id)
            if roster == None:
                self.handleNotFound()

            else:
                self.send_response(200)
                # all headers go here:
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(bytes(json.dumps(roster), "utf-8"))
        else:
            self.handle401()


    def handleAddPlayerToMyTeam(self):
        #called by POST METHOD
        if ( self.isLoggedIn() ):
            length = self.headers["Content-length"]  # tells the server how many bytes were sent
            body = self.rfile.read(int(length)).decode(
                "utf-8")  # reading the entire chunk of data. the rfile gives us access to it. utf decoding translates it to a string
            print("the text body:", body)
            parsed_body = parse_qs(body)  # takes the body and makes it a dictionary of lists of values. hence the [0] below
            print("the parsed body:", parsed_body)

            # save the player to myTeam table
            name = parsed_body["name"][0]
            number = parsed_body["number"][0]
            rating = parsed_body["rating"][0]
            position = parsed_body["position"][0]
            team = parsed_body["team"][0]
            team_id = self.session["userId"]
            # send these values to the DB, specifically the myTeam table!
            db = NBADB()
            db.addPlayerToMyTeam( name, number, rating, position, team, team_id )

            self.handle201()

        else:
            self.handle401()

    def handleMyTeamRoster(self, fullRoster ):
        #called by GET METHOD
        # IF fullroster-  grab all players in myTeam table, sorting them by rank in desc order
        # ELSE grabs just the last player added
        if self.isLoggedIn():
            userId = self.session["userId"]
            db = NBADB()  # create local instance of the database query so we reconnect everytime and aren't leaving connectins open
            if ( fullRoster ):
                myRoster = db.getMyTeamRoster( userId )
                if myRoster == None:
                    self.handleNotFound()
            else:
                myRoster = db.getLatestPlayer()
                if myRoster == None:
                    self.handleNotFound()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(myRoster), "utf-8"))
        else:
            self.handle401()


    def handleDeletePlayerFromMyTeam( self, id ):
        if self.isLoggedIn():
            db = NBADB()
            # check to see if the id already exists, if not handle not found.
            if id == None:
                self.handleNotFound()
            elif db.getPlayer(id) == None:
                self.handleNotFound()
            else:
                db.deletePlayer(id)
                self.send_response(200)
                # all headers go here:
                self.send_header("Content-type", "application/json")
                self.end_headers()
        else:
            self.handle401()

    def handleUpdateTeamName(self, team_id):
        if self.isLoggedIn():
            length = self.headers["Content-length"]  # tells the server how many bytes were sent
            body = self.rfile.read(int(length)).decode(
                "utf-8")  # reading the entire chunk of data. the rfile gives us access to it. utf decoding translates it to a string
            print("the text body:", body)
            parsed_body = parse_qs(body)  # takes the body and makes it a dictionary of lists of values. hence the [0] below
            print("the parsed body:", parsed_body)

            newTeamName = parsed_body["teamName"][0]
            print("new team name: " + newTeamName )


            db = NBADB()
            #check to see if that team exists
            if db.checkTeamExists( team_id ) == None:
                print("not recognizing this user having a team")
                self.handleNotFound()
            else:
                db.updateTeamName(newTeamName, team_id)
                self.send_response(201, "Created")
                # self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
        else:
            self.handle401()

    def handleNotFound(self):
        self.loadSession()
        self.send_response(404)
        # self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not Found", "utf-8"))

    def handle401(self):
        self.loadSession()
        self.send_response(401)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Not logged in.", "utf-8"))


    def handle201(self):
        self.loadSession()
        self.send_response(201)
        self.end_headers()



    #  RESTMETHODS  #

    def do_OPTIONS(self):
        #this is for preflighted requests
        self.loadSession()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-type")
        self.end_headers()


    def do_PUT(self):
        self.loadSession()
        parts = self.path.split('/')[1:]
        collection = parts[0]

        if collection == "myteam":
            userId = self.session["userId"]
            self.handleUpdateTeamName( userId )
        else:
            self.handleNotFound()



    def do_DELETE(self):
        self.loadSession()
        parts = self.path.split('/')[1:]
        collection = parts[0]
        print("in DELETE collection is:" + collection)

        if collection == 'sessions':
            print("collection in delete is :  " + collection )
            self.handleSignOut()

        if len(parts) > 1:
            id = parts[1]
            print(" in DELETE id is " + id )
            #id should be player id
            self.handleDeletePlayerFromMyTeam( id )
            if collection == '/myteam':
                if id == None:
                    self.handleNotFound()
                else:
                    self.handleDeletePlayerFromMyTeam(id)
        else:
            self.handleNotFound()




    def do_GET(self):
        self.loadSession()
        # parse the path to find the collection and identifier
        # ALWAYS CHECK THE PATH IN THE CORS METHODS (get, post, etc)
        parts = self.path.split('/')[1:]
        collection = parts[0]
        print("in GET, collection is:" + collection)

        if len(parts) > 1:
            id = parts[1]
            #id should be team name
        else:
            id = None

        if collection == "players":
            if id == None:
                #doesn't specify which team roster, load all players in players database
                self.handleAllPlayers()
            else:
                self.handleRosterRetrieve(id)
        elif collection == "myteam":
            self.handleMyTeamRoster( True )
        elif self.path == "/latestplayer":
            self.handleMyTeamRoster( False )
        # elif collection == "userid":
        #     self.handleRetrieveUserId()
        # elif collection == "username":
        #     self.handleRetrieveUserName()
        else:
            self.handleNotFound()


    def do_POST(self):
        self.loadSession()
        # inserting data into the database
        print(self.path)
        if self.path == "/myteam":
            self.handleAddPlayerToMyTeam()
        elif self.path == "/users":
            self.handleRegisterUser()
        elif self.path == "/sessions":
            self.handleAuthentication()
        else:
            self.handleNotFound()

    #overload end_headers to send a cookie everytime it is called
    def end_headers(self):
        self.sendCookie()
        #if you allow cookies, you cannot use * wildcard for allow origin
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        #now call the original end_headers method.
        BaseHTTPRequestHandler.end_headers(self)


def run():
    nba_db = NBADB()
    nba_db.createTables()
    nba_db = None
    user_db = USERDB()
    user_db.createTables()
    user_db = None
    

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever()

run()

#https://johnson3200.herokuapp.com/

