from typing import TypedDict


class Finding(TypedDict):
    query: str
    title: str
    url: str
    snippet: str


class ResearchState(TypedDict):
    topic: str
    queries: list[str]
    findings: list[Finding]
    report: str
