# -*- coding: utf-8 -*-
import logging
import os
import random
import re
import sys
import string
import pickle
from collections import defaultdict
import codecs
import unicodedata
import glob
# import nltk

PERMISSIBLE_PUNCTUATION = [u'!', u',', u'?', u'.', u'’', u':', u';']

PUNCTUATION_TRANSLATE_TABLE = {i:None for i in range(sys.maxunicode)
    if unicodedata.category(unichr(i)).startswith('P') and unichr(i) not in PERMISSIBLE_PUNCTUATION}

def collable():
    return defaultdict(float)

class TextGenerator:
    def __init__(self):
        self.cortage_ = defaultdict(collable)


    def SentenceBreaker(self, sentence):
        key = tuple([''] * 2)
        sentence = sentence.strip()
        # Берём и делим по всем знакам препинания, рассматривая их как отдельные слова
        sentence = re.split(r'([.!?,:;])', sentence)
        splited_sentence = []
        for combination_of_words in sentence:
            splited_sentence += combination_of_words.split()
        sentence_iterable = iter(splited_sentence)
        last_word = sentence_iterable.next()
        for word in sentence_iterable:
            yield key, last_word
            key = (key[1], last_word)
            last_word = word
        yield key, last_word

    def BookSentenceFinder(self, book):
        book = book.read()
        # Удаляем всю пунктуацию кроме некоторых знаков, с которыми хочется поиграться дальше
        book = book.translate(PUNCTUATION_TRANSLATE_TABLE)
        # Регулярным выражением разбиваем текст на предложения, можно было бы
        # использовать nltk, но решил что лучше обойтись подручными средствами
        book = re.findall(r'[^ ].*?[.!?]', book)
        # book = nltk.sent_tokenize(book)
        for sentence in book:
            yield sentence
        
    def GenerateCortage(self, directory = "./corpus/*.txt"):
        # С помощью codecs.open() избегаем проблем с чтением юникода и utf
        try:
            books = glob.glob(directory)
        except IOError:
            print u"Ошибка при открытии директории,", directory
        it = 1
        for book_file in books:
            # Просто итератор, чтобы не скучно было ждать конца обработки
            print it
            it += 1
            try:
                book = codecs.open(book_file, "r", "utf-8-sig")
            except IOErrorex:
                print u"Ошибка при открытии файла,", book_file
            seed = ("", "")
            for sentence in self.BookSentenceFinder(book):
                for key, word in self.SentenceBreaker(sentence):
                    self.cortage_[key][word] += 1
        self.NormalizeIt()
        with open('cortage.pickle', 'wb') as file_with_cortage:
            pickle.dump(self.cortage_, file_with_cortage)

    def OpenCortage(self, file_with_cortage = "./cortage.pickle"):
        try:
            with open(file_with_cortage, 'rb') as file_with_cortage:
                self.cortage_ = pickle.load(file_with_cortage)
        except IOError:
            print u"Ошибка при открытии файла-кортежа,", file_with_cortage

    def NormalizeIt(self):
        for key in self.cortage_:
            zustandsumme = 0.0 #Стат сумма для всех слов
            for word in self.cortage_[key]:
                zustandsumme += self.cortage_[key][word]
            if zustandsumme != 0:
                for word in self.cortage_[key]:
                    self.cortage_[key][word] /= zustandsumme

    def GenerateText(self, number_of_paragraph = 500):
        text = []
        for it in range(number_of_paragraph):
            text.append(self.GenerateParagraph())
        text = ''.join(text)
        try:
            text_file = codecs.open("Output.txt", "w","utf-8-sig")
            text_file.write(text)
        except IOError:
            print u"Ошибка призаписи в файл,", directory

    def GenerateParagraph(self):
        paragraph_length = random.randint(1, 12)
        paragraph = []
        for it in range(paragraph_length):
            paragraph.append(self.GenerateSentence())
        paragraph.append("\n\n")
        return ''.join(paragraph)
        
    def GenerateSentence(self):
        sentence = []
        key = ("", "")
        quotes = 0
        previous_word_from_punct = False
        sentence_ended = False
        first_word = True
        for it in range(50):
            next_word = self.NextWord(key)
            if first_word:
                next_word.title()
                first_word = False
            if next_word == "":
                sentence_ended = True
                break
            if next_word in PERMISSIBLE_PUNCTUATION:
                if previous_word_from_punct:
                    continue
                previous_word_from_punct = True
                sentence.append(next_word)
                key = (key[1], next_word)
                continue
            previous_word_from_punct = False
            sentence.append(" ")
            sentence.append(next_word)
            key = (key[1], next_word)
        if not sentence_ended:
            sentence.append(".")
        return  ''.join(sentence)

    def NextWord(self, key):
        eventual_next_words = self.cortage_[key]
        probability = random.random()
        most_common = ""
        prob_max = 0
        for next_word in eventual_next_words:
            if prob_max < eventual_next_words[next_word]:
                prob_max = eventual_next_words[next_word]
                most_common = next_word
            if eventual_next_words[next_word] > probability:
                return next_word
            probability -= eventual_next_words[next_word]
        return most_common
        
def BookWriter():
    textGen = TextGenerator()
    # textGen.GenerateCortage()
    textGen.OpenCortage()
    textGen.GenerateText()
    
BookWriter()
