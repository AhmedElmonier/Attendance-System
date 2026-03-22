# Research: Biometric Model & HNSW Performance (Phase 1)

## Decision: Biometric Model
- **Choice**: **MobileFaceNet** (PyTorch/ONNX).
- **Rationale**: 
  - Lightweight ($<5.0\text{MB}$ weight size).
  - High accuracy on LFW/MegaFace benchmarks.
  - Sub-50ms inference on standard Laptop/WSL2 CPU (i5/i7) and $<150ms$ on Raspberry Pi 4.
- **Alternatives Considered**: 
  - *ResNet50*: Too heavy for edge CPU (approx. 500ms+ inference).
  - *MediaPipe Face Detection*: Used only for landmarks/Euler angles, not for 512-d embeddings.

## Decision: Local Indexing
- **Choice**: **hnswlib** (Hierarchical Navigable Small World).
- **Rationale**: 
  - Extremely fast similarity search ($O(\log N)$).
  - Low memory footprint for 1,000-10,000 vectors.
  - Native Python bindings available.
- **Alternatives Considered**: 
  - *FAISS*: Powerful but has heavier dependencies and overhead for small local indices.

## Decision: Edge Persistence
- **Choice**: **SQLite with SQLCipher**.
- **Rationale**: 
  - Zero-config, single-file database.
  - SQLCipher provides transparent AES-256 encryption at rest, fulfilling Constitution Principle I.
- **Alternatives Considered**: 
  - *Plain SQLite*: Rejected due to lack of native encryption-at-rest.
