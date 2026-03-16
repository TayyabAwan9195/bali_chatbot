import re
import json
import os
from PyPDF2 import PdfReader

PDF_PATH = 'd:/Freelance Projects/bali_chatbot/AI Chat Bot 1.pdf'


def extract_topic_chunks(pdf_path: str = PDF_PATH) -> list[str]:
    """Read PDF and split into topic-based chunks using ⸻ separator."""
    reader = PdfReader(pdf_path)
    full_text = ''
    for page in reader.pages:
        page_text = page.extract_text() or ''
        full_text += ' ' + page_text
    # Normalize whitespace
    full_text = ' '.join(full_text.split())
    
    # Split by ⸻ to get sections
    sections = re.split(r'⸻', full_text)
    chunks = []
    seen = set()
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Count Q&A pairs (minimum 3 per chunk)
        q_count = section.count('Q:')
        if q_count >= 3:
            # Remove duplicates
            if section not in seen:
                seen.add(section)
                chunks.append(section)
    
    return chunks

# if run directly, extract FAQs and also produce chunks file
path = PDF_PATH
reader = PdfReader(path)
text = ''
for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += '\n' + page_text

# parse lines to handle questions and answers cleanly
lines = text.splitlines()
faqs = []
current_q = None
current_a_lines = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith('Q:'):
        # save previous FAQ if exists
        if current_q:
            ans = ' '.join(l for l in current_a_lines if l)
            # clean answer before saving
            ans = re.split(r'⸻|-{3,}', ans)[0].strip()
            faqs.append({'question': current_q, 'answer': ans})
        current_q = stripped[2:].strip()
        # remove trailing section markers if present
        current_q = re.split(r'⸻|-{3,}', current_q)[0].strip()
        current_a_lines = []
    elif stripped.startswith('A:') and current_q is not None:
        current_a_lines.append(stripped[2:].strip())
    else:
        # continuation of answer or ignore odd lines
        if current_q is not None and current_a_lines is not None:
            current_a_lines.append(stripped)
# append last
if current_q:
    ans = ' '.join(l for l in current_a_lines if l)
    # clean answer: drop any trailing section marker and following text
    ans = re.split(r'⸻|-{3,}', ans)[0].strip()
    faqs.append({'question': current_q, 'answer': ans})

# dedupe within extracted
unique = []
seen = set()
for item in faqs:
    key = item['question'].lower()
    if key not in seen:
        seen.add(key)
        unique.append(item)
faqs = unique
print('found', len(faqs), 'faqs (unique)')
stopwords=set(['the','is','a','an','to','for','of','in','and','with','how','what','can','are','it','on','does','do','at','by','or','from','that','which'])
import string
for item in faqs:
    words=[w.strip(string.punctuation) for w in item['question'].lower().split()]
    keywords=[w for w in words if w not in stopwords]
    keywords_unique=[]
    for w in keywords:
        if w not in keywords_unique:
            keywords_unique.append(w)
    item['keywords']=', '.join(keywords_unique[:5])

with open('faq.json','r',encoding='utf-8') as f:
    data=json.load(f)
existing_questions=[e['question'].lower() for e in data['faq']]
added=0
for item in faqs:
    if item['question'].lower() not in existing_questions:
        data['faq'].append(item)
        added+=1

print('added',added,'new items; total', len(data['faq']))
with open('faq.json','w',encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# also write PDF chunks for RAG
chunks = extract_topic_chunks(path)
with open('chunks.json','w',encoding='utf-8') as f:
    json.dump({"chunks": chunks}, f, indent=2, ensure_ascii=False)
print('wrote', len(chunks), 'topic-based chunks to chunks.json')

# Delete cached embeddings to force regeneration
if os.path.exists('chunks_embeddings.npy'):
    os.remove('chunks_embeddings.npy')
    print('deleted chunks_embeddings.npy')
