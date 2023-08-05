import functools
import math
import operator
from typing import Generic, NamedTuple, SupportsInt, TypeVar


class Vec2(NamedTuple):
    """2-dimensional vector struct, represented as a named tuple.
    """
    x: float
    y: float

    def norm(self) -> float:
        """Computes the L2 norm of the vector.

        Returns:
            float: Norm of this vector
        """        
        return math.sqrt(self.x * self.x + self.y * self.y)
    

class Vec3(NamedTuple):
    """3-dimensional vector struct, represented as a named tuple.
    """    
    x: float
    y: float
    z: float

    def norm(self) -> float:
        """Computes the L2 norm of the vector.

        Returns:
            float: Norm of this vector
        """        
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    

class VecN(NamedTuple):
    """N-dimensional vector struct, represented as a named tuple.
    """    
    n: int
    components: tuple[float, ...]

    @classmethod
    def from_components(cls, *components: float) -> "VecN":
        """Constructs a VecN from however many floating point components are provided.

        Returns:
            VecN: A new n-dimensional vector with the specified components
        """        
        return cls(len(components), components)
    
    @classmethod
    def from_list(cls, xs: list[float]) -> "VecN":
        """Constructs a VecN from a list of floats.

        Args:
            xs (list[float]): Components of the n-dimensional vector

        Returns:
            VecN: The n-dimensional vector
        """        
        return cls.from_components(*xs)

    def norm(self) -> float:
        """Computes the L2 norm of the vector.

        Returns:
            float: Norm of this vector
        """        
        return math.sqrt(
            functools.reduce(
                operator.add,
                map(lambda xi: xi * xi, self.components),
                0.0,
            )
        )
    
def flatten_vecs(vecs: list[VecN]) -> VecN:
    """Flattens a provided list of vectors into a single vector.

    Args:
        vecs (list[VecN]): Vectors to flatten

    Returns:
        VecN: Flattened vector result
    """    
    return VecN.from_list(list(functools.reduce(operator.add, [v.components for v in vecs], ())))