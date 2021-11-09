# use the python slim image as the bottom layer
FROM python:slim 

#  set the working directory as /code
WORKDIR /code

# copy the content of current host folder to the guest /code folder
COPY . /code/

# install the python library from the list "requirements.txt"
RUN pip install -r requirements.txt

# set the environment variables
# ENV MONGO_USERNAME='comp3122'
# ENV MONGO_PASSWORD='12345'
# ENV MONGO_SERVER_HOST='menu-db' 
# ENV MONGO_SERVER_PORT='27017'

CMD python app.py