from typing import List, Dict, Any
from app.src.config import get_settings

class ContextBuilder:
    def __init__(self):
        self.settings = get_settings()

    def build_context(self, search_results: List[Dict[str, Any]]) -> str:
        if not search_results:
            return ""

        context_parts = []
        for i, result in enumerate(search_results, start=1):
            title = result.get('title', '')
            url = result.get('url', '')
            content = result.get('content', '')

            header = f"Citation [{i}] | Titled: {title}"
            if url:
                header += f" | Url: ({url})"

            context_parts.append(f" -----\n{header}\n{content}")

        return "\n\n".join(context_parts)
