#!/usr/bin/env python3
"""Generates the static site. Edit the data below, then run: python3 build.py"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).parent
SITE = ROOT.parent
SVG = lambda n: (ROOT / 'svg' / n).read_text()
SITE_URL = 'https://hominparkbcm.github.io'

FONTS = ('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;700'
         '&family=Newsreader:ital,opsz,wght@0,6..72,400..600;1,6..72,400&display=swap')

LINKS = {
    'email': 'mailto:Ho-min.Park@bcm.edu',
    'scholar': 'https://scholar.google.com/citations?user=mFzW6LEAAAAJ',
    'github': 'https://github.com/powersimmani',
    'github_bcm': 'https://github.com/HominParkBCM',
    'orcid': 'https://orcid.org/0000-0001-9937-8617',
    'linkedin': 'https://www.linkedin.com/in/park-ho-min-b46658a6',
}

NAV = [('Surgery', 'index.html#surgery'), ('Radiology', 'index.html#radiology'),
       ('Molecules', 'index.html#molecules'), ('Microscopy', 'index.html#microscopy'),
       ('Signals', 'index.html#signals'), ('Teaching', 'index.html#teaching'),
       ('Publications', 'publications.html'), ('Contact', 'index.html#contact')]


def head(title, desc, path):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="Ho-min Park">
<link rel="canonical" href="{SITE_URL}/{path}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{path}">
<meta property="og:image" content="{SITE_URL}/assets/img/rct-camscore-1600.webp">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="assets/css/site.css">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Person","name":"Ho-min Park","jobTitle":"Assistant Professor","affiliation":{{"@type":"Organization","name":"Baylor College of Medicine"}},"email":"Ho-min.Park@bcm.edu","sameAs":["{LINKS['scholar']}","{LINKS['orcid']}","{LINKS['github']}"]}}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


def header(current):
    items = []
    for label, href in NAV:
        cur = ' aria-current="page"' if label == current else ''
        items.append(f'<a href="{href}"{cur}>{label}</a>')
    return f'''<header class="site-head">
  <div class="wrap">
    <a class="brand" href="index.html">Ho-min Park</a>
    <nav class="nav" aria-label="Sections">{''.join(items)}</nav>
  </div>
</header>
'''


FOOT = '''<footer class="site-foot">
  <div class="wrap">
    <p>Figures come from the papers and public repositories named in each legend. Fig. 6 and the chart in Fig. 2b were drawn for this site; the numbers and findings in them come from the papers.</p>
    <p>Last updated September 2026.</p>
  </div>
</footer>
<dialog class="lb" id="lightbox" aria-label="Enlarged figure">
  <img alt="">
  <div class="lb-bar"><span class="lb-cap"></span><button type="button" class="lb-close">Close</button></div>
</dialog>
<script src="assets/js/site.js" defer></script>
</body>
</html>
'''


def img(name, alt, sizes='(min-width: 1160px) 1100px, 94vw', widths=(900, 1600), full=None, zoom=True):
    srcset = ', '.join(f'assets/img/{name}-{w}.webp {w}w' for w in widths)
    tag = (f'<img src="assets/img/{name}-{widths[-1]}.webp" srcset="{srcset}" sizes="{sizes}" '
           f'alt="{html.escape(alt)}" loading="lazy" decoding="async">')
    if not zoom:
        return tag
    fullsrc = f'assets/img/{name}-full.webp' if full is None else full
    return f'<button type="button" class="zoom" data-full="{fullsrc}" aria-label="Enlarge: {html.escape(alt)}">{tag}</button>'


def panel(letter, body, sub='', pad=True):
    s = f'<p class="sub">{sub}</p>' if sub else ''
    cls = 'panel pad' if pad else 'panel'
    return f'<div class="{cls}"><span class="pl" aria-hidden="true">{letter}</span>{body}{s}</div>'


def plate(no, body, venue, role, title, legend, cite, res, hint='tap'):
    hint_html = {'tap': '<p class="hint">Tap a figure to enlarge it.</p>',
                 'scroll': '<p class="hint">Scroll sideways to see the whole figure.</p>',
                 'both': '<p class="hint">Tap the image to enlarge it. Scroll the chart sideways.</p>'}.get(hint, '')
    legend_html = ''.join(f'<p>{p}</p>' for p in legend)
    res_html = ' '.join(f'<a href="{u}">{t}</a>' for t, u in res)
    return f'''<figure class="plate" id="fig{no}">
  <div class="plate-body">{body}</div>{hint_html}
  <figcaption>
    <div class="meta"><span class="fig-no">Fig. {no}</span>{venue}<br>{role}</div>
    <div class="legend">
      <p class="fig-title">{title}</p>
      {legend_html}
      <p class="cite">{cite}</p>
      <p class="res">{res_html}</p>
    </div>
  </figcaption>
</figure>
'''


def wide_svg(name):
    return f'<div class="svgscroll" tabindex="0" role="region" aria-label="Scrollable figure">{SVG(name)}</div>'


def related(items):
    lis = ''.join(f'<li>{t} <span>{v}</span></li>' for t, v in items)
    return f'<div class="related"><h3>Related papers</h3><ul>{lis}</ul></div>'


def doi(d):
    return f'https://doi.org/{d}'


# ---------------------------------------------------------------- index
def build_index():
    out = [head('Ho-min Park, biomedical AI research',
                'Ho-min Park builds interpretable machine learning for surgical video, radiology and molecular biology at the Texas Children\'s Hospital Data Center, Baylor College of Medicine.',
                ''),
           header(None)]
    out.append(f'''<main id="main">
<div class="wrap">
<section class="hero" aria-labelledby="name">
  <h1 id="name">Ho-min Park</h1>
  <p class="post">Assistant Professor, Texas Children's Hospital Data Center, Baylor College of Medicine, Houston</p>
  <p class="lead">I build machine learning models for surgery, radiology and molecular biology that the clinician or biologist using them can inspect and question. I work as the engineering partner of surgeons and biologists, from model design to interpretability analysis.</p>
  <ul class="links">
    <li><a href="{LINKS['email']}">Email</a></li>
    <li><a href="{LINKS['scholar']}">Google Scholar</a></li>
    <li><a href="{LINKS['github']}">GitHub</a></li>
    <li><a href="{LINKS['orcid']}">ORCID</a></li>
    <li><a href="{LINKS['linkedin']}">LinkedIn</a></li>
  </ul>
</section>
''')

    # ---- Surgery
    out.append('''<section class="theme" id="surgery" aria-labelledby="h-surgery">
  <h2 id="h-surgery">Surgical video</h2>
  <p class="intro">Staging laparoscopy decides whether a patient with gastrointestinal cancer can go on to curative treatment, and that decision often depends on whether a small nodule on the peritoneum is metastasis. With surgeons at Ghent University Hospital I build models that read these videos, and methods that still work when the phase or lesion of interest appears in only a few frames.</p>
''')
    src = 'Tozzi et al., <i>International Journal of Surgery</i> 2026'
    ijs_body = (''
        + '<div class="panels">'
        + panel('a', img('ijs-overview', 'Study overview: staging laparoscopy videos, frame selection and annotation, morphologic assessment by experts, pathology review, then deep learning, machine learning and multimodal models, validated with ROC curves, SHAP and surgeon predictions', widths=(900, 1600)), f'Figure 1 of {src}.')
        + '</div><div class="panels pair" style="margin-top:28px">'
        + panel('b', img('ijs-roc', 'Four ROC curves on the test set: image-based model AUC 0.72, morphology-based model AUC 0.86, multimodal model AUC 0.88, and experts AUC 0.78', sizes='(min-width: 820px) 640px, 94vw', widths=(900, 1600)), f'Figure 3 of {src}.')
        + panel('c', img('ijs-shap', 'SHAP summary plot and mean absolute SHAP values of the morphology-based model; flat surface and presence of neovasculature rank highest', sizes='(min-width: 820px) 360px, 94vw', widths=(900, 1600)), f'Figure 2 of {src}.')
        + '</div>')
    out.append(plate(1, ijs_body,
        'International Journal of Surgery, 2026', 'Co-first author, equal contribution',
        'A multimodal model for peritoneal lesions during staging laparoscopy',
        ['(a) Study design. The cohort had 453 biopsied lesions from 67 patients, split at the patient level. An image model reads intraoperative frames, a second model reads morphologic features scored by two blinded surgeons with a structured checklist, and a multimodal model combines the two.',
         '(b) ROC curves on the independent test set of 13 patients: image-based model AUC 0.72, morphology-based model 0.86, multimodal model 0.88, and the 13 surgeons 0.78.',
         '(c) SHAP values of the morphology model. Neovasculature and marked nodularity moved predictions toward metastasis, while a flat surface and absence of marked contours moved them toward benign.'],
        'Tozzi F, Park HM, Mousavi SA, Van Liefferinge M, Moon D, Fadaei S, et al. <i>International Journal of Surgery</i> 112:373&ndash;383, 2026. Figures reproduced unchanged under the CC BY-NC-ND 4.0 license.',
        [('Paper', doi('10.1097/JS9.0000000000003448'))]))
    tta_body = (panel('a', img('tta-overview', 'Figure 1 of the MICCAI 2026 paper. A film strip of laparoscopic frames passes through a foundation model; in feature space the common-phase prototype covers a wide region while the rare-phase prototype covers a narrow one, so new rare frames are misclassified. Below, the pipeline: training videos give initial prototypes, and test videos pass through a temporal precision filter, an adaptive-threshold update and auto-guided annotation to give updated prototypes.', widths=(1000, 1600)), 'Figure 1 of the paper, reproduced from Park et al., MICCAI 2026.')
        + '<div class="panels" style="margin-top:28px">'
        + panel('b', wide_svg('fig-tta-results.svg'))
        + '</div>')
    out.append(plate(2, tta_body,
        'MICCAI 2026', 'First and corresponding author',
        'Test-time adaptation for rare surgical phases',
        ['(a) A rare-phase prototype built from a few videos covers only a narrow region of feature space, so new rare frames (&times;) are assigned to a common phase. Adding more rare-phase training videos does not close this gap, because averaging frames from different surgical contexts dilutes the prototype. We call this the coverage-gap paradox. The method adapts the prototypes at test time on frozen foundation-model features: a temporal precision filter (stages 1 and 2), an adaptive per-class threshold for pseudo-labels (stage 3), and annotation of five frames chosen by decision margin (stages 4 and 5).',
         '(b) Rare-phase accuracy with one rare-labeled training video, or five for Cholec80, where rare labels were masked instead of videos removed. Temporal uses no labels at test time; Combined adds five annotated frames. The adaptation adds about 20K parameters and runs in under 0.1 ms per frame.'],
        'Park HM, Tozzi F, De Muynck R, Kim N, Rashidian N, Willaert W, De Neve W, Vankerschaver J. <i>Medical Image Computing and Computer Assisted Intervention (MICCAI 2026)</i>, Lecture Notes in Computer Science, Springer. In press.',
        [('Code', 'https://github.com/powersimmani/tta-rare-surgical')], hint='both'))
    out.append(related([
        ('Development of a video-based deep learning model for differentiation of malignant and benign lesions during staging laparoscopy: is the machine better than the expert?',
         'ASCO Annual Meeting abstract, <i>Journal of Clinical Oncology</i> 42(16 suppl):e13616, 2024.'),
        ('Machine learning models for classification and morphological assessment of peritoneal lesions during staging laparoscopy.',
         '<i>European Journal of Surgical Oncology</i> 50, 2024.'),
        ('A reference-based approach for tumor size estimation in monocular laparoscopic videos.',
         'International Workshop on Computational Mathematics Modeling in Cancer, Springer, 2024.'),
    ]))
    out.append('</section>\n')

    # ---- Radiology
    rct_body = ('<div class="panels two">'
        + panel('a', img('rct-anatomy', 'Drawings of a normal rotator cuff, a partial-thickness tear and a full-thickness tear', sizes='(min-width: 1160px) 720px, 94vw'))
        + panel('b', SVG('fig-rct-classes.svg'))
        + '</div><div class="panels" style="margin-top:28px">'
        + panel('c', img('rct-camscore', 'Interpretable rotator cuff tear pipeline: axial, coronal and sagittal single-plane models, a fusion model, and CAMscore curves over MRI slices with the matching heat maps'))
        + '</div>')
    out.append('''<section class="theme" id="radiology" aria-labelledby="h-radiology">
  <h2 id="h-radiology">Radiology and screening</h2>
  <p class="intro">In diagnostic imaging I care about what a model looked at and how to measure it. The rotator cuff work began with a shoulder MRI dataset and a diagnostic model, and continued with CAMscore, which ranks MRI slices by how much they contribute to a prediction.</p>
''')
    out.append(plate(3, rct_body,
        'MLHC 2020 and SPIE Medical Imaging 2024', 'First author of the SPIE 2024 paper',
        'Rotator cuff tears in shoulder MRI',
        ['(a) Normal rotator cuff, partial-thickness tear and full-thickness tear.',
         '(b) The shoulder MRI dataset released with the MLHC 2020 paper. Partial-thickness tears are rare, so class imbalance is part of the problem.',
         '(c) Interpretable diagnosis. Models trained on axial, coronal and sagittal series are fused into one prediction. CAMscore then ranks individual slices, and a plane importance analysis shows how much each series contributes.'],
        '(a, b) Kim M, Park H, Kim JY, Kim SH, Hoeke S, De Neve W. <i>Machine Learning for Healthcare Conference</i>, PMLR 126:292&ndash;308, 2020. (c) Park H, Yun I, Kim M, Nguyen KT, Van Messem A, De Neve W. <i>Medical Imaging 2024: Computer-Aided Diagnosis</i>, SPIE 12927:683&ndash;693.',
        [('MLHC paper', 'http://proceedings.mlr.press/v126/kim20a.html'),
         ('Dataset and code', 'https://github.com/powersimmani/MRI-based-Diagnosis-of-Rotator-Cuff-Tears-using-Deep-Learning-and-Weighted-Linear-Combinations')]))
    out.append(related([
        ('Towards improved cervical cancer screening: vision transformer-based classification and interpretability.',
         'IEEE International Symposium on Biomedical Imaging (ISBI), 2025.'),
        (f'<a href="{doi("10.1117/12.2580819")}">Towards a quantitative analysis of class activation mapping for deep learning-based computer-aided diagnosis.</a>',
         'SPIE Medical Imaging 2021: Image Perception, Observer Performance, and Technology Assessment.'),
    ]))
    out.append('</section>\n')

    # ---- Molecules
    out.append('''<section class="theme" id="molecules" aria-labelledby="h-molecules">
  <h2 id="h-molecules">Proteins and CRISPR</h2>
  <p class="intro">On the biology side I use structure prediction and docking to study CRISPR-Cas systems and the anti-CRISPR proteins that phages use to block them. Work with Hyunjin Shim and colleagues produced a public set of predicted anti-CRISPR structures and a docking service for crRNA and Cas protein pairs.</p>
''')
    out.append(plate(4, img('acr-structures', 'Predicted structures of anti-CRISPR proteins 0272 and 0153, each shown alone and superimposed on its experimental structure, 6MCB chain C and 5Y6A chain A'),
        'Pharmaceuticals, 2022', 'First author',
        'AlphaFold structures of anti-CRISPR proteins',
        ['Predicted structures of two anti-CRISPR proteins, Acr 0272 and Acr 0153, each shown alone and superimposed on its experimentally determined structure (PDB 6MCB chain C and 5Y6A chain A). Sequences came from anti-CRISPRdb and were grouped by how well each protein has been verified. The paper uses these structures to discuss how anti-CRISPR proteins could be developed as protein drugs.'],
        'Park HM, Park Y, Vankerschaver J, Van Messem A, De Neve W, Shim H. <i>Pharmaceuticals</i> 15(3):310, 2022.',
        [('Paper', doi('10.3390/ph15030310')), ('Predicted structures', 'https://github.com/powersimmani/ACR_alphafold')]))
    out.append(plate(5, img('crispr-cas-docker', 'CRISPR-Cas-Docker web interface: the query form, the submitted Cas protein and CRISPR RNA structures, and the top docking results table'),
        'BMC Bioinformatics, 2023', 'First author',
        'CRISPR-Cas-Docker, a web service for crRNA and Cas protein docking',
        ['Users submit a crRNA and a Cas protein, either as experimental structures or as predicted ones (a 3D-predicted crRNA and an AlphaFold Cas protein). The service docks each pair with HDOCK, returns the top ten models with their scores, and uses machine learning to classify which crRNA and Cas pairs belong together when a genome carries several CRISPR arrays and Cas systems.'],
        'Park H, Won J, Park Y, Anzaku ET, Vankerschaver J, Van Messem A, De Neve W, Shim H. <i>BMC Bioinformatics</i> 24(1):167, 2023.',
        [('Paper', doi('10.1186/s12859-023-05296-0')), ('Web service', 'https://crisprcasdocker.org')]))
    out.append(plate(6, wide_svg('fig-mutation.svg'),
        'BMC Bioinformatics, 2024', 'Co-author',
        'Which point mutations make useful augmentations for genomic data',
        ['Image models are often trained on flipped or cropped copies of their inputs, but most of those operations change the meaning of a DNA sequence. This study proposed codon substitutions in coding regions instead and tested them on translation initiation and splice site detection. Silent and missense mutations improved performance, while nonsense mutations and random mutations in non-coding regions generally degraded it. The codons shown are illustrative examples.'],
        'Lee H, Ozbulak U, Park H, Depuydt S, De Neve W, Vankerschaver J. <i>BMC Bioinformatics</i> 25(1):170, 2024.',
        [('Paper', doi('10.1186/s12859-024-05787-6')), ('Data and code', 'https://zenodo.org/records/10457890')], hint='scroll'))
    out.append(related([
        (f'<a href="{doi("10.1186/s13062-022-00339-5")}">In silico optimization of RNA-protein interactions for CRISPR-Cas13-based antimicrobials.</a>',
         '<i>Biology Direct</i> 17(1), 2022. First author.'),
    ]))
    out.append('</section>\n')

    # ---- Microscopy
    mp_body = (panel('a', img('mp-pipeline', 'Pipeline from clams to a fluorescence image, a segmentation mask, and particle type and size'))
        + '<div class="panels mp" style="margin-top:28px">'
        + panel('b', img('mp-fluorescence', 'Stitched fluorescence image of a stained sample with many bright particles', sizes='(min-width: 820px) 300px, 94vw', widths=(512,), full='assets/img/mp-fluorescence-512.webp'), 'Fluorescence')
        + panel('', img('mp-brightfield', 'Stitched bright-field image of the same sample', sizes='(min-width: 820px) 300px, 94vw', widths=(512,), full='assets/img/mp-brightfield-512.webp'), 'Bright field, same sample')
        + panel('c', img('mp-annotation-tool', 'Microplastics Annotation Package window with menus for masks, annotation and model training over a fluorescence image', sizes='(min-width: 820px) 380px, 94vw', widths=(700, 1154), full='assets/img/mp-annotation-tool-1154.webp'), 'Microplastics Annotation Package')
        + '</div>')
    out.append('''<section class="theme" id="microscopy" aria-labelledby="h-microscopy">
  <h2 id="h-microscopy">Microscopy</h2>
  <p class="intro">Microplastics in seafood are usually identified by eye under a fluorescence microscope. MP-Net segments the particles automatically, and the annotation tool and image set we built for it are public.</p>
''')
    out.append(plate(7, mp_body,
        'PLoS ONE, 2022', 'First author',
        'MP-Net: segmentation of microplastics isolated from clams',
        ['(a) Particles isolated from clams are stained with Nile red and imaged under fluorescence. MP-Net segments each particle, and the masks give particle type and size.',
         '(b) Stitched fluorescence and bright-field images of the same sample from the public image set.',
         '(c) The annotation tool used to build the segmentation masks.'],
        'Park H, Park S, de Guzman MK, Baek JY, Cirkovic Velickovic T, Van Messem A, De Neve W. <i>PLoS ONE</i> 17(6):e0269449, 2022.',
        [('Paper', doi('10.1371/journal.pone.0269449')),
         ('Annotation tool', 'https://github.com/powersimmani/Microplastics-Annotation-Package'),
         ('Image set', 'https://github.com/powersimmani/nile-red-microplastic-images')]))
    out.append(related([
        ('Developing a segmentation model for microscopic images of microplastics isolated from clams.',
         'ICPR International Workshops and Challenges, LNCS 12666, 2021.'),
    ]))
    out.append('</section>\n')

    # ---- Signals
    out.append('''<section class="theme" id="signals" aria-labelledby="h-signals">
  <h2 id="h-signals">Physiological signals</h2>
  <p class="intro">Stress and emotion models combine video, audio, text and wearable sensor signals, so it is hard to tell what a prediction is based on. Our team took third place in MuSe-Stress 2022 and second place in MuSe-Personalisation 2023, and the journal paper that followed examines the stress models with SHAP values and attention weights.</p>
''')
    out.append(plate(8, img('stress-pipeline', 'Stress detection pipeline: video, audio, text and sensor inputs, two feature extractors, a model predicting arousal and valence, and use cases'),
        'IEEE Transactions on Affective Computing, 2025', 'First author',
        'Which signals drive a stress prediction',
        ['Pipeline for the MuSe-Stress 2022 task. Video, audio, text and physiological sensor signals are turned into features by two extractors, and models predict arousal and valence over time. The journal paper uses SHAP and attention to show which inputs each prediction depends on. Target uses include job interviews, public speaking, consultation and healthcare.'],
        'Park H, Kim G, Oh J, Van Messem A, De Neve W. <i>IEEE Transactions on Affective Computing</i> 15(1):1&ndash;17.',
        [('Paper', doi('10.1109/TAFFC.2024.3488112')), ('Team results', 'https://github.com/powersimmani/MuSe2022FeelsGood')]))
    out.append(related([
        (f'<a href="{doi("10.1145/3551876.3554807")}">Towards multimodal prediction of time-continuous emotion using pose feature engineering and a transformer encoder.</a>',
         'MuSe Workshop and Challenge, ACM Multimedia 2022.'),
        (f'<a href="{doi("10.1145/3606039.3613104")}">MuSe-Personalization 2023: feature engineering, hyperparameter optimization, and transformer-encoder re-discovery.</a>',
         'MuSe Workshop and Challenge, ACM Multimedia 2023. Second place.'),
    ]))
    out.append('</section>\n')

    # ---- Teaching
    out.append(f'''<section class="theme" id="teaching" aria-labelledby="h-teaching">
  <h2 id="h-teaching">Teaching and mentoring</h2>
  <div class="intro">
    <p>In 2021 I started the AI Vacation School at Ghent University Global Campus, an unpaid intensive program for undergraduates that runs in summer and winter. I wrote a 20-lecture curriculum that goes from regression and CNNs to transformers, diffusion models and SHAP, and released the slides and notebooks openly.</p>
    <p>More than thirty students have taken part. Several became co-authors on the papers on this page, and alumni have gone on to graduate programs at KAIST, Seoul National University, UNIST, Ghent University and Scripps Research.</p>
    <p><a href="https://github.com/powersimmani/AIVS">Program repository</a>&nbsp;&nbsp;&nbsp;<a href="https://powersimmani.github.io/AIVS_Lecture_Slides/">Lecture slides</a></p>
  </div>
''')
    out.append(plate(9, img('aivs-posters', 'Four student research posters: Parkinson\'s disease biomarkers, rotator cuff tear diagnosis, heart disease diagnosis and hepatitis C prediction', widths=(1000, 2000)),
        'AI Vacation School, 2021 to 2026', 'Founder and lead instructor',
        'Student research posters',
        ['Research posters by AI Vacation School students on biomarker discovery for Parkinson\'s disease, rotator cuff tear diagnosis from MRI, heart disease diagnosis and hepatitis C prediction.'],
        'Center for Biosystems and Biotech Data Science, Ghent University Global Campus.',
        []))
    out.append('</section>\n')

    # ---- Contact
    out.append(f'''<section class="theme" id="contact" aria-labelledby="h-contact">
  <h2 id="h-contact">Contact</h2>
  <p class="invite">At Texas Children's Hospital I am building a group that pairs engineers with clinicians on pediatric and oncology problems. If you are a clinician with a question your data could answer, or a student who wants to work on one, please write to me.</p>
  <div class="contact">
    <img src="assets/img/profile-480.webp" alt="Portrait of Ho-min Park" width="180" height="216" loading="lazy">
    <dl>
      <dt>Email</dt><dd><a href="{LINKS['email']}">Ho-min.Park@bcm.edu</a></dd>
      <dt>Affiliation</dt><dd>Texas Children's Hospital Data Center, Baylor College of Medicine, Houston, Texas</dd>
      <dt>Code</dt><dd><a href="{LINKS['github']}">github.com/powersimmani</a><br><a href="{LINKS['github_bcm']}">github.com/HominParkBCM</a></dd>
      <dt>Profiles</dt><dd><a href="{LINKS['scholar']}">Google Scholar</a>, <a href="{LINKS['orcid']}">ORCID 0000-0001-9937-8617</a>, <a href="{LINKS['linkedin']}">LinkedIn</a></dd>
      <dt>Training</dt><dd>Postdoctoral researcher, Ghent University Global Campus, 2025 to 2026<br>Ph.D. in Computer Science Engineering, Ghent University, 2025<br>M.S. in Computer Engineering, Ajou University, 2018<br>B.S. in Computer Science and Engineering, Ajou University, 2016</dd>
    </dl>
  </div>
</section>
</div>
</main>
''')
    out.append(FOOT)
    (SITE / 'index.html').write_text(''.join(out))


# ---------------------------------------------------------------- publications
THEMES = [('surgery', 'Surgical video'), ('radiology', 'Radiology and screening'),
          ('molecules', 'Proteins and CRISPR'), ('microscopy', 'Microscopy'),
          ('signals', 'Signals and affect'), ('methods', 'ML methods'),
          ('industrial', 'Industrial systems')]
TN = dict(THEMES)

# (year, authors, title, venue, theme, notes, links)
JOURNALS = [
    (2026, 'Tozzi F, Park HM, Mousavi SA, Van Liefferinge M, Moon D, Fadaei S, et al.',
     'Multimodal machine learning for staging laparoscopy: a combined image analysis and morphologic tool for the discrimination of peritoneal metastasis',
     '<i>International Journal of Surgery</i> 112(1):373&ndash;383', 'surgery', ['Co-first author', 'Fig. 1'],
     [('DOI', doi('10.1097/JS9.0000000000003448'))]),
    (2025, 'Park H, Kim G, Oh J, Van Messem A, De Neve W',
     'Interpreting stress detection models using SHAP and attention for MuSe-Stress 2022',
     '<i>IEEE Transactions on Affective Computing</i> 15(1):1&ndash;17', 'signals', ['First author', 'Fig. 8'],
     [('DOI', doi('10.1109/TAFFC.2024.3488112'))]),
    (2024, 'Lee H, Ozbulak U, Park H, Depuydt S, De Neve W, Vankerschaver J',
     'Assessing the reliability of point mutation as data augmentation for deep learning with genomic data',
     '<i>BMC Bioinformatics</i> 25(1):170', 'molecules', ['Fig. 6'],
     [('DOI', doi('10.1186/s12859-024-05787-6')), ('Data and code', 'https://zenodo.org/records/10457890')]),
    (2023, 'Ozbulak U, Lee HJ, Boga B, Anzaku ET, Park H, Van Messem A, et al.',
     'Know your self-supervised learning: a survey on image-based generative and discriminative training',
     '<i>Transactions on Machine Learning Research</i>', 'methods', [], []),
    (2023, 'Park H, Won J, Park Y, Anzaku ET, Vankerschaver J, Van Messem A, De Neve W, Shim H',
     'CRISPR-Cas-Docker: web-based in silico docking and machine learning-based classification of crRNAs with Cas proteins',
     '<i>BMC Bioinformatics</i> 24(1):167', 'molecules', ['First author', 'Fig. 5'],
     [('DOI', doi('10.1186/s12859-023-05296-0')), ('Web service', 'https://crisprcasdocker.org')]),
    (2022, 'Park H, Park Y, Berani U, Bang E, Vankerschaver J, Van Messem A, De Neve W, Shim H',
     'In silico optimization of RNA-protein interactions for CRISPR-Cas13-based antimicrobials',
     '<i>Biology Direct</i> 17(1)', 'molecules', ['First author'],
     [('DOI', doi('10.1186/s13062-022-00339-5'))]),
    (2022, 'Park HM, Park Y, Vankerschaver J, Van Messem A, De Neve W, Shim H',
     'Rethinking protein drug design with highly accurate structure prediction of anti-CRISPR proteins',
     '<i>Pharmaceuticals</i> 15(3):310', 'molecules', ['First author', 'Fig. 4'],
     [('DOI', doi('10.3390/ph15030310')), ('Structures', 'https://github.com/powersimmani/ACR_alphafold')]),
    (2022, 'Park H, Park S, de Guzman MK, Baek JY, Cirkovic Velickovic T, Van Messem A, De Neve W',
     'MP-Net: deep learning-based segmentation for fluorescence microscopy images of microplastics isolated from clams',
     '<i>PLoS ONE</i> 17(6):e0269449', 'microscopy', ['First author', 'Fig. 7'],
     [('DOI', doi('10.1371/journal.pone.0269449'))]),
]

PROCEEDINGS = [
    (2026, 'Park HM, Tozzi F, De Muynck R, Kim N, Rashidian N, Willaert W, De Neve W, Vankerschaver J',
     'Test-time adaptation for rare surgical phase recognition: bridging the coverage-gap paradox',
     '<i>MICCAI 2026</i>, Lecture Notes in Computer Science, Springer. In press', 'surgery',
     ['First and corresponding author', 'Fig. 2'], [('Code', 'https://github.com/powersimmani/tta-rare-surgical')]),
    (2025, 'Nguyen KT, Park H, Oh G, Vankerschaver J, De Neve W',
     'Towards improved cervical cancer screening: vision transformer-based classification and interpretability',
     '<i>IEEE 22nd International Symposium on Biomedical Imaging (ISBI)</i>, 1&ndash;5', 'radiology', [], []),
    (2025, 'Singh AK, Kim G, Kim J, Park H, Choi BJ, De Neve W',
     'RAMM: a residual attention multimodal model for humor detection',
     '<i>International Conference on Intelligent Human Computer Interaction</i>, 229&ndash;240', 'signals', [], []),
    (2024, 'Mousavi SA, Tozzi F, Park H, Anzaku ET, Van Liefferinge M, Rashidian N, et al.',
     'A reference-based approach for tumor size estimation in monocular laparoscopic videos',
     '<i>International Workshop on Computational Mathematics Modeling in Cancer</i>, Springer', 'surgery', [], []),
    (2024, 'Park H, Yun I, Kim M, Nguyen KT, Van Messem A, De Neve W',
     'Interpretable rotator cuff tear diagnosis using MRI slides with CAMscore and SHAP',
     '<i>Medical Imaging 2024: Computer-Aided Diagnosis</i>, SPIE 12927:683&ndash;693', 'radiology', ['First author', 'Fig. 3'], []),
    (2024, 'Singh AK, Kim G, Kim J, Park H, Choi BJ, De Neve W',
     'Exploring multimodal approaches and fusion methods for CEO social attribute prediction in 2024 MuSe-Perception',
     '<i>Proceedings of the 5th Multimodal Sentiment Analysis Challenge and Workshop</i>, ACM, 36&ndash;44', 'signals', [],
     [('DOI', doi('10.1145/3689062.3689081'))]),
    (2023, 'Park HM, Kim G, Van Messem A, De Neve W',
     'MuSe-Personalization 2023: feature engineering, hyperparameter optimization, and transformer-encoder re-discovery',
     '<i>Proceedings of the 4th Multimodal Sentiment Analysis Challenge and Workshop</i>, ACM, 89&ndash;97', 'signals',
     ['First author', 'Second place, MuSe-Personalisation'], [('DOI', doi('10.1145/3606039.3613104'))]),
    (2022, 'Park H, Yun I, Kumar A, Singh AK, Choi BJ, Singh D, De Neve W',
     'Towards multimodal prediction of time-continuous emotion using pose feature engineering and a transformer encoder',
     '<i>Proceedings of the 3rd International Multimodal Sentiment Analysis Workshop and Challenge</i>, 47&ndash;54', 'signals',
     ['First author', 'Third place, MuSe-Stress'], [('DOI', doi('10.1145/3551876.3554807'))]),
    (2021, 'Kang H, Park H, Ahn Y, Van Messem A, De Neve W',
     'Towards a quantitative analysis of class activation mapping for deep learning-based computer-aided diagnosis',
     '<i>Medical Imaging 2021: Image Perception, Observer Performance, and Technology Assessment</i>, SPIE 11599', 'radiology', [],
     [('DOI', doi('10.1117/12.2580819'))]),
    (2021, 'Park H, Kang B, Van Messem A, De Neve W',
     '3-D deep learning-based item classification for belt conveyors targeting packaging and logistics',
     '<i>Pattern Recognition, ICPR International Workshops and Challenges</i>, LNCS 12666:578&ndash;591', 'industrial', ['First author'],
     [('DOI', doi('10.1007/978-3-030-68799-1_42'))]),
    (2021, 'Baek JY, de Guzman MK, Park H, Park S, Shin B, Cirkovic Velickovic T, Van Messem A, De Neve W',
     'Developing a segmentation model for microscopic images of microplastics isolated from clams',
     '<i>Pattern Recognition, ICPR International Workshops and Challenges</i>, LNCS 12666:86&ndash;97', 'microscopy', [], []),
    (2020, 'Kim M, Park H, Kim JY, Kim SH, Hoeke S, De Neve W',
     'MRI-based diagnosis of rotator cuff tears using deep learning and weighted linear combinations',
     '<i>Machine Learning for Healthcare Conference (MLHC)</i>, PMLR 126:292&ndash;308', 'radiology', ['Fig. 3'],
     [('Paper', 'http://proceedings.mlr.press/v126/kim20a.html'),
      ('Dataset', 'https://github.com/powersimmani/MRI-based-Diagnosis-of-Rotator-Cuff-Tears-using-Deep-Learning-and-Weighted-Linear-Combinations')]),
    (2020, 'Park H, Van Messem A, De Neve W',
     'Item measurement for logistics-oriented belt conveyor systems using a scenario-driven approach and automata-based control design',
     '<i>IEEE 7th International Conference on Industrial Engineering and Applications (ICIEA)</i>', 'industrial', ['First author'], []),
    (2019, 'Park HM, Van Messem A, De Neve W',
     'Box-Scan: an efficient and effective algorithm for box dimension measurement in conveyor systems using a single RGB-D camera',
     '<i>7th IIAE International Conference on Industrial Application Engineering</i>, Kitakyushu', 'industrial',
     ['First author', 'Best Presentation Award'], []),
]

ABSTRACTS = [
    (2024, 'Tozzi F, Mousavi SA, Van Liefferinge M, Moon D, Park H, Fadaei S, et al.',
     'Development of a video-based deep learning model for differentiation of malignant and benign lesions during staging laparoscopy: is the machine better than the expert?',
     '<i>Journal of Clinical Oncology</i> 42(16 suppl):e13616, ASCO Annual Meeting', 'surgery', [], []),
    (2024, 'Tozzi F, Park HM, Moon D, Mousavi SA, Van Liefferinge M, Fadaei S, et al.',
     'Machine learning models for classification and morphological assessment of peritoneal lesions during staging laparoscopy',
     '<i>European Journal of Surgical Oncology</i> 50', 'surgery', [], []),
]

PATENTS = [
    (2021, 'Park HM, De Neve W',
     'Apparatus and method for measuring the size of high-speed objects and classifying their type on conveyors using light curtain sensors',
     'Korean Intellectual Property Office, registration 10-2273758', 'industrial', [], []),
    (2020, 'Park HM, De Neve W',
     'Apparatus and method for measuring the size of high-speed boxes on conveyors using an RGB-D camera',
     'Korean Intellectual Property Office, registration 10-2066862', 'industrial', [], []),
]


def bold_me(a):
    return re.sub(r'\bPark H(M)?\b', lambda m: f'<b>{m.group(0)}</b>', a)


def pub_li(p):
    year, authors, title, venue, theme, notes, links = p
    x = [f'<span class="tag">{TN[theme]}</span>'] + [html.escape(n) if not n.startswith('Fig.') else
         f'<a href="index.html#fig{n.split()[-1]}">{n}</a>' for n in notes] + [f'<a href="{u}">{t}</a>' for t, u in links]
    return (f'<li data-theme="{theme}"><span class="yr">{year}</span><div>'
            f'<p class="t">{title}</p><p class="a">{bold_me(authors)}</p><p class="v">{venue}</p>'
            f'<p class="x">{"".join(f"<span>{i}</span>" for i in x)}</p></div></li>')


def build_pubs():
    out = [head('Publications, Ho-min Park',
                'Journal papers, conference proceedings, abstracts and patents by Ho-min Park.',
                'publications.html'),
           header('Publications')]
    chips = ['<button type="button" data-filter="all" aria-pressed="true">All</button>'] + [
        f'<button type="button" data-filter="{k}" aria-pressed="false">{v}</button>' for k, v in THEMES]
    out.append(f'''<main id="main">
<div class="wrap">
<section class="page-head">
  <h1>Publications</h1>
  <p>329 citations and an h-index of 11 on <a href="{LINKS['scholar']}">Google Scholar</a> as of August 2026. My name is in bold. All papers listed here come from work done before Baylor College of Medicine.</p>
  <fieldset class="filters">
    <legend>Show papers by topic</legend>
    {''.join(chips)}
  </fieldset>
  <p id="filter-status" class="visually-hidden" aria-live="polite"></p>
</section>
''')
    for gid, name, rows, note in [
        ('journals', 'Journal articles', JOURNALS, ''),
        ('proceedings', 'Conference proceedings', PROCEEDINGS, 'Full papers in peer-reviewed proceedings, which are archival publications in computer science.'),
        ('abstracts', 'Meeting abstracts', ABSTRACTS, ''),
        ('patents', 'Patents', PATENTS, 'Both patents came out of the MOTIE smart packaging project, 2018 to 2021.'),
    ]:
        n = f'<p class="note">{note}</p>' if note else ''
        out.append(f'<section class="pub-group" id="{gid}" aria-labelledby="h-{gid}"><h2 id="h-{gid}">{name}</h2>{n}'
                   f'<ol class="pubs">{"".join(pub_li(p) for p in rows)}</ol></section>\n')
    out.append('</div>\n</main>\n')
    out.append(FOOT)
    (SITE / 'publications.html').write_text(''.join(out))


if __name__ == '__main__':
    build_index()
    build_pubs()
    print('built')
