from Database import game_database


class Game:
    """
    Game function to manage all the logic of the game.
    Public methods: show_place_cards, players, play_card
    public attributes: gound (place where all the played cards are)
    """

    def __init__(self):

        self.__database = game_database()
        self.ground = (self.__database.ground())[0]

    def show_place_cards(self, place):
        """
        function to show all the cards that are in a single place.
        The possible places are: player_1, player_2, player_3, player_4, ground, deck_1, deck_2
        :param place: a string indicating the place
        :return: a list of cards where everi card will be (int, suit) each suit is a string with one of four possible
        values: "hearts", "clubs", "spades", "diamonds"
        """
        return self.__database.select_position_cards(place)

    def __places(self):
        """
        Function to get a list of all the possible places
        :return: a list of all the possible places
        """
        return self.__database.select_all_places()

    def players(self):
        """
        Function that returns a list of all the players in the game
        :return: a list of all the players in the game
        """
        return self.__database.select_all_players()

    def play_card(self, card, player):
        """
        Method to play a card from the hand of a player
        :param card: card that has to be player (number, suit)
        :param player: player that plays the card
        :return:
        """

        cards = self.__database.select_position_cards(player)
        if card in cards:
            self.__database.update_card_position(card, self.ground[0])
        else:
            raise Exception("card not in player hand")


"""
def main():
    this_game = Game()
    players = this_game.players()
    cards = this_game.show_place_cards(players[0])
    print(this_game.ground)
    this_game.play_card(cards[0], players[1])
    print(this_game.show_place_cards(this_game.ground))

if __name__ == '__main__':
    main()
"""