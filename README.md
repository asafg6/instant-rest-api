
# Instance Rest API

Just add water! ...emm classes :)  
This is an instant-rest-api written in python 3 using [falcon](http://falcon.readthedocs.io/en/stable/index.html).


## What is it good for?

Mainly for client development, demos, examples, testing, etc...
Any situation when you need to bring up a server real quick.
In case it's not obvious to you - **Do not use this for production**

## How to use?

1. clone this repository
2. make a virtualenv (optional)
3. pip install -r dependencies.txt
4. open user_models.py and follow the example
5. run the server with: $ python main.py

A route will be created for each of the classes you added on user_models.py
For example:
If you created a ```class Car(InstantModel)```
a route '/car' will be created

POST   http://localhost:8000/car - (with json body) will create a car and return it's id
PUT    http://localhost:8000/car?id=1 - (with json body) will update the car that has an id of 1
DELETE http://localhost:8000/car?id=1 - will delete car that has id of 1
You can also use delete like this:
DELETE http://localhost:8000/car?id=1,2,3
GET    http://localhost:8000/car?id=1 - would car with id 1
GET    http://localhost:8000/car - would get all cars
GET    http://localhost:8000/car?limit=10&offset=10 - would get all cars with limit and offset of 10
GET    http://localhost:8000/car?color=red - would get all cars that has a color property and is equal to red
GET    http://localhost:8000/car?color=!red - would get all cars that has a color property and is not equal to red



## Configuration

you can override the host and port in config.py


