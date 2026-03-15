import requests
import os
import time

API_URL = "https://api-inference.huggingface.co/models/t5-small"  # Free model
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def paraphrase(text, max_length=500):
    """
    Text ko paraphrase (rewrite) karo using Hugging Face
    """
    if len(text) < 50:
        return text
    
    payload = {
        "inputs": f"paraphrase: {text}",
        "parameters": {
            "max_length": max_length,
            "num_return_sequences": 1,
            "temperature": 0.7
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        elif response.status_code == 503:
            # Model loading, wait and retry
            time.sleep(5)
            response = requests.post(API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()[0]['generated_text']
        return text
    except:
        return text

def rewrite_article(article_text):
    """
    Pure article ko paragraph by paragraph rewrite karo
    """
    paragraphs = article_text.split('\n\n')
    new_paragraphs = []
    
    for para in paragraphs:
        if len(para.strip()) > 100:
            new_para = paraphrase(para.strip())
            new_paragraphs.append(new_para)
        else:
            new_paragraphs.append(para)
    
    return '\n\n'.join(new_paragraphs)

def seo_optimize(title, content):
    """
    Basic SEO optimization
    """
    # Ensure title has keywords
    if len(title.split()) < 5:
        title = title + " - Complete Guide 2026"
    
    # Add meta description (first 160 chars of content)
    meta_description = content[:157] + "..."
    
    # Add headings if missing
    if '<h2>' not in content and '<h3>' not in content:
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            if len(line) > 50 and i % 3 == 0:
                new_lines.append(f'<h2>{line[:30]}</h2>')
            new_lines.append(line)
        content = '\n'.join(new_lines)
    
    return title, content, meta_description
