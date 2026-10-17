# Problem 1: The magnetic hourglass

> Consider an hourglass containing a mixture of normal and ferromagnetic grains.
> Investigate how an external magnetic field affects the flow rate. What properties
> of the field (amplitude, gradient, time-variation etc.) can be inferred from
> observing the granular flow?

## Model so far (layers 1–3)

| Layer | Function(s) | Physics |
|---|---|---|
| 1. Baseline flow | `beverloo`, `mass_vs_time` | **W = C · ρ_b · √g · (D − k·d)^(5/2)**. The Janssen effect means **W** doesn't depend on fill height, so **mass = W · t**. |
| 2. The field | `field_on_axis`, `field_gradient` | On-axis field of a cylinder magnet, **B(s) = (Br/2)·[ (s+L)/√(R²+(s+L)²) − s/√(R²+s²) ]**, and its slope **dB/ds** |
| 3. One grain | `magnetization`, `magnetic_acceleration`, `pull_ratio` | **M = 3K·B/μ₀** with **K = χ/(χ+3)**, capped at **Ms**. Pull: **a = M·\|dB/ds\| / ρ_fe**, and **pull ratio = a / g** |

**Figures** (saved to `figures/`):
1. Mass in the bottom bulb vs. time: a straight line, so the hourglass is a clock.
2. Field strength **B** and the gradient of **B²** vs. distance from the magnet.
3. Magnetic pull ÷ grain weight (**a / g**) vs. distance. Where the curve crosses **1**, the magnet starts beating gravity.

## Assumed parameters: replace with real measurements

Every number in the `Params` class of `model.py` is a placeholder until we replace it.

**Sensitivity** says how much a wrong value distorts the result.
**High** means a 10% error gives a much larger than 10% error.

### A. Measure directly

| Parameter | Default | What it is | How to measure | Sensitivity |
|---|---|---|---|---|
| `D` | 5.0 mm | Orifice (neck) diameter | Calipers on the narrowest point of the neck, or photograph next to a ruler | **High**: **W ∝ (D − k·d)^2.5**, so 10% error in **D** gives ~25%+ error in **W** |
| `d` | 0.30 mm | Grain diameter | Sieves, or photograph ~30 grains next to a ruler with a phone macro lens and average. If sand and iron differ in size, note both (the model assumes one size). | Medium |
| `M_total` | 100 g | Sand mass in the top bulb | Weigh before filling | Low: only sets when the run ends |
| `w` | 20% | Iron **mass** fraction | Weigh the sand and the iron separately when mixing: **w = m_iron / (m_iron + m_sand)** | Low for now (only changes the bulk density); **High** once layer 4 is added |
| `R_mag`, `L_mag` | 10 mm, 10 mm | Magnet radius and length | Calipers | Medium |
| `gap` | 30 mm | Distance from the orifice to the magnet face | Ruler. Measure to the **inside** of the neck, so include the glass wall thickness. | **High**: the pull falls off very steeply with distance |

### B. Measure with a simple side experiment

| Parameter | Default | What it is | How to measure | Sensitivity |
|---|---|---|---|---|
| `packing` (with `rho_sand`, `rho_fe`) | 0.60, 2650, 7870 kg/m³ | Together these give the bulk density **ρ_b** | Pour the actual mixture loosely into a measuring cylinder, weigh it, and divide mass by volume to get **ρ_b = mass / volume**. Then set `packing = ρ_b / mixture_density(p)`. | Medium: **W ∝ ρ_b** |
| `rho_sand`, `rho_fe` | 2650, 7870 kg/m³ | Density of one grain (no gaps) | Water displacement: weigh a sample, pour it into water in a measuring cylinder, read the volume rise. Rusty or porous iron filings will be below 7870. | Low on their own |
| `Br` | 1.3 T | Magnet strength | Measure **B** on the magnet's axis at 3–5 distances with a Hall probe or a phone magnetometer app (e.g. phyphox). Adjust `Br` until `field_on_axis(...)` matches. Don't trust the spec sheet. | **High**: **pull ∝ B²**, so 10% error in **Br** gives ~20% error in pull |
| `chi` | 20 | How easily your iron grains magnetize | **Jump test:** spread a few iron grains on a flat surface and slowly lower the magnet toward them from above. Measure the height at which they jump up. That is where **pull = weight** (figure 3 crosses **1**). Adjust `chi` until `distance_where_pull_equals_gravity(p)` matches. Only **K = χ/(χ+3)** matters, so above **χ ≈ 20** the result barely changes; report "**χ ≳ 20**" if that's where it lands. | Medium–High for small **χ**, Low for large **χ** |

### C. Fit from flow experiments

| Parameter | Default | What it is | How to fit it | Sensitivity |
|---|---|---|---|---|
| `C`, `k` | 0.58, 1.5 (from [1], consistent with [2]) | Beverloo constants for **your** hourglass shape | Magnet off. Measure **W** (scale + timer) for several orifice sizes **D**. Plot **W^(2/5)** against **D**: it should be a straight line. Its x-intercept is **k·d** (gives `k`) and its slope gives `C`. With only one hourglass, keep `k` = 1.5 and solve the Beverloo formula for `C` from your measured W. | **High**: sets the baseline everything is compared with |

**Why the defaults are only a starting point:** [1] and [2] measured flat-bottomed containers
with a sharp-edged hole. An hourglass neck is curved and tapered, and **C** depends strongly on
the opening's shape: in [2], tilting the hole to vertical dropped **C** from 0.573 to 0.269.

### D. Textbook values (keep unless you have reason not to)

| Parameter | Default | What it is | When to change it |
|---|---|---|---|
| `Ms` | 1.7×10⁶ A/m | Maximum magnetization of iron | **Currently has no effect.** A round grain needs **B ≈ 0.8 T** to saturate, but on the axis of an N42 cylinder magnet **B** never exceeds **Br/2 ≈ 0.65 T** (0.46 T at the face of the default magnet). It matters only for elongated filings or grains beside the magnet's edge. If needed: ~1.0–1.5×10⁶ for oxidized iron or steel filings, ~0.48×10⁶ for magnetite powder. |
| `G`, `MU0` | 9.81, 4π×10⁻⁷ | Gravity, vacuum permeability (in `common/constants.py`) | Never |

### Assumptions built into the formulas (not in `Params`)

| Assumption | Where | If it's wrong |
|---|---|---|
| Grains are spheres | `magnetization` (**K = χ/(χ+3)**) | Elongated filings magnetize more; this ends up absorbed into `chi` |
| The grain sits on the magnet's center line | `field_on_axis` | Off-axis the field is weaker; center the magnet carefully |
| The grain is alone (no neighbors) | Layer 3 | Neighboring iron grains strengthen each other; this is the "stickiness" layer later |

### Record what you measured

When we replace a default, I'll change the comment beside it in `model.py` to say where the
value came from, for example:

```python
D: float = 4.6e-3   # measured with calipers, 2026-10-20, ±0.1 mm
```

## Where the current default values come from

| Value | Default | Source |
|---|---|---|
| `C` | 0.58 | [1]: **C ≈ 0.58**, depending slightly on friction (up to 0.64 for glass spheres). [2] fitted **C = 0.573** for 0.3 mm glass beads. |
| `k` | 1.5 | [1]: **k ≈ 1.5** for spherical grains; depends on grain shape. [2] fitted **k = 1.6**. |
| `packing` | 0.60 | Typical loose packing of round grains. Check: **0.60 × 2650 ≈ 1590 kg/m³** for pure sand, close to the 1530 kg/m³ bulk density measured for glass beads in [2]. |
| `rho_sand` | 2650 kg/m³ | Standard density of quartz (most sand is quartz) |
| `rho_fe` | 7870 kg/m³ | Standard density of pure iron |
| `Ms` | 1.7×10⁶ A/m | Standard saturation magnetization of iron |
| `Br` | 1.3 T | Typical remanence of an N42 neodymium magnet |
| `chi` | 20 | Rough estimate for iron powder; no source, fit it with the jump test |
| `D`, `d`, `M_total`, `w`, `R_mag`, `L_mag`, `gap` | — | Placeholders for a typical setup; replace with your measurements |

## References

1. W. A. Beverloo, H. A. Leniger and J. van de Velde, "The flow of granular solids through
   orifices," *Chemical Engineering Science* 15, 260 (1961). doi:10.1016/0009-2509(61)85030-6.
   Summary of the constants: [Thermopedia, "Granular materials discharge through orifices"](https://thermopedia.com/content/821/)
2. H. G. Sheldon and D. J. Durian, "Granular discharge and clogging for tilted hoppers,"
   [arXiv:0810.0495](https://arxiv.org/abs/0810.0495)

## Data

Put raw measurements in `data/` (e.g. `jump_test.csv`, `field_vs_distance.csv`).
Commit these, since they can't be regenerated.

## Coming next

Layer 4 turns the pull on one grain into a change in flow rate. Given enough time,
later layers should add stickiness between grains, time-varying fields, and validity checks.
