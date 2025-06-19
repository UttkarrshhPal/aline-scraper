from typing import List
import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class ContentCleaner:
    @staticmethod
    def get_site_specific_patterns(url):
        """Get site-specific cleaning patterns"""
        domain = urlparse(url).netloc.lower()
        
        patterns = {
            "realpython.com": {
                "selectors": [
                    "div[class*='article']",
                    ".article-body",
                    ".content-body"
                ],
                "remove": [
                    ".sidebar",
                    ".newsletter-promo",
                    ".related-tutorials",
                    ".share-buttons"
                ],
                "noise_patterns": [
                    r"▼\s+What's your #1 takeaway or favorite thing you learned\?",
                    r"Leave a comment below and let us know\.",
                    r"Free Bonus:",
                ]
            },
            "interviewing.io": {
                "selectors": [
                    ".blog-post-content",
                    "[class*='blogPost']",
                    ".guide-content",
                    ".markdown-content"
                ],
                "remove": [
                    ".author-bio",
                    ".share-buttons",
                    ".newsletter-signup",
                    ".related-posts"
                ],
                "noise_patterns": [
                    r"Share this article",
                    r"Subscribe to our newsletter",
                    r"Related guides"
                ]
            },
            "geeksforgeeks.org": {
                "selectors": [
                    ".article-content",
                    ".interview-exp",
                    ".content-wrapper"
                ],
                "remove": [
                    ".code-block-header",
                    ".recommendedPostsDiv",
                    ".auth-and-rating",
                    ".noIdeasMsg"
                ],
                "noise_patterns": [
                    r"Attention reader!.*?Please take your time",
                    r"Last Updated\s*:\s*\d{2}\s+[A-Za-z]+\s+\d{4}",
                    r"Time Complexity\s*:",
                    r"Space Complexity\s*:"
                ]
            },
            "overreacted.io": {
                "selectors": [
                    "article",
                    ".post-content",
                    ".blog-post"
                ],
                "remove": [
                    ".gatsby-highlight",
                    ".translation-notice",
                    ".date-info"
                ],
                "noise_patterns": [
                    r"Edit on GitHub",
                    r"Follow @dan_abramov",
                    r"This blog is open source\."
                ]
            }
        }
        
        # Default patterns if no specific site match
        default_patterns = {
            "selectors": [
                "article",
                ".content",
                ".post-content",
                ".entry-content",
                "main"
            ],
            "remove": [
                "script",
                "style",
                "nav",
                "header",
                "footer",
                "aside",
                ".sidebar",
                ".navigation",
                ".ad",
                ".advertisement"
            ],
            "noise_patterns": [
                r"Share this:",
                r"Like this:",
                r"Related Posts",
                r"Comments?",
                r"Follow us on",
                r"Subscribe to",
                r"©.*$",
                r"All rights reserved",
                r"Cookie Policy",
                r"Privacy Policy"
            ]
        }
        
        return patterns.get(domain, default_patterns)

    @staticmethod
    def clean_html(html, url):
        """Clean HTML content using site-specific patterns"""
        patterns = ContentCleaner.get_site_specific_patterns(url)
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for selector in patterns["remove"]:
            for element in soup.select(selector):
                element.decompose()
        
        # Extract content using site-specific selectors
        content = None
        for selector in patterns["selectors"]:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element.get_text(separator="\n", strip=True)
                if content and len(content) > 200:
                    break
        
        if not content:
            return None
            
        # Clean up the content
        content = ContentCleaner.clean_text(content, patterns["noise_patterns"])
        return content

    @staticmethod
    def clean_text(text, noise_patterns):
        """Clean extracted text content"""
        if not text:
            return None
            
        # Remove noise patterns
        for pattern in noise_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        
        # General cleanup
        text = re.sub(r"\s+", " ", text)  # Normalize whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)  # Normalize newlines
        text = re.sub(r"(?<=\.) (?=[A-Z])", "\n", text)  # Add newlines between sentences
        
        return text.strip()

    def chunk_content(self, text: str, max_chunk_size: int = 1000, overlap: int = 150) -> List[str]:
        """Chunk content semantically, preserving paragraphs and context overlap."""
        # TODO: Implement semantic chunking
        return []

    def to_markdown(self, text: str) -> str:
        """Convert cleaned text to markdown, preserving headers, lists, code, links, and tables."""
        # TODO: Implement markdown conversion
        return text