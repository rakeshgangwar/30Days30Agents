# Day 6: Learning Coach Agent - Integration Guide

This document provides detailed guidance on integrating the Learning Coach agent with various open-source learning tools and services.

## Table of Contents
1. [Learning Management Systems](#learning-management-systems)
2. [Learning Pathways Tools](#learning-pathways-tools)
3. [Knowledge Graphs](#knowledge-graphs)
4. [Open Educational Resources](#open-educational-resources)
5. [Assessment Tools](#assessment-tools)
6. [Integration Best Practices](#integration-best-practices)

## Learning Management Systems

### Frappe LMS

Frappe LMS is an open-source learning management system built on the Frappe framework.

#### Integration Method
- **API-based**: RESTful API integration
- **GitHub**: [https://github.com/frappe/lms](https://github.com/frappe/lms)

#### Setup Instructions
1. Install Frappe LMS locally or use a hosted instance
2. Generate API credentials in the LMS admin panel
3. Configure the Learning Coach agent with these credentials

#### API Endpoints
- `GET /api/courses`: List all available courses
- `GET /api/courses/{id}`: Get course details
- `GET /api/progress/{user_id}`: Get user progress
- `POST /api/enroll`: Enroll user in a course

#### Implementation Example
```python
import requests

class FrappeLMSConnector:
    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {api_key}:{api_secret}'
        })
    
    def get_courses(self):
        response = self.session.get(f"{self.base_url}/api/courses")
        return response.json()
    
    def get_course_details(self, course_id):
        response = self.session.get(f"{self.base_url}/api/courses/{course_id}")
        return response.json()
    
    def enroll_user(self, user_id, course_id):
        data = {
            'user_id': user_id,
            'course_id': course_id
        }
        response = self.session.post(f"{self.base_url}/api/enroll", json=data)
        return response.json()
```

### CourseList

CourseList is an open-source platform for creating and selling courses.

#### Integration Method
- **API-based**: RESTful API integration
- **GitHub**: [https://github.com/codelitdev/courselit](https://github.com/codelitdev/courselit)

#### Setup Instructions
1. Set up a CourseList instance (self-hosted or cloud)
2. Create API credentials in the admin settings
3. Configure the Learning Coach agent with these credentials

#### API Endpoints
- `GET /api/courses`: List available courses
- `GET /api/lessons/{id}`: Get lesson content
- `GET /api/progress/{user_id}`: Get user progress
- `POST /api/progress`: Update progress

#### Implementation Example
```python
import requests

class CourseListConnector:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
    
    def get_courses(self, filters=None):
        params = filters or {}
        response = self.session.get(f"{self.base_url}/api/courses", params=params)
        return response.json()
    
    def get_lesson(self, lesson_id):
        response = self.session.get(f"{self.base_url}/api/lessons/{lesson_id}")
        return response.json()
```

## Learning Pathways Tools

### Mangro.io Concepts

Mangro.io is a learning roadmap platform for creating visual learning paths.

#### Integration Method
- **Concept Adaptation**: Since there's no direct API, we'll implement the concepts and UI patterns
- **Reference**: [https://mangro.io/](https://mangro.io/)

#### Implementation Approach
1. Create a visual path builder UI component inspired by Mangro.io
2. Implement node-based learning paths with connections
3. Allow for branching paths based on user choices or performance

#### Implementation Example
```python
# Streamlit UI for a Mangro.io-style learning path builder
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

def render_learning_path(path_data):
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes (topics)
    for topic in path_data['topics']:
        G.add_node(topic['id'], label=topic['title'])
    
    # Add edges (prerequisites)
    for topic in path_data['topics']:
        for prereq in topic.get('prerequisites', []):
            G.add_edge(prereq, topic['id'])
    
    # Plot
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', 
            node_size=2000, edge_color='gray', arrows=True)
    
    # Convert to Streamlit
    st.pyplot(plt)
```

### Learning-Pathways.org Models

Learning-Pathways.org is a platform for creating and sharing collections of learning resources.

#### Integration Method
- **Concept Adaptation**: Implement similar models for resource organization
- **Reference**: [https://learning-pathways.org/](https://learning-pathways.org/)

#### Implementation Approach
1. Create data models for organizing resources into thematic collections
2. Implement a recommendation system for suggesting related resources
3. Allow users to create and share their own learning pathways

#### Implementation Example
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class LearningPathway:
    id: str
    title: str
    description: str
    creator_id: str
    created_at: datetime
    is_public: bool
    tags: List[str]
    resources: List['Resource']
    
    def add_resource(self, resource):
        self.resources.append(resource)
        
    def remove_resource(self, resource_id):
        self.resources = [r for r in self.resources if r.id != resource_id]
        
    def reorder_resources(self, new_order):
        # Reorder resources based on the new order of IDs
        resource_map = {r.id: r for r in self.resources}
        self.resources = [resource_map[id] for id in new_order if id in resource_map]
```

## Knowledge Graphs

### Wikidata Integration

Wikidata is a free and open knowledge base that can be read and edited by both humans and machines.

#### Integration Method
- **SPARQL Endpoint**: Query the Wikidata SPARQL service
- **Endpoint**: [https://query.wikidata.org/sparql](https://query.wikidata.org/sparql)

#### Setup Instructions
1. No authentication required for read queries
2. Install the SPARQLWrapper Python package
3. Create query templates for common knowledge retrievals

#### Implementation Example
```python
from SPARQLWrapper import SPARQLWrapper, JSON

class WikidataConnector:
    def __init__(self):
        self.endpoint = "https://query.wikidata.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setReturnFormat(JSON)
    
    def query_subject_concepts(self, subject_name):
        query = f"""
        SELECT ?item ?itemLabel ?itemDescription WHERE {{
          ?item ?label "{subject_name}"@en .
          ?item wdt:P31 wd:Q5 .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
    
    def get_subject_prerequisites(self, subject_id):
        query = f"""
        SELECT ?prereq ?prereqLabel WHERE {{
          wd:{subject_id} wdt:P2283 ?prereq .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]
```

### ConceptNet Integration

ConceptNet is an open, multilingual knowledge graph designed to help computers understand the meanings of words.

#### Integration Method
- **REST API**: HTTP requests to the ConceptNet API
- **API Endpoint**: [http://api.conceptnet.io/](http://api.conceptnet.io/)

#### Implementation Example
```python
import requests

class ConceptNetConnector:
    def __init__(self):
        self.base_url = "http://api.conceptnet.io"
    
    def get_related_concepts(self, concept, relation=None):
        """Get concepts related to the input concept."""
        params = {'limit': 50}
        url = f"{self.base_url}/c/en/{concept}"
        if relation:
            url = f"{self.base_url}/query?start=/c/en/{concept}&rel=/r/{relation}"
        
        response = requests.get(url, params=params)
        return response.json()
    
    def get_edges_between(self, concept1, concept2):
        """Get relationships between two concepts."""
        url = f"{self.base_url}/query?node=/c/en/{concept1}&other=/c/en/{concept2}"
        response = requests.get(url)
        return response.json()
```

## Open Educational Resources

### OER Commons Integration

OER Commons is a public digital library of open educational resources.

#### Integration Method
- **Web Scraping**: Since there's no official API, implement web scraping with proper rate limiting
- **Website**: [https://www.oercommons.org/](https://www.oercommons.org/)

#### Implementation Example
```python
import requests
from bs4 import BeautifulSoup
import time

class OERCommonsConnector:
    def __init__(self):
        self.base_url = "https://www.oercommons.org"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Learning Coach Agent - Educational Purpose'
        })
    
    def search_resources(self, query, subject=None, grade_level=None):
        params = {
            'query': query
        }
        if subject:
            params['subject'] = subject
        if grade_level:
            params['grade_level'] = grade_level
            
        response = self.session.get(self.search_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for item in soup.select('.search-result-item'):
            title = item.select_one('.item-title').text.strip()
            url = self.base_url + item.select_one('a')['href']
            description = item.select_one('.item-description').text.strip()
            
            results.append({
                'title': title,
                'url': url,
                'description': description
            })
            
        time.sleep(1)  # Rate limiting
        return results
    
    def get_resource_details(self, resource_url):
        response = self.session.get(resource_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract detailed information
        title = soup.select_one('.resource-title').text.strip()
        description = soup.select_one('.resource-description').text.strip()
        subjects = [s.text.strip() for s in soup.select('.metadata-subjects .value')]
        grade_levels = [g.text.strip() for g in soup.select('.metadata-education-levels .value')]
        
        time.sleep(1)  # Rate limiting
        return {
            'title': title,
            'description': description,
            'subjects': subjects,
            'grade_levels': grade_levels
        }
```

### OpenStax Integration

OpenStax offers free, peer-reviewed, openly licensed textbooks for educational use.

#### Integration Method
- **Web Scraping + Direct Content Access**: Scrape metadata and access content through direct links
- **Website**: [https://openstax.org/](https://openstax.org/)

#### Implementation Example
```python
import requests
from bs4 import BeautifulSoup
import time

class OpenStaxConnector:
    def __init__(self):
        self.base_url = "https://openstax.org"
        self.books_url = f"{self.base_url}/subjects"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Learning Coach Agent - Educational Purpose'
        })
    
    def get_available_books(self):
        response = self.session.get(self.books_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        books = []
        for book in soup.select('.book-card'):
            title = book.select_one('.title').text.strip()
            book_url = self.base_url + book.select_one('a')['href']
            subject = book.select_one('.subject').text.strip()
            
            books.append({
                'title': title,
                'url': book_url,
                'subject': subject
            })
            
        time.sleep(1)  # Rate limiting
        return books
    
    def get_book_contents(self, book_url):
        response = self.session.get(book_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get table of contents
        toc = []
        for chapter in soup.select('.chapter'):
            chapter_title = chapter.select_one('.title').text.strip()
            chapter_url = self.base_url + chapter.select_one('a')['href']
            
            toc.append({
                'title': chapter_title,
                'url': chapter_url
            })
            
        time.sleep(1)  # Rate limiting
        return toc
```

## Assessment Tools

### H5P Integration

H5P is an open-source framework for creating rich interactive content.

#### Integration Method
- **JavaScript Embedding**: Embed H5P content in web pages
- **API Integration**: Use the H5P PHP library or REST API (if available)
- **Reference**: [https://h5p.org/](https://h5p.org/)

#### Setup Instructions
1. Set up an H5P server (or use an existing one)
2. Create H5P content types for quizzes, flashcards, etc.
3. Use the embed codes or API to integrate with the Learning Coach

#### Implementation Example (Python + JavaScript)
```python
# Python server-side component
class H5PConnector:
    def __init__(self, h5p_endpoint, api_key=None):
        self.h5p_endpoint = h5p_endpoint
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def get_content_types(self):
        response = self.session.get(f"{self.h5p_endpoint}/content-types")
        return response.json()
    
    def get_content(self, content_id):
        response = self.session.get(f"{self.h5p_endpoint}/content/{content_id}")
        return response.json()
    
    def create_quiz_content(self, title, questions):
        # Structure depends on the specific H5P implementation
        data = {
            'title': title,
            'contentType': 'Quiz',
            'parameters': {
                'questions': questions
            }
        }
        response = self.session.post(f"{self.h5p_endpoint}/content", json=data)
        return response.json()
```

```javascript
// JavaScript client-side component for embedding H5P content
function embedH5PContent(containerId, contentId, h5pUrl) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const iframe = document.createElement('iframe');
    iframe.src = `${h5pUrl}/content/${contentId}/embed`;
    iframe.width = '100%';
    iframe.height = '400px';
    iframe.frameBorder = '0';
    iframe.allowFullscreen = true;
    
    container.appendChild(iframe);
    
    // Listen for H5P events
    window.addEventListener('message', function(event) {
        if (event.data && event.data.context === 'h5p') {
            console.log('H5P Event:', event.data);
            // Handle events like 'completed', 'answered', etc.
        }
    });
}
```

### Spaced Repetition (SM-2 Algorithm)

Implement the SuperMemo SM-2 algorithm for spaced repetition scheduling.

#### Integration Method
- **Direct Implementation**: Code the algorithm directly in the Learning Coach agent
- **Reference**: [https://www.supermemo.com/en/archives1990-2015/english/ol/sm2](https://www.supermemo.com/en/archives1990-2015/english/ol/sm2)

#### Implementation Example
```python
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class FlashcardStats:
    repetition: int = 0
    ease_factor: float = 2.5
    interval: int = 0  # days
    next_review: datetime = datetime.now()

class SM2SpacedRepetition:
    def __init__(self):
        self.flashcards = {}  # id -> FlashcardStats
    
    def add_flashcard(self, card_id):
        self.flashcards[card_id] = FlashcardStats()
    
    def process_response(self, card_id, quality):
        """Process a flashcard response.
        
        quality: 0-5 scale where:
            0 = complete blackout
            1 = incorrect, but recognized
            2 = incorrect, but easy to remember
            3 = correct, but difficult
            4 = correct, with effort
            5 = correct, perfect recall
        """
        if card_id not in self.flashcards:
            self.add_flashcard(card_id)
            
        stats = self.flashcards[card_id]
        
        if quality < 3:
            # Failed recall, reset repetition
            stats.repetition = 0
            stats.interval = 0
        else:
            # Successful recall, update parameters
            if stats.repetition == 0:
                stats.interval = 1
            elif stats.repetition == 1:
                stats.interval = 6
            else:
                stats.interval = round(stats.interval * stats.ease_factor)
            
            stats.repetition += 1
        
        # Update ease factor
        stats.ease_factor = max(1.3, stats.ease_factor + (0.1 - (5 - quality) * 0.08))
        
        # Calculate next review date
        stats.next_review = datetime.now() + timedelta(days=stats.interval)
        
        return stats
    
    def get_due_cards(self):
        """Get all cards due for review."""
        now = datetime.now()
        return [card_id for card_id, stats in self.flashcards.items() 
                if stats.next_review <= now]
```

## Integration Best Practices

### Error Handling
- Implement robust error handling for all external service calls
- Use exponential backoff for retries
- Provide graceful fallbacks when services are unavailable

```python
import time
from functools import wraps

def retry_with_backoff(retries=3, backoff_factor=2):
    """Retry a function with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = retries
            retry_count = 0
            delay = 1
            
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise e
                    
                    time.sleep(delay)
                    delay *= backoff_factor
            
        return wrapper
    return decorator
```

### Caching
- Implement caching for expensive or frequently used queries
- Use time-based expiration for dynamic content
- Consider using Redis or a similar caching system

```python
import functools
import time

def timed_cache(seconds=600):
    """Simple time-based cache decorator."""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            current_time = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result
        
        return wrapper
    return decorator
```

### Rate Limiting
- Respect rate limits of external services
- Implement token bucket or similar rate limiting algorithms
- Distribute requests over time for batch operations

```python
import time
import threading

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = threading.Lock()
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.lock:
                current_time = time.time()
                # Remove old calls
                self.calls = [t for t in self.calls if current_time - t < self.period]
                
                if len(self.calls) >= self.max_calls:
                    # Rate limit exceeded, sleep until oldest call expires
                    sleep_time = self.period - (current_time - self.calls[0])
                    time.sleep(max(0, sleep_time))
                
                self.calls.append(time.time())
            
            return func(*args, **kwargs)
        return wrapper
```

### Concurrency
- Use async/await for I/O-bound operations
- Implement thread or process pools for parallel tasks
- Ensure proper locking for shared resources

```python
import asyncio
import aiohttp

async def fetch_content(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parallel_fetch(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

### Logging & Monitoring
- Log all integration activities for debugging
- Monitor performance and error rates
- Set up alerts for integration failures

```python
import logging

logger = logging.getLogger('integrations')

class LoggedIntegration:
    def __init__(self, name):
        self.name = name
        
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Integration call: {self.name} - {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Integration success: {self.name} - {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Integration error: {self.name} - {func.__name__}: {str(e)}")
                raise
        return wrapper
```

## Conclusion

This integration guide provides a foundation for connecting the Learning Coach agent with various open-source learning tools. By following these examples and best practices, you can create a robust, scalable system that leverages the best educational tools available.

When implementing these integrations, consider starting with the most critical ones for your use case and gradually adding more as needed. This incremental approach allows for better testing and validation of each integration before moving on to the next.