# DocuFlow
Document Pre-Processing 

# 1. Application Overview

### a. Objective
- **Purpose:**  
  Build a scalable document ingestion pipeline that extracts, transforms, and structures data from diverse document types (PDFs, DOCX, HTML, images) with an emphasis on accurate table parsing and traceability.
- **Problem Solved:**  
  Automate the processing of unstructured and structured document data (especially complex tables), maintain links between raw and parsed content, and support advanced AI/ML analysis (using IBM Granite Models, OCR, etc.) for regulated industries (healthcare, finance, law enforcement).
- **Intended Users:**  
  AI/ML engineers, data engineers, software architects, DevOps teams, and compliance officers in enterprise environments (e.g., hospitals, financial institutions, government agencies).

### b. Features & Functional Requirements
- **Core Features:**  
  - Document ingestion from various sources (file system/Kafka events).
  - Parsing of documents using IBM Docling for layout and table extraction.
  - Modular table extraction using both AI-driven (OCR, deep learning) and rule-based methods.
  - Structured storage of extracted data (JSON, CSV) along with traceability metadata.
  - Integration with Elasticsearch (for text search and vector retrieval) and Neo4j (for relationship mapping).
  - API endpoints for document retrieval and query processing.
- **Optional/Nice-to-Have Features:**  
  - Advanced AI validation using IBM Granite Models.
  - Multilingual processing and locale-specific normalization.
  - UI dashboards for monitoring ingestion, performance, and error logs.
- **User Interactions:**  
  - CRUD operations on document metadata and parsed outputs.
  - Automated ingestion and periodic batch processing.
  - AI processing tasks (model inference, error correction) running in the background.
  - Real-time API queries and analytics.

### c. Expected Input & Output
- **Input Data:**  
  - Diverse document formats: scanned/digital PDFs, DOCX, HTML, and image files.
- **Output Formats:**  
  - JSON documents capturing structured data, including parsed tables with metadata.
  - CSV or DataFrame representations of extracted tables.
  - API responses (REST/GraphQL) delivering searchable document data and relationships.
  - Log files and metrics for monitoring pipeline performance.

---

# 2. Technology Stack & Development Environment

### a. Core Technologies
- **Programming Languages:**  
  - Python (for backend processing, AI/ML modules, scripting)
  - JavaScript/TypeScript (for potential UI or API development)
- **Frontend Framework (if applicable):**  
  - React, Angular, or Vue (for building dashboards or monitoring UI)
- **Backend Framework:**  
  - FastAPI or Flask (for REST API development)
- **Databases:**  
  - Elasticsearch (for full-text and vector search)
  - Neo4j (for graph-based relationship storage)
  - PostgreSQL or MongoDB (for additional structured storage if needed)
- **AI/ML Components:**  
  - IBM Docling for document parsing
  - IBM Granite Models for advanced AI processing
  - OCR libraries: Tesseract, Camelot, PDFMiner, OpenCV (for image and PDF processing)
- **Containerization:**  
  - Docker (for local development and container images)
  - Podman (if integrating into an OpenShift environment)

### b. Development Environment
- **Local Setup:**  
  - Python virtual environments (using pip or poetry)
  - Node.js and npm/yarn for any JavaScript-based frontends
  - Configuration files (using a `.env` file) to manage environment variables for database endpoints, API keys, etc.
- **Dependencies & Package Managers:**  
  - Use `pip`/`poetry` for Python dependencies.
  - Use `npm` or `yarn` for frontend dependencies.
- **Version Control & CI/CD:**  
  - Git repositories (e.g., GitHub, GitLab)
  - OpenShift Pipelines/Tekton for CI/CD automation

---

# 3. Application Architecture

### a. High-Level Architecture Diagram
*(A textual description of the architecture diagram follows; a visual diagram should be created separately.)*

- **Frontend ↔ Backend:**  
  - The frontend (if developed) interacts via REST/GraphQL APIs.
- **Backend Services:**  
  - **Ingestion Service:** Monitors input sources (file system, Kafka) and triggers processing.
  - **Document Parsing Service:** Wraps IBM Docling to convert files into structured JSON.
  - **Table Extraction Module:** Processes JSON to extract table data (using AI and rules-based methods).
  - **Storage Services:**  
    - Elasticsearch for indexing and searching document text and embeddings.
    - Neo4j for storing document relationships and traceability metadata.
- **Third-Party Integrations:**  
  - External OCR libraries, IBM Granite Models for AI inference.
  - Integration with Kafka (or Red Hat AMQ Streams) for event-driven processing.

### b. Key Components & Services
- **Authentication & Authorization:**  
  - JWT or OAuth2 for securing API endpoints.
  - Optionally, Keycloak for centralized authentication.
- **APIs & Endpoints:**  
  - REST APIs (via FastAPI/Flask) for document ingestion, query processing, and status monitoring.
- **Data Flow & Processing:**  
  - Ingestion → Document Parsing (Docling) → Table Extraction → Metadata Enrichment → Storage (Elasticsearch/Neo4j).
- **Background Jobs & Automation:**  
  - Use Kafka and OpenShift Pipelines/Tekton to schedule background tasks.
  - Consider Celery for asynchronous tasks if needed.

---

# 4. Local Deployment & Testing

### a. Running the Application Locally
- **Step-by-Step Setup:**
  1. Clone the repository and set up the Python virtual environment.
  2. Install required packages (using `pip install -r requirements.txt` or via Poetry).
  3. Create and configure a `.env` file for environment variables (database endpoints, API keys, etc.).
  4. Run local instances of dependent services (using Docker Compose for Elasticsearch, Neo4j, Kafka).
  5. Start the backend application (e.g., `uvicorn main:app --reload` for FastAPI).
  6. For containerized runs, build Docker images and run with Docker or Podman.
- **Dev Mode vs. Production Mode:**  
  - Dev mode: Enable hot-reloading, verbose logging, and debugging.
  - Production mode: Use production-grade configurations (Gunicorn/Uvicorn with workers, secure connections, etc.).

### b. Testing Strategy
- **Unit Tests & Integration Tests:**  
  - Use `pytest` for unit testing individual modules (parsing, extraction, API endpoints).
  - Write integration tests to simulate end-to-end pipeline processing.
- **Mocking External Dependencies:**  
  - Use libraries like `pytest-mock` or `unittest.mock` to simulate API calls and database queries.
- **Test Coverage:**  
  - Ensure tests cover ingestion, parsing, table extraction, and data storage workflows.

---

# 5. Deployment Strategy

### a. Deployment Options
- **Local Packaging & Deployment:**  
  - Dockerize each module and use Docker Compose for local multi-container orchestration.
- **Containerized Deployment on OpenShift/Kubernetes:**  
  - Create Kubernetes/Openshift YAML manifests or Tekton Pipeline definitions for each service.
  - Use Helm charts for templated deployments if needed.

### b. Environment Configurations
- **Dev vs. Prod Environment Variables:**  
  - Use separate `.env` files or Kubernetes Secrets/ConfigMaps for environment-specific settings.
- **Secrets Management:**  
  - Implement Kubernetes Secrets or use HashiCorp Vault for sensitive configuration data.

---

# 6. Security & Performance Considerations

### a. Security Best Practices
- **Secure API Endpoints:**  
  - Use JWT/OAuth2 for authentication and authorization.
  - Enforce HTTPS for all API traffic.
- **Input Validation & Sanitization:**  
  - Validate incoming documents and API parameters to prevent injection attacks.
- **Rate Limiting:**  
  - Implement rate limiting on API endpoints to mitigate abuse.
- **Audit Logging:**  
  - Log all access and modifications for compliance and troubleshooting.

### b. Performance Optimization
- **Caching Strategies:**  
  - Cache intermediate processing results (e.g., model inference outputs) where possible.
- **Query Optimization:**  
  - Optimize Elasticsearch queries and Neo4j graph traversals.
- **Load Balancing & Scalability:**  
  - Use Kubernetes Horizontal Pod Autoscalers and KEDA for dynamic scaling.
  - Employ parallel processing in ingestion and document parsing (document-level and task-level parallelism).

---

# 7. Future Enhancements & Scalability

- **Scalability:**  
  - Design the system to scale horizontally—each service runs as independent microservices.
  - Leverage cloud-based scaling tools (e.g., auto-scaling groups, managed Kubernetes).
- **Potential Integrations:**  
  - Integrate with cloud storage, analytics platforms, or advanced monitoring tools (e.g., Prometheus, Grafana).
  - Expand AI capabilities (e.g., additional NLP modules, improved OCR via IBM Granite Models).
- **Feature Roadmap:**  
  - Enhanced UI dashboards for real-time monitoring.
  - Multilingual document processing improvements.
  - Additional connectors to third-party systems (e.g., ERP, CRM).

---

# Detailed Task List for Modular Implementation

### **Phase 1: Architecture & Environment Setup**
1. **Define Architecture & Create Diagrams:**
   - Draw high-level diagrams showing Ingestion, Parsing, Extraction, and Storage components.
2. **Setup Development Environment:**
   - Provision an OpenShift development cluster.
   - Install and configure Apache Kafka/Red Hat AMQ Streams.
   - Setup persistent storage via OpenShift Data Foundation.
3. **Build Base Container Images:**
   - Create Dockerfiles for Python (Docling, OCR libraries) and Node.js (if UI is needed).
4. **Configure CI/CD:**
   - Create pipelines using Tekton/OpenShift Pipelines.
   - Integrate Git repository with CI/CD for automatic builds and tests.

### **Phase 2: Ingestion & Pre-Processing Module**
1. **Develop Ingestion Service:**
   - Create a Python service that monitors a folder or listens to Kafka events.
   - Implement a file watcher that triggers processing with a unique document ID.
2. **Build Document Parsing Module:**
   - Develop a wrapper around IBM Docling to process various document formats.
   - Write tests to verify JSON output from Docling.
3. **Implement Table Extraction:**
   - Develop code to extract tables from the JSON using AI methods and rule-based fallbacks (Camelot, PDFMiner).
   - Ensure extraction generates CSVs/pandas DataFrames and includes metadata.
4. **Define Pipeline Workflow:**
   - Write a Tekton/Kubeflow pipeline definition that sequences ingestion, parsing, extraction, and storage.
   - Test end-to-end on sample documents.

### **Phase 3: Structured Storage & Traceability**
1. **Elasticsearch Integration:**
   - Write a module to index full-text and JSON data.
   - Develop a script to generate vector embeddings (optional) and store them.
2. **Neo4j Integration:**
   - Write a module to create document and table nodes with relationships.
   - Ensure metadata (document ID, page, caption) is attached to each node.
3. **Data Linking & Metadata Enrichment:**
   - Modify the parsing output to include traceability information.
   - Test data consistency between stored JSON and graph relationships.

### **Phase 4: AI Model Training & Optimization**
1. **Prepare Datasets & Fine-Tune Models:**
   - Collect representative documents and create a training set.
   - Fine-tune IBM Granite Models or alternative OCR/NLP models.
2. **Deploy an Inference Service:**
   - Build a REST API to run inference on ambiguous or low-confidence documents.
   - Integrate this service as an optional step in the pipeline.
3. **Benchmark & Optimize:**
   - Write benchmarking scripts to measure throughput, latency, and accuracy.
   - Adjust resource allocation (e.g., GPU vs. CPU) based on test results.

### **Phase 5: Downstream Integration**
1. **Develop REST APIs:**
   - Build API endpoints using FastAPI (or Flask) for querying Elasticsearch and Neo4j.
   - Document API endpoints with OpenAPI/Swagger.
2. **Connect to ETL/Data Lakes:**
   - Develop connectors using Camel/Kamelets or custom scripts.
   - Validate data schema compatibility and successful data transfers.
3. **End-to-End Testing:**
   - Perform integration testing on the complete pipeline.
   - Write automated tests for all API endpoints and workflows.

### **Phase 6: Production Deployment & Scaling**
1. **Deploy to Production OpenShift Cluster:**
   - Use the CI/CD pipelines to deploy container images.
   - Configure environment variables via ConfigMaps and Secrets.
2. **Implement Load Testing & Auto-scaling:**
   - Run load tests to simulate high document volumes.
   - Set up Kubernetes Horizontal Pod Autoscalers and KEDA for dynamic scaling.
3. **Security & Compliance:**
   - Enforce RBAC, TLS, and audit logging.
   - Run security scans and compliance checks.

### **Phase 7: Monitoring & Continuous Improvement**
1. **Set Up Observability:**
   - Integrate Prometheus and Grafana for monitoring performance metrics.
   - Configure alerts for errors and performance degradation.
2. **Maintenance & Future Enhancements:**
   - Schedule regular maintenance (model re-training, dependency updates).
   - Collect feedback and plan additional features (e.g., enhanced UI, multilingual support).

