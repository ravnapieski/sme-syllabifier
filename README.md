# Sme-Syllabifier

A Python tool for syllabifying words and texts according to specific linguistic rules for Northern Sámi (and similar language patterns). You can use it as a command-line tool or import it as a module in your Python projects.

## Usage

### Running as a Command-Line Tool

You can directly syllabify words or sentences from the command line:

1. **Direct Command-Line Argument**

   ```bash
   python syllabifier.py čieža čáppa čáhppes cizáža čohkkájit ja čuhket čázi čoavjji čađa čoliide
   ```

This will output the syllabified result:

    čie-ža čáp-pa čáhp-pes ci-zá-ža čohk-ká-jit ja čuh-ket čá-zi čoavj-ji ča-đa čo-lii-de

2. **Interactive Mode**

   ```bash
   python syllabifier.py
   ```

Then, enter the word or text at the prompt.

## Files

- **syllabifier.py**  
  Contains the syllabification logic and provides a command-line interface. When executed directly, it processes input (from the command line or interactively) and outputs the syllabified text.

- **test_syllabifier.py**  
  A test script that reads test cases from `tests.csv` and compares the output of the syllabifier against expected results.

- **tests.csv**  
  A CSV file containing test cases. Each row defines an input word and its expected syllabified output. The CSV file should have the following headers:
  - `word`
  - `expected`

## Limitations

### Edge-case Syllabifications:

There are a few test cases where the output does not exactly match the expected results:

áiccuidgeassi: Expected áic-cuid-geas-si but got áic-cui-dgeas-si.

aitosašáššiid: Expected ai-to-saš-áš-šiid but got ai-to-sa-šáš-šiid.

ándagasátnun: Expected án-da-gas-át-nun but got án-da-ga-sát-nun.

gieddegeašáhkku: Expected gied-de-geaš-áhk-ku but got gied-de-gea-šáhk-ku.

These are under work.
