## Resource - My NBA Team
This program lets you select your dream NBA team from current (soon to be all) NBA players.

Each NBA Team consists of players with :
* Name
* Number
* Rating
* Position
* Current Team

## Resource - Users
The program allows for many users to create a fantasy team.
Each User has the following attributes:
* Full Name
* Email
* Password
**NOTE: Passwords are hashed using the bcrypt() hashing algorithm**

## Database Schema: 

Players Table Holds NBA Team Rosters with respect to the current NBA landscape.
* CREATE TABLE players ( 
        id INTEGER PRIMARY KEY,
        name TEXT,
        number INTEGER,
        rating INTEGER,
        position TEXT,
        team TEXT );

MyTeam table will hold all of the users' players that they want.
* CREATE TABLE myteam ( 
        id INTEGER PRIMARY KEY,
        name TEXT,
        number INTEGER,
        rating INTEGER,
        position TEXT,
        team TEXT
        team_id INTEGER );

Users table will hold all the information pertaining to a user.
* CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        password TEXT);

#### REST 
NAME | HTTP METHOD | PATH | DETAILS
-----|-------------|------|--------
Create | POST | /myteam | This Request happens when adding a player to the users team, or when creating a custom player from scratch.
List | GET | /players |  This Request will return a full list of the NBA players in the players table.
List | GET | /myteam | This Request will load all the players that have been added to the user's team. 
Retrieve | GET | /latestplayer | This Request will tell the server to load just the last person added to the users team. This is to be used with adding players to the users team, allowing a CSS effect to only apply the latest player added to the team.
Delete | DELETE | /myteam/id | This Request will delete the player from the users team with the unique id passed in.
Replace | PUT | /myteam/previousTeamName | This Request happens when the user updates the team name. It changes **all** players that had the previous team name value in their team row (which should be every one of them), in the myteam table.
Create | POST | /users | This request is invoked when creating a new user registers through the program.
Create | POST | /sessions | This request is invokedd when a user's credentials are being authorized. 
Delete | DELETE | /sessions | This request is invoked when a logged in user opts to sign out. The request will delete the user's id from the session store. 
# heroku
