from newspaper import Article

def extract_from_url(url):
    """
    Kisi bhi URL se article extract karo
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            'title': article.title,
            'text': article.text,
            'authors': article.authors,
            'publish_date': article.publish_date,
            'top_image': article.top_image,
            'images': list(article.images)
        }
    except Exception as e:
        return {
            'title': 'Error',
            'text': f'Failed to extract article: {str(e)}',
            'authors': [],
            'publish_date': None,
            'top_image': None,
            'images': []
        }
