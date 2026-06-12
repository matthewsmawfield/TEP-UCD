# Temporal Equivalence Principle: The Dirac Limit of Dynamical Proper Time
**Matthew Lukin Smawfield**
Version: v0.1 (Qatar)
First published: 7 June 2026 · Last updated: 12 June 2026
DOI: 10.5281/zenodo.20572698

---

## Abstract

Standard Quantum Field Theory and the Dirac equation are low-resolution, flat-frame tangent limits of a deeper dynamical proper-time phase transport governed by the Temporal Equivalence Principle (TEP). By treating proper time *τ* as a dynamical scalar field *φ* rather than a universal parameter, five foundational results are recovered.

(1) The phase action *S = −mc^{2} ∫ dτ̃* emerges as the primitive geometric driver, with mass appearing in the primitive action as the parameter governing the oscillator frequency, *ω_{0} = mc^{2} / ℏ*, modulated by the conformal factor in the causal matter metric *g̃_{μν}*. (2) The Klein-Gordon equation is derived from the minimal geometric Lagrangian in the causal metric and verified via WKB / eikonal expansion; its eikonal limit recovers the *g̃*-Hamilton-Jacobi equation, not via operator substitution. (3) The Dirac operator is recovered as the local Clifford/tetrad representation in the isochronous background — it emerges in the limit where temporal shear *Σ_{μ}* and disformal coupling *B(φ)* are negligible. (4) Spin-1/2 is reinterpreted as temporal-orientation holonomy of the proper-time phase frame, and antimatter as reversed phase orientation on the second sheet of the two-sheeted temporal manifold. (5) The spinor structure of relativistic quantum mechanics may be reinterpreted geometrically: Dirac's 1928 spinor encoded temporal-orientation holonomy without access to a dynamical proper-time geometry. These results subsume standard quantum theory as a geometric approximation valid in the screened limit, where local interaction energy densities exceed the saturation scale *ρ_{T} ≈ 20 g/cm^{3}* (established in TEP-UCD, Paper 6).

Keywords: quantum foundations, Dirac equation, proper time, phase transport, spin, antimatter, scalar-tensor theories, geometric quantum mechanics, temporal equivalence principle, Hamilton-Jacobi equation, Klein-Gordon equation

## 1. Introduction: The Background-Dependency of Quantum Field Theory

### 1.1 The External-Metric Postulate

Every equation of quantum mechanics — from the Schrödinger equation to the Dirac equation, from the path integral to the operator formalism of Quantum Field Theory — is formulated on a prescribed spacetime background. The metric *g_{μν}* is not dynamical in the quantum sector; it is an external input, fixed either as the Minkowski metric *η_{μν}* in flat-space QFT or as a classical solution to Einstein's equations in QFT in curved spacetime. In neither case does the quantum field back-react on the temporal geometry. Proper time *τ* is computed from a metric that is unaffected by the quantum state of the matter fields it governs.

This is not a bug in the formalism; it is a deliberate approximation. The energy scales of known particle physics are so far below the Planck scale that gravitational back-reaction is negligible. However, the approximation becomes a structural limitation when one asks whether the quantum state itself — the phase coherence, the entanglement, the spin orientation — might be fundamentally tied to the geometry that the metric describes. In standard QFT, the metric is a stage; the quantum fields are actors. The Temporal Equivalence Principle reverses this hierarchy.

A critical distinction must be made. General Relativity *does* recognise local proper-time variance — gravitational time dilation is a well-measured phenomenon. A clock near a massive body ticks slower than a distant clock. However, GR treats this variance as a curvature effect within a single, globally defined spacetime manifold. The metric *g_{μν}* is universal; all matter and light propagate on the same geometric background. The temporal variance is integrable: one can always construct a globally synchronous foliation in the absence of rotation, and the proper time along any path is computed from the same metric. Beneath this lies a deeper structural assumption: *global isochrony*, the premise that all local proper-time clocks within a spacetime neighbourhood can be synchronised to a single universal time parameter. It is this assumption of global isochrony — not the curvature itself — that is the exact structural limitation that dynamical proper-time geometry dismantles.

The Temporal Equivalence Principle goes further. It treats proper time not merely as a parameter computed from a prescribed metric, but as a *dynamical scalar field* *φ* governed by its own field equations, coupled to matter density through a conformal–disformal metric. The metric that governs quantum phase transport is not the observed metric *g_{μν}*; it is the causal matter metric *g̃_{μν}*, which differs from the observed metric by a conformal factor *A(φ)* that modulates with local matter density. In standard QFT, even in curved spacetime, the metric is externally prescribed and the quantum field is quantised on that fixed background. The Bogoliubov transformation between vacua encodes particle creation (the Unruh and Hawking effects), but the metric itself remains classical and unaffected. This paper targets the structural assumption that the metric governing quantum phase transport is externally prescribed rather than dynamically coupled to the matter fields it governs.

### 1.2 The Inventions It Forces

When a dynamical, density-dependent temporal landscape is forced into the framework of a fixed background metric, the theory must invent compensating structures to account for the discrepancy:

- *Wavefunction collapse:* The sudden, non-unitary reduction of the quantum state upon measurement may reflect the inability of a fixed-background formalism to accommodate the geometric interaction between a probe and the local temporal shear field. In a dynamical proper-time geometry, the measurement process is reinterpreted as the equilibration of probe and system to a shared temporal contour: as the probe approaches the interaction region, the joint shear field relaxes to a common isochronous manifold. The apparent collapse is not a discontinuous jump but the geometric relaxation of two initially independent temporal topologies to a single synchronised phase. The fluid dynamics of the temporal shear field conserve geometric stress; what standard quantum mechanics records as projection onto an eigenstate is, in the TEP framework, the settling of the combined system onto a contour of constant proper-time phase. A rigorous derivation of this correspondence from the full TEP field equations, including the non-linear disformal sector, is beyond the scope of this paper and is addressed in TEP-KIN (Paper 25).

- *Intrinsic spin:* In standard quantum mechanics, spin-1/2 is described by an abstract SU(2) representation without reference to spatial extent. In the TEP framework, spin-1/2 is the temporal-orientation holonomy of a localized topological charge — a geometric, not algebraic, property.

- *Antimatter as separate field:* The Dirac equation's negative-energy solutions are reinterpreted as a separate particle species. In the TEP framework, antimatter is the reversed proper-time phase orientation on the second sheet of the two-sheeted temporal manifold.

- *Virtual particles as force carriers:* The exchange of momentum between particles across empty space is modeled by the emission and absorption of unobservable virtual bosons. In the TEP framework, forces may be reinterpreted as routed through the continuous geometry of the disformally tilted light cone. The derivation of the Maxwell equations and full quantum electrodynamic interactions from the TEP disformal geometry is not provided in this paper; it is addressed in TEP-SPIN (Paper 24).

### 1.3 The Temporal Equivalence Principle

The Temporal Equivalence Principle (TEP) treats proper time as a dynamical scalar field *φ* governed by a conformal–disformal metric (Paper 0). Matter clocks tick at rates set by the conformal factor *A(φ) = exp(β_{A} φ / M_{Pl})*. The critical saturation scale *ρ_{T} ≈ 20 g/cm^{3}* (established in TEP-UCD, Paper 6, New Delhi, and cross-validated across compact-object and galactic scales) is the Temporal Topology saturation scale at which screening effects saturate; it is a property of the theory's non-linear regime and not a binary threshold. In the screened limit, where the local interaction energy density substantially exceeds *ρ_{T}*, the locally observable Temporal Shear is suppressed, *A(φ) → 1*, and standard physics is recovered. In the unscreened regime, the full geometric structure of the Temporal Topology is manifest. The disformal coupling *B(φ)* controls the tilting of the light cone by the temporal gradient; in the screened limit the observable disformal response is suppressed and interactions become isotropic.

What "local density" means in this context requires clarification. The saturation scale *ρ_{T}* characterizes the energy density of the local temporal-field configuration, not merely the ambient matter density of the laboratory environment. High-energy particle collisions (e.g., TeV-scale interactions) produce local energy densities of order *10^{24} g/cm^{3}*, vastly exceeding *ρ_{T}* and placing such processes deep in the screened limit. Even in an evacuated chamber, the interaction region of a scattering event carries an energy density far above the saturation scale. Thus standard QFT remains valid for all currently accessible particle-physics experiments, while low-energy, long-baseline interferometry in ultra-low-density environments may probe the unscreened regime.

The foundational geometric framework of TEP was established in the original theory paper (Smawfield 2026, Paper 0, DOI: 10.5281/zenodo.16921911), which introduced the full disformal metric *g̃_{μν} = A^{2}(φ) g_{μν} + B(φ) ∇_{μ}φ ∇_{ν}φ* with *A(φ) = exp(β_{A} φ / M_{Pl})*, demonstrated local Lorentz invariance as a theorem, and introduced the sector ontology of Temporal Topology (spatial/covariance structure of *ln A(φ)*), Temporal Shear (*Σ_{μ} = ∇_{μ} ln A*), and the saturation scale *ρ_{T}*. This paper works in the conformal limit *B(φ) = 0* and adopts the foundational convention throughout: the symbol *A(φ)* denotes the original conformal factor of the Jakarta theory, so the causal matter metric reads *g̃_{μν} = A^{2}(φ) g_{μν}*. The screened limit *A(φ) → 1* recovers the standard Minkowski background; the singular limit *A(φ) → ∞*, reached as *φ → +∞* (for *β_{A} > 0*), marks the topological defects identified in Section 4. The conformal limit suffices for the quantum-field subsumption derivation because the disformal sector contributes only higher-order corrections to the tangent-space degradation. The full disformal structure becomes essential for cosmological synchronization holonomy and multi-messenger tests, addressed in companion papers.

Companion papers in this series develop TEP across a wide range of mass densities, from subatomic scales (TEP-SPIN) through laboratory interferometry (TEP-KIN) to cosmological distances (TEP-C0). This paper addresses the quantum regime directly, arguing that standard QFT is the flat-frame, isochronous tangent limit of a deeper dynamical proper-time geometry.

### 1.4 Structure of This Paper

Section 2 establishes the phase action and recovers the Klein-Gordon relation as the Euler-Lagrange equation of the minimal scalar-field Lagrangian in the causal metric. Section 3 delivers the central derivation: the Dirac operator is recovered as the local tetrad representation in the screened limit. Section 4 reinterprets spin and antimatter as geometric orientations. Section 5 concludes and outlines the synthesis with companion papers.

### 1.5 Broader Framework Context

Beyond the tangent-space derivations developed below, TEP carries conceptual implications that extend across the companion series. Bell's theorem assumes that entangled particles are zero-dimensional points separated by absolute vacuum, with correlations mediated only by pre-programmed local hidden variables. TEP discards this premise: the interval between entangled charges is filled by the macroscopic temporal shear field, and the pair is bound by a continuous geometric contour in the disformal temporal field. Measurement of one particle is not a superluminal signal through empty space but a physical perturbation of one end of a rigid macroscopic topology, with geometric stress conserved along the shared contour — geometric non-local realism in place of the Copenhagen epistemic retreat. Temporal-topology drag denotes the influence of large-scale temporal-field configurations on local particle dynamics, mediated by the conformal factor *A(φ)* rather than spacetime curvature; environment-dependent mass emerges from modulation of the proper-time oscillator frequency by *A(φ)*. What standard QFT models as virtual force carriers and statistical wavefunctions may be effective descriptions of geometric stress propagation in a contiguous temporal fluid. These phenomena furnish concrete experimental signatures developed in TEP-SPIN (Paper 24) and TEP-KIN (Paper 25).

## 2. Proper-Time Phase Transport

### 2.1 The Phase Action

The fundamental action for a massive particle in the TEP framework is:

S = −mc^{2} ∫ dτ̃

where *τ̃* is the dynamical proper time measured along the particle's worldline in the causal matter metric *g̃_{μν}*. This is not an abstract phase — it is the *physical accumulated phase* of the matter-clock oscillator, whose frequency is set by the local conformal factor *A(φ)*.

Dimensional analysis confirms the primitive status of this action. The dimensions are:

[S] = [m] [c^{2}] [τ̃] = M L^{2} T^{−1} = [ℏ]

Thus *S/ℏ* is dimensionless, as required for a phase. The action is not postulated; it is the unique Lorentz-invariant, first-order geometric functional of the proper-time interval. The mass *m* appears not as an inertial parameter but as the frequency of phase accumulation: *ω_{0} = mc^{2} / ℏ*.

The causal matter metric is related to the observed metric *g_{μν}* by the conformal transformation:

g̃_{μν} = A^{2}(φ) g_{μν}

In the screened limit, where the local interaction energy density substantially exceeds the saturation scale *ρ_{T}*, *A(φ) → 1* and *g̃_{μν} → g_{μν}*. In the unscreened regime, the particle's phase accumulates along geodesics of the causal metric, not the observed metric.

### 2.2 The Massive Particle as Proper-Time Oscillator

A massive particle is defined geometrically as a stable, local proper-time oscillator governed by the causal metric. The oscillator's natural frequency in the flat-frame limit is:

ω_{0} = mc^{2} / ℏ

In the full TEP geometry, this frequency is modulated by the conformal factor:

ω_{local}(φ) = ω_{0} · A(φ)

Mass parameter and conformal rescaling. The bare mass *m* enters the primitive action *S = −mc^{2} ∫ dτ̃*. The local oscillator frequency is *ω_{local} = mc^{2} A(φ) / ℏ*. The Klein-Gordon equation uses the bare parameter *m* because the conformal modulation is already encoded in the causal d'Alembertian *□̃* (via *A^{2}* in the metric). The effective inertial mass measured by local clock response reduces to *m* when *A → 1* in the screened limit.

### 2.3 The g̃-Hamilton-Jacobi Equation

The Hamilton-Jacobi equation for the proper-time phase action in the causal metric is:

g̃^{μν} ∂_{μ}S ∂_{ν}S = m^{2}c^{2}

This is the fundamental classical equation governing the phase transport of a massive particle. It is not an operator equation — it is the Hamilton-Jacobi equation in a curved geometry. The quantum features emerge from the geometric structure, not from operator quantization.

Metric signature convention. Throughout this paper, the metric signature is *(+, −, −, −)*. In the flat Minkowski limit, *η_{μν} = diag(1, −1, −1, −1)*, and the Hamilton-Jacobi equation takes the explicit form:

(∂_{t}S)^{2} − |∇S|^{2} = A^{2}(φ) m^{2}c^{2}

### 2.4 Deriving the Klein-Gordon Equation from Geometric First Principles

The Klein-Gordon equation is derived as the Euler-Lagrange equation of the minimal scalar-field Lagrangian in the causal metric. The derivation proceeds in three steps.

#### Step 1: The geometric scalar-field Lagrangian.

The phase field *Ψ* is a complex scalar field propagating on the causal manifold with metric *g̃_{μν}*. The covariant, second-order Lagrangian for a massive scalar field that reduces to the standard Klein-Gordon Lagrangian in the flat limit is:

L = ½ ( g̃^{μν} ∂_{μ}Ψ^{*} ∂_{ν}Ψ − m^{2} |Ψ|^{2} )

The metric tensor *g̃^{μν}* raises indices; the inverse metric is *g̃^{μν} = A^{−2}(φ) g^{μν}*. The bare mass parameter *m* enters here because it is the only dimensionful parameter available from the primitive action *S = −mc^{2} ∫ dτ̃*. This Lagrangian follows directly from the causal metric *g̃_{μν}* via minimal coupling; its form is fixed by the geometric structure established in Section 2.1. The linear structure of the resulting wave equation follows from the stationarity condition on this action, exactly as in standard field theory, but now formulated in the causal geometry.

#### Step 2: Euler-Lagrange equation.

Varying the action *S = ∫ L √−g̃ d^{4}x* with respect to *Ψ^{*}* gives:

∂_{μ} ( √−g̃ g̃^{μν} ∂_{ν}Ψ ) − √−g̃ m^{2} Ψ = 0

Dividing by *√−g̃* yields the causal d'Alembertian form:

□̃ Ψ + m^{2} Ψ = 0

where *□̃ = (1 / √−g̃) ∂_{μ}( √−g̃ g̃^{μν} ∂_{ν} )* is the d'Alembertian operator constructed from the causal metric *g̃_{μν}*.

#### Step 3: Connection to the Hamilton-Jacobi equation via WKB / eikonal expansion.

To verify that this linear wave equation is consistent with the classical Hamilton-Jacobi equation derived in Section 2.3, insert the WKB / eikonal ansatz:

Ψ = R e^{iS/ℏ} , R, S ∈ ℝ

Substituting into *(□̃ + m^{2}) Ψ = 0* and dividing by *e^{iS/ℏ}* yields an equation that can be organised by powers of *ℏ*. Before collecting orders, recall the exact decomposition of the causal d'Alembertian established in Step 2. With *g̃_{μν} = A^{2}(φ) η_{μν}* in the flat-background limit,

□̃ = A^{−2}(φ) □_{M} + 2 A^{−3}(φ) η^{μν} (∂_{μ}A)(∂_{ν}Ψ)

where *□_{M} = ∂_{t}^{2} − ∇^{2}* is the Minkowski d'Alembertian. The conformal factor *A(φ)* is the same scalar field-dependent rescaling introduced in Section 2.1; throughout the eikonal expansion it is treated as a prescribed geometric background, not as part of the *ℏ*-expansion of *Ψ*. Its derivatives *∂_{μ}A = A Σ_{μ}* enter only through the second, temporal-shear term.

At leading order *O(ℏ^{−2})*, the real part recovers the Hamilton-Jacobi equation. The conformal bookkeeping at this order is explicit. From the WKB ansatz, *∂_{ν}Ψ = (i / ℏ) Ψ ∂_{ν}S + O(ℏ^{0})*, so the shear term is *O(ℏ^{−1})* and does not contribute at *O(ℏ^{−2})*. The conformal factor therefore enters the leading order exclusively through the kinetic prefactor *A^{−2}(φ)* in the first term: gradients of the phase *S* are contracted with the inverse causal metric *g̃^{μν} = A^{−2}(φ) η^{μν}* before any quantum corrections appear. The mass term carries no conformal prefactor (it is the bare parameter *m* from the primitive action). Collecting the *ℏ^{−2}* coefficients therefore gives

−A^{−2}(φ) R [(∂_{t}S)^{2} − |∇S|^{2}] + m^{2}c^{2} R = 0

Dividing by *R* and multiplying by *−A^{2}(φ)* immediately yields the *g̃*-Hamilton-Jacobi equation of Section 2.3, with the conformal mass shift *A^{2}(φ)* on the right-hand side:

(∂_{t}S)^{2} − |∇S|^{2} = A^{2}(φ) m^{2}c^{2}

The appearance of *A^{2}(φ)* at this order is not an independent postulate; it is the classical signature of propagation on the causal manifold. In the screened limit *A → 1*, the equation reduces to the standard Hamilton-Jacobi form; in the unscreened regime, the effective inertia of the phase front is modulated by the local conformal clock-rate rescaling before any *O(ℏ^{−1})* transport or *O(ℏ^{0})* quantum-potential terms enter.

At next order *O(ℏ^{−1})*, the imaginary part gives the transport equation in the causal metric:

∂_{t}(R^{2} ∂_{t}S) − ∇ · (R^{2} ∇S) + 2A^{−1}R^{2} η^{μν}(∂_{μ}A)(∂_{ν}S) = 0

which expresses conservation of the probability current *j^{μ} = R^{2} ∂^{μ}S* modified by the temporal shear *Σ_{μ} = ∂_{μ} ln A*. In the screened limit *A → 1*, *∂_{μ}A → 0*, this reduces to the standard transport equation.

At finite order *O(ℏ^{0})*, the quantum-potential term with shear coupling appears:

A^{−2} □_{M} R / R + 2A^{−3} η^{μν}(∂_{μ}A) (∂_{ν}R) / R

which reduces to *□_{M} R / R* in the screened limit and is suppressed by *ℏ^{2}* relative to the Hamilton-Jacobi term.

The Klein-Gordon equation is thus *derived* from the minimal geometric Lagrangian in the causal metric, and its eikonal limit is verified to coincide with the *g̃*-Hamilton-Jacobi equation. The inputs are the causal metric *g̃_{μν}*, the bare mass *m* from the primitive action, and the standard scalar-field Lagrangian minimally coupled to that metric. No operator substitution is required.

In the screened limit *g̃_{μν} → η_{μν}* and the standard Klein-Gordon equation is recovered. In the unscreened regime, the causal d'Alembertian encodes the full geometric structure of the temporal field, including additional temporal-shear coupling terms proportional to *∂_{μ}A*.

## 3. Subsuming the Dirac Operator

### 3.1 The Standard Dirac Equation

The Dirac equation, the cornerstone of relativistic quantum mechanics, is:

(iγ^{μ}∂_{μ} − m) ψ = 0

where *γ^{μ}* are the Dirac matrices satisfying the Clifford algebra *{γ^{μ}, γ^{ν}} = 2η^{μν}*. This equation is noted for its Lorentz covariance, its prediction of antimatter, and its role as the foundation of Quantum Electrodynamics.

### 3.2 Algebraic Flat-Space Recovery

The historical inability to geometrically unify quantum mechanics with relativity stemmed from a fundamental metric misattribution. Previous frameworks attempted to map particle holonomy onto the gravitational spacetime metric while maintaining time as a universal parameter. TEP demonstrates that standard Quantum Field Theory and the Dirac equation are actually low-resolution, flat-frame tangent limits of a deeper dynamical proper-time phase transport. The geometric operator successfully reduces to the familiar Dirac operator only when the temporal background is artificially flattened. By treating proper time τ as a dynamical scalar field φ and deriving the action from the causal matter metric *g̃_{μν}*, the geometric language of a deeper temporal topology is naturally revealed.

The standard Dirac equation is recovered as the local Clifford/tetrad representation in the isochronous (screened) limit. This is an exact mathematical result: the geometric operator reduces to the familiar Dirac operator when the temporal background is flat.

In curved spacetime, spinors cannot be defined directly on the manifold. They require a local frame (tetrad) *e^{a}_{μ}* at each point, related to the metric by:

g_{μν} = e^{a}_{μ} e^{b}_{ν} η_{ab}

The Dirac matrices in curved spacetime are defined as *γ^{μ} = e_{a}^{μ} γ^{a}*, where *γ^{a}* are the flat-space Dirac matrices. The Dirac operator in curved spacetime becomes:

(iγ^{μ}∇_{μ} − m) ψ = 0

where *∇_{μ}* is the spin-covariant derivative, incorporating the spin connection *ω^{ab}_{μ}*.

The flattening conditions. The standard Dirac equation *(iγ^{μ}∂_{μ} − m) ψ = 0* makes two critical assumptions that are never stated explicitly:

- *The temporal shear vanishes:* *Σ_{μ} = ∇_{μ} ln A(φ) = 0*. This means the conformal factor is constant, and the causal metric is identical to the observed metric.

- *The observable disformal response is suppressed:* *B(φ)(∇φ)² → 0*. This means the light-cone tilt becomes phenomenologically negligible, and all interactions are effectively isotropic in the screened regime.

When these two conditions are imposed, the causal metric *g̃_{μν}* reduces to the Minkowski metric *η_{μν}*, the tetrad field becomes the identity, and the spin-covariant derivative reduces to the ordinary partial derivative. The full geometric Dirac operator:

(i e^{μ}_{a} γ^{a} ∇_{μ} − m) ψ = 0

collapses to the standard form:

(iγ^{μ}∂_{μ} − m) ψ = 0

### 3.2.1 Disformal Departure from Conformal Collapse

The conformal sector *g̃_{μν} = A^{2}(φ) η_{μν}* alone admits tetrad rescaling *e^{a}_{μ} → A(φ) δ^{a}_{μ}*. The rank-one disformal correction *B(φ) ∇_{μ}φ ∇_{ν}φ* cannot be absorbed into a single conformal factor: for generic *∇_{μ}φ ≠ 0*, off-diagonal components such as *g̃_{0x} = B(φ) ∂_{t}φ ∂_{x}φ* are non-zero unless *B(φ) = 0*. Even with temporal shear suppressed (*A(φ) = 1*, *Σ_{μ} = 0*), the metric departs from Minkowski through *g̃_{00} − 1 = B(φ)(∂_{t}φ)^{2}* and *g̃_{xx} + 1 = B(φ)(∂_{x}φ)^{2}*. Standard Clifford collapse therefore requires both flattening conditions of Section 3.2. SymPy Audit 3b in `results/sympy_audit.log` verifies this signpost; the full disformal tensor audit (inverse metric, null-cone tilt, Christoffel symbols, synchronization holonomy) is in TEP-KIN (Paper 25), `results/disformal_kinematics_audit.log`.

Bridge to the full matter metric. The conformal subsumption proof of Sections 2–3 is not an abandonment of the Jakarta ansatz *g̃_{μν} = A^{2}(φ) g_{μν} + B(φ) ∇_{μ}φ ∇_{ν}φ*; it isolates the tangent-space algebra that standard QFT already assumes. Particle-physics experiments operate in the screened regime where *B(φ)(∇φ)^{2} → 0*, so the Dirac and Klein-Gordon derivations of this paper are the exact limiting forms of the same geometric operator written against the full *g̃_{μν}*. Outside that limit, the disformal sector does not modify the Clifford algebra by a small perturbative correction; it replaces the isotropic Minkowski inner product with a direction-dependent causal structure. TEP-KIN (Paper 25) carries the full metric through: the symbolic inverse *g̃^{μν}*, the effective refractive index *n*_{eff} that tilts null cones, the Christoffel symbols that route geodesics through *B(φ)* gradients, and the synchronization-holonomy sector that distinguishes conformal transport (exact one-form *d ln A*) from genuinely non-integrable disformal transport. The narrative continuity is therefore explicit: Paper 23 establishes what standard relativistic quantum mechanics recovers when both temporal shear and observable disformal response are suppressed; Paper 25 establishes how interactions, measurement, and interferometric observables behave when they are not.

Exact tensor algebra. The derivation proceeds by exact tensor algebra. The individual steps — tetrad collapse to the identity, vanishing of the spin connection, and reduction of the covariant derivative to the ordinary partial derivative — are the standard flat-space limit of the Fock–Ivanenko formalism in curved-spacetime quantum mechanics. Every term in the geometric operator is tracked through the flattening limit; no approximation is made. The standard Dirac operator is the exact local Clifford/tetrad representation in the isochronous background. This tensor-algebraic derivation has been verified symbolically using SymPy; see `results/sympy_audit.log`.

### 3.3 The Screened Limit

The flattening conditions correspond to the physical limit where the local interaction energy density substantially exceeds the saturation scale *ρ_{T}*. In this regime:

- *A(φ) → 1* (conformal factor approaches unity)

- *Σ_{μ} = ∇_{μ} ln A(φ) → 0* (temporal shear vanishes)

- *B(φ)(∇φ)² → 0* (observable disformal response suppressed)

The standard Dirac equation is thus the *screened limiting case* of the geometric operator, valid in the regime where the geometric structure of the temporal field is negligible. High-energy particle collisions (TeV-scale, with characteristic local energy densities of order *10^{24} g/cm^{3}*) are deep in this screened limit, which is why standard QFT remains empirically successful for all currently accessible particle-physics experiments.

### 3.4 Geometric Reinterpretation of Spinor Structure

The algebraic subsumption derivation shows that the standard Dirac equation is recovered within the TEP framework as the screened limit. The TEP framework further provides a geometric reinterpretation of the spinor structure that Dirac introduced in 1928.

The algebraic structure of the Dirac equation — the Clifford algebra, the spinor representation, the charge conjugation and parity operations — all emerge from the tetrad structure. When the tetrad is trivial (flat background), these operations appear as abstract algebraic symmetries. When the tetrad is non-trivial (curved temporal background), they are revealed as geometric orientation operations on the proper-time manifold.

In the TEP framework, the spinor is not an abstract internal vector space but a mathematical encoding of temporal-orientation holonomy. The Clifford algebra is not an abstract symmetry but the local algebra of frame rotations in the temporal orientation bundle. The gamma matrices are not fundamental operators but the generators of infinitesimal rotations in the proper-time phase frame. This reinterpretation follows directly from the geometric structure of the temporal manifold; it reveals the physical origin of the algebraic structure that Dirac discovered.

The Dirac equation is thus *subsumed* by the TEP framework: it is recovered as the screened limit when temporal shear and disformal coupling are negligible. This characterizes an encompassing theoretical framework: the standard theory is the tangent limit of a deeper geometric structure.

## 4. Spin and Antimatter as Geometric Orientations

### 4.1 Spin-1/2 as Temporal-Orientation Holonomy

In the TEP framework, spin-1/2 arises as temporal-orientation holonomy of topological charge defects in the temporal field. In standard quantum mechanics, spin-1/2 is described by an abstract SU(2) representation without reference to spatial extent. The SU(2) spinor encodes angular momentum *ℏ/2* algebraically, not as a physical rotation in space.

In the TEP framework, spin is reinterpreted as temporal-orientation holonomy. A fermion is not a point particle with intrinsic angular momentum — it is a localized topological charge in the temporal landscape. The charge core is a topological defect where the scalar field diverges, *φ → +∞* (for *β_{A} > 0*), driving the conformal factor to its singular limit *A(φ) → ∞*. At this singularity *ln A(φ)* is multi-valued. Away from the core, the temporal shear *Σ_{μ} = ∇_{μ} ln A(φ)* is a smooth gradient; the integral of a gradient around any closed loop in a simply connected region is zero, consistent with the original TEP theory, which assumes the smooth exponential *A(φ) = exp(β_{A} φ / M_{Pl})* everywhere. The non-zero holonomy arises exclusively from circulation around the singular core, where Stokes' theorem does not apply. The topological charge is therefore an *extension* of the smooth TEP framework into the topological defect regime, not a consequence of the smooth field equations alone.

Singularity regulation. The limit *φ → +∞* is adopted here as a strict topological point defect for holonomy purposes: the winding of *ln A(φ)* around a codimension-two core encodes the circulation, and Stokes' theorem is inapplicable precisely because the connection is not globally exact. This idealization parallels the Dirac-string construction for a magnetic monopole or the *1/r* vortex of a superfluid; it is not regulated by perturbative renormalization of a zero-dimensional source. Physically, the fermion carries finite Compton-scale extent *r_{c} = ℏ/(mc)*; the scalar field equation with potential *V(φ)* saturates the conformal response at the core, smearing the vorticity *(∇ × Σ)* over this radius rather than admitting a bare ultraviolet divergence. A loop penetrating this smeared core (*r < r_{c}*) therefore encounters redistributed vorticity rather than a point singularity, yet the enclosed holonomy does not degrade continuously: the integer winding *n = ±1* in the orientation bundle is a topological invariant, and any closed contour encircling the defect yields the same *±4π* phase regardless of how deeply it penetrates the core. Observable spin and transport are computed in the exterior regime *r &gg; r_{c}*, where the *1/r* shear profile applies; the interior regularization is derived in TEP-SPIN (Paper 24).

The "spin-1/2" property emerges because a closed loop encircling the charge core accumulates a phase of *±4π*, corresponding to the single-valuedness requirement of the proper-time oscillator. A rotation of *2π* would leave the phase field double-valued (*e^{i2π/2} = −1*), which is forbidden for a scalar phase; the minimal closed loop returning the phase to its original value therefore carries *4π* of accumulated phase. This is the geometric origin of fermionic statistics: the phase field is single-valued only after a *4π* circuit, exactly as spin-1/2 requires. The connection to the standard spin-statistics theorem — that half-integer spin implies fermionic exchange symmetry — is recovered because the topological charge carries the minimal half-integer holonomy of the temporal orientation bundle. The two "spins" are the two possible orientations of the topological charge relative to the local matter-clock congruence:

- *Spin up:* The topological charge rotates in the same sense as the local temporal shear circulation.

- *Spin down:* The topological charge rotates in the opposite sense.

The spinor algebra SU(2) is not an abstract symmetry group but the local holonomy group of the temporal field's orientation bundle. The Pauli matrices *σ_{i}* are the generators of infinitesimal rotations in this orientation bundle, not in physical space.

### 4.2 The g-Factor as Geometric Ratio

The anomalous magnetic moment *g − 2* arises in QED from loop corrections involving virtual photons. In the TEP framework, the g-factor is a geometric ratio that measures the deviation from the flat-frame approximation. The "anomaly" is not a quantum correction but a consequence of the topological charge geometry in the temporal field. Far from the charge core, where the conformal factor flattens (*A(φ) → 1*), the geometric correction vanishes and *g → 2*, recovering the Dirac value. The geometric contribution to the g-factor is addressed in TEP-SPIN (Paper 24).

### 4.3 Antimatter as Reversed Proper-Time Orientation

In standard quantum mechanics, antimatter is introduced as a separate field of particles with opposite charge. The Dirac equation's negative-energy solutions are reinterpreted as positive-energy antiparticles moving backward in time, a conceptual device (the Feynman-Stückelberg interpretation) that preserves causality by reinterpreting negative-energy states as antiparticles.

In the TEP framework, antimatter is not a separate field or opposite charge — it is the reversed proper-time phase orientation relative to the local matter-clock congruence. Where a particle's phase advances as *+τ̃* along the future-directed light cone, its antiparticle advances as *−τ̃* along the past-directed cone.

This reversal is a *geometric*, not algebraic, operation. It arises naturally from the two-sheeted structure of the proper-time manifold, where the "other sheet" corresponds to reversed phase orientation. The two-sheeted topology is a global property of the temporal manifold and is independent of the local density. The critical saturation scale *ρ_{T} ≈ 20 g/cm^{3}* is the Temporal Topology saturation scale at which screening effects saturate; it does not act as a boundary between the sheets. In the screened limit, where the local interaction energy density substantially exceeds *ρ_{T}*, the observable temporal shear is suppressed and the phase-orientation distinction becomes unresolvable at the measurement scale, recovering the standard CPT-symmetric effective theory.

Geometric junction of the two sheets. Formally, the proper-time manifold is a double cover *M = M_{+} ⊔ M_{−}*, with sheets distinguished by the sign of phase accumulation along the matter-clock congruence. The junction hypersurface *Σ* is the codimension-one locus on which future-directed and past-directed orientations meet: points of *Σ* are those at which the local proper-time covector *k_{μ} = ∂_{μ}S* is null in the causal metric (*g̃^{μν} k_{μ} k_{ν} = 0*) and the orientation of *k_{μ}* is not globally continuable to a single sheet without crossing a branch. Charge conjugation *C* acts locally as orientation reversal across *Σ*: a future-directed worldline on *M_{+}* maps to a past-directed continuation on *M_{−}* with *dτ̃ → −dτ̃*. Particle–antiparticle creation and annihilation are the physical realisations of this junction: a single connected phase contour on *Σ* bifurcates onto opposite sheets at creation, and opposite contours recombine at annihilation. The junction is therefore not a spatial wall in laboratory coordinates; it is a topological seam in the orientation bundle, localised to events where the temporal phase field changes sheet. Away from *Σ*, each sheet supports smooth, future-directed propagation; across *Σ*, only the combined configuration *M_{+} ⊔ M_{−}* remains globally single-valued.

Laboratory realisation: pair production. The abstract seam *Σ* admits a concrete laboratory identification in photon-induced pair production, *γ + Z → e^{−} + e^{+} + Z*, where a high-energy photon converts in the Coulomb field of a nucleus *Z*. The process is traced here in laboratory coordinates *(t, \mathbf{x})*; the sheet assignment is a property of the orientation bundle, not of the spatial direction of motion in the lab frame.

*(i) Pre-junction approach.* Before the vertex, the photon propagates on the future null cone with *k_{μ} k^{μ} = 0* in *g̃*. Its phase action *S* advances along the null generator; no timelike proper-time oscillator is yet present because the photon is massless. The covector *k_{μ} = ∂_{μ}S* is future-directed and lies entirely on one orientation sheet.

*(ii) Junction event.* At the interaction vertex—the spacetime event at which the electromagnetic coupling supplies sufficient energy–momentum budget to populate the electron mass shell—the local covector remains null on the photon mass shell but is no longer globally continuable on a single sheet: the connected phase contour must branch to support two timelike, on-shell continuations. This vertex is a point of *Σ*. It is localised to a single laboratory event (a point in *(t, \mathbf{x})*), not extended along a spatial hypersurface; detectors record the bifurcation only through the emergence of two timelike tracks downstream of that event.

*(iii) Bifurcation onto opposite sheets.* From the connected contour on *Σ* emerge two branches. The electron continues on *M_{+}* with timelike *k^{μ}*, accumulating phase as *+dτ̃* along a future-directed worldline. The positron continues on *M_{−}* with reversed proper-time orientation, *dτ̃ → −dτ̃* relative to the matter-clock congruence. Both worldlines advance forward in coordinate time *t*; the sheet distinction is geometric, not a reversal of laboratory causality. The Feynman–Stückelberg reinterpretation is recovered as the screened-laboratory projection of a past-directed proper-time orientation on *M_{−}*: the positron appears in detectors as a particle of opposite charge propagating forward in *t*, while its phase transport is reversed on the second sheet. In the screened limit, all standard QED observables—track curvature in a magnetic field, bremsstrahlung spectra, coincidence timing—are recovered; the TEP content is the geometric identification of the creation vertex with a branch point on *Σ*.

*(iv) Post-creation separation and entanglement.* As the pair separates, each branch carries a localized topological charge (Section 4.1) on its respective sheet. The phase contour rooted at the *Σ* event remains a single connected geometric object: TEP-KIN (Paper 25) identifies this as the macroscopic entanglement link between the bifurcated charges. The junction event is therefore not only the sheet transition but also the origin of the shared orientation-bundle holonomy that enforces quantum correlations between the outgoing tracks.

*(v) Annihilation as recombination.* The reverse process, *e^{−} + e^{+} → γ + γ*, is recombination on *Σ*: timelike contours from *M_{+}* and *M_{−}* converge at a common null event, the shared phase contour closes, and a single future-directed null continuation emerges. Creation and annihilation are time-reversed navigations of the same topological seam.

Textual spacetime schematic. The same navigation can be read directly in the laboratory *(t, x)* plane, with *x* along the photon beam axis and *t* increasing upward. For *t < t_{V}*, the incident photon follows a null generator at slope *dt/dx = ±1/c* (future light cone); its phase contour lies on a single sheet. At the vertex *V = (t_{V}, x_{V})*, that null generator meets *Σ*—a single event, not a spatial line or wall. For *t > t_{V}*, two timelike worldlines branch from *V*, each with *|dx/dt| < c* and both advancing in coordinate time. The electron worldline *γ_{e^{−}}* lies on *M_{+}* with *dτ̃ > 0*; the positron worldline *γ_{e^{+}}* lies on *M_{−}* with reversed orientation *dτ̃ < 0* in the matter-clock congruence. The two branches may separate symmetrically in *x* (for example, emission at equal angles about the beam axis) while remaining future-directed in *t*. A track photograph or time-resolved coincidence measurement records only these timelike curves in *(t, x)*; the sheet labels are not imprinted on the tracks but are fixed by the sign of phase accumulation along each worldline. Annihilation is the time-reverse reading of the same diagram: *γ_{e^{−}}* and *γ_{e^{+}}* converge at a vertex *V′* on *Σ*, and the outgoing photon again follows a null generator from *V′*. The junction is thereby visible only as a fork or merge in the causal structure of recorded worldlines, localised to the vertex events *V* and *V′*.

Crucially, CPT symmetry is *preserved locally*. The local CPT theorem remains valid at every point in spacetime: a full rotation in the local orientation bundle (C × P × T) returns the system to its original state. Charge conjugation C is realised as a local reflection in the orientation bundle (reversing the direction of proper-time phase accumulation), not as a global sheet transition. The global topology of the temporal manifold is two-sheeted: a particle and its antiparticle reside on opposite sheets, but this separation is a consequence of the global boundary conditions, not of the local C operation itself. This suggests a possible topological origin for the observed matter-antimatter asymmetry: rather than requiring a symmetry-breaking event in the early universe, the dominance of matter may reflect the global topology of the temporal manifold, which may favor one sheet over the other in certain density regimes. A quantitative prediction of the baryon-to-photon ratio from this topological bias is an active research direction within the TEP framework.

### 4.4 Unification of C, P, and T

Charge conjugation (C), parity (P), and time reversal (T) are unified as orientation operations on the two-sheeted temporal manifold:

- *C (Charge conjugation):* Local reflection in the orientation bundle — maps particle to antiparticle by reversing phase orientation.

- *P (Parity):* Spatial reflection — reverses the handedness of the topological charge in the temporal landscape.

- *T (Time reversal):* Phase reversal — reverses the direction of proper-time accumulation, mapping future-directed phase transport to past-directed. It belongs to the same orientation-bundle sector as charge conjugation but is a distinct operation in the product group C × P × T.

The CPT theorem, a central result in quantum field theory, is reinterpreted geometrically: a full rotation in the orientation bundle (C × P × T) returns the system to its original state. In standard QFT, the theorem is derived rigorously from Lorentz invariance, locality, and the spin-statistics connection (Lüders-Pauli, Jost). The TEP framework recovers this derivation and reveals its geometric origin: the theorem is manifest as the orientability of the temporal manifold.

### 4.5 Experimental Implications

The TEP framework makes concrete, falsifiable predictions that distinguish it from standard QFT. In the unscreened regime, where the local interaction energy density is well below the saturation scale *ρ_{T}*, the conformal factor *A(φ)* deviates from unity. While high-energy particle collisions (TeV-scale, with characteristic local energy densities of order *10^{24} g/cm^{3}*) are deep in the screened limit, low-energy, long-baseline atomic interferometry in ultra-high-vacuum environments may probe the unscreened regime.

Order-of-magnitude estimate: For a conformal factor *A(φ) = exp(β_{A} φ / M_{Pl})*, the fractional mass shift in a region of ambient density *ρ* below the saturation scale is parametrically *δm/m ~ (1 − A) &sim; β_{A} φ / M_{Pl}*. The scalar field *φ* scales with the local energy density; in the linear regime well below *ρ_{T}*, *φ / M_{Pl} ~ ρ / ρ_{T}*. For an ultra-high-vacuum environment with *ρ ~ 10^{−15} g/cm^{3}* and *ρ_{T} ~ 20 g/cm^{3}*, the ratio is *ρ / ρ_{T} ~ 5 × 10^{−17}*. With a coupling *β_{A} ~ O(1)*, the predicted fractional mass shift is:

δm/m ~ 5 × 10^{−17}

For a cold-atom interferometer with a baseline *L ~ 10 m* and interrogation time *T ~ 1 s*, the phase shift due to a fractional mass variation is *δΦ ~ k L δm/m*, where *k* is the atomic wave number. For rubidium-87 atoms with *k ~ 10^{7} m^{−1}*, the predicted phase shift is *δΦ ~ 5 × 10^{−9} rad*, which is within reach of state-of-the-art atom interferometers (current sensitivity *~ 10^{−10} rad / √Hz* with shot-noise-limited detection). The signal grows linearly with baseline and is distinguishable from standard gravity gradients because it correlates with the temporal shear *Σ_{μ}* rather than the Newtonian potential. Because the unscreened signal relies on the local interaction energy density remaining well below *ρ_{T} ≈ 20 g/cm^{3}* along the entire flight path, the full 10 m vacuum pipe must sustain ultra-high vacuum (*ρ &lsim; 10^{−15} g/cm^{3}*) with no localized high-density hardware or residual-gas pockets that could engage continuous screening, suppress *Σ_{μ}* along part of the baseline, and collapse the predicted phase before it is resolved.

The companion paper TEP-KIN (Paper 25) develops specific experimental protocols for laboratory interferometry and has provided empirical support via graphene Aharonov-Bohm data. TEP-SPIN (Paper 24) addresses subatomic structure and spin-dependent measurements.

### 4.6 The Spinor: A Historical Reinterpretation

In 1928, Dirac derived the spinor as the mathematical object required to linearize the Klein-Gordon equation. The spinor was introduced as a four-component complex vector that transforms under the Lorentz group via a double-valued representation. Dirac showed that the spinor "internal space" was necessary to accommodate both positive- and negative-energy solutions while preserving Lorentz covariance. The algebraic machinery — Clifford algebra, gamma matrices, charge conjugation — was taken as fundamental.

The TEP framework offers a geometric reinterpretation. Dirac was attempting to describe physical temporal-orientation holonomy without access to a dynamical proper-time geometry. The "internal space" of the spinor is understood as an encoding of geometric orientation data (the direction of temporal shear circulation) into an algebraic object defined on a flat, isochronous background.

The four components of the Dirac spinor correspond to:

- *Upper two components:* Particle with spin up/down relative to the local temporal shear circulation.

- *Lower two components:* Antiparticle with reversed proper-time phase orientation (the "negative-energy" solutions).

In the TEP framework, these are not components of an abstract internal vector space. They are the four possible combinations of (topological charge orientation) × (phase direction) on the two-sheeted temporal manifold. The Clifford algebra is not an abstract symmetry; it is the local algebra of frame rotations in the temporal orientation bundle. The gamma matrices are not fundamental operators; they are the generators of infinitesimal rotations in the proper-time phase frame. Dirac's spinor was an effective mathematical workaround for a geometric structure that physics had not yet developed.

This reinterpretation is not a dismissal of Dirac's work; it is an elevation. The Dirac equation remains an accurate description of relativistic quantum mechanics in the screened limit. But its algebraic structure, which appeared fundamental in 1928, is now revealed as the natural geometric language of a deeper temporal topology.

## 5. Conclusion

This paper recovers five foundational results that subsume standard Quantum Field Theory within the Temporal Equivalence Principle:

- *The phase action* *S = −mc^{2} ∫ dτ̃* is the primitive geometric driver, with mass appearing as the parameter governing the oscillator frequency *ω_{0} = mc^{2} / ℏ*, modulated by the conformal factor in the causal matter metric *g̃_{μν}*.

- *The Klein-Gordon equation* *(□̃ + m^{2}c^{2} / ℏ^{2}) Ψ = 0* is derived from the minimal geometric Lagrangian in the causal metric and verified via WKB / eikonal expansion; its eikonal limit recovers the *g̃*-Hamilton-Jacobi equation, not via operator substitution.

- *The Dirac operator* *iγ^{μ}∂_{μ} − m* is recovered as the local Clifford/tetrad representation in the isochronous background. It emerges as the limiting case of the geometric operator when temporal shear *Σ_{μ}* and disformal coupling *B(φ)* are negligible.

- *Spin and antimatter* are reinterpreted as geometric orientations on the two-sheeted proper-time manifold, not intrinsic quantum properties. Antimatter is the reversed proper-time phase orientation on the second sheet; CPT is preserved locally while the global two-sheeted topology isolates matter and antimatter topologically.

- *The spinor* is reinterpreted geometrically: Dirac's 1928 spinor encoded temporal-orientation holonomy without access to a dynamical proper-time geometry.

These results provide the quantum-foundation layer for the full TEP framework. All tensor-algebraic derivations have been verified symbolically using SymPy; the audit log is available in `results/sympy_audit.log`. The companion papers develop the implications for subatomic structure (TEP-SPIN), interaction kinematics (TEP-KIN), and cosmological synthesis (TEP-C0).

The standard quantum framework is recovered as the screened limit of the Temporal Equivalence Principle. In the screened limit, where the local interaction energy density substantially exceeds the saturation scale *ρ_{T}*, the conformal factor *A(φ) → 1* and the temporal shear is suppressed, reproducing the familiar Minkowski background. In the unscreened regime, the full geometric structure is manifest, and new phenomena become accessible. The broader conceptual implications — geometric entanglement, temporal-topology drag, and the geometric resolution to Bell non-locality — are introduced in Section 1.5 and developed in the companion papers TEP-SPIN and TEP-KIN.

## References

- Smawfield, M. L. (2025). *Temporal Equivalence Principle: Dynamic Time & Emergent Light Speed*. Preprint v0.9 (Jakarta). Zenodo. DOI: 10.5281/zenodo.16921911 (Paper 0)

- Smawfield, M. L. (2025). *Universal Critical Density: Cross-Scale Consistency of ρ_{T}*. Preprint v0.3 (New Delhi). Zenodo. DOI: 10.5281/zenodo.18064365 (Paper 6)

- Smawfield, M. L. (2026). *Temporal Equivalence Principle: Disformal Kinematics and the Measurement Landscape*. Preprint v0.1 (Kuala Lumpur). Zenodo (Paper 25)

- Smawfield, M. L. (2026). *Temporal Equivalence Principle: A Topological Fermion Model for Spin and the g−2 Anomaly*. Preprint v0.1 (Paris). Zenodo (Paper 24)

- Smawfield, M. L. (2026). *Temporal Equivalence Principle: A Covariant Alternative to Cosmic Expansion*. Preprint v0.1 (Athens). Zenodo. DOI: 10.5281/zenodo.20370144 (Paper 26)

- Dirac, P. A. M. (1928). The quantum theory of the electron. *Proc. R. Soc. A* 117(778), 610–624.

- Klein, O. & Gordon, W. (1928). Derivation of the relativistic wave equation. *Z. Phys.* 48(11–12), 897–903.

- Stückelberg, E. C. G. (1941). Relativistic invariance in the interaction of particles. *Helv. Phys. Acta* 14, 372–383.

- Feynman, R. P. (1949). The theory of positrons. *Phys. Rev.* 76(6), 749–759.

- Penrose, R. & Rindler, W. (1984). *Spinors and Space-Time*. Vol. 1. Cambridge University Press. §6.7.

## Appendix A: Detailed Derivations

### A.1 Tetrad Formalism in Curved Spacetime

In curved spacetime, the Dirac spinor cannot be defined directly on the manifold. A local orthonormal frame (tetrad) *e^{a}_{μ}* is required at each point, satisfying:

g_{μν} = e^{a}_{μ} e^{b}_{ν} η_{ab}

where *η_{ab}* is the Minkowski metric. The inverse tetrad *e_{a}^{μ}* satisfies *e^{a}_{μ} e_{a}^{ν} = δ^{ν}_{μ}*. The Dirac matrices in curved spacetime are defined as:

γ^{μ} = e_{a}^{μ} γ^{a}

where *γ^{a}* are the constant flat-space Dirac matrices satisfying the Clifford algebra *{γ^{a}, γ^{b}} = 2η^{ab}*.

### A.2 Spin Connection

The spin-covariant derivative incorporates the spin connection *ω^{ab}_{μ}*:

∇_{μ} = ∂_{μ} + (1/4) ω^{ab}_{μ} σ_{ab}

where *σ_{ab} = (1/2)[γ_{a}, γ_{b}]* are the Lorentz generators. The spin connection is related to the tetrad by:

ω^{ab}_{μ} = e^{a}_{ν} ∇_{μ} e_{b}^{ν}

In the flat-frame limit where the tetrad becomes the identity (*e^{a}_{μ} → δ^{a}_{μ}*), the spin connection vanishes and the covariant derivative reduces to the ordinary partial derivative.

### A.3 Conformal Transformation of the Dirac Operator

Under the conformal transformation *g̃_{μν} = A^{2}(φ) g_{μν}*, the tetrad rescales as *e^{a}_{μ} → A(φ) e^{a}_{μ}*. The Dirac operator therefore acquires both a direct tetrad rescaling and additional terms from the modified spin connection. The explicit transformation is non-trivial because the spin connection depends on derivatives of *A(φ)*; see e.g. Penrose & Rindler [10]. When *A(φ) = 1* (screened limit, where the local interaction energy density substantially exceeds *ρ_{T}*), the conformal transformation is trivial and the standard Dirac operator is recovered.

The full tetrad algebra factorisation — from the geometric Dirac operator *(i e^{μ}_{a} γ^{a} ∇_{μ} − m) ψ = 0* to the standard flat-space form *(iγ^{μ}∂_{μ} − m)ψ = 0* under the flattening conditions *Σ_{μ} = 0*, *B(φ)(∇φ)^{2} → 0* — has been verified symbolically using SymPy. The audit log documenting each algebraic step (Clifford algebra verification, tetrad identity, spin connection vanishing, operator collapse, and disformal signpost) is available in `results/sympy_audit.log`. The corresponding derivation scripts are in `scripts/derivations/`.

### A.3b Disformal Departure from Conformal Collapse

On the full Jakarta ansatz *g̃_{μν} = A^{2}(φ) g_{μν} + B(φ) ∇_{μ}φ ∇_{ν}φ*, the conformal sector alone is tetrad-rescalable. The disformal term is rank-one and generates off-diagonal matter-frame components *g̃_{μν} = B(φ) ∇_{μ}φ ∇_{ν}φ* whenever *∇_{μ}φ ∇_{ν}φ* has support in both temporal and spatial directions. Identity tetrad collapse therefore requires suppression of the observable disformal response, not merely vanishing temporal shear. SymPy Audit 3b verifies this obstruction at the metric level; the complete disformal kinematics audit (inverse metric, *n*_{eff}, Christoffel symbols, holonomy sector) is implemented in TEP-KIN (Paper 25), which carries the full *g̃_{μν}* through interaction routing and measurement while this paper establishes the screened tangent limit recovered when *B(φ)(∇φ)^{2} → 0*.

### A.4 Holonomy of the Orientation Bundle

The temporal field carries an orientation bundle with structure group *O(1,3)*. Away from topological defects, the temporal shear *Σ_{μ} = ∇_{μ} ln A(φ)* is a smooth gradient, and by Stokes' theorem:

∮_{C} Σ_{μ} dx^{μ} = ∮_{C} d(ln A) = 0

for any contractible loop in a simply connected region where *A(φ)* is smooth and single-valued, as established in the original TEP theory, which assumes the exponential form *A(φ) = exp(β_{A} φ / M_{Pl})* everywhere. Non-zero holonomy arises only when the loop encircles a charge core where the scalar field diverges and *A(φ)* approaches its singular limit *A → ∞*. At such a singularity, *ln A(φ)* is multi-valued and the integral computes the winding number:

Δφ = ∮_{C} Σ_{μ} dx^{μ} = n · 4π, n ∈ ℤ

Single-valuedness of the phase field *Ψ = exp(iS/ℏ)* requires that *S/ℏ* change by an integer multiple of *2π* around any closed loop. The action *S* is related to the temporal shear *Σ_{μ}* through the phase transport equation *dS = ℏ Σ_{μ} dx^{μ}* (up to an overall constant of proportionality set by the topological charge), so the holonomy of *Σ* around the loop maps directly to the phase change. Because the spinor representation is double-valued — a *2π* rotation yields a sign change (*e^{iπ} = −1* for the fundamental representation) — the scalar phase field *Ψ* itself remains single-valued only after a *4π* circuit. The minimal non-trivial winding therefore requires *n = ±1* in the *4π* quantization, giving the two spin orientations. The local holonomy group is *SU(2)*, whose generators are the Pauli matrices.

### A.5 SymPy Audit Environment

The symbolic derivations were executed in a reproducible Python environment with the following pinned dependencies: Python 3.11, SymPy 1.12, NumPy 1.26, and SciPy 1.11. The primary derivation scripts — `derive_klein_gordon.py`, `derive_dirac_subsumption.py`, `derive_spin_holonomy.py`, and `sympy_audit.py` — are located in `scripts/derivations/`. The master audit verifies: (i) Clifford algebra closure for the rescaled Dirac matrices; (ii) tetrad identity *g_{μν} = e^{a}_{μ} e^{b}_{ν} η_{ab}* under conformal rescaling; (iii) spin-connection vanishing in the flat-frame limit *Σ_{μ} = 0*; (iv) operator collapse from the curved-space Dirac operator to the standard flat-space form; and (v) Audit 3b disformal signpost (rank-one obstruction to conformal collapse). To reproduce the audit independently, run `python scripts/run_all.py --audit` from the repository root; the master audit writes the step-by-step log to `results/sympy_audit.log`. The full disformal tensor audit is in TEP-KIN (Paper 25).


## 9. Data Availability & Reproducibility

This work follows open-science practices. All theoretical derivations and numerical results are fully reproducible using the documented code.


### Repository and Code

GitHub Repository: github.com/matthewsmawfield/TEP-QF

The repository contains the analytical derivations and numerical verification scripts for the TEP quantum-field framework, Dirac-operator anomaly, and spin–antimatter coupling.


### Repository Structure

TEP-QF/ ├── data/ │ ├── cobaya/ # Cobaya MCMC chains │ └── hi_class/ # TEP-CLASS implementation ├── scripts/ │ └── steps/ # Analysis pipeline steps ├── core/ # TEP shared constants and parameters ├── site/ │ └── components/ # Manuscript HTML sections ├── requirements.txt ├── CITATION.bib └── README.md ### Software Environment Key packages: NumPy, SciPy, SymPy, Matplotlib. The scripts have been tested on Python 3.10+.


### License

All code and manuscripts are released under CC-BY-4.0.