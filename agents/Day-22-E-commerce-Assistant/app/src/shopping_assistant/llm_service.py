"""
LLM Service for AI-powered shopping assistance
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from .models import Product, Review, RecommendationRequest, UserPreferences

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered features"""
    
    def __init__(self):
        logger.info("Initializing LLMService...")
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"OpenAI API key loaded: {'Yes' if self.api_key else 'No'}")
        if self.api_key:
            logger.info(f"API key starts with: {self.api_key[:10]}..." if len(self.api_key) > 10 else "API key too short")
        
        self.model = "gpt-3.5-turbo"
        self.client = None
        
        # Only initialize OpenAI if API key is available
        if self.api_key:
            try:
                logger.info("Attempting to import OpenAI library...")
                from openai import OpenAI
                logger.info("OpenAI library imported successfully")
                
                logger.info("Initializing OpenAI client...")
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
                
            except ImportError as e:
                logger.error(f"OpenAI library not available: {e}")
                self.client = None
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            logger.warning("No OpenAI API key found - will use demo mode")
    
    def _is_available(self) -> bool:
        """Check if LLM service is available"""
        available = self.client is not None and self.api_key is not None
        logger.debug(f"LLM service available: {available}")
        return available
    
    def parse_query(self, prompt: str) -> Dict[str, Any]:
        """Parse natural language shopping query"""
        logger.info("Starting query parsing...")
        
        if not self._is_available():
            logger.warning("LLM service not available - returning demo parsing")
            # Return basic parsing for demo mode
            return {
                "query_type": "search",
                "category": "electronics",
                "features": [],
                "brands": [],
                "sort_by": "relevance"
            }
        
        logger.info("LLM service available - making OpenAI API call...")
        
        try:
            logger.debug(f"Sending prompt to OpenAI: {prompt[:100]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a shopping query parser. Extract structured information from natural language shopping queries and return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            logger.info("OpenAI API call successful")
            content = response.choices[0].message.content
            logger.debug(f"OpenAI response: {content[:200]}...")
            
            # Try to extract JSON from the response
            try:
                result = json.loads(content)
                logger.info("Successfully parsed JSON response from OpenAI")
                return result
            except json.JSONDecodeError:
                logger.warning("Direct JSON parsing failed, trying to extract from code blocks")
                # If direct JSON parsing fails, extract from code blocks
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from code blocks")
                    return result
                else:
                    logger.error("Could not extract JSON from OpenAI response")
                    return {}
        except Exception as e:
            logger.error(f"Error parsing query with OpenAI: {e}")
            return {}
    
    def enhance_recommendation_query(self, request: RecommendationRequest, 
                                   user_prefs: Optional[UserPreferences]) -> str:
        """Enhance recommendation query with user context"""
        logger.info("Starting recommendation query enhancement...")
        
        if not self._is_available():
            logger.warning("LLM service not available - using basic enhancement")
            # Return enhanced query for demo mode
            enhanced = request.description
            if request.budget:
                enhanced += f" under ${request.budget}"
            if request.preferred_brands:
                enhanced += f" from {' or '.join(request.preferred_brands)}"
            return enhanced
        
        logger.info("LLM service available - enhancing query with OpenAI...")
        
        prompt = f"""
        Create an enhanced search query for product recommendations based on:
        
        Original description: {request.description}
        Budget: {request.budget or 'No specific budget'}
        Preferred brands: {', '.join(request.preferred_brands) if request.preferred_brands else 'None'}
        Must-have features: {', '.join(request.must_have_features) if request.must_have_features else 'None'}
        """
        
        if user_prefs:
            prompt += f"""
        User preferences:
        - Preferred brands: {', '.join(user_prefs.preferred_brands)}
        - Preferred categories: {', '.join(user_prefs.preferred_categories)}
        - Price range: {user_prefs.price_range}
        - Favorite stores: {', '.join(user_prefs.favorite_stores)}
        """
        
        prompt += "\nGenerate a detailed search query that incorporates all relevant information to find the best products for this user."
        
        try:
            logger.debug("Making OpenAI API call for query enhancement...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a shopping assistant. Create detailed search queries for finding the best products based on user requirements and preferences."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            enhanced_query = response.choices[0].message.content.strip()
            logger.info(f"Successfully enhanced query with OpenAI: {enhanced_query[:100]}...")
            return enhanced_query
            
        except Exception as e:
            logger.error(f"Error enhancing query with OpenAI: {e}")
            return request.description
    
    def analyze_comparison(self, products: List[Product], 
                         comparison_table: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], str]:
        """Analyze product comparison and determine winner"""
        logger.info("Starting product comparison analysis...")
        
        if not self._is_available():
            logger.warning("LLM service not available - using demo analysis")
            # Return demo analysis
            if products:
                # Simple demo logic: pick the one with best price/rating ratio
                best_product = None
                best_score = 0
                
                for product in products:
                    score = 0
                    if product.rating:
                        score += product.rating * 2
                    if product.price:
                        # Lower price is better, but normalize
                        score += max(0, (1000 - product.price) / 100)
                    
                    if score > best_score:
                        best_score = score
                        best_product = product
                
                winner = best_product.id or best_product.title if best_product else None
                summary = f"Based on price and rating analysis, {best_product.title if best_product else 'the first product'} offers the best value. "
                summary += "Consider factors like brand reputation, specific features, and warranty when making your final decision."
                
                return winner, summary
            
            return None, "No products to compare in demo mode."
        
        logger.info("LLM service available - analyzing comparison with OpenAI...")
        
        # Full LLM analysis code continues...
        products_info = []
        for product in products:
            info = {
                "title": product.title,
                "price": product.price,
                "rating": product.rating,
                "features": product.features,
                "brand": product.brand
            }
            products_info.append(info)
        
        prompt = f"""
        Analyze this product comparison and determine the best choice:
        
        Products: {json.dumps(products_info, indent=2)}
        
        Comparison data: {json.dumps(comparison_table, indent=2)}
        
        Consider:
        1. Value for money (price vs features)
        2. User ratings and reviews
        3. Feature completeness
        4. Brand reputation
        
        Provide:
        1. Winner (product title)
        2. Detailed explanation of why this product is the best choice
        3. Pros and cons of each product
        """
        
        try:
            logger.debug("Making OpenAI API call for comparison analysis...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product comparison expert. Analyze products objectively and provide detailed recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            logger.info("Successfully analyzed comparison with OpenAI")
            
            # Extract winner (simple approach - look for product title in response)
            winner = None
            for product in products:
                if product.title.lower() in content.lower():
                    winner = product.id or product.title
                    break
            
            return winner, content
        except Exception as e:
            logger.error(f"Error analyzing comparison with OpenAI: {e}")
            return None, "Unable to analyze comparison at this time."
    
    def summarize_reviews(self, reviews: List[Review]) -> Dict[str, Any]:
        """Summarize product reviews using LLM"""
        logger.info(f"Starting review summarization for {len(reviews)} reviews...")
        
        if not reviews:
            logger.warning("No reviews provided for summarization")
            return {
                "pros": [],
                "cons": [],
                "themes": [],
                "summary": "No reviews available."
            }
        
        if not self._is_available():
            logger.warning("LLM service not available - using demo summary")
            # Return demo summary
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            
            demo_pros = ["Good quality", "Fast shipping", "Good value for money"]
            demo_cons = ["Some quality issues", "Limited features"] if avg_rating < 4 else ["Minor issues"]
            demo_themes = ["Quality", "Value", "Performance"]
            
            return {
                "pros": demo_pros,
                "cons": demo_cons,
                "themes": demo_themes,
                "summary": f"Based on {len(reviews)} reviews with an average rating of {avg_rating:.1f}/5, customers generally find this product {'excellent' if avg_rating >= 4.5 else 'good' if avg_rating >= 4 else 'decent'}."
            }
        
        logger.info("LLM service available - summarizing reviews with OpenAI...")
        
        # Full LLM review analysis continues...
        review_texts = []
        for review in reviews[:20]:  # Limit to avoid token limits
            review_texts.append({
                "rating": review.rating,
                "content": review.content[:500]  # Truncate long reviews
            })
        
        prompt = f"""
        Summarize these product reviews and extract key insights:
        
        Reviews: {json.dumps(review_texts, indent=2)}
        
        Provide a JSON response with:
        1. "pros": List of positive aspects mentioned in reviews
        2. "cons": List of negative aspects or complaints
        3. "themes": Common themes or topics discussed
        4. "summary": Overall summary of customer sentiment
        
        Focus on the most frequently mentioned points and overall sentiment.
        """
        
        try:
            logger.debug("Making OpenAI API call for review summarization...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a review analyst. Extract key insights from customer reviews and provide structured summaries in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            logger.info("Successfully summarized reviews with OpenAI")
            
            # Try to parse JSON response
            try:
                result = json.loads(content)
                logger.info("Successfully parsed JSON response from review summarization")
                return result
            except json.JSONDecodeError:
                logger.warning("Direct JSON parsing failed for review summary, trying code blocks")
                # Extract JSON from code blocks if needed
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    logger.info("Successfully extracted JSON from code blocks for review summary")
                    return result
                else:
                    logger.error("Could not extract JSON from review summary response")
                    return {
                        "pros": [],
                        "cons": [],
                        "themes": [],
                        "summary": content
                    }
        except Exception as e:
            logger.error(f"Error summarizing reviews with OpenAI: {e}")
            return {
                "pros": [],
                "cons": [],
                "themes": [],
                "summary": "Unable to summarize reviews at this time."
            }
    
    def generate_product_description(self, product: Product) -> str:
        """Generate an enhanced product description"""
        if not self._is_available():
            # Return demo description
            return f"{product.title} - A quality product with excellent features and good value for money. Highly rated by customers."
        
        # Full LLM description generation continues...
        prompt = f"""
        Create an engaging product description for:
        
        Title: {product.title}
        Price: ${product.price}
        Brand: {product.brand}
        Features: {', '.join(product.features) if product.features else 'None listed'}
        Rating: {product.rating}/5 ({product.review_count} reviews)
        
        Write a compelling description that highlights key benefits and helps users understand why they should consider this product.
        Keep it concise but informative (2-3 paragraphs).
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product copywriter. Create engaging and informative product descriptions that help customers make informed decisions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating description: {e}")
            return product.description or "No description available."
    
    def extract_product_features(self, description: str) -> List[str]:
        """Extract key features from product description"""
        if not self._is_available():
            # Return demo features
            return ["High Quality", "Durable", "User Friendly", "Good Value"]
        
        # Full LLM feature extraction continues...
        prompt = f"""
        Extract key product features from this description:
        
        {description}
        
        Return a JSON list of specific, important features that would help someone compare products.
        Focus on concrete features, specifications, and benefits.
        Example: ["Wireless connectivity", "10-hour battery life", "Water resistant", "Touch screen"]
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product analyst. Extract key features from product descriptions and return them as a JSON list."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from code blocks if needed
                import re
                json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                else:
                    return []
        except Exception as e:
            print(f"Error extracting features: {e}")
            return [] 