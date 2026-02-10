"""
Dependency Injection Container for VALEO-NeuroERP
Clean architecture dependency management using simple DI container
"""

from typing import Optional, Any, Dict, Type, TypeVar
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DependencyContainer:
    """
    Simple dependency injection container for clean architecture.
    Manages service lifecycles and dependencies.
    """

    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, callable] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}

    def register(self, interface: Type[T], implementation: Type[T], singleton: bool = True) -> None:
        """
        Register a service implementation.

        Args:
            interface: The interface/abstract class
            implementation: The concrete implementation
            singleton: Whether to create as singleton
        """
        if singleton:
            self._services[interface] = implementation
        else:
            self._factories[interface] = implementation

        logger.debug(f"Registered {implementation.__name__} for {interface.__name__}")

    def register_instance(self, interface: Type[T], instance: T) -> None:
        """
        Register a pre-created instance as singleton.

        Args:
            interface: The interface/abstract class
            instance: The instance to register
        """
        self._singletons[interface] = instance
        logger.debug(f"Registered instance {instance.__class__.__name__} for {interface.__name__}")

    def register_factory(self, interface: Type[T], factory: callable) -> None:
        """
        Register a factory function for creating instances.

        Args:
            interface: The interface/abstract class
            factory: Factory function that returns an instance
        """
        self._factories[interface] = factory
        logger.debug(f"Registered factory for {interface.__name__}")

    def resolve(self, interface: Type[T], scope: Optional[str] = None) -> T:
        """
        Resolve a service instance.

        Args:
            interface: The interface to resolve
            scope: Optional scope for scoped instances

        Returns:
            Instance of the requested interface

        Raises:
            ValueError: If interface is not registered
        """
        # Check scoped instances first
        if scope and scope in self._scoped_instances and interface in self._scoped_instances[scope]:
            return self._scoped_instances[scope][interface]

        # Check singletons
        if interface in self._singletons:
            return self._singletons[interface]

        # Check registered services
        if interface in self._services:
            impl_class = self._services[interface]
            instance = impl_class()
            self._singletons[interface] = instance
            logger.debug(f"Created singleton instance of {impl_class.__name__}")
            return instance

        # Check factories
        if interface in self._factories:
            factory = self._factories[interface]
            instance = factory()
            if scope:
                if scope not in self._scoped_instances:
                    self._scoped_instances[scope] = {}
                self._scoped_instances[scope][interface] = instance
            logger.debug(f"Created instance via factory for {interface.__name__}")
            return instance

        raise ValueError(f"No registration found for {interface.__name__}")

    def has_registration(self, interface: Type[T]) -> bool:
        """
        Check if an interface is registered.

        Args:
            interface: The interface to check

        Returns:
            True if registered, False otherwise
        """
        return (interface in self._services or
                interface in self._singletons or
                interface in self._factories)

    @contextmanager
    def scoped_container(self, scope: str):
        """
        Create a scoped container context.

        Args:
            scope: The scope name
        """
        if scope not in self._scoped_instances:
            self._scoped_instances[scope] = {}

        try:
            yield self
        finally:
            # Clean up scoped instances
            if scope in self._scoped_instances:
                del self._scoped_instances[scope]
                logger.debug(f"Cleaned up scope: {scope}")

    def clear(self) -> None:
        """Clear all registrations and instances."""
        self._services.clear()
        self._singletons.clear()
        self._factories.clear()
        self._scoped_instances.clear()
        logger.debug("Dependency container cleared")


# Global container instance
container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return container


def inject(interface: Type[T]) -> T:
    """
    Dependency injection decorator/helper.

    Args:
        interface: The interface to inject

    Returns:
        Instance of the interface
    """
    return container.resolve(interface)