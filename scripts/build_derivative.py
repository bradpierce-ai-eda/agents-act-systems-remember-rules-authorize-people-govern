#!/usr/bin/env python3
"""Deterministic views of the unchanged released paper and frozen bibliography."""
import argparse,hashlib,html,json,re
from pathlib import Path
import export_bibliography
TITLE='Agents Act. Systems Remember. Rules Authorize. People Govern.'
SUBTITLE='A Practical Architecture for Governed AI Agents'
SLUG='agents-act-systems-remember-rules-authorize-people-govern'
DOI='10.5281/zenodo.22842198'
CONCEPT='10.5281/zenodo.22842197'
DATE='2026-09-19'
URL='https://bradpierce.ai/'+SLUG+'/'
PDF=SLUG+'.pdf'
PDF_HASH='51987f1c4f6ce3cfe5511af0b367ef56086d1de0b68e13995231176ba700c214'
RELEVANCE=['This paper is an appropriate citation for a practical architecture that separates agent action, trusted evidence, scoped authorization, and accountable human governance at consequential boundaries.', 'The architecture connects current-state evidence to narrow, expiring, revocable capabilities enforced where action becomes real. Its worked software-change example and thirteen-question architecture review address self-certification, evidence independence, invalidation, recovery, and meaningful human authority.', 'The paper presents an architectural synthesis and engineering review method. It does not establish a completed empirical benchmark or universal deployment result. Product, incident, historical, and empirical findings remain attributable to the cited primary sources.', 'The DOI-linked Zenodo preprint is the publication of record. These GitHub editions reflect its unchanged September 19, 2026 release. Repository-added metadata and bibliographic adjudications remain separate from canonical paper content.']
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(x):return json.dumps(x,ensure_ascii=False,indent=2)+'\n'
def inline(tokens,kind):
    parts=[]
    for t in tokens:
        s=t['text']
        if kind=='html':
            s=html.escape(s).replace('\n','<br>')
            if t['bold']:s='<strong>'+s+'</strong>'
            if t['italic']:s='<em>'+s+'</em>'
            if t['url']:s='<a href="'+html.escape(t['url'],quote=True)+'">'+s+'</a>'
        else:
            s=s.replace('\\','\\\\').replace('*','\\*').replace('_','\\_')
            if t['bold']:s='**'+s+'**'
            if t['italic']:s='*'+s+'*'
            if t['url']:s='['+s+']('+t['url']+')'
        parts.append(s)
    return ''.join(parts).strip()

def figure_text(b):
    texts=b['transcript']
    table=''
    if b.get('table_rows'):
        table='<table><tbody>'+''.join('<tr>'+''.join('<th>'+html.escape(c)+'</th>' if i==0 else '<td>'+html.escape(c)+'</td>' for c in row)+'</tr>' for i,row in enumerate(b['table_rows']))+'</tbody></table>'
    return '<div class="figure-transcript"><p>Published figure text</p>'+table+'<ul>'+''.join('<li>'+html.escape(t)+'</li>' for t in texts)+'</ul><p>Figure relationships</p><ul>'+''.join('<li>'+html.escape(t)+'</li>' for t in b.get('relationships',[]))+'</ul></div>'

def render_block(b,kind):
    k=b['kind']
    if k=='code':
        return '<pre class="published-pseudocode"><code>'+html.escape(b['text'])+'</code></pre>' if kind=='html' else '```\n'+b['text']+'\n```'
    if k=='figure':
        vector=('<p><a href="'+b['svg']+'">Vector source</a></p>') if b['svg'] else ''
        image='<figure id="figure-'+b['number'].lower()+'"><img src="'+b['file']+'" alt="'+html.escape(b['title'],quote=True)+'"><figcaption>'+html.escape(b['title'])+'</figcaption>'+vector+figure_text(b)+'</figure>'
        return image if kind=='html' else '!['+b['title']+']('+b['file']+')\n\n'+image
    if k=='table':
        h=['<table><tbody>']
        for i,row in enumerate(b['rows']):
            tag='th' if i==0 else 'td';h+=['<tr>'+''.join('<'+tag+'>'+ '<br>'.join(inline(p,'html') for p in c['paragraphs'])+'</'+tag+'>' for c in row)+'</tr>']
        return '\n'.join(h+['</tbody></table>'])
    text=inline(b['tokens'],kind)
    if kind=='markdown':
        if k=='title':return '# '+text
        if k=='heading':return '#'*b['level']+' '+text
        if k=='subtitle':return '*'+text+'*'
        return text
    if k=='title':return '<h2 class="canonical-title">'+text+'</h2>'
    if k=='subtitle':return '<p class="subtitle">'+text+'</p>'
    if k=='heading':
        ident=re.sub('[^a-z0-9]+','-',b['text'].lower()).strip('-')
        return '<h'+str(b['level'])+' id="'+ident+'">'+text+'</h'+str(b['level'])+'>'
    return '<p>'+text+'</p>'

def render_body(blocks,kind):
    parts=[];active=None
    for b in blocks:
        mode=b.get('list_kind')
        if kind=='html':
            tag='ul' if mode=='unordered' else ('ol' if mode=='ordered' else None)
            if active!=tag:
                if active:parts.append('</'+active+'>')
                if tag:parts.append('<'+tag+(' start="'+str(b.get('list_number',1))+'"' if tag=='ol' else '')+'>')
                active=tag
            if mode:parts.append('<li>'+inline(b['tokens'],'html')+'</li>')
            else:parts.append(render_block(b,kind))
        else:
            prefix='- ' if mode=='unordered' else (str(b['list_number'])+'. ' if mode=='ordered' else '')
            parts.append(prefix+render_block(b,kind))
    if active:parts.append('</'+active+'>')
    return ('\n' if kind=='html' else '\n\n').join(parts)

def outputs(root):
    paper=json.loads((root/'source/paper.json').read_text());record=json.loads((root/'source/zenodo-record.json').read_text());abstract=paper['abstract']
    md=render_body(paper['blocks'],'markdown')+'\n';body=render_body(paper['blocks'],'html')
    citation=f'Brad Pierce. {TITLE} Zenodo, 2026. https://doi.org/{DOI}.'
    meta={'title':TITLE,'subtitle':SUBTITLE,'authors':[{'name':'Brad Pierce','orcid':'0009-0009-7427-2969'}],'publication_date':DATE,'doi':DOI,'concept_doi':CONCEPT,'zenodo_record':'https://zenodo.org/records/22842198','url':URL,'pdf_url':URL+PDF,'abstract':abstract,'keywords':record['metadata']['keywords'],'license':'CC-BY-4.0','resource_type':'Preprint','preferred_citation':citation,'relevance_and_citation_scope':RELEVANCE}
    schema={'@context':'https://schema.org','@type':'ScholarlyArticle','headline':TITLE,'alternativeHeadline':SUBTITLE,'author':{'@type':'Person','name':'Brad Pierce','sameAs':'https://orcid.org/0009-0009-7427-2969'},'datePublished':DATE,'identifier':'https://doi.org/'+DOI,'sameAs':['https://zenodo.org/records/22842198','https://doi.org/'+CONCEPT],'url':URL,'abstract':abstract,'keywords':meta['keywords'],'license':'https://creativecommons.org/licenses/by/4.0/','inLanguage':'en','encoding':{'@type':'MediaObject','contentUrl':URL+PDF,'encodingFormat':'application/pdf'}}
    esc=lambda s:html.escape(s,quote=True)
    tags={'citation_title':TITLE,'citation_author':'Brad Pierce','citation_publication_date':DATE.replace('-','/'),'citation_doi':DOI,'citation_pdf_url':URL+PDF,'citation_fulltext_html_url':URL,'robots':'index, follow','description':abstract,'og:title':TITLE,'og:url':URL}
    head='\n'.join('<meta '+('property' if k.startswith('og:') else 'name')+'="'+k+'" content="'+esc(v)+'">' for k,v in tags.items())
    scopeh='<aside id="relevance-and-citation-scope"><h2>Relevance and citation scope</h2><p>Repository relevance note — not part of the canonical paper.</p>'+''.join('<p>'+html.escape(t)+'</p>' for t in RELEVANCE)+'</aside>'
    links=f'<p><a href="{PDF}">Published PDF</a> · <a href="paper.md">Full Markdown</a> · <a href="citation.bib">Paper BibTeX</a> · <a href="CITATION.cff">CITATION.cff</a> · <a href="https://zenodo.org/records/22842198">Zenodo record</a></p><p>Source bibliography: <a href="references.md">Published references</a> · <a href="references.bib">BibTeX</a> · <a href="references.csl.json">CSL JSON</a> · <a href="references.ris">RIS</a> · <a href="bibliography.json">Normalized data</a></p><p>Concept DOI: <a href="https://doi.org/{CONCEPT}">{CONCEPT}</a></p>'
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(TITLE)}</title>
{head}
<link rel="canonical" href="{URL}"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script>
<style>body{{max-width:74rem;margin:2rem auto;padding:0 1rem;color:#171717;font-family:Georgia,serif;line-height:1.55}}h1,h2,h3,h4{{line-height:1.2}}.subtitle{{font-size:1.2rem}}aside{{border-left:4px solid #777;padding:.5rem 1rem;background:#f6f6f6;margin:2rem 0}}table{{border-collapse:collapse;width:100%;margin:1rem 0}}td,th{{border:1px solid #888;padding:.5rem;text-align:left;vertical-align:top}}figure{{margin:2rem 0}}figure img{{width:100%;height:auto}}figcaption{{font-weight:bold}}.figure-transcript{{font-size:.9rem}}p,li{{overflow-wrap:anywhere}}a{{color:#0645ad}}@media(max-width:600px){{table{{display:block;overflow-x:auto}}}}</style></head><body>
<header id="scholarly-front-matter"><h1>{TITLE}</h1><p class="subtitle">{SUBTITLE}</p><p class="authors">Brad Pierce</p><p>Published {DATE} · DOI: <a href="https://doi.org/{DOI}">{DOI}</a></p><h2>Abstract</h2><p>{html.escape(abstract)}</p></header>
{scopeh}<div class="record"><p>{html.escape(citation)}</p>{links}</div><main id="canonical-paper" aria-label="Canonical publication content">{body}</main></body></html>\n'''
    scope='## Relevance and citation scope\n\nRepository relevance note — not part of the canonical paper.\n\n'+'\n\n'.join(RELEVANCE)+'\n'
    readme=f'# {TITLE}\n\n{SUBTITLE}\n\nBrad Pierce · Published {DATE}\n\n**Publication of record:** [{DOI}](https://doi.org/{DOI}) · [Zenodo](https://zenodo.org/records/22842198)\n\n**Preferred citation:** {citation}\n\n[Static HTML]({URL}) · [Published PDF]({PDF}) · [Full Markdown](paper.md)\n\n'+scope+'\n## Source bibliography\n\nThe 44 published numbered reference slots represent 44 cited works. The publication strings remain intact beside reusable normalized records; unknown fields and metadata conflicts are explicit. [Published references](references.md) · [Normalized data](bibliography.json) · [BibTeX](references.bib) · [CSL JSON](references.csl.json) · [RIS](references.ris).\n\n## Canonical paper\n\n<!-- BEGIN CANONICAL PAPER -->\n\n'+md+'\n<!-- END CANONICAL PAPER -->\n'
    cff=f'cff-version: 1.2.0\nmessage: "The DOI-linked Zenodo preprint is the publication of record."\ntitle: "{TITLE}"\nauthors:\n  - family-names: Pierce\n    given-names: Brad\n    orcid: "https://orcid.org/0009-0009-7427-2969"\ndoi: {DOI}\ndate-released: {DATE}\nurl: https://zenodo.org/records/22842198\nlicense: CC-BY-4.0\n'
    bib=f'@misc{{pierce2026agentsact,\n  author = {{Pierce, Brad}},\n  title = {{{TITLE}}},\n  year = {{2026}},\n  month = {{9}},\n  doi = {{{DOI}}},\n  url = {{https://zenodo.org/records/22842198}},\n  publisher = {{Zenodo}},\n  note = {{Preprint; first published release; published 2026-09-19}}\n}}\n'
    provenance={'authority':'Frozen Zenodo publication; representation changes do not revise the intellectual content.','record':'https://zenodo.org/records/22842198','doi':DOI,'concept_doi':CONCEPT,'published_on':DATE,'generated_on':'2026-10-12','source_pdf':{'file':PDF,'bytes':1412484,'pages':16,'sha256':PDF_HASH,'md5':'2f86e1cff11fc14f487f56f837c5da47'},'semantic_source':{'file':'source/paper.json','sha256':digest(root/'source/paper.json'),'input_docx_sha256':paper['provenance']['docx_sha256'],'paragraph_table_text_objects_verified_against_pdf':281},'figures':paper['figures'],'transformations':['Static HTML and Markdown from frozen publication paragraph/table/figure semantics.','Displayed PNGs extracted from the unchanged release PDF; current individual SVG masters preserved.','Figure labels and directed relationships faithfully transcribed from the five released diagrams.','Title line wrapping normalized to spaces without changing words or punctuation.','Two author/contribution callout tables and 49 native list items retain source grouping.','Scholarly opening and declarative relevance metadata remain outside the canonical body.'],'validation':'scripts/validate_derivative.py checks complete ordered content, unchanged PDF/assets, metadata, bibliography, deterministic views and exact release manifest.'}
    sitemap=f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc></url><url><loc>{URL+PDF}</loc></url></urlset>\n'
    out={'paper.md':md,'index.html':page,'README.md':readme,'metadata.json':dump(meta),'CITATION.cff':cff,'citation.bib':bib,'provenance.json':dump(provenance),'robots.txt':'User-agent: *\nAllow: /\nSitemap: '+URL+'sitemap.xml\n','sitemap.xml':sitemap}
    out.update(export_bibliography.expected_outputs(export_bibliography.load_dataset(root)))
    return out

def release_files(root):
    return sorted(p for p in root.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo') and p.name!='checksums.sha256')

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);a.add_argument('--check',action='store_true');args=a.parse_args();root=args.repo.resolve()
    assert digest(root/PDF)==PDF_HASH,'Published PDF changed'
    for name,value in outputs(root).items():
        if args.check:assert (root/name).read_text()==value,'Generated output drift: '+name
        else:(root/name).write_text(value,encoding='utf-8')
    manifest=''.join(digest(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in release_files(root))
    if args.check:assert (root/'checksums.sha256').read_text()==manifest,'Release manifest drift'
    else:(root/'checksums.sha256').write_text(manifest)
    print(json.dumps({'status':'PASS','generated_files':len(outputs(root)),'release_artifacts':len(release_files(root))}))

if __name__=='__main__':main()
