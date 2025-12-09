#!/usr/bin/env python3
"""Debug energy calculation components."""

from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
import numpy as np

# Create small simulation
params = MicromagneticParams(grid_size=16, num_steps=50)
sim = SkyrmionSimulator(params)

print(f"System parameters:")
print(f"  Grid size: {sim.N}x{sim.N}")
print(f"  dx: {sim.dx} m = {sim.dx*1e9} nm")
print(f"  thickness: {sim.thickness} m = {sim.thickness*1e9} nm")
print(f"  K_z range: [{sim.K_z_map.min():.2e}, {sim.K_z_map.max():.2e}] J/m³")
print(f"  A: {params.A} J/m")
print(f"  M_s: {params.M_s} A/m")
print(f"  B_z: {params.B_z} T\n")

# Manually compute energy components
N = sim.N
dx = sim.dx
thickness = sim.thickness
m = sim.m
K_z_map = sim.K_z_map
A = params.A
M_s = params.M_s
B_z = params.B_z

inv_dx = 1.0 / dx

# Exchange energy
E_ex = 0.0
A_eff = A * thickness
for i in range(3):
    grad_m_x = np.gradient(m[:, :, i], axis=1) * inv_dx
    grad_m_y = np.gradient(m[:, :, i], axis=0) * inv_dx
    E_ex += np.sum(grad_m_x**2 + grad_m_y**2) * A_eff * (dx ** 2)

print(f"Exchange energy components:")
print(f"  A_eff: {A_eff:.6e} J/m²")
print(f"  E_ex (total): {E_ex:.6e} J")
print(f"  Per cell: {E_ex / (N*N):.6e} J")

# Anisotropy energy
E_anis_cells = K_z_map * m[:, :, 2]**2 * (dx ** 2) * thickness
E_anis = -np.sum(E_anis_cells)

print(f"\nAnisotropy energy components:")
print(f"  Per-cell energy range: [{E_anis_cells.min():.6e}, {E_anis_cells.max():.6e}] J")
print(f"  E_anis (total): {E_anis:.6e} J")
print(f"  E_anis per cell: {E_anis / (N*N):.6e} J")

# Zeeman energy
mu_0 = 4 * np.pi * 1e-7
E_zee_cells = -mu_0 * M_s * B_z * m[:, :, 2] * (dx ** 2) * thickness
E_zee = np.sum(E_zee_cells)

print(f"\nZeeman energy components:")
print(f"  Per-cell energy range: [{E_zee_cells.min():.6e}, {E_zee_cells.max():.6e}] J")
print(f"  E_zee (total): {E_zee:.6e} J")
print(f"  E_zee per cell: {E_zee / (N*N):.6e} J")

# Total
total_energy = E_ex + E_anis + E_zee
total_area = (N * dx) ** 2
energy_density = total_energy / total_area

print(f"\nTotal energy:")
print(f"  E_total: {total_energy:.6e} J")
print(f"  Total area: {total_area:.6e} m²")
print(f"  Energy density: {energy_density:.6e} J/m²")
print(f"  Energy density: {energy_density:.2f} J/m²")

# Sanity check: what if we use surface energy densities?
print(f"\nSanity check - using surface energy densities:")
K_z_surf = params.K_z * thickness  # Convert to surface
A_surf = params.A / thickness if thickness > 0 else params.A
print(f"  K_z_surface: {K_z_surf:.6e} J/m²")
print(f"  A_surface: {A_surf:.6e} J/m²")
print(f"  Expected E_anis ~ K_z_surface × area: {K_z_surf * total_area:.6e} J")
print(f"  Actual E_anis: {E_anis:.6e} J")
