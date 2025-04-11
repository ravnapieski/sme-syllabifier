import csv
import io
from syllabifier import syllabify, join_syllables

def run_tests_from_csv(file_path="tests.csv"):
    with open(file_path, encoding='utf-8') as csvfile:
        # Read file content and filter out comment lines (starting with '#')
        filtered_lines = [line for line in csvfile if not line.lstrip().startswith("#")]
        # Use io.StringIO to pass the filtered lines to csv.DictReader
        reader = csv.DictReader(io.StringIO("".join(filtered_lines)))
        
        passed = 0
        total = 0
        
        for row in reader:
            word = row['word']
            expected = row['expected']
            result = join_syllables(syllabify(word))
            total += 1
            if result != expected:
                print(f"❌ {word}: expected '{expected}', got '{result}'")
            else:
                print(f"✅ {word}: '{result}'")
                passed += 1
        print(f"\n✅ Passed {passed}/{total} tests.")

if __name__ == "__main__":
    run_tests_from_csv()
