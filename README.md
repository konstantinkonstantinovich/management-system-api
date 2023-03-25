# Company Management System
 Terms of reference for python in Mobidev. Goal to learn python and DRF.

## First run
- create `.env` file from `.env.example`
- create a virtual environment  `python3 -m venv venv`
- activate it `source venv/bin/activate`
- `docker-compose build .`
- `docker-compose up`

## Usage
 
#### To run server:
 ```docker
 docker-compose up
```
#### To stop server:
 ```docker
docker-compose stop
```
#### To run seeder:
```docker
docker-compose run --rm api python ./company_management_system_api/manage.py seed api --number=15
```
#### To run postgres shell: 
- ``docker-compose run --rm db``, then open new terminal and run:
     ```shell
  docker exec -it company_management_system_db_1 psql -U newuser -W postgres
  ```
#### To create django admin user run:
```docker
docker-compose run --rm api python ./company_management_system_api/manage.py create_admin
```