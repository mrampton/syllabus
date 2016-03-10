
1. Create a new virtualenv: `virtualenv venv`
2. Install libraries: `./venv/bin/pip install click flask sqlalchemy psycopg2`
3. Create a database and a user. With Postgres:

    CREATE ROLE injection LOGIN PASSWORD 'somerealpassword';
    CREATE DATABASE injection;
    GRANT ALL ON DATABASE injection TO injection;

4. Edit `server.py` to set your database URI:

    DATABASEURI = "<your database uri>"

5. Run it in the shell: `./venv/bin/python server.py`

Or get help with: `./venv/bin/python server.py --help`


Fun queries:

* Get the size of the table:
    '); INSERT INTO bad_table SELECT 77, CONCAT('table size: ', count(*)) FROM bad_table; --
* Delete everything
    '); DROP TABLE bad_table; --
