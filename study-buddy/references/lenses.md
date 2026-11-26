# Lenses: examples from the learner's world

A lens turns an unfamiliar exam concept into something the learner already runs every day. Pick it from `profile.json` (`"lens": "devops"`), the request ("my background is networking"), or what the learner has said; otherwise use **general IT**. Ask once if the learner's field is unknown and the pack is long; remember the answer.

## Rules for any lens

1. The analogy must keep the direction of the request and the role of each component (who calls whom, who stores, who runs).
2. Say where it breaks in one clause ("Where it breaks: a build finishes; a model is retrained as data drifts").
3. Use the learner's actual tools by name when known (from profile or conversation); otherwise the common ones below.
4. One lens callout per objective at most. The exam answer always uses the vendor's term, never the analogy.
5. Build a Rosetta-stone table (exam term ↔ learner's world) near the start of the core guide and reuse its pairs consistently.

## DevOps lens (built in)

Tools to draw on: Jenkins (controller, labelled agents, pipelines, shared libraries), GitLab CI, Ansible (inventory, playbooks, roles, idempotency), Terraform, Nexus / Artifactory, SonarQube quality gates, WebSphere / Tomcat / app servers, Kubernetes, Docker, Prometheus / Grafana / node exporter, ELK / Splunk, HashiCorp Vault, load balancers, blue-green and canary releases, change and release management, on-call and incident runbooks.

| Exam concept (examples) | DevOps analogy | Where it breaks |
|---|---|---|
| Model training | Nightly full build on the whole agent farm | A model is retrained repeatedly as data changes |
| Inference / model serving | Production traffic on app servers (WebSphere cluster behind a load balancer) | Latency budget is per request and GPU memory bound |
| Model registry, container catalog | Nexus / Artifactory with versioned artifacts | Models carry metrics and lineage, not just binaries |
| Optimising a model for inference | Build optimisation and packaging step | Changes numeric precision, can change accuracy |
| Data pipeline / ETL | Pipeline stages with quality gates | Data quality is statistical, not pass/fail |
| Experiment tracking | Build history with parameters and test reports | Many runs are expected to "fail" |
| Model drift monitoring | Config drift detection and SLO alerts | Drift comes from the world changing, not from code |
| GPU / job scheduler (Slurm, K8s device plugin) | Jenkins controller assigning jobs to labelled agents | Gang scheduling: all GPUs or none |
| Cluster provisioning | Ansible playbooks + PXE boot | Firmware and driver versions must match across nodes |
| GPU telemetry (DCGM) | Node exporter → Prometheus → Grafana | Thermal and memory errors matter more |
| Partitioning one GPU (MIG) | Splitting a server into VMs / containers with quotas | Hardware-enforced slices with fixed sizes |
| High-speed interconnect inside a server | Backplane between blades | Synchronises gradients every step |
| Cluster network between servers | Dedicated back-end network for cluster traffic | Needs RDMA-class latency |
| Quality gate before release | SonarQube gate | Model evaluation thresholds, bias and safety checks |
| Canary / shadow deployment of a model | Canary release of an app | Compare prediction quality, not just errors |
| Secrets and access control | Vault + RBAC | Same, plus data access governance |
| Infrastructure as code for ML | Terraform / Ansible | Same |

Extend the table for the exam at hand; keep the "where it breaks" column.

## Other lenses

| Lens | Anchor vocabulary |
|---|---|
| Developer | Functions, APIs, unit tests, CI, code review, dependency versions |
| Network engineer | Switches, VLANs, routing, bandwidth vs latency, QoS, fabrics |
| Data / analytics | SQL, ETL, data warehouse, dashboards, batch vs streaming |
| Sysadmin / Windows admin | Services, Group Policy, AD, patching, backups, event logs |
| Project / business | Budgets, SLAs, vendors, risk registers, change boards |
| Student / no tech background | Everyday analogies (kitchen, post office, library), always with the limit stated |
| General IT (default) | Servers, storage, networks, apps, monitoring, tickets |

## Mnemonics that work

- **Chains** for order or layers: KNOW → BUILD → RUN.
- **Contrast pairs** for look-alikes: "inside the server = NVLink, between servers = InfiniBand".
- **Acronyms** that spell a real word, only if each letter maps to a real term.
- **Number hooks**: "PUE 1.5 means half again on top".
- Every mnemonic must unpack into a correct explanation, is labelled MEMORY HOOK, and appears again on the mnemonics card.
