#!/usr/bin/python
# coding=utf-8
#包含去除异常值和特征选择的算法

import sys
import csv
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit

from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedShuffleSplit


#将字典转化为csv格式
def convert_to_csv(data_dict):
    with open('../data/data.csv', 'w') as csvfile:
        fieldnames = ['name'] + data_dict.itervalues().next().keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for value in data_dict:
            key = data_dict[value]
            key['name'] = value
            writer.writerow(key)

#按照index去除
def remove_outliers(data_dict, indices):
    for index in indices:
        data_dict.pop(index, 0)

#获取前k个最好的特征
def get_k_best(data_dict, features_list, k):

    data = featureFormat(data_dict, features_list)
    labels_train, features_train = targetFeatureSplit(data)

    #使用的是f_classif方法
    k_best = SelectKBest(f_classif, k=k)
    k_best.fit(features_train, labels_train)

    #按得分排序并生成字典
    unsorted_list = zip(features_list[1:], k_best.scores_)
    sorted_list = sorted(unsorted_list, key=lambda x: x[1], reverse=True)

    for (key,value) in sorted_list[:k]:
        print key , value

    k_best_features = dict(sorted_list[:k])

    return ['poi'] + k_best_features.keys()

#往来邮件中有多少是和嫌疑人相关的
def fraction_poi_communication(data_dict):
    features = ['to_messages', 'from_messages', 'from_this_person_to_poi', 'from_poi_to_this_person']

    for key in data_dict:
        name = data_dict[key]

        is_null = False
        for feature in features:
            if name[feature] == 'NaN':
                is_null = True

        if not is_null:
            #poi往来邮件的总和/收发邮件总数
            name['fraction_poi_communication'] = float(name['from_this_person_to_poi'] + name['from_poi_to_this_person']) /\
                                                 (name['to_messages'] + name['from_messages'])
        else:
            name['fraction_poi_communication'] = 'NaN'


def total_wealth(data_dict):

    #全部的财产 total_payments, total stock value
    features = ['total_payments', 'total_stock_value']

    for key in data_dict:
        name = data_dict[key]

        is_null = False
        for feature in features:
            if name[feature] == 'NaN':
                is_null = True

        if not is_null:
            name['total_wealth'] = name['total_payments'] + name['total_stock_value']
        else:
            name['total_wealth'] = 'NaN'


def get_best_parameters_reports(clf, parameters, features, labels):
    #使用GridSearch测试最佳参数

    #将测试集和训练集三七分
    features_train, features_test, labels_train, labels_test = \
        train_test_split(features, labels, test_size=0.3, random_state=42)

    #进行100次交叉验证
    cv = StratifiedShuffleSplit(labels_train, 100, test_size=0.2, random_state=42)

    #按照f1分数进行判断
    grid_search = GridSearchCV(clf, parameters, n_jobs=-1, cv=cv, scoring='f1')
    grid_search.fit(features_train, labels_train)


    print ('Best score: %0.3f' % grid_search.best_score_)
    print ('Best parameters set:')
    best_parameters_set = grid_search.best_estimator_.get_params()
    for param_name in sorted(parameters.keys()):
        print '\t%s: %r' % (param_name, best_parameters_set[param_name])

