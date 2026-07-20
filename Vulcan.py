import matplotlib.pyplot as plt
import numpy as np
# from scipy.optimize import fsolve
from scipy.integrate import quad
# from scipy.special import lambertw
import matplotlib.image as mpimg
import os
from matplotlib.backends.backend_pdf import PdfPages

current_directory = os.path.dirname(os.path.abspath(__file__))

### Definitions to keep in mind in this script
# Numh - The vulcan characters
# Spline - The vertical lines where the characters are centered
# Bars - The dashes indicating the need for swirls
# Start - The patam, the first symbol in the upper left corner

# TODO
# - The height is left slightly ambiguous at the moment. The current rule is:
#       "After 500 pixels, it tries to add line-break. Always complete the full (compound)word before line-break."


# Fine tuning parameters
debug = False

centered_on_nuhm = False

# Parameters for spaces and end-lines in number of black spaces, where a blank space is 10 pixels (in .png format).
subbranch_height = 5 # Min=5
space_height = 3 # Min=0
ending_height = 5 # Min=0

# Other specifications
resolution = 32 # In figsize. Default is 16, so the scaling is res/16.
padding_factor = 1.1 # In (start-)widths to add space on the side.
tel_width = 0.5 # In widths, for maximal outswing.

list_of_figures = []

def save_images_in_pdf(filename,list_of_figures):
    with PdfPages(filename) as pdf:
        for fig in list_of_figures:
            # Write the specific figure instance to the document
            pdf.savefig(fig)
            
            # Explicitly release the figure from memory now that it is written
            plt.close(fig)

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
    y = polynomial*(np.exp(c*x))
    return y
def abspolynomial(x,roots,c):
    return np.abs(polynomial(x,roots,c))
def curve(roots,ax,line,linewidth,contrast,color):
    c_list = np.linspace(-0.05,0.05,10000)
    x = np.linspace(min(roots),max(roots),1000)

    equivalent_width = []
    for i in range(len(c_list)):
        normalization_factor = np.max((abspolynomial(x,roots,c_list[i])))
        integrated_area = quad(abspolynomial,min(roots),max(roots),args=(roots,c_list[i]))[0]
        if(np.isfinite(integrated_area)):
            equivalent_width.append(integrated_area/normalization_factor)
        else:
            equivalent_width.append(0)

    c = c_list[np.nanargmax(equivalent_width)]
    print("Optimal parameter c:",c)

    # Plotting the optimization and the comparrison between the swirls
    fig_optimize,axs = subplots(2,1,1.0,override=True)
    axs[0].plot(c_list,equivalent_width,color="blue",label="Equivalent width function")
    axs[0].vlines(x=c,ymin=np.nanmin(equivalent_width),ymax=np.nanmax(equivalent_width),
                  color=color,linestyle="--",label=r"Optimal $c=$"+str(np.round(c,6)))
    axs[0].set_xlabel(r"$c$ parameter")
    axs[0].set_ylabel("Equivalent width")
    axs[1].plot(x,x*0,color=color)
    y_original = polynomial(x,roots,c=0)/np.max(abspolynomial(x,roots,c=0))*(-1)**(len(roots)+1)
    y_optimized = polynomial(x,roots,c=c)/np.max(abspolynomial(x,roots,c=c))*(-1)**(len(roots)+1)
    axs[1].plot(x,y_original,color="red",label="Original swirls")
    axs[1].plot(x,y_optimized,color=color,label="Optimized swirls")

    axs[1].set_xlabel("Vertical coordinate")
    axs[1].set_ylabel("Normalized horizontal \n coordinate")
    axs[1].set_title(str(roots)+"   "+str(np.round(roots/np.max(roots),4)))
    fig_optimize.legend()
    # fig_optimize.savefig(current_directory+"/Optimizer.png")
    list_of_figures.append(fig_optimize)
    plt.close(fig_optimize)
    y = polynomial(x,roots,c)

    # Ensure the curve ALWAYS starts to the right
    y = y/max(abs(y))*(-1)**(len(roots)+1)
    ax.fill_betweenx(x,y*get_svg_size("start.svg")[0]*tel_width+line,y*contrast*get_svg_size("start.svg")[0]*tel_width+line,color=color)
    ax.plot(y*get_svg_size("start.svg")[0]/2+line,x,c=color,linewidth=linewidth)
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
            # print(string[i])
            nuhms.append(string[i])
            i += 1
    return nuhms

import re
import numpy as np
from xml.etree import ElementTree as ET
from svgpath2mpl import parse_path
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D


def _local_tag(elem):
    return elem.tag.split('}')[-1]
def _parse_transform(transform_str):
    """Parse an SVG transform attribute into a 3x3 affine matrix
    (matplotlib convention: [[a,c,e],[b,d,f],[0,0,1]])."""
    mat = np.identity(3)
    if not transform_str:
        return mat
    for cmd, args in re.findall(r'(\w+)\s*\(([^)]*)\)', transform_str):
        nums = [float(x) for x in re.split(r'[,\s]+', args.strip()) if x]
        if cmd == 'translate':
            tx = nums[0]
            ty = nums[1] if len(nums) > 1 else 0
            m = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
        elif cmd == 'scale':
            sx = nums[0]
            sy = nums[1] if len(nums) > 1 else sx
            m = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
        elif cmd == 'matrix':
            a, b, c, d, e, f = nums
            m = np.array([[a, c, e], [b, d, f], [0, 0, 1]])
        else:
            m = np.identity(3)
        mat = mat @ m  # compose left-to-right as SVG spec requires
    return mat
def _collect_paths(elem, parent_matrix, out,color):
    """Recursively collect (d_string, fill, matrix) for every <path>."""
    tag = _local_tag(elem)
    matrix = parent_matrix @ _parse_transform(elem.get('transform'))

    if tag == 'path' and elem.get('d') is not None:
        fill = elem.get('fill', color)
        out.append((elem.get('d'), fill, matrix))

    for child in elem:
        _collect_paths(child, matrix, out,color)
def image_svg(imagename, ax, line, height,color, target_width=None, target_height=None):
    tree = ET.parse(current_directory+"/alphabet_vectorized//" + imagename)
    root = tree.getroot()

    if 'viewBox' in root.attrib:
        minx, miny, svg_w, svg_h = map(float, root.attrib['viewBox'].split())
    else:
        def _num(s):
            return float(re.match(r'[\d.]+', s).group())
        svg_w = _num(root.get('width', '100'))
        svg_h = _num(root.get('height', '100'))
        minx, miny = 0, 0
    svg_w = svg_w
    svg_h = svg_h

    # --- decide final display size ---
    if target_width is None and target_height is None:
        disp_w, disp_h = svg_w, svg_h          # native size
    elif target_width is not None and target_height is None:
        disp_w = target_width
        disp_h = svg_h * (target_width / svg_w)   # keep aspect ratio
    elif target_height is not None and target_width is None:
        disp_h = target_height
        disp_w = svg_w * (target_height / svg_h)   # keep aspect ratio
    else:
        disp_w, disp_h = target_width, target_height   # stretch to exact size

    sx = disp_w / svg_w
    sy = disp_h / svg_h

    # if disp_w > width:
    #     width = disp_w

    x0 = -disp_w / 2 + line
    y0 = height

    # placement matrix: viewBox coords -> scaled -> translated into data coords
    placement = np.array([
        [sx, 0,  x0 - minx * sx],
        [0,  sy, y0 - miny * sy],
        [0,  0,  1],
    ])

    paths_data = []
    _collect_paths(root, np.identity(3), paths_data,color)

    for d_str, fill, group_matrix in paths_data:
        mpl_path = parse_path(d_str)
        total_matrix = placement @ group_matrix
        transform = Affine2D(total_matrix) + ax.transData
        ax.add_patch(PathPatch(
            mpl_path,
            transform=transform,
            facecolor=fill if fill not in (None, 'none') else 'none',
            edgecolor='none',
            linewidth=0,
        ))

    height += disp_h
    return height
def get_svg_size(imagename):
    tree = ET.parse("alphabet_vectorized//" + imagename)
    root = tree.getroot()

    if 'viewBox' in root.attrib:
        __, __, svg_w, svg_h = map(float, root.attrib['viewBox'].split())
    return svg_w,svg_h
def calculate_window_size(clumps,line_break_height,complex_sentence_structure):
    figsize_x, figsize_y = get_svg_size("start.svg")
    figsize_x += figsize_x # Padding on the sides
    height = figsize_y
    figsize_y += figsize_y # Padding on the top and bottom
    print("Start_size:",get_svg_size("start.svg")[0])
    if(complex_sentence_structure):
        height += subbranch_height*get_svg_size("_.svg")[1]
    # Complex sentence structures
    complex_sentence_indicies = []
    sentence_start = 0
    continuing_sentence = False
    # print(4*get_svg_size("_.svg")[1],get_svg_size("newline3.svg")[1])
    for i in range(len(clumps)):
        # If it is the end of a sentence, add vertical lines, line-break and start new sentence. Reset bars
        if(clumps[i]=="." or clumps[i]=="!"):
            height += ending_height*get_svg_size("_.svg")[1] # Ending line
            if(clumps[i]=="!"):
                height += get_svg_size("!.svg")[1] # Exclamation mark
            if(continuing_sentence):
                complex_sentence_indicies.append(sentence_start)
                continuing_sentence = False
            sentence_start = i+1
            figsize_y = np.max([figsize_y,height])
            if(i!=len(clumps)-1):
                figsize_x += get_svg_size("start.svg")[0]*padding_factor
                height = get_svg_size("newline3.svg")[1]

                if(complex_sentence_structure):
                    height += subbranch_height*get_svg_size("_.svg")[1]
                    # if(i==0):
                    #     height += 3*get_svg_size("_.svg")[1]
        
        # If the space between two words in the middle of a sentence, add some spacing and reset bars.
        if(clumps[i]=="_" and clumps[i-1]!="."):
            # If another nuhm can be fitted within the line_break_height
            if(height+space_height*get_svg_size("_.svg")[1] < line_break_height):
                # height = image(clumps[i]+".svg",main_axs[0],line,height,space_height)
                height += space_height*get_svg_size("_.svg")[1]
            else:
                height += get_svg_size("newline2.svg")[1]
                # complex_sentence_indicies.append(sentence_start)
                figsize_x += get_svg_size("start.svg")[0]*padding_factor
                figsize_y = np.max([figsize_y,height])
                height = get_svg_size("newline.svg")[1]
                if(complex_sentence_structure):
                    height += get_svg_size("newline4.svg")[1]/2+get_svg_size("newline.svg")[1]/2
                    height += get_svg_size("_.svg")[1]*(subbranch_height-int(np.round((get_svg_size("newline.svg")[1]+get_svg_size("newline4.svg")[1])/2/get_svg_size("_.svg")[1])))
                continuing_sentence = True
        if(clumps[i]==","):
            height += space_height*get_svg_size("_.svg",)[1]
        # If normal nuhms, just add them.
        if(clumps[i]!="-" and clumps[i]!="." and clumps[i]!="_" and clumps[i]!="!"):
            height += get_svg_size(clumps[i]+".svg")[1]

        # If the line exceeds the specified height limit, insert a line-break and continue on new line.
        # if(height+space_height*get_svg_size("_.svg")[1] > line_break_height and clumps[i]=="_" and clumps[i-1]!="."):
        #     height += get_svg_size("newline2.svg")[1]
        #     # complex_sentence_indicies.append(sentence_start)
        #     figsize_x += get_svg_size("start.svg")[0]*padding_factor
        #     figsize_y = np.max([figsize_y,height])
        #     height = get_svg_size("newline.svg")[1]
        #     if(complex_sentence_structure):
        #         height += get_svg_size("start.svg")[1]+get_svg_size("newline4.svg")[1]/2-get_svg_size("newline.svg")[1]/2
        #     continuing_sentence = True
        # print(i,clumps[i],height,figsize_x)
    return figsize_x,figsize_y,complex_sentence_indicies

def image(imagename,ax,line,height,color,repeat=1):
    '''
    The function displays the numh corresponding to the romanized text clump.
    '''
    for i in range(repeat):
        height = image_svg(imagename,ax,line,height,color)
    return height


# string = "Stal nameStonn le-matya k'stonn ik tal-tor svi'mazhiv po'ta zeshal aushfa mal-nef-hinek t'sa-veh. Ish-wak svi-aru."
# string = "Nam-tor Olozhika kluterek t'sha'sutenivaya k'ish she-tor etek s'nezhak isan utvau vah sha'kakhartayek."
# string = "Rok-tor etek ta sanoi nash uzh-rarav ik ki'fereik-tor nameT'Prion. Dungi olau ish-veh kunli pa'ta paribau k'kanok-veh svi'Shi'svatorai."
# string = "os-pid-vuhlkansu"
# string = "na'Gen-lis-tal a"
# string = "ahtortorki'fer eik-toraan-aish-ano-de"
# string = "mal-nef-hinek mal-nef-hinek mal-nef-hinek mal-nef-hinek"
# string = "mal-nef-hinek mal-nef-hinek mal-nef-hinek mal-nef-hinek mal-nef-hinek"
# string = "mal mal mal mal"
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
# string = "ketilikpitoh-su'us-ek'tal"
# string = "galu-dahshaya"
# string = "ro-kasaya ro-kasaya"
# string = "Nash-vel ra. Sular vi. Fai-tor du n'au ha. Katravahsular t'du ha."
# string = "Ki'nam-tor nash-veh heh kwon-sum dungau nam-tor t'hai'la t'du."
# translate = "Stonn killed the le-matya with an antler that he found in the sand after the animal bit his kneecap. It was mid-afternoon."
# translate = "Logic is the cement of our civilization with which we ascen from chaos, using reason as our guide."
# plt.title("\""+string+"\"\n I have and always shall be your friend.")
# plt.title("\""+string+"\"\n "+translate)

def generate_vulcan_calligraphy(string,line_break_height,contrast,complex_sentence_structure,dark_mode):
    line_break_height = line_break_height*4 # Pixel to coordinate conversion
    if(string[-1] != "." and string[-1] != "!"):
        string += "."
    string = string.replace(" ","_")
    print(string)
    clumps = separate_string_into_clumps(string.lower())
    print(clumps)

    figsize_x = 1
    figsize_y = 1
    complex_sentence_indicies = []
    figsize_x,figsize_y, complex_sentence_indicies = calculate_window_size(clumps,line_break_height,complex_sentence_structure)
    # linewidth = 1.5*np.sqrt((1+np.max([1,figsize_x/figsize_y,figsize_y/figsize_x])**2)/2)
    # linewidth = 2.5*np.sqrt(2)/np.sqrt(1+np.max([1,figsize_x/figsize_y,figsize_y/figsize_x])**2)

    # TODO Look at the size parameters here
    # if(figsize_y>figsize_x):
    #     main_fig, main_axs = plt.subplots(1, 1, figsize=(16, 16*figsize_y/figsize_x),layout="constrained")
    # if(figsize_y<figsize_x):
    #     main_fig, main_axs = plt.subplots(1, 1, figsize=(16*figsize_x/figsize_y, 16),layout="constrained")

    # np.max[16,figsize_y / figsize_x*16]
    # np.max[16,figsize_x / figsize_y*16]
    # if figsize_y > figsize_x:
    #     w, h = 16, 16 * figsize_y / figsize_x
    # else:
    #     w, h = 16 * figsize_x / figsize_y, 16

    # Create the figure
    main_fig = plt.figure(figsize=(np.max([resolution,resolution*figsize_x/figsize_y]), np.max([resolution,resolution*figsize_y/figsize_x])))
    linewidth = 1.5*resolution/16
    print("Linewidth:",linewidth)
    print("Figsize:",figsize_x,figsize_y)

    if(dark_mode):
        color = "white"
        plt.style.use('dark_background')
    else:
        color = "black"


    # Add a single axes that takes up 100% of the width and height [left, bottom, width, height]
    main_axs = main_fig.add_axes([0, 0, 1, 1])
    
    # plt.tight_layout()
    main_axs = [main_axs]
    if(not debug):
        main_axs[0].set_axis_off()

    width = get_svg_size("start.svg")[0]
    height = 0 # Required for the patam. Approximately half of the height of the numh.
    max_height = height

    line = 0 # The position of the active spine
    subbar = 0
    
    height = image("start.svg",main_axs[0],line,height,color)
    if(complex_sentence_structure and figsize_x>2*width):
        if(0 in complex_sentence_indicies):
            height = image("newline4.svg",main_axs[0],line,height,color)
            height = image("_.svg",main_axs[0],line,height,color,
                           subbranch_height-int(np.round(get_svg_size("newline4.svg")[1]/get_svg_size("_.svg")[1])))
            # height = image("_.svg",main_axs[0],line,height)
        else:
            height = image("_.svg",main_axs[0],line,height,color,subbranch_height)
    if(centered_on_nuhm):
        bars = [height+get_svg_size(clumps[1]+".svg")[1]/2]
    else:
        bars = [height]
    for i in range(len(clumps)):
        # If it is the end of a sentence, add vertical lines, line-break and start new sentence. Reset bars
        if(clumps[i]=="." or clumps[i]=="!"):
            if(len(bars)>1):
                if(centered_on_nuhm):
                    bars.append(height-get_svg_size(clumps[i-1]+".svg")[1]/2)
                else:
                    bars.append(height)
                curve(bars,main_axs[0],line,linewidth,contrast,color)
            
            if(complex_sentence_structure):
                subbar_position = get_svg_size("start.svg")[1]+get_svg_size("newline4.svg")[1]/2
                if(line != subbar):
                    main_axs[0].plot([subbar+get_svg_size("newline4.svg")[0]/2,line+width/2],
                                     [subbar_position,subbar_position],color=color,linewidth=linewidth*1.5)
            height = image("_.svg",main_axs[0],line,height,color,ending_height)
            if(clumps[i]=="!"):
                height = image("!.svg",main_axs[0],line,height,color)
            max_height = np.max([max_height,height])
            if(i!=len(clumps)-1):
                line += width*padding_factor
                height = 0
                # image("horizontal_line"+file_ending,main_axs[0])
                height = image("newline3.svg",main_axs[0],line,height,color)
                subbar = line
                if(complex_sentence_structure):
                    if(i+1 in complex_sentence_indicies):
                        height = image("newline4.svg",main_axs[0],line,height,color)
                        height = image("_.svg",main_axs[0],line,height,color,
                                       subbranch_height-int(np.round(get_svg_size("newline4.svg")[1]/get_svg_size("_.svg")[1])))
                        # height = image("_.svg",main_axs[0],line,height)
                    else:
                        height = image("_.svg",main_axs[0],line,height,color,subbranch_height)
                if(centered_on_nuhm):
                    bars = [height+get_svg_size(clumps[i+1]+".svg")[1]/2]
                else:
                    bars = [height]
        
        # If the space between two words in the middle of a sentence, add some spacing and reset bars.
        if(clumps[i]=="_" and clumps[i-1]!="."):
            if(len(bars)>1):
                if(centered_on_nuhm):
                    bars.append(height-get_svg_size(clumps[i-1]+".svg")[1]/2)
                else:
                    bars.append(height)
                print(bars)
                curve(bars,main_axs[0],line,linewidth,contrast,color)
            # If another nuhm can be fitted within the line_break_height
            if(height+space_height*get_svg_size("_.svg")[1] < line_break_height):
                height = image(clumps[i]+".svg",main_axs[0],line,height,color,space_height)
            else:
                height = image("newline2.svg",main_axs[0],line,height,color)
                max_height = np.max([max_height,height])
                line += width*padding_factor
                height = 0
                if(complex_sentence_structure):
                    height += get_svg_size("newline4.svg")[1]/2+get_svg_size("newline.svg")[1]/2
                # image("horizontal_line"+file_ending,main_axs[0])
                height = image("newline.svg",main_axs[0],line,height,color)
                if(complex_sentence_structure):
                    height = image("_.svg",main_axs[0],line,height,color,
                                subbranch_height-int(np.round((get_svg_size("newline.svg")[1]+get_svg_size("newline4.svg")[1])/2/get_svg_size("_.svg")[1])))
                # if(centered_on_nuhm):
                #     bars = [height+get_svg_size(clumps[i+1]+".svg")[1]/2]
                # else:
                #     bars = [height]
            if(centered_on_nuhm):
                bars = [height+get_svg_size(clumps[i+1]+".svg")[1]/2]
            else:
                bars = [height]
        
        # If there are bars, do not add a nuhm, just prepare for the swirls.
        if(clumps[i]=="-"):
            bars.append(height)
        
        if(clumps[i]==","):
            height = image("_.svg",main_axs[0],line,height,color,space_height)

        # If normal nuhms, just add them.
        if(clumps[i]!="-" and clumps[i]!="." and clumps[i]!="_" and clumps[i]!="!"):
            height = image(clumps[i]+".svg",main_axs[0],line,height,color)
            if(clumps[i]=="'" and len(bars)==1):
                if(centered_on_nuhm):
                    bars = [height+get_svg_size(clumps[i+1]+".svg")[1]/2]
                else:
                    bars = [height]

        # If the line exceeds the specified height limit, insert a line-break and continue on new line.
        # if(height+space_height*get_svg_size("_.svg")[1] > line_break_height and clumps[i]=="_" and clumps[i-1]!="."):
        #     height = image("newline2.svg",main_axs[0],line,height)
        #     max_height = np.max([max_height,height])
        #     line += width*padding_factor
        #     height = 0
        #     if(complex_sentence_structure):
        #         height += get_svg_size("start.svg")[1]+get_svg_size("newline4.svg")[1]/2-get_svg_size("newline.svg")[1]/2
        #     # image("horizontal_line"+file_ending,main_axs[0])
        #     height = image("newline.svg",main_axs[0],line,height)
        #     if(centered_on_nuhm):
        #         bars = [height+get_svg_size(clumps[i+1]+".svg")[1]/2]
        #     else:
        #         bars = [height]
        # print(i,clumps[i],height,figsize_x)
    
    save_images_in_pdf(current_directory+"/Optimizer.pdf",list_of_figures)

    # The horizontal spine
    main_axs[0].plot([0,width/2+line],[get_svg_size("start.svg")[1]/2,get_svg_size("start.svg")[1]/2],color=color,linewidth=linewidth*1.5)
    main_axs[0].set_xlim(-width,width+line)
    main_axs[0].set_ylim(max_height+width/2,-width/2)
    if(debug):
        main_axs[0].hlines(y=line_break_height,xmin=-width,xmax=width+line,color="red",linestyle="--")
    # main_fig.tight_layout()
    main_fig.savefig(current_directory+"/Generated text.png")

# generate_vulcan_calligraphy(string)

# import subprocess
# from PIL import Image
# from pathlib import Path

# def png_to_svg_with_brightness(input_png, output_svg, brightness=0.55,scale_up=1/10):
#     potrace_path = current_directory+"/potrace-1.16.win64/potrace.exe"  # Full path to Potrace
#     input_png = Path(input_png)
#     temp_pbm = input_png.with_suffix(".pbm")

#     # Convert to grayscale + apply brightness threshold
#     img = Image.open(input_png).convert("L")
#     img = img.point(lambda p: 255 if p/255 > brightness else 0)  # threshold
#     img.save(temp_pbm)

#     # Run Potrace to convert PBM to SVG
#     subprocess.run([
#         potrace_path,
#         str(temp_pbm),
#         "--svg",
#         "-o", str(output_svg)
#     ], check=True)

#     temp_pbm.unlink()  # cleanup

# png_to_svg_with_brightness(
#     current_directory+"/Generated text.png",
#     current_directory+"/output.svg",
#     brightness=0.55
# )

# import xml.etree.ElementTree as ET
# from pathlib import Path

# def count_subpaths_in_path(d):
#     return d.count('M') + d.count('m')

# def list_paths_and_subpaths(svg_path):
#     path_numbers = []
#     svg_path = Path(svg_path)
#     tree = ET.parse(svg_path)
#     root = tree.getroot()
#     ns = {"svg": "http://www.w3.org/2000/svg"}

#     paths = root.findall(".//svg:path", ns)
#     total_subpaths = 0
#     for i, path in enumerate(paths, 1):
#         d_attr = path.attrib.get("d", "")
#         subs = count_subpaths_in_path(d_attr)
#         total_subpaths += subs
#         print(f"Path {i}: {subs} subpaths")
#         path_numbers.append(subs)

#     print(f"\nTotal subpaths (potential FreeCAD regions): {total_subpaths}")
#     return path_numbers

# path_numbers = list_paths_and_subpaths(current_directory+"/output.svg")
# print(path_numbers)
# # ---------------------------------------------------

# f = open(current_directory+"/Demo.svg")
# content = f.read()

# text_to_copy = content.split("<svg")[1].split("<path")[0]
# # print(text_to_copy)

# f = open(current_directory+"/output.svg")
# content = f.read()
# text_to_replace = content.split("<svg")[1].split("<path")[0]

# content = content.replace(text_to_replace,text_to_copy)

# with open(current_directory+"/output.svg", "w") as f:
#   f.write(content)

# from svgpathtools import parse_path
# def svg_paths_bbox(svg_file):
#     tree = ET.parse(svg_file)
#     root = tree.getroot()

#     # Handle namespaces
#     ns = {"svg": "http://www.w3.org/2000/svg"}

#     # Track global bounding box
#     global_xmin = float("inf")
#     global_xmax = float("-inf")
#     global_ymin = float("inf")
#     global_ymax = float("-inf")

#     # Find all path elements
#     for path_elem in root.findall(".//svg:path", ns):
#         d = path_elem.get("d")
#         if not d:
#             continue
#         path = parse_path(d)
#         xmin, xmax, ymin, ymax = path.bbox()

#         global_xmin = min(global_xmin, xmin)
#         global_xmax = max(global_xmax, xmax)
#         global_ymin = min(global_ymin, ymin)
#         global_ymax = max(global_ymax, ymax)

#     width = global_xmax - global_xmin
#     height = global_ymax - global_ymin

#     return width, height, (global_xmin, global_ymin, global_xmax, global_ymax)

# svg_file = current_directory+"/output.svg"
# width, height, bbox = svg_paths_bbox(svg_file)

# print("Width:", width)
# print("Height:", height)
# print(bbox)