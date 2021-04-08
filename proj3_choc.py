####################
## Renzhong Lu    ##
## lurz           ##
####################

import sqlite3

# proj3_choc.py
# You can change anything in this file you want as long as you pass the tests
# and meet the project requirements! You will need to implement several new
# functions.

# Part 1: Read data from a database called choc.db
DBNAME = 'choc.sqlite'


def location(command):
    if 'none' in command:
        return ''
    elif 'country' in command:
        al2 = ''
        index = command.find('country') + 8
        while index < len(command) and command[index] != ' ':
            al2 += command[index]
            index += 1
        return f"C.Alpha2='{al2}'"
    elif 'region' in command:
        name = ''
        index = command.find('region') + 7
        while index < len(command) and command[index] != ' ':
            name += command[index]
            index += 1
        return f"C.Region='{name}'"
    else:
        return ''


def sell_source(command):
    if 'sell' in command:
        return 'B.CompanyLocationId=C.id'
    elif 'source' in command:
        return 'B.BroadBeanOriginId=C.id'
    else:
        return 'B.CompanyLocationId=C.id'


def rating(command):
    if 'ratings' in command:
        return ('ORDER BY B.Rating', 'ORDER BY AVG(B.Rating)', 'AVG(B.Rating)')
    elif 'cocoa' in command:
        return ('ORDER BY B.CocoaPercent',
                'ORDER BY AVG(B.CocoaPercent)', 'AVG(B.CocoaPercent)')
    elif 'number_of_bars' in command:
        return ('', 'ORDER BY COUNT(B.Id)', 'COUNT(B.Id)')
    else:
        return ('ORDER BY B.Rating', 'ORDER BY AVG(B.Rating)', 'AVG(B.Rating)')


def top_bottom(command):
    if 'top' in command:
        return 'DESC'
    elif 'bottom' in command:
        return 'ASC'
    else:
        return 'DESC'


def get_integer(command):
    splitted = command.split(' ')
    for word in splitted:
        if word.isnumeric():
            return 'LIMIT ' + word
    return 'LIMIT 10'


def get_sort(command):
    rate = rating(command)
    order = top_bottom(command)
    limit = get_integer(command)
    return (rate, order, limit)


def get_query(query):
    connection = sqlite3.connect(DBNAME)
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result


# Part 1: Implement logic to process user commands
def process_command(command):
    option = command.split(' ')[0]
    if option == 'bars':
        locate = location(command)
        s_s = sell_source(command)
        clause1 = ''
        if len(locate) != 0:
            clause1 = 'INNER JOIN Countries C ON ' + s_s + ' AND ' + locate

        rate, order, limit = get_sort(command)
        query = ("SELECT B.SpecificBeanBarName, B.Company, D.EnglishName, " +
                 "B.Rating, B.CocoaPercent, E.EnglishName " +
                 f"FROM Bars B " +
                 "LEFT JOIN Countries D ON B.CompanyLocationId=D.Id " +
                 f"LEFT JOIN Countries E ON B.BroadBeanOriginId=E.Id " +
                 f"{clause1} {rate[0]} {order} {limit}")
        # print (query)
        result = get_query(query)
        # print (result)
        return result
    elif option == 'companies':
        locate = location(command)
        clause1 = ''
        if len(locate) != 0:
            clause1 = sell_source('sell') + ' AND ' + locate + ' AND '

        rate, order, limit = get_sort(command)
        query = (f"SELECT B.Company, D.EnglishName, {rate[2]} " +
                 "FROM Bars B, Countries C, Countries D " +
                 f"WHERE {clause1}B.CompanyLocationId=D.Id GROUP BY " +
                 "B.Company HAVING COUNT(DISTINCT B.Id)>4 " +
                 f"{rate[1]} {order} {limit}")
        # print (query)
        result = get_query(query)
        # print (result)
        return result
    elif option == 'countries':
        locate = location(command)
        s_s = sell_source(command)
        clause1 = s_s
        if len(locate) != 0:
            clause1 = s_s + ' AND ' + locate

        rate, order, limit = get_sort(command)
        query = (f"SELECT C.EnglishName, C.Region, {rate[2]}" +
                 " FROM Bars B, Countries C " +
                 f"WHERE {clause1} GROUP BY C.EnglishName " +
                 "HAVING COUNT(DISTINCT B.Id)>4 " +
                 f"{rate[1]} {order} {limit}")
        # print (query)
        result = get_query(query)
        # print (result)
        return result
    elif option == 'regions':
        s_s = sell_source(command)
        rate, order, limit = get_sort(command)
        query = (f"SELECT C.Region, {rate[2]} FROM Bars B, Countries C " +
                 f"WHERE {s_s} GROUP BY C.Region HAVING COUNT(DISTINCT B.Id)>4 " +
                 f"{rate[1]} {order} {limit}")
        # print (query)
        result = get_query(query)
        # print (result)
        return result
    else:
        pass

    return []


def print_response(result):
    print(result)
    col = len(result[0])
    row6 = "| {name1:<20s} | {name2:<12s} | {loc1:<10s} | {rate1:5.1f} | {rate2:.0%} | {loc2:<10s} |".format

    if col == 6:
        for r in result:
            print(row6(name1=r[0] if len(r[0]) < 20 else r[0][0:17] + '...',
                       name2=r[1] if len(r[1]) < 12 else r[1][0:9] + '...',
                       loc1=r[2] if len(r[2]) < 10 else r[2][0:7] + '...',
                       rate1=r[3],
                       rate2=r[4],
                       loc2=r[5] if len(r[5]) < 10 else r[5][0:7] + '...'))


def load_help_text():
    with open('Proj3Help.txt') as f:
        return f.read()

# Part 2 & 3: Implement interactive prompt and plotting. We've started for you!


def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue
        elif response == 'exit':
            print('bye')
            break
        else:
            splitted = response.split(' ')
            if splitted[0] == 'bars' or splitted[0] == 'companies' or splitted[0] == 'countries' or splitted[0] == 'regions':
                print_response(process_command(response))


# Make sure nothing runs or prints out when this file is run as a
# module/library
if __name__ == "__main__":
    interactive_prompt()
