import json
import re
from pathlib import Path

from app.config import (
    VECTORSTORE_FOLDER,
    TOP_K
)

from app.services.embeddings import (
    EmbeddingService
)

from app.services.vector_store import (
    VectorStore
)


class Retriever:

    def __init__(self):

        print("\nInitializing retriever...")

        # -----------------------------------------------------
        # EMBEDDINGS
        # -----------------------------------------------------

        self.embedding_service = EmbeddingService()

        # -----------------------------------------------------
        # VECTOR STORE
        # -----------------------------------------------------

        self.vector_store = VectorStore()
        self.vector_store.load(VECTORSTORE_FOLDER)

        print(
            f"Loaded "
            f"{self.vector_store.index.ntotal} "
            f"vectors."
        )

        # -----------------------------------------------------
        # LOAD ALL DOCUMENTS
        #
        # This is important.
        #
        # FAISS is used for semantic candidates.
        # documents.json is used for keyword candidates.
        # -----------------------------------------------------

        self.documents = self.load_documents()

        print(
            f"Loaded "
            f"{len(self.documents)} "
            f"documents for hybrid retrieval."
        )

    # =========================================================
    # LOAD DOCUMENTS
    # =========================================================

    def load_documents(self):

        path = Path(
            VECTORSTORE_FOLDER
        ) / "documents.json"

        if not path.exists():

            print(
                f"documents.json not found: {path}"
            )

            return []

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            # Usually documents.json is a list
            if isinstance(data, list):

                return data

            # Support {"documents": [...]}
            if isinstance(data, dict):

                if isinstance(
                    data.get("documents"),
                    list
                ):

                    return data["documents"]

            print(
                "Unknown documents.json format."
            )

            return []

        except Exception as e:

            print(
                f"Error loading documents.json: {e}"
            )

            return []

    # =========================================================
    # NORMALIZE TEXT
    # =========================================================

    def normalize_text(self, text):

        if not text:
            return ""

        text = str(text).lower()

        replacements = {

            "vice-chancellor":
                "vice chancellor",

            "pro-chancellor":
                "pro chancellor",

            "b.tech":
                "btech",

            "b tech":
                "btech",

            "b.sc":
                "bsc",

            "b sc":
                "bsc",

            "m.sc":
                "msc",

            "m sc":
                "msc",

            "fee structures":
                "fee structure",

            "registered students":
                "registered students",

            "student count":
                "student count",

            "students count":
                "student count",

            "number of students":
                "student count",

            "count of students":
                "student count"
        }

        for old, new in replacements.items():

            text = text.replace(
                old,
                new
            )

        text = re.sub(
            r"[^a-z0-9]+",
            " ",
            text
        )

        return text.strip()

    # =========================================================
    # TOKENIZE
    # =========================================================

    def tokenize(self, text):

        normalized = self.normalize_text(text)

        return set(
            word
            for word in normalized.split()
            if len(word) > 1
        )

    # =========================================================
    # KEYWORD SCORE
    # =========================================================

    def keyword_score(
        self,
        query,
        document
    ):

        query_words = self.tokenize(
            query
        )

        document_words = self.tokenize(
            document.get("text", "")
        )

        if not query_words:

            return 0.0

        common = (
            query_words &
            document_words
        )

        return (
            len(common) /
            len(query_words)
        )

    # =========================================================
    # PHRASE SCORE
    # =========================================================

    def phrase_score(
        self,
        query,
        document
    ):

        query_text = self.normalize_text(
            query
        )

        document_text = self.normalize_text(
            document.get("text", "")
        )

        phrases = [

            "vice chancellor",

            "registered students",

            "student count",

            "fee structure",

            "academic calendar",

            "campus achievers",

            "student innovations",

            "student awards",

            "semester fee"
        ]

        score = 0.0

        for phrase in phrases:

            if phrase in query_text:

                if phrase in document_text:

                    score += 1.0

        return min(
            score,
            1.0
        )

    # =========================================================
    # CATEGORY DETECTION
    # =========================================================

    def detect_category(
        self,
        query
    ):

        query = self.normalize_text(
            query
        )

        # -----------------------------------------------------
        # OFFICIALS
        # -----------------------------------------------------

        if any(
            word in query
            for word in [
                "vice chancellor",
                "registrar",
                "pro chancellor",
                "chancellor",
                "dean",
                "director",
                "official"
            ]
        ):

            return "officials"

        # -----------------------------------------------------
        # STUDENT ANALYTICS
        # -----------------------------------------------------

        if any(
            phrase in query
            for phrase in [
                "registered students",
                "student count",
                "student count",
                "number students",
                "number of students",
                "count students",
                "students registered",
                "enrollment",
                "enrolment"
            ]
        ):

            return "student_analytics"

        # -----------------------------------------------------
        # STUDENT ACHIEVEMENTS
        # -----------------------------------------------------

        if any(
            phrase in query
            for phrase in [
                "campus achiever",
                "student achievement",
                "student award",
                "student innovation",
                "student success"
            ]
        ):

            return "student_innovations"

        # -----------------------------------------------------
        # FEES
        # -----------------------------------------------------

        if any(
            word in query
            for word in [
                "fee",
                "fees",
                "tuition",
                "semester fee",
                "annual fee",
                "admission fee"
            ]
        ):

            return "fees"

        # -----------------------------------------------------
        # NOTICES
        # -----------------------------------------------------

        if any(
            word in query
            for word in [
                "notice",
                "notices",
                "notification",
                "announcement",
                "latest update"
            ]
        ):

            return "notices"

        # -----------------------------------------------------
        # WEBSITE
        # -----------------------------------------------------

        if any(
            word in query
            for word in [
                "website",
                "online",
                "official website",
                "current information"
            ]
        ):

            return "website"

        return None

    # =========================================================
    # CATEGORY MATCH
    # =========================================================

    def category_match(
        self,
        category,
        document
    ):

        if category is None:

            return True

        text = self.normalize_text(
            document.get("text", "")
        )

        source = self.normalize_text(
            document.get("source", "")
        )

        document_type = document.get(
            "type",
            ""
        ).lower()

        # -----------------------------------------------------
        # OFFICIALS
        # -----------------------------------------------------

        if category == "officials":

            return (
                "vice chancellor" in text
                or "registrar" in text
                or "pro chancellor" in text
                or "chancellor" in text
                or "dean" in text
                or "director" in text
            )

        # -----------------------------------------------------
        # STUDENT ANALYTICS
        # -----------------------------------------------------

        if category == "student_analytics":

            return (
                "registered students" in text
                or "students" in text
                and (
                    "analytics" in text
                    or "registered" in text
                    or "active accounts" in text
                )
                or "student count" in text
            )

        # -----------------------------------------------------
        # STUDENT INNOVATIONS
        # -----------------------------------------------------

        if category == "student_innovations":

            return (
                "campus achiever" in text
                or "student innovation" in text
                or "student achievement" in text
                or "student award" in text
                or "student success" in text
            )

        # -----------------------------------------------------
        # FEES
        # -----------------------------------------------------

        if category == "fees":

            return (
                "fee" in text
                or "fees" in text
                or "tuition" in text
                or "fee structure" in text
            )

        # -----------------------------------------------------
        # NOTICES
        # -----------------------------------------------------

        if category == "notices":

            return (
                "notice" in text
                or "notification" in text
                or "announcement" in text
            )

        # -----------------------------------------------------
        # WEBSITE
        # -----------------------------------------------------

        if category == "website":

            return (
                document_type == "website"
                or "itmuniversity.ac.in" in source
            )

        return True

    # =========================================================
    # SOURCE BONUS
    # =========================================================

    def source_bonus(
        self,
        category,
        document
    ):

        source = document.get(
            "source",
            ""
        ).lower()

        text = self.normalize_text(
            document.get("text", "")
        )

        bonus = 0.0

        # -----------------------------------------------------
        # OFFICIALS
        # -----------------------------------------------------

        if category == "officials":

            if (
                "name_and_post" in source
                or "university_name_and_post" in source
                or "official" in source
            ):

                bonus += 1.5

            if (
                "vice chancellor" in text
                and "prof" in text
            ):

                bonus += 1.0

        # -----------------------------------------------------
        # STUDENT ANALYTICS
        # -----------------------------------------------------

        if category == "student_analytics":

            if "parakh.itmuniversity.ac.in" in source:

                bonus += 1.5

            if "registered students" in text:

                bonus += 1.5

            if "e parakh analytics" in text:

                bonus += 0.8

            if "analytics" in text:

                bonus += 0.3

        # -----------------------------------------------------
        # STUDENT ACHIEVERS
        # -----------------------------------------------------

        if category == "student_innovations":

            if "parakh.itmuniversity.ac.in" in source:

                bonus += 1.5

            if "campus achiever" in text:

                bonus += 1.5

        # -----------------------------------------------------
        # FEES
        # -----------------------------------------------------

        if category == "fees":

            if "fee structure" in source:

                bonus += 1.5

            if document.get(
                "type",
                ""
            ).lower() == "pdf":

                bonus += 0.3

        # -----------------------------------------------------
        # WEBSITE
        # -----------------------------------------------------

        if category == "website":

            if document.get(
                "type",
                ""
            ).lower() == "website":

                bonus += 0.8

        return bonus

    # =========================================================
    # EXACT MATCH
    # =========================================================

    def exact_match_score(
        self,
        query,
        document
    ):

        query_text = self.normalize_text(
            query
        )

        document_text = self.normalize_text(
            document.get("text", "")
        )

        score = 0.0

        # -----------------------------------------------------
        # VICE CHANCELLOR
        # -----------------------------------------------------

        if "vice chancellor" in query_text:

            if "vice chancellor" in document_text:

                score += 2.5

        # -----------------------------------------------------
        # REGISTERED STUDENTS
        # -----------------------------------------------------

        if (
            "registered students" in query_text
            or "student count" in query_text
            or "number of students" in query_text
            or "count of students" in query_text
        ):

            if "registered students" in document_text:

                score += 2.5

        # -----------------------------------------------------
        # CAMPUS ACHIEVER
        # -----------------------------------------------------

        if "campus achiever" in query_text:

            if "campus achiever" in document_text:

                score += 2.0

        # -----------------------------------------------------
        # FEE STRUCTURE
        # -----------------------------------------------------

        if "fee structure" in query_text:

            if "fee structure" in document_text:

                score += 2.0

        return score

    # =========================================================
    # DOCUMENT ID
    # =========================================================

    def document_id(
        self,
        document
    ):

        return (
            str(
                document.get(
                    "source",
                    ""
                )
            )
            + "|"
            + str(
                document.get(
                    "page",
                    0
                )
            )
            + "|"
            + str(
                document.get(
                    "chunk_id",
                    0
                )
            )
        )

    # =========================================================
    # RETRIEVE
    # =========================================================

    def retrieve(
        self,
        query,
        top_k=TOP_K
    ):

        print(
            f"\nSearching for: {query}"
        )

        # -----------------------------------------------------
        # CATEGORY
        # -----------------------------------------------------

        category = self.detect_category(
            query
        )

        print(
            f"Detected category: {category}"
        )

        # -----------------------------------------------------
        # EMPTY DATABASE
        # -----------------------------------------------------

        total_vectors = (
            self.vector_store
            .index
            .ntotal
        )

        if total_vectors == 0:

            print(
                "Vector database is empty."
            )

            return []

        # =====================================================
        # 1. SEMANTIC RETRIEVAL
        # =====================================================

        query_embedding = (
            self.embedding_service
            .generate_query_embedding(
                query
            )
        )

        semantic_k = min(
            50,
            total_vectors
        )

        semantic_results = (
            self.vector_store.search(
                query_embedding,
                top_k=semantic_k
            )
        )

        print(
            f"Semantic candidates: "
            f"{len(semantic_results)}"
        )

        # =====================================================
        # 2. KEYWORD RETRIEVAL OVER ALL DOCUMENTS
        # =====================================================

        keyword_candidates = []

        for document in self.documents:

            keyword = self.keyword_score(
                query,
                document
            )

            phrase = self.phrase_score(
                query,
                document
            )

            exact = self.exact_match_score(
                query,
                document
            )

            category_match = (
                self.category_match(
                    category,
                    document
                )
            )

            if (
                keyword > 0
                or phrase > 0
                or exact > 0
            ):

                keyword_candidates.append({

                    "document": document,

                    "distance": 999.0,

                    "keyword_score": keyword,

                    "phrase_score": phrase,

                    "exact_match_score": exact,

                    "category_match":
                        category_match,

                    "semantic_score": 0.0,

                    "retrieval_type":
                        "keyword"

                })

        print(
            f"Keyword candidates: "
            f"{len(keyword_candidates)}"
        )

        # =====================================================
        # 3. UNION SEMANTIC + KEYWORD
        # =====================================================

        candidates = {}

        # -----------------------------------------------------
        # Add semantic results
        # -----------------------------------------------------

        for result in semantic_results:

            document = result[
                "document"
            ]

            doc_id = self.document_id(
                document
            )

            distance = result[
                "distance"
            ]

            semantic_score = (
                1.0 /
                (1.0 + float(distance))
            )

            candidates[doc_id] = {

                "document":
                    document,

                "distance":
                    distance,

                "semantic_score":
                    semantic_score,

                "keyword_score":
                    self.keyword_score(
                        query,
                        document
                    ),

                "phrase_score":
                    self.phrase_score(
                        query,
                        document
                    ),

                "exact_match_score":
                    self.exact_match_score(
                        query,
                        document
                    ),

                "category_match":
                    self.category_match(
                        category,
                        document
                    ),

                "retrieval_type":
                    "semantic"

            }

        # -----------------------------------------------------
        # Add keyword results
        # -----------------------------------------------------

        for result in keyword_candidates:

            document = result[
                "document"
            ]

            doc_id = self.document_id(
                document
            )

            if doc_id in candidates:

                candidates[
                    doc_id
                ][
                    "keyword_score"
                ] = max(
                    candidates[
                        doc_id
                    ][
                        "keyword_score"
                    ],
                    result[
                        "keyword_score"
                    ]
                )

                candidates[
                    doc_id
                ][
                    "phrase_score"
                ] = max(
                    candidates[
                        doc_id
                    ][
                        "phrase_score"
                    ],
                    result[
                        "phrase_score"
                    ]
                )

                candidates[
                    doc_id
                ][
                    "exact_match_score"
                ] = max(
                    candidates[
                        doc_id
                    ][
                        "exact_match_score"
                    ],
                    result[
                        "exact_match_score"
                    ]
                )

                candidates[
                    doc_id
                ][
                    "retrieval_type"
                ] = "hybrid"

            else:

                candidates[
                    doc_id
                ] = result

        print(
            f"Combined candidates: "
            f"{len(candidates)}"
        )

        # =====================================================
        # 4. RERANK
        # =====================================================

        reranked = []

        for item in candidates.values():

            document = item[
                "document"
            ]

            semantic = item.get(
                "semantic_score",
                0.0
            )

            keyword = item.get(
                "keyword_score",
                0.0
            )

            phrase = item.get(
                "phrase_score",
                0.0
            )

            exact = item.get(
                "exact_match_score",
                0.0
            )

            category_match = item.get(
                "category_match",
                False
            )

            category_bonus = (
                0.5
                if category_match
                else 0.0
            )

            source_bonus = (
                self.source_bonus(
                    category,
                    document
                )
            )

            # -------------------------------------------------
            # FINAL HYBRID SCORE
            # -------------------------------------------------

            final_score = (

                semantic * 1.5

                + keyword * 1.5

                + phrase * 2.0

                + exact * 2.0

                + category_bonus

                + source_bonus
            )

            item[
                "final_score"
            ] = final_score

            item[
                "source_bonus"
            ] = source_bonus

            reranked.append(
                item
            )

        # =====================================================
        # 5. SORT
        # =====================================================

        reranked.sort(
            key=lambda x:
                x["final_score"],
            reverse=True
        )

        # =====================================================
        # DEBUG
        # =====================================================

        print(
            "\n=============================="
        )

        print(
            "FINAL RETRIEVAL RESULTS"
        )

        print(
            "=============================="
        )

        for i, result in enumerate(
            reranked[:top_k],
            start=1
        ):

            document = result[
                "document"
            ]

            text = document.get(
                "text",
                ""
            ).replace(
                "\n",
                " "
            )

            print(
                f"\n#{i}"
            )

            print(
                "Source:",
                document.get(
                    "source",
                    "Unknown"
                )
            )

            print(
                "Page:",
                document.get(
                    "page",
                    0
                )
            )

            print(
                "Chunk:",
                document.get(
                    "chunk_id",
                    0
                )
            )

            print(
                "Retrieval:",
                result.get(
                    "retrieval_type",
                    ""
                )
            )

            print(
                "Semantic:",
                round(
                    result.get(
                        "semantic_score",
                        0
                    ),
                    4
                )
            )

            print(
                "Keyword:",
                round(
                    result.get(
                        "keyword_score",
                        0
                    ),
                    4
                )
            )

            print(
                "Phrase:",
                round(
                    result.get(
                        "phrase_score",
                        0
                    ),
                    4
                )
            )

            print(
                "Exact:",
                round(
                    result.get(
                        "exact_match_score",
                        0
                    ),
                    4
                )
            )

            print(
                "Source bonus:",
                round(
                    result.get(
                        "source_bonus",
                        0
                    ),
                    4
                )
            )

            print(
                "FINAL:",
                round(
                    result.get(
                        "final_score",
                        0
                    ),
                    4
                )
            )

            print(
                "Preview:",
                text[:250]
            )

        print(
            "\n==============================\n"
        )

        return reranked[:top_k]