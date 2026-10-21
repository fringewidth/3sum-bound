# Deterministic 3SUM: exponent 1.92027942879891253

This fork of [JoshuaQFEX/3sum-bound](https://github.com/JoshuaQFEX/3sum-bound)
exports the exact rational target
**4800698571997281331/2500000000000000000 = 1.9202794287989125324**.
The previous revision exported 192027945701/100000000000 = 1.92027945701.

**Authorship.** Claude Opus 5.5 (Anthropic) wrote this refinement. Hrishik Sai
Bojnal ([fringewidth](https://github.com/fringewidth)) published it.

The entry point in [Submission.lean](Submission.lean) is:

```lean
theorem Race.bound :
    EndStatement.ThreeSum.SolvedInTime ((4800698571997281331 : Rat) / 2500000000000000000) := by
  exact ThreeSum.solvedInTime_4800698571997281331_2500000000000000000
```

## What changes

The construction and the cost ledger are c0ldzy17's and Joshua Wharton's. This
revision changes three things.

1. **Rebalanced parameters.** On the previous parameters the bank term
   `2B/H` (1.92027945607) sat 7e-8 above the query term `2 - G/H + 2Q/H`.
   The deficit trades one against the other, but the schedule fixes it to a
   multiple of `10^-8`, and the balance point lay between two grid points. A
   lattice search over `(pi1, pi2, deficit)` in steps of `(2, 3, 1) * 10^-8`
   (so that `alpha = (pi0 + pi1/2 + pi2/3, pi1/2 + pi2/3, pi2/3)` stays on the
   same grid) found `pi = (81204746, 15860450, 2934804) / 10^8` and
   `deficit = 1344861 / 10^8`. The exact ledger maximum there is
   1.92027942879891253, 2.6e-12 above the continuous optimum
   1.92027942879632. `y` and `z` are the Gibbs optima for these values, to
   `10^-10`.
1. **Tighter logarithm intervals.** 20 atanh terms instead of 16, endpoints
   rounded outward to `10^-20` (entropies to `10^-19`). The certificate
   `9601397143994562657/5000000000000000000` is the smallest value on the
   `10^-19` grid that clears every interval ledger bound and every
   cross-multiplied `linarith` slack.
1. **Runtime chain.** `K >= 10^20`, with the chain gaps of the previous
   revision divided by `10^7`: soft certificate + 2e-19, frontend + 4e-19,
   colored + 6e-19, micro bound 1e-19, target = certificate + 1e-18.

The target is 1.4e-18 above the exact ledger maximum at these parameters.

The schedule literals derived from the parameters (`fixedPi`, `fixedAlpha`,
`bankCut = 20385197`, `queryDeficit = 1344861`, `alphaRank = 10865029`, and the
`7930225 = pi1/2` and `978268 = alpha2` multiples) move with them.
[refinement/rebalance_parameters.py](refinement/rebalance_parameters.py)
generates the whole diff from commit `d13cca02`. The exact-arithmetic checker
passes:

```bash
python3 refinement/verify_certificate.py \
  --certificate refinement/rational_certificate_refined.json \
  --parameters Submission/ThreeSum/TernaryParameters.lean \
  --runtime-root .
```

## What is left

The bound is the ledger maximum of this construction plus a rational margin.
The ledger value is irrational, so any exported rational sits strictly above it.
Here the gap is about 1.4e-18. The remaining 2.6e-12 gap to the continuous
optimum would need a finer schedule length than `10^8 m`. A real improvement
needs a new construction.

## Verification

The full build and axiom audit run in
[.github/workflows/verify.yml](.github/workflows/verify.yml), unchanged from the
predecessor.

The files `verification.json`, `verification/` and `refinement/target_19202796.patch`
describe the predecessor revision. They are kept for provenance and do not
certify this fork.

## Attribution and license

- Joshua Wharton, QFEX: the refined entropy certificates and the 1.9202796
  revision this fork starts from. His README is kept in
  [docs/UPSTREAM_README_1.9202796.md](docs/UPSTREAM_README_1.9202796.md).
- [c0ldzy17](https://github.com/c0ldzy17/three-sum-lean): the algorithmic
  construction and the original full formalization.
- The authors credited in [METHOD.md](METHOD.md) and [NOTICE](NOTICE),
  including Josh Alman and Virginia Vassilevska Williams; Björklund, Husfeldt,
  Kaski and Koivisto; and Swapnil Jain.
- Anthropic's formalization supplies the benchmark statement, the word-RAM
  program logic and the compiler.

Copyright notices, [LICENSE](LICENSE) (Apache-2.0) and [NOTICE](NOTICE) are kept.

Problem and leaderboard: [Big O Speedrun, 3SUM](https://bigospeedrun.com/3sum).
