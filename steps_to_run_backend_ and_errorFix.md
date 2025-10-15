1. Download the "piidm\_online\_sqlite.db" file from "https://www.sqlite.org/download.html" and add in PIIDM-BACKEND folder.
2. Add the "SQLALCHEMY\_DATABASE\_URL = f'sqlite:////Users/Manish/Documents/PIIDM Projects/piidm-backend/piidm\_online\_sqlite.db'"
   to app.py file.
3. Run the backend using command: python ./app.py.


## Whenever I  do git pull,   do the   following   activites
0. check if files are   changed  or not,  do the   needful  steps 
1. git   pull  origin   master
2. python -m flask db upgrade

Errors  (To fix):

1. I have got error - email/mobile and password are incorrect.

&nbsp; -->   Replace old "piidm\_online\_sqlite.db" with new "piidm\_online\_sqlite.db" file.


