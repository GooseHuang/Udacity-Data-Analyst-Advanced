#!/usr/bin/python
# coding=utf-8
# coding=utf-8

import sys
import pickle
sys.path.append("../tools/")


#对数据进行预处理并去除异常值
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
import enron
import tester

#特征选择和预处理方法
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


#需要用到的分类算法
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier



### Task 1: Select what features you'll use.

#这是安然数据集中的所有可以数值化的特征，供19个，之后我将选择其中比较好的特征

features_list = ['poi',
                 'bonus',
                 'deferral_payments',
                 'deferred_income',
                 'director_fees',
                 'exercised_stock_options',
                 'expenses',
                 'loan_advances',
                 'long_term_incentive',
                 'other',
                 'restricted_stock',
                 'restricted_stock_deferred',
                 'salary',
                 'total_payments',
                 'total_stock_value',
                 'from_messages',
                 'from_poi_to_this_person',
                 'from_this_person_to_poi',
                 'shared_receipt_with_poi',
                 'to_messages']



### Load the dictionary containing the dataset
data_dict = pickle.load(open("../data/final_project_dataset.pkl", "r"))


### Task 2: Remove outliers
#通过检查导出的csv文件发现了3个异常值
enron.convert_to_csv(data_dict)
#TOTAL 是总计       LOCKHAET EUGENU E 所有的值为空          THE TRAVEL AGENCY 非安然职员
outliers = ['TOTAL', 'LOCKHART EUGENE E', 'THE TRAVEL AGENCY IN THE PARK']
enron.remove_outliers(data_dict, outliers)


### Task 3: Create new feature(s)
#这里创造了两个变量 fraction_poi_communication    收发邮件中与嫌疑人相关邮件占比
#                  total_wealth                 财富总和
#课程中使用了fraction_poi_communication，这里是我们已知了他和嫌疑人的信的比例，
# 但针对真实的情况，面对一个新人，我们可能不知道全部的嫌疑人都有哪些。这一点在实际使用中
#可能会受到限制。

enron.fraction_poi_communication(data_dict)
enron.total_wealth(data_dict)

features_list += ['fraction_poi_communication', 'total_wealth']

###备份数据集
my_dataset = data_dict


# 使用SelectKBest()获取前十个最好的特征.
best_features_list  = enron.get_k_best(my_dataset,features_list,10)
# 选择依据是f_classif
for item in best_features_list:
    print item

"""  
从高到低特征排序
exercised_stock_options 24.8150797332
total_stock_value 24.1828986786
bonus 20.7922520472
salary 18.2896840434
total_wealth 17.8087911742
deferred_income 11.4584765793
long_term_incentive 9.92218601319
restricted_stock 9.21281062198
total_payments 8.77277773009
shared_receipt_with_poi 8.58942073168

            
最终选取的特征如下(未排序)：
['poi',
 'salary',
 'total_payments',
 'bonus',
 'total_wealth',
 'shared_receipt_with_poi',
 'exercised_stock_options',
 'total_stock_value',
 'deferred_income',
 'restricted_stock',
 'long_term_incentive']   
 
 在后面的额调整中，每种算法会选取不同的特征
"""


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys=True)
labels, features = targetFeatureSplit(data)


### Task 4: Tune and try a variety of classifiers
#这里将测试逻辑回归、SCV、决策树、随机森林和ada_boost(自适应增强）这几种算法。
#我们将测试其中各种参数

def tune_logistic_regression():

    skb = SelectKBest()
    pca = PCA()
    lr_clf = LogisticRegression()

    #SKB是标签   SKB__k     k被传递给SKB中的k属性
    pipe_lr = Pipeline(steps=[("SKB", skb), ("PCA", pca), ("LogisticRegression", lr_clf)])


    lr_k = {"SKB__k": range(8, 10)}
    lr_params = {'LogisticRegression__C': [1e-08, 1e-07, 1e-06],
                 'LogisticRegression__tol': [1e-2, 1e-3, 1e-4],
                 'LogisticRegression__penalty': ['l1', 'l2'],
                 'LogisticRegression__random_state': [42, 46, 60]}
    #尝试不同的特征数和白化
    lr_pca = {"PCA__n_components": range(3, 8), "PCA__whiten": [True, False]}

    #将参数合并
    lr_k.update(lr_params)
    lr_k.update(lr_pca)

    enron.get_best_parameters_reports(pipe_lr, lr_k, features, labels)


def tune_svc():

    skb = SelectKBest()
    pca = PCA()
    svc_clf = SVC()

    pipe_svc = Pipeline(steps=[("SKB", skb), ("PCA", pca), ("SVC", svc_clf)])

    svc_k = {"SKB__k": range(8, 10)}
    svc_params = {'SVC__C': [1000], 'SVC__gamma': [0.001], 'SVC__kernel': ['rbf']}
    svc_pca = {"PCA__n_components": range(3, 8), "PCA__whiten": [True, False]}

    svc_k.update(svc_params)
    svc_k.update(svc_pca)

    enron.get_best_parameters_reports(pipe_svc, svc_k, features, labels)


def tune_decision_tree():

    skb = SelectKBest()
    pca = PCA()
    dt_clf = DecisionTreeClassifier()

    pipe_dt = Pipeline(steps=[("SKB", skb), ("PCA", pca), ("DecisionTreeClassifier", dt_clf)])

    dt_k = {"SKB__k": range(8, 10)}
    dt_params = {"DecisionTreeClassifier__min_samples_leaf": [2, 6, 10, 12],
                 "DecisionTreeClassifier__min_samples_split": [2, 6, 10, 12],
                 "DecisionTreeClassifier__criterion": ["entropy", "gini"],
                 "DecisionTreeClassifier__max_depth": [None, 5],
                 "DecisionTreeClassifier__random_state": [42, 46, 60]}
    dt_pca = {"PCA__n_components": range(4, 7), "PCA__whiten": [True, False]}

    dt_k.update(dt_params)
    dt_k.update(dt_pca)

    enron.get_best_parameters_reports(pipe_dt, dt_k, features, labels)


def tune_random_forest():

    skb = SelectKBest()
    rf_clf = RandomForestClassifier()

    pipe_rf = Pipeline(steps=[("SKB", skb), ("RandomForestClassifier", rf_clf)])

    rf_k = {"SKB__k": range(8, 11)}
    rf_params = {'RandomForestClassifier__max_depth': [None, 5, 10],
                  'RandomForestClassifier__n_estimators': [10, 15, 20, 25],
                  'RandomForestClassifier__random_state': [42, 46, 60]}
    rf_k.update(rf_params)

    #效果不好，予以去除
    #rf_pca = {"PCA__n_components": range(4, 7), "PCA__whiten": [True, False]}
    #rf_k.update(rf_pca)


    enron.get_best_parameters_reports(pipe_rf, rf_k, features, labels)


def tune_ada_boost():

    skb = SelectKBest()
    ab_clf = AdaBoostClassifier()

    pipe_ab = Pipeline(steps=[("SKB", skb), ("AdaBoostClassifier", ab_clf)])

    ab_k = {"SKB__k": range(8, 11)}
    ab_params = {'AdaBoostClassifier__n_estimators': [10, 20, 30, 40],
                 'AdaBoostClassifier__algorithm': ['SAMME', 'SAMME.R'],
                 'AdaBoostClassifier__learning_rate': [.8, 1, 1.2, 1.5]}

    #效果不好，予以去除
    #ab_pca = {"PCA__n_components": range(4, 7), "PCA__whiten": [True, False]}
    #ab_k.update(ab_pca)

    ab_k.update(ab_params)

    enron.get_best_parameters_reports(pipe_ab, ab_k, features, labels)


if __name__ == '__main__':

    '''         GAUSSIAN NAIVE BAYES            '''

    #设置需要使用的分类器
    clf = GaussianNB()
    #CrossValidation进行测试
    print "Gaussian Naive Bayes : \n", tester.test_classifier(clf, my_dataset, best_features_list)

    """
    Gaussian Naive Bayes : 
    GaussianNB(priors=None)
        Accuracy: 0.84380	Precision: 0.40058	Recall: 0.34550	F1: 0.37101	F2: 0.35527
        Total predictions: 15000	True positives:  691	False positives: 1034	False negatives: 1309	True negatives: 11966
    
    None
        
    """





    '''         LOGISTIC REGRESSION             '''

    #使用tune获取每个算法的最佳参数

    #tune_logistic_regression()

    """
    获取的最佳参数为：
    Best parameters set:
	LogisticRegression__C: 1e-08
	LogisticRegression__penalty: 'l2'
	LogisticRegression__random_state: 42
	LogisticRegression__tol: 0.01
	PCA__n_components: 7
	PCA__whiten: False
	SKB__k: 9
	
	Best score: 0.292

    """

    #按照上面得到的最佳参数来设置
    best_features_list_lr = enron.get_k_best(my_dataset, features_list, 9)

    clf_lr = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=7, whiten=False)),
        ('classifier', LogisticRegression(tol=0.01, C=1e-08, penalty='l2', random_state=42))])

    print "Logistic Regression : \n", tester.test_classifier(clf_lr, my_dataset, best_features_list_lr)

    """
    运行结果：
        Logistic Regression : 
    Pipeline(memory=None,
         steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('pca', PCA(copy=True, iterated_power='auto', n_components=7, random_state=None,
      svd_solver='auto', tol=0.0, whiten=False)), ('classifier', LogisticRegression(C=1e-08, class_weight=None, dual=False, fit_intercept=True,
              intercept_scaling=1, max_iter=100, multi_class='ovr', n_jobs=1,
              penalty='l2', random_state=42, solver='liblinear', tol=0.01,
              verbose=0, warm_start=False))])
        Accuracy: 0.85527	Precision: 0.45719	Recall: 0.45650	F1: 0.45684	F2: 0.45664
        Total predictions: 15000	True positives:  913	False positives: 1084	False negatives: 1087	True negatives: 11916
    None

    
    """



    '''         SUPPORT VECTOR CLASSIFIER           '''

    #获取最佳参数
    #tune_svc()
    """：
    Best score: 0.103
    Best parameters set:
	PCA__n_components: 5
	PCA__whiten: True
	SKB__k: 9
	SVC__C: 1000
	SVC__gamma: 0.001
	SVC__kernel: 'rbf'
    
    """

    # 按照上面得到的最佳参数来设置
    best_features_list_svc = enron.get_k_best(my_dataset, features_list, 9)

    clf_svc = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=5, whiten=True)),
        ('classifier', SVC(C=1000, gamma=.001, kernel='rbf'))])

    print "Support Vector Classifier : \n", tester.test_classifier(clf_svc, my_dataset, best_features_list_svc)

    """
    运行结果：
    Support Vector Classifier : 
    Pipeline(memory=None,
         steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('pca', PCA(copy=True, iterated_power='auto', n_components=5, random_state=None,
      svd_solver='auto', tol=0.0, whiten=True)), ('classifier', SVC(C=1000, cache_size=200, class_weight=None, coef0=0.0,
      decision_function_shape='ovr', degree=3, gamma=0.001, kernel='rbf',
      max_iter=-1, probability=False, random_state=None, shrinking=True,
      tol=0.001, verbose=False))])
        Accuracy: 0.86473	Precision: 0.45869	Recall: 0.08050	F1: 0.13696	F2: 0.09640
        Total predictions: 15000	True positives:  161	False positives:  190	False negatives: 1839	True negatives: 12810
    
    None
    """



    '''         DECISION TREE CLASSIFIER            '''

    #tune_decision_tree()

    """
    Best score: 0.255
    Best parameters set:
        DecisionTreeClassifier__criterion: 'gini'
        DecisionTreeClassifier__max_depth: None
        DecisionTreeClassifier__min_samples_leaf: 2
        DecisionTreeClassifier__min_samples_split: 2
        DecisionTreeClassifier__random_state: 42
        PCA__n_components: 5
        PCA__whiten: True
        SKB__k: 9

    """

    # 按照上面得到的最佳参数来设置
    best_features_list_dt = enron.get_k_best(my_dataset, features_list, 9)

    clf_dt = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=5, whiten=True)),
        ('classifier', DecisionTreeClassifier(criterion='gini',
                                              min_samples_leaf=2,
                                              min_samples_split=2,
                                              random_state=42,
                                              max_depth=None))
    ])

    print "Decision Tree Classifier : \n",tester.test_classifier(clf_dt, my_dataset, best_features_list_dt)

    """
    运行结果：
    Decision Tree Classifier : 
    Pipeline(memory=None,
         steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('pca', PCA(copy=True, iterated_power='auto', n_components=5, random_state=None,
      svd_solver='auto', tol=0.0, whiten=True)), ('classifier', DecisionTreeClassifier(class_weight=None, criterion='gini', max_depth=None,
          ...        min_weight_fraction_leaf=0.0, presort=False, random_state=42,
                splitter='best'))])
        Accuracy: 0.80440	Precision: 0.19357	Recall: 0.14750	F1: 0.16742	F2: 0.15487
        Total predictions: 15000	True positives:  295	False positives: 1229	False negatives: 1705	True negatives: 11771
    
    None
    """



    '''         RANDOM FOREST CLASSIFIER              '''

    #寻找最优参数
    tune_random_forest()

    """
    Best score: 0.166
    Best parameters set:
        RandomForestClassifier__max_depth: None
        RandomForestClassifier__n_estimators: 15
        RandomForestClassifier__random_state: 46
        SKB__k: 10
    """

    # 按照上面得到的最佳参数来设置
    best_features_list_rf = enron.get_k_best(my_dataset, features_list, 10)

    clf_rf = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(max_depth=None,
                                              n_estimators=15,
                                              random_state=46))
    ])

    print "Random Forest Classifier : \n", tester.test_classifier(clf_rf, my_dataset, best_features_list_rf)

    """
    运行结果：
    Random Forest Classifier : 
    Pipeline(memory=None,
         steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('classifier', RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini',
                max_depth=None, max_features='auto', max_leaf_nodes=None,
                min_impurity_decrease=0.0, min_impurity_split=None,
                min_samples_leaf=1, min_samples_split=2,
                min_weight_fraction_leaf=0.0, n_estimators=15, n_jobs=1,
                oob_score=False, random_state=46, verbose=0, warm_start=False))])
        Accuracy: 0.85573	Precision: 0.41332	Recall: 0.19550	F1: 0.26544	F2: 0.21853
        Total predictions: 15000	True positives:  391	False positives:  555	False negatives: 1609	True negatives: 12445
    
    None
    """




    '''         ADA BOOST CLASSIFIER            '''

    #tune_ada_boost()


    """
    Best score: 0.324
    Best parameters set:
        AdaBoostClassifier__algorithm: 'SAMME.R'
        AdaBoostClassifier__learning_rate: 0.8
        AdaBoostClassifier__n_estimators: 40
        SKB__k: 10
    """

    # 按照上面得到的最佳参数来设置
    best_features_list_ab = enron.get_k_best(my_dataset, features_list, 10)

    clf_ab = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', AdaBoostClassifier(learning_rate=0.8,
                                          n_estimators=40,
                                          algorithm='SAMME.R'))
    ])

    print "Ada Boost Classifier : \n", tester.test_classifier(clf_ab, my_dataset, best_features_list_ab)

    """
    运行结果：
    Ada Boost Classifier : 
    Pipeline(memory=None,
         steps=[('scaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('classifier', AdaBoostClassifier(algorithm='SAMME.R', base_estimator=None,
              learning_rate=0.8, n_estimators=40, random_state=None))])
        Accuracy: 0.82627	Precision: 0.30118	Recall: 0.22950	F1: 0.26050	F2: 0.24097
        Total predictions: 15000	True positives:  459	False positives: 1065	False negatives: 1541	True negatives: 11935
    
    None
    """

    #储存生成的数据文件
    #dump_classifier_and_data(clf_lr, my_dataset, best_features_list_lr)
