import fitz  # PyMuPDF
import re
from collections import Counter
from src.utils import clean_text, is_bold_font, is_all_upper, is_title_case, is_binary_data

class PDFParser:
    """
    Handles the extraction of structural elements from PDFs using 
    heuristic analysis of font metadata (size, weight, casing).
    """

    def extract_candidates(self, pdf_path):
        """
        Analyzes PDF to find potential headings based on font properties.
        (Renamed from extract_heading_candidates to match main.py)
        """
        doc = fitz.open(pdf_path)
        candidates = []
        all_lines = []

        # 1. First Pass: Extract all lines with detailed metadata
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            spans = []

            for block in blocks:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        spans.append({
                            "text": span["text"],
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "x0": span["bbox"][0],
                            "x1": span["bbox"][2],
                            "y0": span["bbox"][1],
                            "y1": span["bbox"][3],
                            "origin_y": line["bbox"][1],
                            "page_width": page.rect.width,
                            "page_num": page_num
                        })

            # Sort spans by vertical position, then horizontal
            spans.sort(key=lambda s: (round(s["origin_y"], 1), s["x0"]))
            
            # Merge spans into lines
            merged_lines = self._merge_spans_to_lines(spans)
            all_lines.extend(merged_lines)

        if not all_lines:
            return []

        # 2. Analyze global document statistics
        median_font_size, threshold_width = self._calculate_doc_stats(all_lines)

        # 3. Second Pass: Filter candidates based on heuristics
        for sentence, size, span in all_lines:
            reasons = self._evaluate_heading_heuristics(
                sentence, size, span, median_font_size, threshold_width
            )

            if reasons:
                candidates.append({
                    "text": sentence,
                    "page_num": span["page_num"],
                    "y": span["y0"],
                    "reasons": reasons
                })

        return candidates

    def extract_sections(self, pdf_path, heading_matches):
        """
        Extracts content text between identified headings.
        """
        doc = fitz.open(pdf_path)
        sorted_matches = sorted(heading_matches, key=lambda x: (x["page_num"], x["y"]))
        sections = []

        for i, current in enumerate(sorted_matches):
            start_page = current["page_num"]
            start_y = current["y"]
            
            # Determine end boundary
            if i + 1 < len(sorted_matches):
                next_heading = sorted_matches[i + 1]
                end_page = next_heading["page_num"]
                end_y = next_heading["y"]
            else:
                end_page = doc.page_count - 1
                end_y = None

            section_content = self._extract_text_range(doc, start_page, start_y, end_page, end_y)
            
            sections.append({
                "heading": current["text"],
                "score": current.get("score", 0.0),
                "content": clean_text(section_content),
                "page_number": start_page + 1
            })

        return sections

    # --- Helper Methods for Internal Logic ---

    def _merge_spans_to_lines(self, spans):
        merged_lines = []
        buffer = ""
        last_y = None
        last_size = None
        last_span = None

        for span in spans:
            raw_text = span["text"]
            if is_binary_data(raw_text): continue
            
            text = clean_text(raw_text)
            if not text: continue

            current_y = round(span["origin_y"], 1)
            size = span["size"]
            
            is_new_para = (last_y is not None and abs(current_y - last_y) > size * 1.2)

            if buffer and (re.search(r"[.?!]$", buffer) or is_new_para):
                merged_lines.append((buffer.strip(), last_size, last_span))
                buffer = text
            else:
                buffer = buffer + " " + text if buffer else text

            last_y = current_y
            last_size = size
            last_span = span

        if buffer:
            merged_lines.append((buffer.strip(), last_size, last_span))
        return merged_lines

    def _calculate_doc_stats(self, all_lines):
        line_widths = [span["x1"] - span["x0"] for _, _, span in all_lines]
        rounded_widths = [round(w, -1) for w in line_widths]
        
        if rounded_widths:
            most_common_width = Counter(rounded_widths).most_common(1)[0][0]
            threshold_width = 0.75 * most_common_width
        else:
            threshold_width = 0

        font_sizes = [line[1] for line in all_lines]
        median_font_size = sorted(font_sizes)[len(font_sizes) // 2] if font_sizes else 12
        
        return median_font_size, threshold_width

    def _evaluate_heading_heuristics(self, sentence, size, span, median_size, threshold_width):
        page_width = span["page_width"]
        text_width = span["x1"] - span["x0"]
        is_bold = is_bold_font(span)
        is_centered = abs(span["x0"] - (page_width - span["x1"])) < 20
        word_count = len(sentence.split())
        
        reasons = []
        if size > median_size * 1.15: reasons.append("Larger font")
        if is_bold: reasons.append("Bold")
        if is_centered and (text_width < threshold_width or word_count < 10): reasons.append("Centered")
        if is_all_upper(sentence): reasons.append("Uppercase")
        if is_title_case(sentence): reasons.append("Title Case")
        if word_count < 10 and size > median_size: reasons.append("Short & Prominent")
        
        return reasons

    def _extract_text_range(self, doc, start_page, start_y, end_page, end_y):
        text = ""
        for p in range(start_page, end_page + 1):
            page = doc[p]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    line_y = line["bbox"][1]
                    # Skip text before start_y on first page
                    if p == start_page and line_y < start_y: continue
                    # Skip text after end_y on last page
                    if p == end_page and end_y is not None and line_y >= end_y: continue
                    
                    for span in line["spans"]:
                        text += span["text"] + " "
            text += "\n"
        return text