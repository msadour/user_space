# user_space


## This project

user_space is an API that allows MFA and account deletion.


## Tech/framework

* Framework: ``FastAPI``
* Database: ``postgres`` 
* Containerization ```Docker```
* Testing ```pytest```

## Installation

```
$ git clone https://github.com/msadour/user_space

$ cd user_space

$ docker-compose build && docker-compose up

```

## Run tests (before launch docker-compose as mentioned above)

* docker ps 
* docker exec -it <user_space_api_container_id> bash
* pytest

## Utilisation (Postman or any software that can perform API call)

### Registration

* url : http://0.0.0.0:8000/api/registration
* method : POST
* Payload : {
    "email": "valid-email",
    "phone_number": "valid-number",
    "password": "password"
}

### Verify e-mail (One Time Password link)

* url : the link provided in your email box (it will be probably another link where you have to click in order to get the right link (Sendgrid link))
* method : GET


### Refresh the link validation

* url : http://0.0.0.0:8000/api/refresh-otp
* method : POST
* Payload : {
    "email": "your-email",
    "password": "password"
}


### Supply password

* url : http://0.0.0.0:8000/api/supply-password
* method : POST
* Payload : {
    "password": "password",
    "password_again": "password"
}
  

### Authentication with email/password

* url : http://0.0.0.0:8000/api/auth
* method : POST
* Payload : {
    "email": "your-email",
    "password": "password"
}
  
### Authentication with SMS code

First you have to send a sms in order to receive your code authentication

* url : http://0.0.0.0:8000/api/send-sms
* method : POST
* Payload : {
    "phone": "your-phone-number"
}
  
Then send this code

* url : http://0.0.0.0:8000/api/auth-sms
* method : POST
* Payload : {
    "phone": "your-phone-number",
    "code": "code-received"
}
  

### Delete profile

* url : http://0.0.0.0:8000/api/delete_account
* method : DELETE
* Payload : {
    "email": "your-email",
    "password": "password"
}