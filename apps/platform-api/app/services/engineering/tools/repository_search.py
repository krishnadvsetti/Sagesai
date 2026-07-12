import re
from pathlib import Path

from app.services.engineering.tools.base import BaseTool


class RepositorySearchTool(BaseTool):
    name = "repository_search"
    description = (
        "Search the Sagesai source repository for code, "
        "configuration, classes, functions, and text."
    )

    ALLOWED_EXTENSIONS = {
        ".py",
        ".toml",
        ".yaml",
        ".yml",
        ".json",
        ".md",
        ".txt",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
    }

    STOP_WORDS = {
        "the",
        "and",
        "for",
        "from",
        "with",
        "usage",
        "source",
        "code",
        "repository",
        "sagesai",
        "current",
        "currently",
        "analyze",
        "using",
        "used",
    }

    def __init__(
        self,
        repository_root: Path | None = None,
    ) -> None:
        self.repository_root = (
            repository_root
            or Path(__file__).resolve().parents[6]
        )

    async def execute(
        self,
        query: str,
        max_results: int = 10,
    ) -> dict:
        keywords = [
            word.lower()
            for word in re.findall(r"[A-Za-z0-9_]+", query)
            if len(word) >= 3
            and word.lower() not in self.STOP_WORDS
        ]

        if not keywords:
            keywords = [
                word.lower()
                for word in re.findall(
                    r"[A-Za-z0-9_]+",
                    query,
                )
                if len(word) >= 3
            ]

        matches = []

        for path in self.repository_root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                continue

            if any(
                part in {
                    ".git",
                    ".venv",
                    "node_modules",
                    "__pycache__",
                    "artifacts",
                }
                for part in path.parts
            ):
                continue

            try:
                content = path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )
            except OSError:
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1,
            ):
                line_lower = line.lower()

                matched_keywords = [
                    keyword
                    for keyword in keywords
                    if keyword in line_lower
                ]

                if matched_keywords:
                    matches.append(
                        {
                            "file": str(
                                path.relative_to(
                                    self.repository_root
                                )
                            ),
                            "line": line_number,
                            "content": line.strip(),
                            "matched_keywords": matched_keywords,
                            "relevance_score": len(
                                matched_keywords
                            ),
                        }
                    )

        matches.sort(
            key=lambda item: item["relevance_score"],
            reverse=True,
        )

        selected_matches = matches[:max_results]

        return {
            "tool": self.name,
            "query": query,
            "search_keywords": keywords,
            "matches": selected_matches,
            "match_count": len(selected_matches),
        }