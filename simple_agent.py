from pysc2.agents import base_agent
from pysc2.lib import actions

import time

# definitions so keeping track is easier

# Functions

_BUILD_SUPPLY_DEPOT = actions.FUNCTIONS.Build_SupplyDepot_screen.id
_NO_OP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id

# Features

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit ID's

_TERRAN_COMMANDCENTER = 18
_TERRAN_SCV = 45

# Parameters

_PLAYER_SELF = 1
_SCREEN = [0]


class SimpleAgent(base_agent.BaseAgent):
    base_top_left = None # set as default befor step loop

    def step(self, obs):
        super(SimpleAgent, self).step(obs)

        time.sleep(0.2)

        return actions.FunctionCall(actions.FUNCTIONS.no_op.id, [])
