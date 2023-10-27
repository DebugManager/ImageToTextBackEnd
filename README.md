# Getting Started with Django App

## Available Scripts

In the project directory, you can run:

### `pip install`
### `api:`
#### `Get:`
https://pdf-to-txt-back.onrender.com/v1/main/ - all CompanyDoc\
https://pdf-to-txt-back.onrender.com/v1/main/<id>/ - 1 CompanyDoc\
https://pdf-to-txt-back.onrender.com/v1/plan?type=Annual - for annual prices
https://pdf-to-txt-back.onrender.com/v1/users/ - get all users from db\
https://pdf-to-txt-back.onrender.com/v1/users/<id>/ - get 1 user from db
#### `Post:`  
https://pdf-to-txt-back.onrender.com/v1/main/  - create new\
https://pdf-to-txt-back.onrender.com/auth/token/login/ - log in and get token\
https://pdf-to-txt-back.onrender.com/auth/token/logout/ - log out\
https://pdf-to-txt-back.onrender.com/v1/auth/users/ - sign up (required username, password)\
https://pdf-to-txt-back.onrender.com/v1/auth/users/reset_password/ - reset password (required "email")\
https://pdf-to-txt-back.onrender.com/v1/users/reset_password_confirm/ - reset password confirm (required "uid", "token", "new_password")
#### `Put/Patch:`
https://pdf-to-txt-back.onrender.com/v1/main/{pk:id}/  - edit CompanyDoc\
https://pdf-to-txt-back.onrender.com/v1/choose-plan/1/ - for choosing plan
#### `Delete:`
https://pdf-to-txt-back.onrender.com/v1/main/{pk:id}/ - delete CompanyDoc\