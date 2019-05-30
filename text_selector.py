import argparse
from enum import Enum
import io
import os
import base64
import re
import math
import time
from fuzzywuzzy import process
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/user/Desktop/mpower/textfiles/OCR-TEST-3aa327fd94ed.json"#!/usr/bin/env python3


from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw


_provider_name = ''
_guarantor_name = ''
_provider_address = ''


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
    """
    The method takes in boundry
    """
    for container in container_list:
        if is_word_in_block(word_bound,container):
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
    if (check(word_bound.vertices[0],block_bound) and
    check(word_bound.vertices[1],block_bound) and
    check(word_bound.vertices[2],block_bound) and
    check(word_bound.vertices[3],block_bound)):
        return True
    else:
        return False
def distance_between_point(point1,point2):
    return math.pow(point1.x-point2["x"],2) + math.pow(point1.y-point2["y"],2)

def get_word_bound(word,dict_list):
    all_words =[]
    for dict in dict_list:
        if(dict["description"] == word):
            all_words.append(dict["bound"])
    return all_words

def get_matched_word(regex,dict_list):
     all_words =[]
     for dict in dict_list:
         if(re.search(regex, dict["description"])):
             all_words.append(dict["bound"])
     return all_words

def get_document_bounds(file_name, feature):
    """Returns document bounds given an image."""
    print("Testing Google API time:")
    start = time.time()
    client = vision.ImageAnnotatorClient()
    # print(b64_string)
    boundsWord = []
    bounds = []

    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()
    # print(type(content))
    # print("content: " + content)

    image = types.Image(content=content)

    # image = types.Image(content=content)
# print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(is_word_in_block(word_bound,container))
        # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    responseWord = client.text_detection(image=image)
    texts = responseWord.text_annotations
    end = time.time()
    print(end-start)

    for text in texts:
        desc = text.description.replace(',', '').replace('(','')
        text_data ={
        "description":desc.lower(),
        "bound": text.bounding_poly
        }
        boundsWord.append(text_data)
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

    return boundsWord,bounds


def get_all_words_within_container(container_bound,word_list):
    words_within=[]
    for word in word_list:
        if is_word_in_block(word["bound"], container_bound):
            words_within.append(word["description"])
    return words_within

def resize_container_with_buffer(bound,buffer):
    bound.vertices[0].x = bound.vertices[0].x - buffer
    bound.vertices[0].y = bound.vertices[0].y - buffer
    bound.vertices[1].x = bound.vertices[1].x + buffer
    bound.vertices[1].y = bound.vertices[1].y - buffer
    bound.vertices[2].x = bound.vertices[2].x + buffer
    bound.vertices[2].y = bound.vertices[2].y + buffer
    bound.vertices[3].x = bound.vertices[3].x - buffer
    bound.vertices[3].y = bound.vertices[3].y + buffer
    return bound

def render_from_post_call(b64_string):
    print("test")
    start_block = time.time()
    boundsTest,boundsBlock = get_document_bounds(b64_string, FeatureType.BLOCK)
    # boundsTest = get_document_bounds(b64_string,FeatureType.NONE)
    end_block_time = time.time()
    print("Time taken to calculate blocks")
    print(end_block_time-start_block)

    start_getter = time.time()
    amount_bound = get_word_bound("amount",boundsTest)
    due_bound = get_word_bound("due",boundsTest)
    amt_result_bound = amount_bound+due_bound
    final_result = []
    for amt in amt_result_bound:
        result =[]
        for bounds in boundsTest:
            if is_word_in_block(bounds["bound"], get_container_bound(amt,boundsBlock)):
                result.append(bounds["description"])
        final_result.append(result)
    # print(get_all_words_within_container(boundsBlock[0],boundsTest))
    filtered_result=[]
    for result in final_result:
        r = re.compile(r"^\$?[0-9]+\.?[0-9]*$")
        newlist = list(filter(r.match, result))
        if newlist:
            filtered_result.append(newlist)
    print(filtered_result)
    if not filtered_result:
        amount_value =  get_farthest_regex(boundsTest,r"^\$[0-9]+\.?[0-9]*$")
    else:
        amount_value = filtered_result[0][0]
    provider_name = get_provider_name(b64_string,boundsBlock,boundsTest)
    provider_address = get_provider_address(b64_string,provider_name,boundsTest,boundsBlock)
    guarantor_number,guarantor_name = get_guarantor_number(b64_string,boundsTest,boundsBlock)
    end_getter = time.time()
    print("Getter functions :")
    print(end_getter-start_getter)
    return amount_value,provider_name,provider_address,guarantor_name,guarantor_number


def get_farthest_regex(boundsTest,regex):
    regex_blocks = get_matched_word(regex,boundsTest)
    if not regex_blocks:
        return ''
    max_distance = 0
    farthest_bound = regex_blocks[0]
    origin = {"x":0, "y":0}
    for block in regex_blocks:
        if distance_between_point(block.vertices[0],origin) > max_distance:
            max_distance = distance_between_point(block.vertices[0],origin)
            farthest_bound = block
    for block in boundsTest:
        if block["bound"]==farthest_bound:
            result = block["description"]
    return result

def get_provider_name(b64_string,boundsBlock,boundsTest):
    min_distance = 10000
    provider_name_container = boundsBlock[0]
    origin = {"x":0, "y":0}
    for block in boundsBlock:
        if distance_between_point(block.vertices[0],origin) < min_distance:
            min_distance = distance_between_point(block.vertices[0],origin)
            provider_name_container = block

    resize_container_with_buffer(provider_name_container,10)
    list = get_all_words_within_container(provider_name_container,boundsTest)
    # image = Image.open(b64_string)
    # draw_boxes(image,boundsBlock,'green')
    # rgb_im = image.convert('RGB')
    # rgb_im.show()
    return ' '.join(list)

def get_provider_address(b64_string,provider_name,boundsTest,boundsBlock):
    pincode_bound = get_matched_word(r'^[0-9]{5}(?:-[0-9]{4})?$',boundsTest)
    final_result = []
    for pincode in pincode_bound:
        result =[]
        for bounds in boundsTest:
            if is_word_in_block(bounds["bound"], get_container_bound(pincode,boundsBlock)):
                result.append(bounds["description"])

        final_result.append(' '.join(result))
    print(final_result)
    _provider_address = get_fuzzy_matched_string(provider_name,final_result)
    return _provider_address

def get_guarantor_number(b64_string,boundsTest,boundsBlock):
    guarantor_bound = get_word_bound("guarantor",boundsTest)
    final_result =[]
    for grn_bound in guarantor_bound:
        result =[]
        for bounds in boundsTest:
            if is_word_in_block(bounds["bound"], get_container_bound(grn_bound,boundsBlock)):
                result.append(bounds["description"])
        final_result.append(result)
    # print(get_all_words_within_container(boundsBlock[0],boundsTest))
    filtered_result=[]
    for result in final_result:
        r = re.compile(r"^(\d{9})$")
        newlist = list(filter(r.match, result))
        if newlist:
            filtered_result.append(newlist)
    print(filtered_result)
    if not filtered_result:
        guarantor_number = ''
    else: guarantor_number =  filtered_result[0][0]

    filtered_result =[]
    isname = False
    for result in final_result:
        if 'name' in result:
            filtered_result.append(' '.join(result))


    guarantor_name =''
    for flist in filtered_result:
        regexp = re.compile(r"^[_A-z][_A-z\s]*$")
        if(regexp.search(flist)):
            flist = flist.split()
            if(len(flist)>=4):
                guarantor_name = flist[2]+" "+flist[3]

    return guarantor_number,guarantor_name




def get_fuzzy_matched_string(string, list_of_strings):
    if not list_of_strings:
        return ''
    [address,score] = process.extractOne(string,list_of_strings)
    return address
# def render_doc_text(filein, fileout):
#     image = Image.open(filein)
#     # bounds = get_document_bounds(filein, FeatureType.PAGE)
#     # draw_boxes(image, bounds, 'blue')
#     boundsBlock = get_document_bounds(filein, FeatureType.BLOCK)
#     draw_boxes(image,boundsBlock,'green')
#     # bounds = get_document_bounds(filein, FeatureType.PARA)
#     # draw_boxes(image, bounds, 'red')
#     # boundsWord = get_document_bounds(filein, FeatureType.WORD)
#     # draw_boxes(image, boundsWord, 'red')
#     #
#     boundsTest = get_document_bounds(filein,FeatureType.NONE)
#     # for item in boundsTest:
#     #     if item["description"]=="$1,231.62":
#     #             print(item["bound"])
#
#     amount_bound = get_word_bound("amount",boundsTest)
#     due_bound = get_word_bound("due",boundsTest)
#     amt_result_bound = amount_bound+due_bound
#
#
#     final_result = []
#     for amt in amt_result_bound:
#         result =[]
#         for bounds in boundsTest:
#             if is_word_in_block(bounds["bound"], get_container_bound(amt,boundsBlock)):
#                 result.append(bounds["description"])
#         final_result.append(result)
#     # print(get_all_words_within_container(boundsBlock[0],boundsTest))
#     filtered_result=[]
#     for result in final_result:
#         r = re.compile(r"^\$?[0-9]+\.?[0-9]*$")
#         print("result is:")
#         print(result)
#         newlist = list(filter(r.match, result))
#         print("new result is:")
#         print(newlist)
#         filtered_result.append(newlist)
#     print(filtered_result)
#     rgb_im = image.convert('RGB')
#     if fileout is not 0:
#         rgb_im.save(fileout)
#     else:
#         rgb_im.show()

def test_function(values):
    start_total = time.time()
    amt,provider_name,pvr_add,gr_name,gr_number = render_from_post_call(values)
    # provider_name = get_provider_name(values)
    # pvr_add = get_provider_address(values,provider_name)
    # gr_number,gr_name = get_guarantor_number(values)
    # print(gr_number,gr_name)
    jt = {
    'amount':amt,
    'provider_name':provider_name,
    'provider_address':pvr_add,
    'guarantor_number':gr_number,
    'guarantor_name':gr_name
    }
    final_time = time.time()
    print("total_time taken:")
    print(final_time-start_total)
    return jt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('detect_file', help='The image for text detection.')
    parser.add_argument('-out_file', help='Optional output file', default=0)
    args = parser.parse_args()

    render_doc_text(args.detect_file, args.out_file)
