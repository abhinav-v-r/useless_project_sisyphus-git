import re

# ---------------------------------------------------------------------------
# Math / Science keyword lists
# ---------------------------------------------------------------------------

MATH_KEYWORDS = {
    # Core math vocabulary
    "algorithm", "function", "variable", "constant", "derivative", "integral",
    "matrix", "vector", "tensor", "scalar", "eigenvalue", "eigenvector",
    "polynomial", "equation", "inequality", "identity", "theorem", "proof",
    "lemma", "corollary", "axiom", "topology", "geometry", "algebra",
    "calculus", "differential", "gradient", "divergence", "curl", "laplacian",
    "fourier", "laplace", "transform", "series", "sequence", "convergence",
    "recursion", "iteration", "permutation", "combination", "probability",
    "distribution", "variance", "standard deviation", "mean", "median", "mode",
    "logarithm", "exponential", "modular", "prime", "factorial", "fibonacci",
    "binary", "hexadecimal", "boolean", "bitwise", "complexity", "asymptotic",
    "hypothesis", "inference", "regression", "optimization", "convex",
    "stochastic", "markov", "entropy", "information theory",

    # Science vocabulary
    "hypothesis", "empirical", "experiment", "observation", "data", "analysis",
    "synthesis", "catalyst", "reaction", "molecule", "atom", "nucleus",
    "electron", "proton", "neutron", "quantum", "photon", "energy", "mass",
    "momentum", "velocity", "acceleration", "force", "torque", "entropy",
    "enthalpy", "thermodynamics", "electromagnetic", "frequency", "wavelength",
    "amplitude", "resonance", "oscillation", "gravity", "relativity",
    "spacetime", "singularity", "wavefunction", "superposition", "coherence",
    "mitosis", "meiosis", "dna", "rna", "protein", "enzyme", "genome",
    "evolution", "natural selection", "mutation", "gene", "allele",
    "ecosystem", "metabolism", "photosynthesis", "cellular", "neural",
    "neuron", "synapse", "cortex", "cognitive", "simulation", "model",
    "parameter", "coefficient", "magnitude", "perpendicular", "parallel",
    "tangential", "radial", "logarithmic", "exponential",

    # Programming / CS terms (still scientific)
    "recursion", "complexity", "heuristic", "deterministic", "stochastic",
    "binary tree", "hash", "polynomial", "abstraction", "encapsulation",
}

# Patterns that strongly indicate math / science content
MATH_PATTERNS = [
    r'\b\d+(\.\d+)?\s*[\+\-\*\/\^]\s*\d+',            # arithmetic: 2 + 3, 5 * x
    r'[a-zA-Z]\s*[\+\-\*\/\^=<>]\s*[a-zA-Z0-9]',      # variable expressions: x = y, n + 1
    r'\b(O|Θ|Ω)\s*\(\s*\w[\w\s\^]*\)',                 # Big-O: O(n log n)
    r'\b\d+\s*(ms|ns|kb|mb|gb|hz|khz|mhz|ghz|rpm|nm|μm|mm|cm|km)\b',  # units
    r'\b(sin|cos|tan|log|ln|sqrt|exp|lim|sum|prod|∑|∏|∫|∂|∇|≈|≡|≤|≥)\b',  # math ops
    r'\b\d+(\.\d+)?\s*%',                              # percentage
    r'\b(theorem|proof|lemma|corollary)\b',             # formal math
    r'[A-Z][a-z]*\'s\s+(law|theorem|principle|equation|constant)',  # Newton's law etc.
    r'\b\d+\s*(times?|iterations?|steps?|rounds?|epochs?|layers?)\b',  # quantified process
    r'\b(because|therefore|thus|hence|since|given that|it follows)\b.*(math|science|physic|chem|bio|compute|formula|equation)',
]


class SentimentGate:
    def __init__(self):
        # Pre-compile all patterns for efficiency
        self._patterns = [re.compile(p, re.IGNORECASE) for p in MATH_PATTERNS]

    def check_despair(self, user_text: str) -> tuple[bool, float]:
        """
        Checks whether the user's explanation is mathematical or scientific.
        Returns (passes_gate, confidence_score).
        
        - passes_gate = True  → user spoke science, commit is allowed.
        - confidence_score    → 0.0–1.0 measure of how scientific the text is;
                                used as the despair/score value on the leaderboard.
        """
        text_lower = user_text.lower()
        words = set(re.findall(r"[a-z][a-z' ]*[a-z]|[a-z]", text_lower))
        word_count = max(len(user_text.split()), 1)

        # --- Keyword hits ---
        keyword_hits = sum(1 for kw in MATH_KEYWORDS if kw in text_lower)

        # --- Pattern hits ---
        pattern_hits = sum(1 for p in self._patterns if p.search(user_text))

        # --- Score: weighted combination, normalized to 0-1 ---
        # Each keyword hit = 0.15, each pattern hit = 0.25
        # Longer, richer answers are rewarded (log scale dampener removed for simplicity)
        raw = (keyword_hits * 0.15) + (pattern_hits * 0.25)
        confidence = min(raw, 1.0)

        # Threshold: must score at least 0.15 (≥1 keyword OR ≥1 pattern)
        passes = confidence >= 0.15

        return passes, confidence
