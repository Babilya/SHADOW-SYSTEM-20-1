import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SocialMediaOSINT:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.timeout = 10
    
    def search_reddit(self, keyword: str, limit: int = 25) -> List[Dict[str, Any]]:
        try:
            url = f"https://www.reddit.com/search.json"
            params = {'q': keyword, 'limit': min(limit, 100), 'sort': 'relevance'}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for post in data.get('data', {}).get('children', []):
                    post_data = post.get('data', {})
                    results.append({
                        'title': post_data.get('title'),
                        'author': post_data.get('author'),
                        'subreddit': post_data.get('subreddit'),
                        'url': post_data.get('url'),
                        'score': post_data.get('score'),
                        'num_comments': post_data.get('num_comments'),
                        'created': datetime.fromtimestamp(post_data.get('created_utc', 0)).isoformat(),
                        'selftext': post_data.get('selftext', '')[:200]
                    })
                
                return results
            return [{'error': f'Status code: {response.status_code}'}]
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            return [{'error': str(e)}]
    
    def get_github_user(self, username: str) -> Dict[str, Any]:
        try:
            url = f"https://api.github.com/users/{username}"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'login': data.get('login'),
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'company': data.get('company'),
                    'location': data.get('location'),
                    'email': data.get('email'),
                    'blog': data.get('blog'),
                    'twitter_username': data.get('twitter_username'),
                    'public_repos': data.get('public_repos'),
                    'public_gists': data.get('public_gists'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'avatar_url': data.get('avatar_url'),
                    'timestamp': datetime.now().isoformat()
                }
            elif response.status_code == 404:
                return {'error': 'User not found'}
            return {'error': f'Status code: {response.status_code}'}
        except Exception as e:
            logger.error(f"GitHub user error: {e}")
            return {'error': str(e)}
    
    def get_github_repos(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            url = f"https://api.github.com/users/{username}/repos"
            params = {'sort': 'updated', 'per_page': limit}
            
            response = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                repos = []
                for repo in response.json():
                    repos.append({
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description'),
                        'language': repo.get('language'),
                        'stars': repo.get('stargazers_count'),
                        'forks': repo.get('forks_count'),
                        'watchers': repo.get('watchers_count'),
                        'open_issues': repo.get('open_issues_count'),
                        'created_at': repo.get('created_at'),
                        'updated_at': repo.get('updated_at'),
                        'url': repo.get('html_url'),
                        'is_fork': repo.get('fork')
                    })
                return repos
            return [{'error': f'Status code: {response.status_code}'}]
        except Exception as e:
            logger.error(f"GitHub repos error: {e}")
            return [{'error': str(e)}]
    
    def check_username_availability(self, username: str) -> Dict[str, Any]:
        platforms = {
            'github': f'https://github.com/{username}',
            'twitter': f'https://twitter.com/{username}',
            'instagram': f'https://www.instagram.com/{username}/',
            'tiktok': f'https://www.tiktok.com/@{username}',
            'youtube': f'https://www.youtube.com/@{username}',
            'linkedin': f'https://www.linkedin.com/in/{username}',
            'reddit': f'https://www.reddit.com/user/{username}'
        }
        
        results = {'username': username, 'platforms': {}}
        
        for platform, url in platforms.items():
            try:
                response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
                results['platforms'][platform] = {
                    'exists': response.status_code == 200,
                    'url': url,
                    'status_code': response.status_code
                }
            except Exception as e:
                results['platforms'][platform] = {
                    'exists': None,
                    'url': url,
                    'error': str(e)
                }
        
        results['timestamp'] = datetime.now().isoformat()
        return results
    
    def search_hacker_news(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            search_url = f"https://hn.algolia.com/api/v1/search"
            params = {'query': keyword, 'hitsPerPage': limit}
            
            response = requests.get(search_url, params=params, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for hit in data.get('hits', []):
                    results.append({
                        'title': hit.get('title'),
                        'author': hit.get('author'),
                        'url': hit.get('url'),
                        'points': hit.get('points'),
                        'num_comments': hit.get('num_comments'),
                        'created_at': hit.get('created_at'),
                        'story_id': hit.get('story_id'),
                        'hn_url': f"https://news.ycombinator.com/item?id={hit.get('story_id')}"
                    })
                return results
            return [{'error': f'Status code: {response.status_code}'}]
        except Exception as e:
            logger.error(f"HN search error: {e}")
            return [{'error': str(e)}]

social_media_osint = SocialMediaOSINT()
