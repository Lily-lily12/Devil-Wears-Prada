import numpy as np
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
df = pd.read_csv('clothes.csv')

# Preprocess the dataset
df['T1'] = df['Weather'].str.cat(df['Color Palette'].astype(str), sep=',')
df['T2'] = df['Pattern'].str.cat(df['Feeling'].astype(str), sep=',')
df['T3'] = df['T1'].str.cat(df['T2'].astype(str), sep=',')
df['T4'] = df['T3'].str.cat(df['Clothing Fit'].astype(str), sep=',')
df = df.drop(columns=['Weather', 'Color Palette', 'Pattern', 'Feeling', 'Clothing Fit', 'T1', 'T2', 'T3'])
df['Text'] = df['T4'].str.cat(df['Description'].astype(str), sep=',')
df = df.drop(columns=['Description', 'T4'])

# Preprocess the text data
nltk.download('stopwords')
corpus = []
ps = PorterStemmer()
all_stopwords = stopwords.words('english')
all_stopwords.remove('not')

for i in range(0, 1000):
    text = re.sub('[^a-zA-Z]', ' ', df['Text'][i])
    text = text.lower()
    text = text.split()
    text = [ps.stem(word) for word in text if word not in set(all_stopwords)]
    text = ' '.join(text)
    corpus.append(text)

# Vectorize the text data
cv = CountVectorizer(max_features=1500)
X = cv.fit_transform(corpus).toarray()

# Prepare the target variable
y = df.iloc[:, 0].values

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)

# Train the RandomForestClassifier
classifier = RandomForestClassifier(n_estimators=10, criterion='entropy', random_state=0)
classifier.fit(X_train, y_train)

# Save the model and the CountVectorizer
with open('classifier.pkl', 'wb') as f:
    pickle.dump(classifier, f)

with open('cv.pkl', 'wb') as f:
    pickle.dump(cv, f)

# Function to predict dress name from input string
def prediction(ex1):
    new_text = re.sub('[^a-zA-Z]', ' ', ex1)
    new_text = new_text.lower()
    new_text = new_text.split()
    new_text = [ps.stem(word) for word in new_text if word not in set(all_stopwords)]
    new_text = ' '.join(new_text)
    X_prediction = cv.transform([new_text]).toarray()
    y_prediction = classifier.predict(X_prediction)
    return y_prediction

# Example usage
x1 = "Snowy,Earth,Geometric,Unique,Oversized"
print(prediction(x1))

import streamlit as st
import pandas as pd
import re
import pickle
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Load the trained model and CountVectorizer
with open('classifier.pkl', 'rb') as f:
    classifier = pickle.load(f)

with open('cv.pkl', 'rb') as f:
    cv = pickle.load(f)

# Initialize the PorterStemmer and stopwords
ps = PorterStemmer()
nltk_stopwords = stopwords.words('english')
nltk_stopwords.remove('not')

# Function to preprocess input and predict dress name
def prediction(ex1):
    new_text = re.sub('[^a-zA-Z]', ' ', ex1)
    new_text = new_text.lower()
    new_text = new_text.split()
    new_text = [ps.stem(word) for word in new_text if word not in set(nltk_stopwords)]
    new_text = ' '.join(new_text)
    X_prediction = cv.transform([new_text]).toarray()
    y_prediction = classifier.predict(X_prediction)
    return y_prediction

# Dictionary mapping dress names to image URLs
dress_images = {
    "Sheath": "https://i0.wp.com/fabrickated.com/wp-content/uploads/2015/01/sheath-dress-2.jpg",
    "Sweater": "https://www.lulus.com/images/product/xlarge/10839821_2196696.jpg?w=375&hdpi=1",
    "Turtleneck": "https://rukminim2.flixcart.com/image/850/1000/kihqz680-0/t-shirt/l/p/v/m-lady-high-black-39-lime-original-imafy9hhhmrtfkbu.jpeg?q=90&crop=false",
    "Maxi": "https://binfinite.in/cdn/shop/products/AA_c21d64c0-d27f-4331-9af9-0ea7f58bb065_1080x.jpg?v=1651586266",
    "Tunic": "https://cdn.shopify.com/s/files/1/0520/7395/5522/files/Chique_02561_360x.jpg?v=1710743487",
    "Shift": "https://assets.ajio.com/medias/sys_master/root/20230825/msmp/64e8b00fddf77915197c6140/-473Wx593H-466498789-black-MODEL.jpg",
    "Knit Sweater": "https://www.parents.com/thmb/P_GRQSTQzyPvBgT_SHC1ygbQvrE=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/anrabess-women-2023-fall-crewneck-long-sleeve-oversized-cable-knit-chunky-pullover-short-sweater-ffbff34c11664b9b842848a08f4054af.jpg",
    "Peplum": "https://m.media-amazon.com/images/I/61G-3cHhh5L._AC_UY1100_.jpg",
    "Boho Midi": "https://saffronthreadsclothing.com/cdn/shop/files/154_1d55281f-0886-4361-beb7-f18162e131be_864x1152.png?v=1710853990",
    "Wrap": "https://sassystripes.com/wp-content/uploads/2022/12/AHF9657.jpg",
    "Sundress": "https://m.media-amazon.com/images/I/81z7GNVCFuL._SY741_.jpg",
    "Fit and Flare": "https://i.etsystatic.com/5609612/r/il/26377e/2464428607/il_794xN.2464428607_sess.jpg",
    "Kaftan": "https://gillori.com/cdn/shop/products/GilloriKaftanDress.jpg?v=1634469459&width=1800",
    "Pencil": "https://imgs7.luluandsky.com/catalog/product/C/D/CDDE2930-BLACK_1.jpeg",
    "Bodycon": "https://assets.ajio.com/medias/sys_master/root/20230706/Dm2i/64a5c74deebac147fc509de9/-473Wx593H-466336756-black-MODEL.jpg",
    "A-Line": "https://rukminim2.flixcart.com/image/850/1000/l19m93k0/dress/y/1/9/m-bule-yellow-western-gurudev-fashion-original-imagcvckezdrfrjf.jpeg?q=90",
    "Shirt": "https://www.hancockfashion.com/cdn/shop/files/14053White_6_1800x1800.jpg?v=1698823457",
    "T-Shirt": "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.amazon.in%2FKDF-Denim-Shirt-Dress-Women%2Fdp%2FB0C9JDWQS2&psig=AOvVaw07Q0IFhUbuT2bt04oGjqpD&ust=1720167053778000&source=images&cd=vfe&opi=89978449&ved=0CBEQjRxqFwoTCIC89eP3jIcDFQAAAAAdAAAAABAE",
    "Long Sleeve": "https://m.media-amazon.com/images/I/819Eb+tMZOL._AC_UY350_.jpg",
    "Pinafore": "https://10d06a4d12b851f1b2d5-6729d756a2f36342416a9128f1759751.lmsin.net/1000010733006-Black-BLACK-1000010733006-8122021_01-1200.jpg"
}

# Streamlit app
st.title("Dress Name Predictor")

st.write("Please select the following details to predict the dress name:")

weather_options = ["Snowy", "Sunny", "Pleasant", "Windy"]
color_palette_options = ["Earth", "Bright", "Pastel", "Neutral"]
pattern_options = ["Geometric", "Floral", "Solid colors", "Stripes"]
feeling_options = ["Unique", "Casual", "Sophisticated", "Trendy"]
clothing_fit_options = ["Oversized", "Loose", "Standard", "Tight"]

weather = st.radio("1 - What is the expected weather during the event?", weather_options, index=None)
color_palette = st.radio("2 - Choose a color palette:", color_palette_options, index=None)
pattern = st.radio("3 - Select a pattern:", pattern_options, index=None)
feeling = st.radio("4 - How do you want to feel in the outfit?", feeling_options, index=None)
clothing_fit = st.radio("5 - Choose a clothing fit:", clothing_fit_options, index=None)

if st.button("Predict Dress Name"):
    if weather and color_palette and pattern and feeling and clothing_fit:
        input_str = f"{weather},{color_palette},{pattern},{feeling},{clothing_fit}"
        result = prediction(input_str)
        dress_name = result[0]
        st.write("Predicted Dress Name:", dress_name)
        
        # Display the image if the dress name is in the dictionary
        if dress_name in dress_images:
            st.image(dress_images[dress_name], caption=dress_name)
        else:
            st.write("No image available for the predicted dress.")
    else:
        st.write("Please select an option for all questions.")
