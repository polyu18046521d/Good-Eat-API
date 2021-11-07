# Good-Eat-API
It is a RESTful API service for the food ordering service. Clients can choose their favorite restaurant to order the food and the restaurant owners can update their menu with this service.

# Microservice Architecture

There are mainly 8 services for the project, namely, Restaurant service, Store service, Menu service, Tracking service, Order service, Delivery service, Authentication service, and Centralized logging service.

![Microservice Architecture](https://user-images.githubusercontent.com/93090281/139533871-d641e0d2-a6ff-4482-b3bc-8b60e4734d98.png)

The service in green means it is completed the basic requirement and contain the basic fields. Service in red color means it is in development. The service in yellow means the data is hardcoded and will move to real database afterward. **(Latest Update: 2021/10/30)**

> ### **API Gateway**
> It is implemented with nginx as reverse proxy and force the client to do authentication before using any services.

> ### **Authentication**
> It stores the username and password of users. It will generate the JSON Web Token (JWT) for the valid logins. All the requests via API Gateway (except /login) require valid Bearer Token in the request header.

> ### **Store**
> It is responsible for storing the restaurant basic information, for example, store_id and store_name.

> ### **Menu**
> It is responsible for storing the menu of the restaurant. For example, menu_id, 
menu_name, and price. It also adopts the CQRS pattern, the PUT/PATCH/POST or updated related event will all be handled in the menu-write-service. The query is handled by the menu-read-service and will eventually be consistent with the write-service database.

> ### **Restaurant**
> It is a service for checking the restaurant information, menu, and the restaurant status (OFFLINE, ONLINE). It stores the status of restaurants only. It will send the menu-update event via the event bus to the Menu service.

> ### **Order**
> It is a service for storing the order information by the client. All the ordering request will be handled by this service, but not responsible for the order status (like accepted/canceled by the restaurant).

> ### **Delivery**
> It is a microservice for the delivery service. It will show the delivery status of the order (ON_THE_WAY, ARRIVED, PENDING)

> ### **Tracking**
> It is responsible for tracking the order status (like accepted/canceled by the restaurant).

> ### **Centralized logging**
> It collects the logs of the various microservices. 

# Current Available Endpoints
The microservices is still in developement, but there are few endpoints that are available:
### **API Gateway (listen port 80)**
  Login service
  - POST /login 
    > to get the JWT Bearer Token
    ```sh
    curl -H "Content-Type: application/json" \
      --request POST \
      -d '{ "username": <username>, "password": <password> }' \
      http://localhost:15000/takes/11111
    ```
    _Currently there is only one user available (username: test, password: test)_

  Restaurant service
  - GET /eats/\<store_id\> 
    > to get the restaurant information which include `store_name`, and `menus`
    ```sh
    curl localhost/eats/00001
    ```

  - POST /eats/\<store_id\>/menu
    > to update the restaurant menus
    ```sh
    curl -H "Content-Type: application/json" \
      --request POST \
      -d '{"course_id": "COMP55555"}' \
      http://localhost:15000/takes/11111
    ```
  
  Order service
  - GET /eats/order/<order_id>
    > to get the order inforamtion
    ```sh
    curl localhost/order/000011
    ```
  - POST /eats/order/
    > to create a new order

<!-- ### **Menu Service**
  - GET /<store_id>
    > to get all the menus of a store
  - POST /<store_id>
    > to append a menu to the store menu

### **Restaurant**
  - GET /<store_id>
    > to get all the information of a restaruant
  - POST /<store_id>/status
    > to udpate the store's status (OFFLINE, ONLINE)
  - POST /<store_id>/menu
    > to append a menu to the store menu

### **Store Service**
  - GET /
    > to get all store's information
  - GET /<store_id>
    > to get the information of a store

### **Tracking Service**
  - POST /
    > to create a new order
  - GET /<order_id>
    > to get a order with status (PENDING/ACCPETD/CANCELED)

### **Order Service**
  - GET /<order_id>
    > to get a order -->

## Implementation
- Event queue - RabbitMQ
- API Gateway - NGNIX
- Database - MongoDB
- API Service - Flask

- Logging - Elasticsearch, Logstash/Filebeat, Kibana
- Monitoring - Prometheus, Grafana

- Testing - pytest

## Trello
Invitation Link: https://trello.com/invite/b/Eey3fmel/8219e2c7116c431b7f69db5ebd9b09fd/tasks