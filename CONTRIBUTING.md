# Contributing to HyperCraft

Thank you for your interest in contributing to **HyperCraft**! We are building an immutable, spec-verified standard for high-craft frontend engineering, GPU graphics, and AI builder prompt architectures.

---

## 🎯 Contribution Principles

1. **Spec-Verified & Zero AI Slop:** Every new primitive, token, or algorithm must be backed by a primary standard (W3C, IETF RFC, IEEE) or peer-reviewed publication.
2. **Zero-Dependency Tests:** Any new algorithm in `tests/` should have zero heavy runtime dependencies where possible.
3. **No Breaking Links or Unchecked Evidence:** All new documentation links must use HTTPS and pass `python scripts/validate_links_and_refs.py`.

---

## 🚀 Good First Issues (Quick Ways to Jump In)

Looking for an easy way to contribute? Here are great starting points:

- [ ] **Prompt Wrappers for New IDEs:** Add a calibrated prompt wrapper in `06-budget-and-tool-aware-prompting/` for new tools (e.g., Cline, Roo Code, Claude Code).
- [ ] **Three.js TSL Material Recipes:** Add self-contained Three.js Shading Language (TSL) node material snippets in `02-3d-pbr-and-motion-engineering/`.
- [ ] **Expanded DGA Telemetry Samples:** Add hard-negative domain samples to `benchmarks/datasets/dga_domains_sample.csv`.
- [ ] **WCAG 2.2 SC 2.4.11 Focus Appearance:** Add focus-appearance contrast calculation tests to `tests/frontend_math.test.mjs`.

---

## 🛠️ Local Development & Testing

```bash
# 1. Run Python domain tests
python3 -m unittest discover -s tests -v

# 2. Run Node frontend math & loupe tests
node --test tests/frontend_math.test.mjs

# 3. Validate links and SHA-256 evidence digests
python3 scripts/validate_links_and_refs.py

# 4. Run benchmark smoke tests
python3 benchmarks/run_benchmarks.py --quick
```

---

## 📬 Submitting a Pull Request

1. Fork the repository and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. Commit your changes with clear semantic commit messages:
   ```bash
   git commit -m "feat(module): description of verified craft addition"
   ```
3. Ensure all tests and link validations pass locally.
4. Push to your fork and submit a Pull Request to `DHRUVASAI/frontend-hypercraft`.
