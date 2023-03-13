# DS project

## Setting up the development environment

Run the script to setup the development environment.

```shell
chmod +x setup.sh
./setup.sh
```

## Dependency control

Note: ./setup.sh syncs these dependencies automatically when run,

### Sync dependencies
```shell
pip-sync
```

### Add or update dependencies
```shell
pip-compile
```


## Use the game logic

When you need to use the game logic first thing import the game object
```
from game_logic.game import Game
```

after that instantiate an object of the class Game. This wil create a database in ram and the manage the game logic. 
You can access it using public 3 methods and 1 public attribute: 

#### ground
is a public attribute that contains a reference to the playing ground

#### players()
Return a list of the four different players

#### show_place_cards(place)
Return a list of the cards contained in one place. By place are ment both the hands of the player and the ground

#### play_card(card, player)
Require a card and a player. If the card is in the hand of the player the method will play it. If the card is not in
the player hand it will raise an exception: "card not in player hand"


## Play the game

Start the system first, requires Docker.

```shell
chmod +x run.sh
./run.sh
```

After that connect 4 clients by running the following 4 times in separate terminals:
```shell
chmod +x play.sh
./play.sh
```

You need to give a second or two for client to connect (this is still a working issue)
Then you can play card with client and see what happens.