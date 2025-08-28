import google.generativeai as genai
import os
import re
from typing import List, Dict, Any
from app.src.config import get_settings
from app.src.utils.logs import logger

class CitationAnalyzer:
    def __init__(self):
        self.settings = get_settings()
        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self.model = genai.GenerativeModel(self.settings.gemini_model)
            logger.info("Citation analyzer initialized with Gemini model")
        else:
            self.model = None
            logger.error("GEMINI_API_KEY not configured for citation analyzer")

    def _build_query_analysis_prompt(self, query: str, search_results: List[Dict[str, Any]]) -> str:
        try:
            logger.debug("Building query analysis prompt")

            prompt_path = os.path.join(
                os.path.dirname(__file__),
                "system_prompts/query_system_prompt.txt"
            )

            if not os.path.exists(prompt_path):
                logger.error(f"Query system prompt file not found: {prompt_path}")
                raise FileNotFoundError(f"Query system prompt file not found: {prompt_path}")

            with open(prompt_path, 'r', encoding='utf-8') as file:
                prompt_template = file.read()

            if not prompt_template.strip():
                logger.error("Query system prompt template is empty")
                raise ValueError("Query system prompt template is empty")

            citations_text = ""
            for i, result in enumerate(search_results, 1):
                title = result.get('title', 'Untitled')
                content = result.get('content', '')
                citations_text += f"\n-----\nCitation [{i}] | Title: {title}\nContent: {content}\n-----\n"

            if not citations_text.strip():
                logger.error("No valid citations found for prompt building")
                raise ValueError("No valid citations found for prompt building")

            prompt = prompt_template.replace("{query}", query)
            prompt = prompt.replace("{citations}", citations_text)

            logger.debug(f"Query analysis prompt built successfully - Query length: {len(query)}, Citations: {len(search_results)}")
            return prompt

        except FileNotFoundError as e:
            logger.error(f"File not found error in prompt building: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error building query analysis prompt: {str(e)}")
            raise

    def _parse_citation_response(self, response: str) -> List[int]:
        try:
            logger.debug(f"Parsing citation response: {response}")
            if not response or not response.strip():
                logger.warning("Empty response received from citation analysis")
                return []
            response_clean = response.strip()
            numbers = re.findall(r'\d+', response_clean)
            if not numbers:
                logger.warning(f"No valid citation numbers found in response: {response_clean}")
                return []
            parsed_numbers = []
            for num_str in numbers:
                try:
                    num = int(num_str)
                    if num > 0:
                        parsed_numbers.append(num)
                except ValueError:
                    logger.warning(f"Invalid number format: {num_str}")
                    continue
            logger.debug(f"Parsed citation numbers: {parsed_numbers}")
            return parsed_numbers

        except Exception as e:
            logger.error(f"Error parsing citation response: {str(e)}")
            return []

    def analyze_relevant_citations(self, query: str, search_results: List[Dict[str, Any]]) -> List[int]:
        try:
            logger.info(f"Starting citation analysis - Query: '{query[:50]}...', Results: {len(search_results)}")
            if not self.model:
                raise ValueError("Gemini model not available for citation analysis")
            if not search_results:
                raise ValueError("No search results provided for citation analysis")
            if not query or not query.strip():
                raise ValueError("Query cannot be empty for citation analysis")

            prompt = self._build_query_analysis_prompt(query, search_results)
            logger.debug("Sending request to Gemini for citation analysis")
            logger.info("analysis prompt: " + prompt)
            response = self.model.generate_content(
                prompt,
                generation_config={"max_output_tokens": self.settings.answer_max_tokens}
            )
            if not response or not response.text:
                raise ValueError("No response received from Gemini for citation analysis")

            logger.info(f"Received response from Gemini: {response.text}")
            relevant_indices = self._parse_citation_response(response.text)
            valid_indices = [i for i in relevant_indices if 1 <= i <= len(search_results)]
            if not valid_indices:
                raise ValueError("No valid citation indices found in LLM response")
            final_indices = valid_indices[:2]
            logger.info(f"Citation analysis completed successfully - Selected indices: {final_indices}")
            return final_indices

        except ValueError as e:
            logger.error(f"Validation error in citation analysis: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in citation analysis: {str(e)}")
            fallback_indices = list(range(1, min(3, len(search_results) + 1)))
            logger.warning(f"Using fallback citation indices due to error: {fallback_indices}")
            return fallback_indices
