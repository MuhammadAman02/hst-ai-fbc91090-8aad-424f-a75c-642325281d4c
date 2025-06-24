"""
Advanced Fashion Asset Management System for ZARA E-commerce Store
Provides professional fashion imagery with contextual categories and fallback systems
"""

import hashlib
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ImageAsset:
    """Professional image asset with multiple sources and metadata"""
    primary_url: str
    fallback_url: str
    alt_text: str
    category: str
    keywords: List[str]

class FashionAssetManager:
    """Advanced fashion retail image management system"""
    
    FASHION_CATEGORIES = {
        "hero": {
            "keywords": ["fashion", "style", "elegant", "modern", "luxury", "boutique"],
            "dimensions": "1920x800",
            "style": "lifestyle"
        },
        "women": {
            "keywords": ["woman-fashion", "female-model", "dress", "elegant", "style", "chic"],
            "dimensions": "800x1000",
            "style": "portrait"
        },
        "men": {
            "keywords": ["man-fashion", "male-model", "suit", "casual", "style", "modern"],
            "dimensions": "800x1000", 
            "style": "portrait"
        },
        "kids": {
            "keywords": ["kids-fashion", "children", "playful", "colorful", "cute", "family"],
            "dimensions": "800x800",
            "style": "lifestyle"
        },
        "accessories": {
            "keywords": ["accessories", "jewelry", "bags", "shoes", "watches", "luxury"],
            "dimensions": "600x600",
            "style": "product"
        },
        "lifestyle": {
            "keywords": ["lifestyle", "urban", "street-style", "casual", "everyday", "natural"],
            "dimensions": "1200x800",
            "style": "environmental"
        },
        "products": {
            "keywords": ["clothing", "fashion-items", "apparel", "garments", "style", "trendy"],
            "dimensions": "600x800",
            "style": "product"
        }
    }
    
    SEASONAL_THEMES = {
        "spring": ["spring", "fresh", "bright", "floral", "light"],
        "summer": ["summer", "beach", "sunny", "vacation", "casual"],
        "autumn": ["autumn", "cozy", "warm", "layers", "earth-tones"],
        "winter": ["winter", "elegant", "formal", "sophisticated", "luxury"]
    }
    
    def __init__(self):
        """Initialize the fashion asset manager"""
        self.base_unsplash_url = "https://source.unsplash.com"
        self.base_picsum_url = "https://picsum.photos"
        self.current_season = self._get_current_season()
    
    def _get_current_season(self) -> str:
        """Determine current season for contextual imagery"""
        import datetime
        month = datetime.datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"
    
    def _generate_seed(self, category: str, index: int = 0) -> int:
        """Generate consistent seed for reproducible images"""
        seed_string = f"zara_{category}_{index}_{self.current_season}"
        return int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16) % 10000
    
    def get_hero_images(self, theme: str = "fashion", count: int = 3) -> List[ImageAsset]:
        """Get hero banner images for main carousel"""
        images = []
        hero_config = self.FASHION_CATEGORIES["hero"]
        seasonal_keywords = self.SEASONAL_THEMES.get(self.current_season, [])
        
        for i in range(count):
            # Combine base keywords with seasonal themes
            all_keywords = hero_config["keywords"] + seasonal_keywords
            keyword = all_keywords[i % len(all_keywords)]
            seed = self._generate_seed("hero", i)
            
            primary_url = f"{self.base_unsplash_url}/{hero_config['dimensions']}/?{keyword}&sig={seed}"
            fallback_url = f"{self.base_picsum_url}/{hero_config['dimensions']}?random={seed}"
            
            images.append(ImageAsset(
                primary_url=primary_url,
                fallback_url=fallback_url,
                alt_text=f"ZARA {self.current_season} collection - {keyword} fashion",
                category="hero",
                keywords=[keyword] + seasonal_keywords
            ))
        
        return images
    
    def get_category_image(self, category: str, index: int = 0) -> str:
        """Get category showcase image"""
        if category not in self.FASHION_CATEGORIES:
            category = "products"  # Default fallback
        
        config = self.FASHION_CATEGORIES[category]
        keyword = config["keywords"][index % len(config["keywords"])]
        seed = self._generate_seed(category, index)
        
        return f"{self.base_unsplash_url}/{config['dimensions']}/?{keyword}&sig={seed}"
    
    def get_product_images(self, product_category: str, count: int = 4) -> List[ImageAsset]:
        """Get product images for galleries"""
        images = []
        
        # Map product categories to image categories
        category_mapping = {
            "dresses": "women",
            "tops": "women", 
            "bottoms": "women",
            "suits": "men",
            "shirts": "men",
            "pants": "men",
            "kids": "kids",
            "accessories": "accessories"
        }
        
        img_category = category_mapping.get(product_category.lower(), "products")
        config = self.FASHION_CATEGORIES[img_category]
        
        for i in range(count):
            keyword = config["keywords"][i % len(config["keywords"])]
            seed = self._generate_seed(f"{img_category}_{product_category}", i)
            
            primary_url = f"{self.base_unsplash_url}/{config['dimensions']}/?{keyword}&sig={seed}"
            fallback_url = f"{self.base_picsum_url}/{config['dimensions']}?random={seed}"
            
            images.append(ImageAsset(
                primary_url=primary_url,
                fallback_url=fallback_url,
                alt_text=f"ZARA {product_category} - {keyword}",
                category=img_category,
                keywords=[keyword, product_category]
            ))
        
        return images
    
    def get_lifestyle_images(self, context: str = "urban", count: int = 6) -> List[ImageAsset]:
        """Get lifestyle and environmental images"""
        images = []
        lifestyle_config = self.FASHION_CATEGORIES["lifestyle"]
        
        contexts = {
            "urban": ["city", "street", "urban", "modern", "metropolitan"],
            "casual": ["casual", "everyday", "relaxed", "comfortable", "natural"],
            "professional": ["business", "office", "professional", "formal", "corporate"],
            "evening": ["evening", "elegant", "sophisticated", "glamorous", "luxury"]
        }
        
        context_keywords = contexts.get(context, contexts["urban"])
        
        for i in range(count):
            base_keyword = lifestyle_config["keywords"][i % len(lifestyle_config["keywords"])]
            context_keyword = context_keywords[i % len(context_keywords)]
            combined_keyword = f"{base_keyword}+{context_keyword}"
            
            seed = self._generate_seed(f"lifestyle_{context}", i)
            
            primary_url = f"{self.base_unsplash_url}/{lifestyle_config['dimensions']}/?{combined_keyword}&sig={seed}"
            fallback_url = f"{self.base_picsum_url}/{lifestyle_config['dimensions']}?random={seed}"
            
            images.append(ImageAsset(
                primary_url=primary_url,
                fallback_url=fallback_url,
                alt_text=f"ZARA lifestyle - {context} {base_keyword}",
                category="lifestyle",
                keywords=[base_keyword, context_keyword, context]
            ))
        
        return images
    
    def get_seasonal_collection_images(self, season: Optional[str] = None, count: int = 8) -> List[ImageAsset]:
        """Get seasonal collection showcase images"""
        if not season:
            season = self.current_season
        
        seasonal_keywords = self.SEASONAL_THEMES.get(season, self.SEASONAL_THEMES["spring"])
        base_keywords = ["collection", "fashion", "style", "trendy", "new"]
        
        images = []
        for i in range(count):
            seasonal_keyword = seasonal_keywords[i % len(seasonal_keywords)]
            base_keyword = base_keywords[i % len(base_keywords)]
            combined_keyword = f"{seasonal_keyword}+{base_keyword}+fashion"
            
            seed = self._generate_seed(f"seasonal_{season}", i)
            
            primary_url = f"{self.base_unsplash_url}/800x1000/?{combined_keyword}&sig={seed}"
            fallback_url = f"{self.base_picsum_url}/800x1000?random={seed}"
            
            images.append(ImageAsset(
                primary_url=primary_url,
                fallback_url=fallback_url,
                alt_text=f"ZARA {season} collection - {seasonal_keyword} fashion",
                category="seasonal",
                keywords=[seasonal_keyword, base_keyword, season]
            ))
        
        return images
    
    def get_trust_and_service_images(self) -> Dict[str, ImageAsset]:
        """Get images for trust badges and service highlights"""
        services = {
            "shipping": {
                "keyword": "delivery+fast+shipping",
                "alt": "Fast and reliable shipping"
            },
            "returns": {
                "keyword": "return+exchange+satisfaction", 
                "alt": "Easy returns and exchanges"
            },
            "quality": {
                "keyword": "quality+premium+craftsmanship",
                "alt": "Premium quality materials"
            },
            "customer_service": {
                "keyword": "customer+service+support",
                "alt": "Excellent customer service"
            }
        }
        
        service_images = {}
        for service, config in services.items():
            seed = self._generate_seed(f"service_{service}")
            
            primary_url = f"{self.base_unsplash_url}/400x300/?{config['keyword']}&sig={seed}"
            fallback_url = f"{self.base_picsum_url}/400x300?random={seed}"
            
            service_images[service] = ImageAsset(
                primary_url=primary_url,
                fallback_url=fallback_url,
                alt_text=config["alt"],
                category="service",
                keywords=config["keyword"].split("+")
            )
        
        return service_images
    
    @staticmethod
    def generate_fashion_css() -> str:
        """Generate CSS for professional fashion retail styling"""
        return """
        /* ZARA Fashion Store Styling */
        :root {
            --zara-black: #000000;
            --zara-white: #ffffff;
            --zara-gray-light: #f5f5f5;
            --zara-gray-medium: #cccccc;
            --zara-gray-dark: #666666;
            --zara-accent: #d4af37;
            --font-primary: 'Helvetica Neue', Arial, sans-serif;
            --transition-fast: 0.2s ease;
            --transition-medium: 0.3s ease;
            --shadow-subtle: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-elevated: 0 8px 24px rgba(0,0,0,0.15);
        }
        
        /* Fashion Image Styling */
        .hero-image {
            width: 100%;
            height: 600px;
            object-fit: cover;
            transition: var(--transition-medium);
        }
        
        .product-image {
            width: 100%;
            height: 400px;
            object-fit: cover;
            transition: transform var(--transition-medium);
        }
        
        .product-image:hover {
            transform: scale(1.02);
        }
        
        .category-image {
            width: 100%;
            height: 300px;
            object-fit: cover;
            filter: brightness(0.9);
            transition: filter var(--transition-medium);
        }
        
        .category-image:hover {
            filter: brightness(1);
        }
        
        /* Fashion Card Styling */
        .fashion-card {
            background: var(--zara-white);
            border: none;
            box-shadow: var(--shadow-subtle);
            transition: all var(--transition-medium);
            overflow: hidden;
        }
        
        .fashion-card:hover {
            box-shadow: var(--shadow-elevated);
            transform: translateY(-2px);
        }
        
        /* Product Grid */
        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            padding: 2rem 0;
        }
        
        @media (max-width: 768px) {
            .product-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }
            
            .hero-image {
                height: 300px;
            }
            
            .product-image {
                height: 250px;
            }
        }
        
        /* Fashion Typography */
        .fashion-title {
            font-family: var(--font-primary);
            font-weight: 300;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        .fashion-price {
            font-family: var(--font-primary);
            font-weight: 600;
            color: var(--zara-black);
        }
        
        .fashion-category {
            font-family: var(--font-primary);
            font-size: 0.75rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--zara-gray-dark);
        }
        
        /* Interactive Elements */
        .fashion-button {
            background: var(--zara-black);
            color: var(--zara-white);
            border: none;
            padding: 12px 24px;
            font-family: var(--font-primary);
            font-size: 0.875rem;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all var(--transition-fast);
            cursor: pointer;
        }
        
        .fashion-button:hover {
            background: var(--zara-gray-dark);
            transform: translateY(-1px);
        }
        
        .fashion-button-outline {
            background: transparent;
            color: var(--zara-black);
            border: 1px solid var(--zara-black);
        }
        
        .fashion-button-outline:hover {
            background: var(--zara-black);
            color: var(--zara-white);
        }
        
        /* Color Swatches */
        .color-swatch {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid var(--zara-gray-medium);
            cursor: pointer;
            transition: border-color var(--transition-fast);
        }
        
        .color-swatch:hover,
        .color-swatch.selected {
            border-color: var(--zara-black);
        }
        
        /* Size Selection */
        .size-option {
            min-width: 40px;
            height: 40px;
            border: 1px solid var(--zara-gray-medium);
            background: var(--zara-white);
            color: var(--zara-black);
            font-family: var(--font-primary);
            font-size: 0.875rem;
            cursor: pointer;
            transition: all var(--transition-fast);
        }
        
        .size-option:hover,
        .size-option.selected {
            border-color: var(--zara-black);
            background: var(--zara-black);
            color: var(--zara-white);
        }
        
        /* Loading States */
        .image-loading {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Responsive Images */
        .responsive-image {
            width: 100%;
            height: auto;
            display: block;
        }
        
        /* Image Overlay Effects */
        .image-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(
                to bottom,
                transparent 0%,
                rgba(0,0,0,0.3) 70%,
                rgba(0,0,0,0.7) 100%
            );
            opacity: 0;
            transition: opacity var(--transition-medium);
            display: flex;
            align-items: flex-end;
            padding: 1.5rem;
            color: var(--zara-white);
        }
        
        .fashion-card:hover .image-overlay {
            opacity: 1;
        }
        """