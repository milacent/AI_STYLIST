from .models import Looks
class LookStrategy:
    def get_look(self, **kwargs):
        raise NotImplementedError

class TemperatureLookStrategy(LookStrategy):
    def get_look(self, **kwargs):
        temperature = kwargs.get("temperature")
        return Looks.get_for_temperature(temperature)

class LookFactory:
    @staticmethod
    def get_strategy(criteria: str):
        if criteria == "temperature":
            return TemperatureLookStrategy()
        raise ValueError(f"Unknown criteria: {criteria}")