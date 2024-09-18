
# n = 6 for generating tie-breaks for 3 credentials
# Generate all possible n-tuples, e.g., if n=6, (0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 1), ...
def generate_all_binary_tuples(n):
    all_binary_tuples = []
    for i in range(2**n):
        binary_tuple = []
        for j in range(n):
            binary_tuple.append((i >> j) & 1)
        all_binary_tuples.append(binary_tuple)
    return all_binary_tuples

# https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/composition.html
def compositions(n):
    """
    Generate all compositions of n.
    """
    if n == 0:
        return [[]]  # Base case: one way to partition 0 (empty list)
    
    result = []
    for i in range(1, n+1):
        for p in compositions(n - i):
            result.append([i] + p)  # Append current part and recurse on the rest
    return result

# Removes the blatant duplicates from a list of profiles
def remove_duplicates(profiles):
    # Get unique profiles
    unique_profiles = []
    for (label, profile) in profiles:
        if len([p for (_, p) in unique_profiles if p == profile]) == 0:
            unique_profiles.append((label, profile))
    return unique_profiles
