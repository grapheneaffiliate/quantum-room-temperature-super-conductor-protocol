# Fabrication SOP (v1.0): Hydrogen-Intercalated Graphene / h-BN Heterostructures for RT Superconductivity Trials

## Scope
End-to-end, physically-grounded process to fabricate, encapsulate, and measure hydrogen-rich graphene/h-BN devices aimed at achieving Allen–Dynes targets: 𝜔_log ≥ 120 meV, 𝜇∗ ≤ 0.12, 𝜆_eff ≥ 2.5. Designed for a standard 2D-materials cleanroom. Includes recipes, tool setpoints, inline QC, pass/fail gates, and failure-mode fixes. Two device variants are provided to derisk: A) monolayer graphene + H; B) twisted bilayer graphene (TBG) + H.

## 0) Safety & contamination controls

### Chemicals
Piranha (H₂SO₄/H₂O₂), acetone/IPA, TMA/H₂O (thermal ALD), dilute HF (optional native oxide strip), FeCl₃ (Cu etch), PMMA, PPC.

### Gases
UHP Ar, UHP H₂, forming gas (5% H₂/N₂).

### Plasma
Low-power H₂ plasma only (10–30 W). Never expose unprotected graphene to O₂ plasma.

### PPE
Splash goggles, face shield, acid apron, heavy nitrile gloves for wet benches; HF protocol if used.

### Cross-contam
Dedicate graphene-only carriers/boats; no polymer outgassing in furnaces. ALD and RIE load-locks must be clean (pre-bake).

## 1) Bill of materials & tools (representative; substitute equivalents acceptable)

### Substrates
4-inch Si(100) with 285–300 nm thermal SiO₂ (dice to 10×10 mm chips).

### 2D materials
Monolayer CVD graphene on Cu foil; optional monolayer/few-layer h-BN (CVD) for capping; optional TBG via tear-and-stack.

### Metals & dielectrics
Ti/Au (10/80–100 nm) for contacts, Pd (1–3 nm) micro-reservoir (optional), Al₂O₃ (8–15 nm) thermal ALD cap, optional SiNₓ (5–10 nm) PEALD outer moisture barrier.

### Core tools
Optical lithography or EBL, e-beam evaporation or sputter, thermal ALD (TMA/H₂O), RIE with H₂ capability (or downstream H₂ plasma), hot plates, glovebox (optional but ideal), Raman (532 nm), AFM, SEM, XPS (optional), STM/STS (optional), PPMS or MPMS for transport / magnetometry.

## 2) Device architecture (baseline)

### Substrate stack
Si/SiO₂(300 nm) (Si is global back gate).

### Channel
Graphene (Variant A) or TBG ~1.1–1.2° (Variant B). Channel: 10–30 µm length × 2–5 µm width Hall-bar or 4-probe bar.

### Hydrogenation
Low-damage H₂ plasma (two-sided effective via edge infiltration + pre/post caps).

### Encapsulation (“trap-and-clamp”)
Immediate thermal ALD Al₂O₃ (8–15 nm) at 90–120 °C; optional Pd micro-reservoir ring (1–3 nm) outside active channel, buried under Al₂O₃; optional outer PEALD SiNₓ (5–10 nm) at ≤120 °C.

### Gating
Global back-gate (Si) + optional top-gate (Au over Al₂O₃/h-BN; 20–40 nm spacing) for plasmon tuning.

## 3) Process flow (high-level)

1.  Substrate clean & fiducials
2.  (Optional) Substrate strain features (nano-ridges)
3.  2D transfer (graphene; optional h-BN underlayer; TBG assembly if chosen)
4.  Contact patterning + metallization
5.  Pre-cap (thin Al₂O₃ 3–5 nm)
6.  Hydrogenation (low-power H₂ plasma)
7.  Final caps (Al₂O₃ → optional Pd ring → Al₂O₃ → optional SiNₓ)
8.  Top-gate (optional)
9.  Post-fab low-T anneal (≤150 °C)
10. Inline metrology & electrical bring-up
11. Superconductivity test plan (R(T), Meissner, spectroscopy)

Stop/go gates embedded after steps 1, 3, 5, 6, 7, 10.

## 4) Detailed SOP & recipes

### Step 1 — Substrate prep (10×10 mm chips)
*   **Reproducibility and Cleanup:** Emphasize cleanroom assembly protocols. Ensure all tools and consumables are certified for cleanroom use.
*   Cleave wafer; ultrasonic acetone 5 min → IPA 2 min → N₂ dry.
*   Piranha 3:1 H₂SO₄:H₂O₂, 10 min @ 110–120 °C → copious DI rinse → N₂ dry.
*   Hotplate 150 °C, 5 min (desorb moisture).
*   (Optional) O₂ UV-ozone 5 min for organics; do not O₂-plasma the graphene later.
*   QC-1: Contact angle < 15° (hydrophilic SiO₂); optical: no particles > 1 µm.

### Step 2 — (Optional) Strain-tuning ridges (pre-pattern)
*   Goal: ~0.5–1.5% uniaxial strain after transfer.
### Step 2 — (Optional) Strain-tuning ridges (pre-pattern)
*   Goal: ~0.5–1.5% uniaxial strain after transfer.

### Step 2 — (Optional) Strain-tuning ridges (pre-pattern)
*   Goal: ~0.5–1.5% uniaxial strain after transfer.
*   Spin PMMA A4 4000 rpm 60 s, softbake 180 °C 90 s.
*   EBL: define 20–50 nm tall, 200–500 nm pitch ridges (HSQ or resist-reflow method).
*   RIE-SiO₂: CHF₃/Ar 30/10 sccm, 30 mTorr, 80 W, etch 20–50 nm (calibrate).
*   Strip resist (NMP 80 °C) → IPA → N₂ → 150 °C 5 min bake.
*   QC-2: AFM ridge height within ±5 nm; RMS roughness < 0.5 nm between ridges.

### Step 3 — 2D material assembly

#### 3A) Monolayer graphene transfer (wet, PMMA)
*   Spin PMMA A4 3000 rpm 60 s on graphene/Cu → bake 180 °C 2 min.
*   Float in 0.1–0.5 M FeCl₃ to etch Cu; multiple DI exchanges.
*   Scoop onto SiO₂ chip; dry 5 min; bake 60–80 °C 10 min (avoid wrinkles).
*   PMMA removal: acetone 20 min → IPA → N₂; 120 °C 10 min bake.
*   QC-3: Raman (532 nm): Monolayer: 𝐼_2𝐷/𝐼_𝐺 > 2; D peak at ~1350 cm⁻¹ negligible (D/G < 0.05 pre-H). 2D FWHM < 35 cm⁻¹. Map over channel area (5×5 grid).
*   (Optional underlayer h-BN via dry pick-up improves 𝜇∗ screening; keep ≤5 nm to maintain gate coupling.)

#### 3B) TBG tear-and-stack (Variant B)
*   PPC/PDMS stamp picks up half-flake at RT, rotate 1.15 ± 0.05°, pick second half.
*   **Twist Angle Precision:** Utilize SHG microscopy or a piezo-controlled micro-rotator for real-time twist-angle monitoring, aiming for ±0.02° precision. Fine-tune angle after initial stacking if necessary.
*   **Reproducibility and Cleanup:** Before stacking, perform a high-temperature annealing step (e.g., 150-200 °C in vacuum or forming gas) to minimize defects and ensure a clean, stable stack.
*   Release on chip at 90–110 °C.
*   PPC removal: chloroform 20 min → IPA → N₂ → 120 °C 10 min bake.
*   QC-3B: Moiré check by STM/FFT or dark-field TEM if available; else Raman 2D anisotropy mapping. Accept if twist 1.10–1.20° and wrinkle-free over ≥10 µm span.

### Step 4 — Contacts & mesa (Hall-bar / 4-probe)
*   Spin PMMA A4 4000 rpm 60 s; EBL define electrodes (tip spacing 1–3 µm, width 0.5–1 µm).
*   Descum: downstream Ar (no O₂), 10 W, 30 s (or no-plasma if resist well developed).
*   E-beam evap: Ti/Au 10/90 nm @ ≤0.5 Å/s; base pressure ≤2×10⁻⁷ Torr; stage ≤25 °C.
*   Lift-off: acetone soak 30–60 min (no ultrasonics on fragile stacks) → IPA → N₂.
*   (Optional) Mesa etch to isolate channel: CHF₃/O₂ 30/3 sccm, 20 mTorr, 40 W, etch 10–20 s (protect contacts).
*   QC-4: SEM: clean edges; AFM: < 2 nm residue. Probe test: 2-terminal contact 𝑅_𝑐 < 1 kΩ/contact.

### Step 5 — Pre-cap Al₂O₃ (protect before H)
*   Thermal ALD (TMA/H₂O), 100 °C, 30–50 cycles → 3–5 nm Al₂O₃.
*   Purge ≥10 s between pulses to avoid parasitics.
*   QC-5: Ellipsometry (+/−0.3 nm), AFM uniformity; Raman: graphene D peak unchanged (no damage).

### Step 6 — Hydrogenation (low-damage, two-sided effective)
*   Rationale: Achieve sub-monolayer C–H incorporation (few % of C sites) to add high-ω modes while preserving conductivity. Use pulsed, low-power H₂ plasma with immediate post-cap.
*   **Hydrogen Stability Enhancements:** Consider adding a CaHₓ or PdHₓ nanolayer (1-3 nm) as a hydride reservoir, either as a pre-hydrogenation layer or integrated within the encapsulation stack, to enable "recharging" of hydrogen.
*   Tool: downstream RIE or ICP with remote plasma, sample grounded.
*   Chamber base ≤5×10⁻⁶ Torr.
*   Recipe H-1 (gentle): H₂ 50 sccm, 20 mTorr, 10 W RF, stage 25 °C. 10× pulses 20 s ON / 40 s OFF (total ON = 200 s).
*   Recipe H-2 (moderate): H₂ 75 sccm, 30 mTorr, 20 W RF, 25 °C; 6× pulses 20 s/40 s (ON = 120 s).
*   Keep plasma line-of-sight blocked (use shadow mask) to promote radical diffusion and minimize ion bombardment.
*   Critical: Transfer within ≤5 min under dry N₂ to ALD tool for final cap.
*   QC-6 (immediate Raman, 532 nm): Emergent C–H stretch (~2850–2950 cm⁻¹ shoulders); 𝐷/𝐺 rises but target 0.10 ≤ 𝐷/𝐺 ≤ 0.35 (over-hydrogenation if > 0.4). 2D peak persists (conductive network intact).
*   Abort if: D/G > 0.5 or G peak severely broadened (amorphization).

### Step 7 — Final encapsulation (“clamp”)
*   Main ALD cap: Thermal ALD Al₂O₃ to total 10–15 nm (i.e., add 5–10 nm above pre-cap) at 100–120 °C. **Ensure this ALD Al₂O₃ layer is dense and pinhole-free to effectively trap and clamp hydrogen.**
*   Optional Pd micro-reservoir ring (edge-fed): Lithography: define a 1–2 µm-wide ring around channel, ≥1 µm away from active graphene (on cap). E-beam evap Pd 1–3 nm @ ≤0.2 Å/s; lift-off. Purpose: Pd absorbs H and buffers local chemical potential; do not place Pd directly on channel.
*   Outer moisture barrier (optional): PEALD SiNₓ 5–10 nm @ ≤120 °C (low-power plasma).
*   Top-gate (optional): Define gate over channel (separated by Al₂O₃/h-BN dielectric); Au 30–50 nm.
*   QC-7: AFM step heights; gate leakage < 10 pA @ ±5 V; Raman confirms no new damage.

### Step 8 — Low-temperature stabilization anneal
*   Forming gas (5% H₂/N₂), 120–150 °C, 1–2 h in tube furnace or hotplate enclosure.
*   Purpose: heal mild defects, stabilize C–H; avoid >150 °C to preserve hydrogenation.
*   QC-8: Raman map: D/G unchanged ±0.05; sheet resistance within 10% of pre-anneal; no gate leakage drift.

## 5) Inline metrology & acceptance criteria (per gate)

| Gate | Metric | Target / Window | Rationale |
|---|---|---|---|
| QC-1 | Surface particles | None > 1 µm (optical) | Prevent blisters/wrinkles |
| QC-2 | Ridge height | 20–50 nm ±5 nm | Predictable strain |
| QC-3 | Raman monolayer | 𝐼_2𝐷/𝐼_𝐺 > 2, D/G<0.05 | High-quality graphene prior to H |
| QC-3B | Twist angle | 1.10–1.20° | Flat-band regime |
| QC-4 | Contact 𝑅_𝑐 | < 1 kΩ | Low series R for 4-probe |
| QC-5 | Pre-cap thickness | 3–5 nm Al₂O₃ | Damage shield before H |
| QC-6 | Raman after H | 0.10 ≤ 𝐷/𝐺 ≤ 0.35; C–H present; 2D visible | Sub-ML H without amorphization |
| QC-7 | Cap stack | Al₂O₃ total 10–15 nm; SiNₓ 0/5–10 nm; Pd 1–3 nm ring | Trap-and-clamp; moisture barrier |
| QC-8 | Stability | Raman unchanged; leakage < 10 pA @ ±5 V | Integrity before measurements |

## 6) Estimating physical targets (ω_log, λ_eff, μ*) from lab observables

Note: Only full 𝛼²𝐹(𝜔) (e.g., INS/DFPT) yields rigorous 𝜔_log. Below are pragmatic proxies for screening and iteration.

### 𝜔_log proxy from vibrational spectra
Acquire FTIR (or high-range Raman) 600–3200 cm⁻¹. Compute 𝜔_log ≈ exp( (∑ᵢ𝑤ᵢln𝜔ᵢ) / (∑ᵢ𝑤ᵢ) ), 𝑤ᵢ∝𝐼ᵢ with 𝐼ᵢ the (baseline-corrected, polarization-averaged) peak intensities of C–C (∼1580 cm⁻¹), C–H (∼2900 cm⁻¹), and any B–N/H modes present. Screening target: 𝜔_log ≥ 120 meV (~968 cm⁻¹; C–H modes strongly lift the log-average).

### 𝜆_eff trend from Raman linewidth & electronic DOS
Mode softening & linewidth broadening (G, 2D) with gating/doping and strain can indicate EPC strength. Track ∂𝜔_𝐺/∂𝑛 and FWHM vs carrier density; larger shifts under gating suggest stronger EPC. Combine with low-bias STS DOS enhancement (Variant B).

### 𝜇∗ mitigation by dielectric environment
Use h-BN under/over layers (3–10 nm total) and Al₂O₃ cap to enhance screening; avoid ultra-high carrier densities that raise Coulomb repulsion. Dual-gate operation to tune to the sweet spot where gap opens but dissipation remains low.

These quick-look proxies plus transport give a go/no-go to proceed to deep characterization.

## 7) Electrical & magnetic test plan (room-T capable)

### Transport (4-probe Hall-bar)
*   PPMS or probe station 300 K → 4.2 K sweeps; I = 1–100 µA (start small).
*   Record R(T), I–V at multiple T, B-field 0–1 T.
*   RT superconductivity signature: near-ohmic above 𝑇_𝑐, sharp R→0 within 1–5 K around 300 K; critical current emerges; field suppresses zero-R.
*   Artifacts to exclude: contact shorts (check non-local resistance), ionic conduction (time-dependent drift), Joule self-heating (current dependence).

### Magnetometry (MPMS)
*   ZFC/FC protocol; small field 5–10 Oe; T = 250–330 K.
*   Look for Meissner onset coincident (±3 K) with R(T) transition; correct for substrate/background.

### Spectroscopy (STS/IETS, optional)
*   Room-T UHV-STM; measure dI/dV and d²I/dV² over 0–150 meV.
*   Target gap 2Δ ≈ 3.5–4.5 k_B T_c → Δ ≈ 45–60 meV for 𝑇_𝑐 ∼ 300 K.

### Specific heat (PPMS heat-cap option, optional but decisive)
*   Micro-calorimetry on chip arrays; look for heat-capacity jump Δ𝐶 at 𝑇_𝑐.

### Integrated Measurement Points (IETS)
*   **On-chip IETS Junction:** Integrate an Inelastic Electron Tunneling Spectroscopy (IETS) junction directly into the device structure (e.g., by defining a small tunnel barrier during contact patterning). This allows for direct, consistent measurements of α²F(ω) and confirmation of λ_eff without device reassembly.

### Concordance rule
Claim only if transport + Meissner (+/- spectroscopy) co-align within ±3 K and field/current dependencies are consistent with superconductivity.

## 8) Parameter sweeps & DOE (design-of-experiments)
Run N ≥ 12 chips across a matrix:
*   H-dose: H-1 vs H-2; pulse count ±50%.
*   Cap thickness: Al₂O₃ 8, 12, 15 nm; with/without SiNₓ.
*   Strain: No ridges vs 20 nm vs 50 nm ridges.
*   Variant: Monolayer vs TBG.
*   Gate bias: Back-gate sweep −60…+60 V; optional top-gate ±5 V.

Track: Raman (D/G, CH), sheet R, R(T), leakage, onset features. Use SPC charts; promote only statistically significant wins.

### Pressure and Environment Control
*   **Piston-Cylinder Cell:** For critical steps involving pressure, utilize a piston-cylinder cell with a controllable pressure ramp. This allows for gradual pressure increase and real-time monitoring of device stability, optimizing conditions beyond a single setpoint.

## 9) Common failure modes & fixes

### Over-hydrogenation (amorphization)
D/G > 0.4; 2D collapses. → Reduce power to 10 W, halve pulses, increase OFF-time; ensure pre-cap present.

### No H signature
No CH peaks; D/G < 0.1. → Increase total ON-time 1.5×; consider mild sample warm (40–60 °C) to enhance radical mobility; add Pd ring.

### High contact resistance
Poor Ti adhesion on Al₂O₃ residues. → Brief Ar sputter clean (200 eV, 10 s) on contact windows only before metallization.

### Gate leakage
Pinholes in ALD. → Increase cycles; lower temp to improve film density; add SiNₓ 5 nm.

### R(T) drop but no Meissner
Possible filament/short or ionic conduction. → Non-local measurement; drive frequency dependence; remove Pd ring (re-fab); cross-section inspect.

## 10) Optional Variant B (TBG-focused enhancements)
*   Aim twist 1.15°; apply uniaxial strain 0.5–1% via ridges to flatten bands further.
*   Retain lower H-dose (stay H-1) to minimize disorder.
*   Prefer h-BN underlayer (3–5 nm) to smooth potential landscape; top-gate strongly recommended to tune filling.

## 11) Data logging (minimal template)
*   Chip ID / Variant / Lot / Date
*   Process recipe IDs (H-dose, ALD cycles, ridge height)
*   Raman maps (CSV of peak positions, FWHM, intensities)
*   AFM/SEM thumbnails
*   Electrical: R(T), I–V, non-local R, gate leakage
*   Magnetometry: ZFC/FC curves; background subtraction notes
*   Comments: anomalies, tool deviations, ambient conditions

## 12) Practical notes on physics targets

### 𝜔_log
Introduction of C–H stretch (∼360 meV) elevates the log-average even at small coverage; avoid killing 𝜋 network—stay in D/G 0.1–0.3 band.

### 𝜆_eff
Increases with EPC (strain-softened G, moiré-enhanced DOS in TBG) plus plasmonic contribution via gating at 10–50 nm distances; dual-gate lets you find the “λ-ridge.”

### 𝜇∗
Keep electronic screening high (h-BN + Al₂O₃ stack; moderate carrier density). Excessive doping can increase Coulomb repulsion; tune to maximize gap/coherence instead of raw carrier count.

### Quick “Golden Recipes” (starting points)
*   **GR-A (Monolayer graphene)**: QC graphene → contacts → pre-cap Al₂O₃ 4 nm (100 °C) → H-1 (10 W, 200 s total ON) → Al₂O₃ +8 nm → SiNₓ 5 nm → form-gas 130 °C 90 min.
*   **GR-B (TBG 1.15°)**: Same as GR-A but H-1 at 120 s total ON, with h-BN 3–5 nm underlayer and top-gate Au 40 nm.

## 13) What constitutes a credible “hit”

### R(T)
≥3-order drop to instrument floor near 300 K, reversible with B-field (≥0.1 T) and I-bias.

### Meissner
Diamagnetic onset aligned with R(T); ZFC/FC separation expected.

### Spectroscopy
STS/IETS feature consistent with Δ ≈ 45–60 meV.

### Specific heat
Micro-calorimetry on chip arrays; look for heat-capacity jump Δ𝐶 at 𝑇_𝑐.

### Concordance rule
Claim only if transport + Meissner (+/- spectroscopy) co-align within ±3 K and field/current dependencies are consistent with superconductivity.

### Reproducibility
≥3 chips with concordant onsets; parameter-trend consistency (e.g., H-dose or gate-tuning shifts 𝑇_𝑐 logically).

### Artifacts excluded
Via non-local tests, contact re-layout, and thermal controls.

## Final remarks
This SOP is deliberately conservative on hydrogenation (low-damage, pulsed, immediate capping) and aggressive on encapsulation and inline QC—the two levers most likely to preserve high-frequency H modes (lifting 𝜔_log) while keeping the 𝜋 network conductive (supporting 𝜆_eff). Variant B (TBG) offers an additional flat-band route if monolayer trials plateau.
