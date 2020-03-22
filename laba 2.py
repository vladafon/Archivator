#!/usr/bin/env python
# coding: utf-8

# In[1]:


class node:
    letter = None
    value = 0
    left = None
    right = None
    
    def __lt__(self,other):
        return self.value<other.value
    
#Depth-first search

def dfs(n,dicti,code = ''):
    if n.letter:
        #print(n.letter, code)
        dicti[n.letter] = code
    if n.left:
        dfs(n.left, dicti, code+'0')
    if n.right:
        dfs(n.right, dicti, code+'1')


def haffman_compression(string):
    if len(string) % 2 != 0:
        string+='%'
    #parse into dict
    letters = {}

    for i in range(len(string)//2):
        letter = string[i*2:i*2+2]
        if letter not in letters:
            letters[letter] = 1
        else:
            letters[letter] += 1

    #Haffman
    node_list = []

    for key,value in letters.items():
        n = node()
        n.letter = key
        n.value = value
        node_list.append(n)
    
    while len(node_list) > 1:
        node_list.sort(reverse = True)
        n1 = node_list.pop()
        n2 = node_list.pop()
        n3 = node()
        n3.value = n1.value+n2.value
        n3.left = n1
        n3.right = n2
        node_list.append(n3)
 
    #get codes
    haffman = {}

    dfs(node_list[0],haffman)


    #get string
    compressed_string = ''

    for i in range(len(string)//2):
        letter = string[i*2:i*2+2]
        compressed_string += haffman[letter]
        
   # import numpy as np

    #H=0

    #for f in letters.values():
     #   H -= f/sum(letters.values())*np.log2(f/sum(letters.values()))
    #best_comp = (len(string)/2)*H
    
    return compressed_string, haffman #, best_comp

def BWT_compression(string):
    string = string + '^'
    list_of_strings = []
    
    #Получаем все перестановки строки
    for i in range(len(string)):
        list_of_strings.append(string[len(string)-i:]+string[:len(string)-i])
        
    comp_string = ''
    for s in sorted(list_of_strings):
        comp_string += s[-1] # выводим последний символ каждой строки
    return comp_string

def MTF_compression(text):
    letters = ['0','1','2','3','4','5','6','7','8','9','^',',']
    
    comp_string = ''
    
    for i in range(len(text)):
        mtf = letters.index(text[i])
        if mtf<10:
            comp_string += str(mtf)
        elif mtf == 10:
            comp_string += 'A'
        elif mtf == 11:
            comp_string += 'B'
        letters = letters[mtf:]+letters[:mtf] # сдвигаем массив
    return comp_string

def packaging(path, exitPath, L=1000):
    import datetime
    date = datetime.datetime.now()
    
    f = open(path,'rb') # Выберите любой файл у себя на компьютере, например картинку
    fd = f.read()
    
    #Get array of str bytes
    fd_int = [int(char) for char in fd]
    fd_str_int =  [str(num) for num in fd_int]

    #Получем кол-во блоков для разбения
    blocksCount = len(fd_str_int)//L
    
    blocks_array = []
    #Делим на блоки и собираем цельные строки из элементов группы с разделением через запятую
    for i in range(0,blocksCount):
        block = fd_str_int[i*L:(i+1)*(L)]
        part_string = ''
        for element in block:
            part_string += element + ','
        blocks_array.append(part_string.strip(','))

    #Учтываем остаток в конце
    block = fd_str_int[blocksCount*L:]
    part_string = ''
    for element in block:
        part_string += element + ','
    if (part_string.strip(',') != ''):
        blocks_array.append(part_string.strip(','))

    #Сжатие алгоритмами (самое долгое)
    compressed_blocks_array = []
    for element in blocks_array:
        compressed_blocks_array.append(MTF_compression(BWT_compression(element)))

    afterMTFString = ''
    for e in compressed_blocks_array:
        afterMTFString += e+'@'
    afterMTFString = afterMTFString.strip('@')
    
   
    compressed_string, table = haffman_compression(afterMTFString.strip('@'))
    
    
    #Преобразование битов в байты
    bit_array = []
    for i in range (0,(len(compressed_string)//8)):
        bit_array.append(compressed_string[i*8:(i+1)*8])
        
   #Сохранение остатка
    ost = compressed_string[(len(compressed_string)//8)*8:]
    ost+='0'*(8-len(ost))
    bit_array.append(ost)
    
    
    
   

    converted_byte_array = [int(eight_bits,2) for eight_bits in bit_array]
    
    #Сохранение сжатого файла
    import os.path
    
    f = open(exitPath+'/'+os.path.splitext(path)[0].split('/')[-1]+'.vld', 'wb')

    for byte in converted_byte_array:
        f.write(byte.to_bytes(1,'big')) # преобразование int в byte (1 байт на символ - utf8)
    
    import json
    stringTable = 'table'+json.dumps(table)+'table'+str(len(compressed_string))+'table'+os.path.splitext(path)[1]
    for byte in stringTable.encode():
        f.write(byte.to_bytes(1,'big'))

    f.close()
    date = datetime.datetime.now()-date
    return (1-((len(converted_byte_array)+len(stringTable))/len(fd)))*100, date


# In[8]:


packaging("G:/Мой диск/БИСТ-17-1/3 курс/6 семестр/Технологии обработки информации/Кодирование/Звуки гонок Формула-1.mp3","G:/Мой диск/БИСТ-17-1/3 курс/6 семестр/Технологии обработки информации/Кодирование")


# In[86]:


def anti_haffman(string,table):
    uncompressed_symbols = ''
    bitCode = ''
    
    for char in string:
        bitCode += char
        for key, value in table.items():
            if value == bitCode: #We found our symbol
                uncompressed_symbols += key
                bitCode = ''
    return uncompressed_symbols.strip('%')

def BWT_decompression(string):
    list_of_strings = []
    #init
    for i in range(len(string)):
        list_of_strings.append('')
    
    #Getting table
    for i in range(0,len(string)):
        for j in range(0,len(string)):
            list_of_strings[j] = string[j]+list_of_strings[j]
        list_of_strings.sort()
        
    #finding source string
    for element in list_of_strings:
        if element[-1] == '^':
            return element.strip('^')
    
    return ''

def MTF_decompression(text):
    letters = ['0','1','2','3','4','5','6','7','8','9','^',',']
    
    decomp_string = ''
    
    for char in text:
        mtf = 0
        if char == 'A':
            mtf = 10
        elif char == 'B':
            mtf = 11
        else:
            mtf = int(char)
        decomp_string += letters[mtf]
        letters = letters[mtf:]+letters[:mtf] # сдвигаем массив
    return decomp_string

def unpackaging(path, exitPath):
    import datetime
    date = datetime.datetime.now()
    
    f = open(path,"rb")
    text = f.read()


    #Get Text and haffman table
    text_parts = text.split(b'table')

    #Get array of int bytes
    compTextBytes = [int(char) for char in text_parts[0]]
   
    import json
    haffmanTable = json.loads(text_parts[1].decode())

    haffmanString = ''
    for byte in compTextBytes:
        haffmanString += format(byte, '08b')

    haffmanLength = int(text_parts[2].decode())
    haffmanString = haffmanString[0:haffmanLength]
    
    #Unpack haffman
    unHaffmanString = anti_haffman(haffmanString,haffmanTable)
    
    #Get blocks
    blocks_array = unHaffmanString.split('@')
    
    
    #Разжатие алгоритмами (самое долгое)
    uncompressed_blocks_array = []
    for element in blocks_array:
        uncompressed_blocks_array.append(BWT_decompression(MTF_decompression(element)))
        print(datetime.datetime.now()-date)
 
    #Получение массива байтов
    bytes_str_array = []
    for block in uncompressed_blocks_array:
        bytes_str_array.extend(block.split(','))
        
        
    bytes_array = []
    for char in bytes_str_array:
        if char != '':
            bytes_array.append(int(char))
        
    
    #Сохранение разжатого файла
    f = open(exitPath+'/'+path.split('/')[-1].split('.')[0]+text_parts[3].decode(), 'wb')

    for byte in bytes_array:
        f.write(byte.to_bytes(1,'big')) # преобразование int в byte (1 байт на символ - utf8)
    
    f.close()
    date = datetime.datetime.now()-date
    return len(bytes_array), date


# In[87]:


unpackaging("G:/Мой диск/БИСТ-17-1/3 курс/6 семестр/Технологии обработки информации/Кодирование/1.vld","G:/Мой диск/БИСТ-17-1/3 курс/6 семестр/Технологии обработки информации")


# In[ ]:




