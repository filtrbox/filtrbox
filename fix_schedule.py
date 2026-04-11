for filepath in [
    '/home/ubuntu/filtrbox/templates/dashboard.html',
    '/home/ubuntu/filtrbox/templates/client.html'
]:
    with open(filepath, 'r') as f:
        content = f.read()

    new_functions = '''async function toggleSchedule() {
            if(navigator.vibrate)navigator.vibrate(20);
            const newActive = !document.getElementById("schedule-toggle").classList.contains("active");
            document.getElementById("schedule-toggle").classList.toggle("active", newActive);
            await sendCommand("programmation", {
                active: newActive,
                heure_debut: document.getElementById("start-time").value || currentStatus.prog?.heure_debut,
                heure_fin: document.getElementById("end-time").value || currentStatus.prog?.heure_fin
            });
        }
        async function saveSchedule() {
            if(navigator.vibrate)navigator.vibrate([30,50,30]);
            const active = document.getElementById("schedule-toggle").classList.contains("active");
            await sendCommand("programmation", {
                active: active,
                heure_debut: document.getElementById("start-time").value,
                heure_fin: document.getElementById("end-time").value
            });
            alert("Schedule saved!");
        }'''

    import re
    content = re.sub(
        r'async function toggleSchedule\(\).*?alert\("Schedule saved!"\);\s*\}',
        new_functions,
        content,
        flags=re.DOTALL
    )

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"OK - {filepath.split('/')[-1]} corrige")
