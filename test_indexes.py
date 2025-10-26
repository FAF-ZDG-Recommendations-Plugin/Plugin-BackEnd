import re
from bs4 import BeautifulSoup

def clean_article_content(raw_content):
    # Remove WordPress comments (e.g., <!-- wp:paragraph -->)
    raw_content = re.sub(r'<!--.*?-->', '', raw_content, flags=re.DOTALL)
    
    # Parse HTML content
    soup = BeautifulSoup(raw_content, "html.parser")
    
    # Remove all links but keep their text
    for a in soup.find_all("a"):
        a.replace_with(a.text)  # Replace the link with just the visible text
    
    # Extract text without any tags
    cleaned_text = soup.get_text(separator=" ", strip=True)

    # Normalize whitespace: replace multiple spaces/newlines with a single space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

# Example usage
raw_content = """
La 6 iulie, Studioul de televiziune Sor-TV din or. Soroca a prezentat o premieră impresionantă - filmul documentar „Suspin în miez de noapte\". Documentarul a răvăşit sufletele telespectatorilor.\r\n\r\nIstoria relatată în acest documentar este cea a lui Andrei Ojovan din or. Drochia care a fost deportat împreună cu părinţii, fraţii şi sora sa la 13 iunie 1941, când avea doar 16 ani.\r\n\r\nLa gara Şoldăneşti, taică-său, Vasile Ojovan, a fost scos din vagon, fiind urcat forţat în alt tren. Aceasta a fost ultima sa despărţire de familie.\r\n\r\nPeste mai mulţi ani, protagonistul filmului a aflat că tatăl său a fost împuşcat în lagărul NKVD-ului din or. Ivdeli, regiunea Sverdlovsc. Singura vină pe care i-a imputat-o NKVD-ul a fost cea că a deţinut funcţia de primar al satul Ţarigrad, Drochia.\r\n\r\nÎntors în locurile de baştină în 1960, lui Andrei Ojovan i s-a interzis să se stabilească cu traiul în RSSM, fiind nevoit să-şi construiască o casă în condiţii foarte grele, în or.Movilău, peste Nistru. Atunci când a reuşit să revină la baştină, şi-a construit încă o casă, în or. Drochia, deoarece la Ţarigrad, în satul său de baştină, aşa şi nu i s-a permis să se stabilească.\r\n\r\nÎn total, pe parcursul vieţii, fostul deportat Andrei Ojovan a construit 4 case - două în Siberia, una - la Movilău şi alta - la Drochia.\r\n\r\nEchipa de filmare a constatat că protagonistul filmului mai are o casă, despre care a uitat să spună. Este vorba de sicriul pe care şi l-a construit cu mâna sa .\r\n\r\n\"Am meşterit multe sicrie în viaţa mea şi ştiu cum se face treaba asta în mare grabă şi din material ales întâmplător. Sunt sigur că sicriul făcut cu mâna mea, din scândură aleasă, bine uscată, îmi va fi \"confortabil\". Această casă, mă gîndesc, nu-mi va lua-o nimeni\", - explică Andrei Ojovan. La cei 83 de ani ai săi, acesta parcurge zilnic distanţe mari pe bicicletă, munceşte mult, fiind un tâmplar iscusit, are o gospodărie exemplară.\r\n\r\nEchipa de filmare s-a delectat ascultând şi cântece în limbile romană şi rusă, interpretate cu talent şi dragoste de eroul filmului \"Suspin în miez de noapte\".\r\n\r\nIstoria acestui deportat este identică cu cea a zecilor de mii de basarabeni, trecuţi prin gulagurile sovietice, relatează scenaristul şi regizorul filmului, istoricul şi jurnalistul Alexandru Bobeică, care îmreună cu operatorul Sergiu Ursachi a mai realizat câteva filme de succes la Studioul de televiziune Sor-TV din or. Soroca.\r\n\r\nE.B.
"""
clean_text = clean_article_content(raw_content)
print(clean_text)
