import markdown
import os
import subprocess

md_path = "research_paper.md"
html_path = "research_paper_formatted.html"
pdf_path = "research_paper.pdf"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split("## 1. Introduction", 1)
header_md = parts[0]
body_md = "## 1. Introduction" + (parts[1] if len(parts) > 1 else "")

html_header = markdown.markdown(header_md, extensions=['tables'])
html_body = markdown.markdown(body_md, extensions=['tables'])

html_header = html_header.replace('<h2>Abstract</h2>', '<p class="abstract"><strong>Abstract—</strong>')
html_header = html_header.replace('<p><strong>Keywords:</strong>', '</p><p class="keywords"><strong>Keywords—</strong>')
html_header = html_header.replace('<p><strong>Author:</strong>', '<p class="author"><strong>Author:</strong>')

html_body = html_body.replace('<em>Figure', '<p class="caption">Figure')
html_body = html_body.replace('</em>', '</p>')

css = '''
    @page { 
        size: A4; 
        margin: 20mm 15mm 20mm 15mm; 
    }
    body { 
        font-family: "Times New Roman", Times, serif; 
        font-size: 10pt; 
        line-height: 1.15; 
        color: black; 
        text-align: justify;
    }
    
    .header { 
        text-align: center; 
        margin-bottom: 2em; 
    }
    .header h1 { 
        font-size: 20pt; 
        font-weight: bold; 
        line-height: 1.1; 
        margin-bottom: 0.5em; 
    }
    .header p.author {
        font-size: 12pt;
        margin-bottom: 1em;
    }
    .header p.abstract { 
        text-align: justify; 
        font-weight: bold; 
        margin: 1.5em 1.5cm 0.5em 1.5cm; 
        font-size: 9.5pt;
    }
    .header p.keywords { 
        text-align: justify; 
        font-weight: bold;
        font-style: italic;
        margin: 0 1.5cm 1em 1.5cm; 
        font-size: 9.5pt;
        border-bottom: 1px solid #ccc;
        padding-bottom: 1em;
    }
    hr { display: none; }
    
    .content { 
        column-count: 2; 
        column-gap: 0.6cm; 
        text-align: justify; 
    }
    
    h2 { 
        font-size: 11pt; 
        font-weight: bold; 
        margin-top: 1.4em; 
        margin-bottom: 0.4em;
        text-align: center;
        text-transform: uppercase;
        break-after: avoid;
    }
    h3 { 
        font-size: 10pt; 
        font-weight: bold; 
        font-style: italic; 
        margin-top: 1.2em; 
        margin-bottom: 0.3em; 
        break-after: avoid;
    }
    
    p { 
        margin-top: 0; 
        margin-bottom: 0.5em; 
        text-indent: 1em; 
    }
    h2 + p, h3 + p { 
        text-indent: 0; 
    }
    
    img { 
        max-width: 100%; 
        height: auto; 
        display: block; 
        margin: 1.5em auto 0.5em auto; 
    }
    .caption { 
        text-align: center; 
        font-size: 8.5pt; 
        margin-top: 0; 
        margin-bottom: 1.5em; 
        text-indent: 0;
    }
'''

full_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
{css}
</style>
</head>
<body>
    <div class="header">
        {html_header}
    </div>
    <div class="content">
        {html_body}
    </div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)
print("Generated HTML.")
