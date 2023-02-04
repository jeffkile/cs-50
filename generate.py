import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Make sure every value in the variables domain has the same number of letters as the variables length
        for variable in self.domains:
            items_to_remove = []
            for word in self.domains[variable]:
                if len(word) != variable.length:
                    items_to_remove.append(word)
            for item in items_to_remove:
                self.domains[variable].remove(item)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revision_was_made = False

        # For any pair of variables v1, v2, their overlap is either:
        #    None, if the two variables do not overlap; or
        #    (i, j), where v1's ith character overlaps v2's jth character
        overlaps = self.crossword.overlaps[x, y]
        if overlaps != None:
            (i, j) = overlaps

            # Remove from x if it's incompatable with y
            items_to_remove = []
            for word_in_x in self.domains[x]:
                found_a_match = False
                for word_in_y in self.domains[y]:
                    if word_in_x[i] == word_in_y[j]:
                        found_a_match = True
                        break
                if found_a_match == False:
                    items_to_remove.append(word_in_x)
                    revision_was_made = True

            for item in items_to_remove:
                self.domains[x].remove(item)

        return revision_was_made


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queue = arcs

        if queue is None:
            queue = []
            # Find all of the arcs by going through all of the variables and seeing if they intersect
            for var in self.domains:
                for neighbor in self.crossword.neighbors(var):
                    queue.append((var, neighbor))

        while len(queue) > 0:
            (x, y) = queue.pop()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check that all values are distinct
        for var1 in assignment:
            for var2 in assignment:
                if var1 != var2 and assignment[var1] == assignment[var2]:
                    return False
        # Passes distinct check

        # Check that every value is the correct length
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        # Passes size check

        # Check that there are no conflicts between neighboring variables
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Get neighbors
        neighbors = self.crossword.neighbors(var)
        word_to_num_ruled_out = {}
        for word in self.domains[var]:
            count = 0
            for neighbor in neighbors:
                # If neighbor has already been assigned then ignore it
                if neighbor in assignment:
                    continue
                for neighbor_word in self.domains[neighbor]:
                    if neighbor_word == word:
                        count = count + 1
                        break
            word_to_num_ruled_out[word] = count

        return dict(sorted(word_to_num_ruled_out.items(), key=lambda item: item[1]))

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        min_vals = float('inf')
        for var in self.domains:
            if var not in assignment and len(self.domains[var]) < min_vals:
                min_vals = len(self.domains[var])

        max_degree = float('-inf')
        chosen_var = None
        for var in self.domains:
            if var not in assignment and len(self.domains[var]) == min_vals:
                num_neighbors = len(self.crossword.neighbors(var))
                if num_neighbors > max_degree:
                    max_degree = num_neighbors
                    chosen_var = var

        return chosen_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment_new = assignment.copy()
            assignment_new[var] = value
            if self.consistent(assignment_new):
                # Possible speedup: Call AC-3 with all arcs of x
                result = self.backtrack(assignment_new)
                if result != None:
                    return result

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
