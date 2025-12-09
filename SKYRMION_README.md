# Skyrmion Manifold Data Transmission Simulator

A sophisticated finite-difference solver for simulating chiral magnetic thin films with skyrmion configurations that encode data from 2D manifolds. This project implements the Landau-Lifshitz-Gilbert (LLG) equation with full micromagnetic energy density.

## Overview

**Physics Model:**
- **Micromagnetic Energy:**
  - Exchange interaction: $E_{ex} = A \int (\nabla \mathbf{m})^2 d\mathbf{r}$
  - Dzyaloshinskii-Moriya interaction: $E_{DMI} = D \int \mathbf{m} \cdot (\nabla \times \mathbf{m}) d\mathbf{r}$
  - Perpendicular anisotropy: $E_K = -K_z \int m_z^2 d\mathbf{r}$
  - Zeeman field: $E_Z = -\mu_0 M_s B_z \int m_z d\mathbf{r}$

- **LLG Dynamics:**
$$\frac{d\mathbf{m}}{dt} = -\frac{\gamma}{1+\alpha^2}[\mathbf{m} \times \mathbf{H}_{eff} + \alpha \mathbf{m} \times (\mathbf{m} \times \mathbf{H}_{eff})]$$

- **Data Encoding:**
  Spatially modulated anisotropy: $K_z(x,y) = K_0 + \varepsilon \cdot D(x,y)$

## Project Structure

```
skyrmion_simulator.py          # Main simulator engine with LLG solver
skyrmion_analysis.py           # Analysis tools and skyrmion detection
skyrmion_examples.py           # Comprehensive usage examples
README.md                      # This file
requirements.txt               # Python dependencies
```

## Key Features

### 1. **Full Micromagnetic Solver**
- Finite-difference implementation of exchange, DMI, anisotropy, and Zeeman energies
- Time-stepping via Euler or RK2 scheme
- Automatic magnetization normalization
- Periodic boundary conditions

### 2. **Data Encoding**
- Input manifolds (2D arrays/images) can be encoded into skyrmion configurations
- Spatially modulated anisotropy creates position-dependent skyrmion nucleation
- Supports multiple data patterns (Gaussian bumps, sinusoids, checkerboard, random)

### 3. **Advanced Analysis**
- **Skyrmion Detection:** Topological charge-based identification
- **Correlation Analysis:** Quantify data encoding fidelity
- **Energy Tracking:** Monitor system relaxation
- **Channel Capacity:** Estimate information content
- **Spin Texture Entropy:** Characterize magnetic order

### 4. **Visualization**
- Real-time energy evolution plots
- Magnetization field maps
- Skyrmion center detection overlay
- Data-magnetization correlation analysis
- Comprehensive multi-panel analysis plots

## Installation

### Prerequisites
- Python 3.8+
- NumPy
- SciPy
- Matplotlib
- scikit-learn

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Or individually:
pip install numpy scipy matplotlib scikit-learn
```

## Quick Start

### Run the Main Simulator

```python
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams, create_sample_manifold
import numpy as np

# Configure parameters
params = MicromagneticParams(
    grid_size=256,
    dt=5e-13,
    num_steps=30000,
    alpha=0.3,
    eps_K=0.2,
)

# Create data manifold
data_field = create_sample_manifold(size=256, pattern='gaussian_bumps')

# Initialize simulator
simulator = SkyrmionSimulator(params, data_field=data_field)

# Run simulation
simulator.run(verbose=True)

# Get results
m_z = simulator.get_m_z()
energy_history = simulator.get_energy_history()
```

### Analyze Results

```python
from skyrmion_analysis import SkyrmionAnalyzer, DataEncodingDecoder

analyzer = SkyrmionAnalyzer()
decoder = DataEncodingDecoder()

# Detect skyrmions
skyrmion_info = analyzer.detect_skyrmions(m_z, threshold=0.3)
print(f"Detected {skyrmion_info['count']} skyrmions")

# Check encoding fidelity
correlation = analyzer.extract_manifold_signature(m_z, data_field)
print(f"Data-magnetization correlation: {correlation:.4f}")

# Estimate channel capacity
capacity = decoder.compute_channel_capacity(m_z)
print(f"Channel capacity: {capacity:.1f} bits")

# Compute topological properties
topological_charge = analyzer.compute_topological_charge(
    simulator.get_magnetization()[:,:,0],
    simulator.get_magnetization()[:,:,1],
    simulator.get_magnetization()[:,:,2]
)
```

### Visualize

```python
from skyrmion_simulator import visualize_results, save_results
from pathlib import Path

# Comprehensive visualization
visualize_results(simulator, save_dir='outputs/results')

# Save all data
save_results(simulator, Path('outputs/results'))
```

## Running Examples

Four comprehensive examples are provided:

### Example 1: Basic Skyrmion Creation
```bash
python skyrmion_examples.py
```
Demonstrates basic skyrmion formation without data modulation.

### Example 2: Data Encoding with Multiple Patterns
Creates skyrmions encoded with different manifold patterns:
- Gaussian bumps
- Sinusoidal patterns
- Checkerboard patterns

Analyzes encoding fidelity (correlation) and channel capacity.

### Example 3: Parameter Sensitivity
Tests sensitivity to:
- DMI constant strength
- Anisotropy modulation coefficient
Generates sensitivity analysis plots.

### Example 4: High-Resolution Encoding
Full 256×256 simulation with detailed analysis:
- Skyrmion detection and counting
- Data-magnetization correlation
- Spin texture entropy
- Channel capacity estimation

## Key Parameters

### Physical Parameters

| Parameter | Symbol | Default | Unit | Description |
|-----------|--------|---------|------|-------------|
| Exchange Stiffness | A | 15e-12 | J/m | Controls domain wall width |
| DMI Constant | D | 4e-3 | J/m² | Enables skyrmion stabilization |
| Base Anisotropy | K_z | 0.8e6 | J/m³ | Favors perpendicular magnetization |
| Anisotropy Modulation | ε | 0.2 | — | Data encoding strength |
| External Field | B_z | -0.01 | T | Slightly negative favors skyrmions |
| Gilbert Damping | α | 0.3 | — | Dissipation; higher = faster relaxation |
| Saturation Magnetization | M_s | 4e5 | A/m | Material property |

### Simulation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Grid Size | 256 | N×N grid points |
| Cell Size | 1.0 | nm per grid point |
| Time Step | 5e-13 | seconds (Euler scheme) |
| Total Steps | 30000 | Simulation duration |
| Save Interval | 500 | Save every N steps |

### Tuning for Skyrmion Formation

For good skyrmion formation:
1. **DMI Strength:** D ≈ 3-5 mJ/m² (stabilizes skyrmions)
2. **Anisotropy:** K_z positive (favors perpendicular magnetization)
3. **External Field:** B_z slightly negative (−0.01 to −0.05 T)
4. **Damping:** α ≈ 0.3-0.5 (faster convergence, α > 0.5 needed for stability)

For best data encoding:
1. **Modulation Strength:** ε ≈ 0.1-0.3 (balance between encoding and skyrmion stability)
2. **Grid Resolution:** ≥ 128×128 (finer grids capture details)
3. **Simulation Time:** Allow sufficient relaxation (typically 20k-40k steps)

## Output Files

When running simulations, the following files are saved to `outputs/`:

```
skyrmion_results/
├── magnetization_field.npy       # Full 3D magnetization field
├── m_z_final.npy                # Out-of-plane component
├── data_field.npy               # Input data manifold
├── K_z_map.npy                  # Modulated anisotropy map
├── energy_history.npy           # Energy evolution
├── parameters.json              # Simulation parameters
└── skyrmion_analysis.png        # Comprehensive analysis figure
```

## Physics Validation

The implementation includes several validation checks:

1. **Energy Conservation:** Total energy should converge monotonically during relaxation
2. **Magnetization Normalization:** $|\mathbf{m}| = 1$ enforced at each step
3. **Topological Charge:** Skyrmions have non-zero, quantized topological charge
4. **Equilibrium State:** Energy plateau indicates system has relaxed

## Performance Notes

- **Grid Size Impact:** Computation scales as $O(N^2)$ per step
  - 128×128: ~1 sec/1000 steps
  - 256×256: ~4 sec/1000 steps
  - 512×512: ~16 sec/1000 steps

- **Optimization Tips:**
  1. Reduce grid size for parameter exploration
  2. Use smaller time steps (dt) for finer temporal resolution
  3. Increase Gilbert damping (α) for faster convergence
  4. Reduce number of steps when testing new parameters

## Advanced Usage

### Custom Data Fields

```python
import numpy as np
from PIL import Image

# Load from image
img = Image.open('my_image.png').convert('L')
data = np.array(img, dtype=float) / 255.0
data = 2 * data - 1  # Normalize to [-1, 1]

# Use in simulation
simulator = SkyrmionSimulator(params, data_field=data)
```

### Parameter Sweeps

```python
from pathlib import Path

results = []
for eps in [0.1, 0.2, 0.3, 0.4]:
    for D in [2e-3, 4e-3, 6e-3]:
        params = MicromagneticParams(eps_K=eps, D=D)
        simulator = SkyrmionSimulator(params, data_field=data)
        simulator.run(verbose=False)
        
        m_z = simulator.get_m_z()
        correlation = SkyrmionAnalyzer.extract_manifold_signature(m_z, data)
        results.append({'eps': eps, 'D': D, 'correlation': correlation})
```

### Skyrmion Tracking

```python
# Run simulation and save intermediate states
for step_idx in range(10000):
    simulator.step()
    if step_idx % 1000 == 0:
        m_z = simulator.get_m_z()
        skyrmion_info = analyzer.detect_skyrmions(m_z)
        print(f"Step {step_idx}: {skyrmion_info['count']} skyrmions")
```

## Troubleshooting

### Issue: No Skyrmions Form
- **Solution:** Check DMI strength (D) is large enough (~4 mJ/m²)
- **Solution:** Ensure external field B_z is negative
- **Solution:** Increase simulation time (more steps)
- **Solution:** Check anisotropy K_z is positive and sufficiently large

### Issue: Energy Not Converging
- **Solution:** Reduce time step (dt) for better stability
- **Solution:** Increase damping coefficient (α)
- **Solution:** Check parameter values for physical consistency

### Issue: Poor Data Encoding
- **Solution:** Increase modulation strength (ε)
- **Solution:** Use finer grid resolution
- **Solution:** Allow more relaxation time
- **Solution:** Check data field range is [-1, 1]

## References

1. Rohart, S., & Thiaville, A. (2013). Skyrmion confinement in ultrathin film structures.
2. Moreau-Luchaire, C., et al. (2016). Additive interfacial chiral interaction in multilayers.
3. Büttner, F., et al. (2018). Magnetic skyrmions: from fundamental to applications.

## Citation

If you use this simulator in your research, please cite:

```bibtex
@software{skyrmion_simulator_2024,
  title={Skyrmion Manifold Data Transmission Simulator},
  author={Your Name},
  year={2024},
  url={https://your-repository-url}
}
```

## License

This project is provided as-is for research and educational purposes.

## Contact & Support

For questions, issues, or contributions, please refer to the project documentation or contact the maintainer.

---

## Changelog

### v1.0.0 (2024)
- Initial release with full LLG solver
- Micromagnetic energy implementation
- Data encoding and analysis tools
- Comprehensive examples and documentation
