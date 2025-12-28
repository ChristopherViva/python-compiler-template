# Python docTR OCR CLI

A simple command-line tool to run Optical Character Recognition (OCR) on images using [docTR](https://mindee.github.io/doctr/) (Document Text Recognition). This tool loads an image, runs OCR, prints the extracted text, and can optionally export the full docTR result as JSON.

> **Note:**  

> Installations
**pip install PyInstaller**
**pip install python-doctr**
> This project uses a **downgraded version of torch (2.0.0)** to fix PyTorch DLL loading issues.  
> Make sure to install the correct torch version as shown below.
**pip install torch==2.8.0 torchvision==0.23.0 torchaudio==2.8.0**


---

## Features

- Run OCR on images (JPG, PNG, etc.) using docTR.
- Print extracted text to the console.
- Optionally export full docTR results as JSON.
- Choose detection and recognition architectures.
- Clean path handling for both relative and absolute paths.

---

## Installation

1. **Clone this repository:**
    ```sh
    git clone <your-repo-url>
    cd python-compile-template
    ```

2. **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```sh
    pip install doctr[torch]
    pip install torch==2.0.0  # Downgrade torch to 2.0.0 to fix DLL issues
    ```

---

## Usage

```sh
python [main.py](http://_vscodecontentref_/0) <image_path> [--json-out <output.json>] [--det-arch <detector>] [--reco-arch <recognizer>] [--no-text]