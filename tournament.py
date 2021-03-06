#!Troy Ballard - Back-End Project - May 27, 2017
#
# tournament.py -- implementation of a Swiss-system tournament
#
# See the README.TXT file for instructions on how to run.

import psycopg2

def connect():
    """"Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        return psycopg2.connect(dbname="tournament")
    except:
        print('Unable to connect to database.  See Github README file')

def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    db_cursor = conn.cursor()
    query = "DELETE FROM matches;"
    db_cursor.execute(query)
    conn.commit()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    db_cursor = conn.cursor()
    query = "DELETE FROM players;"
    db_cursor.execute(query)
    conn.commit()
    conn.close()

def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    db_cursor = conn.cursor()
    query = "SELECT COUNT(name) as c FROM players;"
    db_cursor.execute(query)
    # fetchone returns array with single element
    result = db_cursor.fetchone()
    conn.close()
    return result[0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    db_cursor = conn.cursor()
    query = "INSERT INTO players (name) VALUES (%s);"
    db_cursor.execute(query, (name,))
    conn.commit()
    conn.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    db_cursor = conn.cursor()
    # could have made this a VIEW, but just did the table JOINs in the function
    query = """SELECT p.id, p.name,
            (SELECT count(*) FROM
            matches WHERE matches.winner = p.id) as wins,
            (SELECT count(*) FROM
            matches WHERE p.id in (winner, loser)) as total
            FROM players p
            GROUP BY p.id
            ORDER BY wins DESC;"""
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    conn.close()
    return results

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    db_cursor = conn.cursor()
    query = "INSERT INTO matches (winner, loser) VALUES (%s, %s);"
    db_cursor.execute(query, (winner, loser,))
    conn.commit()
    conn.close()

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    results = []
    standings = playerStandings()
    for i in xrange(0, len(standings), 2):
        player1 = standings[i]
        player2 = standings[i+1]
        results.append([player1[0], player1[1], player2[0], player2[1]])

    return results
    
