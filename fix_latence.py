for filepath in [
    '/home/ubuntu/filtrbox/templates/dashboard.html',
    '/home/ubuntu/filtrbox/templates/client.html'
]:
    with open(filepath, 'r') as f:
        content = f.read()

    # Ajouter le CSS pour feedback visuel
    old_css = '.btn:active { transform: scale(0.95); }'
    new_css = '''.btn:active { transform: scale(0.95); }
        .btn-sending { opacity: 0.6; transform: scale(0.97); transition: all .1s; }
        .btn-success { border-color: #00FF94 !important; background: rgba(0,255,148,0.3) !important; transition: all .2s; }
        .btn-error   { border-color: #FF4444 !important; background: rgba(255,68,68,0.3) !important; transition: all .2s; }'''

    # Remplacer setMode pour feedback immédiat
    old_mode = '''async function setMode(mode)    { if(navigator.vibrate)navigator.vibrate(20); await sendCommand("mode", mode); }'''
    new_mode = '''async function setMode(mode) {
            if(navigator.vibrate) navigator.vibrate(20);
            const btnId = "mode-" + mode.toLowerCase()
                .replace("filtration","filtration")
                .replace("lavage","lavage")
                .replace("rinçage","rincage")
                .replace("recirculation","recirculation")
                .replace("vidange","vidange")
                .replace("hivernage","hivernage")
                .replace("arrêt","arret");
            const btn = document.getElementById(btnId);
            if (btn) {
                btn.classList.add("btn-sending");
                btn.textContent = "⏳ " + btn.textContent.substring(3);
            }
            try {
                await sendCommand("mode", mode);
                if (btn) {
                    btn.classList.remove("btn-sending");
                    btn.classList.add("btn-success");
                    setTimeout(() => btn.classList.remove("btn-success"), 1500);
                }
            } catch(e) {
                if (btn) {
                    btn.classList.remove("btn-sending");
                    btn.classList.add("btn-error");
                    setTimeout(() => btn.classList.remove("btn-error"), 1500);
                }
            }
        }'''

    ok = 0
    if old_css in content:
        content = content.replace(old_css, new_css); ok += 1
    if old_mode in content:
        content = content.replace(old_mode, new_mode); ok += 1

    with open(filepath, 'w') as f:
        f.write(content)
    print(f"OK - {filepath.split('/')[-1]} : {ok}/2 corrections")
