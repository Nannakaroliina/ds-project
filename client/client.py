import json
import logging
import uuid

from bson import json_util
from kafka import KafkaConsumer, KafkaProducer


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
        logging.error('Exception in publishing message', exc_info=True)


def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['localhost:9092'], api_version=(0, 10))
        print('Connected!')
    except Exception as ex:
        logging.error('Exception while connecting Kafka', exc_info=True)
    finally:
        return _producer


def send_OK():
    """
    sends OK message to the manager. (not needed probably)
    """
    kafka_producer = connect_kafka_producer()
    publish_message(kafka_producer, "OK", "OK", "OK", "string")
    kafka_producer.close()


def connect_to_game(client_id):
    """
    Connects to the game with client_id (client_id not used at the moment)
    """
    pnumber = None
    kafka_producer = connect_kafka_producer()
    publish_message(kafka_producer, "connect", "conn", client_id, "string")
    welcome_consumer = KafkaConsumer("welcome", bootstrap_servers=['localhost:9092'], group_id=client_id,
                                     api_version=(0, 10), consumer_timeout_ms=1000)

    while True:
        for message in welcome_consumer:
            print(message.value.decode())
            pnumber = message.value.decode()
            print("You are player number: {}".format(pnumber))

        if pnumber is not None:
            welcome_consumer.close()
            send_OK()
            return pnumber

    if welcome_consumer is not None:
        welcome_consumer.close()


def play_a_card(cards, playerNumber):
    """
    Plays selected card
    """
    print("Pick a card you want to play")

    for i, card in enumerate(cards):
        print("Press {} to choose {} of {}".format(i, card[0], card[1]))

    while True:
        play = input("Your pick: ")
        try:
            if (int(play) < len(cards)) and (int(play) >= 0):
                break
        except ValueError:
            pass
        print("You must provide a suitable number")

    kafka_producer = connect_kafka_producer()
    publish_message(kafka_producer, "play", "play", {"card": play, "player": playerNumber})


def listen_messages(pnumber, tconsumer):
    """
    Basic function to determine wich client has the turn and goes to the play_a_card function() or ends the game if needed
    """

    turn = None
    tend = False

    for message in tconsumer:
        data = json.loads(message.value)
        turn = data["turn"]

    if turn == "end":
        tend = True

    elif turn is not None:
        if turn == int(pnumber):
            print("It is your turn")
            print("Cards on the ground are {}".format(data["ground"]))
            cards = data["players"][int(pnumber) - 1]["cards"]
            play_a_card(cards, pnumber)

        else:
            print("It is someone elses turn")
            print("Cards on the ground are {}".format(data["ground"]))
            print("Cards in your hand are {}".format(data["players"][int(pnumber) - 1]["cards"]))

    return tend


if __name__ == "__main__":
    logging.info("Client starting...")

    client = str(uuid.uuid4())

    playerNumber = connect_to_game(client)

    my_topic = "player_{}".format(int(playerNumber))
    consumer = KafkaConsumer(my_topic, bootstrap_servers=["localhost:9092"], api_version=(0, 10),
                             consumer_timeout_ms=1000)

    while True:
        end = listen_messages(playerNumber, consumer)
        if end:
            break

    print("Calculating results...")

    while True:
        for msg in consumer:
            print(msg.value.decode())
