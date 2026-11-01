"""Geometric verification of the foldable litter box: clearances + fold sweeps."""
import sys, itertools
sys.path.insert(0, __import__('os').path.dirname(__file__))
import litterbox as L

MINGAP = 0.24     # required min clearance between separate shells (mm)
fails = []


def check(label, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + label + ('  ' + info if info else ''))
    if not ok:
        fails.append(label)


def gap(a, b):
    return a.min_gap(b, 3.0)


def inter_vol(a, b):
    return (a ^ b).volume()


def module_checks(name, md):
    t, lg, sh = md['tile'], md['long'], md['short']
    for (n1, p1), (n2, p2) in itertools.combinations([('tile', t), ('long', lg), ('short', sh)], 2):
        g = gap(p1, p2)
        check(f'{name}: deployed clearance {n1}/{n2}', g >= MINGAP, f'min gap {g:.3f}')
    # fold sequence A: long first (short upright), then short
    worst = 0.0
    for deg in range(0, 91, 3):
        l2 = L.fold_long(lg, md['a_long'], deg)
        v = inter_vol(l2, t) + inter_vol(l2, sh)
        worst = max(worst, v)
        if deg in (0, 90):
            g = min(gap(l2, t), gap(l2, sh))
            check(f'{name}: long wall clear at {deg} deg', g >= MINGAP * 0.9 or deg == 0 and g >= MINGAP * 0.9, f'min gap {g:.3f}')
    check(f'{name}: long wall fold sweep (short upright) no collision', worst < 1e-6, f'max overlap vol {worst:.4f}')
    l90 = L.fold_long(lg, md['a_long'], 90)
    worst = 0.0
    gmin = 99
    for deg in range(0, 91, 3):
        s2 = L.fold_short(sh, md['a_short'], deg, md['mirrored'])
        worst = max(worst, inter_vol(s2, t) + inter_vol(s2, l90))
        gmin = min(gmin, gap(s2, l90) if deg > 40 else 99)
    check(f'{name}: short wall fold sweep (long folded) no collision', worst < 1e-6, f'max overlap vol {worst:.4f}')
    check(f'{name}: short wall folded clearance over long wall', gmin >= 0.3, f'min gap {gmin:.3f}')
    # hinge stop: outward lean limited
    for deg, expect_hit in ((0.3, False), (4.0, True)):
        l2 = L.fold_long(lg, md['a_long'], -deg)
        hit = inter_vol(l2, t) > 1e-6
        check(f'{name}: long hinge stop at {-deg} deg: collision={hit}', hit == expect_hit)
        s2 = L.fold_short(sh, md['a_short'], -deg, md['mirrored'])
        hit = inter_vol(s2, t) > 1e-6
        check(f'{name}: short hinge stop at {-deg} deg: collision={hit}', hit == expect_hit)
    return


def all_pieces(mods, long_deg, short_deg):
    pieces = {}
    for k, md in mods.items():
        t, lg, sh = L.state(md, long_deg, short_deg)
        for part, geo in (('tile', t), ('long', lg), ('short', sh)):
            pieces[(k, part)] = L.place(geo, md['rot'])
    return pieces


def cross_overlaps(pieces, min_gap=None):
    bad = []
    for (ka, pa), (kb, pb) in itertools.combinations(pieces, 2):
        a, b = pieces[(ka, pa)], pieces[(kb, pb)]
        if ka == kb and (pa == 'tile' or pb == 'tile') and min_gap is None:
            continue
        v = inter_vol(a, b)
        if v > 1e-6:
            bad.append((ka, pa, kb, pb, f'overlap {v:.2f}'))
        elif min_gap is not None and ka != kb and not (pa == 'tile' and pb == 'tile'):
            g = gap(a, b)
            if g < min_gap:
                bad.append((ka, pa, kb, pb, f'gap {g:.3f}'))
    return bad


def box_checks(mods):
    """Whole-box checks.  Walls on the same side fold together (coaxial hinges
    + lap seam); all long walls fold first, then all short walls."""
    bad = cross_overlaps(all_pieces(mods, 0, 0), min_gap=0.2)
    check('box: deployed, no overlaps; cross-module gaps >= 0.2 (tiles mate flush)', not bad, str(bad[:6]))
    bad = cross_overlaps(all_pieces(mods, 90, 90), min_gap=0.2)
    check('box: fully folded, no overlaps; cross-module gaps >= 0.2', not bad, str(bad[:6]))
    bad = []
    for deg in range(0, 91, 5):                 # phase 1: long walls, shorts upright
        for b in cross_overlaps(all_pieces(mods, deg, 0)):
            bad.append((deg,) + b)
    check('box: fold phase 1 (all long walls 0->90, short walls up) collision-free', not bad, str(bad[:4]))
    bad = []
    for deg in range(0, 91, 5):                 # phase 2: short walls over folded long walls
        for b in cross_overlaps(all_pieces(mods, 90, deg)):
            bad.append((deg,) + b)
    check('box: fold phase 2 (all short walls 0->90, long walls folded) collision-free', not bad, str(bad[:4]))
    # unfold order is the reverse of the same states, so it is covered.


if __name__ == '__main__':
    mods = {}
    A = L.build_module('A'); Be = L.build_module('B_entry'); Bp = L.build_module('B_plain')
    mods['FL'] = dict(A, rot=False)
    mods['FR'] = dict(Be, rot=False)
    mods['BR'] = dict(A, rot=True)
    mods['BL'] = dict(Bp, rot=True)
    module_checks('A', A)
    module_checks('B_entry', Be)
    box_checks(mods)
    print('\nFAILED:' if fails else '\nALL CHECKS PASSED', len(fails), 'failure(s)')
    for f in fails:
        print(' -', f)
    sys.exit(1 if fails else 0)
