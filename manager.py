import json

from bson import json_util
from kafka import KafkaConsumer, KafkaProducer
from time import sleep

from game_logic.game import Game

def publish_message(producer_instance, topic_name, key, value, value_type="json"):
    """
    Publishes the json type message with producer, topic_name, key and value. Optional value_type attribute that can be assigned to string.
    """
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
        print('Exception in publishing message')
        print(str(ex))

def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10))
    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
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

def connect_players(id, consumer_connect, consumer_ok):
    """
    Functionality to connect all four clients
    """
    client_id = None
    ok = False
    
    while ok == False:
        for msg in consumer:
            client_id = msg.value.decode()
        if client_id is not None:
            producer = connect_kafka_producer()
            publish_message(producer, "welcome", "welcome", "{}".format(id), "string")
            producer.close()
            while ok == False:
                #ok = listen_OK(consumer_ok)
                #does not work for some reason
                for msg in consumer_ok:
                    ok = msg.value.decode()
    
    print("player connected")
    
def parse_cards():
    """
    Parses the data coming from the database
    """
    
    cards = []
    ground = game.show_place_cards(("ground",))
    for player in players:
        cards.append(game.show_place_cards(player))
    
    data = {"players": [{"playerNumber": 1, "cards": cards[0]}, {"playerNumber": 2, "cards": cards[1]}, {"playerNumber": 3, "cards": cards[2]}, {"playerNumber": 4, "cards": cards[3]}], "ground": ground, "turn": turn}
    
    return data
    
def play_a_card(game_consumer):
    """
    gets the played card and the player
    """
    played = None
    
    while True:
        for msg in game_consumer:
            played = json.loads(msg.value)
            return played

def end_the_game(producer):
    """
    ends the game
    """
    points_team_1, points_team_2 = game.points_counter()
    
    print("game has ended")
    print("team 1 points")
    print(points_team_1)
    print("cards tem one")
    print(game.show_place_cards(["deck_1"]))
    
    print("team 2 points")
    print(points_team_2)
    print("cards tem one")
    print(game.show_place_cards(["deck_2"]))
    
    won = "You have won the game!"
    lost = "You have lost the game :("
    tie = "game has ended to a tie"


    if points_team_1 > points_team_2:
        for i in range(4):
            if (i == 0) or (i == 2):
                publish_message(game_producer, "player_{}".format(i + 1), "game", won, "string")
            else:
                publish_message(game_producer, "player_{}".format(i + 1), "game", lost, "string")
    elif points_team_1 < points_team_2:
        for i in range(4):
            if (i == 1) or (i == 3):
                publish_message(game_producer, "player_{}".format(i + 1), "game", won, "string")
            else:
                publish_message(game_producer, "player_{}".format(i + 1), "game", lost, "string")
    else:
        for i in range(4):
            publish_message(game_producer, "player_{}".format(i + 1), "game", tie, "string")

if __name__ == "__main__":
    consumer = KafkaConsumer("connect", bootstrap_servers=["localhost:9092"], api_version=(0,10), consumer_timeout_ms=1000)
    consumer_ok = KafkaConsumer("OK", bootstrap_servers=["localhost:9092"], api_version=(0,10), consumer_timeout_ms=1000)
    game_consumer = KafkaConsumer("play", bootstrap_servers=["localhost:9092"], api_version=(0,10), consumer_timeout_ms=1000)
    for i in range(4):
        connect_players(i + 1, consumer, consumer_ok)
        
    consumer.close()
    print("all players connected")
    
    turn = 1
    
    game = Game()
    players = game.players()
    cards = game.show_place_cards(players[3])
    
    game_producer = connect_kafka_producer()
    
    data = parse_cards()
    
    while len(cards) > 0:
        for i in range(4):
            publish_message(game_producer, "player_{}".format(i + 1), "game", data)
        
        played_card = play_a_card(game_consumer)
        if (int(played_card["player"]) == turn):
            print(int(played_card["card"]))
            game.play_card(game.show_place_cards(players[turn - 1])[int(played_card["card"])], players[turn - 1])
        turn += 1
        if turn > 4:
            turn = 1
            
        cards = game.show_place_cards(players[3])
        data = parse_cards()
            
    for i in range(4):
        publish_message(game_producer, "player_{}".format(i + 1), "game", {"turn": "end"})
        
    #this helps the clients to catch up
    sleep(5)
    
    print("game over")
    end_the_game(game_producer)
    