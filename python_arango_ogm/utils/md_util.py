import base64
from enum import Enum
import json
import textwrap

from IPython.display import display, display_svg, HTML, Markdown, Latex, SVG
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers import get_lexer_by_name
from pygments.lexers.data import JsonLexer
from pygments.formatters import HtmlFormatter
from jupyterlab_pygments import JupyterStyle
import qgrid

from .str_util import squish_text

PrettyFormats = Enum('PrettyFormats', 'json python')

COL_SEP = ' | '
NEWLINE = "\r\n"
CR = "\n"
INDENT = '  '

PAD = "style='margin: 4em; padding 1em; vertical-align:top;'"
CELL_HTML = f"<td {PAD}>%s</td>"
ROW_HTML = f"<tr {PAD}>%s</tr>"
TABLE_HTML = f"<table {PAD}>%s</table>"
MIN_VISIBLE_ROWS = 8

BG_HEADER = '#202B30'
FG_HEADER = '#BBBBBB'

BG_ROW = '#455A64'
FG_ROW = '#BBBBBB'

BG_ROWODD = '#769BAE'
FG_ROWODD = '#222222'

QGRID_CSS = f"""
<style>
  .q-grid {{
    background-color: {BG_HEADER};
    height: auto;
    width: auto;
    max-height: 600px;
  }}
  .q-grid .slick-header, .q-grid .slick-header-columns {{
    background-color: {BG_HEADER};
  }}
  .q-grid .slick-header-column {{
    background-color: {BG_HEADER};
    color: {FG_HEADER};
    border-color: {FG_HEADER};
  }}
  .q-grid .slick-row.odd {{
    background-color: {BG_ROWODD};
    color: {FG_ROWODD};
    border-color: {FG_ROWODD};
  }}
  .q-grid .slick-row.even {{
    background-color: {BG_ROW};
    color: {FG_ROW};
    border-color: {FG_ROW};
  }}
  .q-grid .slick-resizable-handle {{
    background-color: {BG_ROW};
    border-left-color: {BG_ROWODD};
    border-right-color: {BG_ROWODD};
    border-left-width: 1px;
    border-right-width: 1px;
  }}
</style>
"""

def display_obj(obj):
  display(obj)

def display_html(html):
  display_obj(HTML(html))

def render_svg(data, b64=True):
  svg_data = str(base64.b64encode(data)) if b64 else data
  # b64 = str(base64.b64encode(svg).decode('utf-8'))
  display_obj(SVG(svg_data))  # , raw=raw)

def init_df_grid_style():
  display_obj(HTML(QGRID_CSS))

def md(md_text, render=True):
  markdown = Markdown(str(md_text))
  return display_obj(markdown) if render else markdown

def md_code(md_code: any, syntax: str = '', escape=True, render=True, squish=False, simple=True):
  md_txt = escape_md(md_code) if escape else str(md_code)
  code_text = squish_text(md_txt) if squish else md_txt
  code_text = textwrap.indent(code_text, INDENT)
  if simple:
    return md(f"`{code_text}`{NEWLINE}", render=render)
  else:
    return md(f"```{syntax}{NEWLINE}{code_text}{NEWLINE}```", render=render)

def md_table(cols, vals, header=True):
  md(table_md(cols, vals, header=header))

def md_list(rows, render=True, bullet='*', header=None):
  bullets = [f"{bullet} {row}" for row in rows]
  md_bullets = CR.join(bullets)
  markdown = f"{header}{CR}{md_bullets}" if header else md_bullets
  md(markdown, render=render)

# Usage: horizontally('foo', 'bar', '`baz`')
def horizontally(*items):
  cells_html = ''.join([(CELL_HTML % item) for item in items])
  md(TABLE_HTML % (ROW_HTML % cells_html))

def vertically(*items):
  rows_html = ''.join([(ROW_HTML % (CELL_HTML % item)) for item in items])
  md(TABLE_HTML % (rows_html))

# Add escape characters to string to avoid marking down:
def escape_md(obj):
  md = str(obj)
  return md.replace('_', '\_')

def table_header_md(cols):
  col_names = cols.values() if hasattr(cols, 'values') else cols
  col_captions = [f"<th>{(col.title())}</th>" for col in col_names]
  # md_cols = "<tr>%s</tr>" % COL_SEP.join(col_captions)
  # md_sep = "| :--- " * len(col_names) + '|'
  return "<tr>%s</tr>" % ''.join(col_captions)  # f"{md_cols}{NEWLINE}{md_sep}"

def table_body_md(cols, vals):
  md_rows = []
  col_names = cols.keys() if hasattr(cols, 'keys') else cols
  for row in vals:
    row_vals = [f"<td>{str(row[col])}</td>" for col in col_names]
    md_row = ''.join(row_vals)
    md_rows.append("<tr>%s</tr>" % md_row)

  return NEWLINE.join(md_rows)

def table_md(cols, vals, caption=None, header=True):
  md_rows = ['<table>']

  # if caption: md_rows.append(f"### {caption}")
  if header:
    md_rows.append(table_header_md(cols))

  md_rows.append(table_body_md(cols, vals))
  md_rows.append('</table>')
  return NEWLINE.join(md_rows)

def pretty_json(json, markdown=True):
  return pretty(json, markdown=markdown, format=PrettyFormats.json)

def pretty(code, markdown=True, format=PrettyFormats.python, render=True):
  code_str = json.dumps(code, indent=2) if format == PrettyFormats.json else str(code)
  formatter = HtmlFormatter(style=JupyterStyle)
  # lexer = PythonLexer if format==PrettyFormats.PYTHON else JsonLexer
  lexer = get_lexer_by_name("json", stripall=False)
  html = highlight(code_str, lexer, formatter)
  css = formatter.get_style_defs('.highlight')
  html = f'<style>{css}</style><div class="highlight">{html}</div>'
  return display_html(html) if markdown else html

def md_dataframe(df, heading=None, include_index: bool = False, render: bool = True, sortable: bool = False, filterable: bool = False, allrows: bool = False, plain: bool = False):

  if plain:
    html = df.to_html(index=False)
    if render:
      return(HTML(html))
    else:
      return html
  else:
    min_rows = len(df.index_name) + 2 if allrows else min(MIN_VISIBLE_ROWS, len(df.index_name) + 1)
    widget = qgrid.show_grid(df, show_toolbar=False, grid_options=dict(
        forceFitColumns=False,
        syncColumnCellResize=True,
        fullWidthRows=False,
        minVisibleRows=min_rows,
        sortable=sortable,
        filterable=filterable,
    ))

    header = f"## {heading}" if heading else None
    if render:
      if header:
        md(header, render=render)
      return(widget)
    else:
      return widget
