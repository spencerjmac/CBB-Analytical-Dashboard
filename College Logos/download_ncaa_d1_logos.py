#!/usr/bin/env python3
"""
NCAA Division I College Basketball Logo Scraper for Tableau

This script scrapes all NCAA Division I college basketball team logos from ESPN,
downloads them, processes them for Tableau use, and creates a zip file ready for
import into Tableau as custom shapes.

USAGE INSTRUCTIONS:
-------------------
1. Install dependencies:
   
   On Windows, try one of these commands:
   - python -m pip install -r requirements.txt
   - python3 -m pip install -r requirements.txt
   - py -m pip install -r requirements.txt
   - pip install -r requirements.txt
   
   If Python is not installed, download it from https://www.python.org/downloads/
   Make sure to check "Add Python to PATH" during installation.

2. Run the script:
   python download_ncaa_d1_logos.py
   
   Or if that doesn't work:
   python3 download_ncaa_d1_logos.py
   py download_ncaa_d1_logos.py

   Optional arguments:
   python download_ncaa_d1_logos.py --out-dir output --max-size 512 --throttle-seconds 1.0

3. Find the output:
   - The zip file will be created at: output/ncaa_d1_basketball_logos_for_tableau.zip
   - Extract this zip file to: My Tableau Repository/Shapes/NCAA_D1_College_Basketball_Logos/
   - In Tableau, you can then use these logos as custom shapes in your visualizations

4. Using in Tableau:
   - After extracting to the Shapes folder, restart Tableau
   - When creating a visualization, go to Shape > More Shapes
   - Select "NCAA_D1_College_Basketball_Logos" from the list
   - Map your team names to the logo filenames using the metadata CSV

Author: Generated for Tableau logo collection
Date: 2024
"""

import argparse
import csv
import logging
import os
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple
from multiprocessing import Pool, Manager
from functools import partial

# Check for required dependencies
try:
    import requests
except ImportError:
    print("ERROR: 'requests' module not found.")
    print("Please install dependencies by running:")
    print("  python -m pip install -r requirements.txt")
    print("Or: pip install requests beautifulsoup4 Pillow lxml")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: 'beautifulsoup4' module not found.")
    print("Please install dependencies by running:")
    print("  python -m pip install -r requirements.txt")
    print("Or: pip install requests beautifulsoup4 Pillow lxml")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("ERROR: 'Pillow' module not found.")
    print("Please install dependencies by running:")
    print("  python -m pip install -r requirements.txt")
    print("Or: pip install requests beautifulsoup4 Pillow lxml")
    sys.exit(1)

import io

# Configure logging with UTF-8 support
import codecs

# Create a UTF-8 stream handler for stdout
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        if stream is None:
            stream = sys.stdout
        # Reopen stdout with UTF-8 encoding if possible
        if hasattr(stream, 'reconfigure'):
            try:
                stream.reconfigure(encoding='utf-8', errors='replace')
            except:
                pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        UTF8StreamHandler(sys.stdout),
        logging.FileHandler('scrape_log.txt', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """Helper function for multiprocessing - sanitize filename."""
    # Remove common prefixes/suffixes
    name = re.sub(r'\s*(University|College|State|Tech|Institute)\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE)
    
    # Convert to lowercase and replace spaces/special chars with underscores
    name = name.lower()
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except hyphens
    name = re.sub(r'[\s_]+', '_', name)  # Replace spaces and multiple underscores with single underscore
    name = name.strip('_')  # Remove leading/trailing underscores
    
    return name


def download_logo_worker(idx: int, total: int, team: Dict, logos_dir: str, max_size: int, throttle_seconds: float) -> Dict:
    """
    Worker function for multiprocessing to download a single logo.
    
    Args:
        idx: Team index (1-based)
        total: Total number of teams
        team: Team dictionary
        logos_dir: Directory to save logos
        max_size: Maximum image size
        throttle_seconds: Delay between requests (not used in worker, but kept for compatibility)
        
    Returns:
        Dictionary with 'success', 'filename', and 'error' keys
    """
    import requests
    from PIL import Image
    import io
    
    school_name = team['school_name']
    team_name = team['team_name']
    logo_url = team['logo_url']
    
    logger.info(f"[{idx}/{total}] Processing: {school_name}")
    
    if not logo_url:
        return {
            'success': False,
            'filename': None,
            'error': 'No logo URL found'
        }
    
    # Generate filename
    filename = sanitize_filename(school_name)
    if filename != sanitize_filename(team_name):
        team_filename = sanitize_filename(team_name)
        filename = f"{filename}_{team_filename}"
    
    # Create session for this worker
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    # Download image
    image_data = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = session.get(logo_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Check if it's an image
            content_type = response.headers.get('Content-Type', '').lower()
            if not (content_type.startswith('image/') or 
                    'svg' in content_type or 
                    logo_url.lower().endswith('.svg') or
                    logo_url.lower().endswith('.svgz')):
                if not content_type:
                    if not logo_url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                        if attempt == max_retries - 1:
                            return {
                                'success': False,
                                'filename': None,
                                'error': 'Not an image file'
                            }
                else:
                    if attempt == max_retries - 1:
                        return {
                            'success': False,
                            'filename': None,
                            'error': f'Invalid content type: {content_type}'
                        }
            
            image_data = response.content
            break
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return {
                    'success': False,
                    'filename': None,
                    'error': f'Download failed: {str(e)}'
                }
    
    if not image_data:
        return {
            'success': False,
            'filename': None,
            'error': 'Download failed'
        }
    
    # Process and save image
    try:
        logos_path = Path(logos_dir)
        
        # Check if it's an SVG file
        if image_data.startswith(b'<svg') or image_data.startswith(b'<?xml'):
            output_path = logos_path / f"{filename}.svg"
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return {
                'success': True,
                'filename': f"{filename}.svg",
                'error': None
            }
        
        # Try to open as image with Pillow
        try:
            img = Image.open(io.BytesIO(image_data))
        except Exception:
            # If it's not a standard image format, try saving as-is
            if image_data.startswith(b'\x89PNG'):
                ext = '.png'
            elif image_data.startswith(b'\xff\xd8'):
                ext = '.jpg'
            elif image_data.startswith(b'GIF'):
                ext = '.gif'
            else:
                ext = '.png'
            
            output_path = logos_path / f"{filename}{ext}"
            with open(output_path, 'wb') as f:
                f.write(image_data)
            return {
                'success': True,
                'filename': f"{filename}{ext}",
                'error': None
            }
        
        # Convert RGBA if needed
        if img.mode not in ('RGBA', 'RGB', 'LA', 'L'):
            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
            else:
                img = img.convert('RGB')
        
        # Resize if needed
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Save as PNG
        output_path = logos_path / f"{filename}.png"
        img.save(output_path, 'PNG', optimize=True)
        
        return {
            'success': True,
            'filename': f"{filename}.png",
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'filename': None,
            'error': f'Image processing failed: {str(e)}'
        }


class NCAA_Logo_Scraper:
    """Scraper for NCAA Division I college basketball team logos."""
    
    def __init__(self, out_dir: str = "output", max_size: int = 512, throttle_seconds: float = 1.0, num_workers: int = 20):
        """
        Initialize the scraper.
        
        Args:
            out_dir: Output directory for logos and metadata
            max_size: Maximum pixel dimension for resized logos
            throttle_seconds: Delay between HTTP requests (not used with multiprocessing)
            num_workers: Number of parallel workers for downloading logos
        """
        self.out_dir = Path(out_dir)
        self.logos_dir = self.out_dir / "logos"
        self.metadata_dir = self.out_dir / "metadata"
        self.max_size = max_size
        self.throttle_seconds = throttle_seconds
        self.num_workers = num_workers
        
        # Create output directories
        self.logos_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        self.teams: List[Dict] = []
        self.missing_logos: List[Dict] = []
    
    def sanitize_filename(self, name: str) -> str:
        """
        Convert a team/school name to a clean filename.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized filename (lowercase, underscores, no special chars)
        """
        # Remove common prefixes/suffixes
        name = re.sub(r'\s*(University|College|State|Tech|Institute)\s*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE)
        
        # Convert to lowercase and replace spaces/special chars with underscores
        name = name.lower()
        name = re.sub(r'[^\w\s-]', '', name)  # Remove special chars except hyphens
        name = re.sub(r'[\s_]+', '_', name)  # Replace spaces and multiple underscores with single underscore
        name = name.strip('_')  # Remove leading/trailing underscores
        
        return name
    
    def get_wikipedia_file_url(self, file_path: str) -> Optional[str]:
        """
        Get the direct file URL from a Wikipedia file path using the API.
        
        Args:
            file_path: File path like "a/a1/Logo.svg" or "File:Logo.svg"
            
        Returns:
            Direct file URL or None
        """
        try:
            # Remove "File:" prefix if present
            if file_path.startswith('File:'):
                file_path = file_path[5:]
            
            # If it's already a full path (e.g., "a/a1/Logo.svg"), use it directly
            if '/' in file_path and not file_path.startswith('http'):
                # Try commons first (most common)
                url = f'https://upload.wikimedia.org/wikipedia/commons/{file_path}'
                # Test if it exists
                test_response = self.session.head(url, timeout=5, allow_redirects=True)
                if test_response.status_code == 200:
                    return url
                
                # Try en.wikipedia.org
                url = f'https://upload.wikimedia.org/wikipedia/en/{file_path}'
                test_response = self.session.head(url, timeout=5, allow_redirects=True)
                if test_response.status_code == 200:
                    return url
            
            # Use Wikipedia API to get file info
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': f'File:{file_path}',
                'prop': 'imageinfo',
                'iiprop': 'url'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get('imageinfo', [])
                if imageinfo and len(imageinfo) > 0:
                    return imageinfo[0].get('url')
            
        except Exception as e:
            logger.debug(f"Error getting file URL for {file_path}: {e}")
        
        return None
    
    def search_athletics_logo_file(self, school_name: str, team_name: str) -> Optional[str]:
        """
        Search Wikipedia for athletics logo files directly.
        
        Args:
            school_name: School name
            team_name: Team name/nickname
            
        Returns:
            Logo URL or None
        """
        # Common athletics logo filename patterns
        search_patterns = [
            f"{school_name} {team_name} logo",
            f"{school_name} athletics logo",
            f"{team_name} logo",
            f"{school_name} logo"
        ]
        
        for pattern in search_patterns:
            try:
                api_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': f'filetype:bitmap {pattern}',
                    'srnamespace': 6,  # File namespace
                    'srlimit': 5
                }
                
                response = self.session.get(api_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                results = data.get('query', {}).get('search', [])
                for result in results:
                    title = result.get('title', '')
                    # Check if it's a logo file (not a seal)
                    if 'logo' in title.lower() and 'seal' not in title.lower():
                        # Get the file URL
                        file_url = self.get_wikipedia_file_url(title.replace('File:', ''))
                        if file_url:
                            return file_url
                
                time.sleep(0.5)  # Be polite
                
            except Exception as e:
                logger.debug(f"Error searching for athletics logo file: {e}")
                continue
        
        return None
    
    def get_wikipedia_logo_url(self, team_name: str, school_name: str) -> Optional[str]:
        """
        Get the athletics/sports logo URL from a Wikipedia page.
        Prioritizes athletics logos over university seals.
        
        Args:
            team_name: Team name
            school_name: School name
            
        Returns:
            Logo URL or None if not found
        """
        # Try athletics/sports pages first, then general school page
        search_terms = [
            f"{school_name} {team_name}",
            f"{school_name} athletics",
            f"{school_name} basketball",
            f"{team_name} logo",
            f"{school_name} {team_name} logo",
            school_name
        ]
        
        for search_term in search_terms:
            try:
                # Search Wikipedia
                search_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    'action': 'query',
                    'format': 'json',
                    'list': 'search',
                    'srsearch': search_term,
                    'srlimit': 1
                }
                
                response = self.session.get(search_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if not data.get('query', {}).get('search'):
                    continue
                
                page_title = data['query']['search'][0]['title']
                
                # Get the page content
                page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                response = self.session.get(page_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for infobox logo (common pattern)
                infobox = soup.find('table', class_='infobox')
                if infobox:
                    # Prioritize athletics/logo images, exclude seals
                    # First try: look for logo (but not seal)
                    logo_img = infobox.find('img', {'alt': re.compile(r'logo|athletic', re.I)})
                    if not logo_img:
                        # Second try: any image that's not a seal
                        all_imgs = infobox.find_all('img')
                        for img in all_imgs:
                            alt_text = img.get('alt', '').lower()
                            if 'seal' not in alt_text and 'emblem' not in alt_text:
                                logo_img = img
                                break
                    if not logo_img:
                        # Last resort: any image in infobox
                        logo_img = infobox.find('img')
                    
                    if logo_img:
                        # Try to get the full resolution URL from data-file-url attribute first
                        if logo_img.get('data-file-url'):
                            src = logo_img['data-file-url']
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif not src.startswith('http'):
                                src = 'https://en.wikipedia.org' + src
                            return src
                        
                        # Fallback to src attribute
                        if logo_img.get('src'):
                            src = logo_img['src']
                            if src.startswith('//'):
                                src = 'https:' + src
                            elif src.startswith('/'):
                                src = 'https://en.wikipedia.org' + src
                            
                        # Get higher resolution version (remove thumbnail dimensions)
                        if '/thumb/' in src:
                            # Wikipedia thumbnail format: /thumb/path/to/file.ext/widthpx-file.ext
                            # Example: /thumb/a/a1/Logo.svg/250px-Logo.svg
                            # We want: https://upload.wikimedia.org/wikipedia/commons/a/a1/Logo.svg
                            parts = src.split('/thumb/')
                            if len(parts) > 1:
                                file_path = parts[1]
                                # Remove the thumbnail dimension suffix (everything after the last /)
                                if '/' in file_path:
                                    # Split by / and take everything except the last part
                                    path_parts = file_path.split('/')
                                    # The last part is the dimensioned filename, remove it
                                    original_path = '/'.join(path_parts[:-1])
                                    # Get the original filename from the dimensioned one
                                    dimensioned_filename = path_parts[-1]
                                    original_filename = re.sub(r'^\d+px-', '', dimensioned_filename)
                                    # Construct the direct Wikimedia Commons URL
                                    full_path = f"{original_path}/{original_filename}"
                                    # Try to get the URL via API first, fallback to direct construction
                                    api_url = self.get_wikipedia_file_url(full_path)
                                    if api_url:
                                        return api_url
                                    src = f'https://upload.wikimedia.org/wikipedia/commons/{full_path}'
                                else:
                                    # Single filename case
                                    filename = re.sub(r'^\d+px-', '', file_path)
                                    api_url = self.get_wikipedia_file_url(filename)
                                    if api_url:
                                        return api_url
                                    src = f'https://upload.wikimedia.org/wikipedia/commons/{filename}'
                        elif not src.startswith('http'):
                            src = 'https://en.wikipedia.org' + src
                        elif '/wiki/File:' in src or '/wiki/Special:FilePath' in src:
                            # Convert Wikipedia file page URL to direct file URL
                            if '/Special:FilePath/' in src:
                                file_path = src.split('/Special:FilePath/')[-1]
                                # Remove duplicate filename if present
                                if '/' in file_path:
                                    parts = file_path.split('/')
                                    if len(parts) > 1 and parts[-1] == parts[-2]:
                                        file_path = '/'.join(parts[:-1])
                                api_url = self.get_wikipedia_file_url(file_path)
                                if api_url:
                                    return api_url
                                src = f'https://upload.wikimedia.org/wikipedia/commons/{file_path}'
                            elif '/wiki/File:' in src:
                                filename = src.split('/wiki/File:')[-1]
                                # URL decode the filename
                                from urllib.parse import unquote
                                filename = unquote(filename)
                                api_url = self.get_wikipedia_file_url(filename)
                                if api_url:
                                    return api_url
                                # Fallback - try commons (may not work without exact path)
                                src = f'https://upload.wikimedia.org/wikipedia/commons/{filename}'
                        
                        return src
                
                # Fallback: look for athletics logo images on the page (not seals)
                logo_img = None
                all_logo_imgs = soup.find_all('img', {'alt': re.compile(r'logo|athletic', re.I)})
                for img in all_logo_imgs:
                    alt_text = img.get('alt', '').lower()
                    if 'seal' not in alt_text and 'emblem' not in alt_text:
                        logo_img = img
                        break
                
                # If still no logo, try any logo image
                if not logo_img:
                    logo_img = soup.find('img', {'alt': re.compile(r'logo', re.I)})
                if logo_img:
                    # Try data-file-url first
                    if logo_img.get('data-file-url'):
                        src = logo_img['data-file-url']
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif not src.startswith('http'):
                            src = 'https://en.wikipedia.org' + src
                        return src
                    
                    # Fallback to src
                    if logo_img.get('src'):
                        src = logo_img['src']
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://en.wikipedia.org' + src
                        
                        # Handle thumbnails
                        if '/thumb/' in src:
                            parts = src.split('/thumb/')
                            if len(parts) > 1:
                                file_path = parts[1]
                                if '/' in file_path:
                                    path_parts = file_path.split('/')
                                    original_path = '/'.join(path_parts[:-1])
                                    dimensioned_filename = path_parts[-1]
                                    original_filename = re.sub(r'^\d+px-', '', dimensioned_filename)
                                    full_path = f"{original_path}/{original_filename}"
                                    # Try API first
                                    api_url = self.get_wikipedia_file_url(full_path)
                                    if api_url:
                                        src = api_url
                                    else:
                                        src = f'https://upload.wikimedia.org/wikipedia/commons/{full_path}'
                                else:
                                    filename = re.sub(r'^\d+px-', '', file_path)
                                    api_url = self.get_wikipedia_file_url(filename)
                                    if api_url:
                                        src = api_url
                                    else:
                                        src = f'https://upload.wikimedia.org/wikipedia/commons/{filename}'
                        elif '/wiki/File:' in src or '/wiki/Special:FilePath' in src:
                            # Convert Wikipedia file page URL to direct file URL
                            if '/Special:FilePath/' in src:
                                file_path = src.split('/Special:FilePath/')[-1]
                                src = f'https://upload.wikimedia.org/wikipedia/commons/{file_path}'
                        
                        return src
                
                time.sleep(self.throttle_seconds)
                
            except Exception as e:
                logger.warning(f"Error searching for {search_term}: {e}")
                time.sleep(self.throttle_seconds)
                continue
        
        return None
    
    def scrape_teams_from_espn(self) -> List[Dict]:
        """
        Scrape NCAA Division I teams from ESPN's men's college basketball teams page.
        
        Returns:
            List of team dictionaries
        """
        teams = []
        
        espn_url = "https://www.espn.com/mens-college-basketball/teams"
        
        try:
            logger.info(f"Scraping teams from: {espn_url}")
            # ESPN may require specific headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.espn.com/'
            }
            response = self.session.get(espn_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            teams_found = set()  # To avoid duplicates
            
            # Method 1: Look for team links with href pattern
            team_links = soup.find_all('a', href=re.compile(r'/mens-college-basketball/team/_/id/\d+', re.I))
            logger.info(f"Found {len(team_links)} team links")
            
            for link in team_links:
                try:
                    # Extract team name from link text or nearby elements
                    school_name = link.get_text(strip=True)
                    
                    # If no text in link, look for nearby text
                    if not school_name or len(school_name) < 3:
                        parent = link.find_parent()
                        if parent:
                            # Look for h2, h3, or span with team name
                            name_elem = parent.find(['h2', 'h3', 'span'])
                            if name_elem:
                                school_name = name_elem.get_text(strip=True)
                    
                    if not school_name or len(school_name) < 3:
                        continue
                    
                    # Skip if we've already seen this team
                    if school_name.lower() in teams_found:
                        continue
                    teams_found.add(school_name.lower())
                    
                    # Find logo - look in the link or parent container
                    logo_url = None
                    logo_img = link.find('img')
                    
                    if not logo_img:
                        # Look in parent
                        parent = link.find_parent(['div', 'li', 'section'])
                        if parent:
                            logo_img = parent.find('img')
                    
                    if logo_img:
                        logo_url = (logo_img.get('src') or 
                                   logo_img.get('data-src') or 
                                   logo_img.get('data-lazy-src') or
                                   logo_img.get('data-default-src') or
                                   logo_img.get('data-src-default'))
                        
                        if logo_url:
                            # Clean and make absolute
                            if logo_url.startswith('//'):
                                logo_url = 'https:' + logo_url
                            elif logo_url.startswith('/'):
                                logo_url = 'https://a.espncdn.com' + logo_url
                            elif not logo_url.startswith('http'):
                                # ESPN CDN URLs - try to construct proper URL
                                if 'espncdn.com' not in logo_url:
                                    # Extract team ID from link href if possible
                                    href = link.get('href', '')
                                    team_id_match = re.search(r'/id/(\d+)', href)
                                    if team_id_match:
                                        team_id = team_id_match.group(1)
                                        logo_url = f'https://a.espncdn.com/i/teamlogos/ncaa/500/{team_id}.png'
                    
                    # Extract conference from parent structure
                    conference = ""
                    parent = link.find_parent(['div', 'section'])
                    if parent:
                        conf_header = parent.find(['h2', 'h3'], string=re.compile(r'Conference|Conf', re.I))
                        if conf_header:
                            conference = conf_header.get_text(strip=True)
                    
                    team_data = {
                        'school_name': school_name,
                        'team_name': school_name,
                        'conference': conference,
                        'logo_url': logo_url
                    }
                    
                    teams.append(team_data)
                    logger.info(f"Found: {school_name} - Logo: {'Yes' if logo_url else 'No'}")
                    
                except Exception as e:
                    logger.debug(f"Error processing team link: {e}")
                    continue
            
            # Method 2: If we didn't find enough, try looking for images with team logos
            if len(teams) < 100:
                logger.info("Trying alternative method: searching for logo images...")
                logo_images = soup.find_all('img', src=re.compile(r'teamlogos|team-logo|logo', re.I))
                
                for img in logo_images:
                    try:
                        logo_url = (img.get('src') or 
                                   img.get('data-src') or 
                                   img.get('data-lazy-src'))
                        
                        if not logo_url:
                            continue
                        
                        # Make absolute
                        if logo_url.startswith('//'):
                            logo_url = 'https:' + logo_url
                        elif logo_url.startswith('/'):
                            logo_url = 'https://a.espncdn.com' + logo_url
                        
                        # Try to find associated team name
                        parent = img.find_parent(['a', 'div', 'li'])
                        school_name = None
                        
                        if parent:
                            # Look for text in parent or nearby
                            name_elem = parent.find(['h2', 'h3', 'span', 'a'])
                            if name_elem:
                                school_name = name_elem.get_text(strip=True)
                        
                        # Try alt text
                        if not school_name:
                            school_name = img.get('alt', '').strip()
                        
                        if school_name and len(school_name) > 3:
                            if school_name.lower() not in teams_found:
                                teams_found.add(school_name.lower())
                                team_data = {
                                    'school_name': school_name,
                                    'team_name': school_name,
                                    'conference': '',
                                    'logo_url': logo_url
                                }
                                teams.append(team_data)
                                logger.info(f"Found (alt): {school_name}")
                    
                    except Exception as e:
                        logger.debug(f"Error processing logo image: {e}")
                        continue
            
            logger.info(f"Found {len(teams)} teams from ESPN")
            
        except Exception as e:
            logger.error(f"Error scraping ESPN: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        return teams
    
    def scrape_teams_from_wikipedia(self) -> List[Dict]:
        """
        Scrape NCAA Division I teams from Wikipedia list pages.
        
        Returns:
            List of team dictionaries
        """
        teams = []
        
        # Wikipedia page with list of NCAA D1 men's basketball programs
        list_urls = [
            "https://en.wikipedia.org/wiki/List_of_NCAA_Division_I_men%27s_basketball_programs",
        ]
        
        for list_url in list_urls:
            try:
                logger.info(f"Scraping teams from: {list_url}")
                response = self.session.get(list_url, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all tables with team information
                tables = soup.find_all('table', class_='wikitable')
                
                for table in tables:
                    rows = table.find_all('tr')[1:]  # Skip header
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) < 2:
                            continue
                        
                        # Extract school name (usually first column)
                        school_cell = cells[0]
                        school_link = school_cell.find('a')
                        if school_link:
                            school_name = school_link.get_text(strip=True)
                        else:
                            school_name = school_cell.get_text(strip=True)
                        
                        if not school_name or len(school_name) < 3:
                            continue
                        
                        # Extract team name/nickname (usually second column)
                        team_name = school_name  # Default
                        if len(cells) > 1:
                            team_cell = cells[1]
                            team_text = team_cell.get_text(strip=True)
                            if team_text:
                                team_name = team_text
                        
                        # Extract conference if available
                        conference = ""
                        if len(cells) > 2:
                            conf_cell = cells[2]
                            conf_link = conf_cell.find('a')
                            if conf_link:
                                conference = conf_link.get_text(strip=True)
                            else:
                                conference = conf_cell.get_text(strip=True)
                        
                        # Look for logo in the row (prefer athletics logos over seals)
                        logo_url = None
                        # First, try to find images that are likely athletics logos
                        all_imgs = row.find_all('img')
                        logo_img = None
        
                        # Prioritize: look for images with "logo" in alt text (not "seal")
                        for img in all_imgs:
                            alt_text = img.get('alt', '').lower()
                            if 'logo' in alt_text and 'seal' not in alt_text:
                                logo_img = img
                                break
        
                        # If no logo found, take any image that's not a seal
                        if not logo_img:
                            for img in all_imgs:
                                alt_text = img.get('alt', '').lower()
                                if 'seal' not in alt_text and 'emblem' not in alt_text:
                                    logo_img = img
                                    break
        
                        # Last resort: any image
                        if not logo_img and all_imgs:
                            logo_img = all_imgs[0]
        
                        if logo_img:
                            # Try data-file-url first (full resolution)
                            if logo_img.get('data-file-url'):
                                src = logo_img['data-file-url']
                                if src.startswith('//'):
                                    src = 'https:' + src
                                elif not src.startswith('http'):
                                    src = 'https://en.wikipedia.org' + src
                                logo_url = src
                            elif logo_img.get('src'):
                                src = logo_img['src']
                                if src.startswith('//'):
                                    src = 'https:' + src
                                elif src.startswith('/'):
                                    src = 'https://en.wikipedia.org' + src
                                
                                # Get higher resolution version (remove thumbnail dimensions)
                                if '/thumb/' in src:
                                    # Wikipedia thumbnail format: /thumb/path/to/file.ext/widthpx-file.ext
                                    # Example: /thumb/a/a1/Logo.svg/250px-Logo.svg
                                    # We want: https://upload.wikimedia.org/wikipedia/commons/a/a1/Logo.svg
                                    parts = src.split('/thumb/')
                                    if len(parts) > 1:
                                        file_path = parts[1]
                                        # Remove the thumbnail dimension suffix (everything after the last /)
                                        if '/' in file_path:
                                            # Split by / and take everything except the last part
                                            path_parts = file_path.split('/')
                                            # The last part is the dimensioned filename, remove it
                                            original_path = '/'.join(path_parts[:-1])
                                            # Get the original filename from the dimensioned one
                                            dimensioned_filename = path_parts[-1]
                                            original_filename = re.sub(r'^\d+px-', '', dimensioned_filename)
                                            # Construct the direct Wikimedia Commons URL
                                            full_path = f"{original_path}/{original_filename}"
                                            # Try to get URL via API first
                                            api_url = self.get_wikipedia_file_url(full_path)
                                            if api_url:
                                                logo_url = api_url
                                            else:
                                                logo_url = f'https://upload.wikimedia.org/wikipedia/commons/{full_path}'
                                        else:
                                            # Single filename case
                                            filename = re.sub(r'^\d+px-', '', file_path)
                                            api_url = self.get_wikipedia_file_url(filename)
                                            if api_url:
                                                logo_url = api_url
                                            else:
                                                logo_url = f'https://upload.wikimedia.org/wikipedia/commons/{filename}'
                                else:
                                    # If it's already a direct URL, use it; otherwise convert
                                    if src.startswith('https://upload.wikimedia.org'):
                                        logo_url = src
                                    elif '/wiki/File:' in src or '/wiki/Special:FilePath' in src:
                                        # Extract filename and use direct URL
                                        filename = src.split('/')[-1]
                                        # Try to extract path from Special:FilePath URL
                                        if '/Special:FilePath/' in src:
                                            file_path = src.split('/Special:FilePath/')[-1]
                                            logo_url = f'https://upload.wikimedia.org/wikipedia/commons/{file_path}'
                                        else:
                                            logo_url = src
                                    else:
                                        logo_url = src
                        
                        # If no logo in table, try to get from school's Wikipedia page
                        if not logo_url:
                            # First try searching for athletics logo files directly
                            logo_url = self.search_athletics_logo_file(school_name, team_name)
                            # If that fails, try the general Wikipedia page search
                            if not logo_url:
                                logo_url = self.get_wikipedia_logo_url(team_name, school_name)
                        
                        team_data = {
                            'school_name': school_name,
                            'team_name': team_name,
                            'conference': conference,
                            'logo_url': logo_url
                        }
                        
                        teams.append(team_data)
                        logger.info(f"Found: {school_name} ({team_name})")
                        
                        time.sleep(self.throttle_seconds)
                
                logger.info(f"Found {len(teams)} teams from {list_url}")
                
            except Exception as e:
                logger.error(f"Error scraping {list_url}: {e}")
                continue
        
        return teams
    
    def get_wikipedia_file_url(self, file_path: str) -> Optional[str]:
        """
        Get the direct file URL from Wikipedia using the API.
        
        Args:
            file_path: File path (e.g., "a/a1/Logo.svg")
            
        Returns:
            Direct file URL or None
        """
        try:
            # Extract filename from path
            filename = file_path.split('/')[-1]
            # URL encode the filename
            from urllib.parse import quote
            encoded_filename = quote(filename, safe='')
            
            # Use Wikipedia API to get file info
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'titles': f'File:{filename}',
                'prop': 'imageinfo',
                'iiprop': 'url'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                imageinfo = page_data.get('imageinfo', [])
                if imageinfo and len(imageinfo) > 0:
                    return imageinfo[0].get('url')
            
        except Exception as e:
            logger.debug(f"Could not get file URL from API for {file_path}: {e}")
        
        return None
    
    def download_image(self, url: str, max_retries: int = 3) -> Optional[bytes]:
        """
        Download an image from a URL with retries.
        If the URL fails and it's a Wikipedia URL, try to get the correct URL via API.
        
        Args:
            url: Image URL
            max_retries: Maximum number of retry attempts
            
        Returns:
            Image bytes or None if download failed
        """
        original_url = url
        
        for attempt in range(max_retries):
            try:
                # If this is a Wikipedia upload URL that failed, try API lookup
                if attempt > 0 and 'upload.wikimedia.org' in url:
                    # Try to extract file path and use API
                    if '/wikipedia/commons/' in url:
                        file_path = url.split('/wikipedia/commons/')[-1]
                        api_url = self.get_wikipedia_file_url(file_path)
                        if api_url:
                            url = api_url
                            logger.debug(f"Using API URL: {url}")
                
                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Check if it's an image or SVG
                content_type = response.headers.get('Content-Type', '').lower()
                # Accept image types and SVG
                if not (content_type.startswith('image/') or 
                        'svg' in content_type or 
                        url.lower().endswith('.svg') or
                        url.lower().endswith('.svgz')):
                    # If no content-type header, check URL extension
                    if not content_type:
                        if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')):
                            pass  # Likely an image
                        else:
                            logger.warning(f"URL {url} may not be an image (Content-Type: {content_type})")
                            # Still try to download it
                    else:
                        logger.warning(f"URL {url} does not appear to be an image (Content-Type: {content_type})")
                        return None
                
                return response.content
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {url}: {e}")
                    time.sleep(2 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to download {url} after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def process_image(self, image_data: bytes, filename: str) -> bool:
        """
        Process and save an image (resize, convert to PNG).
        For SVG files, saves as SVG if Pillow can't process them.
        
        Args:
            image_data: Raw image bytes
            filename: Output filename (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if it's an SVG file
            if image_data.startswith(b'<svg') or image_data.startswith(b'<?xml'):
                # Save SVG as-is (Tableau can use SVG files)
                output_path = self.logos_dir / f"{filename}.svg"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                logger.debug(f"Saved SVG file: {filename}.svg")
                return True
            
            # Try to open as image with Pillow
            try:
                img = Image.open(io.BytesIO(image_data))
            except Exception as e:
                # If it's not a standard image format, try saving as-is
                logger.warning(f"Could not open image with Pillow for {filename}, trying to save as-is: {e}")
                # Try to determine extension from first bytes
                if image_data.startswith(b'\x89PNG'):
                    ext = '.png'
                elif image_data.startswith(b'\xff\xd8'):
                    ext = '.jpg'
                elif image_data.startswith(b'GIF'):
                    ext = '.gif'
                else:
                    ext = '.png'  # Default
                
                output_path = self.logos_dir / f"{filename}{ext}"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return True
            
            # Convert RGBA if needed (for transparency)
            if img.mode not in ('RGBA', 'RGB', 'LA', 'L'):
                if img.mode == 'P' and 'transparency' in img.info:
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
            
            # Resize if needed
            if max(img.size) > self.max_size:
                img.thumbnail((self.max_size, self.max_size), Image.Resampling.LANCZOS)
            
            # Save as PNG
            output_path = self.logos_dir / f"{filename}.png"
            img.save(output_path, 'PNG', optimize=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing image for {filename}: {e}")
            return False
    
    def download_all_logos(self):
        """Download and process all team logos using multiprocessing."""
        logger.info(f"Starting download of {len(self.teams)} team logos using {self.num_workers} parallel workers...")
        
        # Prepare arguments for worker function
        worker_args = []
        for idx, team in enumerate(self.teams, 1):
            worker_args.append((
                idx,
                len(self.teams),
                team,
                str(self.logos_dir),
                self.max_size,
                self.throttle_seconds
            ))
        
        # Use multiprocessing Pool with specified number of workers
        with Pool(processes=self.num_workers) as pool:
            results = pool.starmap(download_logo_worker, worker_args)
        
        # Process results
        successful = 0
        failed = 0
        
        for idx, result in enumerate(results):
            team = self.teams[idx]
            if result['success']:
                team['logo_filename'] = result['filename']
                successful += 1
                logger.info(f"[OK] Successfully saved logo for {team['school_name']}")
            else:
                self.missing_logos.append({
                    **team,
                    'error': result['error']
                })
                failed += 1
        
        logger.info(f"Download complete: {successful} successful, {failed} failed")
    
    def save_metadata(self):
        """Save team metadata to CSV."""
        metadata_path = self.metadata_dir / "team_logo_mapping.csv"
        
        with open(metadata_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['school_name', 'team_name', 'conference', 'logo_filename', 'logo_source_url']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for team in self.teams:
                if 'logo_filename' in team:
                    writer.writerow({
                        'school_name': team['school_name'],
                        'team_name': team['team_name'],
                        'conference': team.get('conference', ''),
                        'logo_filename': team.get('logo_filename', ''),
                        'logo_source_url': team.get('logo_url', '')
                    })
        
        logger.info(f"Metadata saved to {metadata_path}")
        
        # Save missing logos
        if self.missing_logos:
            missing_path = self.metadata_dir / "missing_logos.csv"
            with open(missing_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['school_name', 'team_name', 'conference', 'logo_source_url', 'error']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for team in self.missing_logos:
                    writer.writerow({
                        'school_name': team['school_name'],
                        'team_name': team['team_name'],
                        'conference': team.get('conference', ''),
                        'logo_source_url': team.get('logo_url', ''),
                        'error': team.get('error', 'Unknown error')
                    })
            
            logger.info(f"Missing logos list saved to {missing_path}")
    
    def create_zip_file(self):
        """Create a zip file with all logos for Tableau."""
        zip_path = self.out_dir / "ncaa_d1_basketball_logos_for_tableau.zip"
        
        logger.info(f"Creating zip file: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all logo files (PNG, SVG, JPG, etc.)
            image_extensions = ['*.png', '*.svg', '*.jpg', '*.jpeg', '*.gif', '*.webp']
            for ext in image_extensions:
                for logo_file in self.logos_dir.glob(ext):
                    zipf.write(logo_file, f"logos/{logo_file.name}")
                    logger.debug(f"Added {logo_file.name} to zip")
            
            # Add metadata
            metadata_file = self.metadata_dir / "team_logo_mapping.csv"
            if metadata_file.exists():
                zipf.write(metadata_file, "metadata/team_logo_mapping.csv")
        
        logger.info(f"[OK] Zip file created: {zip_path}")
        logger.info(f"  Extract this to: My Tableau Repository/Shapes/NCAA_D1_College_Basketball_Logos/")
    
    def run(self):
        """Run the complete scraping process."""
        logger.info("=" * 60)
        logger.info("NCAA Division I Basketball Logo Scraper")
        logger.info("=" * 60)
        
        # Step 1: Scrape team list
        logger.info("Step 1: Scraping team list from ESPN...")
        self.teams = self.scrape_teams_from_espn()
        logger.info(f"Found {len(self.teams)} teams")
        
        if not self.teams:
            logger.error("No teams found! Exiting.")
            return
        
        # Step 2: Download logos
        logger.info("Step 2: Downloading and processing logos...")
        self.download_all_logos()
        
        # Step 3: Save metadata
        logger.info("Step 3: Saving metadata...")
        self.save_metadata()
        
        # Step 4: Create zip file
        logger.info("Step 4: Creating zip file...")
        self.create_zip_file()
        
        logger.info("=" * 60)
        logger.info("Scraping complete!")
        logger.info(f"Output directory: {self.out_dir.absolute()}")
        logger.info("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Scrape NCAA Division I college basketball team logos for Tableau',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_ncaa_d1_logos.py
  python download_ncaa_d1_logos.py --out-dir output --max-size 512 --throttle-seconds 1.0

Output:
  The script will create a zip file at: output/ncaa_d1_basketball_logos_for_tableau.zip
  Extract this to: My Tableau Repository/Shapes/NCAA_D1_College_Basketball_Logos/
        """
    )
    
    parser.add_argument(
        '--out-dir',
        type=str,
        default='output',
        help='Output directory (default: output)'
    )
    
    parser.add_argument(
        '--max-size',
        type=int,
        default=512,
        help='Maximum pixel dimension for logos (default: 512)'
    )
    
    parser.add_argument(
        '--throttle-seconds',
        type=float,
        default=1.0,
        help='Delay between HTTP requests in seconds (default: 1.0, not used with multiprocessing)'
    )
    
    parser.add_argument(
        '--num-workers',
        type=int,
        default=20,
        help='Number of parallel workers for downloading logos (default: 20)'
    )
    
    args = parser.parse_args()
    
    scraper = NCAA_Logo_Scraper(
        out_dir=args.out_dir,
        max_size=args.max_size,
        throttle_seconds=args.throttle_seconds,
        num_workers=args.num_workers
    )
    
    try:
        scraper.run()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

