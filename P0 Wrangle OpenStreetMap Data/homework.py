#homework


# =============================================================================
# 1.count tags
# =============================================================================
import xml.etree.cElementTree as ET
import pprint
import os
#切换到当前工作目录
DIR = os.getcwd()
os.chdir(DIR)

filename = 'wuhan_china.osm'

def count_tags(filename):
    tree = ET.iterparse(filename)
    child_dict = {}
    for event,child in tree:
        if not child.tag in child_dict.keys():
            child_dict[child.tag]=1
        else:
            child_dict[child.tag]+=1
    return child_dict

tags = count_tags(filename)
pprint.pprint(tags)


#内部的tag也访问到了
"""
{'bounds': 1,
 'member': 8994,
 'nd': 380786,
 'node': 322152,
 'osm': 1,
 'relation': 424,
 'tag': 92020,
 'way': 35018}
"""

# =============================================================================
# 2.check tag key
# =============================================================================
import re
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
                             
def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
            #print('lower:',element.attrib['k'])
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
            #print('lower_colon:',element.attrib['k'])
        elif problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
            #print('problemchars:',element.attrib['k'])
        else:
            keys['other'] +=1
            #print('other:',element.attrib['k'])
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

check_tag_keys = process_map(filename)

other_list =[]
for _,element in ET.iterparse(filename):
    #只有tag单元格才会有属性，每个tag会有一个属性
    if element.tag == "tag":
        if not (lower.search(element.attrib['k']) or
            lower_colon.search(element.attrib['k']) or
            problemchars.search(element.attrib['k'])):
            other_list.append(element.attrib['k'])

"""
 {'lower': 88745, 
 'lower_colon': 3175,
 'other': 100, 
 'problemchars': 0}

other 中大都是同时包含大小写或"-" "_" ":"符号的


"""

# =============================================================================
# 3. how many unique users
# =============================================================================
def get_user(users,element):
    if 'id' in element.attrib.keys():
        users.add( element.attrib['uid'])
    return users

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        get_user(users,element)
    return users


users = process_map(filename)
 
len(users)

"""
557
总共有557个用户贡献
"""

# =============================================================================
# 4. 审查街道名
# =============================================================================
#from collections import defaultdict
#
## UPDATE THIS VARIABLE
#"""
#路名说清楚就行了
#特殊需要修改的我直接在文件内部改好了，很好改
#"""
#   
#
#def audit_street_type(street_types, street_name):
#    m = street_type_re.search(street_name)
#    if m:
#        street_type = m.group()
#        if street_type not in expected:
#            street_types[street_type].add(street_name)
#
#
#def is_street_name(elem):
#    return (elem.attrib['k'] == "addr:street")
#
#
#def audit(osmfile):
#    osm_file = open(osmfile, "r",encoding='utf8')
#    #生成元素为集合的字典
#    street_types = defaultdict(set)
#    for event, elem in ET.iterparse(osm_file, events=("start",)):
#        
#        if elem.tag == "node" or elem.tag == "way":
#            for tag in elem.iter("tag"):
#                if is_street_name(tag):
#                    audit_street_type(street_types, tag.attrib['v'])
#    osm_file.close()
#    return street_types
#
#
#street_types = audit(filename)
#
#
#street_dict=dict()
#for key,value in street_types.items():
#    street_dict[key] = list(value)
#
#
#street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
#
#expected = ["Street","Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
#            "Trail", "Parkway", "Commons"]
#
#mapping = { "Rd" : "Road",
#            
#            #特殊替换处理,直接替换，没有空格，最后加上空格
#            "街":" Street",
#            "大道":" Avenue",
#            "路":" Road",
#            "广场":" Square",
#            "园":" Parkway",
#            "巷":" Lane"
#            }
#            
#
#
#def update_name(name, mapping):
#    for key,value in mapping.items():
#        if key in name:
#            name = name.replace(key,value)
#            return name
#
#
#
##更新名称
##单独处理这些例外情况，原先的不动
#st_types = audit(filename)
#pprint.pprint(dict(st_types))
#
#for st_type, ways in st_types.items():
#    for name in ways:
#        better_name = update_name(name, mapping)
#        print(name, "=>", better_name)
#
#
#
## =============================================================================
## 审查所有种类的tag 'k'
## =============================================================================
#osmfile = filename
#
#osm_file = open(osmfile, "r",encoding='utf8')
##生成元素集合
#k_types = set()
#for event, elem in ET.iterparse(osm_file, events=("start",)):
#    if elem.tag == "node" or elem.tag == "way":
#        for tag in elem.iter("tag"):
#            k_types.add(tag.attrib['k'])
#osm_file.close()
#
#k_types = list(k_types)
#
##生成元素字典并计数
#osm_file = open(osmfile, "r",encoding='utf8')
#k_types = dict()
#for event, elem in ET.iterparse(osm_file, events=("start",)):
#    if elem.tag == "node" or elem.tag == "way":
#        for tag in elem.iter("tag"):
#            if tag.attrib['k'] in k_types.keys():
#                k_types[tag.attrib['k']]+=1
#            else:
#                k_types[tag.attrib['k']] = 1
#osm_file.close()

# =============================================================================
# 5. 转换成csv文件，便于进一步清洗和上传至数据库
# =============================================================================

import os
os.chdir(r'C:\Users\Goose\Documents\Code')
filename = 'wuhan_china.osm'

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
import pandas as pd


OSM_PATH = filename

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

#同文件目录下的字典文件                             
SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street","Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]


# UPDATE THIS VARIABLE
mapping = { "Rd" : "Road",
            #特殊替换处理,直接替换，没有空格，最后加上空格
            "街":" Street",
            "大道":" Avenue",
            "路":" Road",
            "广场":" Square",
            "园":" Parkway",
            "巷":" Lane"
            }

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

#def update_name(name):
#    m = street_type_re.search(name)
#    if m:
#        street_type = m.group()
#        if street_type not in expected:
#            name = name.replace(street_type,mapping[street_type])
#    return name
    
def update_name(name, mapping):
    """
    直接替换掉不想要的文字
    """
    m = street_type_re.search(name)
    if m and (m.group() in expected):
        pass
    else:
        for key,value in mapping.items():
            if key in name:
                name = name.replace(key,value)
    return name

def load_new_tag(element, secondary, default_tag_type):
    """
    Load a new tag dict to go into the list of dicts for way_tags, node_tags
    主要处理的是次级tag中的内容，node和way都具有自己的tag，一个id下的多个tag合在一起构成了这个
    element的属性，储存在数据库中，每条属性是一条记录
    """
    new = {}
    #对应该次级tag所属的id
    new['id'] = element.attrib['id']
    
    #处理多种情况下次级tag的‘k’
    if ":" not in secondary.attrib['k']:
        new['key'] = secondary.attrib['k']
        new['type'] = default_tag_type
    else:
        post_colon = secondary.attrib['k'].index(":") + 1
        new['key'] = secondary.attrib['k'][post_colon:]
        new['type'] = secondary.attrib['k'][:post_colon - 1]
    

    # Cleaning and loading values of various keys
    
    # 处理次级tag的街道属性
    if is_street_name(secondary):
        street_name = update_name(secondary.attrib['v'],mapping)
        new['value'] = street_name
    else:
        new['value'] = secondary.attrib['v']
        
    # 这里可以再添加其他情况的处理
    
    return new


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict
        将元素转变为字典格式
    """

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements



    if element.tag == 'node':
        #不关心的栏目不要
        for attrib, value in element.attrib.items():
            if attrib in node_attr_fields:
                node_attribs[attrib] = value
        
        # For elements within the top element
        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    #问题属性被直接跳过了
                    continue
                else:
                    #处理tag属性，返回一个字典，包含id、key、type、value
                    new = load_new_tag(element, secondary,default_tag_type)
                    if new is not None:
                        tags.append(new)
                        
                 #node_attribs和way_attribs是一组字典，包含当前element的一级信息       
                 #tags是一个list，包含许多的字典，包含element的二级信息       
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for attrib, value in element.attrib.items():
            if attrib in way_attr_fields:
                way_attribs[attrib] = value

        counter = 0
        for secondary in element.iter():
            if secondary.tag == 'tag':
                if problem_chars.match(secondary.attrib['k']) is not None:
                    continue
                else:
                    new = load_new_tag(element, secondary, default_tag_type)
                    if new is not None:
                        tags.append(new)
            elif secondary.tag == 'nd':
                newnd = {}
                newnd['id'] = element.attrib['id']
                newnd['node_id'] = secondary.attrib['ref']
                newnd['position'] = counter
                counter += 1
                way_nodes.append(newnd)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
    
            
#按字典写入csv
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""
    ###
    #file_in = filename
    ###
    encoding = "utf8"
    
    with open(NODES_PATH, 'w',encoding=encoding) as nodes_file, \
         open(NODE_TAGS_PATH, 'w',encoding=encoding) as nodes_tags_file, \
         open(WAYS_PATH, 'w',encoding=encoding) as ways_file, \
         open(WAY_NODES_PATH, 'w',encoding=encoding) as way_nodes_file, \
         open(WAY_TAGS_PATH, 'w',encoding=encoding) as way_tags_file:    
            
        nodes_writer = csv.DictWriter(nodes_file, fieldnames=NODE_FIELDS )
        nodes_writer.writeheader()
        
        nodes_tags_writer = csv.DictWriter(nodes_tags_file, fieldnames=NODE_TAGS_FIELDS )
        nodes_tags_writer.writeheader()    
        
        ways_writer = csv.DictWriter(ways_file, fieldnames=WAY_FIELDS )
        ways_writer.writeheader()   
        
        ways_nodes_writer = csv.DictWriter(way_nodes_file, fieldnames=WAY_NODES_FIELDS)
        ways_nodes_writer.writeheader()  
        
        ways_tags_writer = csv.DictWriter(way_tags_file, fieldnames=WAY_TAGS_FIELDS )
        ways_tags_writer.writeheader()       
    


        for i,element in enumerate(get_element(file_in, tags=('node', 'way'))):
#            n = 10000
#            if i%n== 0 :
#                print(int(i/n))
            #tag装进字典里
            el = shape_element(element)      
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    for item in el['node_tags']:
                        nodes_tags_writer.writerow(item)
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    for item in el['way_nodes']:
                        ways_nodes_writer.writerow(item)
                    for item in el['way_tags']:
                        ways_tags_writer.writerow(item)


process_map(filename)


import toolkit as tk

df_nodes = tk.read_csv_in_str('nodes.csv',sep=',',encoding='utf8')

df_node_tags = tk.read_csv_in_str('nodes_tags.csv',sep=',',encoding='utf8')

df_ways = tk.read_csv_in_str('ways.csv',sep=',',encoding='utf8')

df_ways_nodes = tk.read_csv_in_str('ways_nodes.csv',sep=',',encoding='utf8')

df_ways_tags = tk.read_csv_in_str('ways_tags.csv',sep=',',encoding='utf8')























