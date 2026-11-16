"""
Skill Detector - Automatic skill selection via keyword matching, embedding matching, or hybrid with LLM fallback.
"""
from typing import Optional, Tuple, List
from Langchain.Skills.skillRegistry import SkillRegistry, SkillMetadata


class SkillDetector:
    def __init__(self, registry: SkillRegistry, llm=None):
        self.registry = registry
        self.llm = llm  # For LLM-based classification fallback
        self._embedding_model = None  # Lazy load sentence-transformers if available
        self._skill_embeddings = {}  # Cache skill embeddings
    
    def detect(self, user_input: str, threshold: float = 0.65, detection_mode: str = "keyword") -> Tuple[Optional[SkillMetadata], float, str]:
        """
        Detect the best skill for user input.
        
        Args:
            user_input: The user's input text
            threshold: Minimum confidence threshold (0.0-1.0)
            detection_mode: "keyword" | "embedding" | "hybrid"
        
        Returns: (skill_metadata, confidence, method)
        method: "keyword" | "embedding" | "hybrid" | "llm" | "none"
        """
        if not user_input or not user_input.strip():
            return None, 0.0, "none"
        
        if detection_mode == "keyword":
            # Pure keyword/pattern matching
            skill, confidence = self._keyword_match(user_input, threshold)
            if skill:
                return skill, confidence, "keyword"
        
        elif detection_mode == "embedding":
            # Pure semantic embedding matching
            skill, confidence = self._embedding_match(user_input, threshold)
            if skill:
                return skill, confidence, "embedding"
        
        elif detection_mode == "hybrid":
            # Keyword first, then embedding fallback
            skill, confidence = self._keyword_match(user_input, threshold)
            if skill:
                return skill, confidence, "hybrid-keyword"
            
            skill, confidence = self._embedding_match(user_input, threshold)
            if skill:
                return skill, confidence, "hybrid-embedding"
        
        # 2. LLM classification fallback (if LLM available)
        if self.llm:
            skill, confidence = self._llm_classify(user_input, threshold)
            if skill:
                return skill, confidence, "llm"
        
        return None, 0.0, "none"
    
    def _keyword_match(self, user_input: str, threshold: float) -> Tuple[Optional[SkillMetadata], float]:
        """Keyword-based matching using registry's built-in scoring."""
        skill = self.registry.find_best_match(user_input, threshold)
        if skill:
            # Recalculate exact score for return
            score = self.registry._calculate_match_score(user_input.lower(), skill)
            return skill, score
        return None, 0.0
    
    def _embedding_match(self, user_input: str, threshold: float) -> Tuple[Optional[SkillMetadata], float]:
        """Semantic embedding-based matching using sentence-transformers."""
        try:
            # Lazy load embedding model
            if self._embedding_model is None:
                self._embedding_model = self._load_embedding_model()
                if self._embedding_model is None:
                    return None, 0.0
            
            # Get or compute skill embeddings
            if not self._skill_embeddings:
                self._compute_skill_embeddings()
            
            # Embed user input
            user_embedding = self._embedding_model.encode(user_input, convert_to_tensor=True)
            
            # Find best match
            best_skill = None
            best_score = 0.0
            
            import torch
            for skill_name, skill_embedding in self._skill_embeddings.items():
                skill = self.registry.get_skill(skill_name)
                if not skill:
                    continue
                
                # Cosine similarity
                similarity = torch.nn.functional.cosine_similarity(
                    user_embedding.unsqueeze(0), 
                    skill_embedding.unsqueeze(0)
                ).item()
                
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_skill = skill
            
            if best_skill:
                return best_skill, best_score
            
        except Exception as e:
            print(f"[SkillDetector] Embedding matching error: {e}")
        
        return None, 0.0
    
    def _load_embedding_model(self):
        """Load sentence-transformers model for semantic matching."""
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight, fast model suitable for Raspberry Pi
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[SkillDetector] Loaded embedding model: all-MiniLM-L6-v2")
            return model
        except ImportError:
            print("[SkillDetector] sentence-transformers not installed. Run: pip install sentence-transformers")
            return None
        except Exception as e:
            print(f"[SkillDetector] Failed to load embedding model: {e}")
            return None
    
    def _compute_skill_embeddings(self) -> None:
        """Pre-compute embeddings for all skills."""
        try:
            import torch
            skills = self.registry.get_all_skills()
            for skill in skills:
                # Create rich text representation for embedding
                skill_text = f"{skill.display_name}. {skill.description}"
                if skill.keywords:
                    skill_text += f" Keywords: {', '.join(skill.keywords)}"
                if skill.intent_patterns:
                    skill_text += f" Patterns: {', '.join(skill.intent_patterns)}"
                
                embedding = self._embedding_model.encode(skill_text, convert_to_tensor=True)
                self._skill_embeddings[skill.name] = embedding
            
            print(f"[SkillDetector] Computed embeddings for {len(self._skill_embeddings)} skills")
        except Exception as e:
            print(f"[SkillDetector] Error computing skill embeddings: {e}")
    
    def _llm_classify(self, user_input: str, threshold: float) -> Tuple[Optional[SkillMetadata], float]:
        """Use LLM to classify which skill best matches the user input."""
        try:
            skills = self.registry.get_all_skills()
            if not skills:
                return None, 0.0
            
            # Build skill descriptions for LLM
            skill_descriptions = []
            for skill in skills:
                desc = f"- {skill.name}: {skill.description}"
                if skill.keywords:
                    desc += f" (keywords: {', '.join(skill.keywords[:5])})"
                skill_descriptions.append(desc)
            
            prompt = f"""Given the user input, select the most appropriate skill from the list below.
Return ONLY the skill name (exact name from list) and a confidence score 0.0-1.0.
If no skill matches well, return "NONE" and 0.0.

User Input: "{user_input}"

Available Skills:
{chr(10).join(skill_descriptions)}

Response format: SKILL_NAME|CONFIDENCE
Example: git-push|0.85"""
            
            # Use the LLM to classify
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            content = content.strip()
            if "|" in content:
                skill_name, conf_str = content.split("|", 1)
                skill_name = skill_name.strip()
                try:
                    confidence = float(conf_str.strip())
                except ValueError:
                    confidence = 0.0
                
                if skill_name != "NONE" and confidence >= threshold:
                    skill = self.registry.get_skill(skill_name)
                    if skill:
                        return skill, confidence
            
        except Exception as e:
            print(f"[SkillDetector] LLM classification error: {e}")
        
        return None, 0.0
    
    def set_llm(self, llm) -> None:
        """Update the LLM used for classification fallback."""
        self.llm = llm
    
    def invalidate_embedding_cache(self) -> None:
        """Clear embedding cache (call after skill registry reload)."""
        self._skill_embeddings.clear()


# Global detector instance
_global_detector: Optional[SkillDetector] = None

def get_detector(registry: SkillRegistry = None, llm=None) -> SkillDetector:
    """Get or create global skill detector."""
    global _global_detector
    if _global_detector is None:
        if registry is None:
            from Langchain.Skills.skillRegistry import get_registry
            registry = get_registry()
        _global_detector = SkillDetector(registry, llm)
    elif llm and _global_detector.llm != llm:
        _global_detector.set_llm(llm)
    return _global_detector