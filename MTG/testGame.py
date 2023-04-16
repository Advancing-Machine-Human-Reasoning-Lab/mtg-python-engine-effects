import sys
import os
from MTG import game
from MTG import player
from MTG import play
from MTG import zone
from MTG import cards
from MTG import gamesteps
from MTG import cardtype
from MTG import combat
from MTG import triggers
from MTG.exceptions import *
#AMHR file

"""
    Keep track of what cards played, what they do, intended cause and effect
    will aim to play the card and examine the effect

    for example: if card deals 10 damage
        check if opponent blocked, and if not check that their life took 10 damage

    Only doing instants for now
"""

def getCardName(card):
    return card.characteristics.name

def getInstants(hand):
    instants = []
    for card in hand:
        if card.is_instant:
            instants.append(card)
    return instants

def printCardCharacteristics(cardList):
   for card in cardList:
        cardCharacteristics = card.characteristics
        print(f"{cardCharacteristics.name} \033[91m{cardCharacteristics.text}\033[0m")

if __name__ == "__main__":
    decks = game.parseDecks()
    gamePlayed = game.Game(decks)
    gamePlayed.setup_game()
    cardsPlayed = set()

    players = gamePlayed.players_list
    handPlayer0 = players[0].hand

    instants = getInstants(handPlayer0)
    printCardCharacteristics(instants)
    gamePlayed.step = gamesteps.Step.BEGINNING_OF_COMBAT

    for instant in instants:
        cardName = getCardName(instant)
        if cardName in cardsPlayed:
            # ignore cards we've already tested
            continue

        canTarget = instant.targets()
        try:
            inPlay = play.Play(apply_func=instant.play_func,
                               card=instant)
            inPlay.apply()
            print(players[1].life)            
            cardsPlayed.add(cardName)
        except:
            raise Exception(f"Could not play {instant.characteristics.name}")
        
 