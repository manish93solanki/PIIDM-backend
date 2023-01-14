### PIIDM APIs

### DB Setup
```
export FLASK=app.py
flask db init
flask db migrate -m "create tables"
flask db upgrade
```

rm -f ./piidm_dev.db && rm -rf ./migrations && flask db init && flask db migrate && flask db upgrade


### Country List
`https://gist.github.com/anubhavshrimal/75f6183458db8c453306f93521e93d37#file-countrycodes-json`


### Run mysql
`brew services restart mysql`
`mysql -u root -p root12345`

`CREATE USER 'piidm_dev'@'localhost' IDENTIFIED WITH mysql_native_password BY 'piidm_dev_password123';`
`GRANT ALL PRIVILEGES ON * . * TO 'piidm_dev'@'localhost';`

`mysql -u piidm_dev -p piidm_dev_password123`
`Create database piidm_dev;`
