"""
Procedural Memory module for Project Shri Sudarshan.

Procedural memory stores successful workflows and analytical patterns
using vector similarity search.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


class ProceduralMemory:
    """
    Vector database storage for successful workflows and patterns.
    
    Uses ChromaDB for similarity search of procedural knowledge.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        """
        Initialize procedural memory.
        
        Args:
            persist_directory: Directory for ChromaDB persistence
        """
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        
        if not CHROMA_AVAILABLE:
            print("Warning: ChromaDB not available. Procedural memory will operate in mock mode.")
            return
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="procedural_memory",
                metadata={"description": "Successful workflows and patterns"}
            )
        except Exception as e:
            print(f"Warning: Failed to initialize ChromaDB: {e}")
            print("Procedural memory will operate in mock mode.")
    
    def store_pattern(
        self,
        pattern_id: str,
        description: str,
        context: Dict[str, Any],
        success_metrics: Dict[str, float],
    ) -> None:
        """
        Store a successful pattern or workflow.
        
        Args:
            pattern_id: Unique identifier for the pattern
            description: Natural language description
            context: Context in which pattern was successful
            success_metrics: Metrics demonstrating success
        """
        if self.collection is None:
            return
        
        try:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "context": str(context),
                "success_metrics": str(success_metrics),
            }
            
            self.collection.add(
                ids=[pattern_id],
                documents=[description],
                metadatas=[metadata],
            )
        except Exception as e:
            print(f"Warning: Failed to store pattern: {e}")
    
    def search_similar_patterns(
        self,
        query: str,
        n_results: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar successful patterns.
        
        Args:
            query: Natural language query
            n_results: Number of results to return
            
        Returns:
            List of similar patterns with metadata
        """
        if self.collection is None:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            
            patterns = []
            for i in range(len(results["ids"][0])):
                patterns.append({
                    "id": results["ids"][0][i],
                    "description": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                })
            
            return patterns
        except Exception as e:
            print(f"Warning: Failed to search patterns: {e}")
            return []
    
    def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific pattern by ID.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Pattern data or None if not found
        """
        if self.collection is None:
            return None
        
        try:
            result = self.collection.get(ids=[pattern_id])
            
            if not result["ids"]:
                return None
            
            return {
                "id": result["ids"][0],
                "description": result["documents"][0],
                "metadata": result["metadatas"][0],
            }
        except Exception as e:
            print(f"Warning: Failed to get pattern: {e}")
            return None
    
    def delete_pattern(self, pattern_id: str) -> bool:
        """
        Delete a pattern from memory.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            True if deleted, False otherwise
        """
        if self.collection is None:
            return False
        
        try:
            self.collection.delete(ids=[pattern_id])
            return True
        except Exception as e:
            print(f"Warning: Failed to delete pattern: {e}")
            return False
    
    def __repr__(self) -> str:
        count = self.collection.count() if self.collection else 0
        return f"ProceduralMemory(patterns={count}, persist_dir={self.persist_directory})"
