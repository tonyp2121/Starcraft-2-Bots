#to run type python -m pysc2.bin.agent --map Simple64 --agent pysc2.agents.simple_agent.SimpleAgent<race> --agent_race <racehere>
# at least thats how it works for me on Windows

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

import time

# definitions so keeping track is easier
# this is for Terran only would have to change

# Functions

_BUILD_SUPPLY_DEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_BUILD_BARRACKS = actions.FUNCTIONS.Build_Barracks_screen.id
_BUILD_PYLON = actions.FUNCTIONS.Build_Pylon_screen.id
_BUILD_GATEWAY = actions.FUNCTIONS.Build_Gateway_screen.id
_NO_OP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_ATTACK_MINIMAP = actions.FUNCTIONS.Attack_minimap.id
_TRAIN_MARINES = actions.FUNCTIONS.Train_Marine_quick.id
_RALLY_UNITS_MINIMAP = actions.FUNCTIONS.Rally_Units_minimap.id


# Features

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit ID's

_TERRAN_COMMANDCENTER = 18
_TERRAN_SUPPLYDEPOT = 19
_TERRAN_SCV = 45
_TERRAN_BARRACKS = 21
_PROTOSS_PROBE = 84
_PROTOSS_GATEWAY = 62
_PROTOSS_PYLON = 60
_PROTOSS_NEXUS = 59

# Parameters

_SUPPLY_USED = 3
_SUPPLY_MAX = 4
_PLAYER_SELF = 1
_MINIMAP = [1]
_QUEUED = [1]
_SCREEN = [0]
_NOADD = [0]

class SimpleAgentTerran(base_agent.BaseAgent):
    base_top_left = None # set as default before step loop
    supply_depot_built = False
    barracks_built = False
    barracks_selected = False
    barracks_rallied = False
    scv_selected = False
    army_selected = False
    army_rallied = False

    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        return [x + x_distance, y + y_distance]

    def step(self, obs):
        super(SimpleAgentTerran, self).step(obs)

        if   self.base_top_left is None:
            player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
            self.base_top_left = player_y.mean() <= 31

        if not self.supply_depot_built:
            if not self.scv_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_SCV).nonzero()

                target = [unit_x[0], unit_y[0]]

                self.scv_selected = True

                return actions.FunctionCall(_SELECT_POINT, [_SCREEN, target]) #clicks on the SCV
            elif _BUILD_SUPPLY_DEPOT in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

                self.supply_depot_built = True

                return actions.FunctionCall(_BUILD_SUPPLY_DEPOT, [_SCREEN, target])

        if not self.barracks_built:
            if _BUILD_BARRACKS in obs.observation["available_actions"]:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_COMMANDCENTER).nonzero()

                target = self.transformLocation(int(unit_x.mean()), 20, int(unit_y.mean()), 0)

                self.barracks_built = True

                return actions.FunctionCall(_BUILD_BARRACKS, [_SCREEN, target])

        elif not self.barracks_rallied:
            if not self.barracks_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _TERRAN_BARRACKS).nonzero()

                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]

                    self.barracks_selected = True

                    return actions.FunctionCall(_SELECT_POINT, [_SCREEN, target])
            else:
                self.barracks_rallied = True

                if self.base_top_left:
                    return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_MINIMAP, [29, 21]])

                return actions.FunctionCall(_RALLY_UNITS_MINIMAP, [_MINIMAP, [29, 46]])
        elif obs.observation["player"][_SUPPLY_USED] < obs.observation["player"][_SUPPLY_MAX] and _TRAIN_MARINES in obs.observation["available_actions"]:
            return actions.FunctionCall(_TRAIN_MARINES, [_QUEUED])

        elif not self.army_rallied:
            if not self.army_selected:
                if _SELECT_ARMY in obs.observation["available_actions"]:
                    self.army_selected = True
                    self.barracks_selected = False

                    return actions.FunctionCall(_SELECT_ARMY, [[0]])
            elif _ATTACK_MINIMAP in obs.observation["available_actions"]:
                self.army_rallied = True
                self.army_selected = False

                if self.base_top_left:
                    return actions.FunctionCall(_ATTACK_MINIMAP, [[1], [39,45]])
                return actions.FunctionCall(_ATTACK_MINIMAP, [[1], [21,24]])


        return actions.FunctionCall(_NO_OP, [])

class SimpleAgentProtoss(base_agent.BaseAgent):
    base_top_left = None
    pylon_built = False
    gateway_built = False
    gateway_selected = False
    probe_selected = False
    counter_for_apm = 0
    build_gateway_attempts = 0

    def transformLocation(self, x, x_distance, y, y_distance):
        if not self.base_top_left:
            return [x - x_distance, y - y_distance]
        return [x + x_distance, y + y_distance]

    def step(self, obs):
        super(SimpleAgentProtoss, self).step(obs)
        time.sleep(.5)
        if self.counter_for_apm == 5:   # This is to make sure its not cheating according to deepmind this should be about
            self.counter_for_apm = 0    # 200 apm (actions per minute) which is on par with pros and advanced players.
            if self.base_top_left is None:
                player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
                self.base_top_left = player_y.mean() <= 31

            if not self.pylon_built:
                if not self.probe_selected:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _PROTOSS_PROBE).nonzero()

                    target = [unit_x[0], unit_y[0]]

                    self.probe_selected = True

                    return actions.FunctionCall (_SELECT_POINT, [_SCREEN, target])
                elif _BUILD_PYLON in obs.observation ["available_actions"]:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _PROTOSS_NEXUS).nonzero()

                    target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

                    self.pylon_built = True

                    return actions.FunctionCall(_BUILD_PYLON, [_SCREEN, target])
                    self.counter_for_apm = 0;

            if not self.gateway_built:
                if _BUILD_GATEWAY in obs.observation["available_actions"]:
                    unit_type = obs.observation["screen"][_UNIT_TYPE]
                    unit_y, unit_x = (unit_type == _PROTOSS_PYLON).nonzero()

                    target = self.transformLocation(int(unit_x.mean()), 10, int(unit_y.mean()), 0)
                    if self.build_gateway_attempts > 3:
                        self.gateway_built = True
                    self.build_gateway_attempts += 1
                    return actions.FunctionCall(_BUILD_GATEWAY, [_SCREEN, target])

            if not self.gateway_selected:
                unit_type = obs.observation["screen"][_UNIT_TYPE]
                unit_y, unit_x = (unit_type == _PROTOSS_GATEWAY).nonzero()

                if unit_y.any():
                    target = [int(unit_x.mean()), int(unit_y.mean())]

                    self.gateway_selected = True

                    return actions.FunctionCall(_SELECT_POINT, [_SCREEN, target])

            return actions.FunctionCall(_NO_OP, [])
        else:
            self.counter_for_apm += 1
            return actions.FunctionCall(_NO_OP, [])

        #   if not self.gateway_selected:




        return actions.FunctionCall(_NO_OP, [])
