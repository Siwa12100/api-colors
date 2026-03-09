from PIL import Image
import colorsys
import math
import extcolors
import tempfile as TF
import requests

## "white", "grey" and "black" are also possible colors,
## although not represeneted in this dictionary
COLORS = {
    "red": [*range(0,20)] + [*range(340,356)],
    "orange": range(20, 45),
    "yellow": range(45, 70),
    "green": range(70, 135),
    "cyan": range(135, 185),
    "blue": range(185, 250),
    "purple": range(250, 280),
    "pink": range(280, 340)
}

def get_image(url: str):
    """
    Gets the thumbnail from the url passed as a param.
    Returns: file-like object

    Contract: calling function has to CLOSE the returned 
    file object when done with it.
    """
    data = requests.get(url).content

    ## creating a safe tmpfile
    tmp_file = TF.NamedTemporaryFile()

    # Storing the image data inside the data variable to the file
    tmp_file.write(data)
    return tmp_file

## --------------- COLORS

def dominant_colors(img: Image) -> tuple:
    """
    Calculates the dominant colors of an image
    and returns them as a list of tuples ((rgb), occurencies).
    from https://towardsdatascience.com/image-color-extraction-with-python-in-4-steps-8d9370d9216e/
    """
    colors = extcolors.extract_from_image(img, tolerance=20, limit=5)
    
    return colors[0]


def classisfy_color(color: tuple):
    """
    Takes an rgb tuple and determines which of the predefined
    colors it is the closest to.
    """
    color_class = ""

    color = tuple(map(lambda a: a/256, color))
    color = colorsys.rgb_to_hsv(*color) # conversion to HSV
    hue, sat, bright = color
    hue *= 355
    sat *= 100
    bright *= 100

    if sat <= 15 and bright >= 75:
        color_class = "white"
    elif sat <= 15 and bright <= 10:
        color_class = "black"
    elif sat > 15 and bright >= 20:
        for name, color_range in COLORS.items():
            if math.floor(hue) in color_range:
                color_class = name
                break
    else:
        color_class = "grey"

    return color_class

def determine_dominant(image: Image):
    """
    Determines the 3 most dominant colors (could be less), 
    taking into account at most the 5 most present colors.
    Returns: list of max 3 strings
    """
    colors = dominant_colors(image)
    present = {}

    for color, count in colors:
        dom = classisfy_color(color)
        # print(dom)
        if dom in present: present[dom] += count
        else: present[dom] = count


    most_colors = list(present.items())
    most_colors.sort(key = lambda a: a[1], reverse=True) # sort by occurances
    most_colors = [color for color, count in most_colors]
    # print("occurancies, classified and sorted: ", most_colors)
    return most_colors[:3] if len(most_colors) >= 3 else most_colors

## ----------- OTHER

def avg_luminosity(img):
    ## look at every pixel, sum luminsoity (HSV brightness)
    ## and divide by nb pixels
    image = img.convert("HSV")
    brightness_sum = 0
    nb_pixels = image.width * image.height
    for x in range(image.width):
        for y in range(image.height):
            hue, sat, bright = image.getpixel((x,y))
            brightness_sum += bright
    
    return math.floor(brightness_sum / nb_pixels)


def general_contrast():
    ## what does this mean ????
    pass

def ratio(width: int, height: int):
    ## classify image ratio if it is a common one 
    ## (tolerqnce of 5px diff) otherwise just return
    ## width x height
    return (width, height) 

## ----------- OVERALL
def analyse_image(url: str):
    img_file = get_image(url)
    image = Image.open(img_file.name)
    image = image.resize((150, 150))      # optional, to reduce time
    dom_colors = determine_dominant(image)
    avg_lum = avg_luminosity(image)
    img_file.close()

    return {
        "dom_colors": dom_colors,
        "avg_luminosity": avg_lum
    }

# print("dom colors:", determine_dominant('../../../../../../mnt/c/Users/emafi/OneDrive/Počítač/fotky/lyon_ela/IMG_0772.JPG'))