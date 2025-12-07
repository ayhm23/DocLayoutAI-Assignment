import json
import os
from datetime import datetime

class OutputGenerator:
    def __init__(self, input_docs, persona, job, top_k=20):
        self.metadata = {
            "input_documents": input_docs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        }
        self.all_sections = []
        self.top_k = top_k

    def add_result(self, pdf_name, section):
        self.all_sections.append({
            'document': pdf_name,
            'heading': section['heading'],
            'score': section['score'],
            'content': section['content'],
            'page_number': section['page_number']
        })

    def save_json(self, output_path):
        # Sort all findings by Score
        sorted_sections = sorted(self.all_sections, key=lambda x: x['score'], reverse=True)
        top_sections = sorted_sections[:self.top_k]

        output = {
            "metadata": {
                **self.metadata,
                "total_sections_found": len(sorted_sections),
                "top_k_selected": len(top_sections)
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }

        for idx, section in enumerate(top_sections, 1):
            output["extracted_sections"].append({
                "document": section["document"],
                "section_title": section["heading"],
                "importance_rank": idx,
                "page_number": section["page_number"]
            })

            output["subsection_analysis"].append({
                "document": section["document"],
                "refined_text": section["content"],
                "page_number": section["page_number"]
            })

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {output_path}")
        except IOError as e:
            print(f"Error saving file: {e}")