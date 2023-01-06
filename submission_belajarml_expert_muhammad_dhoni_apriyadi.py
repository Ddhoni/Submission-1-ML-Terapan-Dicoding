# -*- coding: utf-8 -*-
"""Submission_BelajarML_Expert_Muhammad Dhoni Apriyadi.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15r6djyBSUgjTt9nrE7tgqUVQMk1WnJNn
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.read_csv("House_Rent_Dataset.csv")

"""# Data Understanding """

df.head()

df.shape

df.info()

"""Fitur Point of Contract dan Posted On tidak mempengaruhi harga sewa pada model sehingga akan didrop

"""

df = df.drop(['Posted On', 'Point of Contact'], axis = 'columns')

"""# Data Preprocessing

## Univariate Analysis
"""

df.groupby('Area Type')['Area Type'].agg('count')

#  Pada Fitur Area Type hanya terdapat 2 sample Built Area sehingga 2 sample tersebut akan dihapus
df.drop(df.index[df['Area Type'] == 'Built Area'], inplace = True)

df.groupby('Area Type')['Area Type'].agg('count')

df.groupby('City')['City'].agg('count')

df.groupby('Furnishing Status')['Furnishing Status'].agg('count')

df.groupby('Tenant Preferred')['Tenant Preferred'].agg('count')

df.groupby('Floor')['Floor'].agg('count')

df.groupby('Floor')['Floor'].agg('count')

df.groupby('Area Locality')['Area Locality'].agg('count')

# Fitur Floor dan Area Locality memiliki banyak sekali nilai unique sehingga akan di drop
df = df.drop(['Floor', 'Area Locality'], axis = 'columns')

df.hist(bins=50, figsize=(10,10))
plt.ticklabel_format(useOffset=False, style='plain')
plt.show()

df.Rent.describe().apply(lambda x: format(x, 'f'))

"""## Multivariate Analysis"""

# Menambahkan fitur baru price per sqft
df['Price_per_sqft'] = df['Rent']*1000/df['Size']

# Mendeteksi size per BHK outlier
# 100 sqft untuk 1 BHK itu tidak biasa sehingga anggap saja batasan tresholdnya 300 sqft/bhk

df[(df.Size/df.BHK) < 300].head()

# Menghapus size per BHK outlier
df1 = df[~(df.Size/df.BHK < 300)]
df1.head()

# Mendeteksi price per sqft outlier
df1.Price_per_sqft.describe().apply(lambda x: format(x, 'f'))

"""dapat kita lihat disini bahwasannya Harga 571 per sqft sangat rendah dan harga 1400000 per sqft sangat tinggi"""

# Menghapus price per sqft outlier dengan mean dan one standard deviation
def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('City'):
        m = np.mean(subdf.Price_per_sqft)
        st = np.std(subdf.Price_per_sqft)
        reduced_df = subdf[(subdf.Price_per_sqft>(m-st)) & (subdf.Price_per_sqft<=(m+st))]
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out

df2 = remove_pps_outliers(df1)
df2.shape

# Mendeteksi bathroom outlier
# 2 BHK dengan 4 kamar mandi itu tidak biasa jadi dianggap batasnya kamar mandi tidak boleh melebihi jumlah BHK + 2

df2[df2.Bathroom > df2.BHK + 2]

# Menghapus bathroom outlier
df2 = df2[~(df2.Bathroom > df2.BHK + 2)]
df2.head()

# Menghilangkan fitur price per sqft karena sudah tidak terpakai
df3 = df2.drop(['Price_per_sqft'], axis = 'columns')

# Melihat kolerasi antara fitur numerik dengan fitur target (harga)
plt.figure(figsize=(10, 8))
correlation_matrix = df3.corr().round(2)
 
sns.heatmap(data=correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, )
plt.title("Correlation Matrix untuk Fitur Numerik ", size=20)

cat_features = df2.select_dtypes(include='object').columns.to_list()
 
for col in cat_features:
  sns.catplot(x=col, y="Rent", kind="bar", dodge=False, height = 4, aspect = 3,  data=df2, palette="Set3")
  plt.title("Rata-rata 'Rent' Relatif terhadap - {}".format(col))

"""# Data Preparation

## Feature Engineering
"""

df3 = pd.get_dummies(data =  df3, columns = ['Area Type'])
df3 = pd.get_dummies(data =  df3, columns = ['City'])
df3 = pd.get_dummies(data =  df3, columns = ['Furnishing Status'])
df3 = pd.get_dummies(data =  df3, columns = ['Tenant Preferred'])

df3.head()

X = df3.drop(["Rent"],axis =1)
y = df3["Rent"]

from sklearn.model_selection import train_test_split
 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.05, random_state=123)

from sklearn.preprocessing import StandardScaler

# Normalisasi data train
numerical_features = ['BHK', 'Size', 'Bathroom']
scaler = StandardScaler()
scaler.fit(X_train[numerical_features])
X_train[numerical_features] = scaler.transform(X_train.loc[:, numerical_features])
X_train[numerical_features].head()

X_test.loc[:, numerical_features] = scaler.transform(X_test[numerical_features])

"""## Modelling"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ShuffleSplit

models = pd.DataFrame(index=['train_mse', 'test_mse'], 
                      columns=['RandomForest', 'Boosting','SVM'])

# buat model prediksi
RF = RandomForestRegressor(n_estimators=50, max_depth=16, random_state=55, n_jobs=-1)
RF.fit(X_train, y_train)
 
models.loc['train_mse','RandomForest'] = mean_squared_error(y_pred=RF.predict(X_train), y_true=y_train)

boosting = AdaBoostRegressor(learning_rate=0.05, random_state=55)                             
boosting.fit(X_train, y_train)
models.loc['train_mse','Boosting'] = mean_squared_error(y_pred=boosting.predict(X_train), y_true=y_train)

svm = SVR()                           
svm.fit(X_train, y_train)
models.loc['train_mse','svm'] = mean_squared_error(y_pred=svm.predict(X_train), y_true=y_train)

# Buat variabel mse yang isinya adalah dataframe nilai mse data train dan test pada masing-masing algoritma
mse = pd.DataFrame(columns=['train', 'test'], index=['RF','Boosting','svm'])
 
# Buat dictionary untuk setiap algoritma yang digunakan
model_dict = { 'RF': RF, 'Boosting': boosting,'svm':svm}
 
# Hitung Mean Squared Error masing-masing algoritma pada data train dan test
for name, model in model_dict.items():
    mse.loc[name, 'train'] = mean_squared_error(y_true=y_train, y_pred=model.predict(X_train))
    mse.loc[name, 'test'] = mean_squared_error(y_true=y_test, y_pred=model.predict(X_test))
 # Panggil mse
mse

"""## Visualiasi chart bar Hasil penghitungan Mean Squared Error masing-masing algoritma"""

fig, ax = plt.subplots()
mse.sort_values(by='test', ascending=False).plot(kind='barh', ax=ax, zorder=3)
ax.grid(zorder=0)

"""## Hasil Prediksi"""

prediksi = X_test.iloc[5:10].copy()
pred_dict = {'y_true':y_test[5:10]}
for name, model in model_dict.items():
    pred_dict['prediksi_'+name] = model.predict(prediksi).round(1)
 
pd.DataFrame(pred_dict)