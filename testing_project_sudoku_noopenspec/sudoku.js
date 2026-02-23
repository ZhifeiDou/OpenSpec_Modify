(function () {
  'use strict';

  // --- Sudoku Solver ---

  function solve(board, maxSolutions) {
    maxSolutions = maxSolutions || 2;
    let count = 0;

    function backtrack(b) {
      if (count >= maxSolutions) return;
      const empty = findEmpty(b);
      if (!empty) {
        count++;
        return;
      }
      const [r, c] = empty;
      for (let num = 1; num <= 9; num++) {
        if (isValid(b, r, c, num)) {
          b[r][c] = num;
          backtrack(b);
          if (count >= maxSolutions) return;
          b[r][c] = 0;
        }
      }
    }

    const copy = board.map(row => row.slice());
    backtrack(copy);
    return count;
  }

  function findEmpty(board) {
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (board[r][c] === 0) return [r, c];
      }
    }
    return null;
  }

  function isValid(board, row, col, num) {
    for (let c = 0; c < 9; c++) {
      if (c !== col && board[row][c] === num) return false;
    }
    for (let r = 0; r < 9; r++) {
      if (r !== row && board[r][col] === num) return false;
    }
    const boxR = Math.floor(row / 3) * 3;
    const boxC = Math.floor(col / 3) * 3;
    for (let r = boxR; r < boxR + 3; r++) {
      for (let c = boxC; c < boxC + 3; c++) {
        if ((r !== row || c !== col) && board[r][c] === num) return false;
      }
    }
    return true;
  }

  // --- Puzzle Generation ---

  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  function generateSolution() {
    const board = Array.from({ length: 9 }, () => Array(9).fill(0));

    function fill(b) {
      const empty = findEmpty(b);
      if (!empty) return true;
      const [r, c] = empty;
      const nums = shuffle([1, 2, 3, 4, 5, 6, 7, 8, 9]);
      for (const num of nums) {
        if (isValid(b, r, c, num)) {
          b[r][c] = num;
          if (fill(b)) return true;
          b[r][c] = 0;
        }
      }
      return false;
    }

    fill(board);
    return board;
  }

  function createPuzzle(solution, difficulty) {
    const cellsToRemove = {
      easy: 36,
      medium: 46,
      hard: 52
    };

    const remove = cellsToRemove[difficulty] || 36;
    const puzzle = solution.map(row => row.slice());

    // Build list of all filled positions, shuffle them
    const positions = [];
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        positions.push([r, c]);
      }
    }
    shuffle(positions);

    let removed = 0;
    for (const [r, c] of positions) {
      if (removed >= remove) break;
      const saved = puzzle[r][c];
      puzzle[r][c] = 0;

      // Check uniqueness
      if (solve(puzzle, 2) !== 1) {
        // Not unique, put it back
        puzzle[r][c] = saved;
      } else {
        removed++;
      }
    }

    return puzzle;
  }

  // --- Game State ---

  let solution = [];
  let puzzle = [];       // initial given cells (0 = empty)
  let board = [];        // current player state
  let selectedCell = null; // {row, col}
  let difficulty = 'easy';

  // --- DOM References ---

  const boardEl = document.getElementById('board');
  const winOverlay = document.getElementById('win-overlay');
  const difficultyBtns = document.querySelectorAll('.difficulty-btn');
  const numBtns = document.querySelectorAll('.num-btn');
  const newGameBtn = document.getElementById('new-game-btn');
  const winNewGameBtn = document.getElementById('win-new-game-btn');

  // --- Rendering ---

  function renderBoard() {
    boardEl.innerHTML = '';
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.row = r;
        cell.dataset.col = c;

        // 3x3 box borders
        if (c === 2 || c === 5) cell.classList.add('border-right');
        if (r === 2 || r === 5) cell.classList.add('border-bottom');

        // Value
        const val = board[r][c];
        if (val !== 0) cell.textContent = val;

        // Given cell
        if (puzzle[r][c] !== 0) {
          cell.classList.add('given');
        }

        cell.addEventListener('click', () => selectCell(r, c));
        boardEl.appendChild(cell);
      }
    }
    updateHighlights();
  }

  function getCellEl(row, col) {
    return boardEl.children[row * 9 + col];
  }

  function updateHighlights() {
    // Clear all highlights
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const el = getCellEl(r, c);
        el.classList.remove('selected', 'same-number', 'conflict');
      }
    }

    // Conflict highlighting
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const val = board[r][c];
        if (val !== 0 && hasConflict(r, c, val)) {
          getCellEl(r, c).classList.add('conflict');
        }
      }
    }

    // Selected cell and same-number highlighting
    if (selectedCell) {
      const { row, col } = selectedCell;
      getCellEl(row, col).classList.add('selected');

      const selectedVal = board[row][col];
      if (selectedVal !== 0) {
        for (let r = 0; r < 9; r++) {
          for (let c = 0; c < 9; c++) {
            if (board[r][c] === selectedVal && (r !== row || c !== col)) {
              getCellEl(r, c).classList.add('same-number');
            }
          }
        }
      }
    }
  }

  // --- Conflict Detection ---

  function hasConflict(row, col, val) {
    // Row
    for (let c = 0; c < 9; c++) {
      if (c !== col && board[row][c] === val) return true;
    }
    // Column
    for (let r = 0; r < 9; r++) {
      if (r !== row && board[r][col] === val) return true;
    }
    // Box
    const boxR = Math.floor(row / 3) * 3;
    const boxC = Math.floor(col / 3) * 3;
    for (let r = boxR; r < boxR + 3; r++) {
      for (let c = boxC; c < boxC + 3; c++) {
        if ((r !== row || c !== col) && board[r][c] === val) return true;
      }
    }
    return false;
  }

  // --- Win Detection ---

  function checkWin() {
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (board[r][c] === 0) return false;
        if (hasConflict(r, c, board[r][c])) return false;
      }
    }
    return true;
  }

  // --- Interaction ---

  function selectCell(row, col) {
    selectedCell = { row, col };
    updateHighlights();
  }

  function inputNumber(num) {
    if (!selectedCell) return;
    const { row, col } = selectedCell;

    // Cannot edit given cells
    if (puzzle[row][col] !== 0) return;

    board[row][col] = num; // 0 = erase

    const cellEl = getCellEl(row, col);
    cellEl.textContent = num === 0 ? '' : num;

    updateHighlights();

    if (num !== 0 && checkWin()) {
      winOverlay.classList.remove('hidden');
    }
  }

  // --- New Game ---

  function newGame() {
    winOverlay.classList.add('hidden');
    selectedCell = null;
    solution = generateSolution();
    puzzle = createPuzzle(solution, difficulty);
    board = puzzle.map(row => row.slice());
    renderBoard();
  }

  // --- Event Listeners ---

  // Difficulty buttons
  difficultyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      difficultyBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      difficulty = btn.dataset.difficulty;
      newGame();
    });
  });

  // Number pad
  numBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      inputNumber(parseInt(btn.dataset.num, 10));
    });
  });

  // Keyboard input
  document.addEventListener('keydown', (e) => {
    if (e.key >= '1' && e.key <= '9') {
      inputNumber(parseInt(e.key, 10));
    } else if (e.key === 'Backspace' || e.key === 'Delete') {
      inputNumber(0);
    } else if (e.key === 'ArrowUp' && selectedCell) {
      selectCell(Math.max(0, selectedCell.row - 1), selectedCell.col);
    } else if (e.key === 'ArrowDown' && selectedCell) {
      selectCell(Math.min(8, selectedCell.row + 1), selectedCell.col);
    } else if (e.key === 'ArrowLeft' && selectedCell) {
      selectCell(selectedCell.row, Math.max(0, selectedCell.col - 1));
    } else if (e.key === 'ArrowRight' && selectedCell) {
      selectCell(selectedCell.row, Math.min(8, selectedCell.col + 1));
    }
  });

  // New Game buttons
  newGameBtn.addEventListener('click', newGame);
  winNewGameBtn.addEventListener('click', newGame);

  // --- Start ---
  newGame();
})();
