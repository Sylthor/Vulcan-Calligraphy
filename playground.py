import Vulcan as vulcan

line_break_height = 900 # The number of pixels set as the height after which it will insert line-breaks. Typical nuhm height is ~360 pixels
contrast = 1.05 # Affects the thin-to-thick-to-thin parts of swirls. Set to 1 for no effect.

# Rules for correct display of strings:
# 1) Always add space after periods.
# 2) Always add 'name' directly before a name. Example: "nameStonn" for the name "Stonn".

# If an incorrect letter is inserted, an error will be thrown.
string = "Stal nameStonn le-matya k'stonn ik tal-tor svi'mazhiv po'ta zeshal aushfa mal-nef-hinek t'sa-veh. Ish-wak svi-aru."

vulcan.generate_vulcan_calligraphy(string,line_break_height,contrast)