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
ENV SECRET_KEY=123456

CMD ["sh", "-c", "python3 auth.py --db=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}/${MYSQL_DB} --secret_key=${SECRET_KEY}"]

EXPOSE 60000