"""Convierte los documentos de entrega de Markdown a Word (.docx) con python-docx.

Soporta el subconjunto de Markdown que usan estos documentos: títulos (#, ##, ###),
párrafos, viñetas (-), listas numeradas (se escriben como texto), tablas, bloques de código
(``` o sangría de 4 espacios), imágenes ![pie](ruta), **negrita**, *cursiva* y `código`. No usa pandoc.

Uso:  python entrega/md_a_docx.py            # convierte los dos documentos de entrega
      python entrega/md_a_docx.py a.md b.md  # o los que se indiquen
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

AQUI = Path(__file__).resolve().parent
DOCUMENTOS = ["Informe_Primera_Entrega.md", "Manual_Tecnico.md"]
FUENTE, FUENTE_CODIGO = "Calibri", "Consolas"
TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`|\*[^*\s][^*]*?\*)")
ESCAPADO = "\u0001"  # marca temporal para \*


def _fuente(run, nombre: str | None = None, tam: float | None = None) -> None:
    if nombre:
        run.font.name = nombre
        run._element.rPr.rFonts.set(qn("w:eastAsia"), nombre)
    if tam:
        run.font.size = Pt(tam)


def agregar_inline(parrafo, texto: str, negrita: bool = False, tam: float | None = None) -> None:
    """Agrega ``texto`` al párrafo interpretando **negrita**, *cursiva* y `código`."""
    texto = texto.replace("\\*", ESCAPADO)
    for trozo in TOKEN.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**") and len(trozo) > 4:
            run = parrafo.add_run(trozo[2:-2].replace(ESCAPADO, "*"))
            run.bold = True
        elif trozo.startswith("`") and trozo.endswith("`"):
            run = parrafo.add_run(trozo[1:-1].replace(ESCAPADO, "*"))
            _fuente(run, FUENTE_CODIGO, (tam or 11) - 1)
            continue
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            run = parrafo.add_run(trozo[1:-1].replace(ESCAPADO, "*"))
            run.italic = True
        else:
            run = parrafo.add_run(trozo.replace(ESCAPADO, "*"))
        if negrita:
            run.bold = True
        if tam:
            run.font.size = Pt(tam)


def _sombrear(celda, color: str) -> None:
    pr = celda._element.get_or_add_tcPr()
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), color)
    pr.append(sombra)


def _tabla(doc: Document, filas: list[list[str]]) -> None:
    n_col = max(len(f) for f in filas)
    tabla = doc.add_table(rows=len(filas), cols=n_col)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, fila in enumerate(filas):
        for j in range(n_col):
            celda = tabla.cell(i, j)
            celda.text = ""
            p = celda.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            agregar_inline(p, fila[j] if j < len(fila) else "", negrita=(i == 0), tam=9.5)
            if i == 0:
                _sombrear(celda, "E8EEF7")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _codigo(doc: Document, lineas: list[str]) -> None:
    for linea in lineas:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run(linea if linea else " ")
        _fuente(run, FUENTE_CODIGO, 9)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def _celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def convertir(origen: Path, destino: Path) -> None:
    lineas = origen.read_text(encoding="utf-8").splitlines()
    doc = Document()
    seccion = doc.sections[0]
    seccion.left_margin = seccion.right_margin = Cm(2.4)
    seccion.top_margin = seccion.bottom_margin = Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name = FUENTE
    normal.font.size = Pt(11)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
    normal.paragraph_format.space_after = Pt(6)

    titulo_hecho = False
    i = 0
    while i < len(lineas):
        linea = lineas[i]
        if not linea.strip():
            i += 1
            continue
        if linea.strip() == "---":
            i += 1
            continue
        if linea.startswith("```"):  # bloque de código con cercas
            i += 1
            bloque = []
            while i < len(lineas) and not lineas[i].startswith("```"):
                bloque.append(lineas[i])
                i += 1
            _codigo(doc, bloque)
            i += 1
            continue
        if linea.startswith("    ") and linea.strip():  # bloque sangrado (fórmulas)
            bloque = []
            while i < len(lineas) and (lineas[i].startswith("    ") or not lineas[i].strip()):
                if not lineas[i].strip() and (i + 1 >= len(lineas) or not lineas[i + 1].startswith("    ")):
                    break
                bloque.append(lineas[i][4:])
                i += 1
            _codigo(doc, bloque)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", linea)
        if m:
            nivel = len(m.group(1))
            texto = re.sub(r"[*`]", "", m.group(2))
            if nivel == 1 and not titulo_hecho:
                doc.add_heading(texto, 0)
                titulo_hecho = True
            else:
                doc.add_heading(texto, max(1, nivel - 1))
            i += 1
            continue
        m = re.match(r"^!\[(.*)\]\((.+)\)\s*$", linea)
        if m:  # imagen: ruta relativa al .md; el texto alternativo queda como pie de figura
            ruta = (origen.parent / m.group(2)).resolve()
            if ruta.exists():
                doc.add_picture(str(ruta), width=Cm(15))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                pie = doc.add_paragraph()
                pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
                agregar_inline(pie, f"*{m.group(1)}*", tam=9.5)
            else:
                agregar_inline(doc.add_paragraph(), f"[Figura no encontrada: {m.group(2)}]")
            i += 1
            continue
        if linea.lstrip().startswith("|"):  # tabla
            filas = []
            while i < len(lineas) and lineas[i].lstrip().startswith("|"):
                celdas = _celdas(lineas[i])
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            _tabla(doc, filas)
            continue
        if re.match(r"^- ", linea):
            p = doc.add_paragraph(style="List Bullet")
            agregar_inline(p, linea[2:])
            p.paragraph_format.space_after = Pt(3)
            i += 1
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", linea)
        if m:  # lista numerada escrita como texto (evita que Word continúe la numeración)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.9)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            p.paragraph_format.space_after = Pt(3)
            agregar_inline(p, f"{m.group(1)}.  {m.group(2)}")
            i += 1
            continue
        # párrafo: se une con las líneas siguientes hasta un renglón vacío o un bloque nuevo
        partes = [linea.strip()]
        i += 1
        while (i < len(lineas) and lineas[i].strip() and not lineas[i].startswith(("#", "|", "- ", "```", "    ", "!["))
               and not re.match(r"^\d+\.\s", lineas[i]) and lineas[i].strip() != "---"):
            partes.append(lineas[i].strip())
            i += 1
        p = doc.add_paragraph()
        agregar_inline(p, " ".join(partes))
    doc.save(destino)


def main(argumentos: list[str]) -> None:
    origenes = [Path(a) for a in argumentos] or [AQUI / n for n in DOCUMENTOS]
    for origen in origenes:
        destino = origen.with_suffix(".docx")
        convertir(origen, destino)
        print(destino)


if __name__ == "__main__":
    main(sys.argv[1:])
