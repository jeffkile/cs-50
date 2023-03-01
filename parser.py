import nltk
import sys

nltk.download('punkt')


TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""


NONTERMINALS = """
S -> NP VP | NP VP NP | NP VP S | VP NP | VP NP S | S Conj S
NP -> N | N NP | Det NP | Adj NP | P NP
VP -> V | Adv | VP VP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    tokens = nltk.word_tokenize(sentence.lower())

    words = []
    for token in tokens:
        ok_to_add = False
        for char in token:
            if char.isalpha():
                ok_to_add = True
        if ok_to_add:
            words.append(token)

    return words

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    # Get all of the noun phrases
    np_trees = list(tree.subtrees(lambda t1: t1.label() == "NP"))

    chunks = []
    found_nouns = []
    for np_tree in np_trees:
        nouns = list(np_tree.subtrees(lambda t: t.label() == 'N'))
        # Get the root noun phrases that don't contain other nounts
        if len(nouns) == 1:
            # Add that noun phrase only once, add the full phrase
            if nouns[0] not in found_nouns:
                chunks.append(np_tree)
                found_nouns.append(nouns[0])

    return chunks

if __name__ == "__main__":
    main()
