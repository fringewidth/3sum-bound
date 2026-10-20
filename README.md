# Deterministic 3SUM: exponent 1.920279461

This fork of [JoshuaQFEX/3sum-bound](https://github.com/JoshuaQFEX/3sum-bound)
exports the exact rational target **1920279461/1000000000 = 1.920279461**.
The predecessor exported 4800699/2500000 = 1.9202796.

**Authorship.** Claude Opus 5.5 (Anthropic) wrote this refinement. Hrishik Sai
Bojnal ([fringewidth](https://github.com/fringewidth)) published it.

The entry point in [Submission.lean](Submission.lean) is:

```lean
theorem Race.bound :
    EndStatement.ThreeSum.SolvedInTime ((1920279461 : Rat) / 1000000000) := by
  exact ThreeSum.solvedInTime_1920279461_1000000000
```

## What changes

The construction, the entropy ledger, the logarithm intervals and the principal
cost certificate 1.92027946 come from Joshua Wharton's revision unchanged. The
largest ledger term stays at `156432807976/81463563795`, about 1.9202794561.
This fork only shrinks the strict margins of the runtime chain above the
certificate.

| Stage | Predecessor | This fork |
|---|---:|---:|
| Principal cost certificate | 1.92027946 | 1.92027946 |
| Fixed block threshold `K` | `10^8` | `10^11` |
| Finite-block certificate | 1.92027957 | 1.9202794602 |
| Frontend budget | 1.92027958 | 1.9202794604 |
| Executed colored solver | 1.92027959 | 1.9202794606 |
| Micro allowance bound and final gap | `10^-8` | `10^-10` |
| Exported benchmark target | 1.9202796 | 1.920279461 |

With `K >= 10^11`, the finite-block terms `8/K` and `10/K` are at most
`10^-10`, below the first gap of `2 * 10^-10`. The allowance `1/(100 K^2)` is at
most `10^-24`. The threshold `K` is chosen once by `Classical.choose`, so no
computation depends on its size.

The diff touches 16 Lean files and the runtime margins of
[rational_certificate_refined.json](refinement/rational_certificate_refined.json).
Each change is a constant in a margin lemma, a `K` hypothesis or a target
literal. The exact-arithmetic checker passes:

```bash
python3 refinement/verify_certificate.py \
  --certificate refinement/rational_certificate_refined.json \
  --parameters Submission/ThreeSum/TernaryParameters.lean \
  --runtime-root .
```

## Verification

The full 1,198-module build and axiom audit run in
[.github/workflows/verify.yml](.github/workflows/verify.yml), unchanged from the
predecessor. [Run 39454903915](https://github.com/fringewidth/3sum-bound/actions/runs/39454903915)
on commit `6a0740d542fae76b25736de4563d22108d2ec21b` passed the certificate
check, the full build and the axiom audit.

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
