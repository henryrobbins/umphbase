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
python clean.py
```

## MySQL Database

Pulling and cleaning the data from ATU can be a little time-consuming.
Alternatively, you can download a `.sql` file which is regularly updated.
Instructions for downloading the `.sql` file and creating the MySQL database
are given below.

```
shell> curl https://umphbase-bucket.s3.us-east-2.amazonaws.com/umphbase.sql.gz --output umphbase.sql.gz
shell> gzip -d umphbase.sql.gz
shell> mysql -u [user] -p

mysql> CREATE DATABASE umphbase
mysql> USE umphbase
mysql> SOURCE umphbase.sql
```

Using [upload.py](aws/update/upload.py), the pull from ATU can be pushed to
a MySQL database. You can connect to the database in multiple different ways.
An example of each of the three methods is given below.

Method 1: Pass the arguments directly to the script

```
python upload.py --path atu_cleaned --method args \
--host [host] --database [database] --u [user] -p [password]
```

Method 2: Have the script prompt you for the arguments

```
python upload.py --path atu_cleaned --method prompt
Connect to a SQL database.
Host: [host]
Database: [database]
User: [user]
Password: [password]
```

Method 3: Store the arguments in a JSON file

```
python upload.py --path atu_cleaned --method json --json credentials.json

# credentials.json
{
    "host": [host],
    "database": [database],
    "user": [user],
    "password": [password]
}
```

This functionality is made possible using Amazon Web Services (AWS). To learn
more about how AWS is used and get instructions on hosting your own endpoint,
see the [README](aws/README.md) in the [aws](aws) directory.

## License

Licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/)
