import graphviz

from pickleshare import PickleShareDB
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from pandas import value_counts

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve, auc
import seaborn as sns
from sklearn.tree import export_graphviz
from transformation_data import df as data_columns, label_encoder
from transformation_data import X,y

#df = pd.read_csv('sample-data/insurance_claims1copy.csv')
# Calculate the correlation matrix
#corr_matrix = df.corr()
#plt.figure(figsize=(10,20))
# Visualize the correlation matrix using a heatmap
#sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
#plt.title("Correlation Matrix of  Dataset (before SMOTE)")

#df.drop(columns=["vehicle_claim"],axis=1)
#print(X.columns)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# create an instance of the Random Forest classifier
rf1= RandomForestClassifier(random_state=42)

# fit the model on the original dataset
rf1.fit(X_train, y_train)

# make predictions on the testing set
y_pred = rf1.predict(X_test)

# print classification report to evaluate the performance of the model on the original dataset

print("Random Forest Classifier used before resampling :")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
# Perform SMOTE resampling

smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# print the number of samples in each class
print('original dataset shape :',value_counts(y),end='\n')
print('Resampled dataset shape:', value_counts(y_resampled),end='\n')

# Train-test split the resampled data
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42,stratify=y_resampled)

print(X.shape)
print(X_resampled.shape)
print(X_train.shape)
print(X_test.shape)

#Random forest classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_resampled, y_resampled)




# Get the feature importances and print them
feature_importances = rf.feature_importances_
print(feature_importances)

# create a DataFrame of feature importances and their corresponding names
importances = pd.DataFrame({'feature': X.columns, 'importance': rf.feature_importances_})

# sort the DataFrame by importance score in descending order
importances_sorted = importances.sort_values(by='importance', ascending=False)

# print the entire DataFrame to see the ranking of all features
print(importances_sorted.head(10))
# evaluate the random forest on the testing set
#rf_pred = rf.predict(X_test)
#print("Random Forest Classifier:")
#print(classification_report(y_test, rf_pred))
#print(confusion_matrix(y_test, rf_pred))

# select the top 10 features
selected_features = importances_sorted['feature'][:10]

# train the model on the selected feature set
rf_selected = RandomForestClassifier(random_state=42)
rf_selected.fit(X_train[selected_features], y_train)

print("X-columns training")
print(X_train[selected_features])
print(y_train)

# calculate the accuracy of the model on the testing set
y_pred_selected = rf_selected.predict(X_test[selected_features])

print("X-columns test")
print(X_test[selected_features])


accuracy_selected = classification_report(y_test, y_pred_selected)
print("Random Forest Classifier used After resampling :")
print(accuracy_selected)
print(confusion_matrix(y_test, y_pred_selected))

# Plot the resampled data using scatter plot
plt.figure(figsize=(10, 12))
plt.scatter(X[y == 0]['age'], X[y == 0]['policy_annual_premium'], color='blue', label='Non-Fraud (Before SMOTE)',alpha=0.5)
plt.scatter(X[y == 1]['age'], X[y == 1]['policy_annual_premium'], color='red', label='Fraud (Before SMOTE)',alpha=0.5)

# Plotting the resampled dataset after SMOTE
plt.scatter(X_resampled[y_resampled == 0]['age'], X_resampled[y_resampled == 0]['policy_annual_premium'], color='green', label='Non-Fraud (After SMOTE)',alpha=0.5)
plt.scatter(X_resampled[y_resampled == 1]['age'], X_resampled[y_resampled == 1]['policy_annual_premium'], color='orange', label='Fraud (After SMOTE)',alpha=0.5)

plt.title('Dataset Before and After SMOTE')
plt.xlabel('Age')
plt.ylabel('Policy Annual Premium')
plt.legend()
plt.show()

pd.set_option('display.max_columns', None)
print(X.head())

categorical_columns = data_columns.select_dtypes(include=['object']).columns.tolist()

# Print the categorical values for each column
for column in categorical_columns:
    print(f"Column: {column}")
    print(data_columns[column])
    print()
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# Get the predicted probabilities for the positive class (fraud)
y_pred_proba = rf_selected.predict_proba(X_test[selected_features])[:, 1]
print(y_pred_proba)
# Compute the false positive rate (FPR), true positive rate (TPR), and thresholds
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

# Compute the area under the ROC curve (AUC)
roc_auc = auc(fpr, tpr)

# Plot the ROC curve
plt.figure()
plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
plt.plot([0, 1], [0, 1], 'k--')  # Random guess line
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()
print(roc_auc)

specificity = 1 - fpr

# Calculate Youden's Index
youden_scores = tpr + specificity - 1

# Find the index of the maximum Youden's Index
max_index = np.argmax(youden_scores)

# Find the corresponding threshold value
optimal_threshold = thresholds[max_index]

print("Optimal Threshold (Youden's Index):", optimal_threshold)

#new_data=["month as customer","age","policy state","policy deductable","policy annual","umbrella limit","insured sex","insur edu level",
 #         "ins occ","ins hobb","ins rel","capi gains","cap-loss","inc state","coll type","incident sev","auth cont","inc state",
  #        "inc city","num vech involve","prop damage","bodily inj","witness","pol rep avai","total claim amt","injury claim","property claim",
   #       "veh claim","auto make","auto model","fraud rep","csl per person","csl per acc","vehicle age","incidet period of day"]
#pd.set_option('display.max_columns', None)
#num_rows_to_display = int(len(X_test) * 0.2)
# Print the first 20% of the test data
#print(X_test.head(num_rows_to_display))
# Save the model
#db = PickleShareDB('model.pkl')
#db['model'] = rf_selected
# Save the label encoder
#db = PickleShareDB('label_encoder.pkl')
#db['label_encoder'] = label_encoder