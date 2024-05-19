import requests
import difflib
import json

API_URL = "https://devapi.beyondchats.com/api/get_message_with_sources"

def fetch_data(api_url):
    all_data = []
    current_page = 1
    while True:
        response = requests.get(api_url, params={'page': current_page})
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        data = response.json()
        all_data.extend(data['data']['data'])
        if data['data']['current_page'] >= data['data']['last_page']:
            break
        current_page += 1
    return all_data

def extract_citations(response_texts, source_contexts):
    citations = []
    cited_ids = set()  
    for response_text in response_texts:
        for source_context in source_contexts:
            similarity = difflib.SequenceMatcher(None, response_text, source_context['context']).ratio()
            if similarity > 0.7 and source_context['link'] and source_context['id'] not in cited_ids:
                citations.append({
                    "id": source_context['id'],
                    "link": source_context['link']
                })
                cited_ids.add(source_context['id'])  
    return citations

def main():
    # Fetch data from the API
    data = fetch_data(API_URL)
    
    # Extract response texts and source contexts
    response_texts = [item['response'] for item in data]
    source_contexts = [{'id': source['id'], 'link': source['link'], 'context': source['context']} 
                       for item in data for source in item.get('source', [])]
    
    # Extract citations
    citations = extract_citations(response_texts, source_contexts)
    
    # Print response text, source context, and citations
    for i, item in enumerate(data):
        print(f"Response {i+1}:")
        print(f"Context: {item['response']}")
        print("Sources (JSON format):")
        print(json.dumps(item['source'], indent=4))
        print("Citations:")
        for citation in citations:
            print(json.dumps(citation, indent=4))
        print("="*50)

if __name__ == "__main__":
    main()
