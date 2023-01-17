# GojengaApi

## Utilizing fastApi to power Gojenga

[![Gojenga](https://circleci.com/gh/drichards188/gojengaApi.svg?style=svg)](https://github.com/drichards188/gojengaApi)

### Architecture

User Type

name: str

password: str | None = None

### Test Flag

Headers:

**Is-Test: True**

_____

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
