import json
import logging

from bson import json_util
from game_logic.game import Game
from kafka import KafkaConsumer, KafkaProducer
from time import sleep


def publish_message(producer_instance, topic_name, key, value, value_type="json"):
    """
    Publishes the json type message with producer, topic_name, key and value. Optional value_type attribute that can be assigned to string.
    """
    value_bytes = b''
    try:
        key_bytes = bytes(key, encoding='utf-8')
        if value_type == "json":
            value_bytes = json.dumps(value, default=json_util.default).encode("utf-8")
        elif value_type == "string":
            value_bytes = bytes(value, encoding='utf-8')

        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print('Message published successfully.')
    except Exception as ex:
        logging.error('Exception in publishing message', exc_info=True)


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['kafka:29092'], api_version=(0, 10))
        print('Producer connected!')
    except Exception as ex:
        logging.error('Exception while connecting Kafka', exc_info=True)
    finally:
        return _producer


"""        
def listen_OK(consumer):
    status = False
    for msg in consumer:
        status = "OK"
    if consumer is not None:
        consumer.close()
    return status
"""


def connect_players(_id, consumer_connect, ok_consumer):
    """
    Functionality to connect all four clients
    """
    print("Connecting players...")
    client_id = None
    ok = False

    while not ok:
        for msg in consumer_connect:
            client_id = msg.value.decode()
            print(client_id)
        if client_id is not None:
            producer = connect_kafka_producer()
            publish_message(producer, "welcome", "welcome", "{}".format(_id), "string")
            producer.close()
            while not ok:
                print("Not ok yet...")
                # ok = listen_OK(consumer_ok)
                # does not work for some reason
                for msg in ok_consumer:
                    ok = msg.value.decode()

    print("Player connected")


def parse_cards():
    """
    Parses the data coming from the database
    """

    tcards = []
    ground = game.show_place_cards(("ground",))
    for player in players:
        tcards.append(game.show_place_cards(player))

    tdata = {"players": [{"playerNumber": 1, "cards": tcards[0]}, {"playerNumber": 2, "cards": tcards[1]},
                        {"playerNumber": 3, "cards": tcards[2]}, {"playerNumber": 4, "cards": tcards[3]}],
            "ground": ground, "turn": turn}

    return tdata


def play_a_card(game_consumer):
    """
    gets the played card and the player
    """

    while True:
        for msg in game_consumer:
            played = json.loads(msg.value)
            return played


def end_the_game(producer):
    """
    ends the game
    """
    points_team_1, points_team_2 = game.points_counter()

    print("Game has ended")
    print("Team 1 points")
    print(points_team_1)
    print("Cards team one")
    print(game.show_place_cards(["deck_1"]))

    print("Team 2 points")
    print(points_team_2)
    print("Cards team one")
    print(game.show_place_cards(["deck_2"]))

    won = "You have won the game!"
    lost = "You have lost the game :("
    tie = "Game has ended to a tie"

    if points_team_1 > points_team_2:
        for i in range(4):
            if (i == 0) or (i == 2):
                publish_message(producer, "player_{}".format(i + 1), "game", won, "string")
            else:
                publish_message(producer, "player_{}".format(i + 1), "game", lost, "string")
    elif points_team_1 < points_team_2:
        for i in range(4):
            if (i == 1) or (i == 3):
                publish_message(producer, "player_{}".format(i + 1), "game", won, "string")
            else:
                publish_message(producer, "player_{}".format(i + 1), "game", lost, "string")
    else:
        for i in range(4):
            publish_message(producer, "player_{}".format(i + 1), "game", tie, "string")


if __name__ == "__main__":
    print("Manager starting...")

    consumer = KafkaConsumer("connect", bootstrap_servers=["kafka:29092"], api_version=(0, 10),
                             consumer_timeout_ms=1000)
    consumer_ok = KafkaConsumer("OK", bootstrap_servers=["kafka:29092"], api_version=(0, 10),
                                consumer_timeout_ms=1000)
    game_consumer = KafkaConsumer("play", bootstrap_servers=["kafka:29092"], api_version=(0, 10),
                                  consumer_timeout_ms=1000)

    for i in range(4):
        connect_players(i + 1, consumer, consumer_ok)

    consumer.close()
    print("All players connected")

    turn = 1

    logging.info('Game begin...')
    game = Game()
    players = game.players()
    cards = game.show_place_cards(players[3])

    game_producer = connect_kafka_producer()

    data = parse_cards()

    while len(cards) > 0:
        for i in range(4):
            publish_message(game_producer, "player_{}".format(i + 1), "game", data)

        played_card = play_a_card(game_consumer)
        if int(played_card["player"]) == turn:
            print(int(played_card["card"]))
            game.play_card(game.show_place_cards(players[turn - 1])[int(played_card["card"])], players[turn - 1])
        turn += 1
        if turn > 4:
            turn = 1

        cards = game.show_place_cards(players[3])
        data = parse_cards()

    for i in range(4):
        publish_message(game_producer, "player_{}".format(i + 1), "game", {"turn": "end"})

    # this helps the clients to catch up
    sleep(5)

    print("Game over")
    end_the_game(game_producer)
