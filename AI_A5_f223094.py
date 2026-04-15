backtrack_calls   = 0   
backtrack_failures = 0  

def read_board(filename):
    board = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if line:
                board.append([int(ch) for ch in line])
    return board


def print_board(board):
    for r in range(9):
        if r in (3, 6):
            print("------+-------+------")
        row = ""
        for c in range(9):
            if c in (3, 6):
                row += "| "
            row += str(board[r][c]) + " "
        print(row)
    print()



def build_domains(board):
    """
    domains[r][c] = set of values still possible for cell (r,c).
    A pre-filled cell gets a single-element set.
    An empty cell starts with {1..9}.
    """
    domains = {}
    for r in range(9):
        for c in range(9):
            if board[r][c] != 0:
                domains[(r, c)] = {board[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
    return domains


def get_peers(r, c):
    """
    Return all cells that share a row, column, or 3x3 box with (r,c).
    These are the 'neighbours' in CSP terms.
    """
    peers = set()

    # same row
    for cc in range(9):
        if cc != c:
            peers.add((r, cc))

    # same column
    for rr in range(9):
        if rr != r:
            peers.add((rr, c))

    # same 3x3 box
    box_r = (r // 3) * 3
    box_c = (c // 3) * 3
    for rr in range(box_r, box_r + 3):
        for cc in range(box_c, box_c + 3):
            if (rr, cc) != (r, c):
                peers.add((rr, cc))

    return peers



def ac3(domains):
    """
    Enforce arc consistency.
    An arc (Xi, Xj) is consistent if for every value in Xi's domain
    there is at least one compatible value in Xj's domain.
    For Sudoku the only constraint is: Xi != Xj.

    Returns False if a domain is wiped out.
    """
    queue = []
    for cell in domains:
        for peer in get_peers(*cell):
            queue.append((cell, peer))

    while queue:
        xi, xj = queue.pop(0)

        if revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False   

            for xk in get_peers(*xi):
                if xk != xj:
                    queue.append((xk, xi))

    return True


def revise(domains, xi, xj):
    
    revised = False
    for val in list(domains[xi]):
        if domains[xj] == {val}:
            domains[xi].discard(val)
            revised = True
    return revised


def select_unassigned(domains, assigned):
    """
    Minimum Remaining Values (MRV): pick the unassigned cell with the
    smallest domain.  Ties broken by first found.
    """
    best = None
    best_size = 10   # larger than any domain

    for cell, dom in domains.items():
        if cell not in assigned and len(dom) < best_size:
            best = cell
            best_size = len(dom)

    return best


def forward_check(domains, assigned, cell, value):
    """
    After assigning 'value' to 'cell', remove 'value' from the domains
    of all unassigned peers.

    Returns (True, pruned) where pruned records what was removed so we
    can undo it on backtrack.
    Returns (False, pruned) if any peer's domain becomes empty.
    """
    pruned = []   

    for peer in get_peers(*cell):
        if peer not in assigned and value in domains[peer]:
            domains[peer].discard(value)
            pruned.append((peer, value))

            if len(domains[peer]) == 0:
                return False, pruned  

    return True, pruned


def undo_pruning(domains, pruned):
    for (cell, val) in pruned:
        domains[cell].add(val)


def backtrack(domains, assigned):
  
    global backtrack_calls, backtrack_failures
    backtrack_calls += 1

    if len(assigned) == 81:
        return assigned

    cell = select_unassigned(domains, assigned)

    for value in list(domains[cell]):

        assigned[cell] = value
        saved_domain = set(domains[cell])
        domains[cell] = {value}

        ok, pruned = forward_check(domains, assigned, cell, value)

        if ok:
            result = backtrack(domains, assigned)
            if result is not None:
                return result  

        undo_pruning(domains, pruned)
        domains[cell] = saved_domain
        del assigned[cell]

    backtrack_failures += 1
    return None


def solve(filename):
    """Solve one Sudoku puzzle file and print results."""
    global backtrack_calls, backtrack_failures
    backtrack_calls   = 0
    backtrack_failures = 0

    print("=" * 42)
    print(f"  File: {filename}")
    print("=" * 42)

    board = read_board(filename)
    print("Puzzle:")
    print_board(board)

    domains = build_domains(board)

    if not ac3(domains):
        print("AC-3 found puzzle unsolvable before search!\n")
        return

    assigned = {}
    for cell, dom in domains.items():
        if len(dom) == 1:
            assigned[cell] = next(iter(dom))

    result = backtrack(domains, assigned)

    if result is None:
        print("No solution found.\n")
    else:
        solution = [[0]*9 for _ in range(9)]
        for (r, c), v in result.items():
            solution[r][c] = v

        print("Solution:")
        print_board(solution)

    print(f"  BACKTRACK calls   : {backtrack_calls}")
    print(f"  BACKTRACK failures: {backtrack_failures}")
    print()


if __name__ == "__main__":

   import os
   script_dir = os.path.dirname(os.path.abspath(__file__))
   puzzles = [os.path.join(script_dir, name) for name in ["easy.txt", "medium.txt", "hard.txt", "evil.txt"]]

   for puzzle in puzzles:
        try:
            solve(puzzle)
        except FileNotFoundError:
            print(f"[!] File not found: {puzzle}  \n")