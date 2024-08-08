Steps to Installation:

https://github.com/BoianaRajaRamesh/AccuknoxTask.git
pip install -r requirements.txt
Create a MySQL database, then update the database details in the manage.py file in the root folder with the new database name, username, and password.
python manage.py migrate
python manage.py runserver

//******\*\*\*\*******\*\*******\*\*\*\*******\*\*******\*\*\*\*******\*\*******\*\*\*\*******//

API Endpoints:

User Signup and Login
POST /api/users/signup/: Create a new user account.
POST /api/users/login/: Authenticate a user and obtain an access token.

User Search:
GET /api/users/search/: Search for users by email or name.

Friend Requests:
POST /api/friends/request/: Send a friend request.
PUT /api/friends/request/{id}/: Accept or reject a friend request.
GET /api/friends/list/: List all friends.
GET /api/friends/pending/: List pending friend requests.
