"""Rebalance the ternary 3SUM parameters and regenerate every dependent literal.

Run from the repository root of a checkout of sharpen-1920279456 (d13cca02).
"""
from fractions import Fraction as F
from pathlib import Path
import json
import re
import sys

ROOT = Path(sys.argv[1])
T = ROOT / 'Submission/ThreeSum'
PARAMS = T / 'TernaryParameters.lean'

N = 20
LOG_SCALE = 10**20
ENTROPY_SCALE = 10**19
S = 10**8

OLD = dict(n0=81204903, n1=15860350, n2=2934747, d=1344845)
NEW = dict(n1=15860450, n2=2934804, d=1344861)
NEW['n0'] = S - NEW['n1'] - NEW['n2']
Y = F(1816256201, 10**10)
Z = F(752397677, 10**10)

# Chain unit u: soft = C+2u, frontend = C+4u, colored = C+6u, micro bound u, target = C+10u.
U = F(1, 10**19)
K_MIN = 10**20


def derived(p):
    n0, n1, n2, d = p['n0'], p['n1'], p['n2'], p['d']
    return {
        'n0': n0, 'n1': n1, 'n2': n2, 'h1': n1 // 2, 'a2': n2 // 3,
        'a1': n1 // 2 + n2 // 3, 'a0': n0 + n1 // 2 + n2 // 3,
        'mean': n1 + 2 * n2, 'hmean': (n1 + 2 * n2) // 2,
        'cut': n1 + 2 * n2 - d, 'd': d,
    }


old, new = derived(OLD), derived(NEW)
assert NEW['n1'] % 2 == 0 and NEW['n2'] % 3 == 0
assert old['a2'] == 978249 and old['a1'] == 8908424 and old['a0'] == 90113327
assert old['cut'] == 20384999 and old['hmean'] == 10864922

pi = [F(new['n0'], S), F(new['n1'], S), F(new['n2'], S)]
alpha = [F(new['a0'], S), F(new['a1'], S), F(new['a2'], S)]
deficit = F(new['d'], S)
mean = pi[1] + 2 * pi[2]
assert alpha[0] == pi[0] + pi[1] / 2 + pi[2] / 3 and alpha[2] <= alpha[1] <= alpha[0]


def floor_q(x, scale):
    return F(x.numerator * scale // x.denominator, scale)


def ceil_q(x, scale):
    return -floor_q(-x, scale)


def round_bounds(b, scale):
    return floor_q(b[0], scale), ceil_q(b[1], scale)


def atanh_t(x):
    return (x - 1) / (x + 1)


def log_series(x):
    t = atanh_t(x)
    assert abs(t) < 1
    s = 2 * sum((t ** (2 * k + 1) / (2 * k + 1) for k in range(N)), F(0))
    e = 2 * abs(t) ** (2 * N + 1) / (1 - t * t)
    return s - e, s + e


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(c, a):
    return (c * a[0], c * a[1]) if c >= 0 else (c * a[1], c * a[0])


def ratio_positive(a, b):
    assert a[0] >= 0 and b[0] > 0
    return a[0] / b[1], a[1] / b[0]


values = {**{f'pi{i}': v for i, v in enumerate(pi)},
          **{f'alpha{i}': v for i, v in enumerate(alpha)},
          'three': F(3), 'y': Y, 'bankArg': 1 + Y + Y * Y, 'z': Z,
          'queryArg1': 1 + Z, 'queryArg2': 1 + Z + Z * Z}
exponents = {'pi0': 1, 'pi1': 3, 'pi2': 6, 'alpha0': 1, 'alpha1': 4, 'alpha2': 7,
             'three': -1, 'y': 3, 'z': 4}
normalized = {}
log_bounds = {'two': round_bounds(log_series(F(2)), LOG_SCALE)}
for name, v in values.items():
    if name in exponents:
        e = exponents[name]
        nv = v * F(2) ** e
        assert 1 <= nv < 2, (name, nv)
        normalized[name] = nv
        nb = round_bounds(log_series(nv), LOG_SCALE)
        log_bounds['normalized_' + name] = nb
        log_bounds[name] = round_bounds(plus(nb, times(-e, log_bounds['two'])), LOG_SCALE)
    else:
        log_bounds[name] = round_bounds(log_series(v), LOG_SCALE)


def isum(xs):
    out = (F(0), F(0))
    for x in xs:
        out = plus(out, x)
    return out


entropy_numerators = {
    'Hpi': isum(times(-v, log_bounds[f'pi{i}']) for i, v in enumerate(pi)),
    'Halpha': isum(times(-v, log_bounds[f'alpha{i}']) for i, v in enumerate(alpha)),
    'partitionEntropy': plus(times(pi[1], log_bounds['two']), times(pi[2], log_bounds['three'])),
    'bankEntropy': plus(log_bounds['bankArg'], times(-(mean - deficit), log_bounds['y'])),
    'queryEntropy': isum([times(pi[1], log_bounds['queryArg1']),
                          times(pi[2], log_bounds['queryArg2']),
                          times(-deficit, log_bounds['z'])]),
}
entropy_bounds = {name: round_bounds(ratio_positive(num, log_bounds['two']), ENTROPY_SCALE)
                  for name, num in entropy_numerators.items()}
H, Ha, G, B, Q = [entropy_bounds[n] for n in
                  ['Hpi', 'Halpha', 'partitionEntropy', 'bankEntropy', 'queryEntropy']]
ledger_upper = [2 * B[1] / H[0], 2 - G[0] / H[1] + 2 * Q[1] / H[0], 2 * Ha[1] / H[0],
                1 + G[1] / H[0], 2 - G[0] / H[1], F(1)]


def cross(c):
    return [c * H[0] - 2 * B[1], G[0] - 2 * Q[1] - (2 - c) * H[1], c * H[0] - 2 * Ha[1],
            (c - 1) * H[0] - G[1], G[0] - (2 - c) * H[1]]


# Smallest certificate on the 1e-19 grid with every cross-multiplied slack positive.
C = ceil_q(max(ledger_upper), 10**19)
while not (all(v < C for v in ledger_upper) and all(s > 0 for s in cross(C))):
    C += F(1, 10**19)
target = C + 10 * U
soft, frontend, colored = C + 2 * U, C + 4 * U, C + 6 * U
assert F(10, K_MIN) < soft - C and F(1, 100 * K_MIN ** 2) < U
assert G[0] / H[1] > F(2517, 10000) and H[0] > F(4, 5) and G[1] / H[0] < F(63, 250)


def frac(x):
    if x.denominator == 1:
        return str(x.numerator)
    return f'{x.numerator} / {x.denominator}'


def tight(x):
    return f'{x.numerator}/{x.denominator}'


def sub(text, pattern, repl, count=1):
    out, n = re.subn(pattern, repl, text, flags=re.S)
    assert n == count, (pattern, n)
    return out


# ---- TernaryParameters.lean ----
text = PARAMS.read_text()
defs = {'pi0': pi[0], 'pi1': pi[1], 'pi2': pi[2], 'alpha0': alpha[0], 'alpha1': alpha[1],
        'alpha2': alpha[2], 'y': Y, 'bankArg': values['bankArg'], 'z': Z,
        'queryArg1': values['queryArg1'], 'queryArg2': values['queryArg2'], 'deficit': deficit}
# alpha2 stays over the schedule length: projection_fiber_log_choose_bound closes
# (a2*m)/(10^8*m) = alpha2 with field_simp against this literal form.
literal = {name: frac(v) for name, v in defs.items()}
literal['alpha2'] = f"{new['a2']} / {S}"
for name in defs:
    text = sub(text, r'(\ndef ' + name + r' : ℝ := \().*?( : ℝ\)\n)',
               lambda m: m.group(1) + literal[name] + m.group(2))
text = sub(text, r'def certificateExponent : ℝ := [0-9 /]+\n',
           f'def certificateExponent : ℝ := {tight(C)}\n')
text = sub(text, r'def targetExponent : ℝ := [0-9 /]+\n', f'def targetExponent : ℝ := {tight(target)}\n')
for name, nv in normalized.items():
    text = sub(text, r'(private def normalized_' + name + r' : ℝ := \().*?( : ℝ\))',
               lambda m: m.group(1) + frac(nv) + m.group(2))
# Atanh parameters and series lengths, one block per direct logarithm.
direct_args = {**{'normalized_' + k: v for k, v in normalized.items()}, 'two': F(2),
               'bankArg': values['bankArg'], 'queryArg1': values['queryArg1'],
               'queryArg2': values['queryArg2']}
for name, x in direct_args.items():
    t = atanh_t(x)
    pattern = (r'(theorem log_' + name + r'_bounds :.*?Real\.sum_range_sub_log_div_le\n'
               r'\s*\(by norm_num : \|\(\().*?( : ℝ\) : ℝ\)\| < 1\) )\d+(\n.*?hratio : \(\(1 \+ \().*?'
               r'( : ℝ\)\) / \(1 - \().*?( : ℝ\)\) : ℝ\) = )')
    text = sub(text, pattern, lambda m: m.group(1) + frac(t) + m.group(2) + str(N) + m.group(3)
               + frac(t) + m.group(4) + frac(t) + m.group(5))
for name, b in log_bounds.items():
    var = '2' if name == 'two' else name
    text = sub(text, r'((?:private )?theorem log_' + re.escape(name) + r'_bounds\s*:\s*).*?( := by)',
               lambda m: m.group(1) + f'({frac(b[0])} : ℝ) ≤ Real.log {var} ∧ Real.log {var} ≤ ({frac(b[1])} : ℝ)' + m.group(2))
for name, b in entropy_bounds.items():
    text = sub(text, r'(theorem ' + re.escape(name) + r'_bounds\s*:\s*).*?( := by)',
               lambda m: m.group(1) + f'({frac(b[0])} : ℝ) ≤ {name} ∧ {name} ≤ ({frac(b[1])} : ℝ)' + m.group(2))
room = mean / 2 - deficit
text = sub(text, r'(theorem deficit_room : mean / 2 - deficit = \().*?( : ℝ\))',
           lambda m: m.group(1) + frac(room) + m.group(2))
text = sub(text, r'(theorem certificate_margin : targetExponent - certificateExponent = \().*?( : ℝ\))',
           lambda m: m.group(1) + frac(target - C) + m.group(2))
text = re.sub(r'\b978249\b', str(new['a2']), text)
for k in ['n0', 'n1', 'n2', 'a0', 'a1', 'd']:
    assert not re.search(r'\b%d\b' % old[k], text), k
PARAMS.write_text(text)

# ---- schedule literals in every other module ----
literal_map = {old[k]: new[k] for k in ['n0', 'n1', 'n2', 'h1', 'a2', 'a1', 'a0', 'mean', 'hmean', 'cut', 'd']}
for path in sorted(T.glob('*.lean')):
    if path == PARAMS:
        continue
    s = path.read_text()
    s2 = re.sub(r'\b(\d{6,})\b', lambda m: str(literal_map.get(int(m.group(1)), m.group(1))), s)
    if s2 != s:
        path.write_text(s2)

# CertifiedParameters mirror (rational, unused downstream).
jt = T / 'TernaryJointType.lean'
s = jt.read_text()
s = sub(s, r'def deficit : ℚ := [0-9 /]+\n', f'def deficit : ℚ := {frac(deficit)}\n')
s = sub(s, r'def bankY : ℚ := [0-9 /]+\n', f'def bankY : ℚ := {frac(Y)}\n')
s = sub(s, r'def queryZ : ℚ := [0-9 /]+\n', f'def queryZ : ℚ := {frac(Z)}\n')
jt.write_text(s)

# ---- runtime chain ----
OLD_C, OLD_T = F(1920279457, 10**9), F(192027945701, 10**11)
OLD_U, OLD_K = F(1, 10**12), 10**13


def q(x):
    return f'{x.numerator}/{x.denominator}'


chain = [
    ('1/1000000000000:', f'1/{U.denominator}:'),
    ('1/1000000000000 :', f'1/{U.denominator} :'),
    ('(1/500000000000 : ℝ)', f'({q(2 * U)} : ℝ)'),
    ('(1/125000000000 : ℝ)', f'({q(8 * U)} : ℝ)'),
    ('(3/500000000000 : ℝ)', f'({q(6 * U)} : ℝ)'),
    ('960139728501/500000000000', q(OLD_C + 2 * OLD_U)),  # placeholder, replaced below
]
soft_old, front_old, col_old = OLD_C + 2 * OLD_U, OLD_C + 4 * OLD_U, OLD_C + 6 * OLD_U
scalars = [(q(soft_old), q(soft)), (q(front_old), q(frontend)), (q(col_old), q(colored)),
           (q(OLD_T), q(target)),
           (f'({OLD_T.numerator} : Rat) / {OLD_T.denominator}',
            f'({target.numerator} : Rat) / {target.denominator}'),
           (f'{OLD_T.numerator}_{OLD_T.denominator}', f'{target.numerator}_{target.denominator}')]
chain = chain[:-1] + scalars
files = [ROOT / 'Submission.lean'] + sorted(T.glob('*.lean'))
for path in files:
    s = path.read_text()
    s2 = re.sub(r'\b%d\b' % OLD_K, str(K_MIN), s)
    for a, b in chain:
        s2 = s2.replace(a, b)
    if s2 != s:
        path.write_text(s2)

# ---- JSON certificate ----
jpath = ROOT / 'refinement/rational_certificate_refined.json'
report = json.loads(jpath.read_text())
report['method'] = f'Exact rational atanh series with absolute geometric remainder, N={N}'
report['log_bounds'] = {k: [str(v[0]), str(v[1])] for k, v in log_bounds.items()}
report['entropy_bounds'] = {k: [str(v[0]), str(v[1])] for k, v in entropy_bounds.items()}
report['certificate'] = str(C)
report['target'] = str(target)
report['ledger_upper'] = [str(v) for v in ledger_upper]
report['ledger_upper_decimal'] = [float(v) for v in ledger_upper]
report['cross_multiplication_slack'] = [str(v) for v in cross(C)]
report['runtime_margins'] = {
    'soft': str(soft), 'frontend': str(frontend), 'colored': str(colored), 'K_min': K_MIN,
    'micro_max': str(F(1, 100 * K_MIN ** 2)), 'micro_bound': str(U),
    'soft_minus_certificate': str(soft - C), 'target_minus_certificate': str(target - C),
    'target_minus_soft': str(target - soft), 'target_minus_frontend': str(target - frontend),
    'target_minus_colored': str(target - colored),
    'largest_ledger_to_certificate_gap': str(C - max(ledger_upper)),
}
jpath.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
print('certificate', C, float(C))
print('target', target, float(target))
print('ledger_upper', [float(v) for v in ledger_upper])
print('C - max ledger_upper', float(C - max(ledger_upper)))
