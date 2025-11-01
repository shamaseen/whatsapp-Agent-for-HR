"""
OpenMemory Client
Integration with self-hosted OpenMemory AI memory engine
"""

import httpx
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OpenMemoryClient:
    """
    Client for OpenMemory - Self-hosted AI memory engine

    OpenMemory provides persistent, structured memory with:
    - Hierarchical Memory Decomposition (HMD)
    - Multi-sector embeddings (episodic, semantic, procedural, emotional, reflective)
    - Graph-based memory linking
    - Composite similarity retrieval

    Architecture: https://github.com/CaviraOSS/OpenMemory
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0
    ):
        """
        Initialize OpenMemory client

        Args:
            base_url: OpenMemory server URL (default: http://localhost:3000)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or "http://localhost:3000").rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=self._get_headers()
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def add_memory(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        sector: str = "episodic"
    ) -> Dict[str, Any]:
        """
        Add a new memory to OpenMemory

        Args:
            content: Memory content to store
            user_id: User identifier
            metadata: Additional metadata
            sector: Memory sector (episodic, semantic, procedural, emotional, reflective)

        Returns:
            Response with memory ID and details
        """
        payload = {
            "content": content,
            "userId": user_id,
            "sector": sector,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            response = await self.client.post("/api/memories", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to add memory: {e}")
            raise

    async def search_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        min_similarity: float = 0.5,
        sectors: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity

        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold (0-1)
            sectors: Filter by specific memory sectors

        Returns:
            List of matching memories with scores
        """
        params = {
            "query": query,
            "userId": user_id,
            "limit": limit,
            "minSimilarity": min_similarity
        }

        if sectors:
            params["sectors"] = ",".join(sectors)

        try:
            response = await self.client.get("/api/memories/search", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by ID

        Args:
            memory_id: Memory identifier

        Returns:
            Memory details or None if not found
        """
        try:
            response = await self.client.get(f"/api/memories/{memory_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing memory

        Args:
            memory_id: Memory identifier
            content: New content (optional)
            metadata: New metadata (optional)

        Returns:
            Updated memory details
        """
        payload = {}
        if content is not None:
            payload["content"] = content
        if metadata is not None:
            payload["metadata"] = metadata

        try:
            response = await self.client.patch(f"/api/memories/{memory_id}", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted successfully
        """
        try:
            response = await self.client.delete(f"/api/memories/{memory_id}")
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False

    async def get_user_memories(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        sector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a user

        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Pagination offset
            sector: Filter by memory sector

        Returns:
            List of memories
        """
        params = {
            "userId": user_id,
            "limit": limit,
            "offset": offset
        }

        if sector:
            params["sector"] = sector

        try:
            response = await self.client.get("/api/memories", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user memories: {e}")
            return []

    async def get_related_memories(
        self,
        memory_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get memories related to a specific memory via graph links

        Args:
            memory_id: Memory identifier
            limit: Maximum number of results

        Returns:
            List of related memories
        """
        try:
            response = await self.client.get(
                f"/api/memories/{memory_id}/related",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get related memories: {e}")
            return []

    async def get_memory_graph(
        self,
        user_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """
        Get memory graph for visualization

        Args:
            user_id: User identifier
            depth: Graph traversal depth

        Returns:
            Graph data with nodes and edges
        """
        try:
            response = await self.client.get(
                "/api/memories/graph",
                params={"userId": user_id, "depth": depth}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get memory graph: {e}")
            return {"nodes": [], "edges": []}

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user

        Args:
            user_id: User identifier

        Returns:
            Statistics including count per sector, total memories, etc.
        """
        try:
            response = await self.client.get(
                "/api/stats",
                params={"userId": user_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    async def health_check(self) -> bool:
        """
        Check if OpenMemory server is healthy

        Returns:
            True if server is responding
        """
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception:
            # Server is not responding
            return False

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Convenience factory function
def create_openmemory_client(
    base_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> OpenMemoryClient:
    """
    Create OpenMemory client with configuration from settings

    Args:
        base_url: Override base URL
        api_key: Override API key

    Returns:
        Configured OpenMemoryClient
    """
    from src.config import settings

    url = base_url or getattr(settings, 'OPENMEMORY_URL', 'http://localhost:3000')
    key = api_key or getattr(settings, 'OPENMEMORY_API_KEY', None)

    return OpenMemoryClient(base_url=url, api_key=key)
