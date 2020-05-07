import os, base64

class SessionStore:

    def __init__(self):
        self.sessions = {}
        return

    def generateSessionId(self):
        rnum = os.urandom(32) #creates random data from the OS. the 32 is bytes.
        rstr = base64.b64encode(rnum).decode("utf-8") #base64 creates a binary string, the decodes it to a normal string
        return rstr
        
    def createSession(self):
        sessionId = self.generateSessionId()
        print( "Generated new session with ID: ", sessionId )
        self.sessions[sessionId] = {}
        return sessionId


    def getSessionData(self, sessionId):
        if sessionId in self.sessions:
            print("recognized previous session id, returning data about that session")
            return self.sessions[sessionId]
        else:
            #bad sessionID
            return None

    # def addSessionData(self, sessionId, userId):
    #     print("got to addSessionData")
    #     if sessionId in self.sessions:
    #         self.sessions[sessionId]["userId"] = userId
    #         print(self.sessions)
    #     return