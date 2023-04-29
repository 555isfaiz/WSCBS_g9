FROM python:3.11.3

WORKDIR /Users/pawbud/Desktop/code/WSCBS_g9/assignment_3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV MYSQL_HOST=db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=example
ENV MYSQL_DB=mydatabase

CMD ["flask", "run", "--host=0.0.0.0"]

EXPOSE 5000
