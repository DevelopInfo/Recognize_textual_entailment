# -*- coding: UTF-8 -*-

import sys
import os
CURRENT_PAHT = os.path.dirname(__file__)
import json
import nltk
from tqdm import tqdm

DATA_PATH = os.path.dirname(os.path.dirname(CURRENT_PAHT))+"/data"
mul_snli_jsonl = [
    DATA_PATH+"/snli_1.0/snli_1.0_train.jsonl",
    DATA_PATH+"/snli_1.0/snli_1.0_dev.jsonl",
    DATA_PATH+"/snli_1.0/snli_1.0_test.jsonl"
]
num_lines_list = [
    550152, 
    10000, 
    10000
]

wordvec_file = DATA_PATH+"/glove.6B/glove.6B.50d.txt"
num_words = 400000

DATA_PROCESSED_PATH = DATA_PATH+"/data_processed"

words_dict_file = DATA_PROCESSED_PATH+"/words_dictionary.txt"
words_embedding_file = DATA_PROCESSED_PATH+"/words_embedding.txt"
mul_snli_jsonl_encoded = [
    DATA_PROCESSED_PATH+"/snli_train_encoded.jsonl",
    DATA_PROCESSED_PATH+"/snli_dev_encoded.jsonl",
    DATA_PROCESSED_PATH+"/snli_test_encoded.jsonl"
]
chars_dict_file = DATA_PROCESSED_PATH+"/chars_dictionary.txt"


def read_pretrain_wordvec(wordvec_file=wordvec_file, num_words=num_words):
    """
    Read pretrain wordvec file.
    Params:
        wordvec_file: the pretrain wordvec file path.
    Returns:
        wordvecs_dict: the wordvec dictionary whose key is word 
            and value is embedding vec.
    """
    wordvecs = open(wordvec_file, 'r')
    wordvecs_dict = dict()
    for i, line in tqdm(enumerate(wordvecs), total=num_words, desc="Read pretrain wordvec"):
        wordvecs_dict[line.split()[0]] = list(map(float,line.split()[1:]))
    # key = word, value = embedding
    return wordvecs_dict


def read_words_dict(words_dict_file=words_dict_file):
    """
    Read words dictionary file.
    Params:
        words_dict_file: the words dictionary file path.
    Returns:
        words_dict: the dict of words.
    """
    words_dict = dict()
    dict_obj = open(words_dict_file, "r")
    for i, word in enumerate(dict_obj):
        # PADDING and UNKNOWN
        words_dict[word.strip("\n")] = i+2

    return words_dict


def read_chars_dict(chars_dict_file=chars_dict_file):
    """
    Read characters dictionary
    Params:
        chars_dict_file: the characters dict file path.
    Returns:
        chars_dict: the dictionary of characters.
    """
    chars_dict = dict()
    chars_obj = open(chars_dict_file, "r")
    for i, char in enumerate(chars_obj):
        chars_dict[char.strip('\n')] = i
    
    return chars_dict


def load_words_set(mul_snli_jsonl=mul_snli_jsonl, num_lines_list=num_lines_list):
    """
    Create words dictionary.
    Params:
        mul_snli_jsonl: the list of train, dev and test file.
    Returns:
        words_set: the words set which contain all words occured in snli.
    """
    words_set = set()

    files_list = list()
    for i in range(len(mul_snli_jsonl)):
        file_obj = open(mul_snli_jsonl[i],'r')
        files_list.append(file_obj)
    for i, file_obj in tqdm(enumerate(files_list), desc="Read snli file", total=len(files_list)):
        for j, elem in tqdm(enumerate(file_obj), desc="Read one of file", total=num_lines_list[i]):
            elem = json.loads(elem)
            for p, word in enumerate(nltk.word_tokenize(elem["sentence1"].lower())):
                words_set.add(word)
            for q, word in enumerate(nltk.word_tokenize(elem["sentence2"].lower())):
                words_set.add(word)
    
    return words_set


def create_embedding_and_dict(
    wordvec_file=wordvec_file, mul_snli_jsonl=mul_snli_jsonl, 
    words_embedding_file=words_embedding_file, words_dict_file=words_dict_file):
    """
    Create words embedding table file.
    Params:
        wordvec_file: the pretrain wordvec file path.
        mul_snli_jsonl: the list of train, dev and test file.
        words_embedding_file: the words embedding table file path that will create.
        words_dict_file: the words dictionary file path that will create.
    """
    wordvecs_dict = read_pretrain_wordvec(wordvec_file)
    words_set = load_words_set(mul_snli_jsonl)

    words_embedding_obj = open(words_embedding_file, "w")
    words_dict_obj = open(words_dict_file, "w")
    voc_size = len(words_set)
    
    print("Begin create embeding file and dict file:")
    print("Words size is {}.".format(voc_size))
    keys_set = set()
    for word in tqdm(words_set, total=voc_size, desc="Create ..."):
        try:
            words_embedding_obj.write(str(wordvecs_dict[word])+"\n")
            words_dict_obj.write(word+"\n")
        except KeyError:
            keys_set.add(word)
    
    print("KeyError size is {}.".format(len(keys_set)))
        

def create_chars_dict(mul_snli_jsonl=mul_snli_jsonl, chars_dict_file=chars_dict_file):
    """
    Create characters dictionary file.
    Params:
        mul_snli_jsonl: the list of train, dev and test file.
        chars_dict_file: the characters dictionary file path which will create.
    """
    words_set = load_words_set(mul_snli_jsonl)
    chars_set = set()
    for word in tqdm(words_set, total=len(words_set), desc="Create characters dict"):
        for char in word:
            chars_set.add(char)
    print("Character size is {}.".format(len(chars_set)))

    chars_dict_obj = open(chars_dict_file, "w")
    for char in chars_set:
        chars_dict_obj.write(char+'\n')


def encode_snli(
    mul_snli_jsonl=mul_snli_jsonl, mul_snli_jsonl_encoded=mul_snli_jsonl_encoded, 
    words_dict_file=words_dict_file, chars_dict_file=chars_dict_file, num_lines_list=num_lines_list):
    # read words dictionary
    words_dict = read_words_dict(words_dict_file)
    chars_dict = read_chars_dict(chars_dict_file)

    def encode_sentence(sentence):
        sent_word_list = list()
        sent_char_list = list()
        for i, word in enumerate(nltk.word_tokenize(elem["sentence1"].lower())):
            # encode word embedding
            try:
                sent_word_list.append(words_dict[word])
            except KeyError:
                # UNKNOWN
                sent_word_list.append(1)

            # encode character embedding
            word_char_list = list()
            for j, char in enumerate(word):
                word_char_list.append(chars_dict[char])
            sent_char_list.append(word_char_list)

        return sent_word_list, sent_char_list

    # open snli file
    files_list = list()
    for i in range(len(mul_snli_jsonl)):
        file_obj = open(mul_snli_jsonl[i],'r')
        files_list.append(file_obj)

    for i, file_obj in tqdm(enumerate(files_list), desc="Begin encoding snli", total=len(files_list)):
        encoded_file = open(mul_snli_jsonl_encoded[i], 'w')
        # entailment = 0, contradiction = 1, neutral = 2, - = 3
        label_list = ["entailment","contradiction","neutral","-"]
        for j, line in tqdm(enumerate(file_obj), desc="Encoding {}st file".format(i+1), total=num_lines_list[i]):
            elem = json.loads(line)
            elem_encoded = dict()
            elem_encoded["label"] = label_list.index(elem["gold_label"])
            # encoding sentence1
            elem_encoded["sentence1_word"], elem_encoded["sentence1_char"] = encode_sentence(elem["sentence1"])
            # encoding sentence2
            elem_encoded["sentence2_word"], elem_encoded["sentence2_char"] = encode_sentence(elem["sentence2"])
            # write encoded elem
            encoded_file.write(json.dumps(obj=elem_encoded, sort_keys=True)+"\n")

        encoded_file.close()


if __name__ == '__main__':
    create_embedding_and_dict()
    create_chars_dict()
    encode_snli()