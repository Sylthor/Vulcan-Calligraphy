import Vulcan as vulcan

line_break_height = 2500 # The max number of pixels. If exceeded, the word will  be moved to the next line. Typical nuhm height is ~360 pixels
contrast = 1.05 # Affects the thin-to-thick-to-thin parts of swirls. Set to 1 for no effect.
complex_sentence_structure = True # Whether to separate sentences into sub-branches.
dark_mode = True # Whether to have black background and white text, or not.
centered_on_nuhm = False # Whether to let the tel start at the approximate center of the nuhm.

# Rules for correct display of strings:
# 1) Always add space after periods.
# 2) Always add 'name' directly before a name. Example: "nameStonn" for the name "Stonn".
# 3) Only use symbols that have defined nuhm from korsaya.org. Symbols such as quotation marks, question marks, or commas have not been defined.
# 4) For "dot" as in "korsaya.com", use "@dot". For exclamation mark, use "!".

# If an incorrect letter is inserted, an error will be thrown.
string = "Stal nameStonn le-matya k'stonn ik tal-tor svi'mazhiv po'ta zeshal aushfa mal-nef-hinek t'sa-veh. Ish-wak svi-aru."

vulcan.generate_vulcan_calligraphy(string,line_break_height,contrast,complex_sentence_structure,dark_mode,centered_on_nuhm)