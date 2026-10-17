"""Evidence-linked SVG and accessible HTML storyboards. No external scripts or assets."""
from html import escape
import math
import textwrap
from .engines import sha

LABELS={
 'uk':{'text':'Текст','historical':'Історичні дані','inferred':'Висновок','reconstruction':'Реконструкція','uncertain':'Невизначено','map':'Координатна схема; наближена рівнопроміжна проєкція; без реконструйованих кордонів.','timeline':'Календарну систему й невизначеність діапазонів дат наведено в джерелах.','schematic':'Схематична реконструкція; пунктир позначає невизначені або художньо доповнені частини.'},
 'en':{'text':'Text','historical':'Historical evidence','inferred':'Inference','reconstruction':'Reconstruction','uncertain':'Uncertain','map':'Coordinate plot; approximate equirectangular projection; no reconstructed borders.','timeline':'Date ranges use the calendar convention and uncertainty stated in the source legend.','schematic':'Schematic reconstruction; dashed geometry indicates uncertain or artistic completion.'},
 'ru':{'text':'Текст','historical':'Исторические данные','inferred':'Вывод','reconstruction':'Реконструкция','uncertain':'Неопределённо','map':'Координатная схема; приближённая равнопромежная проекция; без реконструированных границ.','timeline':'Календарная система и неопределённость диапазонов дат указаны в источниках.','schematic':'Схематическая реконструкция; пунктир обозначает неопределённые или художественно дополненные части.'}}

def render(spec):
    if not isinstance(spec,dict) or spec.get('kind') not in {'map','timeline','comparison','reconstruction','slides'}: raise ValueError('Unknown visual kind')
    if spec.get('language') not in {'uk','en','ru'}: raise ValueError('Unsupported language')
    labels=LABELS[spec['language']]
    for k in ('title','description'):
        if not isinstance(spec.get(k),str) or not spec[k].strip(): raise ValueError('Visual requires '+k)
    if len(spec['title'])>180 or len(spec['description'])>2000:raise ValueError('Visual heading exceeds layout bounds')
    items=spec.get('items')
    if not isinstance(items,list) or not items or len(items)>60: raise ValueError('Visual needs 1–60 items')
    for item in items:
        if not isinstance(item,dict): raise ValueError('Invalid visual item')
        for k in ('label','detail','source','certainty'):
            if not isinstance(item.get(k),str) or not item[k].strip(): raise ValueError('Item requires '+k)
        if item['certainty'] not in {'text','historical','inferred','reconstruction','uncertain'}: raise ValueError('Unknown certainty')
        if any(len(item[k])>1000 for k in ('label','detail','source')): raise ValueError('Item text exceeds visual bounds')
        if spec['kind']=='map':
            for k,limit in [('lat',90),('lon',180)]:
                if type(item.get(k)) not in (int,float) or not math.isfinite(item[k]) or abs(item[k])>limit: raise ValueError('Map needs valid source-backed coordinates')
        if spec['kind']=='timeline':
            if type(item.get('start')) not in (int,float) or type(item.get('end')) not in (int,float) or not math.isfinite(item['start']) or not math.isfinite(item['end']) or item['start']>item['end']: raise ValueError('Timeline needs a valid date range')
    if spec['kind']=='reconstruction' and not any(i['certainty'] in {'reconstruction','uncertain'} for i in items): raise ValueError('Reconstructions must label uncertainty')
    elements=spec.get('elements',[])
    if not isinstance(elements,list) or len(elements)>100:raise ValueError('Invalid reconstruction elements')
    for element in elements:
        if not isinstance(element,dict) or element.get('shape') not in {'rect','line','circle'} or type(element.get('source_item'))!=int or not 1<=element['source_item']<=len(items):raise ValueError('Each diagram element needs a supported shape and source item')
        for k in {'rect':('x','y','width','height'),'line':('x','y','x2','y2'),'circle':('x','y','r')}[element['shape']]:
            if type(element.get(k)) not in (int,float) or not math.isfinite(element[k]) or not 0<=element[k]<=100:raise ValueError('Diagram coordinates must be finite percentages')
        if element['shape']=='rect' and (element['x']+element['width']>100 or element['y']+element['height']>100):raise ValueError('Rectangle exceeds diagram bounds')
        if element['shape']=='circle' and (element['x']-element['r']<0 or element['x']+element['r']>100 or element['y']-element['r']<0 or element['y']+element['r']>100):raise ValueError('Circle exceeds diagram bounds')
    esc=lambda s:escape(str(s),quote=True)
    # Height expands from actual wrapped text, avoiding clipped fixed-height rows.
    rows=[]
    for i,item in enumerate(items,1):
        title=str(i)+'. '+item['label']+' ['+labels[item['certainty']]+']'
        detail=item['detail']+' | '+item['source']
        if spec['kind']=='map':detail+=' | lat '+str(item['lat'])+', lon '+str(item['lon'])
        if spec['kind']=='timeline':detail+=' | '+str(item['start'])+' to '+str(item['end'])
        lines=textwrap.wrap(title,95)+textwrap.wrap(detail,110)
        rows.append(lines)
    map_height=380 if spec['kind']=='map' else 190+len(items)*34 if spec['kind']=='timeline' else 360 if spec['kind']=='reconstruction' and elements else 0
    height=150+map_height+sum(34+len(r)*24 for r in rows)
    parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc" xml:lang="{spec["language"]}">',f'<title id="title">{esc(spec["title"])}</title>',f'<desc id="desc">{esc(spec["description"])}</desc>','<rect width="100%" height="100%" fill="#ffffff"/>','<g fill="#17252b" font-family="Arial, sans-serif">']
    for j,line in enumerate(textwrap.wrap(spec['title'],70)): parts.append(f'<text x="36" y="{42+j*30}" font-size="26">{esc(line)}</text>')
    y=110
    if spec['kind']=='map':
        lons=[i['lon'] for i in items];lats=[i['lat'] for i in items]
        lo=min(lons)-1;hi=max(lons)+1;la=min(lats)-1;lb=max(lats)+1
        parts.append('<rect x="40" y="110" width="920" height="300" fill="#f2f5f6" stroke="#52676f"/>')
        parts.append('<text x="40" y="440" font-size="17">'+esc(labels['map'])+'</text>')
        for i,item in enumerate(items,1):
            x=40+(item['lon']-lo)/(hi-lo)*920;py=110+(lb-item['lat'])/(lb-la)*300
            parts.extend([f'<circle cx="{x:.2f}" cy="{py:.2f}" r="7" fill="#17252b"/>',f'<text x="{x+10:.2f}" y="{py:.2f}" font-size="18">{i}</text>'])
        y+=map_height
    elif spec['kind']=='timeline':
        start=min(i['start'] for i in items);end=max(i['end'] for i in items);span=max(1,end-start)
        axis=y+30
        parts.append(f'<line x1="50" y1="{axis}" x2="950" y2="{axis}" stroke="#52676f" stroke-width="2"/>')
        parts.append(f'<text x="50" y="{axis-12}" font-size="16">{esc(start)}</text><text x="890" y="{axis-12}" font-size="16">{esc(end)}</text>')
        for index,item in enumerate(items,1):
            left=50+(item['start']-start)/span*900;right=50+(item['end']-start)/span*900;row_y=axis+index*34
            parts.append(f'<line x1="{left:.2f}" y1="{row_y}" x2="{max(left+2,right):.2f}" y2="{row_y}" stroke="#17252b" stroke-width="8"/>')
            parts.append(f'<text x="{min(left+8,910):.2f}" y="{row_y-8}" font-size="16">{index}</text>')
        parts.append(f'<text x="50" y="{axis+len(items)*34+40}" font-size="16">'+esc(labels['timeline'])+'</text>')
        y+=map_height
    elif spec['kind']=='reconstruction' and elements:
        parts.append(f'<rect x="40" y="{y}" width="920" height="300" fill="#f2f5f6" stroke="#52676f"/>')
        for element in elements:
            x=40+element['x']*9.2;py=y+element['y']*3
            source=items[element['source_item']-1];dash=' stroke-dasharray="7 5"' if source['certainty'] in {'uncertain','reconstruction'} else ''
            if element['shape']=='rect':shape=f'<rect x="{x}" y="{py}" width="{element["width"]*9.2}" height="{element["height"]*3}"'
            elif element['shape']=='circle':shape=f'<circle cx="{x}" cy="{py}" r="{element["r"]*3}"'
            else:shape=f'<line x1="{x}" y1="{py}" x2="{40+element["x2"]*9.2}" y2="{y+element["y2"]*3}"'
            parts.append(shape+' fill="none" stroke="#17252b" stroke-width="2"'+dash+'/>')
            parts.append(f'<text x="{x+5}" y="{py+20}" font-size="16">{element["source_item"]}</text>')
        parts.append(f'<text x="40" y="{y+330}" font-size="16">'+esc(labels['schematic'])+'</text>');y+=map_height
    for row in rows:
        for j,line in enumerate(row):parts.append(f'<text x="36" y="{y}" font-size="{20 if j==0 else 16}">{esc(line)}</text>');y+=24
        y+=34
    parts.extend(['</g>','</svg>']);svg=''.join(parts)
    cards=''.join('<section><h2>'+esc(i['label'])+'</h2><p>'+esc(i['detail'])+'</p><p>'+esc(labels[i['certainty']])+' · '+esc(i['source'])+'</p></section>' for i in items)
    html='<!doctype html><html lang="'+spec['language']+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; img-src data:"><title>'+esc(spec['title'])+'</title><style>body{margin:2rem auto;padding:0 1rem;max-width:72rem;color:#17252b;background:white;font:18px/1.5 Arial,sans-serif}svg{width:100%;height:auto}section{break-inside:avoid;border-top:1px solid #52676f;padding:1rem 0}@media print{section{break-after:page}}</style><h1>'+esc(spec['title'])+'</h1><p>'+esc(spec['description'])+'</p>'+svg+cards+'</html>'
    return {'svg':svg,'html':html,'sha256':sha(svg),'scope':'Source-linked visual export; facts and rendering require review'}
