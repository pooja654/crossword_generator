import generate
# Testing file for the Crossword Generator

# Run each algorithm and find which has the highest average score with each scoring algorithm
def run_all_algorithms(size, ranking, words_dic, ranked_letters):
    grid1, _ = generate.generate_puzzle_highest_ranked_first(size, generate.create_grid(size), words_dict, ranking, ranked_letters)
    grid2, _ = generate.generate_puzzle_highest_ranked_longest_first(size, generate.create_grid(size), words_dict, ranking, ranked_letters)
    grid3, _ = generate.generate_puzzle_random_first_word(size, generate.create_grid(size), words_dict, ranking, ranked_letters)
    grid4, _ = generate.generate_puzzle_require_alternation(size, generate.create_grid(size), words_dict, ranking, ranked_letters)
    grid5, _ = generate.generate_puzzle_require_alternation_random_first_word(size, generate.create_grid(size), words_dict, ranking, ranked_letters)

    return [grid1, grid2, grid3, grid4, grid5]


# Scoring Algorithm 1: Minimize Whitespace
sum = [0,0,0,0,0]
for i in range(100):
    for j in range(4, 15):
        words_dict, ranked_letters = generate.clean_words(j)
        output = run_all_algorithms(j, generate.ranked_without_intersections, words_dict, ranked_letters)
        index = 0
        for key in output:
            sum[index] += generate.score_generated_minimize_whitespace(key)
            index += 1
for i in range(len(sum)):
    sum[i] = sum[i] / 1100
print(sum)

# Scoring Algorithm 2: Maximize intersections
sum = [0,0,0,0,0]
for i in range(100):
    for j in range(4, 15):
        words_dict, ranked_letters = generate.clean_words(j)
        output = run_all_algorithms(j, generate.ranked_without_intersections, words_dict, ranked_letters)
        index = 0
        for key in output:
            sum[index] += generate.score_generated_maximize_intersections(key)
            index += 1
for i in range(len(sum)):
    sum[i] = sum[i] / 1100
print(sum)

# Scoring Algorithm 3: Maximize intersections
sum = [0,0,0,0,0]
for i in range(100):
    for j in range(4, 15):
        words_dict, ranked_letters = generate.clean_words(j)
        output = run_all_algorithms(j, generate.ranked_without_intersections, words_dict, ranked_letters)
        index = 0
        for key in output:
            sum[index] += generate.score_generated_unique_letters(key)
            index += 1
for i in range(len(sum)):
    sum[i] = sum[i] / 1100
print(sum)

# Test the different ranking functions algorithm performance:
rankings = [generate.ranked_by_common_letters, generate.ranked_by_letter_score, generate.ranked_by_num_intersections, generate.ranked_without_intersections, generate.ranked_without_intersections_and_unique_letters]
sum = [0, 0, 0, 0, 0]
for ranking in rankings:
    for i in range(100):
        for j in range(4, 15):
            words_dict, ranked_letters = generate.clean_words(j)
            output = run_all_algorithms(j, ranking, words_dict, ranked_letters)
            index = 0
            for key in output:
                sum[index] += generate.score_generated_minimize_whitespace(key)
                index += 1

for i in range(len(sum)):
    sum[i] = sum[i] / 1100
print(sum)

