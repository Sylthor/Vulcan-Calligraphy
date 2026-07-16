import matplotlib.pyplot as plt
import numpy as np
# from scipy.optimize import fsolve
from scipy.integrate import quad
# from scipy.special import lambertw
import matplotlib.image as mpimg
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

### Definitions to keep in mind in this script
# Numh - The vulcan characters
# Spline - The vertical lines where the characters are centered
# Bars - The dashes indicating the need for swirls
# Start - The patam, the first symbol in the upper left corner

# TODO
# - The height is left slightly ambiguous at the moment. The current rule is:
#       "After 500 pixels, it tries to add line-break. Always complete the full (compound)word before line-break."
# - Add vectorized nuhm.
# - Along with previous todos, ensure the thickness of the swirls are correct. This is ambiguous
#   since the nuhm are images but swirls are graphs which are invariant under window resizing.


# Fine tuning parameters
maximal_window_height = 500
linewidth = 1.5

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
    return np.abs(polynomial(x,roots,c))

def curve(roots,ax):
    c_list = np.linspace(-0.1,0.1,10000)
    x = np.linspace(min(bars),max(bars),1000)
    roots = bars
    print(roots)
    equivalent_width = []
    for i in range(len(c_list)):
        integrated_area = quad(abspolynomial,min(roots),max(roots),args=(roots,c_list[i]))[0]
        equivalent_width.append(integrated_area/max((abspolynomial(x,roots,c_list[i]))))
    
    c = c_list[np.argmax(equivalent_width)]
    print("Optimal parameter c:",c)

    # Plotting the optimization and the comparrison between the swirls
    fig_optimize,axs = subplots(2,1,1,override=True)
    axs[0].plot(c_list,equivalent_width,color="blue",label="Equivalent width function")
    axs[0].vlines(x=c,ymin=np.min(equivalent_width),ymax=np.max(equivalent_width),
                  color="black",linestyle="--",label=r"Optimal $c=$"+str(np.round(c,6)))
    axs[0].set_xlabel(r"$c$ parameter")
    axs[0].set_ylabel("Equivalent width")
    axs[1].plot(x,x*0,color="black")
    y_original = polynomial(x,roots,c=0)/np.max(abspolynomial(x,roots,c=0))*(-1)**(len(roots)+1)
    y_optimized = polynomial(x,roots,c=c)/np.max(abspolynomial(x,roots,c=c))*(-1)**(len(roots)+1)
    axs[1].plot(x,y_original,color="red",label="Original swirls")
    axs[1].plot(x,y_optimized,color="black",label="Optimized swirls")
    axs[1].set_xlabel("Vertical coordinate")
    axs[1].set_ylabel("Horizontal coordinate")
    axs[1].set_title(bars)
    fig_optimize.legend()
    fig_optimize.savefig(current_directory+"/Optimizer.png")
    y = polynomial(x,roots,c)

    # Ensure the curve ALWAYS starts to the right
    y = y/max(abs(y))*(-1)**(len(roots)+1)
    ax.plot(y*width/2+line,x,c="black",linewidth=linewidth)
def separate_string_into_clumps(string):
    """
    Splitting the provided Romanized string into clumps corresponding to valid numh.

    Args:
        string (string): Romanized string.
    
    Returns:
        nuhms (list,string): List of the separated numh.
    """
    # Sort the list of letters by length in descending order
    letters = os.listdir(current_directory+"/alphabet")
    for i in range(len(letters)):
        letters[i]=letters[i].replace(".png","")
        # letters[i]=letters[i].replace(".svg","")
    sorted_letters = sorted(letters, key=len, reverse=True)

    # Initialize the result list to store the clumps of letters
    nuhms = []
    i = 0
    while i < len(string):
        # Try to match the longest possible letter clump
        matched = False
        for letter in sorted_letters:
            # If the substring matches the letter clump
            if string[i:i+len(letter)] == letter:
                nuhms.append(letter)
                i += len(letter)
                matched = True
                break
        if not matched:
            # If no clump is matched, add the single character
            print(string[i])
            nuhms.append(string[i])
            i += 1
    return nuhms

def image(imagename,ax):
    '''
    The function displays the numh corresponding to the romanized text clump.
    '''
    img = mpimg.imread(current_directory+"/alphabet//"+imagename)
    numh_height,nuhm_width,__ = np.shape(img)

    horizontal_offset = 0
    if(imagename=="start.png"):
        horizontal_offset = 7
    global width
    global height
    global max_height
    if(nuhm_width > width):
        width = nuhm_width
    ax.imshow(img,extent=[-nuhm_width/2+horizontal_offset+line,nuhm_width/2+horizontal_offset+line,height+numh_height,height])
    height += numh_height
    if(max_height<height):
        max_height = height

main_fig, main_axs = plt.subplots(1, 1, figsize=(16, 16))
main_axs = [main_axs]
# main_fig, main_axs = subplots(1,1,4,override=True)
main_axs[0].set_axis_off()


string = "Stal Stonn le-matya k'stonn ik tal-tor svi'mazhiv po'ta zeshal aushfa mal-nef-hinek t'sa-veh. Ish-wak svi-aru."
# string = "Nam-tor Olozhika kluterek t'sha'sutenivaya k'ish she-tor etek s'nezhak isan utvau vah sha'kakhartayek."
# string = "Rok-tor etek ta sanoi nash uzh-rarav ik ki'fereik-tor nameT'Prion. Dungi olau ish-veh kunli pa'ta paribau k'kanok-veh svi'Shi'svatorai."
# string = "os-pid-vuhlkansu"
# string = "na'Gen-lis-tal"
string = "ahtortorki'fer eik-toraan-aish-ano-de"
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
# translate = "Stonn killed the le-matya with an antler that he found in the sand after the animal bit his kneecap. It was mid-afternoon."
# translate = "Logic is the cement of our civilization with which we ascen from chaos, using reason as our guide."
# plt.title("\""+string+"\"\n I have and always shall be your friend.")
# plt.title("\""+string+"\"\n "+translate)


if(string[-1] != "."):
    string += "."
clumps = separate_string_into_clumps(string.lower())
print(clumps)

width = 0
height = -34 # Required for the patam. Approximately half of the height of the numh.
max_height = height

line = 0
image("start.png",main_axs[0])
height_history = [height]
bars = [height]
for i in range(len(clumps)):
    # If it is the end of a sentence, add vertical lines, line-break and start new sentence. Reset bars
    if(clumps[i]=="."):
        if(len(bars)>1):
            bars.append(height)
            curve(bars,main_axs[0])
        image(" .png",main_axs[0])
        image(" .png",main_axs[0])
        image(" .png",main_axs[0])
        if(i!=len(clumps)-1):
            line += width*1.1
            height = -34
            image("newline3.png",main_axs[0])
            bars = [height]
    
    # If the space between two words in the middle of a sentence, add some spacing and reset bars.
    if(clumps[i]==" " and clumps[i-1]!="."):
        if(len(bars)>1):
            bars.append(height)
            curve(bars,main_axs[0])
        image(clumps[i]+".png",main_axs[0])
        image(clumps[i]+".png",main_axs[0])
        bars = [height]
    
    # If there are bars, do not add a nuhm, just prepare for the swirls.
    if(clumps[i]=="-"):
        bars.append(height)
    
    # If normal nuhms, just add them.
    if(clumps[i]!="-" and clumps[i]!="." and clumps[i]!=" "):
        image(clumps[i]+".png",main_axs[0])

    # If the line exceeds the specified height limit, insert a line-break and continue on new line.
    if(height > maximal_window_height and clumps[i]==" "):
        image("newline2.png",main_axs[0])
        line += width*1.1
        height = -34
        image("newline.png",main_axs[0])
        bars=[height]
    height_history.append(height)

# The horizontal spine
main_axs[0].plot([0,width/2+line],[0,0],color="black",linewidth=2.0)
main_axs[0].set_xlim(-width,width+line)
main_axs[0].set_ylim(max_height,-34)
main_fig.tight_layout()
main_fig.savefig(current_directory+"/Generated text.png")

import subprocess
from PIL import Image
from pathlib import Path

def png_to_svg_with_brightness(input_png, output_svg, brightness=0.55,scale_up=1/10):
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

path_numbers = list_paths_and_subpaths(current_directory+"/output.svg")
print(path_numbers)
# ---------------------------------------------------

f = open(current_directory+"/Demo.svg")
content = f.read()

text_to_copy = content.split("<svg")[1].split("<path")[0]
# print(text_to_copy)

f = open(current_directory+"/output.svg")
content = f.read()
text_to_replace = content.split("<svg")[1].split("<path")[0]

content = content.replace(text_to_replace,text_to_copy)

with open(current_directory+"/output.svg", "w") as f:
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

svg_file = current_directory+"/output.svg"
width, height, bbox = svg_paths_bbox(svg_file)

print("Width:", width)
print("Height:", height)
print(bbox)