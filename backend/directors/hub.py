
from backend.ai.director_runner import run_director
from backend.directors.weather import WeatherDirector
from backend.directors.npc import NPCDirector
from backend.directors.traffic import TrafficDirector
from backend.directors.conversation import ConversationDirector

class DirectorHub:
    def __init__(self):
        self.weather = WeatherDirector()
        self.npc = NPCDirector()
        self.traffic = TrafficDirector()
        self.conversation = ConversationDirector()

    def propose_pulse(self, world_state, pulse_count):
        """Spread calls across pulses to keep local-model latency modest."""
        proposals = {}
        if pulse_count % 6 == 0:
            proposals["weather"] = run_director(self.weather, world_state)
        if pulse_count % 3 == 0:
            proposals["npc"] = run_director(self.npc, world_state)
        if pulse_count % 4 == 0:
            proposals["traffic"] = run_director(self.traffic, world_state)
        if pulse_count % 5 == 0:
            proposals["conversation"] = run_director(self.conversation, world_state)
        return {k: v for k, v in proposals.items() if v is not None}

hub = DirectorHub()
