from django.shortcuts import render
from django.http import HttpRequest
import pandas as pd
import numpy as np
import re

popular_df = pd.read_pickle("BookRecSys/popular.pkl")
books = pd.read_pickle("BookRecSys/books.pkl")
pt = pd.read_pickle("BookRecSys/pt.pkl")
similarity_score = pd.read_pickle("BookRecSys/similarity_score.pkl")
popular = pd.read_pickle("BookRecSys/popular.pkl")

def Index(request):
    # Default: show top 50 books
    books_to_display = popular_df.head(50)

    if request.method == "POST":
        user_input = request.POST.get('user_input').strip().title()
        
        user_input = re.escape(user_input)
        
        filtered_books = popular_df[popular_df['Book-Title'].str.contains(user_input, case=False, regex=True)]
        
        if not filtered_books.empty:
            books_to_display = filtered_books

    context = {
        'books': zip(
            books_to_display['Book-Title'].values,
            books_to_display['Book-Author'].values,
            books_to_display['Image-URL-M'].values,
            books_to_display['num_ratings'].values,
            books_to_display['avg_ratings'].values
        ),
        'context': books_to_display[['Book-Title']].drop_duplicates().rename(columns={'Book-Title': 'title'}).to_dict('records')
    }

    return render(request, 'index.html', context)






def Recommend(request):
    data = None
    error_message = None
    context = None  

    if request.method == "POST":
        user_input = request.POST.get('user_input').strip().title()
        user_input = re.escape(user_input)

        if user_input in pt.index:
            index = np.where(pt.index == user_input)[0][0]
            similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]
            data = []
            for i in similar_items:
                temp_df = books[books['Book-Title'] == pt.index[i[0]]]
                item = {
                    'title': temp_df.drop_duplicates('Book-Title')['Book-Title'].values[0],
                    'author': temp_df.drop_duplicates('Book-Title')['Book-Author'].values[0],
                    'rating': temp_df.drop_duplicates('Book-Title')['avg_ratings'].values[0] if 'avg_ratings' in temp_df.columns else 'N/A',
                    'image_url': temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values[0],  # Assuming you want to include the image as well
                }
                data.append(item)
        else:
            error_message = f"Book '{user_input}' not found in the dataset."

    # Prepare context for suggestions
    context = books[['Book-Title']].drop_duplicates().rename(columns={'Book-Title': 'title'})
    # context['title'] = context['title'].str.replace(' ', '_')  # Replace spaces with underscores (if desired)
    context = context.to_dict('records')  # Convert to list of dictionaries
    
    return render(request, 'recommend.html', {'data': data, 'error': error_message, 'context': context})



