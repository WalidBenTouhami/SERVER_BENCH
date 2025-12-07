from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
import os

OUTPUT_DIR = "presentation"
os.makedirs(OUTPUT_DIR, exist_ok=True)

doc = SimpleDocTemplate(
    os.path.join(OUTPUT_DIR, "script_presentation.pdf"),
    pagesize=A4
)

styles = getSampleStyleSheet()
content = []

sections = [
    ("Introduction", 
     "Présentation du projet Serveur Haute Performance..."),
    ("Architecture globale", 
     "Diagramme UML, modules, files FIFO, thread pool..."),
    ("Serveur TCP Mono-thread – Yassine",
     "Fonctionnement séquentiel, limites."),
    ("Serveur HTTP Mono-thread – Islem",
     "Parsing HTTP, routes, réponses JSON."),
    ("Serveur Multi-thread – Walid",
     "Workers permanents, queue, optimisation."),
    ("Serveur HTTP Multi-thread – Ghada",
     "Thread pool + routage HTTP."),
    ("Benchmarks Python",
     "Latence, débit, CPU/RAM, dashboard."),
    ("Conclusion",
     "Synthèse + perspectives.")
]

for title, body in sections:
    content.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(body, styles["BodyText"]))
    content.append(Spacer(1, 20))

doc.build(content)
print("✔ PDF généré : presentation/script_presentation.pdf")

