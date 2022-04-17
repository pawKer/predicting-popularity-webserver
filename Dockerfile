FROM python:3.8
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD gunicorn --bind 0.0.0.0:$PORT server:app 

# docker build .
# heroku container:push web -a predicting-popularity
# heroku container:release web -a predicting-popularity