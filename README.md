# Umphbase

[All Things Umphrey's](https://allthings.umphreys.com/) (ATU) is the static
website which maintains setlist data for [Umphrey's McGee](https://www.umphreys.com/).
This project provides functionality to scrape setlist data from ATU and
compile a [Deadbase](https://www.gdao.org/items/show/100802)-style book
affectionately referred to as *Umphbase*.

Initially, [Selenium](https://selenium-python.readthedocs.io/) and
[Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) were used to
scrape the data from the site. However, in June of 2021, a new version of ATU
was released which provides an [API](https://allthings.umphreys.com/api/docs)
to access the site's data. Read more about the transition
[here](https://allthings.umphreys.com/faq/). The TL;DR is the new version is
based on a setlist engine called [Songfish](https://songfish.xyz/) by
[Adam Scheinberg](https://adamscheinberg.com/).

## Installation (v1.0.0)

First, clone the repo and naviagate to the [directory](v1.0.0) containing files
related to Umphbase v1.0.0.

```
git clone https://github.com/henryrobbins/umphbase.git
cd umphbase/v1.0.0
```

The last web-scrape from the old version of ATU is located in
[atu_pull_2020](v1.0.0/atu_pull_2020-12-21). Umphbase v1.0.0 is created with
[LaTeX](https://www.latex-project.org/). The compilation of the book
requires two steps: generating the `.tex` files and then compiling them.

Generating the `.tex` files can be done by running the jupyter notebook
[compile.ipynb](v1.0.0/compile.ipynb) or from the commandline:

```
pip install runipy
runipy compile.ipynb
```

Lastly, use your favorite LaTeX compiler (like
[Texmaker](https://www.xm1math.net/texmaker/)) to compile
[umphbase-v1.0.0.tex](v1.0.0/umphbase-v1.0.0/umphbase-v1.0.0.tex).

Generating the `.tex` files and compiling them takes about 10 minutes and
30 seconds respectively on a MacBookPro 11.4.0 (16GB, 2.6GHz). For this reason,
the [PDF](v1.0.0/umphbase-v1.0.0/umphbase-v1.0.0.pdf) is pre-compiled.

## Installation (v2.0.0)

Umphbase v2.0.0 is currently in the works. The commands below clone the repo
and then pull the latest setlist data from the ATU database via the API (v1).
The book compilation component of v2.0.0 is under development.

```
git clone https://github.com/henryrobbins/umphbase.git
cd umphbase
python pull.py
```

## MySQL Database

Pulling and cleaning the data from ATU can be a little time-consuming.
Alternatively, you can pull the data from a MySQL database which is
regularly updated. To access the database, you can use
[MySQL Workbench](https://dev.mysql.com/downloads/workbench/). The connection
parameters for the database are given below. Note that `user` has read-only
access.

```
host: umphbase.c8pcawy2rbuj.us-east-2.rds.amazonaws.com
database: umphbase
user: user
password: pass
```

Using [sql_push.py](sql_push.py), the pull from ATU can be pushed to a MySQL
database. You can connect to the database in two different ways. The first
option is to provide the connection parameters every time you run the script.

```
python sql_push.py
Connect to a SQL database.
Host: `host`
Database: `database name`
User: `user`
Password: `password`
```

The second option is to create a `json` file (`login.json` in the example
below) to store these parameters.

```
{
    "host": `host`,
    "database": `database name`,
    "user": `user`,
    "password": `password`
}
```
```
python sql_push.py login
```

## License

Licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/)