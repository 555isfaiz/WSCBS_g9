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
ENV AUTH_IP=auth_ip
ENV IDGEN_IP=id_gen_ip

CMD ["sh", "-c", "python3 app.py --db=mysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}/${MYSQL_DB} --auth=http://${AUTH_IP}/authenticate --idgen=http://${IDGEN_IP}"]

EXPOSE 53333
