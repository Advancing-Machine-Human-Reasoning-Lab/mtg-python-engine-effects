from itertools import cycle
import sys
import os
sys.path.append('/Users/wanqi/Desktop/Python-MTG')
os.chdir('/Users/wanqi/Desktop/Python-MTG')

from MTG.player import Player
from MTG.zone import *
from MTG.cards import *
from MTG.gamesteps import *

global GAME





class GameOverException(Exception):
    """Indicates that the game is over: that every player has either won, lost, or conceded"""
    pass

class Game(object):
    """A game object. This represents the entire state of an in-progress MTG game."""


    # start a game by giving each player their deck
    def __init__(self, decks):
        self.stack = Stack()
        self.num_players = len(decks)
        self.players_list = [Player(decks[i], 'player'+str(i), game=self) for i in range(self.num_players)]
        self.players = cycle(self.players_list)
        self.passed_priority = 0
        self.step = None
        self.pending_turns = []
        self.pending_steps = []


    def get_zone(self, zone_type, player=None):
        return {
            ZoneType.LIBRARY: player.library,
            ZoneType.HAND: player.hand,
            ZoneType.BATTLEFIELD: player.battlefield,
            ZoneType.GRAVEYARD: player.graveyard,
            ZoneType.STACK: self.stack,
            ZoneType.EXILE: player.exile,
            # ZoneType.COMMAND: player.command
        }[zone_type]

    ## TODO
    def apply_state_based_actions(self):
        print("Applying state based actions")
        pass

    ## TODO
    def apply_stack_item(self, stack_item):
        """ resolving a spell/effect from stack"""
        stack_item.apply()
        pass


    def apply_to_battlefield(self, apply_func, condition=lambda p: True):
        "Apply some function to all permanents on the battlefield (filtered out by a condition function if necessary)"
        for player in self.players_list:
            for permanent in player.battlefield.elements:
                if condition(permanent):
                    apply_func(permanent)


    def handle_priority(self, step, priority=None):
        if priority is None:
            priority = self.players_list.index(self.current_player)

        print("priority")
        self.passed_priority = 0

        while self.passed_priority < self.num_players or self.stack:  # while not everyone has passed priority
            self.apply_state_based_actions()
            play = self.players_list[priority].get_action()
            if play is None:  # passes priority
                self.passed_priority += 1
                priority = (priority + 1) % self.num_players  # who's next to get priority
                if self.passed_priority == self.num_players and self.stack:  # resolve top stack item
                    self.apply_stack_item(self.stack.pop())
                continue
            
            # responds with something; must have everyone re-pass priority
            print(play)
            self.passed_priority = 0

            if play.is_mana_ability or play.is_special_action:  # applies instantly
                play.apply()
            else:
                self.stack.add(play)  # add to stack



    def handle_beginning_phase(self, step):
        print(step)
        if step is Step.UNTAP:
            self.apply_to_battlefield(lambda permanent: permanent.untap())
            self.current_player.landPlayed = 0

        elif step is Step.UPKEEP:
            self.handle_priority(step)

        elif step is Step.DRAW:
            self.current_player.draw()
            self.handle_priority(step)
        
        for player in self.players_list:
            player.mana.clear()

        
    ## TODO
    def handle_main_phase(self, step):
        print(step)
        self.handle_priority(step)
        pass

        for player in self.players_list:
            player.mana.clear()

    ## TODO
    def handle_combat_phase(self, step):
        print(step)
        if step is Step.BEGINNING_OF_COMBAT:
            self.apply_to_battlefield(lambda p: p.trigger(triggerConditions.onEnterCombat))
        elif step is Step.DECLARE_ATTACKERS:
            self.apply_to_battlefield(lambda p: p.trigger(triggerConditions.onDeclareAttackers))
        elif step is Step.DECLARE_BLOCKERS:
            self.apply_to_battlefield(lambda p: p.trigger(triggerConditions.onDeclareBlockers))
        elif step is Step.END_OF_COMBAT:
            self.apply_to_battlefield(lambda p: p.trigger(triggerConditions.onEndofCombat))

        if step is Step.DECLARE_ATTACKERS:
            pass
            # declare attackers

        if step is Step.DECLARE_BLOCKERS:
            pass
            # declare blockers

            # resolve damage


        self.handle_priority(step)
        pass
        for player in self.players_list:
            player.mana.clear()



    def handle_end_phase(self, step):
        print(step)
        if step is Step.END:
            self.handle_priority(step)

        elif step is Step.CLEANUP:
            self.current_player.discard(self.current_player.hand.size() - self.current_player.maxHandSize)

        for player in self.players_list:
            player.mana.clear()


    def handle_turn(self):
        for phase in Phase:
            self.pending_steps.extend(phase.steps)

        while self.pending_steps:
            self.step = self.pending_steps.pop(0)
            {
                Step.UNTAP: self.handle_beginning_phase,
                Step.UPKEEP: self.handle_beginning_phase,
                Step.DRAW: self.handle_beginning_phase,
                Step.PRECOMBAT_MAIN: self.handle_main_phase,
                Step.BEGINNING_OF_COMBAT: self.handle_combat_phase,
                Step.DECLARE_ATTACKERS: self.handle_combat_phase,
                Step.DECLARE_BLOCKERS: self.handle_combat_phase,
                Step.FIRST_STRIKE_COMBAT_DAMAGE: self.handle_combat_phase,
                Step.COMBAT_DAMAGE: self.handle_combat_phase,
                Step.END_OF_COMBAT: self.handle_combat_phase,
                Step.POSTCOMBAT_MAIN: self.handle_main_phase,
                Step.END: self.handle_end_phase,
                Step.CLEANUP: self.handle_end_phase
            }[self.step](self.step)
        self.pending_turns.append(self.current_player)
        self.current_player = next(self.players)  # cycles to next player's turn



    ### debug

    ## TODO
    # print each player's states
    # print debug variables
    def print_game_state(self):
        print("\n\n\nPRINTING GAME STATE")

        print("\n\n\n")
        print("stack:\n")
        print(self.stack.elements)

        print("\n\n\n")
        for player in self.players_list:
            player.print_player_state()


    # def __repr__(self):
    #     return self.print_game_state()


    ## TODO
    def set_up_game(self):
        print("setting up game...")
        for player in self.players_list:
            player.draw(7)


    def run_game(self):
        self.current_player = next(self.players)
        self.set_up_game()
        while self.num_players:
            self.pending_turns.extend(self.players_list)  # everyone gets a turn queued up, in order
            
            try:
                self.handle_turn()
            except GameOverException:
                break




def read_deck(filename):
    """ File format:
    NUM CARDNAME

    e.g.
    10 Plains
    10 Oreskos Swiftclaw

    """
    file = open(filename, 'r').read().split("\n")
    deck = []
    for line in file:
        try:
            i = line.index(" ")
            num = int(line[:i])
            for j in range(num):  # add NUM copies of CARDNAME
                card = card_from_name(line[i+1:])
                if card:
                    deck.append(card)
                    # print(deck[-1].name())
                else:
                    pass
                    # print("card {} does not exist\n".format(line[i+1:]))
        except:
            raise DecklistFormatError()

    return deck


decks = [read_deck('cards/decks/deck1.txt'), read_deck('cards/decks/deck1.txt')]
GAME = Game(decks)
GAME.run_game()
