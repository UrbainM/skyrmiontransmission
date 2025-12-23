# skyrmiontransmission
A scientific framework for exploring skyrmion time evolutions in context of data transmission

"""
SKYRMION MANIFOLD DATA TRANSMISSION SIMULATOR
Project Summary and Usage Guide

Version: 1.0.0
Date: December 2024
"""
![til](/outputs/skyrmion_evolution.gif)

import sys
from pathlib import Path

# ============================================================================
# PROJECT OVERVIEW
# ============================================================================

PROJECT_SUMMARY = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          SKYRMION MANIFOLD DATA TRANSMISSION SIMULATOR                     ║
║                                                                            ║
║  A sophisticated finite-difference solver for simulating chiral magnetic  ║
║  thin films with skyrmion configurations that encode data from 2D         ║
║  manifolds using spatially modulated magnetic anisotropy.                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

PROJECT HIGHLIGHTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Full Micromagnetic Solver
  - Exchange interaction (controls domain wall width)
  - Dzyaloshinskii-Moriya interaction (essential for skyrmions)
  - Perpendicular magnetic anisotropy (fixes out-of-plane orientation)
  - Zeeman field energy (external magnetic field)

✓ Landau-Lifshitz-Gilbert Dynamics
  - Time-stepping via Euler or RK2 schemes
  - Adaptive magnetization normalization
  - Periodic boundary conditions for infinite films

✓ Data Encoding
  - Input 2D manifolds (images, patterns) encoded as K_z(x,y) modulation
  - Skyrmion positions/sizes correlated with input data
  - Fidelity quantified via data-magnetization correlation

✓ Advanced Analysis Tools
  - Skyrmion detection via topological charge
  - Data encoding fidelity assessment
  - Channel capacity estimation
  - Energy evolution monitoring
  - Spin texture entropy computation

✓ Comprehensive Visualization
  - Magnetization field maps
  - Energy convergence plots
  - Skyrmion center overlays
  - Data-magnetization correlation analysis
  - 6-panel comprehensive analysis plots

✓ Pre-configured Parameter Sets
  - QUICK_TEST (5 min, 64×64 grid)
  - STANDARD (30 min, 128×128 grid)
  - HIGH_RESOLUTION (4 hours, 256×256 grid)
  - Plus specialized configs for specific scenarios


PHYSICS MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Micromagnetic Energy:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  E_total = E_exchange + E_DMI + E_anisotropy + E_Zeeman               │
│                                                                         │
│  E_ex = A ∫ (∇m)² dr                    [Exchange]                     │
│  E_DMI = D ∫ m·(∇×m) dr                [Chirality]                     │
│  E_k = -K_z ∫ m_z² dr                  [Perpendicular anisotropy]     │
│  E_z = -μ₀ M_s B_z ∫ m_z dr           [External field]               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Landau-Lifshitz-Gilbert Equation:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  dm/dt = -γ/(1+α²) [m × H_eff + α m × (m × H_eff)]                  │
│                                                                         │
│  where:                                                                 │
│    γ = 1.76×10¹¹ rad/(T·s)  [Gyromagnetic ratio]                      │
│    α = damping coefficient   [Dissipation]                             │
│    H_eff = effective field   [All contributions]                       │
│    |m| = 1                   [Unit magnetization]                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Data Encoding:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  K_z(x,y) = K_0 + ε·D(x,y)                                            │
│                                                                         │
│  where:                                                                 │
│    K_0 = base anisotropy constant                                      │
│    ε = modulation strength parameter                                   │
│    D(x,y) = input data field (manifold) ∈ [-1, 1]                    │
│                                                                         │
│  Result: Spatially modulated skyrmion configurations encode data       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


FILES AND MODULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 skyrmion_simulator.py  [MAIN ENGINE - ~600 lines]
   ├─ MicromagneticParams: Configuration dataclass
   ├─ SkyrmionSimulator: Main solver class
   │  ├─ Micromagnetic field calculations
   │  ├─ LLG time-stepping
   │  ├─ Energy computation
   │  └─ Energy history tracking
   ├─ create_sample_manifold(): Pattern generation
   ├─ visualize_results(): 6-panel analysis
   └─ save_results(): Data export

📄 skyrmion_analysis.py  [ANALYSIS TOOLKIT - ~400 lines]
   ├─ SkyrmionAnalyzer: Detection and characterization
   │  ├─ detect_skyrmions(): Topological identification
   │  ├─ compute_topological_charge(): Local Q(x,y)
   │  ├─ extract_manifold_signature(): Correlation
   │  └─ compute_spin_texture_entropy(): Order parameter
   ├─ DataEncodingDecoder: Encode/decode operations
   │  ├─ encode_to_magnetization(): Binary encoding
   │  ├─ decode_from_magnetization(): Quantization
   │  └─ compute_channel_capacity(): Information theory
   └─ Visualization: plot_skyrmion_detection(), plot_energy_landscape()

📄 skyrmion_examples.py  [DEMONSTRATIONS - ~350 lines]
   ├─ example_1_basic_skyrmion_creation()
   ├─ example_2_data_encoding()
   ├─ example_3_parameter_sensitivity()
   └─ example_4_high_resolution_encoding()

📄 skyrmion_config.py  [CONFIGURATION GUIDE - ~400 lines]
   ├─ ConfigurationLibrary: 9 pre-configured setups
   ├─ PARAMETER_GUIDANCE: Detailed parameter reference
   ├─ MATERIALS: Real material properties
   ├─ QUICK_START_GUIDE: Quick reference table
   └─ TROUBLESHOOTING: Common issues & solutions

📄 SKYRMION_README.md  [DOCUMENTATION - ~400 lines]
   └─ Complete reference guide


QUICK START (5 MINUTES)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. INSTALL DEPENDENCIES:
   pip install numpy scipy matplotlib scikit-learn

2. RUN EXAMPLES:
   python skyrmion_examples.py

3. INTERPRET RESULTS:
   - Outputs saved to outputs/ directory
   - See outputs/skyrmion_results/skyrmion_analysis.png
   - Check outputs/example_*.png for comparative analysis

4. BASIC USAGE:
   
   from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
   from skyrmion_config import ConfigurationLibrary
   
   # Use pre-configured params
   params = ConfigurationLibrary.STANDARD
   
   # Create simulator
   simulator = SkyrmionSimulator(params)
   
   # Run
   simulator.run(verbose=True)
   
   # Analyze
   from skyrmion_analysis import SkyrmionAnalyzer
   analyzer = SkyrmionAnalyzer()
   skyrmion_info = analyzer.detect_skyrmions(simulator.get_m_z())
   print(f"Found {skyrmion_info['count']} skyrmions")


TYPICAL WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: CHOOSE CONFIGURATION
       ↓
       Use QUICK_TEST to explore parameters (5 min)
       ↓
       Use STANDARD for standard simulations (30 min)
       ↓
       Use HIGH_RESOLUTION for detailed work (4 hours)

Step 2: CREATE DATA MANIFOLD
       ↓
       Use built-in patterns (Gaussian, sinusoid, checkerboard)
       OR load from image: np.array(PIL.Image.open(...))
       OR create custom: custom_function(x, y)
       
Step 3: INITIALIZE & RUN
       ↓
       params = ConfigurationLibrary.STANDARD
       simulator = SkyrmionSimulator(params, data_field=my_data)
       simulator.run(verbose=True)

Step 4: ANALYZE
       ↓
       m_z = simulator.get_m_z()
       skyrmion_info = analyzer.detect_skyrmions(m_z)
       correlation = analyzer.extract_manifold_signature(m_z, data_field)
       capacity = decoder.compute_channel_capacity(m_z)

Step 5: VISUALIZE & SAVE
       ↓
       visualize_results(simulator, save_dir='outputs/')
       save_results(simulator, Path('outputs/'))


KEY PARAMETERS TO TUNE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For Skyrmion Formation:
  • D (DMI): 4-6 mJ/m²         [Stronger → more skyrmions]
  • K_z: 0.8-1.2 MJ/m³         [Stronger → more compact]
  • B_z: -0.01 to -0.05 T      [More negative → favors skyrmions]
  • α: 0.3-0.5                 [Higher → faster convergence]

For Data Encoding:
  • eps_K: 0.1-0.3             [Strength of modulation]
  • grid_size: 128-256         [Finer → more detail]
  • num_steps: 20k-40k         [More → better relaxation]

For Speed:
  • grid_size: Reduce to 64    [4× speedup]
  • α: Increase to 0.6         [2× speedup, less underdamped]
  • dt: Increase 2-5×          [Risky, watch for divergence]


COMPUTATIONAL REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration      Grid Size    Memory        Time (30k steps)  Typical Use
──────────────────────────────────────────────────────────────────────────
QUICK_TEST         64×64        10 MB         5 min             Parameter testing
STANDARD           128×128      40 MB         30 min            Standard work
HIGH_RESOLUTION    256×256      150 MB        4 hours           Publication
ULTRA_HIGH_RES     512×512      600 MB        8+ hours          Research


TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ No skyrmions form
   → D might be too weak (try 5-6 mJ/m²)
   → B_z sign wrong (should be negative)
   → Increase |B_z| to -0.02 or -0.03
   → Allow more time (50k+ steps)

❌ Energy diverges
   → Time step too large (reduce dt by 2×)
   → Increase damping (α to 0.5)
   → Use finer grid (256×256)

❌ Poor data encoding
   → Modulation too weak (increase eps_K)
   → Grid too coarse (try 256×256)
   → Insufficient relaxation (30k+ steps)

❌ Slow performance
   → Use FAST_RELAXATION config (higher α)
   → Reduce grid_size for testing
   → Break into smaller simulations


PHYSICS VALIDATION CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Energy convergence: Should reach plateau monotonically
✓ Magnetization norm: |m| = 1 enforced everywhere
✓ Skyrmion statistics: Reasonable sizes and distributions
✓ Topological charge: Q ≈ integer (±1, ±2, etc.)
✓ Data correlation: Should increase with eps_K
✓ Parameter trends: Physical behavior with parameter changes


EXAMPLE COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Run all examples
python skyrmion_examples.py

# Run specific example
# (Modify skyrmion_examples.py to comment out others)

# View configuration guide
python skyrmion_config.py

# Generate quick test
python -c "
from skyrmion_simulator import SkyrmionSimulator
from skyrmion_config import ConfigurationLibrary
sim = SkyrmionSimulator(ConfigurationLibrary.QUICK_TEST)
sim.run()
print(f'Skyrmions: {len(sim.energy_history)} saved states')
"

# Custom simulation
python -c "
import numpy as np
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams

params = MicromagneticParams(grid_size=128, num_steps=10000)
data = np.random.randn(128, 128)
sim = SkyrmionSimulator(params, data_field=data)
sim.run(verbose=False)
print(f'Final m_z mean: {sim.get_m_z().mean():.3f}')
"


NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Run example_1 to understand basic skyrmion formation
2. Try example_2 with different data patterns (gaussian, sinusoid, etc.)
3. Use example_3 to understand parameter sensitivity
4. Modify parameters based on insights
5. Run full HIGH_RESOLUTION simulation for your specific application
6. Analyze results using skyrmion_analysis tools
7. Publish results! 📊


REFERENCES & CITATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Key Papers:
  • Magnetic Skyrmions: Überblick
    A. Fert, N. Reyren, V. Cros (Nature Rev. Materials, 2017)
  
  • Skyrmions in magnetic multilayers
    N. Nagaosa and Y. Tokura (Nature Nanotechnology, 2013)
  
  • DMI and perpendicular anisotropy
    S. Rohart and A. Thiaville (PRL, 2013)
  
  • Data storage in skyrmions
    Y. Zhou et al. (Nature Communications, 2015)


PROJECT INFO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Version:        1.0.0
Created:        December 2024
Language:       Python 3.8+
Dependencies:   numpy, scipy, matplotlib, scikit-learn
License:        Research Use
Status:         Active development

For questions or issues, refer to SKYRMION_README.md
"""

# ============================================================================
# MAIN - Print comprehensive guide
# ============================================================================

if __name__ == '__main__':
    print(PROJECT_SUMMARY)
    
    print("\n" + "="*80)
    print("To get started, run:")
    print("  python skyrmion_examples.py")
    print("\nFor configuration guidance, run:")
    print("  python skyrmion_config.py")
    print("\nFor full documentation, see:")
    print("  SKYRMION_README.md")
    print("="*80 + "\n")
