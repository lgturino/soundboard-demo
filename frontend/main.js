const status = document.getElementById('status');
const files = document.getElementById('files');
const player = document.getElementById('player');

const randomForm = document.getElementById('getrand');
const audioList = document.getElementById('audiolist');

function updateSounds(names) {
    for (const name of names) {

        const box = document.createElement('div');
        box.className = "sound_box";

        const player = document.createElement('audio');
        player.src = "/api/audio/" + encodeURIComponent(name);
        player.controls = true;

        const title = document.createElement('p');
        title.textContent = name;

        // const story = document.createElement('textarea');

        box.append(player);
        box.append(title);
        // box.append(story);

        audioList.append(box);

    }
}

randomForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const response = await fetch('/api/rand', {
        method: 'POST',
        body: new FormData(randomForm),
    });

    if (!response.ok) {
        status.textContent = 'could not get random sounds';
        return;
    }

    const names = await response.json();
    audioList.replaceChildren();

    updateSounds(names);

})

fetch('/api/selected')
    .then(response => {
        if (!response.ok) throw new Error('cannot get current selected');
        return response.json();
    })
    .then(names => {
        updateSounds(names);
    });

const uploadForm = document.getElementById('upload');

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const response = await fetch('/api/audio', {
        method: 'POST',
        body: new FormData(uploadForm),
    });

    if (!response.ok) {
        const error = await response.json();
        status.textContent = error.detail || 'upload failed';
        return;
    }

    uploadForm.reset();
    location.reload();
})

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

        // remove file
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
