import sys
import os

from itertools import cycle

sys.path.append('/Users/wanqi/Desktop/Python-MTG')
os.chdir('/Users/wanqi/Desktop/Python-MTG')

from MTG import player
from MTG import zone
from MTG import cards
from MTG import gamesteps
from MTG import combat
from MTG import permanent
from MTG.exceptions import *

global GAME





class Game(object):
    """A game object. This represents the entire state of an in-progress MTG game.


    Full doc string goes here
    """

    # Give each player their deck.
    def __init__(self, decks, test=False):
        self.stack = zone.Stack()
        self.num_players = len(decks)
        self.players_list = [player.Player(decks[i], 'player'+str(i), game=self)
                             for i in range(self.num_players)]
        # self.players = cycle(self.players_list)
        self.passed_priority = 0
        self.step = None
        self.pending_turns = []
        self.pending_steps = []
        self.test = test


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
        self.apply_to_battlefield(lambda p: p.dies(), 
                lambda p: p.is_creature() and p.status.damage_taken >= p.characteristics.toughness)
        pass

    ## TODO
    def apply_stack_item(self, stack_item):
        """ resolving a spell/effect from stack"""
        stack_item.apply()
        pass


    def apply_to_battlefield(self, apply_func, condition=lambda p: True):
        """Apply some function to permanents on the battlefield 

        - filter out by a condition function if necessary
        - defaults to all permanents
        """
        for _player in self.players_list:
            for permanent in _player.battlefield.elements:
                if condition(permanent):
                    apply_func(permanent)


    def handle_priority(self, step, priority=None):
        if priority is None:
            priority = self.players_list.index(self.current_player)

        self.passed_priority = 0

        while self.passed_priority < self.num_players or self.stack:  # while not everyone has passed priority
            self.apply_state_based_actions()

            if self.players_list[priority].passPriorityUntil not in [None, step]:  # auto pass priority
                _play = None
            else:
                self.players_list[priority].passPriorityUntil = None
                _play = self.players_list[priority].get_action()  # ask current player for an action
                

            if _play is None:  # passes priority
                self.passed_priority += 1
                priority = (priority + 1) % self.num_players  # who's next to get priority
                if self.passed_priority == self.num_players and self.stack:  # resolve top stack item
                    self.apply_stack_item(self.stack.pop())
                    self.passed_priority = 0
            else:
                # responds with something; must have everyone re-pass priority
                print(_play)
                self.passed_priority = 0

                if _play.is_mana_ability or _play.is_special_action:  # applies instantly
                    _play.apply()
                else:
                    self.stack.add(_play)  # add to stack



    def handle_beginning_phase(self, step):
        print(step)
        if step is gamesteps.Step.UNTAP:
            self.apply_to_battlefield(lambda permanent: permanent.untap())
            for _player in self.players_list:
                _player.landPlayed = 0

        elif step is gamesteps.Step.UPKEEP:
            self.handle_priority(step)
            self.apply_to_battlefield(lambda p: p.trigger(
                                    permanent.triggerConditions.onUpkeep))

        elif step is gamesteps.Step.DRAW:
            if self.first_player_does_not_draw:
                self.first_player_does_not_draw = False
            else:
                self.current_player.draw()
            self.handle_priority(step)
        


        
    ## TODO
    def handle_main_phase(self, step):
        print(step)
        self.handle_priority(step)
        pass



    ## TODO
    def handle_combat_phase(self, step):
        print(step)
        if step is gamesteps.Step.BEGINNING_OF_COMBAT:
            self.apply_to_battlefield(
                    lambda p: p.trigger(permanent.triggerConditions.onEnterCombat))

        elif step is gamesteps.Step.DECLARE_ATTACKERS:
            self.apply_to_battlefield(
                    lambda p: p.trigger(permanent.triggerConditions.onDeclareAttackers))
        
        elif step is gamesteps.Step.DECLARE_BLOCKERS:
            self.apply_to_battlefield(
                    lambda p: p.trigger(permanent.triggerConditions.onDeclareBlockers))
        
        elif step is gamesteps.Step.END_OF_COMBAT:
            self.apply_to_battlefield(
                    lambda p: p.trigger(permanent.triggerConditions.onEndofCombat))


        if step is gamesteps.Step.DECLARE_ATTACKERS:
            can_atk = []
            self.apply_to_battlefield(
                    lambda p: can_atk.append(p), 
                    lambda p: p.controller == self.current_player and p.can_attack())
            
            if can_atk:
                print("Creatures that can attack:", can_atk)

                for _player in self.players_list:
                    if _player == self.current_player:
                        continue
                    
                    ok = True
                    while ok:
                        # declare attackers
                        # space-separated list of indices of creatures in can_atk, starting at 0
                        answer = self.current_player.make_choice(
                                "\n{}, Choose all creatures you'd like to attack {} with\n"
                                .format(self.current_player, _player.name))

                        ## TODO: planeswalkers
                        answer = answer.split(" ")
                        try:
                            ok = False
                            for ind in answer:
                                ind = int(ind)
                                if ind < len(can_atk):
                                    can_atk[ind].attacks(_player)
                                    can_atk[ind].tap()
                                else:
                                    print("creature #{} is out of bounds\n"
                                            .format(str(ind)))
                        except:
                            print("wrong format: {}\n".format(ind))
                            ok = True

                for creature in can_atk:
                    print("{} is attacking {}\n".format(
                            creature.name(), creature.status.is_attacking))


                # check remove-from-combat abilities/events


        if step is gamesteps.Step.DECLARE_BLOCKERS:
            ## TODO: need to figure out which player's turn / priority

            for _player in self.players_list:
                if _player == self.current_player:  # only current player's opponents need to block
                    continue
                _is_attacking = []  # get all attacking creatures
                self.apply_to_battlefield(
                        lambda p: _is_attacking.append(p), 
                        lambda p: p.status.is_attacking == _player)

                if _is_attacking:
                    print("Creatures attacking {}: {}\n\n".format(_player, _is_attacking))

                    can_block = []
                    self.apply_to_battlefield(
                                lambda p: can_block.append(p), 
                                lambda p: p.controller == _player and p.can_block())
                
                    ## TODO: check blocking restrictions (e.g. flying)
                    print("Avaliable blockers: {}\n".format(can_block))


                    # declare blockers
                    if can_block:
                        for attacker in _is_attacking:

                            ok = True
                            while ok:
                                answer = _player.make_choice("\n{}, Choose all creatures you'd like to block {} with\n"
                                        .format(_player, attacker))

                                try:
                                    ## TODO: menace / multiple-blocking restrictions
                                    answer = map(int, answer.split(" "))
                                    for ind in answer:
                                        if ind < len(can_block):
                                            if can_block[ind].blocks(attacker):
                                                ok = False
                                            else:   # oops this blocking is illegal
                                                print("{} cannot block {}\n".format(can_block[ind], attacker))
                                        else:
                                            print("creature #{} is out of bounds\n".format(ind))
                                except:
                                    print("wrong format: {}\n".format(answer))
                                    ok = True
                        ## TODO: attacker declare multi-block dmg order
                        ## TODO: check for menace
                        pass

                    for creature in _is_attacking:
                        print("{} is attacking {}\n".format(
                            creature.name(), creature.status.is_attacking))


        if step is  gamesteps.Step.FIRST_STRIKE_COMBAT_DAMAGE:
            ## TODO: first strike
            self.apply_to_battlefield(
                    lambda p: p.deals_damage(p.status.is_attacking, p.characteristics.power), 
                    lambda p: p.status.is_attacking and (p.has_ability("First_Strike")
                                                 or p.has_ability("Double_Strike")))
            pass

        if step is gamesteps.Step.COMBAT_DAMAGE:
            _is_attacking = []
            self.apply_to_battlefield(
                    lambda p: _is_attacking.append(p), 
                    lambda p: p.status.is_attacking and (not p.has_ability("First_Strike")
                                                         or p.has_ability("Double_Strike")))

            for creature in _is_attacking:
                if isinstance(creature.status.is_attacking, player.Player):
                    creature.deals_damage(creature.status.is_attacking,
                            creature.characteristics.power)
                else:
                    combat.fight(creature, creature.status.is_attacking)

            # damage resolve / triggers

        if step is gamesteps.Step.END_OF_COMBAT:
            self.apply_to_battlefield(
                lambda p: p.exits_combat())


            pass


        self.handle_priority(step)





    def handle_end_phase(self, step):
        print(step)
        if step is gamesteps.Step.END:
            self.handle_priority(step)

        elif step is gamesteps.Step.CLEANUP:
            self.current_player.discard(self.current_player.hand.size()
                                     - self.current_player.maxHandSize)
            self.apply_to_battlefield(
                    lambda p: p.trigger(permanent.triggerConditions.onCleanup))


        


    def handle_turn(self):
        self.pending_steps = []
        for phase in gamesteps.Phase:
            self.pending_steps.extend(phase.steps)

        while self.pending_steps:
            self.step = self.pending_steps.pop(0)
            {
                gamesteps.Step.UNTAP: self.handle_beginning_phase,
                gamesteps.Step.UPKEEP: self.handle_beginning_phase,
                gamesteps.Step.DRAW: self.handle_beginning_phase,
                gamesteps.Step.PRECOMBAT_MAIN: self.handle_main_phase,
                gamesteps.Step.BEGINNING_OF_COMBAT: self.handle_combat_phase,
                gamesteps.Step.DECLARE_ATTACKERS: self.handle_combat_phase,
                gamesteps.Step.DECLARE_BLOCKERS: self.handle_combat_phase,
                gamesteps.Step.FIRST_STRIKE_COMBAT_DAMAGE: self.handle_combat_phase,
                gamesteps.Step.COMBAT_DAMAGE: self.handle_combat_phase,
                gamesteps.Step.END_OF_COMBAT: self.handle_combat_phase,
                gamesteps.Step.POSTCOMBAT_MAIN: self.handle_main_phase,
                gamesteps.Step.END: self.handle_end_phase,
                gamesteps.Step.CLEANUP: self.handle_end_phase
            }[self.step](self.step)
            for _player in self.players_list:
                _player.mana.clear()

        self.pending_turns.append(self.current_player)
        self.current_player = self.pending_turns.pop(0)  # cycles to next player's turn
        return True


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
        for _player in self.players_list:
            _player.print_player_state()


    # def __repr__(self):
    #     return self.print_game_state()


    ## TODO
    def set_up_game(self):
        print("setting up game...")
        for _player in self.players_list:
            _player.draw(7)
        self.pending_turns.extend(self.players_list)  # everyone gets a turn queued up, in order
        self.first_player_does_not_draw = True
        self.current_player = self.pending_turns.pop(0)


    def run_game(self):
        self.set_up_game()
        
        while self.num_players:
            try:
                self.handle_turn()
            except GameOverException:
                break






if __name__ == '__main__':
    decks = [cards.read_deck('cards/decks/deck1.txt'),
            cards.read_deck('cards/decks/deck1.txt')]
    GAME = Game(decks)
    GAME.run_game()
