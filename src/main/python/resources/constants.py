"""Static data used by the Morse code training application."""

LETTER_MORSE_PAIRS = (
    ('a', '.-'),
    ('b', '-...'),
    ('c', '-.-.'),
    ('d', '-..'),
    ('e', '.'),
    ('f', '..-.'),
    ('g', '--.'),
    ('h', '....'),
    ('i', '..'),
    ('j', '.---'),
    ('k', '-.-'),
    ('l', '.-..'),
    ('m', '--'),
    ('n', '-.'),
    ('o', '---'),
    ('p', '.--.'),
    ('q', '--.-'),
    ('r', '.-.'),
    ('s', '...'),
    ('š', '----'),
    ('t', '-'),
    ('u', '..-'),
    ('v', '...-'),
    ('w', '.--'),
    ('ä', '.-.-'),
    ('ö', '---.'),
    ('ü', '..--'),
    ('x', '-..-'),
    ('y', '-.--'),
    ('z', '--..'),
)

LETTER_TO_MORSE_MAP: dict[str, str] = {}
for letter, code in LETTER_MORSE_PAIRS:
    LETTER_TO_MORSE_MAP[letter] = code
    LETTER_TO_MORSE_MAP[letter.upper()] = code

NUMBER_SYMBOL_MORSE_PAIRS = (
    ('1', '.----'),
    ('2', '..---'),
    ('3', '...--'),
    ('4', '....-'),
    ('5', '.....'),
    ('6', '-....'),
    ('7', '--...'),
    ('8', '---..'),
    ('9', '----.'),
    ('0', '-----'),
    (',', '--..--'),
    ('.', '.-.-.-'),
    ('!', '-.-.--'),
    ('?', '..--..'),
    ('/', '-..-.'),
    ('-', '-....-'),
    ("'", '.----.'),
    ('"', '.-..-.'),
    (':', '---...'),
    (';', '-.-.-.'),
    ('+', '.-.-.'),
    ('=', '-...-'),
    ('(', '-.--.'),
    (')', '-.--.-'),
    ('&', '.-...'),
    ('$', '...-..-'),
    ('@', '.--.-.'),
    ('_', '..--.-'),
)

NUMBER_TO_MORSE_MAP = {
    char: code for char, code in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit()
}

SYMBOL_TO_MORSE_MAP = {
    char: code for char, code in NUMBER_SYMBOL_MORSE_PAIRS if not char.isdigit()
}


LETTER_AUDIO_MAP = {
    f"{letter.upper()} {letter}": f"resources/letters/{letter.upper()}.wav"
    for letter, _ in LETTER_MORSE_PAIRS
}

NUMBER_AUDIO_MAP = {
    char: f"resources/numbers/{char}.wav"
    for char, _ in NUMBER_SYMBOL_MORSE_PAIRS
    if char.isdigit()
}

_SYMBOL_AUDIO_LABELS = (
    ('_', 'alakriips'),
    ('&', 'ja'),
    ("'", 'ülakoma'),
    ('@', 'ät'),
    ('(', 'avav_sulg'),
    ('$', 'dollar'),
    ('!', 'hüüumärk'),
    ('/', 'kaldkriips'),
    (',', 'koma'),
    (':', 'koolon'),
    ('?', 'küsimärk'),
    ('+', 'pluss'),
    ('.', 'punkt'),
    (';', 'semikoolon'),
    (')', 'sulgev_sulg'),
    ('=', 'võrdusmärk'),
    ('"', 'jutumärk'),
    ('-', 'miinus'),
)

SYMBOL_AUDIO_MAP = {
    symbol: f"resources/symbols/{slug}.wav"
    for symbol, slug in _SYMBOL_AUDIO_LABELS
}


WORD_AUDIO_ENTRIES = tuple(f"sõna{i}" for i in range(1, 11))
SENTENCE_AUDIO_ENTRIES = tuple(f"lause{i}" for i in range(1, 11))

PHRASE_AUDIO_MAP = {
    entry: f"resources/{entry}.wav"
    for entry in (*WORD_AUDIO_ENTRIES, *SENTENCE_AUDIO_ENTRIES)
}

TRANSLATION_TEXT_SAMPLES = [
    'Programmeerimine',
    'Morsekood',
    'Marcus Kommussaar',
    'Sander Sirge',
    'Tartu linn',
    'Tartu Ylikool',
    '2 valget kassi',
    '1632',
    'Must & valge koer',
    'Delta keskus',
    'Tartu Ylikool asutati aastal 1632.',
    'Programmeerimine on eriti lahe!',
    'Kas sinule meeldib Pythoni keel?',
    '(x + y - z) = 420',
    'Meie email ei ole morsekood@morsekood.com',
    'Meie projektikood on PROJEKT-MORSEKOOD.py',
    'Praktikumid tulevad suureks kasuks.',
    'Kellegi arvutis jookseb 875 protsessi.',
    '"See on tsitaat, vist": Sander Sirge 2023',
    "Google'i 4. kvartali tulu oli 75,33 mld dollarit.",
]

TRANSLATION_MORSE_SAMPLES = [
    '.--. .-. --- --. .-. .- -- -- . . .-. .. -- .. -. .',
    '-- --- .-. ... . -.- --- --- -..',
    '-- .- .-. -.- ..- ...   -.- --- -- -- ..- ... ... .- .- .-.',
    '... .- -. -.. . .-.   ... .. .-. --. .',
    '- .- .-. - ..-   .-.. .. -. -.',
    '- .- .-. - ..-   -.-- .-.. .. -.- --- --- .-..',
    '..---   ...- .- .-.. --. . -   -.- .- ... ... ..',
    '.---- -.... ...-- ..---',
    '-- ..- ... -   .-...   ...- .- .-.. --. .   -.- --- . .-.',
    '-.. . .-.. - .-   -.- . ... -.- ..- ...',
    '- .- .-. - ..-   -.-- .-.. .. -.- --- --- .-..   .- ... ..- - .- - ..\n.- .- ... - .- .-..   .---- -.... ...-- ..--- .-.-.-',
    '.--. .-. --- --. .-. .- -- -- . . .-. .. -- .. -. .\n--- -.   . .-. .. - ..   .-.. .- .... . -.-.--',
    '-.- .- ...   ... .. -. ..- .-.. .   -- . . .-.. -.. .. -...\n.--. -.-- - .... --- -. ..   -.- . . .-.. ..--..',
    '-.--. -..-   .-.-.   -.--   -....-   --.. -.--.-   -...-   ....- ..--- -----',
    '-- . .. .   . -- .- .. .-..   . ..   --- .-.. .\n-- --- .-. ... . -.- --- --- -.. .--.-. -- --- .-. ... . -.- --- --- -.. .-.-.- -.-. --- --',
    '-- . .. .   .--. .-. --- .--- . -.- - .. -.- --- --- -..   --- -.\n--. .-. --- .--- . -.- - -....- -- --- .-. ... . -.- --- --- -.. .-.-.- .--. -.--',
    '.--. .-. .- -.- - .. -.- ..- -- .. -..   - ..- .-.. . ...- .- -..\n... ..- ..- .-. . -.- ...   -.- .- ... ..- -.- ... .-.-.-',
    '-.- . .-.. .-.. . --. ..   .- .-. ...- ..- - .. ...   .--- --- --- -.- ... . -...\n---.. --... .....   .--. .-. --- - ... . ... ... .. .-.-.-',
    '.-..-. ... . .   --- -.   - ... .. - .- .- - --..--   ...- .. ... - .-..-. ---...\n... .- -. -.. . .-.   ... .. .-. --. .   ..--- ----- ..--- ...--',
    "--. --- --- --. .-.. . .----. ..   ....- .-.-.-   -.- ...- .- .-. - .- .-.. ..\n- ..- .-.. ..-   --- .-.. ..   --... ..... --..-- ...-- ...--   -- .-.. -..\n-.. --- .-.. .- .-. .. - .-.-.-",
]

TEST_TEXT_PROMPTS = [
    'Programmeerimine',
    'Morsekood',
    'Linux',
    'Windows',
    'Android',
    'Tartu Ylikool asutati aastal 1632.',
    "Google'i 4. kvartali tulu oli 75,33 mld dollarit",
    'Apple on parem kui Android?',
    'Diskreetne matemaatika on raske!',
    'Informaatika eriala on ainus sobiv valik',
    '- .- .-. - ..-   -.-- .-.. .. -.- --- --- .-..',
    '-- ..- ... -   .-...   ...- .- .-.. --. .   -.- --- . .-.',
    '-.- . .-. -. . .-..',
    '.--- .- ...- .- ... -.-. .-. .. .--. -',
    '-.- .- ... ..- - .- .--- .- .-.. .. .. -.. . ...',
    '-.- . .-.. .-.. . --. ..   .- .-. ...- ..- - .. ...   .--- --- --- -.- ... . -...\
---.. --... .....   .--. .-. --- - ... . ... ... .. .-.-.-',
    '.--. .-. .- -.- - .. -.- ..- -- .. -..   - ..- .-.. . ...- .- -..\
... ..- ..- .-. . -.- ...   -.- .- ... ..- -.- ... .-.-.-',
    '..- .-. .- .-..   --- -.   .- .- ... - .- - . .-..\
.---- ----. ..... ----. -....- .---- ----. --... .----\
- --- --- -.. . - ..- -..   . .-.. . -.- - .-. --- -. .- .-. ...- ..- - .. - .\
... . . .-. .. .- .-.-.-',
    '-.- .- ...   ... .-   -.- --- .-. -.. .- ... .. -..   - . ... - .. -.- ... ..--..',
    '. -.. ..-   - . .. .-.. .   . -.- ... .- -- .. .-.. -.-.--',
]

TEST_MORSE_ANSWERS = [
    '.--. .-. --- --. .-. .- -- -- . . .-. .. -- .. -. .',
    '-- --- .-. ... . -.- --- --- -..',
    '.-.. .. -. ..- -..-',
    '.-- .. -. -.. --- .-- ...',
    '.- -. -.. .-. --- .. -..',
    '- .- .-. - ..-   -.-- .-.. .. -.- --- --- .-..   .- ... ..- - .- - ..   .- .- ... - .- .-..   .---- -.... ...-- ..--- .-.-.-',
    "--. --- --- --. .-.. . .----. ..   ....- .-.-.-   -.- ...- .- .-. - .- .-.. ..   - ..- .-.. ..-   --- .-.. ..   --... ..... --..-- ...-- ...--   -- .-.. -..   -.. --- .-.. .- .-. .. -",
    '.- .--. .--. .-.. .   --- -.   .--. .- .-. . --   -.- ..- ..   .- -. -.. .-. --- .. -.. ..--..',
    '-.. .. ... -.- .-. . . - -. .   -- .- - . -- .- .- - .. -.- .-   --- -.   .-. .- ... -.- . -.-.--',
    '.. -. ..-. --- .-. -- .- .- - .. -.- .-   . .-. .. .- .-.. .-   --- -.   .- .. -. ..- ...   ... --- -... .. ...-   ...- .- .-.. .. -.-',
    'Tartu ylikool',
    'Must & valge koer',
    'Kernel',
    'Javascript',
    'Kasutajaliides',
    'Kellegi arvutis jookseb 875 protsessi.',
    'Praktikumid tulevad suureks kasuks.',
    'Ural on aastatel 1959-1971 toodetud elektronarvutite seeria.',
    'Kas sa kordasid testiks?',
    'Edu teile eksamil!',
]

# Pre-computed key views for faster lookup.
UPPERCASE_LETTER_KEYS = tuple(letter.upper() for letter, _ in LETTER_MORSE_PAIRS)
UPPERCASE_LETTER_ORDER = UPPERCASE_LETTER_KEYS
LOWERCASE_LETTER_KEYS = tuple(letter for letter, _ in LETTER_MORSE_PAIRS)
LOWERCASE_LETTER_ORDER = LOWERCASE_LETTER_KEYS
NUMBER_KEYS = tuple(char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if char.isdigit())
NUMBER_ORDER = NUMBER_KEYS
SYMBOL_KEYS = tuple(char for char, _ in NUMBER_SYMBOL_MORSE_PAIRS if not char.isdigit())
SYMBOL_ORDER = SYMBOL_KEYS
LETTER_AUDIO_KEYS = LETTER_AUDIO_MAP.keys()
NUMBER_AUDIO_KEYS = NUMBER_AUDIO_MAP.keys()
SYMBOL_AUDIO_KEYS = SYMBOL_AUDIO_MAP.keys()

__all__ = [
    "LETTER_MORSE_PAIRS",
    "LETTER_TO_MORSE_MAP",
    "NUMBER_SYMBOL_MORSE_PAIRS",
    "NUMBER_TO_MORSE_MAP",
    "SYMBOL_TO_MORSE_MAP",
    "LETTER_AUDIO_MAP",
    "NUMBER_AUDIO_MAP",
    "SYMBOL_AUDIO_MAP",
    "PHRASE_AUDIO_MAP",
    "TRANSLATION_TEXT_SAMPLES",
    "TRANSLATION_MORSE_SAMPLES",
    "TEST_TEXT_PROMPTS",
    "TEST_MORSE_ANSWERS",
    "UPPERCASE_LETTER_KEYS",
    "UPPERCASE_LETTER_ORDER",
    "LOWERCASE_LETTER_KEYS",
    "LOWERCASE_LETTER_ORDER",
    "NUMBER_KEYS",
    "NUMBER_ORDER",
    "SYMBOL_KEYS",
    "SYMBOL_ORDER",
    "LETTER_AUDIO_KEYS",
    "NUMBER_AUDIO_KEYS",
    "SYMBOL_AUDIO_KEYS",
]
