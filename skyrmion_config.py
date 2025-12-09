"""
Configuration Guide for Skyrmion Simulations

This module provides pre-configured parameter sets for common use cases
and guidance on parameter selection.
"""

from dataclasses import dataclass
from skyrmion_simulator import MicromagneticParams


# ============================================================================
# PRE-CONFIGURED PARAMETER SETS
# ============================================================================

class ConfigurationLibrary:
    """Library of pre-configured parameter sets for various scenarios."""
    
    # Quick Test - for rapid parameter exploration
    QUICK_TEST = MicromagneticParams(
        grid_size=64,
        dt=1e-12,
        num_steps=5000,
        save_interval=100,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )
    
    # Standard Simulation - balanced for skyrmion formation
    STANDARD = MicromagneticParams(
        grid_size=128,
        dt=1e-12,
        num_steps=15000,
        save_interval=250,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )
    
    # High Resolution - detailed data encoding
    HIGH_RESOLUTION = MicromagneticParams(
        grid_size=256,
        dt=5e-13,
        num_steps=30000,
        save_interval=500,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )
    
    # Ultra High Resolution - research-grade simulation
    ULTRA_HIGH_RES = MicromagneticParams(
        grid_size=512,
        dt=2e-13,
        num_steps=50000,
        save_interval=1000,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )
    
    # Skyrmion Creation - optimized for skyrmion formation
    SKYRMION_CREATION = MicromagneticParams(
        grid_size=128,
        dt=1e-12,
        num_steps=20000,
        save_interval=200,
        A=15e-12,
        D=5e-3,      # Stronger DMI
        K_z=1.0e6,   # Stronger anisotropy
        B_z=-0.02,   # More negative field
        alpha=0.4,   # Higher damping for stability
        eps_K=0.0,   # No modulation
    )
    
    # Data Encoding - optimized for manifold encoding
    DATA_ENCODING = MicromagneticParams(
        grid_size=256,
        dt=5e-13,
        num_steps=25000,
        save_interval=250,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.015,
        alpha=0.3,
        eps_K=0.25,    # Moderate modulation
    )
    
    # Fast Relaxation - for quick convergence
    FAST_RELAXATION = MicromagneticParams(
        grid_size=64,
        dt=2e-12,
        num_steps=10000,
        save_interval=200,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.6,    # High damping
    )
    
    # Stable Low-Field - for stable skyrmion phases
    STABLE_LOW_FIELD = MicromagneticParams(
        grid_size=128,
        dt=5e-13,
        num_steps=40000,
        save_interval=400,
        A=15e-12,
        D=3e-3,       # Moderate DMI
        K_z=1.2e6,    # Stronger anisotropy
        B_z=-0.005,   # Weak field
        alpha=0.25,   # Low damping
    )
    
    # Strong DMI - for robust skyrmion formation
    STRONG_DMI = MicromagneticParams(
        grid_size=128,
        dt=1e-12,
        num_steps=15000,
        save_interval=250,
        A=15e-12,
        D=6e-3,       # Strong DMI
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )


# ============================================================================
# PARAMETER GUIDANCE
# ============================================================================

PARAMETER_GUIDANCE = {
    'A_exchange': {
        'description': 'Exchange stiffness constant',
        'unit': 'J/m',
        'typical_range': (10e-12, 20e-12),
        'effects': {
            'increase': 'Larger domain walls, higher energy barriers',
            'decrease': 'Smaller domain walls, easier magnetization rotation',
        },
        'physics': 'Controls the cost of magnetization gradients; larger A = stiffer spins',
    },
    
    'D_dmi': {
        'description': 'Dzyaloshinskii-Moriya interaction constant',
        'unit': 'J/m²',
        'typical_range': (2e-3, 8e-3),
        'effects': {
            'increase': 'Stronger skyrmion stabilization, smaller skyrmions',
            'decrease': 'Weaker DMI, harder to form skyrmions',
        },
        'physics': 'Asymmetric exchange; essential for skyrmion formation in thin films',
        'tuning_tip': 'Start at 4 mJ/m² and adjust for desired skyrmion density',
    },
    
    'K_z_anisotropy': {
        'description': 'Perpendicular magnetic anisotropy',
        'unit': 'J/m³',
        'typical_range': (0.5e6, 2.0e6),
        'effects': {
            'increase': 'Stronger out-of-plane preference, more compact skyrmions',
            'decrease': 'Weaker perpendicular anisotropy, thicker skyrmions',
        },
        'physics': 'Orients spins perpendicular to film; essential for 2D skyrmions',
    },
    
    'B_z_field': {
        'description': 'External magnetic field (perpendicular)',
        'unit': 'Tesla',
        'typical_range': (-0.05, 0.0),
        'effects': {
            'more_negative': 'Favors down spins, helps nucleate skyrmions',
            'less_negative': 'Fewer skyrmions, more uniform state',
            'positive': 'Uniform out-of-plane magnetization, no skyrmions',
        },
        'physics': 'Zeeman energy competes with anisotropy and DMI',
        'tuning_tip': 'Usually slightly negative (−0.01 to −0.02 T)',
    },
    
    'alpha_damping': {
        'description': 'Gilbert damping coefficient',
        'unit': 'dimensionless',
        'typical_range': (0.1, 0.8),
        'effects': {
            'increase': 'Faster convergence, higher dissipation',
            'decrease': 'Slower convergence, lower dissipation (can be unstable)',
        },
        'physics': 'Dissipation per unit time; drives system to energy minimum',
        'tuning_tip': 'α ≈ 0.3 is a good compromise; α > 0.5 ensures stability',
    },
    
    'eps_K_modulation': {
        'description': 'Anisotropy modulation strength',
        'unit': 'dimensionless',
        'typical_range': (0.0, 0.5),
        'effects': {
            'increase': 'Stronger data encoding, modified skyrmion structure',
            'decrease': 'Weaker coupling to data field',
            'zero': 'No data encoding, baseline skyrmions',
        },
        'physics': 'K_z(x,y) = K_0 + ε*K_0*D(x,y); couples data to skyrmion positions',
        'tuning_tip': 'Start at 0.1-0.2 for balanced encoding without destabilizing',
    },
    
    'grid_size': {
        'description': 'Grid resolution (N × N)',
        'typical_values': [64, 128, 256, 512],
        'effects': {
            'increase': 'Better spatial resolution, higher computational cost',
            'decrease': 'Faster computation, less detail',
        },
        'physics': 'Spatial discretization; cell_size sets physical length scale',
        'tuning_tip': 'Use 128×128 for exploration, 256×256 for production',
    },
    
    'dt_timestep': {
        'description': 'Time step for integration',
        'unit': 'seconds',
        'typical_range': (1e-13, 1e-11),
        'effects': {
            'increase': 'Faster simulation (but less accurate)',
            'decrease': 'More accurate (but slower)',
        },
        'physics': 'Euler scheme stability requires dt ~ 1e-12 or smaller',
        'tuning_tip': 'If energy diverges, reduce dt by factor of 2',
    },
    
    'num_steps': {
        'description': 'Total simulation time steps',
        'typical_values': [5000, 10000, 20000, 50000],
        'effects': {
            'increase': 'Better relaxation to equilibrium',
            'decrease': 'Faster simulation (may not reach equilibrium)',
        },
        'physics': 'System evolves toward minimum free energy',
        'tuning_tip': 'Monitor energy convergence; stop when plateau reached',
    },
}


# ============================================================================
# MATERIAL PARAMETER SETS
# ============================================================================

MATERIALS = {
    'FeGe': {
        'description': 'Iron germanium - archetypal skyrmion material',
        'A': 8.8e-12,
        'D': 1.58e-3,
        'K_z': 0.04e6,
        'M_s': 3.84e5,
        'reference': 'Nature Physics 6, 17 (2010)',
    },
    'MnSi': {
        'description': 'Manganese silicide - skyrmion host',
        'A': 2e-11,
        'D': 1.6e-3,
        'K_z': 0.0,      # Weak anisotropy
        'M_s': 3.4e5,
        'reference': 'Science 323, 915 (2009)',
    },
    'Co_Pt_multilayer': {
        'description': 'Co/Pt multilayer - induced perpendicular anisotropy',
        'A': 15e-12,
        'D': 3.9e-3,
        'K_z': 0.6e6,
        'M_s': 5.8e5,
        'reference': 'Nature Communications 6, 8504 (2015)',
    },
    'Fe_Gd_multilayer': {
        'description': 'Fe/Gd multilayer - ferrimagnetic skyrmions',
        'A': 10e-12,
        'D': 2.5e-3,
        'K_z': 0.9e6,
        'M_s': 3.2e5,
        'reference': 'Nature Nanotechnology 13, 1040 (2018)',
    },
    'Ni_Fe_Pt': {
        'description': 'Ni₈Fe₂/Pt interface - tunable skyrmions',
        'A': 13e-12,
        'D': 4.1e-3,
        'K_z': 0.8e6,
        'M_s': 4.5e5,
        'reference': 'APL Materials 4, 032502 (2016)',
    },
}


# ============================================================================
# QUICK REFERENCE TABLES
# ============================================================================

QUICK_START_GUIDE = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                          QUICK START GUIDE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ SCENARIO                          │ USE THIS CONFIG       │ COMPUTE TIME    │
├───────────────────────────────────┼──────────────────────┼─────────────────┤
│ Testing new parameters            │ QUICK_TEST           │ ~5 minutes      │
│ Basic skyrmion study              │ STANDARD             │ ~30 minutes     │
│ Data encoding demo                │ DATA_ENCODING        │ ~2 hours        │
│ Publication-quality results       │ HIGH_RESOLUTION      │ ~4 hours        │
│ Ultra-detailed research           │ ULTRA_HIGH_RES       │ ~8+ hours       │
│ Need fast answer (α ↑)            │ FAST_RELAXATION      │ ~10 minutes     │
│ Weak field, stable skyrmions      │ STABLE_LOW_FIELD     │ ~1 hour         │
│ Strong skyrmion formation         │ STRONG_DMI           │ ~30 minutes     │
└───────────────────────────────────┴──────────────────────┴─────────────────┘
"""


# ============================================================================
# TROUBLESHOOTING CHECKLIST
# ============================================================================

TROUBLESHOOTING = {
    'no_skyrmions_form': [
        'Check: D > 3 mJ/m² (DMI too weak?)',
        'Check: K_z > 0 (anisotropy sign?)',
        'Check: B_z is negative (field direction wrong?)',
        'Try: Increase |B_z| slightly',
        'Try: Increase D by 20-30%',
        'Try: Reduce α slightly for more underdamped dynamics',
        'Try: Increase num_steps to 30000+',
    ],
    
    'energy_diverges': [
        'Check: dt too large (reduce by 2x)',
        'Check: Grid too coarse (try 256x256)',
        'Try: Increase α to 0.4-0.5 for damping',
        'Try: Reduce dt by factor of 5',
        'Try: Use smaller grid for testing (64x64)',
    ],
    
    'poor_data_encoding': [
        'Check: Data field normalized to [-1, 1]?',
        'Check: eps_K too small (try 0.2-0.3)?',
        'Try: Finer grid (256×256 instead of 128×128)',
        'Try: Longer simulation time (30000+ steps)',
        'Try: Reduce damping (α = 0.2-0.3) for richer dynamics',
    ],
    
    'slow_convergence': [
        'Try: Increase α to 0.4-0.6',
        'Try: Use FAST_RELAXATION configuration',
        'Try: Increase dt (but watch for divergence)',
        'Try: Reduce grid size',
    ],
    
    'out_of_memory': [
        'Try: Reduce grid_size to 128 or 64',
        'Try: Reduce num_steps',
        'Try: Disable saving intermediate states',
        'Consider: Breaking simulation into chunks',
    ],
}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def print_material_properties(material_name: str):
    """Print material properties."""
    if material_name in MATERIALS:
        mat = MATERIALS[material_name]
        print(f"\n{material_name}:")
        print(f"  Description: {mat['description']}")
        print(f"  A = {mat['A']:.2e} J/m")
        print(f"  D = {mat['D']:.2e} J/m²")
        print(f"  K_z = {mat['K_z']:.2e} J/m³")
        print(f"  M_s = {mat['M_s']:.2e} A/m")
        print(f"  Reference: {mat['reference']}")
    else:
        print(f"Unknown material: {material_name}")


def get_config_for_scenario(scenario: str) -> MicromagneticParams:
    """Get recommended configuration for a given scenario."""
    scenarios = {
        'quick': ConfigurationLibrary.QUICK_TEST,
        'standard': ConfigurationLibrary.STANDARD,
        'high_res': ConfigurationLibrary.HIGH_RESOLUTION,
        'ultra_high_res': ConfigurationLibrary.ULTRA_HIGH_RES,
        'skyrmions': ConfigurationLibrary.SKYRMION_CREATION,
        'data': ConfigurationLibrary.DATA_ENCODING,
        'fast': ConfigurationLibrary.FAST_RELAXATION,
        'stable': ConfigurationLibrary.STABLE_LOW_FIELD,
        'strong_dmi': ConfigurationLibrary.STRONG_DMI,
    }
    
    if scenario in scenarios:
        return scenarios[scenario]
    else:
        raise ValueError(f"Unknown scenario: {scenario}. Choose from: {list(scenarios.keys())}")


# ============================================================================
# MAIN - REFERENCE
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("SKYRMION SIMULATOR - CONFIGURATION GUIDE")
    print("="*80)
    
    print(QUICK_START_GUIDE)
    
    print("\n" + "─"*80)
    print("MATERIAL PROPERTIES")
    print("─"*80)
    for mat in MATERIALS.keys():
        print_material_properties(mat)
    
    print("\n" + "─"*80)
    print("PARAMETER GUIDANCE")
    print("─"*80)
    for param, guidance in list(PARAMETER_GUIDANCE.items())[:3]:
        print(f"\n{param.upper()}")
        print(f"  Description: {guidance.get('description', 'N/A')}")
        print(f"  Typical Range: {guidance.get('typical_range', 'N/A')}")
    
    print("\n" + "─"*80)
    print("TROUBLESHOOTING - EXAMPLE")
    print("─"*80)
    print("\nIf no skyrmions form:")
    for tip in TROUBLESHOOTING['no_skyrmions_form']:
        print(f"  • {tip}")
    
    print("\n" + "="*80)
    print("For more details, see SKYRMION_README.md")
    print("="*80)
