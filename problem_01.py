# 요구사항은 https://www.acmicpc.net/problem/1018을 확인하세요
def min_count_of_squares(board: list[list[str]]) -> int:
    m = 64
    ans = [[0 if ('B' if (i+j)%2 else 'W') == board[i][j] else 1 for i in range(len(board))] for j in range (len(board[0]))]
    for i in range (len(board[0])-7):
        for j in range (len(board)-7):
            s = 0
            for x in range (8):
                for y in range (8):
                    s += ans[i+x][j+y]
            m = min(m, s, 64 - s)
    return m
