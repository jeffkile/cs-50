import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    default_prob_for_each_page = (1 - damping_factor) / len(corpus)

    page_to_probability = {}
    # Initiatlize the dictionary with the default probability
    for index in corpus:
        page_to_probability[index] = default_prob_for_each_page

    # If page has no outgoing links, then transition_model should return a probability distribution that chooses randomly among all pages with equal probability.  
    if len(list(corpus[page])) == 0:
        page_to_probability[page] = 1 / len(corpus)
        return page_to_probability

    for link in corpus[page]:
        page_to_probability[link] = page_to_probability[link] + (damping_factor / len(corpus[page]))
    
    return page_to_probability

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # First start with a page at random
    curr_page = list(corpus)[random.randint(0, len(corpus)-1)]
    count = 0

    samples = []
    samples.append(curr_page)
    while count < n:
        t_model = transition_model(corpus, curr_page, damping_factor)

        # Chose a page from the transition_model
        curr_page = random.choices(list(t_model.keys()), weights=list(t_model.values()))[0]
        samples.append(curr_page)
        count = count + 1

    # Group the samples together
    sample_count = {}
    for sample in samples:
        if sample in sample_count:
            sample_count[sample] = sample_count[sample] + 1
        else:
            sample_count[sample] = 1

    sample_probability = {}
    num_samples = len(samples)
    for sample in sample_count:
        sample_probability[sample] = round(sample_count[sample] / num_samples, 3)

    # sum = 0
    # for value in sample_probability.values():
    #     sum += value
    # print(sum)

    return sample_probability

def calculate_page_rank(page, d, N, corpus, page_rank):
    random_selection_probability = (1 - d) / N

    # Find all the pages that link to this page
    links = []
    for key in corpus:
        if page in corpus[key]:
            links.append(key)

    # Sum up the probabilities of all of the links
    sum = 0
    for link in links:
       num_links_on_this_page = len(corpus[link])
       page_rank_value = page_rank[link]
       sum = sum + (page_rank_value / num_links_on_this_page)

    return random_selection_probability + (d * sum)

def page_ranks_differ_by_more_than_001(pr1, pr2):
    for key in pr1:
        if abs(pr1[key] - pr2[key]) > 0.001:
            return True

    return False

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    num_pages = len(corpus)
    initial_page_rank = round(1 / num_pages, 3)
    page_rank = {}

    for page in corpus:
        page_rank[page] = initial_page_rank

    for page in corpus:
        if len(corpus[page]) == 0:
            for page2 in corpus:
                corpus[page].add(page2)

    should_continue = True
    while should_continue:
        previous_page_rank = page_rank.copy()
        for page in corpus:
            page_rank[page] = calculate_page_rank(page, damping_factor, num_pages, corpus, previous_page_rank)

        should_continue = page_ranks_differ_by_more_than_001(page_rank, previous_page_rank)

    # sum = 0
    # for value in page_rank.values():
    #     sum += round(value, 3)
    # print(sum)

    return page_rank

if __name__ == "__main__":
    main()
