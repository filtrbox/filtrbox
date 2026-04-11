with open('/home/leoer/ProgPI/FILTRBOX_2/web_server.py', 'r') as f:
    content = f.read()

old = '''def check_programmation():
    while True:
        if state.prog_active:'''

new = '''def check_programmation():
    while True:
        if state.prog_active and not state.cycle_en_cours:'''

if old in content:
    content = content.replace(old, new)
    with open('/home/leoer/ProgPI/FILTRBOX_2/web_server.py', 'w') as f:
        f.write(content)
    print("OK - corrige")
else:
    print("ERREUR - texte non trouve")
