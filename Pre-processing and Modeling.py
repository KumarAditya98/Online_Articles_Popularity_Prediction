#%%
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import rfit
import os
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import plot_tree

sharedf = pd.read_csv('Dataset/OnlineNewsPopularity_Viz.csv')
print(sharedf.head())

# %%
print(len(sharedf))

#There are total 39644 rows in the entire dataset

# %%
sharedf=sharedf.drop_duplicates()
print(sharedf.isna().sum())

# Any duplicates values in the data set are removed, and there are no 
#null values the data set.

# %%
sharedf.describe()

#%%
sharedf = sharedf[sharedf['timedelta']>21]
#%%
# sharedf = sharedf[sharedf['n_tokens_title']!=0]

# %%
sharedf = sharedf[sharedf['n_tokens_content']!=0]

#The n_tokens_title and n_tokens_content columns which contains the 
# value 0 is removed

#%%
print(len(sharedf))
#After removing these 0 values, the length of the dataframe is 37906.
#1180 rows are removed and the dataset is stored.
 
#%%
print(sharedf['shares'].mean())
print(sharedf['shares'].median())

# The mean value of the shares is 3355.56, and the median value of the shares is 1400

# %%
#correlation between the columns
plt.figure(figsize=(42, 15))
heatmap = sns.heatmap(sharedf.corr(), vmin=-1, vmax=1, annot=True, cmap='BrBG')
heatmap.set_title('Correlation Heatmap', fontdict={'fontsize':18}, pad=12);


# Choosing 0.7 as the threshold, any correlation value greater than this will be removed.
#%%
sharedf = sharedf.drop('url',axis=1)

#%%
#From the collerations we can observe that n_non_stop_words, n_non_stop_unique_tokens, kw_avg_min has high correlations, we are dropping these columns. Along with these, the following columns are also dropped because of high correlation.
# If n columns were highly correlated, only n-1 columns are dropped 

sharedf= sharedf.drop(["n_non_stop_unique_tokens","n_non_stop_words","kw_avg_min",'self_reference_max_shares', 'self_reference_min_shares','kw_avg_avg', 'LDA_00','LDA_02', 'LDA_04', 'is_weekend', 'rate_positive_words', 'rate_negative_words', 'min_negative_polarity',"title_subjectivity" ,'timedelta'],axis=1)

# %%
print(sharedf.head())

#%%
# Outlier Handling, to clean the dataset.
# %%
num_cols = sharedf.select_dtypes(['int64','float64']).columns

for column in num_cols:    
    q1 = sharedf[column].quantile(0.25)    # First Quartile
    q3 = sharedf[column].quantile(0.75)    # Third Quartile
    IQR = q3 - q1                            # Inter Quartile Range

    llimit = q1 - 1.5*IQR                       # Lower Limit
    ulimit = q3 + 1.5*IQR                        # Upper Limit

    outliers = sharedf[(sharedf[column] < llimit) | (sharedf[column] > ulimit)]
    print('Number of outliers in "' + column + '" : ' + str(len(outliers)))
    print(llimit)
    print(ulimit)
    print(IQR)

# Test
# %%
#Treating outlier :  

# %%
from numpy import percentile
#num_cols = sharedf.select_dtypes(['int64','float64']).columns
cols = list(sharedf.columns)
l = ['data_channel_is_lifestyle','data_channel_is_entertainment','data_channel_is_bus','data_channel_is_socmed','data_channel_is_tech','data_channel_is_world','weekday_is_monday','weekday_is_tuesday','weekday_is_wednesday','weekday_is_thursday','weekday_is_friday','weekday_is_saturday','weekday_is_sunday','LDA_01','LDA_03','shares','target','Data_Channel','Publish_DOW']
for i in l:
    cols.remove(i)

# This removal operation is performed to retain only float type of values whose outliers are to be treated. 
#%%
for i in cols:
    
    Q1 = sharedf[i].quantile(0.25)
    Q2 = sharedf[i].quantile(0.75)
    iqr = Q2-Q1
    lower_band = Q1 - 1.5*iqr
    upper_band = Q2 + 1.5*iqr
    sharedf[i] = sharedf[i].clip(lower = lower_band, upper = upper_band)

#%%
for column in cols:    
    q1 = sharedf[column].quantile(0.25)    # First Quartile
    q3 = sharedf[column].quantile(0.75)    # Third Quartile
    IQR = q3 - q1                            # Inter Quartile Range

    llimit = q1 - 1.5*IQR                       # Lower Limit
    ulimit = q3 + 1.5*IQR                        # Upper Limit

    outliers = sharedf[(sharedf[column] < llimit) | (sharedf[column] > ulimit)]
    print('Number of outliers in "' + column + '" : ' + str(len(outliers)))
    print(llimit)
    print(ulimit)
    print(IQR)
    
#%%
# Looking at the distribution of all numerical variables to see if log transformation can be applied to right tailed ones.
sharedf1 = sharedf[cols]

sharedf1.hist(figsize=(20,20))
plt.show()

# Choosing not to apply log transformations. There are some negative features in the dataset. Standard encoder seems to work universally and preserves the distribution of the data whereas log transformations work only in few cases. 

#%%
## Modeling

# First we build a Logistic Regression using stats model using all the features available to us
import statsmodels.api as sm
from statsmodels.formula.api import glm
log_reg = glm(formula = "target ~ n_tokens_title+n_tokens_content+n_unique_tokens+num_hrefs+num_self_hrefs+num_imgs+num_videos+average_token_length+num_keywords+kw_min_min+kw_max_min+kw_min_max+kw_max_max+kw_avg_max+kw_min_avg+kw_max_avg+self_reference_avg_sharess+global_subjectivity+global_sentiment_polarity+global_rate_positive_words+global_rate_negative_words+avg_positive_polarity+min_positive_polarity+max_positive_polarity+avg_negative_polarity+max_negative_polarity+title_sentiment_polarity+abs_title_subjectivity+abs_title_sentiment_polarity+C(Publish_DOW)+C(Data_Channel)", data = sharedf, family=sm.families.Binomial()).fit()
print(log_reg.summary())

#%%
# Sorting the variables by their p-values
coefs = pd.DataFrame({
    'coef': log_reg.params.values,
    'odds ratio': np.exp(log_reg.params.values),
    'pvalue': log_reg.pvalues,
    'name': log_reg.params.index
}).sort_values(by='pvalue', ascending=False)
print(coefs)

#%% Running the stats model after removing non-significant predictors
log_reg1 = glm(formula = "target ~ n_unique_tokens+num_hrefs+num_self_hrefs+num_imgs+num_videos+average_token_length+num_keywords+kw_min_min+kw_max_min+kw_max_max+kw_min_avg+kw_max_avg+self_reference_avg_sharess+global_subjectivity+min_positive_polarity+max_negative_polarity+title_sentiment_polarity+abs_title_subjectivity+C(Publish_DOW)+C(Data_Channel)", data = sharedf, family=sm.families.Binomial()).fit()
print(log_reg1.summary())

# No improvement in R-squared or adjusted R-squared value 
# Since variables were removed, we didn't expect to see this improvement either.

# However, this tells us that we can build our models using lesser number of features as well, and we'll explain the same variability in response.

# However, since with p-values, we can only fail to reject the null hypothesis. This tells us that we don't have enough evidence in our dataset. 

# For the rest of the models, we'll include all the features that are avaialble to us after removing the correlated once.  

# %%
ctoc = pd.DataFrame(coefs[coefs['pvalue']<0.05].index)
print(ctoc)


# %%
## KNN Classification
pd.set_option('display.float_format', lambda x: '%.3f' % x)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score

X = sharedf.drop(['shares','target','Publish_DOW','Data_Channel'],axis=1)
y = sharedf['target']
X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.30, random_state=42)
scaler = StandardScaler()
Scaled_Xtrain = scaler.fit_transform(X_train)
Scaled_Xtest= scaler.transform(X_test)
knn_model = KNeighborsClassifier(n_neighbors=17)
knn_model.fit(Scaled_Xtrain,y_train)
y_pred = knn_model.predict(Scaled_Xtest)
accuracy_score(y_test,y_pred)
cf_matrix = confusion_matrix(y_test,y_pred)

print(classification_report(y_test,y_pred))
import seaborn as sns
sns.heatmap(cf_matrix, annot=True,cmap='Blues', fmt='g')
# %%
#Choosing K value
test_error_rates = []


for k in range(1,30):
    knn_model = KNeighborsClassifier(n_neighbors=k)
    knn_model.fit(Scaled_Xtrain,y_train) 
   
    y_pred_test = knn_model.predict(Scaled_Xtest)
    
    test_error = 1 - accuracy_score(y_test,y_pred_test)
    test_error_rates.append(test_error)
# %%
plt.figure(figsize=(10,6),dpi=200)
plt.plot(range(1,30),test_error_rates,label='Test Error')
plt.legend()
plt.ylabel('Error Rate')
plt.xlabel("K Value")

# We picked the ideal K value according to this error graph (17) and then re-ran the above code. Earlier K was an arbitrary value.

# %%
# Plotting the ROC for KNN
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
y_scores=knn_model.predict_proba(Scaled_Xtest)
fpr,tpr,threshold =roc_curve(y_test,y_scores[:,1])
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr,'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.title('ROC Curve of kNN')
plt.show()

# %%
# Running Logistic Regression again from the Sklearn library now. 
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report
from sklearn.metrics import plot_roc_curve
log_model = LogisticRegression()
log_model.fit(Scaled_Xtrain,y_train)
y_pred = log_model.predict(Scaled_Xtest)
accuracy_score(y_test,y_pred)
cf_matrix = confusion_matrix(y_test,y_pred)
sns.heatmap(cf_matrix, annot=True,cmap='Blues', fmt='g')
print(classification_report(y_test,y_pred))
plot_roc_curve(log_model,Scaled_Xtest,y_test)
#%%
importances = pd.DataFrame(data={
    'Attribute': X.columns,
    'Importance': log_model.coef_[0]
})
importances = importances.sort_values(by='Importance', ascending=False)
print(importances.head(100))

# Since our X_train and X_test are standard scaled, looking at this we'll identify which are the important features in predicting our target.

# %%
# Running the Decision Tree classificatier now
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import plot_tree

model = DecisionTreeClassifier(max_depth=5)
model.fit(Scaled_Xtrain,y_train)
base_pred = model.predict(Scaled_Xtest)
from sklearn.metrics import confusion_matrix,classification_report
cf_matrix = confusion_matrix(y_test,base_pred)
sns.heatmap(cf_matrix, annot=True,cmap='Blues', fmt='g')
print(classification_report(y_test,base_pred))
print(model.feature_importances_)
pd.DataFrame(index=X.columns,data=model.feature_importances_,columns=['Feature Importance'])
plt.figure(figsize=(12,8),dpi=200)
#%%
plt.figure(figsize = (20,20), dpi = 200)
plot_tree(model,filled=True,feature_names=X.columns)
# %%
dff = pd.DataFrame(index=X.columns,data=model.feature_importances_,columns=['Feature Importance']).sort_values('Feature Importance', ascending=False)
print(dff.head(17))

#%%
#ROC for decision tree
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
y_scores=model.predict_proba(Scaled_Xtest)
fpr,tpr,threshold =roc_curve(y_test,y_scores[:,1])
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr,'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.title('ROC Curve of Decision Tree')
plt.show()

#%%
#PRUNING 
#Pruned decision tree
pruned_tree_1 = DecisionTreeClassifier(max_depth=2)
pruned_tree_1.fit(Scaled_Xtrain,y_train)
print(classification_report(y_test,base_pred))
dff = pd.DataFrame(index=X.columns,data=pruned_tree_1.feature_importances_,columns=['Feature Importance']).sort_values('Feature Importance', ascending=False)
print(dff.head(17))
#%%
pruned_tree_2 = DecisionTreeClassifier(max_leaf_nodes=2)
pruned_tree_2.fit(Scaled_Xtrain,y_train)
print(classification_report(y_test,base_pred))
dff = pd.DataFrame(index=X.columns,data=pruned_tree_2.feature_importances_,columns=['Feature Importance']).sort_values('Feature Importance', ascending=False)
print(dff.head(17))
# %%
#Random Forest Classifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix,classification_report,accuracy_score

modelforrc = RandomForestClassifier(n_estimators=100,max_features='auto',random_state=101)
modelforrc.fit(Scaled_Xtrain,y_train)
preds = modelforrc.predict(Scaled_Xtest)
cff = confusion_matrix(y_test,preds)
sns.heatmap(cff, annot=True,cmap='Blues', fmt='g')
print(classification_report(y_test,preds))
#%%
#ROC for decision tree
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
y_scores=modelforrc.predict_proba(Scaled_Xtest)
fpr,tpr,threshold =roc_curve(y_test,y_scores[:,1])
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr,'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.title('ROC Curve of Random Forest')
plt.show()


#%%
#%%
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix,classification_report
svc = SVC(C= 1, class_weight='balanced',probability=True)
svc.fit(Scaled_Xtrain,y_train)
preds = svc.predict(Scaled_Xtest)
cff = confusion_matrix(y_test,preds)
sns.heatmap(cff, annot=True,cmap='Blues', fmt='g')
print(classification_report(y_test,preds))

#%%
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
y_scores=svc.predict_proba(Scaled_Xtest)
fpr,tpr,threshold =roc_curve(y_test,y_scores[:,1])
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr,'b', label = 'AUC = %0.2f' % roc_auc)
plt.legend(loc = 'lower right')
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.title('ROC Curve of svc')
plt.show()



##
# %%


