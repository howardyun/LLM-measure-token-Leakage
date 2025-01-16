import math
import re
import json
import os

BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
HEX_CHARS = "1234567890abcdefABCDEF"


def shannon_entropy(data, iterator):
    """
    Borrowed from http://blog.dkbza.org/2007/05/scanning-data-for-entropy-anomalies.html
    """
    if not data:
        return 0
    entropy = 0
    for x in iterator:
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy


def get_strings_of_set(word, char_set, threshold=20):
    count = 0
    letters = ""
    strings = []
    for char in word:
        if char in char_set:
            letters += char
            count += 1
        else:
            if count > threshold:
                strings.append(letters)
            letters = ""
            count = 0
    if count > threshold:
        strings.append(letters)
    return strings


def find_entropy(strings_output):
    """
    高熵
    #this identifies base64 and hex high entropy strings, this should be used in conjunction with 'strings' output to be more efficient
    :param strings_output:
    :return:
    """
    strings_found = []
    lines = strings_output.split("\n")
    for line in lines:
        for word in line.split():
            base64_strings = get_strings_of_set(word, BASE64_CHARS)
            hex_strings = get_strings_of_set(word, HEX_CHARS)
            for string in base64_strings:
                b64Entropy = shannon_entropy(string, BASE64_CHARS)
                if b64Entropy > 4.5:
                    strings_found.append(string)
            for string in hex_strings:
                hexEntropy = shannon_entropy(string, HEX_CHARS)
                if hexEntropy > 3:
                    strings_found.append(string)
    if len(strings_found) > 0:
        print(strings_found)


def regex_check():
    """
    正则
    :return:
    """
    with open(os.path.join(os.path.dirname(__file__), "regexes.json"), 'r') as f:
        regexes = json.loads(f.read())

    for key in regexes:
        regexes[key] = re.compile(regexes[key])


if __name__ == '__main__':
    pass
