# Fastapi_auctioning_backend
This API primarily utilizes fasapi's websocket feature to create the effect of an auctioning app
# Before you Install!!
The api makes use of databases like sqlite and mariadb for basic CRUD operations. 
## Setting up with sqlite.
within the app module open the ```databse.py``` uncomment a section of code below:
```
#______________________________uncomment to use sqlite ________________________________
use this to test functionality of the database with sqlite

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
3306
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```
after that comment the portion of code for using a mariadb/mysql database.
```
SQLALCHEMY_DATABASE_URL = os.getenv('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
```
 Alternatively if you have a mysql database that you would like to test with, comment the sqlite portion and uncomment the portion below.
 Then, navigate to the ```.env``` file and add the database uri to the ```DB_URL``` portion of the file.
 I would highly recommend working with the sqlite version for demontration reasons because its much easier to set up.
```
SQLALCHEMY_DATABASE_URL = os.getenv('DB_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close
```


# Installation with venv

Create a virtual environment with venv using ***python version 3.12***.
```
python3 -m venv bidding_app
```

activate the virtual environment
``` source myenv/bin/activate ```

then, install the requirements.txt file 
```
 pip install requirements.txt 
```
run ``` uvicorn app:run``` and the server should start up alternatively you can run ``` python3 -m app.run``` and the server will start up 

# Installation with docker.
After you have chosen the preferred database to set the app with simply run
```
sudo docker build .
```
and the server will automatically start


# API Interaction Guide

This guide provides instructions on how to interact with the API endpoints using API clients like Postman. It covers account creation, login, and WebSocket interactions.

## Prerequisites

- Ensure you have [Postman](https://www.postman.com/downloads/) installed on your machine.
- The API server should be running.

REST API Endpoints
#### 1. Create Account
To create a new account, send a POST request to the /auth/register endpoint with the following JSON payload:

Endpoint: POST /auth/register

JSON Payload:
```bash
  {
    "username": "your_username",
    "first_name": "YourFirstName",
    "last_name": "YourLastName",
    "email": "your_email@example.com",
    "password": "your_password",
    "confirm_password": "your_password"
  }
```
### 2. Login
-To log in, send a POST request to the /auth/login endpoint with the following JSON payload:

Endpoint: POST /auth/login

Open Postman and create a new request.
Set the request type to POST.
Enter the URL: http://localhost:8000/auth/login.
Go to the "Body" tab and select "raw" and "JSON" from the dropdown.
Paste the JSON payload above into the body section.
Click "Send" to log in and receive an access token.

JSON Payload:
```bash
{
  "username": "your_username",
  "password": "your_password"
}
```
Example response:
```
{
  "access_token": "YOUR_JWT_TOKEN",
  "token_type": "bearer"
}
```

## Interacting with Websocket endpoints in the bidding app

***Important:***
You must include your JWT token in the WebSocket connection query parameters as ?token=YOUR_JWT_TOKEN.


### 1. Creating Rooms
WebSocket Endpoint:
ws://localhost:8000/ws/create_room?token=YOUR_JWT_TOKEN

In Postman (or another WebSocket client), create a new request and connect to the above URL.
Once connected, send the JSON message with your desired group_name, target_price, and item.
If successful, you’ll receive a response indicating the group was created along with an ID.

 Example JSON Message (to create a group):
```bash 
{
  "action": "create_group",
  "group_name": "Sample Group",
  "target_price": 100.0,
  "item": "Sample Item"
}
```
Response:
```bash
{
  "message": "Joined group successfully.",
  "id":a1b2c3d4-89ab-4ef0-1234-56789abcdef0
}
```
### 2. Closing Auctions

Still using the same WebSocket endpoint.
```
ws://localhost:8000/ws/create_room?token=YOUR_JWT_TOKEN
```
Use the id returned when the group was created.
Send the JSON message to close the group.
A confirmation message will be sent back if the close operation is successful.


Example JSON Message (to close a group):
```bash
{
  "action": "close_group",
  "group_name": "Sample Group",
  "id": "SOME_UUID"
}
```

### 3. Joining Rooms

WebSocket Endpoint for joining rooms and placing bids:
```
ws://localhost:8000/ws/bid_interface?token=YOUR_JWT_TOKEN
```
In Postman, set up a new WebSocket request to the given URL.
Click "Connect".
Send the JSON message with the specific group_name you want to join.
Observe the response, which should include a unique member ID indicating you have successfully joined.

Example JSON Message (to enter group)
```bash
{
  "action": "join_group",
  "group_name": "Sample Group"
}
```

### 4. Placing Bids
While connected to the ```ws://localhost:8000/ws/bid_interface?token=YOUR_JWT_TOKEN endpoint```
Obtain the id returned from the "join_group" response.
Send the JSON message with the bid, bidder_name, your id, and the group_name.

Example JSON Message (placing bids)
```bash
{
  "action": "place_bid",
  "bid": 150.0,
  "bidder_name": "John Doe",
  "id": "MEMBER_UUID",
  "group_name": "Sample Group"
}
```

To disconnect from a group, remain connected to 
```ws://localhost:8000/ws/bid_interface?token=YOUR_JWT_TOKEN```
Use the id obtained from the "join_group" response.
Send the JSON message. The server will respond to confirm that you have disconnected.

``` bash
{
  "action": "disconnect",
  "group_name": "Sample Group",
  "id": "MEMBER_UUID"
}
```


# Token Usage
• Always append your JWT token to the WebSocket URL as:
```
ws://localhost:8000/ws/<endpoint>?token=YOUR_JWT_TOKEN
```
• Replace YOUR_JWT_TOKEN with the token obtained from /auth/login.

### Troubleshooting Tips
Invalid token or no token:
If you attempt to connect to the WebSocket endpoint without a valid token, the server will reject the connection.
Incorrect action format:
Ensure the JSON payload matches the server’s expected structure. An invalid key or missed field will result in an error message or disconnection.
### Logs
Check the server logs for more details if you encounter issues.
By following these instructions and maintaining a valid token in your WebSocket URL, you can create rooms, join rooms, close bids, and exit groups in real time using Postman or any other WebSocket client.
