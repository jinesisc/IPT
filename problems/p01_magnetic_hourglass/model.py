
"""
Model of a Magnetic Hourglass

DESCRIPTION:
An hourglass holds a mixture of ordinary sand and ferromagnetic (iron) grains.
This script builds up the physics in layers (currently three):

  Layer 1  Baseline flow .............. Beverloo law (Janssen effect assumed:
                                        flow rate does not depend on fill height)
  Layer 2  The field .................. on-axis field of a cylindrical permanent magnet
  Layer 3  One grain .................. induced magnetization (with saturation cap)
                                        and the magnet's pull on a single iron grain

It stops at a single grain: it shows how hard the magnet pulls compared with
gravity, but does not yet connect that pull to the flow rate.

COORDINATES: distance s is measured from the magnet's face, along its axis.
All units are SI (m, kg, s, T, A/m).

TO RUN (from the IPT project root):
       python main.py hourglass
       -> runs self-tests, prints a summary, saves figures to this folder's figures/

REQUIRES: numpy, matplotlib
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from common.constants import G, MU0
from common.plotting import COLORS, INK2, apply_style, save_figure

FIGURE_DIR = Path(__file__).parent / "figures"

# =============================================================================
# Parameters
# =============================================================================

@dataclass
class Params:
    # --- grains -------------------------------------------------------------
    d: float = 0.3e-3          # grain diameter [m] (same for sand and iron)
    rho_sand: float = 2650.0   # sand grain density [kg/m^3]
    rho_fe: float = 7870.0     # iron grain density [kg/m^3]
    w: float = 0.2             # MASS fraction of iron grains (0...1)
    packing: float = 0.60      # solid fraction of the packed bed

    # --- hourglass ----------------------------------------------------------
    D: float = 5.0e-3          # orifice diameter [m]
    C: float = 0.58            # Beverloo prefactor (fit from a field-off run)
    k: float = 1.5             # Beverloo edge constant (fit from a field-off run)
    M_total: float = 0.100     # total mass of sand in the top bulb [kg]

    # --- grain magnetism ----------------------------------------------------
    chi: float = 20.0          # effective susceptibility of an iron grain.
                               # Bulk iron is ~1000s; real powders are far lower.
                               # Only K = chi/(chi+3) matters, and K saturates at 1.
    Ms: float = 1.7e6          # saturation magnetization of iron [A/m]

    # --- permanent magnet (cylinder, magnetized along the hourglass axis) ---
    Br: float = 1.3            # remanence [T] (N42 NdFeB ~ 1.3 T)
    R_mag: float = 10e-3       # magnet radius [m]
    L_mag: float = 10e-3       # magnet length [m]
    gap: float = 30e-3         # distance from orifice to nearest magnet face [m]


# =============================================================================
# Layer 1 — baseline flow (Beverloo)
# =============================================================================

def mixture_density(p: Params) -> float:
    """Average solid density of the sand/iron mixture [kg/m^3]."""
    return 1.0 / (p.w / p.rho_fe + (1.0 - p.w) / p.rho_sand)


def bulk_density(p: Params) -> float:
    """Bulk density of the packed mixture (grains + gaps) [kg/m^3]."""
    return p.packing * mixture_density(p)


def beverloo(p: Params) -> float:
    """
    Beverloo law defined:  W = C * rho_b * sqrt(g) * (D - k * d)^(5/2).

    Returns the mass flow rate [kg/s] with no magnet. If the grains are too big
    for the hole (D - k * d <= 0), the flow is 0.
    """
    opening = max(p.D - p.k * p.d, 0.0)
    return p.C * bulk_density(p) * np.sqrt(G) * opening ** 2.5


def mass_vs_time(p: Params, t: np.ndarray) -> np.ndarray:
    """
    Mass collected in the bottom bulb [kg] at times t.
    The flow rate is constant (Janssen effect), so the mass grows in a straight
    line until the top bulb is empty.
    """
    return np.minimum(beverloo(p) * t, p.M_total)


# =============================================================================
# Layer 2 — the field
# =============================================================================

def field_on_axis(p: Params, s: np.ndarray) -> np.ndarray:
    """
    Field [T] of a uniformly magnetized cylinder, on its axis, at distance
    s >= 0 from its face (standard closed-form result):
        B(s) = Br/2 * [ (s+L)/sqrt(R^2+(s+L)^2) - s/sqrt(R^2+s^2) ]
    """
    s = np.asarray(s, dtype=float)
    R, L = p.R_mag, p.L_mag
    return 0.5 * p.Br * ((s + L) / np.sqrt(R**2 + (s + L) ** 2) - s / np.sqrt(R**2 + s**2))


def field_gradient(p: Params, s: np.ndarray) -> np.ndarray:
    """dB/ds [T/m], the slope of the formula above. Negative: the field weakens with distance."""
    s = np.asarray(s, dtype=float)
    R, L = p.R_mag, p.L_mag
    return 0.5 * p.Br * (R**2 / (R**2 + (s + L) ** 2) ** 1.5 - R**2 / (R**2 + s**2) ** 1.5)


# =============================================================================
# Layer 3 — one grain
# =============================================================================

def magnetization(p: Params, B: np.ndarray) -> np.ndarray:
    """
    Induced magnetization of a soft spherical grain [A/m].

    Unsaturated:  M = 3K * B/mu0,  K = chi/(chi+3)   (sphere's demagnetization included)
    Saturated:    M capped at Ms.
    """
    K = p.chi / (p.chi + 3.0)
    M = 3.0 * K * np.asarray(B, dtype=float) / MU0
    return np.minimum(M, p.Ms)


def magnetic_acceleration(p: Params, s: np.ndarray) -> np.ndarray:
    """
    Acceleration of an iron grain toward the magnet [m/s^2], at distance s.
        F = m * |dB/ds|   ->   a = M * |dB/ds| / rho_fe      (grain size cancels)
    Unsaturated this is (3K / 2 mu0 rho) * |d(B^2)/ds|.
    """
    return magnetization(p, field_on_axis(p, s)) * np.abs(field_gradient(p, s)) / p.rho_fe


def pull_ratio(p: Params, s: np.ndarray) -> np.ndarray:
    """Magnetic pull on an iron grain divided by its weight. Above 1, the magnet wins."""
    return magnetic_acceleration(p, s) / G


def distance_where_pull_equals_gravity(p: Params) -> float:
    """Distance from the magnet face [m] inside which the pull beats gravity."""
    s = np.linspace(0.0, 0.2, 20001)
    stronger = s[pull_ratio(p, s) >= 1.0]
    return float(stronger.max()) if stronger.size else 0.0


def is_saturated(p: Params, s: float) -> bool:
    """True if an iron grain at distance s is magnetized to its maximum."""
    return bool(magnetization(p, field_on_axis(p, s)) >= 0.999 * p.Ms)


# =============================================================================
# Self-tests
# =============================================================================

def self_tests() -> None:
    p = Params()

    # Layer 1: flow is constant, so mass vs time is a straight line until empty
    t = np.linspace(0.0, 0.9 * p.M_total / beverloo(p), 50)
    assert np.allclose(np.diff(mass_vs_time(p, t)), mass_vs_time(p, t)[1]), "mass should grow linearly"

    # Layer 1: doubling the opening (D - k * d) multiplies the flow by 2^2.5 = 5.66
    p2 = Params(D=2 * p.D - p.k * p.d)
    assert np.isclose(beverloo(p2) / beverloo(p), 2**2.5), "Beverloo 5/2 power law"

    # Layer 2: the field gets weaker with distance everywhere
    s = np.linspace(0.0, 0.1, 500)
    assert np.all(np.diff(field_on_axis(p, s)) < 0), "field should weaken with distance"

    # Layer 2: the coded slope matches a numerical slope of the field
    numeric = np.gradient(field_on_axis(p, s), s)
    assert np.allclose(field_gradient(p, s)[1:-1], numeric[1:-1], rtol=1e-3), "gradient formula"

    # Layer 3: far from the magnet (unsaturated), matches the closed form (3K / 2 mu0 rho) |d(B^2)/ds|
    far = np.array([0.06])
    K = p.chi / (p.chi + 3)
    closed = 3 * K / (2 * MU0 * p.rho_fe) * np.abs(2 * field_on_axis(p, far) * field_gradient(p, far))
    assert np.allclose(magnetic_acceleration(p, far), closed), "force law"

    # Layer 3: magnetization never exceeds saturation
    assert np.all(magnetization(p, np.linspace(0, 5, 100)) <= p.Ms), "saturation cap"

    print("All self-tests passed.")


# =============================================================================
# Figures
# =============================================================================

def make_figures(outdir: Path = FIGURE_DIR) -> list[Path]:
    apply_style()
    p = Params()
    W0 = beverloo(p)
    saved = []

    # ---- Fig 1: baseline — the hourglass is a clock --------------------------
    t = np.linspace(0.0, 1.2 * p.M_total / W0, 300)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(t, mass_vs_time(p, t) * 1e3, color=COLORS[0])
    ax.set(xlabel="time [s]", ylabel="mass in bottom bulb [g]",
           title="1. Baseline: mass grows linearly, then stops")
    ax.annotate(f"W0 = {W0 * 1e3:.2f} g/s\n(constant: Janssen effect)",
                xy=(0.5 * p.M_total / W0, 0.5 * p.M_total * 1e3), xytext=(10, -40),
                textcoords="offset points", color=INK2)
    saved.append(save_figure(fig, outdir, "1_baseline.png"))

    # ---- Fig 2: field and what actually pulls --------------------------------
    s = np.linspace(2e-3, 80e-3, 300)
    B = field_on_axis(p, s)
    dB = field_gradient(p, s)
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    axs[0].plot(s * 1e3, B * 1e3, color=COLORS[0])
    axs[0].set(xlabel="distance from magnet face [mm]", ylabel="B [mT]",
               title="2a. Field strength", yscale="log")
    axs[1].plot(s * 1e3, np.abs(2 * B * dB), color=COLORS[1])
    axs[1].set(xlabel="distance from magnet face [mm]", ylabel="|d(B²)/ds| [T²/m]",
               title="2b. What actually pulls: gradient of B²", yscale="log")
    saved.append(save_figure(fig, outdir, "2_field_profile.png"))

    # ---- Fig 3: pull on one grain vs its weight -------------------------------
    s_eq = distance_where_pull_equals_gravity(p)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(s * 1e3, pull_ratio(p, s), color=COLORS[0])
    ax.axhline(1.0, color=INK2, lw=1, ls="--")
    ax.axvline(s_eq * 1e3, color=INK2, lw=1, ls=":")
    ax.annotate(f"pull = weight at {s_eq * 1e3:.0f} mm\ncloser: the magnet wins",
                xy=(s_eq * 1e3, 1.0), xytext=(10, 20), textcoords="offset points", color=INK2)
    ax.set(xlabel="distance from magnet face [mm]", ylabel="magnetic pull / grain weight",
           title="3. How hard the magnet pulls one iron grain", yscale="log")
    saved.append(save_figure(fig, outdir, "3_grain_pull.png"))

    return saved


# =============================================================================
# Main
# =============================================================================

def summary(p: Params) -> None:
    W0 = beverloo(p)
    print("\n=== DEFAULT SETUP ===")

    print(f"\norifice (D)             = {p.D * 1e3:.1f} mm")
    print(f"grain (d)               = {p.d * 1e3:.2f} mm")
    print(f"iron mass frac (w)      = {p.w:.0%}")

    print(f"\nW0 (no field)            = {W0 * 1e3:.2f} g/s  -> empties {p.M_total * 1e3:.0f} g in {p.M_total / W0:.1f} s")
    print(f"\nMagnet at {p.gap * 1e3:.0f} mm from the orifice:")
    print(f"  field at orifice       = {field_on_axis(p, p.gap) * 1e3:.1f} mT")
    print(f"  pull / weight          = {pull_ratio(p, p.gap):.3f}")
    print(f"  grain saturated?       = {'yes' if is_saturated(p, p.gap) else 'no'}")

    print(f"\nMagnetic pull beats gravity within {distance_where_pull_equals_gravity(p) * 1e3:.1f} mm of the magnet face.")


def main() -> None:
    self_tests()
    summary(Params())
    files = make_figures()
    print(f"\nSaved {len(files)} figures to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
