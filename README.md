# Structural Analysis Tool for Load Distribution In The Plane

This project provides a tool for structural analysis using the `horloadist` library. You can define a 2D-polygon in x-y space representing a plate and some supports with their bending stiffnesses around the x and y axes.

## Prerequisites

- Python 3.x
- `horloadist` library

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/LuMaul/hor_load_dist.git
   ```

## Usage

The main script demonstrates how to use the `horloadist` library to create a structural model and solve it. Here's a brief overview of the process:

1. Import necessary classes from `horloadist`:
   ```python
   from horloadist import SupportNode, Polygon, Stucture, LinSolve
   ```

2. Define helper functions for moment of inertia calculations:
   ```python
   def globalIy(dx, dy):
       # ...

   def globalIx(dx, dy):
       # ...
   ```

3. Create support nodes using the `SupportNode` class.

4. Define the structure's shape using the `Polygon` class.

5. Create a `Stucture` object with the defined polygon and support nodes.

6. Solve the structure using `LinSolve`.

7. Print the results.

## Example

The provided example creates a plate structure with seven support nodes and solves it for a specific load case.

```python
# Create support nodes
w1 = SupportNode(1, -10.0, -2.5, globalIx(5, 0.3), globalIy(5, 0.3))
# ... (other nodes)

# Define the plate
plate = Polygon([[-12.5, -7.5], [-12.5, 7.5], [12.5, 7.5], [12.5, -7.5]])

# Create and solve the structure
struc = Stucture(plate, [w1, w2, w3, w4, w5, w6, w7])
sol = LinSolve(struc, 0, 1)

# Print results
struc.printTable()
sol.printTable()
```

## Caution

As noted in the code comments:

> Caution! Do not blindly trust this calculation, but always check the plausibility of the results.

It's important to verify the results and ensure they make sense for your specific use case.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.