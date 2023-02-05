### PIIDM APIs

### Mysql dependency for ubuntu
`apt-get install default-libmysqlclient-dev`

### DB Setup
```
export FLASK=app.py
`pip install -r requirements.txt`
flask db init
flask db migrate -m "create tables"
flask db upgrade
```

### Entry records to setup application
`./login_first_time.sh`
`sed -i -e  's/<TOKEN>/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.AHMxv1ZyUSH21Iq3Cb6AFbXgFQjrsOADGcSm83UG770/g' ./first_time.sh`
`./first_time.sh`
--- backup file ./first_time_bkp.sh

### Apache2
`sudo systemctl status apache2`

### Replace with domain IP
`find ./ -type f -exec sed -i -e  's/127.0.0.1/142.93.208.220/g' {} \;`

### Run
`gunicorn -b 127.0.0.1:3002 -w 4 --worker-class gevent app:app --log-level debug --limit-request-line 8000`


### Country List
`https://gist.github.com/anubhavshrimal/75f6183458db8c453306f93521e93d37#file-countrycodes-json`


### Run mysql
`brew services restart mysql`
`mysql -u root -p root12345`

`CREATE USER 'piidm_dev'@'localhost' IDENTIFIED WITH mysql_native_password BY 'piidm_dev_password123';`
`GRANT ALL PRIVILEGES ON * . * TO 'piidm_dev'@'localhost';`

`mysql -u piidm_dev -p piidm_dev_password123`
`Create database piidm_dev;`
`use piidm_dev;`



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