import json
import sqlite3
import flask


def run_sql(sql):
    with sqlite3.connect("netflix (1).db") as connection:
        connection.row_factory = sqlite3.Row
        result = []
        for item in connection.execute(sql).fetchall():
            result.append(dict(item))

        return result


app = flask.Flask(__name__)


@app.get("/movie/<title>")
def step_1(title):
    sql = f'''
            SELECT title, country, release_year, listed_in as genre, description
            FROM netflix
            WHERE title='{title}' 
            ORDER BY date_added desc 
            LIMIT 1
'''
    result = run_sql(sql)
    if result:
        result = result[0]

    return flask.jsonify(result)


@app.get("/movie/<int:year1>/to/<int:year2>")
def step_2(year1, year2):
    sql = f'''
            SELECT title, release_year
            FROM netflix
            WHERE release_year between {year1} and {year2}
            ORDER BY release_year desc
            LIMIT 100
'''
    return flask.jsonify(run_sql(sql))


@app.get("/rating/<rating>")
def step_3(rating):
    my_dict = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }
    sql = f'''
            SELECT title, rating, description
            FROM netflix
            WHERE rating in {my_dict.get(rating, ("R", "PG-13", "NC-17", "PG"))}
'''
    return flask.jsonify(run_sql(sql))


@app.get("/genre/<genre>")
def step_4(genre):
    sql = f'''
            SELECT title, description, release_year
            FROM netflix
            WHERE listed_in LIKE '%{genre.title()}%'
            ORDER BY release_year desc
            LIMIT 10
    '''
    return flask.jsonify(run_sql(sql))


def step_5(name1='Rose McIver', name2='Ben Lamb'):
    sql = f'''
            SELECT "cast"
            FROM netflix
            WHERE "cast" like '%{name1}%' and "cast" like '%{name2}%'
            ORDER BY release_year desc
        '''
    result = run_sql(sql)
    main_name = {}

    for item in result:
        names = item.get('cast').split(", ")
        for name in names:
            main_name[name] = main_name.get(name, 0) + 1

    result = []
    for item in main_name:
        if item not in (name1, name2) and main_name[item] >= 2:
            result.append(item)


def step_6(types='TV Show', release_year=2021, genre='TV'):
    sql = f'''
            SELECT title, description
            FROM netflix
            WHERE type = '{types}'
            AND release_year = '{release_year}'
            AND listed_in like '%{genre}%'
            '''
    return json.dumps(run_sql(sql), indent=4, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)
    # print(step_5())
    # print(step_6())
