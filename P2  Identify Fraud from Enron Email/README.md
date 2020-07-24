# 从安然邮件和财务数据识别欺诈

**Goose Huang**

**我在此确认，所提交的项目为我的工作成果，其中引用的信息出自网站、书籍、论坛、博客文章和 GitHub 代码库等。**


##项目概览

我们将在这个项目中使用一个真正混乱的数据，来训练我们的 **数据清洗** 和 **数据可视化** 能力。我们的任务是清理和可视化数据，查找各种特征之间的关联并识别极端异常值，最后使用 **机器学习算法** 来预测 **欺诈嫌疑人'POI'**。

安然曾是2000年美国最大的公司之一。2002年，由于其存在大量的企业欺诈行为，这个昔日的大集团土崩瓦解。 在随后联邦进行的调查过程中，大量有代表性的保密信息进入了公众的视线，包括成千上万涉及高管的邮件和详细的财务数据。 在此项目中我们将扮演侦探，运用学到的新技能，根据安然丑闻中公开的财务和邮件数据来构建相关人士识别符。数据与手动整理出来的欺诈案涉案人员列表进行了合并， 这意味着被起诉的人员要么达成和解，要么向政府签署认罪协议，再或者出庭作证以获得免受起诉的豁免权。

##1. 数据集和极端异常值

该数据集共包含 **146个数据点** ， **20个可用特征** 和**1个POI识别符**， **18欺诈嫌疑人** 和 **128个非欺诈嫌疑人**。

在进行探索性数据分析后， 我们发现了3条记录需要删除:

* ```TOTAL```: 所有数值数据的加和，不应该包含在数据集中。
* ```THE TRAVEL AGENCY IN THE PARK```: 非公司相关人员。
* ```LOCKHART EUGENE E```: 该点没有任何数据。


去除异常值之前的数据:

![avatar](/image/outliers.png)

去除异常值之后的数据: 

![avatar](/image/outliers_removed.png) 

详见data.excel

##2. 特征选择和变换
除了原本的 **20个特征** （另外一个是POI识别符），我使用已有特征额外生成了 **2个特征** 来尝试获得更好的结果。 

* ```fraction_poi_communication```: 往来邮件中发往和来自POI的比例。
* ```total_wealth```: total payment，total stock value的加和，能够近似的反映个人财产的数量。

使用```SelectKBest```函数找到的10个最佳特征：

| Features                     | Scores   |
| ---------------------------- |:--------:| 
| exercised_stock_options      |   24.815 | 
| total_stock_value            |   24.182 |
| bonus                        |   20.792 |
| salary                       |   18.289 |
| total_wealth                 |   17.808 |
| deferred_income              |   11.458 |
| long_term_incentive          |   9.922  |
| restricted_stock             |   9.212  |
| total_payments               |   8.772  |
| shared_receipt_with_poi      |   8.589  |


我们可以发现，新生成的特征 **Total Wealth** 也出现在最好的10个特征中，我将在算法中也使用这一变量。

**特征缩放:** 该步骤将标准化所有特征，执行标准化是许多机器学习必要的前提步骤，否则，算法可能会失效，我将使用 Scikit-learn中的 ```StandardScaler()``` 函数对特征进行缩放。

##3. 参数调试
我将尝试一系列的参数，并测试它们在各算法中的表现，来找出最佳的参数组合，可以大大的提高算法表现。
对于每个算法，我首先使用```Pipeline``` 进行数据预处理，然后使用 ```GridSearchCV``` 和 ```StratifiedShuffleSplit```进行交叉验证和测试每一种组合。
各项步骤的含义如下：
**PCA** 用来将特征转化为主成分(**PCs**)，来作为新的特征。第一个特征值取自数据集高维上最大化方差（最小化信息损失）的那个方向。 PCA可以大大的降低数据的维度，找到潜变量，使用更少的变量做出更好的预测成为可能。成分的个数最多可以是输入变量的个数， scikit-learn中 ```n_components``` 用来指定获得的```PCA()```个数。

以下是被用来调试算法的参数:

* Select K Best (```SeleckKBest```) : ```k```
* Principal Components Analysis (```PCA```) : ```n_components```, ```whiten```
* Gaussian Naive Bayes (```GaussianNB```) : None
* Logistic Regression (```LogisticRegression```) : ```C```, ```tol```, ```penalty```,  ```random_state```
* Support Vector Classifier(```SVC```) : ```C```, ```gamma```, ```kernel```
* Decision Tree(```DecisionTreeClassifier```) : ```min_samples_split```, ```min_samples_leaf```, ```criterion```, ```max_depth```, ```random_state```.
* Random Forest (```RandomForestClassifier```) : ```n_estimators```, ```max_depth```, ```random_state```
* Ada Boost (```AdaBoostClassifier```) : ```n_estimators```, ```algorithm```, ```learning_rate```

##4. 验证（Validatiion）
验证（Validation）是检验算法效果，防止过拟合的过程。 过拟合（Overfitting）指的是算法在训练集上表现良好，但在测试集(或者没有见过的）数据集上表现很糟糕。具体的，验证可以用在决策树的剪枝。因此，将数据及分割成测试集和训练集以便在不同的数据集上测试和训练非常重要。
在Scikit-Learn中，我门可以使用```StratifiedShuffleSplit```来产生训练集和测试集。该算法会将数据集有放回的重复抽样获得K份不同的子集（folds）。在本次测试中，我将它们分割成了**100 folds**，意思是按照测试集和训练集三七分的规则，随机分配100次原始数据。这样，我们就能避免偶然的一次训练带来的意外误差。



##5. 算法选取
我使用```scikit-learn```总共尝试了6个不同的算法，并利用 ```GridSearchCV``` 找到了每个算法的最佳参数。
以下是每个算法的最佳参数：

###朴素贝叶斯（Gaussian Naive Bayes）

```python
clf = GaussianNB()
```

###逻辑回归（Logistic Regression）

```python
number_of_best_features = 9

    clf_lr = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=7, whiten=False)),
        ('classifier', LogisticRegression(tol=0.01, C=1e-08, penalty='l2', random_state=42))])

```

###支持向量积（Support Vector Machine）

```python
number_of_best_features = 9

    clf_svc = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=5, whiten=True)),
        ('classifier', SVC(C=1000, gamma=.001, kernel='rbf'))])

```

###决策树（Decision Tree）

```python
number_of_best_features = 9


    clf_dt = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('pca', PCA(n_components=5, whiten=True)),
        ('classifier', DecisionTreeClassifier(criterion='gini',
                                              min_samples_leaf=2,
                                              min_samples_split=2,
                                              random_state=42,
                                              max_depth=None))
    ])                                 
```
 
###随机森林（Random Forest）

```python
number_of_best_features = 10
    clf_rf = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier(max_depth=None,
                                              n_estimators=15,
                                              random_state=46))
    ])
```

###自适应增强（Ada Boost）

```python
number_of_best_features = 10

    clf_ab = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('classifier', AdaBoostClassifier(learning_rate=0.8,
                                          n_estimators=40,
                                          algorithm='SAMME.R'))
    ])
```

在使用 **随机森林（Random Forest）** 和 **自适应增强（Ada Boost）** 算法的时候，加上PCA使算法表现不好（这些算法本身就能够适应很高的维度），因此去除了该过程。
在所有的算法中， **逻辑回归（Logistic Regression）** 表现最佳，以下是评估指标。


##6. 评估指标（Evaluation Metrics）

我使用了 **Precision**， **Recall** 和 **F1-score**来判断算法的好坏。我们舍弃了 **Accuracy** 指标，因为在原始数据中，非POI的数量要远远大于POI的数量， **Accuracy** 指标值结果会比较高，但并不额外反映多少信息，而且信息会被混合在一起（一个10%为Positive的数据集，我全部猜Negative也会有90%的精确度）。

以上这些指标反映了预测值和实际值之间的差异，具体的意义如下。

* True Positive (TP) :  该项实际是Positive，并被成功预测为Positive。
* True Negative (TN) :  该项实际是negative，并被成功预测为negative。
* False Positive (FP) : 该项实际是negative，但被错误预测为positive。
* False Negative (FN) : 该项实际是positive，但被成功预测为negative。


**精准度（Precision）：** 在所有被预测为Positive的值中，其真正是Positive的比例. 计算方法为```(TP)/(TP + FP)```。越高的精度（precision）意味着被算法判断为POI的人员越有可能真的是POI. 

**查出率（Recall）：**，在所有真是Positive的值中，有多少比例被算法判定为Positive 。计算方法为```(TP)/(TP + FN)```. 越高的查出率（recall）意味着如果一个人真的是POI，他越有可能被揪出来（整体上，罪犯逃脱的概率更小）。

**F1-分数（F1-score）：**精准度和查出率的调和平均值。计算方法是```(2*recall*precision)/(recall + precision)```.当数值为1时最好，数值为0时最差。

每个算法的精准对（precision），查出率（recall）和F1-分数(f1-score）如下：


| Algorithm                     | Precision   | Recall    | F1-score  | 
| ----------------------------- |:-----------:| :--------:| :--------:|
| Logistic Regression           | 0.457       | 0.456     | 0.456     |
| Gaussian Naive Bayes          | 0.400       | 0.345     | 0.371     |
| Random Forest 			    | 0.413       | 0.196     | 0.265     |
| Ada Boost      				| 0.301       | 0.230     | 0.261     |
| Decision Tree  				| 0.193       | 0.147     | 0.167     |
| Support Vector Machine        | 0.458       | 0.080     | 0.136     | 


因此，本例中**逻辑回归（Logisitic Regression）**在各项指标上都是最好的算法，其次（综合三种指标来看）是**朴素贝叶斯（Gaussian NB)** ，**随机森林（Random Forest）** ，**自适应增强（AdaBoost）** ，**决策树（Decision Tree）** 和 **支持向量积（Support Vector）** 。
针对效果最好的 **逻辑回归（logistic Regreession** ，我们能达到最高45.7%的精准度，意味着我们判定为嫌疑人的人中（共18个，占总体的12%），有45.7%的可能性真的是POI（误伤了9个）；召回率是45.6%，意味着所有POI中，我们找出了45.6%的人（大概9个），还有一半的人没有揪出来（放过了9个）整体上感觉这个算法能帮我们在大量的数据中快速找出嫌疑人，但是具体的我们有一般的几率会找错，误伤的人占总体的比例为6%，逃脱的人也为6%，并不是很累理想。综上，在实际使用中，我们可能还需要结合线下许多手段来完善。

**参考资料**

Dict写入csv:
https://blog.csdn.net/pfm685757/article/details/47806469

SelectKBest: 	
http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html

GridSearch
http://scikit-learn.org/stable/modules/grid_search.html  


适合入门的8个趣味机器学习项目:
http://imgtec.eetrend.com/blog/10545             
                                       

机器学习之安然数据集
https://github.com/supernova16/DAND-P5-Machine-Learning


安然欺诈案， 机器学习
https://github.com/yijigao/Enron_project       
                                              
                                              
                                              
                                              
                                              
                                              
                                            

