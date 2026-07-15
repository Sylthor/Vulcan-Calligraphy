import matplotlib.pyplot as plt
import numpy as np
# from scipy.optimize import fsolve
from scipy.integrate import quad
# from scipy.special import lambertw
import matplotlib.image as mpimg
import os

### Definitions to keep in mind in this script
# Numh - The vulcan characters
# Spline - The vertical lines where the characters are centered
# Bar - The horizontal line from which the spines are connected
# Start - The patam, the first symbol in the upper left corner

def subplots(rows,columns,height_scale,override=False,sharex=False,wcs=None,custom_width_factor=1):
    """
    Sets up figures for pretty plotting with (sub)plots. For a single plot, use rows=1, columns=1.

    Args:
        rows (int): Number of rows.
        columns (int): Number of columns.
        height_scale (float): The scaling factor for the height in number of twocolumnwidths heigh, so height_scale=1 is one twocolumnwidth tall.
        override (bool): Using two single twocolumnwidth as size (for larger plots), or not, and only use one twocolumnwidths.
        sharex (bool): TBD.
        wcs: TBD.
        custom_width_factor (float): Scaling for the number of two twocolumnwidths used for the width of the plot.

    Returns:
        fig: The figure for the plots.
        axs: Flattened list of subplots.
    """
    from matplotlib import ticker
    plt.rcParams.update({
        "font.size": 9,
        "font.family": "serif",  # Use a serif font for text
        "mathtext.fontset": "dejavuserif",  # Use Computer Modern (LaTeX default)
        # Alternative: Try "stix", "stixsans", or "dejavuserif" for other serif fonts
    })
    separation = 0.5 # cm
    padding = 2.0 # cm
    columnwidth = (21-2*padding-separation)/2 # cm
    Width = columnwidth/2.54 # inch
    Width_Long = 2*Width+separation # inch
    subplot_width = Width
    if(columns>1 or override):
        subplot_width = custom_width_factor*Width_Long
    if(wcs==None):
        fig, axs = plt.subplots(rows, columns, figsize=(subplot_width,Width*height_scale),layout="constrained",sharex=sharex)
    else:
        fig, axs = plt.subplots(rows, columns, figsize=(subplot_width,Width*height_scale),layout="constrained",sharex=sharex,subplot_kw=dict(projection=wcs))
    axs = np.array(axs).flatten()
    for ax in axs:
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(which='both', direction='in')
    return fig,axs

def polynomial(x,roots,c):
    '''
    The polynomial for each of the swirls is defined as p(x)=(x-b_1)(x-a_1)(x-a_2)...(x-a_n)(x-b_2) for
    n crossings of the spline corresponding to a_1 to a_n. b_1 and b_2 are the start and stopping points.

    For example, a swirl crossing once will have three roots.

    Args:
        x (array,float): The span of x-values along the spine.
        roots (array,float): The positions of the start, finish, and crossings.
        c: The  
    '''
    polynomial = 1
    for i in range(len(roots)):
        polynomial *= ((x) - roots[i])
    # fig,axs = subplots(1,1,1)
    # axs[0].plot(x,polynomial)
    y = polynomial*(np.exp(c*x))
    # axs[0].plot(x,polynomial)
    # plt.show()
    # if(c<1):
    #     y = polynomial*(1-np.exp(c*x))
    # if(c>=1):
    #     y = polynomial*(np.exp(-c*x))
    return y
def abspolynomial(x,roots,c):
    polynomial = 1
    for i in range(len(roots)):
        polynomial *= ((x) - roots[i])
    y = polynomial*(np.exp(c*x))
    # if(c<1):
    #     y = polynomial*(1-np.exp(c*x))
    # if(c>=1):
    #     y = polynomial*(np.exp(-c*x))
    return y**2
def curve(roots):
    # c = 0.013651365136513646/2
    # c = -0.005976597659765971
    # c = -0.009812981298129811
    c_list = np.linspace(-0.1,0.1,10000)
    x = np.linspace(min(bars),max(bars),100)
    roots = bars
    print(roots)
    sum_list = []
    sum_list1 = []
    for i in range(len(c_list)):
        sum = quad(polynomial,min(roots),max(roots),args=(roots,c_list[i]))[0]
        sum1 = quad(abspolynomial,min(roots),max(roots),args=(roots,c_list[i]))[0]
        sum_list.append(sum/max(polynomial(x,roots,c_list[i])))
        sum_list1.append(sum1/max(abspolynomial(x,roots,c_list[i])))
    # fig,axs = subplots(1,1,1)
    # axs[0].plot(x,polynomial(x,roots,c=0))
    # axs[0].plot(x,polynomial(x,roots,c=0.1))
    # plt.show()
    sum_list = np.array(sum_list)
    sum_list1 = np.array(sum_list1)
    s1 = sum_list/max(abs(sum_list))
    s2 = sum_list1/max(abs(sum_list1))
    s3 = 1/sum_list*1/sum_list1/max(abs(1/sum_list*1/sum_list1))
    s4 = (sum_list+sum_list1)/max(abs(sum_list+sum_list1))
    gradient = np.gradient(s2,c_list[1]-c_list[0])
    ddxx = np.gradient(gradient,c_list[1]-c_list[0])
    # print(sum_list/max(abs(sum_list)))
    # superfunction = 1/sum_list*sum_list1/max(abs(1/sum_list*sum_list1))
    c1 = c_list[np.argmin(s1)]
    c2 = c_list[np.argmax(s2)]
    c3 = c_list[np.argmin(s3)]
    c4 = c_list[np.argmax(s4)]
    c5 = c_list[np.argmin(gradient)]
    # print(c1)
    print(c2)
    print(c5)
    # print(c3)
    # print(c4)
    # plt.show()
    # plt.plot(c_list,s1,label="1")
    # # plt.vlines(x=c1,ymin=-1,ymax=1,linestyles="--")
    # plt.plot(c_list,s2,label="2")
    # plt.vlines(x=c2,ymin=-1,ymax=1,linestyles="--")
    # plt.plot(c_list,gradient/max(abs(gradient)))
    # plt.plot(c_list,s3,label="3")
    # plt.vlines(x=c3,ymin=-1,ymax=1,linestyles="--")
    # plt.plot(c_list,s4,label="4")
    # plt.vlines(x=c4,ymin=-1,ymax=1,linestyles="--")
    # plt.legend()
    # plt.show()
    # plt.plot(c_list,s2,label="2")
    # plt.plot(c_list,gradient/max(abs(gradient)))
    # plt.plot(c_list,ddxx/max(abs(ddxx)))
    # plt.vlines(x=0,ymax=1,ymin=0,linestyles="--")
    # plt.show()
    c = c5
    # c = c2
    # c = 0.0228
    y = polynomial(x,roots,c)
    # print(sum/max(polynomial(x,roots,c)))
    # print(sum1/max(abspolynomial(x,roots,c)),(max(roots)-min(roots))/2)
    # print(sum1/sum)

    y = y/max(abs(y))*(-1)**(len(roots)+1)
    plt.plot(y*width/2+line,x,c="black",linewidth=1.5)
def separate_string_into_clumps(string):
    """
    Splitting the provided Romanized string into clumps corresponding to valid numh.

    Args:
        string (string): Romanized string.
    
    Returns:
        result (list,string): List of the separated numh.
    """
    # Sort the list of letters by length in descending order
    letters = os.listdir("alphabet")
    for i in range(len(letters)):
        letters[i]=letters[i].replace(".png","")
    sorted_letters = sorted(letters, key=len, reverse=True)

    # Initialize the result list to store the clumps of letters
    result = []

    # Initialize the index to start at the beginning of the string
    i = 0

    while i < len(string):
        # Try to match the longest possible letter clump
        matched = False
        for letter in sorted_letters:
            # If the substring matches the letter clump
            if string[i:i+len(letter)] == letter:
                result.append(letter)
                i += len(letter)
                matched = True
                break
        if not matched:
            # If no clump is matched, add the single character
            print(string[i])
            result.append(string[i])
            i += 1

    return result
def image(imagename):
    '''
    The function displays the numh corresponding to the romanized text clump.
    '''
    img = mpimg.imread("alphabet//"+imagename)
    a,b,__ = np.shape(img)
    print(imagename,a,b)
    delta = 0
    if(imagename=="start.png"):
        delta = 7
    global width
    global height
    global max_height
    if(b>width):
        width=b
    plt.imshow(img,extent=[-b/2+delta+line,b/2+delta+line,height+a,height])
    height += a
    if(max_height<height):
        max_height = height
    # plt.plot([0,0],[y+a,y+a+2],color="black",linewidth=3)
    # plt.plot([0,0],[y,y+2],color="black",linewidth=3)

fig, ax = plt.subplots(1, 1, figsize=(16, 16))
ax.set_axis_off()

# print(letters)

string = "Stal Stonn le-matya k'stonn ik tal-tor svi'mazhiv po'ta zeshal aushfa mal-nef-hinek t'sa-veh. Ish-wak svi-aru."
string = "Nam-tor Olozhika kluterek t'sha'sutenivaya k'ish she-tor etek s'nezhak isan utvau vah sha'kakhartayek."
string = "Rok-tor etek ta sanoi nash uzh-rarav ik ki'fereik-tor nameT'Prion. Dungi olau ish-veh kunli pa'ta paribau k'kanok-veh svi'Shi'svatorai."
# string = "os-pid-vuhlkansu"
# string = "na'Gen-lis-tal"
# string = "tor-tor-ki'fereik-tor"
# string = "Kol-ut-shan"
# string = "Ragtaya na'Gen-lis-tal Vuhlkansu eh Gen-lislar os-pid-vuhlkansu ba-golik heh iyi-golik"
# string = "dif-tor heh smusma"
# string = "Va'Vuhnaya s'Va'Terishlar"
# string = "Wa'itaren na'kanok-veh ik ki'shetal rivlidalsu na'nisan t'Zun. Ki'pusatal fe-toyeht uzhaya ik. 7 na'du. Kuv wiri ki'lasha sanu ro'fah'voh fna'raf-ar'kada-sakat na' skladan na' korsaya sfek org."
# string = "rules-of-Mau"
# string = "Nam-tor nash-veh nameniklahs"
# string = "ven-dol-tar rufai-bosh. kup-bau-tor ven-dol-tar na'sha'nazh-kap zo-uf nazh-kap. fe-toyeht na'Gen-lis-tal"
# string = " Nam-tor nen t'tanaf-kitaun t'nash-veh fupa s'vi'le-eshan t'toyeht-irak-dvubikuvan heh tsuri-dvuperuv. Nam-tor nash-kilko tsurkanik fupa s'deshker t'du ha."
# string = "svi'nash-shi."
# string = "ketilik pitoh-su'us-ek'tal"
# string = "galu-dahshaya"
# string = "ro-kasaya"
# string = "Nash-vel ra. Sular vi. Fai-tor du n'au ha. Katravahsular t'du ha."
# string = "Ki'nam-tor nash-veh heh kwon-sum dungau nam-tor t'hai'la t'du."
string = "123-4567-890"
# translate = "Stonn killed the le-matya with an antler that he found in the sand after the animal bit his kneecap. It was mid-afternoon."
# translate = "Logic is the cement of our civilization with which we ascen from chaos, using reason as our guide."
# plt.title("\""+string+"\"\n I have and always shall be your friend.")
# plt.title("\""+string+"\"\n "+translate)

clumps = separate_string_into_clumps(string.lower())
print(clumps)

width = 0
height = -34 # Required for the patam. Approximately half of the height of the numh.
max_height = height
bars = 0
bars = [0]
line = 0
image("start.png")
height_history = [height]
bars = [height]
for i in range(len(clumps)):
    if((i == len(clumps)-1 or clumps[i] == "newline2") and len(bars)>1):
        bars.append(height)
        curve(bars)
        bars = [height]
    if(clumps[i]=="."):
        if(len(bars)>1):
            bars.append(height)
            curve(bars)
        image(" .png")
        image(" .png")
        image(" .png")
        if(i!=len(clumps)-1):
            line += width*1.1
            height = -34
            image("newline.png")
            bars = [height]
    if(clumps[i]==" " and clumps[i-1]!="."):
        if(len(bars)>1):
            bars.append(height)
            curve(bars)
        image(clumps[i]+".png")
        image(clumps[i]+".png")
        # image(clumps[i]+".png")
        bars = [height]
    if(clumps[i]=="-"):
        bars.append(height)
    if(clumps[i]!="-" and clumps[i]!="."):
        image(clumps[i]+".png")
    if(clumps[i] == "newline2"):
        line += width*1.1
        height = -34
        image("newline.png")
    if(height>500 and clumps[i]==" "):
        image("newline2.png")
        line += width*1.1
        height = -34
        image("newline.png")
        bars=[height]
    height_history.append(height)
plt.plot([0,width/2+line],[0,0],color="black",linewidth=2.0)
plt.xlim(-width,width+line)
plt.ylim(max_height,-34)
plt.tight_layout()
plt.savefig("Generated text.png")
# plt.show()

import subprocess
from PIL import Image
from pathlib import Path

def png_to_svg_with_brightness(input_png, output_svg, brightness=0.55,scale_up=1/10):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    potrace_path = current_directory+"/potrace-1.16.win64/potrace.exe"  # Full path to Potrace
    input_png = Path(input_png)
    temp_pbm = input_png.with_suffix(".pbm")

    # Convert to grayscale + apply brightness threshold
    img = Image.open(input_png).convert("L")
    img = img.point(lambda p: 255 if p/255 > brightness else 0)  # threshold
    img.save(temp_pbm)

    # Run Potrace to convert PBM to SVG
    subprocess.run([
        potrace_path,
        str(temp_pbm),
        "--svg",
        "-o", str(output_svg)
    ], check=True)

    temp_pbm.unlink()  # cleanup

current_directory = os.path.dirname(os.path.abspath(__file__))

png_to_svg_with_brightness(
    current_directory+"/Generated text.png",
    current_directory+"/output.svg",
    brightness=0.55
)

import xml.etree.ElementTree as ET
from pathlib import Path

def count_subpaths_in_path(d):
    return d.count('M') + d.count('m')

def list_paths_and_subpaths(svg_path):
    path_numbers = []
    svg_path = Path(svg_path)
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    paths = root.findall(".//svg:path", ns)
    total_subpaths = 0
    for i, path in enumerate(paths, 1):
        d_attr = path.attrib.get("d", "")
        subs = count_subpaths_in_path(d_attr)
        total_subpaths += subs
        print(f"Path {i}: {subs} subpaths")
        path_numbers.append(subs)

    print(f"\nTotal subpaths (potential FreeCAD regions): {total_subpaths}")
    return path_numbers

path_numbers = list_paths_and_subpaths("output.svg")
print(path_numbers)
# ---------------------------------------------------

f = open("Demo.svg")
content = f.read()

text_to_copy = content.split("<svg")[1].split("<path")[0]
# print(text_to_copy)

f = open("output.svg")
content = f.read()
text_to_replace = content.split("<svg")[1].split("<path")[0]

content = content.replace(text_to_replace,text_to_copy)

with open("output.svg", "w") as f:
  f.write(content)

from svgpathtools import parse_path
def svg_paths_bbox(svg_file):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Handle namespaces
    ns = {"svg": "http://www.w3.org/2000/svg"}

    # Track global bounding box
    global_xmin = float("inf")
    global_xmax = float("-inf")
    global_ymin = float("inf")
    global_ymax = float("-inf")

    # Find all path elements
    for path_elem in root.findall(".//svg:path", ns):
        d = path_elem.get("d")
        if not d:
            continue
        path = parse_path(d)
        xmin, xmax, ymin, ymax = path.bbox()

        global_xmin = min(global_xmin, xmin)
        global_xmax = max(global_xmax, xmax)
        global_ymin = min(global_ymin, ymin)
        global_ymax = max(global_ymax, ymax)

    width = global_xmax - global_xmin
    height = global_ymax - global_ymin

    return width, height, (global_xmin, global_ymin, global_xmax, global_ymax)

svg_file = "output.svg"
width, height, bbox = svg_paths_bbox(svg_file)

print("Width:", width)
print("Height:", height)
print(bbox)