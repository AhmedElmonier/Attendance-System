import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VectorIndex:
    def __init__(self, embedding_dim: int = 512, space: str = "cosine"):
        self.embedding_dim = embedding_dim
        self.space = space
        self._labels: List[int] = []
        self._employee_ids: List[str] = []
        self._backend = None
        self._init_index()

    def _init_index(self):
        try:
            import hnswlib

            self._backend = "hnswlib"
            self._init_hnsw_index()
            logger.info("Initialized HNSW index")
        except ImportError:
            try:
                import faiss

                self._backend = "faiss"
                self._init_faiss_index()
                logger.info("Initialized FAISS index (fallback)")
            except ImportError:
                self._backend = "numpy"
                self._init_numpy_index()
                logger.warning("Using NumPy fallback index (slow)")

    def _init_hnsw_index(self):
        import hnswlib

        space_map = {"cosine": "cosine", "ip": "ip", "l2": "l2"}
        hnsw_space = space_map.get(self.space, "cosine")

        self._index = hnswlib.Index(space=hnsw_space, dim=self.embedding_dim)
        self._index.set_num_threads(4)
        self._index.set_ef(100)

    def _init_faiss_index(self):
        import faiss

        if self.space == "cosine":
            self._index = faiss.IndexFlatIP(self.embedding_dim)
        else:
            self._index = faiss.IndexFlatL2(self.embedding_dim)

    def _init_numpy_index(self):
        self._vectors: np.ndarray = np.zeros((0, self.embedding_dim), dtype=np.float32)

    def add(self, employee_id: str, vector: np.ndarray) -> int:
        if vector.shape != (self.embedding_dim,):
            vector = vector.reshape(-1)

        if self.space == "cosine":
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm

        label = len(self._labels)

        if self._backend == "hnswlib":
            vector_2d = vector.reshape(1, -1).astype(np.float32)
            self._index.add_items(vector_2d, label)
        elif self._backend == "faiss":
            vector_2d = vector.reshape(1, -1).astype(np.float32)
            self._index.add(vector_2d)
        else:
            self._vectors = np.vstack([self._vectors, vector.reshape(1, -1)])

        self._labels.append(label)
        self._employee_ids.append(employee_id)

        return label

    def add_batch(self, entries: List[Tuple[str, np.ndarray]]) -> List[int]:
        if not entries:
            return []

        if self._backend == "hnswlib":
            emp_ids, vectors = zip(*entries)
            vectors_array = np.array(vectors, dtype=np.float32)
            if vectors_array.ndim == 1:
                vectors_array = vectors_array.reshape(1, -1)

            if self.space == "cosine":
                norms = np.linalg.norm(vectors_array, axis=1, keepdims=True)
                norms[norms == 0] = 1
                vectors_array = vectors_array / norms

            labels = list(range(len(self._labels), len(self._labels) + len(entries)))
            self._index.add_items(vectors_array, labels)

            for emp_id, label in zip(emp_ids, labels):
                self._employee_ids.append(emp_id)
                self._labels.append(label)

            return labels
        else:
            return [self.add(emp_id, vec) for emp_id, vec in entries]

    def search(
        self, query_vector: np.ndarray, k: int = 1
    ) -> List[Tuple[str, float, int]]:
        if query_vector.shape != (self.embedding_dim,):
            query_vector = query_vector.reshape(-1)

        if self.space == "cosine":
            norm = np.linalg.norm(query_vector)
            if norm > 0:
                query_vector = query_vector / norm

        k = min(k, len(self._labels))

        if k <= 0:
            return []

        if self._backend == "hnswlib":
            query_2d = query_vector.reshape(1, -1).astype(np.float32)
            labels, distances = self._index.knn_query(query_2d, k=k)

            results = []
            for idx, dist in zip(labels[0], distances[0]):
                if idx < len(self._employee_ids):
                    similarity = (
                        1.0 / (1.0 + float(dist))
                        if self.space != "cosine"
                        else float(dist)
                    )
                    results.append((self._employee_ids[idx], similarity, int(idx)))
            return results

        elif self._backend == "faiss":
            import faiss

            query_2d = query_vector.reshape(1, -1).astype(np.float32)
            distances, indices = self._index.search(query_2d, k)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self._employee_ids):
                    similarity = (
                        float(dist)
                        if self.space == "ip"
                        else (1.0 / (1.0 + float(dist)))
                    )
                    results.append((self._employee_ids[idx], similarity, int(idx)))
            return results

        else:
            return self._search_numpy(query_vector, k)

    def _search_numpy(self, query: np.ndarray, k: int) -> List[Tuple[str, float, int]]:
        if len(self._vectors) == 0:
            return []

        similarities = np.dot(self._vectors, query)
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        return [
            (self._employee_ids[idx], float(similarities[idx]), idx)
            for idx in top_k_indices
        ]

    def remove(self, employee_id: str) -> bool:
        try:
            idx = self._employee_ids.index(employee_id)
        except ValueError:
            return False

        self._employee_ids.pop(idx)
        self._labels.pop(idx)

        if self._backend == "numpy":
            self._vectors = np.delete(self._vectors, idx, axis=0)

        return True

    def get_size(self) -> int:
        return len(self._labels)

    def clear(self) -> None:
        self._labels.clear()
        self._employee_ids.clear()

        if self._backend == "hnswlib":
            self._init_hnsw_index()
        elif self._backend == "faiss":
            self._index.reset()
        else:
            self._vectors = np.zeros((0, self.embedding_dim), dtype=np.float32)

    def save(self, path: str) -> None:
        if self._backend == "hnswlib":
            self._index.save_index(f"{path}.hnsw")
            metadata = {
                "employee_ids": self._employee_ids,
                "embedding_dim": self.embedding_dim,
                "space": self.space,
            }
            np.save(f"{path}.meta.npy", metadata, allow_pickle=True)
        elif self._backend == "faiss":
            import faiss

            faiss.write_index(self._index, f"{path}.index")
            np.save(
                f"{path}.meta.npy",
                {
                    "employee_ids": self._employee_ids,
                    "embedding_dim": self.embedding_dim,
                    "space": self.space,
                },
                allow_pickle=True,
            )
        else:
            np.save(f"{path}.vectors.npy", self._vectors)
            np.save(
                f"{path}.employee_ids.npy", np.array(self._employee_ids, dtype=object)
            )

    def load(self, path: str) -> None:
        self.clear()

        if self._backend == "hnswlib":
            try:
                self._index.load_index(f"{path}.hnsw")
                metadata = np.load(f"{path}.meta.npy", allow_pickle=True).item()
                self._employee_ids = metadata["employee_ids"]
                self._labels = list(range(len(self._employee_ids)))
            except Exception as e:
                logger.error(f"Failed to load HNSW index: {e}")
                self._init_hnsw_index()
        elif self._backend == "faiss":
            try:
                import faiss

                self._index = faiss.read_index(f"{path}.index")
                metadata = np.load(f"{path}.meta.npy", allow_pickle=True).item()
                self._employee_ids = metadata["employee_ids"]
                self._labels = list(range(len(self._employee_ids)))
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                self._init_faiss_index()
        else:
            try:
                self._vectors = np.load(f"{path}.vectors.npy")
                self._employee_ids = np.load(
                    f"{path}.employee_ids.npy", allow_pickle=True
                ).tolist()
                self._labels = list(range(len(self._employee_ids)))
            except Exception as e:
                logger.error(f"Failed to load NumPy index: {e}")
