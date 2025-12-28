# Standard library imports (no extra install needed)
import argparse          # For parsing command-line arguments like: app.exe image.jpg --json-out out.json
import json              # For writing docTR results as JSON
import sys               # For printing errors to stderr and returning proper exit codes
from pathlib import Path # For clean cross-platform path handling (Windows/macOS/Linux)

# docTR imports (from python-doctr package)
from doctr.io import DocumentFile          # Loads images/PDFs into docTR's expected format
from doctr.models import ocr_predictor     # Creates an OCR model (detector + recognizer)

# import from own module file
from path_resolver import resolve_input_path

def extract_text_from_doctr_export(exported: dict) -> str:
    """
    docTR gives a structured output in dictionary form via result.export().

    The rough structure is:
    export["pages"] -> page["blocks"] -> block["lines"] -> line["words"]

    Each "word" item usually contains:
    - "value": the recognized text
    - "confidence": score
    - geometry / box coordinates etc.

    This function walks through that structure and produces readable text:
    - words joined into lines
    - lines separated by newline
    - pages separated by an extra blank line
    """

    # Get the list of pages; if missing, default to empty list
    pages = exported.get("pages", [])

    # We'll accumulate final output line-by-line here
    output_lines = []

    # Loop through each page (page_index is optional, but sometimes useful for debugging)
    for page_index, page in enumerate(pages):

        # Each page has blocks (like paragraphs/regions)
        for block in page.get("blocks", []):

            # Each block has lines
            for line in block.get("lines", []):

                # Each line has words; we extract the "value" of each word
                words = []
                for w in line.get("words", []):
                    # Only add non-empty word values
                    value = w.get("value", "")
                    if value:
                        words.append(value)

                # Join words into a single line of text
                if words:
                    output_lines.append(" ".join(words))

        # Add a blank line between pages (but not after the last page)
        if page_index != len(pages) - 1:
            output_lines.append("")

    # Join everything with newline and strip trailing whitespace
    return "\n".join(output_lines).strip()


def main() -> int:
    """
    Main entry point for the CLI app.

    Returns an integer exit code:
    - 0 means success
    - 1 means OCR failed due to runtime exception
    - 2 means invalid input path (not found / not a file)
    """

    # Create an argument parser (defines how user calls this program)
    parser = argparse.ArgumentParser(
        prog="doctr_ocr",  # program name shown in help
        description="Run docTR OCR on an image path (relative/absolute). Prints text, optional JSON export."
    )

    # REQUIRED positional argument: the image path
    parser.add_argument(
        "image_path",
        help="Path to an image file (relative or absolute)."
    )

    # OPTIONAL argument: where to save JSON output
    parser.add_argument(
        "--json-out",
        default="",  # empty string means "no JSON output file"
        help="Optional output path to write docTR export JSON (e.g. out.json)."
    )

    # OPTIONAL argument: choose detection architecture (docTR supports multiple)
    parser.add_argument(
        "--det-arch",
        default="db_resnet50",
        help="Detection architecture (default: db_resnet50)."
    )

    # OPTIONAL argument: choose recognition architecture (docTR supports multiple)
    parser.add_argument(
        "--reco-arch",
        default="crnn_vgg16_bn",
        help="Recognition architecture (default: crnn_vgg16_bn)."
    )

    # OPTIONAL flag: if set, do NOT print text (useful if only JSON is needed)
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Do not print extracted text; useful if you only want JSON."
    )

    # Parse arguments from command line
    args = parser.parse_args()

    # Resolve the image path into an absolute path (handles relative paths nicely)
    img_path = resolve_input_path(args.image_path)

    # Validate the path exists
    if not img_path.exists():
        print(f"ERROR: File not found: {img_path}", file=sys.stderr)
        return 2

    # Validate that it's actually a file (not a folder)
    if not img_path.is_file():
        print(f"ERROR: Not a file: {img_path}", file=sys.stderr)
        return 2

    # Try to run OCR; if anything goes wrong, we catch it and return exit code 1
    try:
        # Load the image into docTR format.
        # DocumentFile.from_images expects one or more image paths.
        # Passing a single path still works; it creates a "document" with one page.
        doc = DocumentFile.from_images(str(img_path))

        # Create the OCR model.
        # docTR OCR uses TWO parts:
        # - det_arch: text detection model (finds where text is)
        # - reco_arch: recognition model (reads characters/words)
        # pretrained=True means use docTR pre-trained weights.
        model = ocr_predictor(
            det_arch=args.det_arch,
            reco_arch=args.reco_arch,
            pretrained=True
        )

        # Run OCR on the loaded document.
        # result contains structured predictions (pages/blocks/lines/words).
        result = model(doc)

        # Convert result into a serializable dictionary format.
        exported = result.export()

        # If user requested JSON output, write it to disk.
        if args.json_out:
            # Resolve output path (relative -> absolute based on current working directory)
            out_path = resolve_input_path(args.json_out)

            # Ensure the parent folder exists (mkdir -p behavior)
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON in UTF-8, keep unicode characters, indent for readability
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(exported, f, ensure_ascii=False, indent=2)

        # If user did NOT disable text output, print extracted text.
        if not args.no_text:
            text = extract_text_from_doctr_export(exported)
            print(text)

        # Success exit code
        return 0

    except Exception as e:
        # Any runtime errors end here
        print(f"ERROR: OCR failed: {e}", file=sys.stderr)
        return 1


# Standard Python pattern:
# - When run directly: execute main()
# - When imported as a module: do nothing automatically
if __name__ == "__main__":
    # Raise SystemExit so the process exits with the integer returned by main()
    raise SystemExit(main())
