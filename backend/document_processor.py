import os
import fitz


def process_pdf(pdf_path, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    document = fitz.open(pdf_path)

    all_pages = []

    for page_number, page in enumerate(document):

        page_data = {
            "page": page_number + 1,
            "text_blocks": [],
            "images": []
        }

        # -----------------------------
        # Extract text blocks
        # -----------------------------

        blocks = page.get_text("blocks")

        for block in blocks:

            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if text:

                page_data["text_blocks"].append({
                    "text": text,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1
                })

        # -----------------------------
        # Extract images
        # -----------------------------

        image_list = page.get_images(full=True)

        for image_index, image in enumerate(image_list):

            xref = image[0]

            image_data = document.extract_image(xref)

            image_bytes = image_data["image"]
            image_extension = image_data["ext"]

            image_filename = (
                f"page_{page_number + 1}_"
                f"image_{image_index + 1}.{image_extension}"
            )

            image_path = os.path.join(
                output_folder,
                image_filename
            )

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Find image position on page
            image_rects = page.get_image_rects(xref)

            for rect in image_rects:

                page_data["images"].append({
                    "filename": image_filename,
                    "x0": rect.x0,
                    "y0": rect.y0,
                    "x1": rect.x1,
                    "y1": rect.y1
                })

        all_pages.append(page_data)

    document.close()

    return all_pages