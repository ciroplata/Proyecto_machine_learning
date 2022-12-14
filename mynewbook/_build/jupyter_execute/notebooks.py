#!/usr/bin/env python
# coding: utf-8

# ## EDA (Analisis Exploratorio de Datos)

# # Clasificación de tumores benignos y malignos

# Para este ejercicio de aprendizaje sobre tecnicas de aprendizaje supervizado se utilizarán los siguientes datos: https://www.kaggle.com/code/gargmanish/basic-machine-learning-with-cancer/data
# Este conjunto de datos contiene información sobre caracteristicas las de tumores detectados en pacientes que fueron diagnosticados como malignos o benignos. A continuación se importan las librerias que se usarán en la actividad. 

# In[1]:


# here we will import the libraries used for machine learning

import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv), data manipulation as in SQL
import numpy as np
import random
import matplotlib.pyplot as plt # this is used for the plot the graph 
import seaborn as sns # used for plot interactive graph. I like it most for plot
import plotly.express as px
get_ipython().run_line_magic('matplotlib', 'inline')
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression # to apply the Logistic regression
from sklearn.model_selection import train_test_split # to split the data into two parts
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold # use for cross validation
from sklearn.model_selection import GridSearchCV# for tuning parameter
from sklearn.ensemble import RandomForestClassifier # for random forest classifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm # for Support Vector Machine
from sklearn import metrics # for the check the error and accuracy of the model
from plotnine import * # incluye funciones de ggplot
from sklearn.svm import SVC # support vector machine
from sklearn.model_selection import cross_val_score # validacion cruzada
from sklearn.model_selection import GridSearchCV # grid
from sklearn.pipeline import make_pipeline
import mglearn
from sklearn.ensemble import GradientBoostingClassifier
import xgboost as xgb
from sklearn.metrics import roc_curve, auc, confusion_matrix


# A contunuación importamos los datos usando la función read_csv de la librería pandas

# In[2]:


data = pd.read_csv(".\data.csv",header=0)


# Reemplazamos las etiquetas desde strings a numeros: 1 = Maligno; 0 = Beningno

# In[3]:


data.diagnosis = data.diagnosis.replace({"M":1, "B": 0})


# A continuación revisamos la estructura del dataframe y de las variables que contiene

# In[4]:


data.head()


# Contamos los valores perdidos para cada variable

# In[5]:


pd.DataFrame(data.isnull().sum()).transpose()


# Se puede observar que las variables no presentan valores perdidos a excepción de la ultima columna, la cual será excluida de los análisis

# Considerando que el interés en este ejercicio es clasificar correctamente los diagnosticos de una base datos, a continuación visualizamos los diagnosticos.

# In[6]:


a = (data
                       .groupby("diagnosis")
                       .agg(frequency=("diagnosis", "count"))
                       .reset_index())

(ggplot(a) +
  geom_bar(aes(x = "diagnosis", y = "frequency"), stat = 'identity'))


# Se puede observar que la mayoría de diagnosticos son de tumores benignos y los malignos se presentan en una menor frecuencia. A continuación examinamos la distribución de los diagnosticos de acuerdo con otras variables de la base de datos.

# Considerando que se tiene un número elevado de variables que registran información sobre los tumores, procedemos a examinar si se pueden agrupar teniendo en cuenta sus correlaciones.

# In[7]:


plt.figure(figsize=(20,20))
sns.heatmap(data.corr(),annot=True,fmt='.0%')


# A partir de la matriz de correlacion se observa que hay grupos de variables que se relacionan entre sí. Por ejemplo, las variables radio, perimetro y area tienen una fuerte correlacion entre ellas.

# In[8]:


facet = sns.FacetGrid(data, hue="diagnosis",aspect=4)
facet.map(sns.kdeplot,'radius_mean',shade= True)
facet.set(xlim=(0, data['radius_mean'].max()))
facet.add_legend() 
plt.show()

facet = sns.FacetGrid(data, hue="diagnosis",aspect=4)
facet.map(sns.kdeplot,'texture_mean',shade= True)
facet.set(xlim=(0, data['texture_mean'].max()))
facet.add_legend() 
plt.xlim(10,40)


# Los tumores malignos, presentan un radio promedio mayor en comparación con los tumores malignos. Mientras que con respecto a la textura (desviación estándar de los valores de la escala de grises), los tumores malignos también muestran una puntuación promedio más alta, que los tumores benignos.

# In[9]:


cols = ["diagnosis", "radius_mean", "texture_mean", "perimeter_mean", "area_mean"]

sns.pairplot(data[cols], hue="diagnosis")
plt.show()


# De acuerdo con los diagramas de densidad, se aprecia que las variables que mejor permiten diferenciar el tipo de tumor, son el perimetro, el area y el radio, ya que en la variable textura, ambos grupos exhiben un alto solapamiento.

# In[10]:


size = len(data['texture_mean'])

area = np.pi * (15 * np.random.rand( size ))**2
colors = np.random.rand( size )

plt.xlabel("texture mean")
plt.ylabel("radius mean") 
plt.scatter(data['texture_mean'], data['radius_mean'], s=area, c=colors, alpha=0.5)


# ## Componentes principales

# A continuación seleccionamos las variables cuantitativas para reducir la dimensionalidad del dataset

# In[11]:


samples=data.iloc[:,2:32] # excluimos la variable de indentificación y la de diagnostico


# A continuación escalamos las variables

# In[12]:


from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler() # el reescalador mixmax

scaler.fit(samples)
samples_scaled = pd.DataFrame(scaler.transform(samples),columns=samples.columns)
samples_scaled


# Ahora examinamos los valores propios para determinar el numero de componentes que debemos extraer

# In[13]:


# creamos el modelo y ajustamos
model = PCA()
model.fit(samples_scaled)

# crear un rango que enumere las característica del ACP
caract = range(model.n_components_)

# grafiquemos la varianza explicada del modelo ACP
plt.bar(caract,model.explained_variance_)
plt.xticks(caract)
plt.ylabel('Varianza')
plt.xlabel('variables del ACP')
plt.show()


# Analizando la varianza explicada por cada componente, parece suficiente extraer cuatro componentes

# In[14]:


pca = PCA(n_components=4)
principalComponents = pca.fit_transform(samples_scaled)
principalDf = pd.DataFrame(data = principalComponents
             , columns = ['PC 1', 'PC 2','PC 3','PC 4'])
principalDf


# In[15]:


pca.explained_variance_ratio_.sum() # varianza explicada


# La varianza total explicada por las cuatro componentes es 83.90% lo cual significa que hubo poca perdida de información si se tiene en cuenta que se redujeron más de 20 dimensiones de la base de datos.

# In[16]:


x = pd.DataFrame(
    data=np.transpose(pca.components_),
    columns=["PC1","PC2","PC3","PC4"],
    index=samples.columns
)
fig, ax = plt.subplots(figsize=(10, 10))
ax = sns.heatmap(x, annot=True, cmap='Spectral', linewidths=.5)
plt.show()


# Examinando la matriz de cargas se puede observar que en el componente 1 las variables con mayor aporte de información son concave points_worst y concave points_means. En la segunda componente las variables con mayor aporte son fractal dimension_mean, fractal dimension_mean y radius_mean. La tercera componente es altamente representada por la información de las variables texture_worst, texture_mean y texture_se. Por su parte en la cuarta componente las variables con mayores cargas son texture_se, symmetry_se y smoothness_worst.
