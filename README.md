# GojengaApi

## Utilizing fastApi to power Gojenga

### Architecture

User Type
name: str
password: str | None = None

*get user information* 
GET /user/{username}

*create user*
Post /user
body: { "name" : "USERNAME", "password" : "PASSWORD" }

*update user*
PUT /user/{username}
body: { "name" : "USERNAME", "password" : "PASSWORD" }

*delete user*
DELETE /user/{username}
