import argparse
from enum import Enum
import io

from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5
    NONE = 6


def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)
    return image

def get_container_bound(word_bound, container_list):
    file = open('container_output.txt',"a")
    file.write(f'word_bound is {word_bound} and list is {container_list}')
    file.close()
    for container in container_list:
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(is_word_in_block(word_bound,container))
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        if is_word_in_block(word_bound,container):
            print(container)
            return container
    return container_list[0]

def area(x1, y1, x2, y2, x3, y3):
      return abs((x1 * (y2 - y3) +
                x2 * (y3 - y1) +
                x3 * (y1 - y2)) / 2.0)


def check(vertex,bound):
    x = vertex.x
    y = vertex.y
    x1 = bound.vertices[0].x - 2
    y1 = bound.vertices[0].y - 2
    x2 = bound.vertices[1].x + 2
    y2 = bound.vertices[1].y - 2
    x3 = bound.vertices[2].x + 2
    y3 = bound.vertices[2].y + 2
    x4 = bound.vertices[3].x - 2
    y4 = bound.vertices[3].y + 2

    A = (area(x1, y1, x2, y2, x3, y3) +
         area(x1, y1, x4, y4, x3, y3))
    A1 = area(x, y, x1, y1, x2, y2)
    A2 = area(x, y, x2, y2, x3, y3)
    A3 = area(x, y, x3, y3, x4, y4)
    A4 = area(x, y, x1, y1, x4, y4);

    return (A == A1 + A2 + A3 + A4)




def is_word_in_block(word_bound, block_bound):
    # print("****************BLOCK TEST***********************")
    # print(check(word_bound.vertices[0],block_bound))
    # print(check(word_bound.vertices[1],block_bound))
    # print(check(word_bound.vertices[2],block_bound))
    # print(check(word_bound.vertices[3],block_bound))
    # print("****************BLOCK TEST END***********************")
    if (check(word_bound.vertices[0],block_bound) and
    check(word_bound.vertices[1],block_bound) and
    check(word_bound.vertices[2],block_bound) and
    check(word_bound.vertices[3],block_bound)):
        return True
    else:
        return False

# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(is_word_in_block(word_bound,container))
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
def get_word_bound(word,dict_list):
    all_words =[]
    for dict in dict_list:
        if(dict["description"] == word):
            all_words.append(dict["bound"])
    return all_words

def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient()

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(is_word_in_block(word_bound,container))
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    responseWord = client.text_detection(image=image)
    texts = responseWord.text_annotations
    if(feature == FeatureType.NONE):
        for text in texts:
            text_data ={
            "description":text.description,
            "bound": text.bounding_poly
            }
            bounds.append(text_data)
    else:
    # Collect specified feature bounds by enumerating all document features
        for page in document.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        for symbol in word.symbols:
                            if (feature == FeatureType.SYMBOL):
                                bounds.append(symbol.bounding_box)

                        if (feature == FeatureType.WORD):
                            bounds.append(word.bounding_box)

                    if (feature == FeatureType.PARA):
                        bounds.append(paragraph.bounding_box)

                if (feature == FeatureType.BLOCK):
                    bounds.append(block.bounding_box)

            if (feature == FeatureType.PAGE):
                bounds.append(block.bounding_box)

    return bounds


def get_all_words_within_container(container_bound,word_list):
    words_within=[]
    for word in word_list:
        if is_word_in_block(word["bound"], container_bound):
            words_within.append(word["description"])
    return words_within


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    # bounds = get_document_bounds(filein, FeatureType.PAGE)
    # draw_boxes(image, bounds, 'blue')
    boundsBlock = get_document_bounds(filein, FeatureType.BLOCK)
    draw_boxes(image,boundsBlock,'green')
    # bounds = get_document_bounds(filein, FeatureType.PARA)
    # draw_boxes(image, bounds, 'red')
    # boundsWord = get_document_bounds(filein, FeatureType.WORD)
    # draw_boxes(image, boundsWord, 'red')
    #
    boundsTest = get_document_bounds(filein,FeatureType.NONE)
    # for item in boundsTest:
    #     if item["description"]=="$1,231.62":
    #             print(item["bound"])

    amount_bound = get_word_bound("Amount",boundsTest)
    final_result = []
    for amt in amount_bound:
        result =[]
        for bounds in boundsTest:
            if is_word_in_block(bounds["bound"], get_container_bound(amt,boundsBlock)):
                result.append(bounds["description"])
        final_result.append(result)
    # print(get_all_words_within_container(boundsBlock[0],boundsTest))
    print(final_result)
    rgb_im = image.convert('RGB')
    if fileout is not 0:
        rgb_im.save(fileout)
    else:
        rgb_im.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('detect_file', help='The image for text detection.')
    parser.add_argument('-out_file', help='Optional output file', default=0)
    args = parser.parse_args()

    render_doc_text(args.detect_file, args.out_file)
