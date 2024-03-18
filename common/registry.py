from typing import TypeVar, Generic, Dict, Union

T = TypeVar("T")  # Declare TypeVar for generic typing


class BaseRegistry(Generic[T]):

    def __init__(self) -> None:
        """
        Initializes a new BaseRegistry instance.

        Manages a dictionary of items.
        """
        self._registry: Dict[str, T] = {}

    def register(self, name: str, item: T) -> None:
        """
        Registers an item with a given name.

        Args:
            name (str): The name of the item.
            item (T): The item to register.
        """
        self._registry[name] = item

    def get(self, name: str) -> Union[T, None]:
        """
        Retrieves an item by its name.

        Args:
            name (str): The name of the item.

        Returns:
            Union[T, None]: The item if found, otherwise None.
        """
        return self._registry.get(name)

    def remove(self, name: str) -> None:
        """
        Removes an item from the registry by its name.

        Args:
            name (str): The name of the item to remove.
        """
        if name in self._registry:
            del self._registry[name]

    def __contains__(self, name: str) -> bool:
        """
        Checks if an item exists in the registry.

        Args:
            name (str): The name of the item.

        Returns:
            bool: True if the item exists, otherwise False.
        """
        return name in self._registry

    def __getitem__(self, name: str) -> Union[T, None]:
        """
        Gets an item by its name using indexing.

        Args:
            name (str): The name of the item.

        Returns:
            Union[T, None]: The item if found, otherwise None.
        """
        return self.get(name)

    def __delitem__(self, name: str) -> None:
        """
        Deletes an item from the registry by its name.

        Args:
            name (str): The name of the item to delete.
        """
        self.remove(name)

    def __len__(self) -> int:
        """
        Gets the number of items in the registry.

        Returns:
            int: The number of items in the registry.
        """
        return len(self._registry)

    def __iter__(self):
        """
        Iterates over the items in the registry.
        """
        return iter(self._registry.values())
