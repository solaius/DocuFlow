# DocuFlow

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

DocuFlow is a document processing pipeline that extracts structured data from various document formats. Built with IBM Docling, it currently supports:

## ✅ Current Features

- Document parsing with IBM Docling integration
- Table structure detection and extraction
- Code block and formula detection
- Image detection and analysis
- Comprehensive error handling
- Support for PDF and image formats
- GPU acceleration (with CUDA)

## 📋 Prerequisites

- Python 3.10 or higher
- CUDA-capable GPU (optional, for GPU acceleration)
- Git

## 🚀 Installation

### Windows (WSL2)

1. Install WSL2 and Ubuntu:
```powershell
# Open PowerShell as Administrator
wsl --install
wsl --set-default-version 2
```

2. Install Python and development tools:
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3.10 python3.10-venv python3-pip git build-essential python3-dev
```

3. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

4. Clone and setup DocuFlow:
```bash
git clone https://github.com/yourusername/DocuFlow.git
cd DocuFlow
poetry install
```

### macOS

1. Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install dependencies:
```bash
brew install python@3.10 git
```

3. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

4. Clone and setup DocuFlow:
```bash
git clone https://github.com/yourusername/DocuFlow.git
cd DocuFlow
poetry install
```

### Linux (Ubuntu/Debian)

1. Install system dependencies:
```bash
sudo apt update && sudo apt upgrade
sudo apt install python3.10 python3.10-venv python3-pip git build-essential python3-dev
```

2. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Clone and setup DocuFlow:
```bash
git clone https://github.com/yourusername/DocuFlow.git
cd DocuFlow
poetry install
```

## 🖥️ GPU Support (Optional)

To enable GPU acceleration:

1. Install NVIDIA CUDA Toolkit:

   **Ubuntu/Debian:**
   ```bash
   # Add NVIDIA package repositories
   wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
   sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
   wget https://developer.download.nvidia.com/compute/cuda/12.1.0/local_installers/cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
   sudo dpkg -i cuda-repo-ubuntu2204-12-1-local_12.1.0-530.30.02-1_amd64.deb
   sudo cp /var/cuda-repo-ubuntu2204-12-1-local/cuda-*-keyring.gpg /usr/share/keyrings/
   sudo apt-get update
   sudo apt-get -y install cuda
   ```

   **Windows/WSL2:**
   1. Install CUDA Toolkit from [NVIDIA website](https://developer.nvidia.com/cuda-downloads)
   2. Install NVIDIA drivers in Windows
   3. Enable CUDA in WSL2 following [NVIDIA's WSL2 guide](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

   **macOS:**
   - CUDA is not supported on macOS. The application will run in CPU-only mode.

2. Set CUDA environment variables:
   ```bash
   # Add to your ~/.bashrc or ~/.zshrc
   export CUDA_HOME=/usr/local/cuda
   export PATH=$CUDA_HOME/bin:$PATH
   export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
   export TORCH_CUDA_ARCH_LIST="8.9+PTX"  # Adjust based on your GPU architecture
   ```

3. Install PyTorch with CUDA support:
   ```bash
   poetry install
   ```

4. Verify CUDA installation:
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   print(f"CUDA device: {torch.cuda.get_device_name(0)}")
   ```

Note: The default CUDA architecture is set to '8.9+PTX'. You may need to adjust `TORCH_CUDA_ARCH_LIST` based on your GPU:
- RTX 40 Series: 8.9
- RTX 30 Series: 8.6
- RTX 20 Series & GTX 16 Series: 7.5
- GTX 10 Series: 6.1
- Older GPUs: Check NVIDIA's [CUDA GPUs list](https://developer.nvidia.com/cuda-gpus)

## 📝 Usage

Currently, DocuFlow can be used through its Python API:

```python
from docuflow.models.document import Document, DocumentType
from docuflow.parsing.service import DocumentParsingService
import asyncio

# Create parsing service (with optional GPU support)
service = DocumentParsingService(use_gpu=True)  # Set to False for CPU only

# Create document object
doc = Document(
    filename="example.pdf",
    file_type=DocumentType.PDF,
    file_path="path/to/example.pdf"
)

# Parse document
async def parse():
    result = await service.parse_document(doc, "path/to/example.pdf")
    print(f"Status: {result.status}")
    print(f"Content: {result.content}")
    print(f"Metadata: {result.metadata}")

# Run parsing
asyncio.run(parse())
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_parsing.py
```

## 🗺️ Development Roadmap

### Phase 1: Core Infrastructure (Current)
- ✅ Project setup and configuration
- ✅ Document models and status tracking
- ✅ Basic file handling and type detection
- ✅ IBM Docling integration
- ✅ Table and image extraction
- ✅ GPU acceleration support
- ✅ Testing infrastructure

### Phase 2: Storage & API (Next)
- [ ] Elasticsearch integration
- [ ] Neo4j integration
- [ ] FastAPI endpoints
- [ ] Document search capabilities
- [ ] Relationship mapping
- [ ] API documentation

### Phase 3: Advanced Features
- [ ] Background processing queue
- [ ] Batch processing support
- [ ] Advanced AI features with IBM Granite Models
- [ ] Multilingual support
- [ ] Enhanced error recovery

### Phase 4: Production Ready
- [ ] Authentication and authorization
- [ ] Rate limiting
- [ ] Monitoring and logging
- [ ] Docker containerization
- [ ] Production deployment guides

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and development process.