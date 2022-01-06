# TypeDB -> CSV to TypeQL (tql) Insert Script
 
<font color = 'yellow'>This script takes a .csv file and automatically generates a typeQL insert script for you. Intended for TypeDB users who don't need the massive power of [TypeDB Loader](https://github.com/typedb-osi/typedb-loader), but don't want the hassle of having to type out a bunch of TypeQL insert commands.</font>

<b> NOTES </b>

Has been tested with all supported TypeDB data types (strings, longs, doubles, booleans, datetimes). `Booleans must be entered with 1st letter capitalized and the rest lowercase`(like `False`). 

Also, `datetimes must be in one of the following formats` (a trailing 'Z' for zulu time is also acceptable when times are included):
```
   - yyyy-mm-dd
   - yyyy-mm-ddThh:mm
   - yyyy-mm-ddThh:mm:ss
   - yyyy-mm-ddThh:mm:ss.f
   - yyyy-mm-ddThh:mm:ss.ff
   - yyyy-mm-ddThh:mm:ss.fff
```

## CSV FORMAT

![plot](csv_preview.png)

Each row represents either an entity or a relationship.

<b> 3 columns are mandatory </b>, the rest contain the attribute and role names defined in your schema.

- `ent_or_rel` - the script uses this to figure out if it's supposed to be making an entity or a relationship for this row of data. You can write `ent` or `entity` or `rel` or `relation`. Capitalization doesn't matter- just the letters `ent` and `rel`. You can even write `entropy` and it'll recognize the `ent` as meaning this is an entity row.

- `sub_type` - defines <i>what kind of entity or relationship is in this row </i>. For example, if you have a `person` entity type in your schema, and this row is for a person, then you put `person` there.

- `alias` - this is the typeQL-style variable you will use to represent this entity. e.g. `$x`. <i>Each row must a unique one in this column </i>.

### Other Column Names

The rest of the column names must correspond to your schema's `attributes` and `roles`.

The values in your role columns (<i> in my example `host` and `client`</i>) must correspond to the aliases you used when defining your entities.

<u>Column order is not important</u>. The script will figure out which columns contain attributes, and which ones contain info describing roles in a relationship.

Row order `is` important, but no more than it is in any TypeQL script. Just make sure you define your entities before you start making links between them.

## HOW TO USE

0. Install the Python package `pandas`
   - `conda install pandas -y`
     or
   - `pip3 install pandas`
1. <u>Have your database & schema created already</u>. This only adds entities and relations to a pre-existing database with a schema loaded.
2. Save this script somewhere on your computer. It has been tested with Python3.6, but it should work with any Python3.x. If it doesn't, let me know.
3. EXECUTE THE SCRIPT LIKE THIS:
   - $ `python3 path/to/data.csv path/to/desired_script_name.tql`
4. Launch your TypeDB console (method varies depending on your install)
5. `> transaction <database_name> data write`
6. `> source /path/to/desired_script_name.tql`
7. `> commit`

Voila, your data is now in your database.
