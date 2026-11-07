const status = document.getElementById('status');
const files = document.getElementById('files');
const player = document.getElementById('player');

fetch('/api/audio')
    .then(response => {
    if (!response.ok) throw new Error('can not load audio files');
    return response.json();
    })
    .then(names => {
    status.textContent = names.length ? '' : 'No MP3 files found.';
    for (const name of names) {
        const item = document.createElement('li');

        // append play file
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = name;
        button.addEventListener('click', () => {
        player.src = '/api/audio/' + encodeURIComponent(name);
        player.hidden = false;
        player.play();
        });
        item.append(button);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.textContent = 'X';
        removeButton.setAttribute('aria-label', `Delete ${name}`);
        removeButton.className = 'remove-button';
        removeButton.addEventListener('click', async () => {
            if (!window.confirm(`Permanently delete ${name}?`)) return;
            removeButton.disabled = true;
            try {
                const response = await fetch('/api/audio/' + encodeURIComponent(name), { method: 'DELETE' });
                if (!response.ok) throw new Error(`Could not delete ${name}.`);
                if (player.src === new URL('/api/audio/' + encodeURIComponent(name), location.href).href) {
                    player.pause();
                    player.removeAttribute('src');
                    player.load();
                    player.hidden = true;
                }
                item.remove();
                if (!files.children.length) status.textContent = 'No MP3 files found.';
            } catch (error) {
                status.textContent = error.message;
                removeButton.disabled = false;
            }
        });
        item.append(removeButton);

        files.append(item);
    }
    })
    .catch(error => { status.textContent = error.message; });
