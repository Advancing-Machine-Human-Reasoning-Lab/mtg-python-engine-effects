from MTG import game
from MTG import play
from MTG import gamesteps
from copy import deepcopy
    
class ObserveGameStates:
    def __init__(self, previous,  current) -> None:
        self.previousPlayerList = previous
        self.currentPlayerList = current
        self.numPlayers = len(previous)

    def observe(self):
        self.lifeChange()
        self.checkStatusChange()
        #TODO: check for other things that may be affected

    def lifeChange(self):
        for i in range(self.numPlayers):
            if self.previousPlayerList[i].life != self.currentPlayerList[i].life:
                difference = self.getLifeDifference(i)
                print(f"Player{i}'s life changed by {difference}")

    def getLifeDifference(self, playerIndex):
        return self.currentPlayerList[playerIndex].life - self.previousPlayerList[playerIndex].life

    def checkStatusChange(self):
        for i in range(self.numPlayers):
            prevZoneList = self.getCardsInAllZones(self.previousPlayerList[i])
            curZoneList = self.getCardsInAllZones(self.currentPlayerList[i])

            for zone1, zone2 in zip(prevZoneList, curZoneList):
                if (zone1.status != zone2.status):
                    print(f"Card {zone1} has changed to status(es): {zone2.status}")

    def getCardsInAllZones(self, player):
        return player.battlefield.elements + player.exile.elements + player.graveyard.elements
    
def catchGameState(game):
    return deepcopy(game.players_list)

def playCard(card):
    card.targets()
    inPlay = play.Play(apply_func=card.play_func, card=card)
    inPlay.apply()
    return inPlay

def setGameConditions():
    decks = game.parseDecks()

    gamePlayed = game.Game(decks)
    gamePlayed.setup_game()

    gamePlayed.step = gamesteps.Step.BEGINNING_OF_COMBAT
    return gamePlayed

def getCardName(card):
    return card.characteristics.name

def getCardText(card):
    return card.characteristics.text

def testInstants(hand, currentGame):
    instantsPlayed = set()
    instants = getInstants(hand)

    for instant in instants:
        cardName = getCardName(instant)
        if cardName in instantsPlayed:
            continue

        print(cardName)

        prevState = catchGameState(currentGame) 

        try:
            playCard(instant)
        except:
            raise Exception(f"Could not play {instant.characteristics.name}")
        
        instantsPlayed.add(cardName)
        currentState = catchGameState(currentGame)
        ObserveGameStates(prevState, currentState).observe()
        
def getInstants(hand):
    instants = []
    for card in hand:
        if card.is_instant:
            instants.append(card)
    return instants

if __name__ == "__main__":
    currentGame = setGameConditions()

    players = currentGame.players_list
    #TODO: Automate it for both players
    hand0 = players[0].hand 

    #TODO: Complete, and expand to creatures and others
    testInstants(hand0, currentGame)