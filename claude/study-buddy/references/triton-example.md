# Worked example: where does Triton sit?

Use these two drawings together. The architecture identifies who owns the files, which process runs the model, and what the application calls. The sequence follows one image through that architecture.

## Architecture: one GPU inference service

```mermaid
flowchart TB
  subgraph build["Training environment"]
    T["Training job<br/>PyTorch"] -->|"exports a supported model file"| M["Versioned model artifact"]
  end
  subgraph store["Persistent storage"]
    R[("Model repository<br/>versioned files and configuration")]
  end
  M -->|"deployment publishes version"| R
  subgraph svc["Serving host · example GPU deployment"]
    subgraph triton["Triton Inference Server"]
      E["HTTP / gRPC endpoint<br/>and request scheduler"]
      B["Model instance<br/>matching execution backend"]
      E -->|"dispatches inference"| B
    end
    G["NVIDIA GPU"]
    B -->|"executes supported operations"| G
  end
  R -. "model files loaded at startup or by request" .-> B
  A["Client application"] -->|"sends input; receives prediction"| E
  classDef runtime fill:#d8edff,color:#112e49,stroke:#24537a
  classDef disk fill:#fff0ca,color:#412c05,stroke:#986817
  class E,B,G runtime
  class R,M disk
```

The dashed arrow is the **model load path**. The server can load a model once and serve many requests with that instance. The cylinder represents persistent storage. A TensorRT engine is one possible model artifact; the matching backend depends on the format you deploy.

## Runtime flow: one image, one prediction

```mermaid
sequenceDiagram
  participant A as Client app
  participant T as Triton endpoint / scheduler
  participant B as Loaded model backend
  participant G as GPU
  A->>T: Send image for inference
  T->>B: Dispatch input to model instance
  B->>G: Run inference operations
  G-->>B: Computed output
  B-->>T: Model output
  T-->>A: Return prediction
```

**Recall check.** You have uploaded a new model version to the repository. What still needs to happen before it can answer requests? Triton must successfully load the version under its configured model control and version policies. A file in storage and a model ready to serve are two different states. [NVIDIA Triton architecture](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/index.html) · [Model management](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_management.html)
