"""
Prompt analysis utilities for complexity classification
"""
import re

class PromptAnalyzer:
    """Analyzes prompts to ascertain complexity score before invoking models."""
    
    # Complexity keywords
    COMPLEX_KEYWORDS = [
        "write", "script", "code", "algorithm", "analyze", "compare", 
        "function", "class", "architect", "python", "javascript", "java",
        "c++", "implement", "create", "build", "develop", "explain in detail",
        "comprehensive", "thorough", "step by step", "tutorial", "guide"
    ]
    
    MEDIUM_KEYWORDS = [
        "explain", "describe", "what is", "how to", "why", "when",
        "summarize", "list", "examples", "benefits", "drawbacks"
    ]
    
    @staticmethod
    def classify_complexity(prompt):
        """
        Classifies complexity into 'Simple', 'Medium', 'Complex' 
        and returns a numerical score (1 to 3) + trimmed prompt.
        """
        original_length = len(prompt)
        
        # 1. Prompt Trimming (RAM awareness)
        if original_length > 600:
            trimmed_prompt = prompt[:590] + "... [Trimmed by Cook]"
        else:
            trimmed_prompt = prompt
        
        prompt_lower = prompt.lower()
        length = len(prompt)
        
        # 2. Check for code indicators (usually complex)
        code_indicators = ["```", "def ", "class ", "function(", "=>", "import "]
        has_code = any(indicator in prompt for indicator in code_indicators)
        
        # 3. Count keywords
        complex_count = sum(1 for kw in PromptAnalyzer.COMPLEX_KEYWORDS if kw in prompt_lower)
        medium_count = sum(1 for kw in PromptAnalyzer.MEDIUM_KEYWORDS if kw in prompt_lower)
        
        # 4. Classification logic
        if has_code or complex_count >= 2 or length > 300:
            return 3, "Complex", trimmed_prompt
        elif complex_count == 1 or medium_count >= 2 or length >= 100:
            return 2, "Medium", trimmed_prompt
        else:
            return 1, "Simple", trimmed_prompt
    
    @staticmethod
    def estimate_tokens(text):
        """Rough estimate of token count"""
        # Very rough estimate: ~4 characters per token for English
        return len(text) // 4
    
    @staticmethod
    def extract_keywords(prompt, max_keywords=5):
        """Extract main keywords from prompt"""
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'what', 'when', 'where', 'which'}
        keywords = [w for w in words if w not in stopwords]
        
        # Return unique keywords
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
        
        return unique_keywords[:max_keywords]