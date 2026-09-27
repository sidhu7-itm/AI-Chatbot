from pathlib import Path

from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: str):
    
    pdf_path = Path(pdf_path)
    reader = PdfReader(
        str(pdf_path)
    )
    pages = []
    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            text = page.extract_text()

        except Exception as error:

            print(
                f"Error reading page "
                f"{page_number}: {error}"
            )

            text = ""


        if text and text.strip():

            pages.append({

                "page_number": page_number,

                "text": text.strip()

            })


    return pages


def load_documents(
    folder_path: str
):
    

    folder = Path(folder_path)

    if not folder.exists():

        print(
            f"Folder does not exist: {folder}"
        )

        return []


    documents = []


    for file_path in sorted(
        folder.iterdir()
    ):

        if file_path.suffix.lower() != ".pdf":

            continue


        print(
            f"\nProcessing: {file_path.name}"
        )


        pages = extract_text_from_pdf(
            str(file_path)
        )


        if not pages:

            print(
                "WARNING: No text extracted."
            )

            continue


        documents.append({

            "source": file_path.name,

            "pages": pages

        })


        print(
            f"Pages with text: {len(pages)}"
        )


    return documents