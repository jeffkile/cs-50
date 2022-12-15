import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count > 0:
            return self.cells

        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)

    def danger_score(self):
        """
        A higher number means more dangerous
        """
        return self.count - len(self.cells)

    def get_random_cell(self):
        """
        Returns a random cell from self.cells
        """
        if len(self.cells) > 0:
            return random.sample(self.cells, 1)[0]
        return None

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #Debugging:
        #print(f"moving: {cell}")
        #print("knowledge:")
        #for sentence in self.knowledge:
        #    print(f"sentence: {sentence}")
        
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # Get the neighboring cells
        neighboring_cells = []
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Skip cells already in safes
                if (i, j) in self.safes:
                    continue

                # If it's a mine then reduce the count by 1 and ignore it
                if (i, j) in self.mines:
                    count = count - 1
                    continue

                # Add to list if the cell is in the bounds of the board and its not in our list of mines or moves made
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighboring_cells.append((i, j))

        self.knowledge.append(Sentence(neighboring_cells, count))

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        # Add this cell that was selected as a safe cell in all sentences 
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # This may reduce the size of some sentences which means we may be able to deduce that some sentences contains mines now

        # Go through all of the sentences and get a list of everything that is a mine:
        for sentence in self.knowledge:
            if sentence.known_mines() is not None:
                for mine in sentence.known_mines():
                    self.mines.add(mine)

        # Check all our sentences against our list of mines, if we find one remove the mine from that sentence and reduce that sentence's count
        for sentence in self.knowledge:
            for mine in self.mines:
                sentence.mark_mine(mine)

        # Now we may have a sentence whose score is 0 meaning it contains safes
        # So go through all of the sentences and get a list of everything that is safe:
        safes_to_add = []
        for sentence in self.knowledge:
            if sentence.known_safes() is not None:
                for safe in sentence.known_safes():
                    if safe not in safes_to_add:
                        safes_to_add.append(safe)

        for safe in safes_to_add:
            self.safes.add(safe)

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        # If we have two sentences set1 = count1 and set2 = count2 where set1 is a subset of set2,
        # then we can construct the new sentence set2 - set1 = count2 - count1
        sentences_to_add = []
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    new_sentence = Sentence(sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                    if new_sentence not in self.knowledge and new_sentence not in sentences_to_add:
                        sentences_to_add.append(new_sentence)

        for sentence in sentences_to_add:
            self.knowledge.append(sentence)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0 or len(self.safes) == len(self.moves_made):
            return None

        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        twice_board_size = self.width * self.height * 2

        cell = self.get_random_pick()
        count = 0;
        while cell in self.moves_made and count < twice_board_size:
            cell = self.get_random_pick()
            count = count + 1

        # Let's make sure this isn't on any lists where the danger score >= 0
        # where danger score is defined as the count minus the length of the list
        # For example {a, b, c, d, e, f} = 1 would be a good list to pick from
        # and {g, h, i} = 3 would be a bad list to chose from
        # However lets not try this forever as it may not be possible
        count = 0
        cont = True
        while count < twice_board_size and cont == True:
            for sentence in self.knowledge:
                count = count + 1
                if cell in sentence.cells and sentence.danger_score() >= 0:
                    cell = self.get_random_pick()
                    continue
            cont = False

        return cell

    def get_random_pick(self):
        # Pick a random i,j that isn't a mine
        i = None
        j = None
        count = 0 # A counter to make sure we don't loop forever
        while i == None or j == None or (i, j) in self.mines or (i, j) in self.moves_made or count > 2 * (self.width * self.height):
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)
            count = count + 1

        if count > 2 * (self.width * self.height):
            return None

        return (i, j)