from docx import Document
from pathlib import Path

file = Path("c:/Antigravity/ovpfh-v2/md/news/Artigo para o jogo do Mirassol e Vasco da Gama.docx")
doc = Document(file)

print(f"File: {file.name}")
print(f"Paragraphs: {len(doc.paragraphs)}")
print(f"Rels: {len(doc.part.rels)}")

for i, rel in enumerate(doc.part.rels.values()):
    print(f"Rel {i}: {rel.target_ref} | Type: {rel.reltype}")
    if "image" in rel.target_ref.lower():
        print(f" Found image in target_ref")
    if "image" in rel.reltype.lower():
        print(f" Found image in reltype")
