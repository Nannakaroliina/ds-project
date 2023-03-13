import random
import sqlite3
from sqlite3 import Error


class GameDatabase:

    def create_connection(self, db_file):
        """create a database file in the working directory"""
        connection = None
        try:
            connection = sqlite3.connect(db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)

        return connection

    def create_table(self, create_table_sql):
        """ creates a table starting from a connection and a sql statement
        :param create_table_sql: a CREATE TABLE statement
        :return
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def __init__(self):
        database = r":memory:"

        sql_create_cards_table = """CREATE TABLE IF NOT EXISTS cards(
                                        number INTEGER,
                                        suit TEXT CHECK(suit IN ('hearts', 'clubs', 'spades', 'diamonds')),
                                        position TEXT NOT NULL,  
                                        PRIMARY KEY (number,suit),
                                        FOREIGN KEY (position) REFERENCES places (name)
                                        );"""

        sql_create_places_table = """CREATE TABLE IF NOT EXISTS places(
                                        name TEXT PRIMARY KEY,
                                        type TEXT NOT NULL CHECK(type IN ('player', 'ground', 'deck'))
                                        );"""

        sql_create_players_table = """CREATE TABLE IF NOT EXISTS players(
                                        name TEXT PRIMARY KEY,
                                        deck TEXT NOT NULL,
                                        FOREIGN KEY (deck) REFERENCES decks(id),
                                        FOREIGN KEY (name) REFERENCES places(name));"""

        sql_create_decks_table = """CREATE TABLE IF NOT EXISTS decks(
                                    name TEXT PRIMARY KEY,
                                    scope INTEGER NOT NULL,
                                    FOREIGN KEY (name) REFERENCES places(name));"""

        self.conn = self.create_connection(database)

        if self.conn is not None:
            # create places table
            self.create_table(sql_create_places_table)

            # create card table
            self.create_table(sql_create_cards_table)

            # create table decks
            self.create_table(sql_create_decks_table)

            # create players table
            self.create_table(sql_create_players_table)
        else:
            print("ERROR cannot create database connection")

        with self.conn:

            # creates all the places in the game
            places = [('player_1', 'player'), ('player_2', 'player'), ('player_3', 'player'), ('player_4', 'player'),
                      ('deck_1', 'deck'), ('deck_2', 'deck'), ('ground', 'ground')]
            for place in places:
                self.__create_place(place)

            # creation of the two decks
            decks = [('deck_1' , 0), ('deck_2', 0)]
            for deck in decks:
                self.__create_deck(deck)

            # creation of the four player and connecting them to the two decks dividing in this way in two teams
            players = [('player_1', 'deck_1'), ('player_2', 'deck_2'), ('player_3', 'deck_1'), ('player_4', 'deck_2')]
            for player in players:
                self.__create_player(player)
            # printing the database to check for errors
            cards = self.__create_all_cards()
            for card in cards:
                self.__create_card(card)

    def __create_place(self, place):
        """
        Create a new row inside the place table
        :param conn:  Connection object
        :param place: place values
        :return:
        """

        sql = '''INSERT INTO places(name, type) VALUES(?,?)'''
        cur = self.conn.cursor()
        cur.execute(sql, place)
        self.conn.commit()
        return cur.lastrowid

    def __create_deck(self, deck):
        """
        creates a new row in the decks table
        :param conn: connection object
        :param deck: deck values
        :return:
        """
        sql = '''INSERT INTO decks(name, scope) VALUES(?, ?)'''
        cur = self.conn.cursor()
        cur.execute(sql, deck)
        self.conn.commit()
        return cur.lastrowid

    def __create_player(self, player):
        """
        Creates a new row for the players table
        :param conn: connection object
        :param player: player value
        :return:
        """
        sql = '''INSERT INTO players(name, deck) VALUES(?, ?)'''
        cur = self.conn.cursor()
        cur.execute(sql, player)
        self.conn.commit()
        return cur.lastrowid

    def __create_card(self, card):
        """
        Creates a new row for the card class
        :param conn: connection object
        :param card: card values
        :return:
        """
        sql = '''INSERT INTO cards(number, suit, position) VALUES(?, ?, ?)'''
        cur = self.conn.cursor()
        cur.execute(sql, card)
        self.conn.commit()
        return cur.lastrowid

    def __create_all_cards(self):
        """
        Function that creates shuffle and distribute the cards between the four players.
        :return: a list of card to be added to the database
        """
        cards = []
        for i in range(1, 11):
            for suit in ('hearts', 'clubs', 'spades', 'diamonds'):
                card = [i, suit]
                cards.append(card)

        random.shuffle(cards)
        players = self.select_all_players_names()
        i = 0
        for card in cards:
            card.append(players[i])
            i += 1
            if i > 3:
                i = 0
        return cards

    def select_all_places(self):
        """
        Select all the places in the database
        :return: list of places
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM places")

        rows = cur.fetchall()

        return rows

    def select_all_places_and_type(self):
        """
        Select all the places in the database
        :return: list of places
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM places")

        rows = cur.fetchall()

        return rows

    def select_all_decks(self):
        """
        Select all the places in the database
        :return: list of decks
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM decks")

        rows = cur.fetchall()

        return rows

    def select_all_decks_and_scope(self):
        """
        Select all the decks and the corrisponding ammount of scope
        :return: list of decks
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM decks")

        rows = cur.fetchall()

        return rows

    def select_player_deck(self, player):
        """
        Select the name of the name of the deck of a player
        :param player: name of the player
        :return: the name of the deck
        """

        cur = self.conn.cursor()
        sql = "SELECT deck FROM players WHERE name = ?"
        cur.execute(sql, player)

        deck = cur.fetchone()[0]

        return deck

    def select_all_players(self):
        """
        Select all the players in the database
        :return: list of all the places in the game
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM players")

        rows = cur.fetchall()

        return rows

    def select_all_players_and_deck(self):
        """
        Select all the places in the database
        :return: list of all the places and their deck
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM players")

        rows = cur.fetchall()

        return rows

    def select_all_players_names(self):
        """
        Select all the players names in the database
        :return: list of decks
        """
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM players")

        rows = cur.fetchall()
        players = []
        for player in rows:
            players.append(player[0])
        return players

    def select_all_cards(self):
        """
        Select all the cards in the database
        :return: list of decks
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM cards")

        rows = cur.fetchall()

        return rows

    def select_position_cards(self, place):
        """
        Fetches from database the cards of the corresponding position and returns them in a list
        :param place:
        :return: list of cards
        """
        cur = self.conn.cursor()
        sql = "SELECT number, suit FROM cards WHERE position=?"
        cur.execute(sql, place)

        rows = cur.fetchall()

        return rows

    def select_card_position(self, card):
        """
        displays the position of a card
        :param card: selected card
        :return: position of the card
        """
        cur = self.conn.cursor()
        sql = "SELECT position FROM cards WHERE number=? AND suit=?"
        cur.execute(sql, card)

        rows = cur.fetchall()

        return rows

    def ground(self):
        """
        get position ground
        :return: position of the card
        """
        cur = self.conn.cursor()
        sql = "SELECT name FROM places WHERE name = ?"
        cur.execute(sql, ["ground"])

        rows = cur.fetchall()

        return rows

    def update_card_position(self, card, new_position):
        """
        Update the card position for example moving from a player hand to the ground or from the ground to a player deck
        :param card: select the card that has to be moved
        :param new_position: sets the new position of the card
        :return:
        """
        sql = '''UPDATE cards 
                 SET position = ?
                 WHERE number = ? AND suit = ?;'''
        cur = self.conn.cursor()
        cur.execute(sql, (new_position, card[0], card[1]))
        self.conn.commit()

    def add_scopa(self, deck):
        """
        Add one to the counter of scope for a team
        :param deck: Indicates the deck
        :return: nothing
        """
        retriever_sql = '''SELECT scope FROM decks WHERE name = ?'''
        cur = self.conn.cursor()
        cur.execute(retriever_sql, [deck])
        scope = cur.fetchone()[0]

        scope += 1

        update_sql = '''UPDATE decks
                        set scope = ?
                        WHERE name = ?;'''
        cur = self.conn.cursor()
        cur.execute(update_sql, (scope, deck))
