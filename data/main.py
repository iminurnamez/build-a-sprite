from . import prepare,tools
from .states import gameplay

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"GAMEPLAY": gameplay.Gameplay()}
    controller.setup_states(states, "GAMEPLAY")
    controller.main()
