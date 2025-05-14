from .models import Looks

class LookStrategy:
    """
    Абстрактный базовый класс для стратегий выбора образа.
    """

    def get_look(self, **kwargs):
        """
        Метод для получения образа по заданным параметрам.

        Args:
            **kwargs: Ключевые параметры для выбора образа.

        Raises:
            NotImplementedError: Если метод не переопределён в подклассе.
        """
        raise NotImplementedError


class TemperatureLookStrategy(LookStrategy):
    """
    Стратегия выбора образа на основе температуры.
    """

    def get_look(self, **kwargs):
        """
        Возвращает образ, подходящий для указанной температуры.

        Args:
            temperature (float or int): Температура для выбора образа.

        Returns:
            Looks: Объект образа, подходящий под заданную температуру.
        """
        temperature = kwargs.get("temperature")
        return Looks.get_for_temperature(temperature)


class LookFactory:
    """
    Фабрика для получения стратегии выбора образа по заданному критерию.
    """

    @staticmethod
    def get_strategy(criteria: str):
        """
        Возвращает объект стратегии в зависимости от критерия.

        Args:
            criteria (str): Критерий выбора стратегии (например, "temperature").

        Returns:
            LookStrategy: Экземпляр соответствующей стратегии.

        Raises:
            ValueError: Если критерий неизвестен.
        """
        if criteria == "temperature":
            return TemperatureLookStrategy()
        raise ValueError(f"Unknown criteria: {criteria}")
