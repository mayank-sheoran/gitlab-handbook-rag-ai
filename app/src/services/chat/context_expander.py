from typing import List, Dict, Any
from app.src.services.chat.document_retriever import DocumentRetriever
from app.src.config import get_settings
from app.src.utils.logs import logger

class ContextExpander:
    def __init__(self):
        self.settings = get_settings()
        self.document_retriever = DocumentRetriever()

    def _extract_citation_sources(self, search_results: List[Dict[str, Any]], relevant_indices: List[int]) -> List[Dict[str, Any]]:
        try:
            logger.debug(f"Extracting citation sources for indices: {relevant_indices}")

            if not search_results:
                logger.warning("No search results provided for citation extraction")
                return []

            if not relevant_indices:
                logger.warning("No relevant indices provided for citation extraction")
                return []

            relevant_citations = []
            for index in relevant_indices:
                if 1 <= index <= len(search_results):
                    citation = search_results[index - 1]
                    relevant_citations.append(citation)
                    logger.debug(f"Extracted citation {index}: {citation.get('title', 'Untitled')}")
                else:
                    logger.warning(f"Invalid citation index {index} for {len(search_results)} results")

            logger.info(f"Successfully extracted {len(relevant_citations)} relevant citations")
            return relevant_citations

        except Exception as e:
            logger.error(f"Error extracting citation sources: {str(e)}")
            return []

    def _get_full_document_for_citation(self, citation: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            citation_id = citation.get('id', 'unknown')
            citation_title = citation.get('title', 'Untitled')
            logger.info(f"Retrieving full document for citation: {citation_title} (ID: {citation_id})")

            if not citation:
                logger.error("Empty citation provided for document retrieval")
                return []

            full_document_chunks = self.document_retriever.get_full_document(citation)

            if not full_document_chunks:
                logger.warning(f"No document chunks retrieved for citation: {citation_id}")
                return [citation]

            if len(full_document_chunks) == 1 and full_document_chunks[0] == citation:
                logger.warning(f"Only original citation returned for: {citation_id}")
            else:
                logger.info(f"Retrieved {len(full_document_chunks)} chunks for citation: {citation_id}")

            return full_document_chunks

        except Exception as e:
            logger.error(f"Error retrieving full document for citation: {str(e)}")
            return [citation]

    def expand_context(self, search_results: List[Dict[str, Any]], relevant_indices: List[int], original_query: str) -> List[Dict[str, Any]]:
        try:
            logger.info(f"Starting context expansion - Query: '{original_query[:50]}...', Indices: {relevant_indices}")

            if not search_results:
                logger.error("No search results provided for context expansion")
                raise ValueError("Search results cannot be empty for context expansion")

            if not relevant_indices:
                logger.error("No relevant indices provided for context expansion")
                raise ValueError("Relevant indices cannot be empty for context expansion")

            if not original_query or not original_query.strip():
                logger.error("Empty or invalid query provided for context expansion")
                raise ValueError("Query cannot be empty for context expansion")

            relevant_citations = self._extract_citation_sources(search_results, relevant_indices)

            if not relevant_citations:
                logger.error("No relevant citations extracted for context expansion")
                raise ValueError("No relevant citations found for context expansion")

            expanded_results = []
            seen_content = set()

            for i, citation in enumerate(relevant_citations):
                try:
                    logger.debug(f"Processing citation {i+1}/{len(relevant_citations)}")
                    full_document_chunks = self._get_full_document_for_citation(citation)

                    for chunk in full_document_chunks:
                        content = chunk.get('content', '')
                        if content and content not in seen_content:
                            seen_content.add(content)
                            expanded_results.append(chunk)
                        else:
                            logger.debug("Skipping duplicate or empty content chunk")
                except Exception as e:
                    logger.error(f"Error processing citation {i+1}: {str(e)}")
                    continue

            if not expanded_results:
                logger.error("No expanded results generated from relevant citations")
                raise ValueError("Context expansion failed to generate any results")

            final_results = expanded_results
            logger.info(f"Context expansion completed successfully - Final results: {len(final_results)} documents")
            return final_results
        except Exception as e:
            logger.error(f"Validation error in context expansion: {str(e)}")
