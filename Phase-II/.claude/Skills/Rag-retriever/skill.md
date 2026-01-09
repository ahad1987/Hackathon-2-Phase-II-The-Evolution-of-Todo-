---
name: rag-retriever
description: Retrieve relevant context from vector stores for RAG systems. Execute semantic search with embeddings, apply filters and ranking strategies. Normalize queries, apply metadata constraints, and select top-k results deterministically. Deduplicate chunks, trim context to token limits, and return structured outputs with source attribution. Use when building RAG systems, semantic search, document retrieval, question answering, or context-aware LLM applications. Ensures reliable, fast, and predictable retrieval.
---

# RAG Retriever

Build production-ready retrieval systems for RAG (Retrieval-Augmented Generation) with semantic search, metadata filtering, and context optimization.

## Core Principles

**Semantic Search First**: Use vector embeddings for semantic similarity, not just keyword matching. Captures meaning, not just exact words.

**Metadata Filtering**: Combine semantic search with structured filters (date, author, category) for precise results.

**Deterministic Ranking**: Use consistent scoring and tie-breaking to ensure reproducible results.

**Context Management**: Respect token limits. Trim, deduplicate, and prioritize most relevant content.

**Source Attribution**: Always track which documents contributed to results. Essential for transparency and debugging.

**Performance Matters**: Optimize for sub-second retrieval. Cache embeddings, use efficient vector stores, batch when possible.

## Vector Store Architecture

### Embedding Strategy

**Generate embeddings for all content**:

```python
# embeddings.py
from openai import OpenAI
from typing import List

class EmbeddingService:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = 1536  # text-embedding-3-small default
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.model,
                input=batch
            )
            embeddings.extend([item.embedding for item in response.data])
        
        return embeddings

# Usage
embedder = EmbeddingService(api_key="your-key")

# Single embedding
query_embedding = embedder.embed_text("What is machine learning?")

# Batch embeddings (more efficient)
documents = ["Doc 1 text", "Doc 2 text", "Doc 3 text"]
doc_embeddings = embedder.embed_batch(documents)
```

### Document Chunking

**Split documents into retrievable chunks**:

```python
# chunking.py
from typing import List, Dict
import re

class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        min_chunk_size: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_by_tokens(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Returns list of chunks with metadata.
        """
        # Simple token approximation (4 chars ≈ 1 token)
        char_size = self.chunk_size * 4
        char_overlap = self.chunk_overlap * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + char_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or exclamation within last 100 chars
                boundary = text.rfind('.', end - 100, end)
                if boundary == -1:
                    boundary = text.rfind('?', end - 100, end)
                if boundary == -1:
                    boundary = text.rfind('!', end - 100, end)
                
                if boundary != -1:
                    end = boundary + 1
            
            chunk_text = text[start:end].strip()
            
            # Skip chunks that are too small
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append({
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'chunk_index': len(chunks),
                    'metadata': metadata or {}
                })
            
            # Move start position with overlap
            start = end - char_overlap
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split by paragraphs, combining small ones.
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_length = len(para)
            
            # If adding this paragraph exceeds chunk size, save current chunk
            if current_length + para_length > self.chunk_size * 4 and current_chunk:
                chunks.append({
                    'text': '\n\n'.join(current_chunk),
                    'chunk_index': len(chunks),
                    'metadata': metadata or {}
                })
                current_chunk = []
                current_length = 0
            
            current_chunk.append(para)
            current_length += para_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'text': '\n\n'.join(current_chunk),
                'chunk_index': len(chunks),
                'metadata': metadata or {}
            })
        
        return chunks

# Usage
chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)

document = "Long document text here..."
metadata = {
    'source': 'manual.pdf',
    'page': 5,
    'title': 'Installation Guide',
    'date': '2024-01-08'
}

chunks = chunker.chunk_by_tokens(document, metadata)
```

### Vector Store Integration

**Pinecone Example**:

```python
# vector_store/pinecone_store.py
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Optional
import uuid

class PineconeVectorStore:
    def __init__(self, api_key: str, index_name: str, dimension: int = 1536):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        
        # Create index if doesn't exist
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-east-1')
            )
        
        self.index = self.pc.Index(index_name)
    
    def upsert(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        """
        Insert or update vectors in batches.
        """
        vectors = []
        
        for chunk, embedding in zip(chunks, embeddings):
            vector_id = chunk.get('id') or str(uuid.uuid4())
            
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': {
                    'text': chunk['text'],
                    **chunk.get('metadata', {})
                }
            })
        
        # Batch upsert (Pinecone handles batching automatically)
        self.index.upsert(vectors=vectors)
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Semantic search with optional metadata filtering.
        """
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=include_metadata
        )
        
        return [
            {
                'id': match['id'],
                'score': match['score'],
                'text': match['metadata']['text'],
                'metadata': {k: v for k, v in match['metadata'].items() if k != 'text'}
            }
            for match in results['matches']
        ]
    
    def delete_by_filter(self, filter: Dict) -> None:
        """Delete vectors matching filter."""
        self.index.delete(filter=filter)

# Usage
store = PineconeVectorStore(
    api_key="your-key",
    index_name="documents",
    dimension=1536
)

# Insert chunks
store.upsert(chunks, embeddings)

# Search with filter
results = store.search(
    query_embedding=query_embedding,
    top_k=5,
    filter={'source': {'$eq': 'manual.pdf'}}
)
```

**ChromaDB Example** (Local/Open Source):

```python
# vector_store/chroma_store.py
import chromadb
from typing import List, Dict, Optional

class ChromaVectorStore:
    def __init__(self, path: str = "./chroma_db", collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def upsert(self, chunks: List[Dict], embeddings: List[List[float]]) -> None:
        """Insert or update vectors."""
        ids = [chunk.get('id', str(i)) for i, chunk in enumerate(chunks)]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk.get('metadata', {}) for chunk in chunks]
        
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter: Optional[Dict] = None
    ) -> List[Dict]:
        """Semantic search with metadata filtering."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter
        )
        
        return [
            {
                'id': results['ids'][0][i],
                'score': 1 - results['distances'][0][i],  # Convert distance to similarity
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i]
            }
            for i in range(len(results['ids'][0]))
        ]

# Usage
store = ChromaVectorStore(path="./my_chroma_db")
store.upsert(chunks, embeddings)

results = store.search(
    query_embedding=query_embedding,
    top_k=5,
    filter={'source': 'manual.pdf'}
)
```

## Query Processing

### Query Normalization

**Preprocess queries for better retrieval**:

```python
# query_processor.py
import re
from typing import List, Optional

class QueryProcessor:
    def __init__(self, max_query_length: int = 512):
        self.max_query_length = max_query_length
    
    def normalize(self, query: str) -> str:
        """
        Normalize query for consistent retrieval.
        """
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Remove special characters (keep alphanumeric, spaces, basic punctuation)
        query = re.sub(r'[^a-zA-Z0-9\s\.\?,!-]', '', query)
        
        # Truncate if too long
        if len(query) > self.max_query_length:
            query = query[:self.max_query_length].rsplit(' ', 1)[0]
        
        return query.strip()
    
    def expand_query(self, query: str, expansions: Optional[List[str]] = None) -> str:
        """
        Add query expansions for better recall.
        """
        if not expansions:
            return query
        
        # Combine original query with expansions
        expanded = f"{query} {' '.join(expansions)}"
        return self.normalize(expanded)
    
    def extract_filters(self, query: str) -> tuple[str, dict]:
        """
        Extract metadata filters from natural language query.
        
        Example: "documents from 2024 about python" 
        -> query="about python", filters={"year": 2024, "topic": "python"}
        """
        filters = {}
        clean_query = query
        
        # Extract year patterns
        year_match = re.search(r'\b(19|20)\d{2}\b', query)
        if year_match:
            filters['year'] = int(year_match.group())
            clean_query = clean_query.replace(year_match.group(), '').strip()
        
        # Extract "from [source]" patterns
        source_match = re.search(r'from\s+([a-zA-Z0-9_.-]+)', query, re.IGNORECASE)
        if source_match:
            filters['source'] = source_match.group(1)
            clean_query = re.sub(r'from\s+[a-zA-Z0-9_.-]+', '', clean_query, flags=re.IGNORECASE).strip()
        
        return self.normalize(clean_query), filters

# Usage
processor = QueryProcessor()

# Normalize
normalized = processor.normalize("  What is    Python???  ")
# Result: "What is Python"

# Expand
expanded = processor.expand_query(
    "machine learning",
    ["ML", "artificial intelligence", "neural networks"]
)

# Extract filters
query, filters = processor.extract_filters("Show me documents from manual.pdf about installation")
# query: "Show me documents about installation"
# filters: {'source': 'manual.pdf'}
```

### Hybrid Search

**Combine semantic search with keyword search**:

```python
# hybrid_search.py
from typing import List, Dict
from rank_bm25 import BM25Okapi

class HybridRetriever:
    def __init__(
        self,
        vector_store,
        embedder,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.bm25 = None
        self.corpus = []
    
    def index_documents(self, documents: List[Dict]) -> None:
        """Build BM25 index for keyword search."""
        self.corpus = documents
        tokenized_corpus = [doc['text'].lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter: Dict = None
    ) -> List[Dict]:
        """
        Hybrid retrieval combining semantic and keyword search.
        """
        # Semantic search
        query_embedding = self.embedder.embed_text(query)
        semantic_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k * 2,  # Retrieve more for reranking
            filter=filter
        )
        
        # Keyword search
        tokenized_query = query.lower().split()
        keyword_scores = self.bm25.get_scores(tokenized_query)
        
        # Combine scores
        combined_results = {}
        
        # Add semantic results
        for result in semantic_results:
            doc_id = result['id']
            combined_results[doc_id] = {
                **result,
                'semantic_score': result['score'],
                'keyword_score': 0.0
            }
        
        # Add keyword scores
        for idx, score in enumerate(keyword_scores):
            if idx < len(self.corpus):
                doc_id = self.corpus[idx].get('id')
                if doc_id in combined_results:
                    combined_results[doc_id]['keyword_score'] = score
                elif score > 0:  # Only include if has keyword relevance
                    combined_results[doc_id] = {
                        'id': doc_id,
                        'text': self.corpus[idx]['text'],
                        'metadata': self.corpus[idx].get('metadata', {}),
                        'semantic_score': 0.0,
                        'keyword_score': score
                    }
        
        # Calculate combined score
        for doc_id in combined_results:
            result = combined_results[doc_id]
            result['score'] = (
                self.semantic_weight * result['semantic_score'] +
                self.keyword_weight * result['keyword_score']
            )
        
        # Sort by combined score and return top_k
        ranked_results = sorted(
            combined_results.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return ranked_results[:top_k]
```

## Ranking and Reranking

### Basic Ranking

**Score-based ranking with tie-breaking**:

```python
# ranking.py
from typing import List, Dict

class ResultRanker:
    def rank(self, results: List[Dict], score_key: str = 'score') -> List[Dict]:
        """
        Rank results by score with deterministic tie-breaking.
        """
        return sorted(
            results,
            key=lambda x: (
                -x.get(score_key, 0),  # Primary: score (descending)
                x.get('id', '')         # Tie-breaker: ID (ascending)
            )
        )
    
    def apply_recency_boost(
        self,
        results: List[Dict],
        boost_factor: float = 0.1,
        date_field: str = 'date'
    ) -> List[Dict]:
        """
        Boost scores for more recent documents.
        """
        from datetime import datetime
        
        now = datetime.now()
        
        for result in results:
            date_str = result.get('metadata', {}).get(date_field)
            if date_str:
                try:
                    doc_date = datetime.fromisoformat(date_str)
                    days_old = (now - doc_date).days
                    
                    # Boost recent documents (exponential decay)
                    recency_boost = boost_factor * (0.99 ** days_old)
                    result['score'] = result.get('score', 0) + recency_boost
                except:
                    pass
        
        return self.rank(results)
    
    def apply_source_boost(
        self,
        results: List[Dict],
        source_weights: Dict[str, float]
    ) -> List[Dict]:
        """
        Boost scores based on document source.
        """
        for result in results:
            source = result.get('metadata', {}).get('source', '')
            if source in source_weights:
                result['score'] = result.get('score', 0) * source_weights[source]
        
        return self.rank(results)

# Usage
ranker = ResultRanker()

# Basic ranking
ranked = ranker.rank(results)

# Apply recency boost (favor recent documents)
ranked = ranker.apply_recency_boost(results, boost_factor=0.2)

# Apply source boost
source_weights = {
    'official_docs': 1.5,
    'user_manual': 1.2,
    'blog_post': 0.8
}
ranked = ranker.apply_source_boost(results, source_weights)
```

### Cross-Encoder Reranking

**Use a cross-encoder model for more accurate ranking**:

```python
# reranker.py
from sentence_transformers import CrossEncoder
from typing import List, Dict

class CrossEncoderReranker:
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self,
        query: str,
        results: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Rerank results using cross-encoder model.
        
        More accurate than bi-encoder (vector search) but slower.
        Use after initial retrieval to rerank top candidates.
        """
        if not results:
            return []
        
        # Prepare query-document pairs
        pairs = [(query, result['text']) for result in results]
        
        # Get reranking scores
        scores = self.model.predict(pairs)
        
        # Update scores
        for result, score in zip(results, scores):
            result['rerank_score'] = float(score)
        
        # Sort by rerank score
        reranked = sorted(
            results,
            key=lambda x: (-x['rerank_score'], x.get('id', '')),
            reverse=False
        )
        
        return reranked[:top_k]

# Usage
reranker = CrossEncoderReranker()

# Initial retrieval gets top 50
initial_results = vector_store.search(query_embedding, top_k=50)

# Rerank to get best 10
final_results = reranker.rerank(query, initial_results, top_k=10)
```

## Context Management

### Deduplication

**Remove duplicate or highly similar chunks**:

```python
# deduplication.py
from typing import List, Dict
from difflib import SequenceMatcher

class ContextDeduplicator:
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
    
    def deduplicate_exact(self, results: List[Dict]) -> List[Dict]:
        """Remove exact duplicate texts."""
        seen_texts = set()
        unique_results = []
        
        for result in results:
            text = result['text']
            if text not in seen_texts:
                seen_texts.add(text)
                unique_results.append(result)
        
        return unique_results
    
    def deduplicate_similar(self, results: List[Dict]) -> List[Dict]:
        """Remove highly similar texts."""
        unique_results = []
        
        for result in results:
            text = result['text']
            is_duplicate = False
            
            # Check similarity with already selected results
            for unique_result in unique_results:
                similarity = self._text_similarity(text, unique_result['text'])
                if similarity > self.similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity ratio."""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def deduplicate_by_source(self, results: List[Dict]) -> List[Dict]:
        """Keep only highest scoring chunk from each source."""
        best_by_source = {}
        
        for result in results:
            source = result.get('metadata', {}).get('source', 'unknown')
            
            if source not in best_by_source or result['score'] > best_by_source[source]['score']:
                best_by_source[source] = result
        
        return sorted(best_by_source.values(), key=lambda x: -x['score'])

# Usage
deduplicator = ContextDeduplicator(similarity_threshold=0.85)

# Remove exact duplicates
unique_results = deduplicator.deduplicate_exact(results)

# Remove similar chunks
unique_results = deduplicator.deduplicate_similar(results)

# One per source
unique_results = deduplicator.deduplicate_by_source(results)
```

### Context Trimming

**Trim context to fit token limits**:

```python
# context_trimmer.py
from typing import List, Dict
import tiktoken

class ContextTrimmer:
    def __init__(self, model: str = "gpt-4", max_tokens: int = 4000):
        self.encoding = tiktoken.encoding_for_model(model)
        self.max_tokens = max_tokens
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def trim_to_limit(
        self,
        results: List[Dict],
        reserve_tokens: int = 1000  # Reserve for prompt + response
    ) -> List[Dict]:
        """
        Trim results to fit within token limit.
        
        Keeps highest-scoring results that fit in limit.
        """
        available_tokens = self.max_tokens - reserve_tokens
        current_tokens = 0
        trimmed_results = []
        
        for result in results:
            text = result['text']
            tokens = self.count_tokens(text)
            
            if current_tokens + tokens <= available_tokens:
                trimmed_results.append(result)
                current_tokens += tokens
            else:
                # Try to fit partial chunk
                remaining_tokens = available_tokens - current_tokens
                if remaining_tokens > 100:  # Only if meaningful space left
                    truncated_text = self._truncate_to_tokens(text, remaining_tokens)
                    truncated_result = {**result, 'text': truncated_text, 'truncated': True}
                    trimmed_results.append(truncated_result)
                break
        
        return trimmed_results
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit in token limit."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)
        return truncated_text + "..."
    
    def optimize_context(self, results: List[Dict]) -> str:
        """
        Format results as optimized context string.
        """
        context_parts = []
        
        for i, result in enumerate(results, 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            score = result.get('score', 0)
            
            context_parts.append(
                f"[{i}] Source: {source} (Relevance: {score:.3f})\n"
                f"{result['text']}\n"
            )
        
        return "\n---\n".join(context_parts)

# Usage
trimmer = ContextTrimmer(model="gpt-4", max_tokens=8000)

# Count tokens
total_tokens = sum(trimmer.count_tokens(r['text']) for r in results)

# Trim to fit
trimmed = trimmer.trim_to_limit(results, reserve_tokens=2000)

# Format for LLM
context = trimmer.optimize_context(trimmed)
```

## Complete Retrieval Pipeline

**Put it all together**:

```python
# retriever.py
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class RetrievalConfig:
    top_k: int = 10
    similarity_threshold: float = 0.7
    enable_reranking: bool = True
    rerank_top_k: int = 50
    max_context_tokens: int = 4000
    reserve_tokens: int = 1000
    deduplicate: bool = True
    deduplication_threshold: float = 0.85

class RAGRetriever:
    def __init__(
        self,
        vector_store,
        embedder,
        query_processor,
        config: RetrievalConfig = None
    ):
        self.vector_store = vector_store
        self.embedder = embedder
        self.query_processor = query_processor
        self.config = config or RetrievalConfig()
        
        # Optional components
        self.reranker = None
        self.deduplicator = None
        self.trimmer = None
        
        if self.config.enable_reranking:
            from reranker import CrossEncoderReranker
            self.reranker = CrossEncoderReranker()
        
        if self.config.deduplicate:
            from deduplication import ContextDeduplicator
            self.deduplicator = ContextDeduplicator(self.config.deduplication_threshold)
        
        from context_trimmer import ContextTrimmer
        self.trimmer = ContextTrimmer(max_tokens=self.config.max_context_tokens)
    
    def retrieve(
        self,
        query: str,
        filters: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> Dict:
        """
        Complete retrieval pipeline.
        
        Returns:
            {
                'query': str,
                'results': List[Dict],
                'context': str,
                'metadata': {
                    'total_results': int,
                    'total_tokens': int,
                    'filters': Dict
                }
            }
        """
        top_k = top_k or self.config.top_k
        
        # 1. Process query
        processed_query = self.query_processor.normalize(query)
        
        # 2. Generate embedding
        query_embedding = self.embedder.embed_text(processed_query)
        
        # 3. Vector search
        retrieve_k = self.config.rerank_top_k if self.config.enable_reranking else top_k
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=retrieve_k,
            filter=filters
        )
        
        # 4. Filter by similarity threshold
        results = [r for r in results if r['score'] >= self.config.similarity_threshold]
        
        # 5. Rerank (optional)
        if self.config.enable_reranking and self.reranker:
            results = self.reranker.rerank(processed_query, results, top_k=top_k)
        
        # 6. Deduplicate (optional)
        if self.config.deduplicate and self.deduplicator:
            results = self.deduplicator.deduplicate_similar(results)
        
        # 7. Trim to token limit
        results = self.trimmer.trim_to_limit(
            results,
            reserve_tokens=self.config.reserve_tokens
        )
        
        # 8. Format context
        context = self.trimmer.optimize_context(results)
        total_tokens = self.trimmer.count_tokens(context)
        
        return {
            'query': query,
            'processed_query': processed_query,
            'results': results,
            'context': context,
            'metadata': {
                'total_results': len(results),
                'total_tokens': total_tokens,
                'filters': filters or {},
                'config': {
                    'top_k': top_k,
                    'similarity_threshold': self.config.similarity_threshold,
                    'reranking_enabled': self.config.enable_reranking
                }
            }
        }

# Usage
config = RetrievalConfig(
    top_k=5,
    similarity_threshold=0.7,
    enable_reranking=True,
    max_context_tokens=4000
)

retriever = RAGRetriever(
    vector_store=vector_store,
    embedder=embedder,
    query_processor=query_processor,
    config=config
)

# Retrieve
result = retriever.retrieve(
    query="How do I install the software?",
    filters={'source': 'manual.pdf'}
)

# Use in RAG
context = result['context']
response = llm.generate(f"Context:\n{context}\n\nQuestion: {result['query']}\nAnswer:")
```

## Metadata Filtering

**Apply structured filters to narrow results**:

```python
# filters.py
from typing import Dict, Any
from datetime import datetime

class MetadataFilter:
    @staticmethod
    def build_pinecone_filter(filters: Dict[str, Any]) -> Dict:
        """
        Build Pinecone-compatible filter.
        
        Example: {'source': 'manual.pdf', 'year': 2024}
        -> {'source': {'$eq': 'manual.pdf'}, 'year': {'$eq': 2024}}
        """
        pinecone_filter = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                # Multiple values (OR)
                pinecone_filter[key] = {'$in': value}
            elif isinstance(value, dict) and 'min' in value and 'max' in value:
                # Range
                pinecone_filter[key] = {
                    '$gte': value['min'],
                    '$lte': value['max']
                }
            else:
                # Exact match
                pinecone_filter[key] = {'$eq': value}
        
        return pinecone_filter
    
    @staticmethod
    def build_chroma_filter(filters: Dict[str, Any]) -> Dict:
        """
        Build ChromaDB-compatible filter.
        
        Example: {'source': 'manual.pdf', 'category': ['tech', 'guide']}
        -> {'source': 'manual.pdf', 'category': {'$in': ['tech', 'guide']}}
        """
        chroma_filter = {}
        
        for key, value in filters.items():
            if isinstance(value, list):
                chroma_filter[key] = {'$in': value}
            else:
                chroma_filter[key] = value
        
        return chroma_filter
    
    @staticmethod
    def date_range_filter(
        field: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        Create date range filter.
        
        Example: date_range_filter('published_date', '2024-01-01', '2024-12-31')
        """
        filter = {}
        
        if start_date:
            start = datetime.fromisoformat(start_date).timestamp()
            filter['$gte'] = start
        
        if end_date:
            end = datetime.fromisoformat(end_date).timestamp()
            filter['$lte'] = end
        
        return {field: filter} if filter else {}

# Usage
# Exact match
filters = MetadataFilter.build_pinecone_filter({
    'source': 'manual.pdf',
    'category': 'installation'
})

# Multiple values (OR)
filters = MetadataFilter.build_pinecone_filter({
    'category': ['installation', 'setup', 'configuration']
})

# Range
filters = MetadataFilter.build_pinecone_filter({
    'page': {'min': 10, 'max': 50}
})

# Date range
filters = MetadataFilter.date_range_filter(
    'published_date',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

## Evaluation and Monitoring

### Retrieval Metrics

```python
# evaluation.py
from typing import List, Set
import numpy as np

class RetrievalEvaluator:
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Precision@K: Fraction of retrieved docs that are relevant.
        
        P@K = (relevant docs in top K) / K
        """
        top_k = retrieved[:k]
        relevant_retrieved = sum(1 for doc_id in top_k if doc_id in relevant)
        return relevant_retrieved / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
        """
        Recall@K: Fraction of relevant docs that were retrieved.
        
        R@K = (relevant docs in top K) / (total relevant docs)
        """
        top_k = retrieved[:k]
        relevant_retrieved = sum(1 for doc_id in top_k if doc_id in relevant)
        return relevant_retrieved / len(relevant) if relevant else 0.0
    
    @staticmethod
    def mean_reciprocal_rank(retrieved_lists: List[List[str]], relevant_sets: List[Set[str]]) -> float:
        """
        MRR: Average of reciprocal ranks of first relevant result.
        
        MRR = (1/n) * Σ(1 / rank of first relevant doc)
        """
        reciprocal_ranks = []
        
        for retrieved, relevant in zip(retrieved_lists, relevant_sets):
            for i, doc_id in enumerate(retrieved, 1):
                if doc_id in relevant:
                    reciprocal_ranks.append(1.0 / i)
                    break
            else:
                reciprocal_ranks.append(0.0)
        
        return np.mean(reciprocal_ranks)
    
    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevance_scores: Dict[str, float], k: int) -> float:
        """
        NDCG@K: Normalized Discounted Cumulative Gain.
        
        Accounts for position and relevance grade.
        """
        def dcg(scores: List[float]) -> float:
            return sum(
                (2 ** score - 1) / np.log2(i + 2)
                for i, score in enumerate(scores)
            )
        
        # Get relevance scores for retrieved docs
        retrieved_scores = [
            relevance_scores.get(doc_id, 0.0)
            for doc_id in retrieved[:k]
        ]
        
        # Calculate DCG
        dcg_score = dcg(retrieved_scores)
        
        # Calculate IDCG (ideal DCG with perfect ranking)
        ideal_scores = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg_score = dcg(ideal_scores)
        
        return dcg_score / idcg_score if idcg_score > 0 else 0.0

# Usage
evaluator = RetrievalEvaluator()

# Test set: retrieved docs and ground truth relevant docs
retrieved_ids = ['doc1', 'doc5', 'doc3', 'doc8', 'doc2']
relevant_ids = {'doc1', 'doc3', 'doc7'}

# Precision and Recall at k=3
p_at_3 = evaluator.precision_at_k(retrieved_ids, relevant_ids, k=3)
r_at_3 = evaluator.recall_at_k(retrieved_ids, relevant_ids, k=3)

print(f"Precision@3: {p_at_3:.2f}")  # 2/3 = 0.67
print(f"Recall@3: {r_at_3:.2f}")     # 2/3 = 0.67

# NDCG with relevance grades
relevance_scores = {
    'doc1': 3,  # Highly relevant
    'doc3': 2,  # Somewhat relevant
    'doc5': 1,  # Marginally relevant
    'doc7': 3,  # Highly relevant
}

ndcg = evaluator.ndcg_at_k(retrieved_ids, relevance_scores, k=5)
print(f"NDCG@5: {ndcg:.2f}")
```

## Production Best Practices

### Caching

```python
# cache.py
from functools import lru_cache
import hashlib
import json
from typing import List, Dict
import redis

class EmbeddingCache:
    def __init__(self, redis_client: redis.Redis = None):
        self.redis = redis_client
        self.ttl = 86400 * 7  # 7 days
    
    def _get_key(self, text: str) -> str:
        """Generate cache key from text."""
        return f"emb:{hashlib.sha256(text.encode()).hexdigest()}"
    
    def get(self, text: str) -> List[float]:
        """Get cached embedding."""
        if not self.redis:
            return None
        
        key = self._get_key(text)
        cached = self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """Cache embedding."""
        if not self.redis:
            return
        
        key = self._get_key(text)
        self.redis.setex(key, self.ttl, json.dumps(embedding))
    
    def get_or_compute(self, text: str, embedder) -> List[float]:
        """Get from cache or compute and cache."""
        embedding = self.get(text)
        
        if embedding is None:
            embedding = embedder.embed_text(text)
            self.set(text, embedding)
        
        return embedding

# Usage
cache = EmbeddingCache(redis_client=redis.Redis())

embedding = cache.get_or_compute(query, embedder)
```

### Monitoring

```python
# monitoring.py
import time
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class RetrievalMetrics:
    query: str
    num_results: int
    retrieval_time_ms: float
    total_tokens: int
    filters: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

class RetrievalMonitor:
    def __init__(self):
        self.metrics: List[RetrievalMetrics] = []
    
    def log_retrieval(self, metrics: RetrievalMetrics) -> None:
        """Log retrieval metrics."""
        self.metrics.append(metrics)
    
    def get_stats(self) -> Dict:
        """Get aggregate statistics."""
        if not self.metrics:
            return {}
        
        retrieval_times = [m.retrieval_time_ms for m in self.metrics]
        token_counts = [m.total_tokens for m in self.metrics]
        
        return {
            'total_queries': len(self.metrics),
            'avg_retrieval_time_ms': sum(retrieval_times) / len(retrieval_times),
            'p95_retrieval_time_ms': sorted(retrieval_times)[int(len(retrieval_times) * 0.95)],
            'avg_results': sum(m.num_results for m in self.metrics) / len(self.metrics),
            'avg_tokens': sum(token_counts) / len(token_counts),
            'max_tokens': max(token_counts)
        }

# Usage in retriever
monitor = RetrievalMonitor()

def retrieve_with_monitoring(self, query: str, filters: Dict = None):
    start_time = time.time()
    
    result = self.retrieve(query, filters)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    monitor.log_retrieval(RetrievalMetrics(
        query=query,
        num_results=len(result['results']),
        retrieval_time_ms=elapsed_ms,
        total_tokens=result['metadata']['total_tokens'],
        filters=filters or {}
    ))
    
    return result

# Check stats
stats = monitor.get_stats()
print(f"Average retrieval time: {stats['avg_retrieval_time_ms']:.2f}ms")
print(f"P95 retrieval time: {stats['p95_retrieval_time_ms']:.2f}ms")
```

## Common Patterns

### Document Q&A

```python
def qa_retrieval(query: str) -> str:
    """Retrieve context for question answering."""
    result = retriever.retrieve(query, top_k=5)
    
    prompt = f"""Answer the question based on the context provided.

Context:
{result['context']}

Question: {query}

Answer:"""
    
    return llm.generate(prompt)
```

### Conversational Search

```python
def conversational_retrieval(query: str, chat_history: List[Dict]) -> str:
    """Retrieve with conversation context."""
    # Rewrite query with conversation context
    conversation_context = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in chat_history[-3:]  # Last 3 turns
    ])
    
    expanded_query = f"{conversation_context}\n\nCurrent question: {query}"
    
    result = retriever.retrieve(expanded_query, top_k=5)
    return result['context']
```

### Multi-Query Retrieval

```python
def multi_query_retrieval(query: str) -> List[Dict]:
    """Generate multiple query variants for better recall."""
    # Generate query variants
    variants = llm.generate(f"Generate 3 different ways to ask: {query}")
    queries = [query] + variants.split('\n')[:3]
    
    # Retrieve for each variant
    all_results = []
    for q in queries:
        results = retriever.retrieve(q, top_k=10)
        all_results.extend(results['results'])
    
    # Deduplicate and rerank
    unique_results = deduplicator.deduplicate_similar(all_results)
    return sorted(unique_results, key=lambda x: -x['score'])[:10]
```

## Production Checklist

Before deploying:

- [ ] **Chunking Strategy**: Optimal chunk size tested (typically 512-1024 tokens)
- [ ] **Embeddings**: Model selected and embeddings generated for all documents
- [ ] **Vector Store**: Indexed with proper metadata and filters
- [ ] **Query Processing**: Normalization and filter extraction working
- [ ] **Ranking**: Score-based ranking with deterministic tie-breaking
- [ ] **Deduplication**: Similar chunks removed
- [ ] **Token Limits**: Context trimmed to fit model limits
- [ ] **Metadata Tracking**: Source attribution for all results
- [ ] **Performance**: Sub-second retrieval achieved
- [ ] **Caching**: Embedding cache implemented for common queries
- [ ] **Monitoring**: Retrieval metrics logged
- [ ] **Evaluation**: Precision, recall, and NDCG measured on test set
- [ ] **Fallback**: Handle no results gracefully

## Quick Reference

### Retrieval Pipeline Steps

1. **Normalize Query** → Clean, truncate, extract filters
2. **Generate Embedding** → Convert query to vector
3. **Vector Search** → Find similar chunks
4. **Apply Filters** → Narrow by metadata
5. **Rerank** → Improve relevance with cross-encoder
6. **Deduplicate** → Remove similar chunks
7. **Trim Context** → Fit within token limit
8. **Format Output** → Structure with sources

### Key Metrics

- **Precision@K**: Relevant / Retrieved
- **Recall@K**: Retrieved / Total Relevant
- **MRR**: Mean Reciprocal Rank
- **NDCG**: Normalized Discounted Cumulative Gain
- **Latency**: Retrieval time (target: < 1 second)

### Optimization Tips

- Use **smaller embeddings** (768d vs 1536d) for faster search
- **Cache** embeddings for common queries
- **Batch** embedding generation
- **Limit** initial retrieval (e.g., 50), then rerank to top-k
- **Partition** large vector stores by metadata
- Use **hybrid search** (semantic + keyword) for better recall

Build RAG systems that are **accurate, fast, and production-ready**.
