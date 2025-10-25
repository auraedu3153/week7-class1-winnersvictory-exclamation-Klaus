# tests/test_problem_01.py
# - pytest 파이프라인에서 동작하도록 설계됨
# - parameterize 미사용 (케이스별 함수 분리: 30개)
# - 대상 파일: 과제 루트의 problem_01.py (필요 시 TARGET 경로만 수정)

from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec
import random

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "problem_01.py"  # ← 학생 구현 파일 경로(필요 시 조정)


def load_module():
    name = "problem_01_under_test"
    loader = SourceFileLoader(name, str(TARGET))
    spec = spec_from_loader(name, loader)
    module = module_from_spec(spec)  # type: ignore
    loader.exec_module(module)       # 실제로 파일 실행
    return module


# ---------- Test helpers (오라클 & 보드 생성기) ----------

def _expected_for_8x8_block(block):
    """Return repaint count needed to make this 8x8 block chessboard-like."""
    # 두 가지 시작 패턴(W/B) 중 최소
    def mismatch(start_color):
        need = 0
        for i in range(8):
            for j in range(8):
                should = start_color if (i + j) % 2 == 0 else ('B' if start_color == 'W' else 'W')
                if block[i][j] != should:
                    need += 1
        return need
    return min(mismatch('W'), mismatch('B'))


def _oracle_min_repaints(board):
    """Reference solution used only for testing."""
    n, m = len(board), len(board[0])
    best = 64  # max repaint for 8x8 is 64, but actual worst is 32; keep safe upper bound
    for si in range(n - 7):
        for sj in range(m - 7):
            sub = [row[sj:sj+8] for row in board[si:si+8]]
            best = min(best, _expected_for_8x8_block(sub))
    return best


def _make_chess(n, m, start='W'):
    """n×m 완전 체스판 생성."""
    other = 'B' if start == 'W' else 'W'
    return [[(start if (i + j) % 2 == 0 else other) for j in range(m)] for i in range(n)]


def _flip(board, i, j):
    board[i][j] = 'B' if board[i][j] == 'W' else 'W'


def _clone(board):
    return [row[:] for row in board]


def _from_strings(lines):
    return [list(line) for line in lines]


# ---------- 30 test cases ----------

def test_problem_01_case_001_perfect_W_start_8x8():
    m = load_module()
    board = _make_chess(8, 8, 'W')
    want = 0
    got = m.min_count_of_squares(board)
    assert got == want == _oracle_min_repaints(board)

def test_problem_01_case_002_perfect_B_start_8x8():
    m = load_module()
    board = _make_chess(8, 8, 'B')
    want = 0
    got = m.min_count_of_squares(board)
    assert got == want == _oracle_min_repaints(board)

def test_problem_01_case_003_single_flip_from_perfect():
    m = load_module()
    board = _make_chess(8, 8, 'W')
    _flip(board, 3, 4)
    got = m.min_count_of_squares(board)
    want = _oracle_min_repaints(board)
    assert got == want

def test_problem_01_case_004_all_W_8x8():
    m = load_module()
    board = [['W'] * 8 for _ in range(8)]
    got = m.min_count_of_squares(board)
    # all same → 최소 32 칠해야 체스판 성립
    assert got == 32 == _oracle_min_repaints(board)

def test_problem_01_case_005_all_B_8x8():
    m = load_module()
    board = [['B'] * 8 for _ in range(8)]
    got = m.min_count_of_squares(board)
    assert got == 32 == _oracle_min_repaints(board)

def test_problem_01_case_006_10x10_contains_perfect_subboard():
    m = load_module()
    board = _make_chess(10, 10, 'W')
    # 일부 위치 뒤틀기(하지만 0~7,0~7은 유지)
    _flip(board, 8, 8)
    _flip(board, 9, 9)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_007_10x13_sample_like_dense_noise():
    m = load_module()
    board = _make_chess(10, 13, 'W')
    # 10x13 전역에 일정 패턴 노이즈 부여
    for i in range(10):
        for j in range(13):
            if (i * 7 + j * 5) % 11 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_008_13x10_transposed_noise():
    m = load_module()
    board = _make_chess(13, 10, 'B')
    for i in range(13):
        for j in range(10):
            if (i * 3 + j * 11) % 7 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_009_border_flips_on_perfect_8x8():
    m = load_module()
    board = _make_chess(8, 8, 'W')
    for k in range(8):
        _flip(board, 0, k)
        _flip(board, 7, k)
        _flip(board, k, 0)
        _flip(board, k, 7)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_010_checker_inverted_8x8():
    m = load_module()
    board = _make_chess(8, 8, 'W')
    # 모든 칸 뒤집어서 시작색 반전 → 여전히 정답 0
    for i in range(8):
        for j in range(8):
            _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_011_band_noise_rows():
    m = load_module()
    board = _make_chess(9, 12, 'W')
    for i in range(2, 7):  # row band
        for j in range(12):
            if j % 3 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_012_band_noise_cols():
    m = load_module()
    board = _make_chess(12, 9, 'B')
    for j in range(1, 8, 2):  # column band
        for i in range(12):
            if i % 4 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_013_exact_8xN_edge_minimal():
    m = load_module()
    board = _make_chess(8, 20, 'W')
    # 오른쪽 구간에 노이즈, 왼쪽 8x8은 완벽
    for i in range(8):
        for j in range(12, 20):
            if (i + j) % 3 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_014_exact_Nx8_edge_minimal():
    m = load_module()
    board = _make_chess(20, 8, 'B')
    for i in range(12, 20):
        for j in range(8):
            if (i + j) % 3 == 1:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_015_full_inversion_noise_9x9():
    m = load_module()
    board = _make_chess(9, 9, 'W')
    for i in range(9):
        for j in range(9):
            if (i * j) % 2 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_016_random_seeded_12x12_seed0():
    m = load_module()
    random.seed(0)
    board = [['W' if random.randint(0, 1) == 0 else 'B' for _ in range(12)] for _ in range(12)]
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_017_random_seeded_12x12_seed1():
    m = load_module()
    random.seed(1)
    board = [['W' if random.randint(0, 1) == 0 else 'B' for _ in range(12)] for _ in range(12)]
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_018_random_seeded_20x20_seed2():
    m = load_module()
    random.seed(2)
    board = [['W' if random.randint(0, 1) == 0 else 'B' for _ in range(20)] for _ in range(20)]
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_019_two_optimal_subboards_compete():
    m = load_module()
    board = _make_chess(9, 16, 'W')
    # 왼쪽 8x8 완벽, 오른쪽 8x8 거의 완벽(오차 소량)
    for i in range(8):
        for j in range(8, 16):
            if (i + j) % 7 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_020_small_noise_every_5th_cell():
    m = load_module()
    board = _make_chess(10, 10, 'B')
    cnt = 0
    for i in range(10):
        for j in range(10):
            cnt += 1
            if cnt % 5 == 0:
                _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_021_diagonal_noise():
    m = load_module()
    board = _make_chess(14, 14, 'W')
    for k in range(14):
        _flip(board, k, k)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_022_block_noise_3x3_tiles():
    m = load_module()
    board = _make_chess(15, 15, 'B')
    for bi in range(0, 15, 3):
        for bj in range(0, 15, 3):
            _flip(board, bi, bj)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_023_all_W_10x10():
    m = load_module()
    board = [['W'] * 10 for _ in range(10)]
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_024_all_B_10x10():
    m = load_module()
    board = [['B'] * 10 for _ in range(10)]
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_025_alternating_rows_same_color():
    m = load_module()
    # 짝수 행은 전부 W, 홀수 행은 전부 B → 체스판과는 다름
    board = []
    for i in range(10):
        row_color = 'W' if i % 2 == 0 else 'B'
        board.append([row_color] * 12)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_026_alternating_cols_same_color():
    m = load_module()
    # 짝수 열은 전부 W, 홀수 열은 전부 B
    board = []
    for i in range(12):
        row = [('W' if j % 2 == 0 else 'B') for j in range(10)]
        board.append(row)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_027_corner_noise_only():
    m = load_module()
    board = _make_chess(8, 12, 'W')
    for (i, j) in [(0, 0), (0, 11), (7, 0), (7, 11)]:
        _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_028_frame_noise():
    m = load_module()
    board = _make_chess(12, 8, 'B')
    for i in range(12):
        _flip(board, i, 0)
        _flip(board, i, 7)
    for j in range(8):
        _flip(board, 0, j)
        _flip(board, 11, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)

def test_problem_01_case_029_from_strings_literal_board():
    m = load_module()
    lines = [
        "BWBWBWBW",
        "WBWBWBWB",
        "BWBWBWBW",
        "WBWBWBWB",
        "BWBWBWBW",
        "WBWBWBWB",
        "BWBWBWBW",
        "WBWBWBWB",
    ]
    board = _from_strings(lines)
    got = m.min_count_of_squares(board)
    assert got == 0 == _oracle_min_repaints(board)

def test_problem_01_case_030_hard_mix_20x25_seed3():
    m = load_module()
    random.seed(3)
    board = [['W' if random.random() < 0.5 else 'B' for _ in range(25)] for _ in range(20)]
    # 후처리: 한 구역(5..12,7..14)을 반전해 지역적 왜곡
    for i in range(5, 13):
        for j in range(7, 15):
            _flip(board, i, j)
    got = m.min_count_of_squares(board)
    assert got == _oracle_min_repaints(board)
