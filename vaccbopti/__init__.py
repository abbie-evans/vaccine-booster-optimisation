# here note down all the functions that are included in the package
from .classes import BoosterAdmin
from .classes import InfectionCount
from .classes import InfectionForce
from .classes import Params
from .classes import Person
from .classes import Timesteps

# and include them in the file
__all__ = ["BoosterAdmin", "InfectionCount", "InfectionForce", "Params", "Person", "Timesteps"]
