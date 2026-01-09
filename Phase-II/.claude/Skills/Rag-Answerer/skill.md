---
name: rag-answerer
description: Generate answers using retrieved context for RAG systems. Ground responses strictly in provided sources without hallucination. Synthesize concise, accurate outputs from multiple documents. Cite sources and reference context explicitly. Handle insufficient or conflicting evidence transparently. Detect when context doesn't support the question. Use when building RAG question-answering, document chatbots, knowledge bases, or context-aware LLM applications. Ensures consistent, verifiable, and production-ready answers.
---

# RAG Answerer

Generate accurate, grounded answers from retrieved context with proper citations and hallucination prevention.

## Core Principles

**Ground in Context**: Answer only what the context supports. Never invent information not present in sources.

**Cite Sources**: Attribute claims to specific sources. Users must be able to verify answers.

**Handle Uncertainty**: Explicitly state when context is insufficient, ambiguous, or conflicting.

**Be Concise**: Synthesize information efficiently. Don't repeat unnecessary context.

**Detect Scope**: Recognize when questions fall outside available context. Say "I don't know" when appropriate.

**Maintain Consistency**: Same question + same context = same answer. Deterministic behavior.

## Prompt Engineering

### Basic Grounded Response Prompt

```python
# prompts.py
class PromptTemplates:
    BASIC_QA = """You are a helpful assistant that answers questions based strictly on the provided context.

Context:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the information in the context above
- If the context doesn't contain the answer, say "I cannot answer this question based on the provided context"
- Be concise and direct
- Do not add information from your general knowledge

Answer:"""

    CITED_QA = """You are a helpful assistant that answers questions using the provided context with citations.

Context:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the context provided
- Cite sources using [Source N] format where N is the source number
- If information comes from multiple sources, cite all relevant sources
- If the context doesn't fully answer the question, state what information is missing
- Be concise but thorough

Answer:"""

    ANALYTICAL_QA = """You are a precise assistant that analyzes context to answer questions.

Context:
{context}

Question: {question}

Instructions:
1. Identify relevant information in the context
2. Synthesize a clear answer if the context supports it
3. Cite specific sources using [N] where N is the source number
4. If context is insufficient, explain what information is missing
5. If context is conflicting, present different viewpoints with sources
6. If context doesn't address the question, explicitly state this

Analyze the context and provide your answer:"""

# Usage
prompt = PromptTemplates.CITED_QA.format(
    context=retrieved_context,
    question=user_question
)
```

### Advanced Prompts with Reasoning

```python
class AdvancedPrompts:
    CHAIN_OF_THOUGHT = """You are a thorough assistant that thinks step-by-step.

Context:
{context}

Question: {question}

Instructions:
1. First, think through what information from the context is relevant (write this in <thinking> tags)
2. Then, synthesize your answer based on that information
3. Cite sources using [N] format
4. If insufficient information, state this clearly

Think step-by-step and answer:"""

    CONFIDENCE_SCORED = """You are a precise assistant that assesses answer confidence.

Context:
{context}

Question: {question}

Provide your answer in this format:

Answer: [Your answer with citations]
Confidence: [High/Medium/Low]
Reasoning: [Why you have this confidence level based on the context]

Guidelines:
- High: Context directly and comprehensively answers the question
- Medium: Context partially answers or requires some inference
- Low: Context tangentially related or requires significant assumptions
- If context doesn't support an answer, state "Cannot answer" with confidence "N/A"

Response:"""

    STRUCTURED_OUTPUT = """Answer the question using the provided context.

Context:
{context}

Question: {question}

Provide your response in JSON format:
{{
    "answer": "Your concise answer",
    "confidence": "high|medium|low",
    "sources": ["List of source numbers used"],
    "evidence": ["Direct quotes from context supporting the answer"],
    "caveats": ["Any limitations or uncertainties"]
}}

Response:"""
```

## Answer Generation

### Basic Answer Generator

```python
# answerer.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class Answer:
    text: str
    sources: List[str]
    confidence: str
    evidence: List[str] = None
    caveats: List[str] = None

class RAGAnswerer:
    def __init__(self, llm_client, prompt_template: str = None):
        self.llm = llm_client
        self.prompt_template = prompt_template or PromptTemplates.CITED_QA
    
    def generate_answer(
        self,
        question: str,
        context: str,
        temperature: float = 0.0  # Low temp for consistency
    ) -> str:
        """
        Generate answer from context.
        
        Low temperature (0.0) ensures deterministic, grounded responses.
        """
        prompt = self.prompt_template.format(
            context=context,
            question=question
        )
        
        response = self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=500
        )
        
        return response
    
    def generate_structured_answer(
        self,
        question: str,
        context: str
    ) -> Answer:
        """
        Generate structured answer with metadata.
        """
        prompt = AdvancedPrompts.STRUCTURED_OUTPUT.format(
            context=context,
            question=question
        )
        
        response = self.llm.generate(
            prompt=prompt,
            temperature=0.0,
            max_tokens=800
        )
        
        # Parse JSON response
        try:
            data = json.loads(response)
            return Answer(
                text=data['answer'],
                sources=data['sources'],
                confidence=data['confidence'],
                evidence=data.get('evidence'),
                caveats=data.get('caveats')
            )
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return Answer(
                text=response,
                sources=[],
                confidence='unknown',
                evidence=[],
                caveats=['Failed to parse structured response']
            )

# Usage
answerer = RAGAnswerer(llm_client)

answer = answerer.generate_answer(
    question="What is the installation process?",
    context=retrieved_context
)
```

### Context Formatting

**Format retrieved chunks for optimal LLM consumption**:

```python
# context_formatter.py
from typing import List, Dict

class ContextFormatter:
    @staticmethod
    def format_with_sources(chunks: List[Dict]) -> str:
        """
        Format chunks with clear source attribution.
        
        Output:
        [1] Source: manual.pdf (Page 5, Relevance: 0.89)
        Installation requires admin privileges. Run setup.exe as administrator...
        
        [2] Source: faq.md (Relevance: 0.85)
        Q: How do I install? A: Download the installer and follow the wizard...
        """
        formatted_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get('metadata', {})
            source = metadata.get('source', 'Unknown')
            page = metadata.get('page')
            score = chunk.get('score', 0.0)
            
            # Header with metadata
            header = f"[{i}] Source: {source}"
            if page:
                header += f" (Page {page})"
            header += f" (Relevance: {score:.2f})"
            
            # Content
            content = chunk['text'].strip()
            
            formatted_parts.append(f"{header}\n{content}\n")
        
        return "\n---\n".join(formatted_parts)
    
    @staticmethod
    def format_concise(chunks: List[Dict]) -> str:
        """
        Format without metadata for cleaner context.
        
        Better for situations where source tracking is less critical.
        """
        return "\n\n".join([
            f"[{i}] {chunk['text'].strip()}"
            for i, chunk in enumerate(chunks, 1)
        ])
    
    @staticmethod
    def format_with_hierarchy(chunks: List[Dict]) -> str:
        """
        Group by source with hierarchical structure.
        
        Source: manual.pdf
        - Page 5: Installation requires...
        - Page 7: Configuration steps...
        
        Source: faq.md
        - Q&A: How do I install?...
        """
        from collections import defaultdict
        
        by_source = defaultdict(list)
        
        for chunk in chunks:
            source = chunk.get('metadata', {}).get('source', 'Unknown')
            by_source[source].append(chunk)
        
        formatted_parts = []
        
        for source, source_chunks in by_source.items():
            formatted_parts.append(f"Source: {source}")
            
            for chunk in source_chunks:
                page = chunk.get('metadata', {}).get('page')
                text = chunk['text'].strip()[:200] + "..."  # Truncate for overview
                
                if page:
                    formatted_parts.append(f"  - Page {page}: {text}")
                else:
                    formatted_parts.append(f"  - {text}")
            
            formatted_parts.append("")  # Blank line between sources
        
        return "\n".join(formatted_parts)

# Usage
formatter = ContextFormatter()

# Standard format with sources
context = formatter.format_with_sources(retrieved_chunks)

# Concise format
context = formatter.format_concise(retrieved_chunks)

# Hierarchical format
context = formatter.format_with_hierarchy(retrieved_chunks)
```

## Citation Extraction

**Extract and validate citations from generated answers**:

```python
# citation_extractor.py
import re
from typing import List, Dict, Tuple

class CitationExtractor:
    @staticmethod
    def extract_citations(text: str) -> List[int]:
        """
        Extract citation numbers from text.
        
        Patterns: [1], [2], [1,2], [1, 2, 3]
        """
        pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        matches = re.findall(pattern, text)
        
        citations = set()
        for match in matches:
            # Handle comma-separated citations
            numbers = [int(n.strip()) for n in match.split(',')]
            citations.update(numbers)
        
        return sorted(citations)
    
    @staticmethod
    def validate_citations(
        answer: str,
        num_sources: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all citations reference valid sources.
        
        Returns: (is_valid, error_messages)
        """
        citations = CitationExtractor.extract_citations(answer)
        errors = []
        
        for citation in citations:
            if citation < 1 or citation > num_sources:
                errors.append(f"Citation [{citation}] references non-existent source")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def add_citation_links(
        answer: str,
        source_metadata: List[Dict]
    ) -> str:
        """
        Convert citations to links or detailed references.
        
        [1] -> [1: manual.pdf, Page 5]
        """
        def replace_citation(match):
            num = int(match.group(1))
            if 0 < num <= len(source_metadata):
                metadata = source_metadata[num - 1]
                source = metadata.get('source', 'Unknown')
                page = metadata.get('page')
                
                if page:
                    return f"[{num}: {source}, Page {page}]"
                return f"[{num}: {source}]"
            return match.group(0)
        
        pattern = r'\[(\d+)\]'
        return re.sub(pattern, replace_citation, answer)

# Usage
extractor = CitationExtractor()

answer = "The installation requires admin privileges [1]. Configuration is in the settings menu [2, 3]."

# Extract citations
citations = extractor.extract_citations(answer)
# Result: [1, 2, 3]

# Validate
is_valid, errors = extractor.validate_citations(answer, num_sources=5)

# Add detailed references
detailed_answer = extractor.add_citation_links(answer, source_metadata)
# Result: "The installation requires admin privileges [1: manual.pdf, Page 5]. ..."
```

## Handling Edge Cases

### Insufficient Context

```python
# edge_cases.py
class ContextAnalyzer:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def assess_context_sufficiency(
        self,
        question: str,
        context: str
    ) -> Dict:
        """
        Determine if context is sufficient to answer question.
        """
        prompt = f"""Analyze if the provided context contains sufficient information to answer the question.

Context:
{context}

Question: {question}

Respond in JSON format:
{{
    "sufficient": true/false,
    "coverage": "none|partial|complete",
    "missing_info": ["What information is missing"],
    "confidence": "high|medium|low"
}}

Analysis:"""

        response = self.llm.generate(prompt, temperature=0.0)
        
        try:
            return json.loads(response)
        except:
            return {
                "sufficient": False,
                "coverage": "unknown",
                "missing_info": ["Failed to analyze context"],
                "confidence": "low"
            }
    
    def generate_answer_with_check(
        self,
        question: str,
        context: str
    ) -> Dict:
        """
        Generate answer only if context is sufficient.
        """
        # First check if context is sufficient
        assessment = self.assess_context_sufficiency(question, context)
        
        if not assessment['sufficient']:
            return {
                'answer': "I cannot answer this question based on the provided context.",
                'reason': 'insufficient_context',
                'missing_info': assessment.get('missing_info', []),
                'confidence': 'none'
            }
        
        # Generate answer if context is sufficient
        prompt = PromptTemplates.CITED_QA.format(
            context=context,
            question=question
        )
        
        answer = self.llm.generate(prompt, temperature=0.0)
        
        return {
            'answer': answer,
            'reason': 'sufficient_context',
            'confidence': assessment.get('confidence', 'medium')
        }

# Usage
analyzer = ContextAnalyzer(llm_client)

result = analyzer.generate_answer_with_check(
    question="What is the refund policy?",
    context=retrieved_context
)

if result['reason'] == 'insufficient_context':
    print(f"Cannot answer. Missing: {result['missing_info']}")
else:
    print(result['answer'])
```

### Conflicting Information

```python
class ConflictHandler:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def handle_conflicting_context(
        self,
        question: str,
        context: str
    ) -> str:
        """
        Generate answer that acknowledges conflicting information.
        """
        prompt = f"""You are analyzing context that may contain conflicting information.

Context:
{context}

Question: {question}

Instructions:
1. Check if the context contains conflicting information about the question
2. If conflicts exist:
   - Present each viewpoint with its source citation
   - Explain the conflict clearly
   - Do not choose one over the other unless there's clear reason
3. If no conflicts, answer normally with citations

Answer:"""

        return self.llm.generate(prompt, temperature=0.0)
    
    def detect_conflicts(
        self,
        question: str,
        chunks: List[Dict]
    ) -> Dict:
        """
        Detect if retrieved chunks contain conflicting information.
        """
        if len(chunks) < 2:
            return {'has_conflicts': False, 'conflicts': []}
        
        # Format chunks for comparison
        formatted_chunks = "\n\n".join([
            f"Source {i+1}: {chunk['text']}"
            for i, chunk in enumerate(chunks)
        ])
        
        prompt = f"""Analyze if these sources contain conflicting information about the question.

Question: {question}

Sources:
{formatted_chunks}

Respond in JSON:
{{
    "has_conflicts": true/false,
    "conflicts": [
        {{
            "topic": "What conflicts about",
            "source_1": "Source 1 says...",
            "source_2": "Source 2 says..."
        }}
    ]
}}

Analysis:"""

        response = self.llm.generate(prompt, temperature=0.0)
        
        try:
            return json.loads(response)
        except:
            return {'has_conflicts': False, 'conflicts': []}

# Usage
conflict_handler = ConflictHandler(llm_client)

# Detect conflicts
conflicts = conflict_handler.detect_conflicts(question, retrieved_chunks)

if conflicts['has_conflicts']:
    # Handle conflicts explicitly
    answer = conflict_handler.handle_conflicting_context(
        question,
        formatted_context
    )
else:
    # Normal answer generation
    answer = answerer.generate_answer(question, formatted_context)
```

### Out-of-Scope Questions

```python
class ScopeDetector:
    def __init__(self, llm_client, domain_description: str = None):
        self.llm = llm_client
        self.domain_description = domain_description
    
    def is_in_scope(self, question: str, context: str) -> Dict:
        """
        Determine if question is within scope of available context.
        """
        domain_context = ""
        if self.domain_description:
            domain_context = f"\nDomain: This knowledge base covers {self.domain_description}"
        
        prompt = f"""Determine if the question can be answered using the provided context.
{domain_context}

Context:
{context}

Question: {question}

Respond in JSON:
{{
    "in_scope": true/false,
    "reason": "Why is it in/out of scope",
    "suggestion": "If out of scope, suggest what type of information would be needed"
}}

Analysis:"""

        response = self.llm.generate(prompt, temperature=0.0)
        
        try:
            return json.loads(response)
        except:
            return {
                'in_scope': True,  # Default to attempting answer
                'reason': 'Unable to determine scope',
                'suggestion': None
            }
    
    def generate_out_of_scope_response(
        self,
        question: str,
        scope_analysis: Dict
    ) -> str:
        """
        Generate helpful response for out-of-scope questions.
        """
        suggestion = scope_analysis.get('suggestion', '')
        
        response = f"I don't have information in my knowledge base to answer this question."
        
        if suggestion:
            response += f"\n\nTo answer this question, I would need: {suggestion}"
        
        if self.domain_description:
            response += f"\n\nMy knowledge base covers: {self.domain_description}"
        
        return response

# Usage
scope_detector = ScopeDetector(
    llm_client,
    domain_description="product installation, configuration, and troubleshooting"
)

scope_analysis = scope_detector.is_in_scope(question, context)

if not scope_analysis['in_scope']:
    answer = scope_detector.generate_out_of_scope_response(question, scope_analysis)
else:
    answer = answerer.generate_answer(question, context)
```

## Answer Quality Control

### Hallucination Detection

```python
# quality_control.py
class HallucinationDetector:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def verify_answer_grounding(
        self,
        question: str,
        answer: str,
        context: str
    ) -> Dict:
        """
        Verify that answer is grounded in context.
        
        Returns assessment of whether answer contains hallucinations.
        """
        prompt = f"""Verify if the answer is fully supported by the context.

Context:
{context}

Question: {question}

Answer:
{answer}

Instructions:
Check each claim in the answer against the context. Identify any information that:
1. Is not present in the context
2. Contradicts the context
3. Makes unsupported inferences

Respond in JSON:
{{
    "grounded": true/false,
    "supported_claims": ["Claims from answer that are in context"],
    "unsupported_claims": ["Claims from answer NOT in context"],
    "contradictions": ["Claims that contradict context"],
    "confidence": "high|medium|low"
}}

Verification:"""

        response = self.llm.generate(prompt, temperature=0.0)
        
        try:
            return json.loads(response)
        except:
            return {
                'grounded': False,
                'supported_claims': [],
                'unsupported_claims': ['Verification failed'],
                'contradictions': [],
                'confidence': 'low'
            }
    
    def filter_hallucinations(
        self,
        answer: str,
        verification: Dict
    ) -> str:
        """
        Remove unsupported claims from answer.
        """
        if verification['grounded']:
            return answer
        
        # If not grounded, return only supported claims
        supported = verification.get('supported_claims', [])
        
        if not supported:
            return "I cannot provide a reliable answer based on the available context."
        
        return "Based on the context: " + " ".join(supported)

# Usage
detector = HallucinationDetector(llm_client)

verification = detector.verify_answer_grounding(question, answer, context)

if not verification['grounded']:
    print("Warning: Answer contains unsupported claims:")
    print(verification['unsupported_claims'])
    
    # Filter hallucinations
    filtered_answer = detector.filter_hallucinations(answer, verification)
```

### Answer Consistency Check

```python
class ConsistencyChecker:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def check_consistency(
        self,
        question: str,
        answer1: str,
        answer2: str
    ) -> Dict:
        """
        Check if two answers to same question are consistent.
        
        Useful for testing determinism and reliability.
        """
        prompt = f"""Compare these two answers to the same question for consistency.

Question: {question}

Answer 1:
{answer1}

Answer 2:
{answer2}

Respond in JSON:
{{
    "consistent": true/false,
    "differences": ["What differs between answers"],
    "semantic_similarity": "high|medium|low"
}}

Comparison:"""

        response = self.llm.generate(prompt, temperature=0.0)
        
        try:
            return json.loads(response)
        except:
            return {
                'consistent': False,
                'differences': ['Comparison failed'],
                'semantic_similarity': 'unknown'
            }
    
    def test_determinism(
        self,
        question: str,
        context: str,
        num_trials: int = 3
    ) -> Dict:
        """
        Test if answer generation is deterministic.
        """
        answers = []
        
        for _ in range(num_trials):
            answer = self.llm.generate(
                PromptTemplates.CITED_QA.format(
                    context=context,
                    question=question
                ),
                temperature=0.0  # Should be deterministic
            )
            answers.append(answer)
        
        # Check if all answers are identical
        all_identical = all(a == answers[0] for a in answers)
        
        # Check semantic consistency
        consistency_scores = []
        for i in range(1, len(answers)):
            check = self.check_consistency(question, answers[0], answers[i])
            consistency_scores.append(check)
        
        return {
            'deterministic': all_identical,
            'answers': answers,
            'consistency_checks': consistency_scores
        }

# Usage
checker = ConsistencyChecker(llm_client)

# Test determinism
result = checker.test_determinism(question, context, num_trials=3)

if result['deterministic']:
    print("✓ Answer generation is deterministic")
else:
    print("✗ Answer generation is non-deterministic")
    print("Differences:", result['consistency_checks'])
```

## Complete RAG Answer Pipeline

```python
# complete_pipeline.py
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RAGConfig:
    temperature: float = 0.0
    max_tokens: int = 500
    enable_verification: bool = True
    enable_conflict_detection: bool = True
    enable_scope_check: bool = True
    min_confidence_threshold: float = 0.5

class CompleteRAGAnswerer:
    def __init__(
        self,
        llm_client,
        config: RAGConfig = None
    ):
        self.llm = llm_client
        self.config = config or RAGConfig()
        
        # Initialize components
        self.answerer = RAGAnswerer(llm_client)
        self.formatter = ContextFormatter()
        self.citation_extractor = CitationExtractor()
        self.context_analyzer = ContextAnalyzer(llm_client)
        self.conflict_handler = ConflictHandler(llm_client)
        self.scope_detector = ScopeDetector(llm_client)
        self.hallucination_detector = HallucinationDetector(llm_client)
    
    def generate(
        self,
        question: str,
        retrieved_chunks: List[Dict]
    ) -> Dict:
        """
        Complete RAG answer generation pipeline with quality checks.
        
        Returns:
            {
                'answer': str,
                'confidence': str,
                'sources': List[int],
                'metadata': Dict
            }
        """
        # 1. Format context
        context = self.formatter.format_with_sources(retrieved_chunks)
        
        # 2. Check scope (optional)
        if self.config.enable_scope_check:
            scope_analysis = self.scope_detector.is_in_scope(question, context)
            
            if not scope_analysis['in_scope']:
                return {
                    'answer': self.scope_detector.generate_out_of_scope_response(
                        question, scope_analysis
                    ),
                    'confidence': 'none',
                    'sources': [],
                    'metadata': {
                        'out_of_scope': True,
                        'reason': scope_analysis['reason']
                    }
                }
        
        # 3. Check for conflicts (optional)
        conflicts = None
        if self.config.enable_conflict_detection:
            conflicts = self.conflict_handler.detect_conflicts(
                question,
                retrieved_chunks
            )
        
        # 4. Generate answer
        if conflicts and conflicts['has_conflicts']:
            answer_text = self.conflict_handler.handle_conflicting_context(
                question, context
            )
        else:
            # Check context sufficiency
            assessment = self.context_analyzer.assess_context_sufficiency(
                question, context
            )
            
            if not assessment['sufficient']:
                return {
                    'answer': "I cannot provide a complete answer based on the available context.",
                    'confidence': 'low',
                    'sources': [],
                    'metadata': {
                        'insufficient_context': True,
                        'missing_info': assessment.get('missing_info', [])
                    }
                }
            
            # Generate answer
            answer_text = self.answerer.generate_answer(
                question,
                context,
                temperature=self.config.temperature
            )
        
        # 5. Extract and validate citations
        citations = self.citation_extractor.extract_citations(answer_text)
        is_valid, citation_errors = self.citation_extractor.validate_citations(
            answer_text,
            len(retrieved_chunks)
        )
        
        # 6. Verify grounding (optional)
        verification = None
        if self.config.enable_verification:
            verification = self.hallucination_detector.verify_answer_grounding(
                question, answer_text, context
            )
            
            if not verification['grounded']:
                # Filter hallucinations
                answer_text = self.hallucination_detector.filter_hallucinations(
                    answer_text, verification
                )
        
        # 7. Determine confidence
        confidence = self._calculate_confidence(
            assessment if not conflicts else {'confidence': 'medium'},
            verification,
            len(citations)
        )
        
        # 8. Build response
        return {
            'answer': answer_text,
            'confidence': confidence,
            'sources': citations,
            'metadata': {
                'has_conflicts': conflicts['has_conflicts'] if conflicts else False,
                'citation_valid': is_valid,
                'citation_errors': citation_errors,
                'grounded': verification['grounded'] if verification else None,
                'num_sources_used': len(citations),
                'total_sources': len(retrieved_chunks)
            }
        }
    
    def _calculate_confidence(
        self,
        sufficiency_assessment: Dict,
        verification: Optional[Dict],
        num_citations: int
    ) -> str:
        """Calculate overall confidence score."""
        # Start with context sufficiency
        confidence_map = {'high': 3, 'medium': 2, 'low': 1}
        score = confidence_map.get(sufficiency_assessment.get('confidence', 'low'), 1)
        
        # Factor in verification
        if verification and not verification['grounded']:
            score = min(score, 1)  # Cap at low if not grounded
        
        # Factor in citations
        if num_citations == 0:
            score = min(score, 1)  # No citations = low confidence
        
        # Map back to confidence level
        if score >= 3:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'

# Usage
config = RAGConfig(
    enable_verification=True,
    enable_conflict_detection=True,
    enable_scope_check=True,
    min_confidence_threshold=0.5
)

rag_answerer = CompleteRAGAnswerer(llm_client, config)

result = rag_answerer.generate(
    question="How do I install the software?",
    retrieved_chunks=retrieved_chunks
)

print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Sources: {result['sources']}")
print(f"Metadata: {result['metadata']}")
```

## Multi-turn Conversation

**Handle follow-up questions with conversation context**:

```python
# conversation.py
from typing import List, Dict

class ConversationalRAG:
    def __init__(self, rag_answerer, retriever):
        self.answerer = rag_answerer
        self.retriever = retriever
        self.conversation_history: List[Dict] = []
    
    def answer_with_history(
        self,
        question: str,
        max_history: int = 3
    ) -> Dict:
        """
        Answer question considering conversation history.
        """
        # Build conversation context
        conversation_context = self._build_conversation_context(max_history)
        
        # Expand query with conversation context for retrieval
        expanded_query = self._expand_query_with_context(
            question,
            conversation_context
        )
        
        # Retrieve with expanded query
        retrieval_result = self.retriever.retrieve(expanded_query)
        
        # Generate answer with conversation awareness
        prompt = f"""Previous conversation:
{conversation_context}

Context from knowledge base:
{retrieval_result['context']}

Current question: {question}

Instructions:
- Consider the conversation history for context
- Answer based on the provided knowledge base context
- Use citations [N] to reference sources
- If the question references previous answers, acknowledge that

Answer:"""
        
        answer = self.answerer.llm.generate(prompt, temperature=0.0)
        
        # Store in history
        self.conversation_history.append({
            'question': question,
            'answer': answer,
            'sources': retrieval_result['results']
        })
        
        return {
            'answer': answer,
            'sources': retrieval_result['results'],
            'conversation_context': conversation_context
        }
    
    def _build_conversation_context(self, max_history: int) -> str:
        """Build conversation context string."""
        if not self.conversation_history:
            return ""
        
        recent_history = self.conversation_history[-max_history:]
        
        context_parts = []
        for turn in recent_history:
            context_parts.append(f"Q: {turn['question']}")
            context_parts.append(f"A: {turn['answer']}")
        
        return "\n\n".join(context_parts)
    
    def _expand_query_with_context(
        self,
        question: str,
        conversation_context: str
    ) -> str:
        """
        Expand current question with conversation context.
        
        E.g., "How do I do that?" -> "How do I install the software?"
        """
        if not conversation_context:
            return question
        
        # Use LLM to expand query
        prompt = f"""Given the conversation history, rewrite the current question to be self-contained.

Conversation history:
{conversation_context}

Current question: {question}

Rewrite the question to include necessary context:"""

        expanded = self.answerer.llm.generate(prompt, temperature=0.0)
        return expanded

# Usage
conv_rag = ConversationalRAG(rag_answerer, retriever)

# First question
result1 = conv_rag.answer_with_history("How do I install the software?")

# Follow-up question (references previous context)
result2 = conv_rag.answer_with_history("What if it fails?")
# Internally expands to: "What if software installation fails?"

# Another follow-up
result3 = conv_rag.answer_with_history("Are there any prerequisites?")
# Expands to: "Are there any prerequisites for software installation?"
```

## Streaming Responses

**Stream answers for better UX**:

```python
# streaming.py
from typing import Generator, Dict

class StreamingRAGAnswerer:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def stream_answer(
        self,
        question: str,
        context: str
    ) -> Generator[str, None, None]:
        """
        Stream answer generation token by token.
        """
        prompt = PromptTemplates.CITED_QA.format(
            context=context,
            question=question
        )
        
        # Stream from LLM
        for token in self.llm.stream_generate(prompt, temperature=0.0):
            yield token
    
    def stream_with_sources(
        self,
        question: str,
        retrieved_chunks: List[Dict]
    ) -> Generator[Dict, None, None]:
        """
        Stream answer with source information.
        
        Yields:
            {'type': 'sources', 'data': [...]} - First, send sources
            {'type': 'token', 'data': '...'} - Then stream tokens
            {'type': 'complete', 'data': {...}} - Finally, send metadata
        """
        # First, send sources
        yield {
            'type': 'sources',
            'data': [
                {
                    'id': i + 1,
                    'source': chunk.get('metadata', {}).get('source'),
                    'score': chunk.get('score')
                }
                for i, chunk in enumerate(retrieved_chunks)
            ]
        }
        
        # Stream answer tokens
        context = ContextFormatter.format_with_sources(retrieved_chunks)
        
        full_answer = ""
        for token in self.stream_answer(question, context):
            full_answer += token
            yield {
                'type': 'token',
                'data': token
            }
        
        # Extract citations from complete answer
        citations = CitationExtractor.extract_citations(full_answer)
        
        # Send completion metadata
        yield {
            'type': 'complete',
            'data': {
                'citations': citations,
                'answer_length': len(full_answer)
            }
        }

# Usage (with async framework like FastAPI)
@app.get("/answer/stream")
async def stream_answer(question: str):
    chunks = retriever.retrieve(question)
    
    async def generate():
        for chunk in streaming_answerer.stream_with_sources(question, chunks):
            yield json.dumps(chunk) + "\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

## Production Monitoring

```python
# monitoring.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import time

@dataclass
class AnswerMetrics:
    question: str
    answer_length: int
    num_citations: int
    confidence: str
    generation_time_ms: float
    grounded: bool
    timestamp: datetime = field(default_factory=datetime.now)

class AnswerMonitor:
    def __init__(self):
        self.metrics: List[AnswerMetrics] = []
    
    def log_answer(self, metrics: AnswerMetrics) -> None:
        """Log answer generation metrics."""
        self.metrics.append(metrics)
    
    def get_stats(self) -> Dict:
        """Get aggregate statistics."""
        if not self.metrics:
            return {}
        
        total = len(self.metrics)
        grounded_count = sum(1 for m in self.metrics if m.grounded)
        
        gen_times = [m.generation_time_ms for m in self.metrics]
        citation_counts = [m.num_citations for m in self.metrics]
        
        confidence_dist = {
            'high': sum(1 for m in self.metrics if m.confidence == 'high'),
            'medium': sum(1 for m in self.metrics if m.confidence == 'medium'),
            'low': sum(1 for m in self.metrics if m.confidence == 'low')
        }
        
        return {
            'total_answers': total,
            'grounded_rate': grounded_count / total,
            'avg_generation_time_ms': sum(gen_times) / len(gen_times),
            'p95_generation_time_ms': sorted(gen_times)[int(len(gen_times) * 0.95)],
            'avg_citations': sum(citation_counts) / len(citation_counts),
            'confidence_distribution': confidence_dist
        }

# Usage with answer generation
monitor = AnswerMonitor()

def generate_with_monitoring(question: str, chunks: List[Dict]) -> Dict:
    start_time = time.time()
    
    result = rag_answerer.generate(question, chunks)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    monitor.log_answer(AnswerMetrics(
        question=question,
        answer_length=len(result['answer']),
        num_citations=len(result['sources']),
        confidence=result['confidence'],
        generation_time_ms=elapsed_ms,
        grounded=result['metadata'].get('grounded', True)
    ))
    
    return result

# Check stats periodically
stats = monitor.get_stats()
print(f"Grounded rate: {stats['grounded_rate']:.1%}")
print(f"Avg generation time: {stats['avg_generation_time_ms']:.0f}ms")
```

## Common Patterns

### Question Answering

```python
def qa_pattern(question: str) -> str:
    """Standard Q&A pattern."""
    chunks = retriever.retrieve(question, top_k=5)
    result = rag_answerer.generate(question, chunks)
    return result['answer']
```

### Summarization

```python
def summarization_pattern(document_id: str) -> str:
    """Summarize a specific document."""
    # Retrieve all chunks from document
    chunks = retriever.retrieve(
        query="",  # Empty query
        filters={'document_id': document_id}
    )
    
    context = formatter.format_with_sources(chunks)
    
    prompt = f"""Provide a comprehensive summary of this document.

Document content:
{context}

Create a structured summary covering:
1. Main topics
2. Key points
3. Important details

Summary:"""
    
    return llm.generate(prompt, temperature=0.0)
```

### Fact Verification

```python
def fact_verification_pattern(claim: str) -> Dict:
    """Verify a claim against knowledge base."""
    # Retrieve relevant context
    chunks = retriever.retrieve(claim, top_k=10)
    context = formatter.format_with_sources(chunks)
    
    prompt = f"""Verify if the following claim is supported by the context.

Context:
{context}

Claim: {claim}

Respond in JSON:
{{
    "verdict": "supported|contradicted|insufficient_evidence",
    "explanation": "Explain the verdict",
    "supporting_sources": [Source numbers that support/contradict],
    "confidence": "high|medium|low"
}}

Verification:"""
    
    response = llm.generate(prompt, temperature=0.0)
    return json.loads(response)
```

## Production Checklist

Before deploying:

- [ ] **Low Temperature**: Use temperature=0.0 for deterministic outputs
- [ ] **Citation Required**: All claims must reference sources with [N] format
- [ ] **Grounding Verification**: Validate answers against context
- [ ] **Scope Detection**: Handle out-of-scope questions gracefully
- [ ] **Conflict Handling**: Address conflicting information explicitly
- [ ] **Insufficient Context**: State when context doesn't support answer
- [ ] **No Hallucinations**: Never generate information not in context
- [ ] **Source Attribution**: Enable users to verify claims
- [ ] **Confidence Scoring**: Indicate answer reliability
- [ ] **Monitoring**: Log generation metrics and quality indicators
- [ ] **Error Handling**: Graceful degradation when components fail
- [ ] **Consistency**: Same question + context = same answer

## Quick Reference

### Answer Generation Pipeline

1. **Format Context** → Structure with source numbers
2. **Check Scope** → Verify question is answerable
3. **Detect Conflicts** → Identify contradicting sources
4. **Generate Answer** → Use grounded prompt with low temperature
5. **Extract Citations** → Find all [N] references
6. **Validate Citations** → Ensure they reference valid sources
7. **Verify Grounding** → Check answer against context
8. **Calculate Confidence** → Assess answer reliability
9. **Return Result** → Answer + sources + metadata

### Quality Signals

**High Quality**:
- Multiple citations from context
- No unsupported claims
- Acknowledges limitations
- Specific and actionable

**Low Quality**:
- No citations or invalid citations
- Vague or generic
- Information not in context
- Overconfident with insufficient evidence

### Prompt Engineering Tips

- **Be explicit**: "Answer ONLY based on context"
- **Require citations**: "Cite sources using [N]"
- **Handle uncertainty**: "If context insufficient, say so"
- **Low temperature**: 0.0 for consistency
- **Structured output**: JSON for parsing
- **Examples**: Few-shot examples improve quality

Build RAG answerers that are **accurate, verifiable, and production-ready**.
