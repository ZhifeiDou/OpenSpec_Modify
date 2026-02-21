// ============================================================
// Sudoku Game — Puzzle Generator, Solver, and Game Logic
// ============================================================

(function () {
  'use strict';

  // --- Solver ---

  /**
   * Find all candidates for a cell in a 9x9 grid.
   * @param {number[][]} grid - 9x9 array, 0 = empty
   * @param {number} row
   * @param {number} col
   * @returns {number[]}
   */
  function getCandidates(grid, row, col) {
    const used = new Set();
    for (let i = 0; i < 9; i++) {
      used.add(grid[row][i]);
      used.add(grid[i][col]);
    }
    const boxR = Math.floor(row / 3) * 3;
    const boxC = Math.floor(col / 3) * 3;
    for (let r = boxR; r < boxR + 3; r++) {
      for (let c = boxC; c < boxC + 3; c++) {
        used.add(grid[r][c]);
      }
    }
    const candidates = [];
    for (let n = 1; n <= 9; n++) {
      if (!used.has(n)) candidates.push(n);
    }
    return candidates;
  }

  /**
   * Solve the grid using backtracking. Returns the number of solutions found
   * (stops after finding `limit` solutions).
   * @param {number[][]} grid - modified in place; restored if limit > 1
   * @param {number} limit - stop searching after this many solutions
   * @returns {number} number of solutions found (up to limit)
   */
  function solve(grid, limit) {
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (grid[r][c] === 0) {
          const candidates = getCandidates(grid, r, c);
          let count = 0;
          for (const n of candidates) {
            grid[r][c] = n;
            count += solve(grid, limit - count);
            if (count >= limit) {
              grid[r][c] = 0;
              return count;
            }
          }
          grid[r][c] = 0;
          return count;
        }
      }
    }
    return 1; // all cells filled — one solution found
  }

  /**
   * Solve and return the completed grid (first solution).
   * @param {number[][]} grid
   * @returns {number[][]|null}
   */
  function solveGrid(grid) {
    const copy = grid.map(row => row.slice());
    if (solve(copy, 1) === 1) return copy;
    return null;
  }

  // --- Grid Generator ---

  /**
   * Shuffle an array in place (Fisher-Yates).
   */
  function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  /**
   * Generate a complete valid 9x9 grid using randomized backtracking.
   * @returns {number[][]}
   */
  function generateCompleteGrid() {
    const grid = Array.from({ length: 9 }, () => Array(9).fill(0));

    function fill(pos) {
      if (pos === 81) return true;
      const r = Math.floor(pos / 9);
      const c = pos % 9;
      const candidates = shuffle(getCandidates(grid, r, c));
      for (const n of candidates) {
        grid[r][c] = n;
        if (fill(pos + 1)) return true;
      }
      grid[r][c] = 0;
      return false;
    }

    fill(0);
    return grid;
  }

  // --- Puzzle Creator ---

  const DIFFICULTY_MAP = {
    easy:   { min: 36, max: 40 },
    medium: { min: 41, max: 50 },
    hard:   { min: 51, max: 55 },
  };

  /**
   * Create a puzzle by removing cells from a complete grid.
   * Ensures the puzzle has a unique solution.
   * @param {string} difficulty - 'easy' | 'medium' | 'hard'
   * @returns {{ puzzle: number[][], solution: number[][] }}
   */
  function generatePuzzle(difficulty) {
    const solution = generateCompleteGrid();
    const puzzle = solution.map(row => row.slice());

    const { min, max } = DIFFICULTY_MAP[difficulty] || DIFFICULTY_MAP.medium;
    const targetEmpties = min + Math.floor(Math.random() * (max - min + 1));

    // Build a shuffled list of all 81 cell positions
    const positions = shuffle(
      Array.from({ length: 81 }, (_, i) => [Math.floor(i / 9), i % 9])
    );

    let empties = 0;
    for (const [r, c] of positions) {
      if (empties >= targetEmpties) break;
      const backup = puzzle[r][c];
      puzzle[r][c] = 0;

      // Check uniqueness — if more than 1 solution, restore
      if (solve(puzzle.map(row => row.slice()), 2) !== 1) {
        puzzle[r][c] = backup;
      } else {
        empties++;
      }
    }

    return { puzzle, solution };
  }

  // --- Game State ---

  let currentPuzzle = null;   // number[][] (0 = empty)
  let currentSolution = null; // number[][]
  let playerGrid = null;      // number[][] (player's current state)
  let lockedCells = null;     // boolean[][]
  let selectedCell = null;    // { row, col } | null
  let timerInterval = null;
  let elapsedSeconds = 0;
  let gameOver = false;

  // --- DOM References ---

  const gridEl = document.getElementById('grid');
  const timerEl = document.getElementById('timer');
  const messageEl = document.getElementById('message');
  const difficultyEl = document.getElementById('difficulty');
  const newGameBtn = document.getElementById('new-game');
  const resetBtn = document.getElementById('reset');
  const checkBtn = document.getElementById('check');

  // --- Rendering ---

  function createGrid() {
    gridEl.innerHTML = '';
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.row = r;
        cell.dataset.col = c;

        // 3x3 box borders
        if (c % 3 === 0 && c !== 0) cell.classList.add('box-left');
        if (r % 3 === 0 && r !== 0) cell.classList.add('box-top');

        cell.addEventListener('click', () => onCellClick(r, c));
        gridEl.appendChild(cell);
      }
    }
  }

  function renderGrid() {
    const cells = gridEl.querySelectorAll('.cell');
    cells.forEach(cell => {
      const r = parseInt(cell.dataset.row);
      const c = parseInt(cell.dataset.col);
      const value = playerGrid[r][c];

      cell.textContent = value !== 0 ? value : '';
      cell.classList.toggle('locked', lockedCells[r][c]);
      cell.classList.toggle('player', !lockedCells[r][c] && value !== 0);
    });
    updateHighlights();
  }

  function updateHighlights() {
    const cells = gridEl.querySelectorAll('.cell');

    // Clear all highlights
    cells.forEach(cell => {
      cell.classList.remove('selected', 'related', 'conflict');
    });

    // Highlight selected cell and related cells
    if (selectedCell) {
      const { row, col } = selectedCell;
      const boxR = Math.floor(row / 3) * 3;
      const boxC = Math.floor(col / 3) * 3;

      cells.forEach(cell => {
        const r = parseInt(cell.dataset.row);
        const c = parseInt(cell.dataset.col);

        if (r === row && c === col) {
          cell.classList.add('selected');
        } else if (
          r === row || c === col ||
          (r >= boxR && r < boxR + 3 && c >= boxC && c < boxC + 3)
        ) {
          cell.classList.add('related');
        }
      });
    }

    // Conflict highlighting
    highlightConflicts(cells);
  }

  function highlightConflicts(cells) {
    // Build a set of conflicting positions
    const conflicts = new Set();

    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const val = playerGrid[r][c];
        if (val === 0) continue;

        // Check row
        for (let cc = 0; cc < 9; cc++) {
          if (cc !== c && playerGrid[r][cc] === val) {
            conflicts.add(r * 9 + c);
            conflicts.add(r * 9 + cc);
          }
        }
        // Check column
        for (let rr = 0; rr < 9; rr++) {
          if (rr !== r && playerGrid[rr][c] === val) {
            conflicts.add(r * 9 + c);
            conflicts.add(rr * 9 + c);
          }
        }
        // Check box
        const boxR = Math.floor(r / 3) * 3;
        const boxC = Math.floor(c / 3) * 3;
        for (let rr = boxR; rr < boxR + 3; rr++) {
          for (let cc = boxC; cc < boxC + 3; cc++) {
            if ((rr !== r || cc !== c) && playerGrid[rr][cc] === val) {
              conflicts.add(r * 9 + c);
              conflicts.add(rr * 9 + cc);
            }
          }
        }
      }
    }

    cells.forEach(cell => {
      const r = parseInt(cell.dataset.row);
      const c = parseInt(cell.dataset.col);
      cell.classList.toggle('conflict', conflicts.has(r * 9 + c));
    });
  }

  // --- Interaction ---

  function onCellClick(row, col) {
    if (gameOver) return;
    selectedCell = { row, col };
    updateHighlights();
  }

  function onKeyDown(e) {
    if (gameOver || !selectedCell) return;
    const { row, col } = selectedCell;

    if (lockedCells[row][col]) return; // can't edit pre-filled cells

    if (e.key >= '1' && e.key <= '9') {
      playerGrid[row][col] = parseInt(e.key);
      renderGrid();
      clearMessage();
    } else if (e.key === 'Backspace' || e.key === 'Delete') {
      playerGrid[row][col] = 0;
      renderGrid();
      clearMessage();
    } else if (e.key === 'ArrowUp' && selectedCell.row > 0) {
      selectedCell.row--;
      updateHighlights();
    } else if (e.key === 'ArrowDown' && selectedCell.row < 8) {
      selectedCell.row++;
      updateHighlights();
    } else if (e.key === 'ArrowLeft' && selectedCell.col > 0) {
      selectedCell.col--;
      updateHighlights();
    } else if (e.key === 'ArrowRight' && selectedCell.col < 8) {
      selectedCell.col++;
      updateHighlights();
    }
  }

  // --- Timer ---

  function startTimer() {
    stopTimer();
    elapsedSeconds = 0;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
      elapsedSeconds++;
      updateTimerDisplay();
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  function updateTimerDisplay() {
    const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
    const secs = String(elapsedSeconds % 60).padStart(2, '0');
    timerEl.textContent = mins + ':' + secs;
  }

  // --- Messages ---

  function showMessage(text, type) {
    messageEl.textContent = text;
    messageEl.className = 'message ' + (type || '');
  }

  function clearMessage() {
    messageEl.textContent = '';
    messageEl.className = 'message';
  }

  // --- Game Controls ---

  function newGame() {
    const difficulty = difficultyEl.value;
    const { puzzle, solution } = generatePuzzle(difficulty);

    currentPuzzle = puzzle;
    currentSolution = solution;
    playerGrid = puzzle.map(row => row.slice());
    lockedCells = puzzle.map(row => row.map(v => v !== 0));
    selectedCell = null;
    gameOver = false;

    clearMessage();
    renderGrid();
    startTimer();
  }

  function resetPuzzle() {
    if (!currentPuzzle) return;
    playerGrid = currentPuzzle.map(row => row.slice());
    selectedCell = null;
    gameOver = false;

    clearMessage();
    renderGrid();
    startTimer();
  }

  function checkSolution() {
    if (!playerGrid) return;

    // Check if all cells are filled
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (playerGrid[r][c] === 0) {
          showMessage('Puzzle is incomplete — fill in all cells first.', 'warning');
          return;
        }
      }
    }

    // Check if solution matches
    let correct = true;
    const incorrectCells = [];
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (playerGrid[r][c] !== currentSolution[r][c]) {
          correct = false;
          incorrectCells.push([r, c]);
        }
      }
    }

    if (correct) {
      stopTimer();
      gameOver = true;
      const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
      const secs = String(elapsedSeconds % 60).padStart(2, '0');
      showMessage('Congratulations! Solved in ' + mins + ':' + secs + '!', 'success');
    } else {
      // Highlight incorrect cells
      const cells = gridEl.querySelectorAll('.cell');
      const incorrectSet = new Set(incorrectCells.map(([r, c]) => r * 9 + c));
      cells.forEach(cell => {
        const r = parseInt(cell.dataset.row);
        const c = parseInt(cell.dataset.col);
        cell.classList.toggle('conflict', incorrectSet.has(r * 9 + c));
      });
      showMessage('Some cells are incorrect — keep trying!', 'error');
    }
  }

  // --- Init ---

  function init() {
    createGrid();

    document.addEventListener('keydown', onKeyDown);
    newGameBtn.addEventListener('click', newGame);
    resetBtn.addEventListener('click', resetPuzzle);
    checkBtn.addEventListener('click', checkSolution);

    newGame();
  }

  init();
})();
