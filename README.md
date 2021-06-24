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

## Installation

The commands below clone the repo and then pull the latest setlist data from
the ATU database via the APU (v1).

```
git clone https://github.com/henryrobbins/umphbase.git
cd umphbase
python pull.py
```

## License

Licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/)