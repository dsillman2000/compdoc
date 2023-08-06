# VectorTest

---

Test module description!

# Classes

- **`Vec2`**: 2-dimensional vector struct, represented as a named tuple.
  - _Base(s)_: NamedTuple

Comes with a helpful function for vector magnitude:


- `norm : (self) -> float`
  - Computes the L2 norm of the vector.
  - **Returns**:
    - `float`: Norm of this vector

- **`Vec3`**: 3-dimensional vector struct, represented as a named tuple.
  - _Base(s)_: NamedTuple

- **`VecN`**: N-dimensional vector struct, represented as a named tuple.
  - _Base(s)_: NamedTuple

Comes with classmethod constructors for using iterables of floats to pack a VecN:


- `from_list : (cls, xs: list[float]) -> VecN`
  - Constructs a VecN from a list of floats.
  - **Args**:
    - `xs (list[float])` : Components of the n-dimensional vector
  - **Returns**:
    - `VecN`: The n-dimensional vector

<br />


- `from_components : (cls, *components: float) -> VecN`
  - Constructs a VecN from however many floating point components are provided.
  - **Returns**:
    - `VecN`: A new n-dimensional vector with the specified components

# Standalone functions

We supply just one function which flattens a list of arbitrary N-dimensional vectors into a single,
concatenated, N-dimensional vector.


- `flatten_vecs : (vecs: list[VecN]) -> VecN`
  - Flattens a provided list of vectors into a single vector.
  - **Args**:
    - `vecs (list[VecN])` : Vectors to flatten
  - **Returns**:
    - `VecN`: Flattened vector result

# Acknowledgements

Author:

- Firstname Lastname