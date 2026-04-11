import re

for filepath in [
    '/home/ubuntu/filtrbox/templates/dashboard.html',
    '/home/ubuntu/filtrbox/templates/client.html'
]:
    with open(filepath, 'r') as f:
        content = f.read()

    old = '''if (currentStatus.prog?.heure_debut) document.getElementById("start-time").value = currentStatus.prog.heure_debut;
            if (currentStatus.prog?.heure_fin)   document.getElementById("end-time").value   = currentStatus.prog.heure_fin;'''

    new = '''if (currentStatus.prog?.heure_debut && document.activeElement.id !== "start-time") document.getElementById("start-time").value = currentStatus.prog.heure_debut;
            if (currentStatus.prog?.heure_fin   && document.activeElement.id !== "end-time")   document.getElementById("end-time").value   = currentStatus.prog.heure_fin;'''

    old2 = '''if (currentStatus.cycle?.heure)       document.getElementById("cycle-time").value         = currentStatus.cycle.heure;
            if (currentStatus.cycle?.lavage_min  !== undefined) document.getElementById("wash-min").textContent  = currentStatus.cycle.lavage_min;
            if (currentStatus.cycle?.lavage_sec  !== undefined) document.getElementById("wash-sec").textContent  = currentStatus.cycle.lavage_sec;
            if (currentStatus.cycle?.rincage_sec !== undefined) document.getElementById("rinse-sec").textContent = currentStatus.cycle.rincage_sec;'''

    new2 = '''if (currentStatus.cycle?.heure && document.activeElement.id !== "cycle-time") document.getElementById("cycle-time").value = currentStatus.cycle.heure;
            if (currentStatus.cycle?.lavage_min  !== undefined && document.activeElement.id !== "wash-min")  document.getElementById("wash-min").textContent  = currentStatus.cycle.lavage_min;
            if (currentStatus.cycle?.lavage_sec  !== undefined && document.activeElement.id !== "wash-sec")  document.getElementById("wash-sec").textContent  = currentStatus.cycle.lavage_sec;
            if (currentStatus.cycle?.rincage_sec !== undefined && document.activeElement.id !== "rinse-sec") document.getElementById("rinse-sec").textContent  = currentStatus.cycle.rincage_sec;'''

    ok = 0
    if old in content:
        content = content.replace(old, new)
        ok += 1
    if old2 in content:
        content = content.replace(old2, new2)
        ok += 1

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"OK - {filepath.split('/')[-1]} : {ok}/2 corrections")
