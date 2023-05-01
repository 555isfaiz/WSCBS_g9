FROM python:3.11.3

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV MYSQL_HOST=db
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=example
ENV MYSQL_DB=mydatabase

ENTRYPOINT [ "python3", "app.py" ]
CMD ["--db"]

EXPOSE 53333
