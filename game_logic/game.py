from game_logic.Database import game_database
from itertools import combinations


class Game:
    """
    Game function to manage all the logic of the game.
    Public methods: show_place_cards, players, play_card
    public attributes: ground (place where all the played cards are)
    """

    def __init__(self):

        self.__last_player = None
        self.__database = game_database()
        self.ground = (self.__database.ground())[0]

    def show_place_cards(self, place):
        """
        function to show all the cards that are in a single place.
        The possible places are: player_1, player_2, player_3, player_4, ground, deck_1, deck_2
        :param place: a string indicating the place
        :return: a list of cards where ever card will be (int, suit) each suit is a string with one of four possible
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

        player_cards = self.__database.select_position_cards(player)
        if card in player_cards:
            self.__check_ground(card, player)
            ground_cards = self.__database.select_position_cards(self.ground)

            if len(ground_cards) <= 0:
                self.__database.add_scopa(self.__database.select_player_deck(player))

        else:
            raise Exception("card not in player hand")

    def __check_ground(self, card, player):
        """
        Method that contains the actual logic on the game behaviour after that a card has been player
        :param card: card that has been played
        :param player: player that plays the card
        :return:
        """
        """Fetched player deck"""
        deck = self.__database.select_player_deck(player)

        """Fetches a list of cards on the ground"""
        cards = self.__database.select_position_cards(self.ground)

        # SINGLE CARD CHECK
        """Check if there is an equal card on the ground and if there is puts the two cards in the player deck
        and sets the last player that picked a card"""
        for ground_card in cards:
            if card[0] == ground_card[0]:
                self.__database.update_card_position(card, deck)
                self.__database.update_card_position(ground_card, deck)
                self.__last_pick(player)
                return

        # COMBINATIONS CHECK
        """Check if there is a combination of cards that has the sum equal to the number of the played card than adds 
        all of them to the player's deck and sets the player as the last one who picked a card"""
        for n in range(2, len(cards) + 1):
            print("combinations of " + str(n) + "cards\n")
            for comb in combinations(cards, n):
                print(comb)
                card_sum = 0
                for comb_card in comb:
                    card_sum += comb_card[0]
                if card_sum == card[0]:
                    self.__database.update_card_position(card, deck)
                    for ground_card in comb:
                        self.__database.update_card_position(ground_card, deck)

                    """Sets the player as last player"""
                    self.__last_pick(player)
                    return

        self.__database.update_card_position(card, self.ground[0])
        return

    def __last_pick(self, player):
        self.__last_player = player

    def points_counter(self):
        """
        counts the points once the game is finished. The methods strats by checking if any player still has cards to
        play in case it raises and EXCEPTION
        :return:
        """

        players = self.players()

        for player in players:
            if len(self.show_place_cards(player)) > 0:
                raise Exception("the game is not finished " + player[0] + " still has cards to play")

        # MOVE THE LAST CARDS TO THE DECK OF THE LAST PLAYER
        remaining_cards = self.__database.select_position_cards(self.ground)

        for card in remaining_cards:
            self.__database.update_card_position(card, self.__database.select_player_deck(self.__last_player))

        # START COUNTING THE POINTS
        decks = self.__database.select_all_decks_and_scope()
        points_team_1 = (decks[0])[1]
        points_team_2 = (decks[1])[1]

        cards_team_1 = self.show_place_cards([(decks[0])[0]])
        cards_team_2 = self.show_place_cards([(decks[1])[0]])

        """Checking who gets the point for most cards"""
        if len(cards_team_1) > len(cards_team_2):
            points_team_1 += 1
        if len(cards_team_1) < len(cards_team_2):
            points_team_2 += 1

        """Checking who gets the point for most diamonds"""
        points_team_1, points_team_2 = self.__count_diamonds(cards_team_1, points_team_1, cards_team_2, points_team_2)

        """Checking who gets the point for the 7 of diamonds"""
        if (7, "diamonds") in cards_team_1:
            points_team_1 += 1
        else:
            points_team_2 += 1

        """Counts point from primiera"""
        points_team_1, points_team_2 = self.__count_primiera(cards_team_1, points_team_1, cards_team_2, points_team_2)

        return points_team_1, points_team_2

    def __count_diamonds(self, cards_team_1, points_team_1, cards_team_2, points_team_2):
        """
        Function that determines to which team should the diamonds point get assigned to.
        :param cards_team_1: list of cards of team 1
        :param points_team_1: int representing the points of team 1
        :param cards_team_2: list of cards of team 2
        :param points_team_2: int representing the points of team 2
        :return: (int) points team 1, (int) points team 2
        """
        diamonds_team_1 = []
        for card in cards_team_1:
            if card[1] == "diamonds":
                diamonds_team_1.append(card)

        diamonds_team_2 = []
        for card in cards_team_2:
            if card[1] == "diamonds":
                diamonds_team_2.append(card)

        if len(diamonds_team_1) > len(diamonds_team_2):
            points_team_1 += 1
        if len(diamonds_team_1) < len(diamonds_team_2):
            points_team_2 += 1

        return points_team_1, points_team_2

    def __count_primiera(self, cards_team_1, points_team_1, cards_team_2, points_team_2):
        """
        Function that determines to which team should the primiera points get assigned to.
        :param cards_team_1: list of cards of team 1
        :param points_team_1: int representing the points of team 1
        :param cards_team_2: list of cards of team 2
        :param points_team_2: int representing the points of team 2
        :return: (int) points team 1, (int) points team 2
        """
        sevens_team_1 = []
        for card in cards_team_1:
            if card[0] == 7:
                sevens_team_1.append(card)

        sevens_team_2 = []
        for card in cards_team_2:
            if card[0] == 7:
                sevens_team_2.append(card)

        if len(sevens_team_1) > len(sevens_team_2):
            points_team_1 += 1
        if len(sevens_team_1) < len(sevens_team_2):
            points_team_2 += 1

        return points_team_1, points_team_2


"""
def main():
    this_game = Game()
    players = this_game.players()
    cards = this_game.show_place_cards(players[3])
    while len(cards) > 0:
        for player in players:
            cards = this_game.show_place_cards(player)
            this_game.play_card(cards[0], player)

        cards = this_game.show_place_cards(players[3])

    points_team_1, points_team_2 = this_game.points_counter()

    print("team 1 points")
    print(points_team_1)
    print("cards tem one")
    print(this_game.show_place_cards(["deck_1"]))

    print("team 2 points")
    print(points_team_2)
    print("cards tem one")
    print(this_game.show_place_cards(["deck_2"]))


    # this_game.points_counter()


if __name__ == '__main__':
    main()"""
