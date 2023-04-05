### PIIDM APIs

### Mysql dependency for ubuntu
`apt-get install python3-dev default-libmysqlclient-dev build-essential`

### Python virtual env
`apt install python3.10-venv`
`python3 -m venv .venv`

### DB Setup
```
export FLASK=app.py
`pip install -r requirements.txt`
flask db init
flask db migrate -m "create tables"
flask db upgrade
```

### Run
`gunicorn -b 127.0.0.1:3002 -w 4 --worker-class gevent app:app --log-level debug --limit-request-line 8000`


### Entry records to setup application
`./login_first_time.sh`
`sed -i -e  's/<TOKEN>/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770/g' ./first_time.sh`
`./first_time.sh`
--- backup file ./first_time_bkp.sh

### Apache2
`sudo systemctl status apache2`

### Replace with domain IP
`find ./ -type f -exec sed -i -e  's/127.0.0.1/142.93.208.220/g' {} \;`
`find ./ -type f -exec sed -i -e  's/127.0.0.1/64.227.150.234/g' {} \;`


### Country List
`https://gist.github.com/anubhavshrimal/75f6183458db8c453306f93521e93d37#file-countrycodes-json`


### Run mysql
`brew services restart mysql`
`mysql -u root -p root12345`
`SHOW VARIABLES LIKE 'validate_password%';` --> workaround for password error
`SET GLOBAL validate_password.policy=LOW;` --> workaround for password error
`CREATE USER 'piidm_online'@'localhost' IDENTIFIED WITH mysql_native_password BY 'piidm_online_password123';`
`GRANT ALL PRIVILEGES ON * . * TO 'piidm_online'@'localhost';`

`mysql -u piidm_online -p piidm_online_password123`
`Create database piidm_online;`
`use piidm_online;`
`drop database piidm_online;`

`select * from `lead` where phone_num LIKE '+91-+91%';`
`update `lead` set phone_num = REPLACE(phone_num, '+91-+91', '+91-') where phone_num LIKE '+91-+91%';`

`select phone_num from `lead` where phone_num NOT LIKE '+91%';`
`update `lead` set phone_num = '+91-' || phone_num where phone_num NOT LIKE '+91%';`
`update `lead` set phone_num = CONCAT('+91-', phone_num) where phone_num NOT LIKE '+91%';`

`select alternate_phone_num from `lead` where alternate_phone_num != '' and alternate_phone_num NOT LIKE '+91%';`
`update `lead` set alternate_phone_num = CONCAT('+91-', alternate_phone_num) where `lead` where alternate_phone_num != '' and alternate_phone_num NOT LIKE '+91%';`

`select phone_num from `lead` where phone_num LIKE '+91- %';`
`update `lead` set phone_num = REPLACE(phone_num, ' ', '') where phone_num LIKE '+91- %';`

`select * from `lead` where phone_num = '+91- 99602 18121'`;
`update `lead` set phone_num = '+91-9960218121' where phone_num = '+91- 99602 18121'`;

`select lead_id, SUBSTRING(phone_num, 1, 14) as alt, name, phone_num from `lead` where length(phone_num) > 14 and phone_num NOT LIKE "%deleted%";`
`update `lead` set phone_num = SUBSTRING(phone_num, 1, 14) where length(phone_num) > 14 and phone_num NOT LIKE "%deleted%";`

`select lead_id, SUBSTRING(alternate_phone_num, 1, 14) as alt, name, alternate_phone_num from `lead`  where length(alternate_phone_num) > 14 and alternate_phone_num NOT LIKE "%deleted%";`
`update `lead` set alternate_phone_num = SUBSTRING(alternate_phone_num, 1, 14) where length(alternate_phone_num) > 14 and alternate_phone_num NOT LIKE "%deleted%";`

`SELECT SUBSTRING_INDEX(phone_num, '/', 1) from `lead` where phone_num LIKE '%/%';`
`update `lead` set phone_num = SUBSTRING_INDEX(phone_num, '/', 1) where phone_num LIKE '%/%';`

**`select lead_id, name, lead_date, phone_num from `lead` where phone_num LIKE '+91-%-%';`
**`update `lead` set phone_num=REGEXP_REPLACE(phone_num, '-', '', 4, 2) where phone_num LIKE '+91-%-%';`

`select lead_id, phone_num, name from `lead` where length(phone_num) > 14 and phone_num NOT LIKE "%deleted%";`

`select lead_id, phone_num, name from `lead` where phone_num LIKE '% %' and phone_num NOT LIKE "%deleted%";`
`update `lead` set phone_num = REPLACE(phone_num, ' ', '') where phone_num LIKE '% %' and phone_num NOT LIKE "%deleted%";`

`select * from student where phone_num NOT LIKE '+91%';`
`update student set phone_num = CONCAT('+91-', phone_num) where phone_num NOT LIKE '+91%';`

`select alternate_phone_num from student where alternate_phone_num NOT LIKE '+91%';`
`update student set alternate_phone_num = '+91-' || alternate_phone_num where alternate_phone_num NOT LIKE '+91%';`
`update student set alternate_phone_num = CONCAT('+91-', alternate_phone_num) where alternate_phone_num NOT LIKE '+91%';`

`select * from user where phone_num NOT LIKE '+91%';`
`update user set phone_num = CONCAT('+91-', phone_num) where phone_num NOT LIKE '+91%';`

`select * from student where phone_num LIKE '+91 %';`
`update student set phone_num = REPLACE(phone_num, '+91 ', '+91-') where phone_num LIKE '+91 %';`

`select * from user where phone_num LIKE '+91 %';`
`update user set phone_num = REPLACE(phone_num, '+91 ', '+91-') where phone_num LIKE '+91 %';`


### Migrate DB steps:
- Drop database.
- Create database.
- Run export app.py and flask upgrade
- Run login sh file
- Replace token placeholder with actual token.
- Run first_time.sh file
- Run migrate_to_new_db.py file
- Exceute above update commands


### Data Tables:
```commandline
    table = $('#example').DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            dataSrc: "",
            url: "api/leads/select-paginate-advanced?start=0&length=2&draw=2",
            type: "GET"
        },
        columns: [
            { data: "name" },
            { data: "email" },
            .
            .
            .
            { data: "lead_date" }
        ]
    });
```


# Server Setup one-time:
#### Python 3.10
`sudo apt update && sudo apt upgrade -y`
`sudo apt install software-properties-common -y`
`sudo add-apt-repository ppa:deadsnakes/ppa`
`sudo apt install python3.10`

#### Mysql
`sudo apt update`
`sudo apt install mysql-server`
`sudo systemctl start mysql.service`

### Apache
`apt install apache2`
`systemctl status apache2`


### For SSL
https://app.zerossl.com/dashboard
piidmindia@gmail.com
Test1234

#### For Gunicorn
```commandline
Domain name = IP address
/var/www/html/certs
/root/codemania/piidm-backend/.venv/bin/python3 /root/codemania/piidm-backend/.venv/bin/gunicorn -b 0.0.0.0:3002 -w 4 --worker-class gevent app:app --log-level debug --limit-request-line 8000 --certfile=/var/www/html/certs/certificate.crt --keyfile=/var/www/html/certs/private.key
```

#### For UI
```commandline
Domain name = online.piidm.com
/var/www/online.piidm.com/certs
vim /etc/apache2/sites-available/online.piidm.com.conf 
```


#### Cron jobs
`0 1 * * * /root/codemania/piidm-backend/.venv/bin/python /root/codemania/piidm-backend/jobs/deactivate_students.py >> /root/codemania/piidm-backend/cronjob_log.out`