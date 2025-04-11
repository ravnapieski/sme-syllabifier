import re
import sys

VOWELS = set("aáeiouyäö")
ALLOWED_DIPHTHONGS = {
    "ai", "ái", "ea", "eá", "iá", "ie", "oa", "ua", "ue", "ui", "uo"
}

# --- Special unsplittable clusters ---
# Rule 1: These sequences, if they occur at the beginning of the consonant cluster, should never be split.
UNSPLIT_SEQUENCES = {"hj", "hl", "hm", "hn", "hr", "nj", "bm", "dn", "gŋ"}
# Also unsplittable if three-letter sequence:
UNSPLIT_3 = {"dnj", "jhn"}
# note that "jhn" does not appear naturally in any Northern Sámi word, but "ihn" does
# and we replace every instance of 'i' to 'j' if 'i' comes after a vowel
# for the syllabification logic to work.

# Rule 2: The two‐letter clusters that are not to be split under one condition.
SPECIAL_CLUSTERS = {"dj", "lj"}

def replace_i_with_j_if_i_after_vowel(word):
    
    # keep ii ii
    chars = list(word)  # Convert to list
    i = 0
    n = len(chars)
    i_swap_indices = set()
    while i < n:
        if chars[i] == 'i' and i > 0 and word[i-1] in VOWELS:
            if word[i-1] != 'i':
                i_swap_indices.add(i)
                chars[i] = 'j'
        i += 1

    return i_swap_indices, ''.join(chars)  # Convert back to string

def split_cluster(cluster, prev_syl, next_exists, double_consonant, three_vowel):
    """
    Given a consonant cluster (string) that occurs between vowels, decide how many letters
    (if any) should be attached to the current syllable’s coda.
    
    Parameters:
      cluster    : the full string of consonants between vowels.
      prev_syl   : the already constructed previous syllable (may be empty)
      next_exists: True if there is a following vowel (i.e. we are not at word’s end).
      consecutive_duplicates: True if there are consecutive duplicates (f.ex: "čč" or "gg")
      three_vowel: True if the nucleus of the current syllable came from exactly 3 vowels.
      
    Returns a tuple (coda, next_onset). The coda is appended to the current syllable.
    The next_onset is prepended to the next syllable.
    
    Standard default: if next_exists is True, for a “normal” situation:
       - if len(cluster)==1: attach none (split_point = 0)
       - if len(cluster)>=2: attach one letter (split_point = 1)
    However, if the cluster starts with an unsplittable sequence (see below), then attach 0.
    
    For a three-vowel nucleus, always attach the first letter (unless it is unsplittable).
    
    SPECIAL (Rule 2): If the cluster begins with dj or lj, then:
       - if prev_syl exists and its last character equals the first letter of the cluster,
         then do not attach any consonant (i.e. return ("", cluster)).
       - Otherwise, attach the first letter.
    """
    if not next_exists:
        # At end-of-word, attach all remaining consonants.
        return (cluster, "")
    
    # If cluster is empty:
    if not cluster:
        return ("", "")
    
    # If the cluster begins with an unsplittable three‐letter sequence:
    if len(cluster) >= 3 and cluster[:3] in UNSPLIT_3:
        if cluster == "jhn": # f.ex: čáihni(čájhni)
            return ("j", cluster[1:])
        if cluster == "jhnn": # f.ex: čáihn-nis(čájhn-nis)
            return ("jhn", "n")
        return ("", cluster)
    
            
    # If the cluster begins with any unsplittable 2-letter sequence
    for seq in UNSPLIT_SEQUENCES:
        if cluster.startswith(seq):
            if len(cluster) == 3: # f.ex: skuhr-rat
                return (seq, cluster.replace(seq, ""))
            return ("", cluster) # f.ex: da-hje, gi-hli, lie-hmu
    
    # If the cluster begins with one of the special clusters dj/lj:
    for seq in SPECIAL_CLUSTERS:
        if cluster.startswith(seq):
            # If previous syllable exists and its last letter equals the first letter of the sequence,
            # then do not attach anything.
            if prev_syl and prev_syl[-1] == cluster[0]:
                return ("", cluster)
            else:
                # Otherwise, split after the first letter.
                return (cluster[0], cluster[1:])
    
    if double_consonant[0] is True:
        return (cluster[:double_consonant[1]], cluster[double_consonant[1]:])        
    # For a three-vowel nucleus, attach one letter if available.
    if three_vowel:
        if len(cluster) >= 1:
            return (cluster[0], cluster[1:])
        else:
            return ("", "")
    else:
        # For a non-three-vowel nucleus, if cluster has at least 2 letters attach one.
        if len(cluster) == 3:
            if cluster[1] == 's' or cluster[1] == 'š': # f.ex: rámš-ki, máis-tit
                return (cluster[:2], cluster[2])
        if len(cluster) >= 2:
            return (cluster[0], cluster[1:])
        else:
            return ("", cluster)

def syllabify(word):
    """
    Syllabify a word according to the provided rules.
    
    The strategy is to process the word from left to right. For each syllable we:
      1. Gather the onset (consecutive consonants).
      2. Process the nucleus (consecutive vowels) with merging rules.
      3. Look ahead at the consonant cluster (until the next vowel or end-of-word). 
    
    Returns a list of syllable strings.
    """
    word = word.lower()
    i_swap_indices, word = replace_i_with_j_if_i_after_vowel(word)
    syllables = []
    boundaries = [] # Each tuple is (start_index, end_index) in the modified word.
    i = 0
    n = len(word)
    
    # The syllables will be built sequentially.
    while i < n:
        syllable_start = i
        # Step 1. Onset: consecutive consonants.
        onset = ""
        while i < n and word[i] not in VOWELS:
            onset += word[i]
            i += 1
        
        if i >= n:
            # No vowel found; append leftover onset as a syllable.
            if onset:
                syllables.append(onset)
                boundaries.append((syllable_start, i))
            break
        
        # Step 2. Nucleus: collect consecutive vowels.
        vowel_start = i
        
        #treat_i_as_j = False
        while i < n and word[i] in VOWELS:
            #if word[i] == 'i':
                #treat_i_as_j = True
                #break
            i += 1
            
        vowel_seq = word[vowel_start:i]
        count_vowels = len(vowel_seq)
        # Apply merging rules:
        if count_vowels == 1:
            nucleus = vowel_seq
            three_vowel = False
        elif count_vowels == 2:
            # Merge if same or if the two vowels form an allowed diphthong.
            if vowel_seq[0] == vowel_seq[1] or vowel_seq in ALLOWED_DIPHTHONGS:
                nucleus = vowel_seq
            else:
                nucleus = vowel_seq[0]
                # Put back the remaining vowel for future processing.
                i = vowel_start + 1
            three_vowel = False
            """
        elif count_vowels == 3:
            nucleus = vowel_seq  # All three belong.
            three_vowel = True
            """
        else:  # 3 or more vowels
            if onset:
                nucleus = vowel_seq[0]
                i = vowel_start + 1
            else:
                nucleus = vowel_seq
            three_vowel = False
        
        # Build the current syllable so far.
        current_syl = onset + nucleus
        
        # Step 3. Process following consonant cluster until next vowel (or end-of-word).
        con_start = i
        previous_letter = ""
        double_consonant = (False, con_start)
        while i < n and word[i] not in VOWELS:
            if word[i] == previous_letter:
                double_consonant = (True, i-con_start)
            previous_letter = word[i]
            i += 1
            
        cluster = word[con_start:i]
        next_exists = (i < n)
        
        # Decide splitting of the consonant cluster.
        coda, next_onset = split_cluster(cluster, current_syl, next_exists,
                                         double_consonant, three_vowel)
        
        # Append the coda to the current syllable.
        current_syl += coda
        syllables.append(current_syl)
        boundaries.append((syllable_start, syllable_start + len(current_syl)))
        
        # The next syllable will start with next_onset.
        # To simulate that, we "prepend" next_onset to the remaining part of the word.
        # We do that by inserting next_onset back into the word at position i.
        if next_onset:
            word = word[:i] + next_onset + word[i:]
            n = len(word)
            i -= 0  # i stays at same position (now beginning with next_onset)
    
    # Before returning, for each syllable, change 'j's (that came from swapped 'i's) back to 'i's.
    if i_swap_indices:
        i = 0
        new_syllables = []
        for syl in syllables:
            new_syl = ""
            for letter in syl:
                if letter == 'j' and i in i_swap_indices:
                    new_syl += 'i'
                    i += 1
                    continue
                new_syl += letter
                i += 1
            new_syllables.append(new_syl)
        syllables = new_syllables            

    return syllables

def stavvalaste(text):
    """
    Remove punctuation, split the text on whitespace, syllabify each word.
    Returns a list of lists (each inner list contains syllables for a word).
    """
    text = re.sub(r'[.,!"\';:0-9]', '', text)
    words = text.split()
    return [syllabify(word) for word in words]

def join_syllables(syllables):
    """Join a list of syllables with hyphens."""
    return "-".join(syllables)

# --- Example usage ---
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
    else:
        input_text = input("Enter a word or text to syllabify: ")

    # Process the input.
    results = stavvalaste(input_text)
    
    # Concatenate syllabified words on a single line.
    output_words = [join_syllables(syllable_list) for syllable_list in results]
    print(" ".join(output_words))
