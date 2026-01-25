"""
Sentiment Analysis Module for Ruang Hijau Feedback
Uses NLP techniques for Indonesian text sentiment analysis
"""

import re
from typing import Dict, Tuple

# Indonesian positive and negative word lexicons
POSITIVE_WORDS = {
    # Common positive words
    'bagus', 'baik', 'hebat', 'keren', 'mantap', 'luar biasa', 'sempurna',
    'amazing', 'excellent', 'great', 'good', 'nice', 'wonderful', 'awesome',
    'terima kasih', 'terimakasih', 'makasih', 'thanks', 'thank you',
    'suka', 'senang', 'gembira', 'bahagia', 'puas', 'memuaskan',
    'membantu', 'berguna', 'bermanfaat', 'helpful', 'useful',
    'mudah', 'cepat', 'responsif', 'ramah', 'friendly',
    'recommend', 'rekomen', 'rekomendasi', 'recommended',
    'terbaik', 'best', 'top', 'jempol', 'oke', 'ok', 'okay',
    'sip', 'jos', 'mantul', 'kece', 'ciamik', 'tokcer',
    'berkualitas', 'quality', 'profesional', 'professional',
    'nyaman', 'aman', 'secure', 'safe', 'comfortable',
    'indah', 'cantik', 'elegan', 'menarik', 'interesting',
    'sukses', 'berhasil', 'success', 'lancar', 'smooth',
    'inspired', 'inspiring', 'inspiratif', 'menginspirasi',
    'positif', 'positive', 'optimis', 'optimistic',
    'lanjutkan', 'terus', 'continue', 'pertahankan', 'keep',
    'apresiasi', 'appreciate', 'appreciation'
}

NEGATIVE_WORDS = {
    # Common negative words
    'buruk', 'jelek', 'parah', 'mengecewakan', 'kecewa',
    'bad', 'poor', 'terrible', 'horrible', 'awful', 'worst',
    'lambat', 'slow', 'lelet', 'lemot', 'lag', 'hang',
    'error', 'gagal', 'fail', 'failed', 'rusak', 'broken',
    'sulit', 'susah', 'ribet', 'complicated', 'difficult', 'hard',
    'mahal', 'expensive', 'overpriced', 'kemahalan',
    'tidak berguna', 'useless', 'sampah', 'garbage', 'trash',
    'benci', 'hate', 'tidak suka', 'dislike', 'malas',
    'bosan', 'boring', 'membosankan', 'monoton',
    'tidak responsif', 'unresponsive', 'tidak ramah',
    'tidak profesional', 'unprofessional', 'amatir', 'amateur',
    'mengkhawatirkan', 'worrying', 'bahaya', 'dangerous',
    'tidak aman', 'unsafe', 'insecure', 'rentan', 'vulnerable',
    'komplain', 'keluhan', 'complaint', 'masalah', 'problem', 'issue',
    'bug', 'bugs', 'glitch', 'crash', 'crashed', 'down',
    'tidak puas', 'unsatisfied', 'dissatisfied', 'disappointed',
    'frustasi', 'frustrated', 'frustrating', 'kesal', 'annoyed',
    'menyesal', 'regret', 'sia-sia', 'waste', 'buang waktu',
    'tidak jelas', 'unclear', 'membingungkan', 'confusing',
    'negatif', 'negative', 'pesimis', 'pessimistic',
    'bohong', 'fake', 'palsu', 'penipuan', 'scam', 'tipu'
}

# Intensifier words (increase sentiment strength)
INTENSIFIERS = {
    'sangat', 'very', 'really', 'extremely', 'super', 'banget', 'sekali',
    'amat', 'luar biasa', 'incredibly', 'totally', 'completely',
    'absolutely', 'definitely', 'truly', 'highly', 'paling', 'most'
}

# Negation words (reverse sentiment)
NEGATIONS = {
    'tidak', 'bukan', 'tak', 'tanpa', 'no', 'not', 'never', 'none',
    'belum', 'jangan', 'nggak', 'gak', 'ga', 'enggak', 'kagak',
    "don't", "doesn't", "didn't", "won't", "wouldn't", "shouldn't"
}


class SentimentAnalyzer:
    """
    Indonesian-English Sentiment Analyzer using Lexicon-based approach
    with support for negation and intensifiers
    """
    
    def __init__(self):
        self.positive_words = POSITIVE_WORDS
        self.negative_words = NEGATIVE_WORDS
        self.intensifiers = INTENSIFIERS
        self.negations = NEGATIONS
    
    def preprocess(self, text: str) -> str:
        """Clean and normalize text"""
        # Convert to lowercase
        text = text.lower()
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize(self, text: str) -> list:
        """Split text into words"""
        return text.split()
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of the given text
        
        Returns:
            Dict with keys:
                - sentiment: 'positive', 'negative', or 'neutral'
                - confidence: float between 0 and 1
                - score: raw sentiment score
                - positive_count: number of positive words found
                - negative_count: number of negative words found
        """
        if not text or not text.strip():
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'words_analyzed': 0
            }
        
        # Preprocess text
        clean_text = self.preprocess(text)
        words = self.tokenize(clean_text)
        
        if not words:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'score': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'words_analyzed': 0
            }
        
        positive_score = 0.0
        negative_score = 0.0
        positive_count = 0
        negative_count = 0
        
        # Analyze each word with context
        for i, word in enumerate(words):
            # Check for intensifier before the word
            intensifier = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensifier = 1.5
            
            # Check for negation before the word
            negated = False
            if i > 0 and words[i-1] in self.negations:
                negated = True
            if i > 1 and words[i-2] in self.negations:
                negated = True
            
            # Score the word
            if word in self.positive_words:
                if negated:
                    negative_score += 1.0 * intensifier
                    negative_count += 1
                else:
                    positive_score += 1.0 * intensifier
                    positive_count += 1
            elif word in self.negative_words:
                if negated:
                    positive_score += 1.0 * intensifier
                    positive_count += 1
                else:
                    negative_score += 1.0 * intensifier
                    negative_count += 1
            
            # Check for bigrams (two-word phrases)
            if i < len(words) - 1:
                bigram = f"{word} {words[i+1]}"
                if bigram in self.positive_words:
                    if negated:
                        negative_score += 1.5 * intensifier
                    else:
                        positive_score += 1.5 * intensifier
                elif bigram in self.negative_words:
                    if negated:
                        positive_score += 1.5 * intensifier
                    else:
                        negative_score += 1.5 * intensifier
        
        # Calculate final score
        total_score = positive_score - negative_score
        total_sentiment_words = positive_score + negative_score
        
        # Normalize confidence (0 to 1)
        if total_sentiment_words > 0:
            confidence = min(abs(total_score) / max(total_sentiment_words, 1), 1.0)
        else:
            confidence = 0.0
        
        # Determine sentiment label
        if total_score > 0.5:
            sentiment = 'positive'
        elif total_score < -0.5:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': round(confidence, 3),
            'score': round(total_score, 3),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'words_analyzed': len(words)
        }
    
    def analyze_with_rating(self, text: str, rating: int) -> Dict:
        """
        Enhanced sentiment analysis that considers the user's rating
        
        Args:
            text: The feedback text
            rating: The user's rating (1-5)
        
        Returns:
            Dict with sentiment analysis results
        """
        # Get text-based sentiment
        result = self.analyze(text)
        
        # Adjust sentiment based on rating
        rating_sentiment = 0
        if rating >= 4:
            rating_sentiment = 1  # Positive
        elif rating <= 2:
            rating_sentiment = -1  # Negative
        else:
            rating_sentiment = 0  # Neutral
        
        # Combine text sentiment with rating
        text_score = result['score']
        
        # Weight: 60% text analysis, 40% rating
        combined_score = (text_score * 0.6) + (rating_sentiment * 2 * 0.4)
        
        # Adjust confidence based on agreement between text and rating
        confidence_adjustment = 1.0
        if text_score > 0 and rating >= 4:
            confidence_adjustment = 1.2  # Agreement boosts confidence
        elif text_score < 0 and rating <= 2:
            confidence_adjustment = 1.2
        elif (text_score > 0 and rating <= 2) or (text_score < 0 and rating >= 4):
            confidence_adjustment = 0.8  # Disagreement reduces confidence
        
        adjusted_confidence = min(result['confidence'] * confidence_adjustment, 1.0)
        
        # Final sentiment determination
        if combined_score > 0.3:
            final_sentiment = 'positive'
        elif combined_score < -0.3:
            final_sentiment = 'negative'
        else:
            final_sentiment = 'neutral'
        
        return {
            'sentiment': final_sentiment,
            'confidence': round(adjusted_confidence, 3),
            'score': round(combined_score, 3),
            'text_score': result['score'],
            'rating_factor': rating_sentiment,
            'positive_count': result['positive_count'],
            'negative_count': result['negative_count'],
            'words_analyzed': result['words_analyzed']
        }


# Singleton instance
_analyzer = None

def get_analyzer() -> SentimentAnalyzer:
    """Get or create the sentiment analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


def analyze_sentiment(text: str) -> Dict:
    """
    Convenience function to analyze sentiment of text
    
    Args:
        text: The text to analyze
    
    Returns:
        Dict with sentiment analysis results
    """
    analyzer = get_analyzer()
    return analyzer.analyze(text)


def analyze_feedback_sentiment(text: str, rating: int) -> Dict:
    """
    Convenience function to analyze sentiment of feedback with rating
    
    Args:
        text: The feedback text
        rating: The user's rating (1-5)
    
    Returns:
        Dict with enhanced sentiment analysis results
    """
    analyzer = get_analyzer()
    return analyzer.analyze_with_rating(text, rating)
