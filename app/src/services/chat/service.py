from app.src.domain.chat import ChatRequest, ChatResponse, Citation
from app.src.services.search.service import SearchService
from app.src.services.chat.context_builder import ContextBuilder
from app.src.services.chat.orchestrator import LLMOrchestrator
from app.src.services.chat.query import QueryProcessor
from app.src.services.chat.citation_analyzer import CitationAnalyzer
from app.src.services.chat.context_expander import ContextExpander
from app.src.services.chat.chat_history_processor import ChatHistoryProcessor
from app.src.config import get_settings
from app.src.utils.logs import logger

class ChatService:
    def __init__(self):
        self.search_service = SearchService()
        self.context_builder = ContextBuilder()
        self.llm = LLMOrchestrator()
        self.query_processor = QueryProcessor()
        self.citation_analyzer = CitationAnalyzer()
        self.context_expander = ContextExpander()
        self.chat_history_processor = ChatHistoryProcessor()
        self.settings = get_settings()
        logger.info("Chat service initialized with all components including chat history processor")

    def chat(self, request: ChatRequest) -> ChatResponse:
        try:
            logger.info(f"Starting chat request - Query: '{request.query[:50]}...', K: {request.k}, History messages: {len(request.chat_history)}")

            if not request.query:
                logger.error("Empty query received in chat request")
                return ChatResponse(
                    answer="Please provide a valid question.",
                    citations=[],
                    rewritten_query=""
                )

            processed_query = self.query_processor.process_query(request.query)
            if not processed_query:
                logger.warning(f"Query processing failed for: '{request.query}'")
                return ChatResponse(
                    answer="Please provide a valid question. Your query should be between 2-500 characters.",
                    citations=[],
                    rewritten_query=request.query
                )

            logger.info(f"Query processed successfully: '{processed_query}'")
            chat_history_context = self.chat_history_processor.extract_relevant_context(
                request.chat_history,
            )
            initial_search_results = self.search_service.search(
                query=processed_query,
                k=request.k
            )
            if not initial_search_results:
                logger.error(f"No search results found for query: '{processed_query}'")
                return ChatResponse(
                    answer="I couldn't find any relevant information for your question. Please try rephrasing or asking about GitLab's handbook/direction topics.",
                    citations=[],
                    rewritten_query=processed_query
                )
            logger.info(f"Initial search completed - Found {len(initial_search_results)} results")

            relevant_citation_indices = self.citation_analyzer.analyze_relevant_citations(
                processed_query,
                initial_search_results
            )

            if not relevant_citation_indices:
                logger.error("No relevant citation indices determined")
                return ChatResponse(
                    answer="I couldn't determine which sources are relevant to your question. Please try rephrasing or asking about GitLab's handbook topics.",
                    citations=[],
                    rewritten_query=processed_query
                )

            logger.info(f"Citation analysis completed - Selected indices: {relevant_citation_indices}")
            expanded_search_results = self.context_expander.expand_context(
                initial_search_results,
                relevant_citation_indices,
                processed_query
            )
            if not expanded_search_results:
                logger.error("No expanded search results generated")
                return ChatResponse(
                    answer="I couldn't find any relevant information for your question. Please try rephrasing or asking about GitLab's handbook topics.",
                    citations=[],
                    rewritten_query=processed_query
                )

            logger.info(f"Context expansion completed - Final results: {len(expanded_search_results)} documents")
            context = self.context_builder.build_context(expanded_search_results)
            logger.info(f"Context built successfully - Length: {len(context)} characters")
            prompt = self.llm.build_prompt(processed_query, context, chat_history_context)
            logger.info("Sending prompt to LLM for answer generation, prompt: " + prompt)
            answer = self.llm.generate(prompt)
            logger.info(f"LLM response generated successfully - Length: {len(answer)} characters, Answer preview: '{answer}...'")

            citations = []
            for i, result in enumerate(expanded_search_results, 1):
                citation = Citation(
                    id=result['id'],
                    url=result.get('url', ''),
                    title=result.get('title', 'Untitled'),
                    index=i,
                    total=len(expanded_search_results),
                    snippet=result.get('content', '')
                )
                citations.append(citation)
            logger.info(f"Citations prepared successfully - Count: {len(citations)}")
            final_response = ChatResponse(
                answer=answer,
                citations=citations,
                rewritten_query=processed_query
            )
            logger.info("Chat request completed successfully")
            return final_response

        except Exception as e:
            logger.error(f"Unexpected error in chat service: {str(e)}")
            return ChatResponse(
                answer="Sorry, I encountered a technical error. Please try again later.",
                citations=[],
                rewritten_query=request.query if request.query else ""
            )
