"""
Keyword BM25 Baseline for AI Model Discovery

Baseline: keyword search over graph metadata fields with BM25 scoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import math
import re

from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import DCTERMS, DCAT, FOAF, RDFS

try:
    from rdflib.namespace import ODRL
except ImportError:
    ODRL = Namespace("http://www.w3.org/ns/odrl/2/")


DEFAULT_PROPERTY_URIS = [
    DCTERMS.title,
    DCTERMS.description,
    DCTERMS.source,
    DCTERMS.creator,
    DCTERMS.identifier,
    DCTERMS.subject,
    DCTERMS.language,
    DCAT.keyword,
    URIRef("http://purl.org/pionera/daimo#task"),
    URIRef("http://purl.org/pionera/daimo#library"),
    URIRef("http://purl.org/pionera/daimo#framework"),
    URIRef("http://purl.org/pionera/daimo#licenseName"),
    URIRef("http://purl.org/pionera/daimo#source"),
    URIRef("http://purl.org/pionera/daimo#modelType"),
    URIRef("http://purl.org/pionera/daimo#baseModel"),
]

LABEL_PREDICATES = [
    FOAF.name,
    RDFS.label,
    DCTERMS.title,
    DCTERMS.identifier,
]


@dataclass
class SearchResult:
    model_uri: str
    score: float


class KeywordBM25Baseline:
    def __init__(
        self,
        graph_path: Path,
        property_uris: Optional[List[URIRef]] = None,
        k1: float = 1.5,
        b: float = 0.75,
        min_token_len: int = 2,
    ):
        self.graph = Graph()
        self.graph.parse(str(graph_path), format="turtle")
        self.DAIMO = Namespace("http://purl.org/pionera/daimo#")

        self.property_uris = property_uris or DEFAULT_PROPERTY_URIS
        self.k1 = k1
        self.b = b
        self.min_token_len = min_token_len

        self._doc_tokens: Dict[str, List[str]] = {}
        self._doc_len: Dict[str, int] = {}
        self._doc_tf: Dict[str, Dict[str, int]] = {}
        self._df: Dict[str, int] = {}
        self._idf: Dict[str, float] = {}
        self._inverted: Dict[str, List[Tuple[str, int]]] = {}
        self._avgdl: float = 0.0

        self._build_index()

    def _build_index(self) -> None:
        models = list(self.graph.subjects(RDF.type, self.DAIMO.Model))
        total_len = 0

        for model in models:
            model_uri = str(model)
            text = self._extract_model_text(model)
            tokens = self._tokenize(text)
            if not tokens:
                continue

            self._doc_tokens[model_uri] = tokens
            self._doc_len[model_uri] = len(tokens)
            total_len += len(tokens)

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self._doc_tf[model_uri] = tf

            for term in set(tokens):
                self._df[term] = self._df.get(term, 0) + 1

        doc_count = max(len(self._doc_len), 1)
        self._avgdl = total_len / doc_count

        for term, df in self._df.items():
            # BM25 IDF with smoothing
            self._idf[term] = math.log((doc_count - df + 0.5) / (df + 0.5) + 1.0)

        for doc_uri, tf in self._doc_tf.items():
            for term, freq in tf.items():
                self._inverted.setdefault(term, []).append((doc_uri, freq))

    def _extract_model_text(self, model: URIRef) -> str:
        values: List[str] = []

        for prop in self.property_uris:
            for obj in self.graph.objects(model, prop):
                values.extend(self._object_texts(obj))

        # License via ODRL policy node
        for policy in self.graph.objects(model, ODRL.hasPolicy):
            for obj in self.graph.objects(policy, DCTERMS.identifier):
                values.extend(self._object_texts(obj))

        return " ".join(values)

    def _object_texts(self, obj) -> List[str]:
        if isinstance(obj, Literal):
            return [str(obj)]

        texts: List[str] = []
        if isinstance(obj, URIRef):
            for pred in LABEL_PREDICATES:
                for label in self.graph.objects(obj, pred):
                    if isinstance(label, Literal):
                        texts.append(str(label))

            if not texts:
                texts.append(self._uri_to_token(obj))
        return texts

    def _uri_to_token(self, uri: URIRef) -> str:
        s = str(uri)
        if "#" in s:
            return s.rsplit("#", 1)[-1]
        return s.rsplit("/", 1)[-1]

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return [t for t in tokens if len(t) >= self.min_token_len]

    def search(self, query_tokens: Iterable[str], top_k: int = 5) -> List[SearchResult]:
        tokens = [t.lower() for t in query_tokens if t]
        if not tokens:
            return []

        scores: Dict[str, float] = {}
        for term in tokens:
            if term not in self._idf:
                continue
            idf = self._idf[term]
            postings = self._inverted.get(term, [])
            for doc_uri, tf in postings:
                dl = self._doc_len[doc_uri]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (dl / self._avgdl))
                score = idf * (tf * (self.k1 + 1.0) / denom)
                scores[doc_uri] = scores.get(doc_uri, 0.0) + score

        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        return [SearchResult(model_uri=uri, score=score) for uri, score in ranked[:top_k]]
