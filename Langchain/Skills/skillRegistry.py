"""
Skill Registry - Centralized skill discovery, metadata, and matching.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import os
import json
import re
from pathlib import Path


@dataclass
class SkillMetadata:
    name: str                    # filename (e.g., "git-push")
    display_name: str            # human-readable (e.g., "Git Push Workflow")
    description: str             # what this skill does
    keywords: List[str]          # trigger keywords for fallback matching
    intent_patterns: List[str]   # natural language patterns
    category: str                # "git", "deployment", "analysis", etc.
    priority: int                # higher = more specific (default 100)
    required_tools: List[str]    # tools this skill expects to use
    file_path: str               # path to skill file
    content: str                 # cached skill prompt content
    embedding: Optional[List[float]] = None  # for semantic matching


class SkillRegistry:
    def __init__(self, skill_dir: str = "./Skill"):
        self.skill_dir = Path(skill_dir)
        self.skills: Dict[str, SkillMetadata] = {}
        self._load_all_skills()
    
    def _load_all_skills(self) -> None:
        """Scan skill directory, read files, build metadata."""
        if not self.skill_dir.exists():
            print(f"[SkillRegistry] Skill directory not found: {self.skill_dir}")
            return
        
        skill_files = [f for f in self.skill_dir.iterdir() 
                       if f.is_file() and not f.name.endswith(('.bak', '.meta.json'))]
        
        for skill_file in skill_files:
            try:
                skill_meta = self._parse_skill_file(skill_file)
                if skill_meta:
                    self.skills[skill_meta.name] = skill_meta
            except Exception as e:
                print(f"[SkillRegistry] Error loading skill {skill_file.name}: {e}")
        
        print(f"[SkillRegistry] Loaded {len(self.skills)} skills: {list(self.skills.keys())}")
    
    def _parse_skill_file(self, skill_file: Path) -> Optional[SkillMetadata]:
        """Parse skill file and extract metadata from header or sidecar."""
        name = skill_file.stem
        file_path = str(skill_file)
        
        # Read skill content
        with open(skill_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
        
        # Check for sidecar metadata file
        meta_file = skill_file.with_suffix(skill_file.suffix + ".meta.json")
        meta = {}
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception as e:
                print(f"[SkillRegistry] Error reading meta file {meta_file}: {e}")
        
        # Parse header from skill content (lines starting with #)
        header_meta = self._parse_header(content)
        
        # Merge: sidecar > header > defaults
        display_name = meta.get("display_name") or header_meta.get("display_name") or name.replace("-", " ").title()
        description = meta.get("description") or header_meta.get("description") or content[:200]
        keywords = meta.get("keywords") or header_meta.get("keywords") or self._extract_keywords(name, content)
        intent_patterns = meta.get("intent_patterns") or header_meta.get("intent_patterns") or []
        category = meta.get("category") or header_meta.get("category") or "general"
        priority = meta.get("priority") or header_meta.get("priority") or 100
        required_tools = meta.get("required_tools") or header_meta.get("required_tools") or []
        
        # Ensure keywords and intent_patterns are lists
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        if isinstance(intent_patterns, str):
            intent_patterns = [p.strip() for p in intent_patterns.split(",")]
        if isinstance(required_tools, str):
            required_tools = [t.strip() for t in required_tools.split(",")]
        
        return SkillMetadata(
            name=name,
            display_name=display_name,
            description=description,
            keywords=keywords,
            intent_patterns=intent_patterns,
            category=category,
            priority=priority,
            required_tools=required_tools,
            file_path=file_path,
            content=content
        )
    
    def _parse_header(self, content: str) -> Dict[str, Any]:
        """Parse metadata from skill file header (comment lines)."""
        meta = {}
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if not line.startswith("#"):
                break
            # Parse # Key: Value format
            match = re.match(r"#\s*(\w+(?:-\w+)?)\s*:\s*(.+)", line)
            if match:
                key = match.group(1).lower().replace("-", "_")
                value = match.group(2).strip()
                # Handle list values
                if key in ("keywords", "intent_patterns", "required_tools"):
                    meta[key] = [v.strip() for v in value.split(",")]
                else:
                    meta[key] = value
        return meta
    
    def _extract_keywords(self, name: str, content: str) -> List[str]:
        """Extract keywords from skill name and content."""
        keywords = [name.replace("-", " "), name]
        # Add common action words from content
        action_words = ["create", "update", "delete", "list", "show", "get", "set", 
                       "push", "pull", "commit", "stage", "merge", "branch",
                       "plan", "analyze", "implement", "test", "deploy",
                       "remind", "schedule", "search", "find", "convert"]
        content_lower = content.lower()
        for word in action_words:
            if word in content_lower:
                keywords.append(word)
        return list(set(keywords))
    
    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """Exact name lookup (for slash commands). Case-insensitive."""
        name_lower = name.lower()
        for key, skill in self.skills.items():
            if key.lower() == name_lower:
                return skill
        return None
    
    def find_best_match(self, user_input: str, threshold: float = 0.65) -> Optional[SkillMetadata]:
        """Keyword/pattern matching for auto-detection. Returns best match above threshold."""
        user_lower = user_input.lower()
        best_skill = None
        best_score = 0.0
        
        for skill in self.skills.values():
            score = self._calculate_match_score(user_lower, skill)
            if score > best_score and score >= threshold:
                best_score = score
                best_skill = skill
        
        return best_skill
    
    def _calculate_match_score(self, user_input: str, skill: SkillMetadata) -> float:
        """Calculate keyword-based match score (0.0 to 1.0)."""
        score = 0.0
        total_weight = 0.0
        
        # Check intent patterns (highest weight) - use word-based matching
        intent_weight = 0.4
        if skill.intent_patterns:
            intent_scores = []
            for pattern in skill.intent_patterns:
                pattern_lower = pattern.lower()
                # Exact substring match (highest)
                if pattern_lower in user_input:
                    intent_scores.append(1.0)
                else:
                    # Word-based match: check if all significant words in pattern are in user_input
                    pattern_words = [w for w in pattern_lower.split() if len(w) > 2]  # Skip short words
                    if pattern_words:
                        matches = sum(1 for w in pattern_words if w in user_input)
                        intent_scores.append(matches / len(pattern_words))
                    else:
                        intent_scores.append(0.0)
            
            # Use best intent pattern match
            best_intent_score = max(intent_scores) if intent_scores else 0.0
            score += best_intent_score * intent_weight
            total_weight += intent_weight
        else:
            total_weight += intent_weight
        
        # Check keywords
        keyword_weight = 0.4
        keyword_matches = 0
        for keyword in skill.keywords:
            if keyword.lower() in user_input:
                keyword_matches += 1
        
        if skill.keywords:
            keyword_score = (keyword_matches / len(skill.keywords)) * keyword_weight
            score += keyword_score
            total_weight += keyword_weight
        else:
            total_weight += keyword_weight
        
        # Check category relevance (lower weight)
        category_weight = 0.1
        if skill.category != "general" and skill.category in user_input:
            score += category_weight
            total_weight += category_weight
        else:
            total_weight += category_weight
        
        # Check skill name
        name_weight = 0.1
        if skill.name.replace("-", " ") in user_input:
            score += name_weight
            total_weight += name_weight
        else:
            total_weight += name_weight
        
        # Normalize by total weight
        if total_weight > 0:
            return score / total_weight
        return 0.0
    
    def get_all_skills(self) -> List[SkillMetadata]:
        """Return all registered skills sorted by priority (desc)."""
        return sorted(self.skills.values(), key=lambda s: s.priority, reverse=True)
    
    def reload(self) -> None:
        """Reload all skills from disk."""
        self.skills.clear()
        self._load_all_skills()
    
    def validate_tools_available(self, skill: SkillMetadata, available_tools: List[str]) -> bool:
        """Check if all required tools for a skill are available."""
        if not skill.required_tools:
            return True
        available_tool_names = [t.name if hasattr(t, 'name') else str(t) for t in available_tools]
        for required in skill.required_tools:
            if required not in available_tool_names:
                print(f"[SkillRegistry] Skill '{skill.name}' requires unavailable tool: {required}")
                return False
        return True


# Global registry instance
_global_registry: Optional[SkillRegistry] = None

def get_registry(skill_dir: str = "./Skill") -> SkillRegistry:
    """Get or create global skill registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SkillRegistry(skill_dir)
    return _global_registry