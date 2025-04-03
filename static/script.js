let currentPage = 1;
const songsPerPage = 5;
let totalPages = 1;

// Check authentication state on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    fetchAndPlotSpotifyData();
});

// Login functionality
document.getElementById('login-button').addEventListener('click', async () => {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!username || !password) {
        alert("Please enter valid credentials.");
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const result = await response.json();

        if (response.ok) {
            localStorage.setItem('authToken', result.token);
            localStorage.setItem('username', username);
            alert(result.message);
            updateAuthUI();
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("An error occurred. Please try again.");
    }
});

// Logout functionality
document.getElementById('logout-button').addEventListener('click', () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    updateAuthUI();
});

// Check authentication and update UI
function checkAuth() {
    const authToken = localStorage.getItem('authToken');
    if (authToken) {
        updateAuthUI();
    }
}

// Update UI based on authentication state
// Update UI based on authentication state
function updateAuthUI() {
    const username = localStorage.getItem('username');

    if (username) {
        document.getElementById('user-name').textContent = username;
        document.getElementById('login-form').style.display = 'none';
        document.getElementById('user-info').style.display = 'block';
    } else {
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('user-info').style.display = 'none';

        // Clear the input fields when logging out
        document.getElementById('username').value = "";
        document.getElementById('password').value = "";
    }
}


// Fetch all songs from the backend
document.getElementById('fetch-songs-button').addEventListener('click', async () => {
    try {
        const response = await fetch(`/songs?page=${currentPage}&per_page=${songsPerPage}`);
        const data = await response.json();
        renderSongs(data.songs);
        renderPagination(data.current_page, data.pages);
        renderChart(data.songs);
    } catch (error) {
        console.error("Error fetching songs:", error);
    }
});

// Render songs with pagination
function renderSongs(songs) {
    const songsContainer = document.getElementById('songs-container');
    songsContainer.innerHTML = songs
        .map(song => `<li class="song-item">${song.song_name} (Plays: ${song.plays})</li>`)
        .join('');
}

// Export songs to CSV
document.getElementById('export-csv-button').addEventListener('click', () => {
    window.location.href = '/export_csv';
});

// Render pagination controls
function renderPagination(current, total) {
    currentPage = current;
    totalPages = total;
    document.getElementById('prev-button').disabled = currentPage <= 1;
    document.getElementById('next-button').disabled = currentPage >= totalPages;
}

// Pagination buttons
document.getElementById('prev-button').addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        document.getElementById('fetch-songs-button').click();
    }
});

document.getElementById('next-button').addEventListener('click', () => {
    if (currentPage < totalPages) {
        currentPage++;
        document.getElementById('fetch-songs-button').click();
    }
});

// Fetch data from the backend endpoint
function fetchAndPlotSpotifyData() {
    fetch("/spotify/visuals")
        .then(response => response.json())
        .then(data => {
            const rawDataDiv = document.getElementById("raw-data");
            rawDataDiv.textContent = JSON.stringify(data, null, 2);

            const songs = data.most_played_songs;
            const artists = data.top_artists;

            if (songs.length > 0) {
                const songNames = songs.map(song => song.song);
                const songPlays = songs.map(song => song.plays);

                Plotly.newPlot("most-played", [{
                    x: songNames,
                    y: songPlays,
                    type: "bar"
                }], {
                    title: "Most Played Songs",
                    xaxis: { title: "Song" },
                    yaxis: { title: "Plays" }
                });
            }

            if (artists.length > 0) {
                const artistNames = [...new Set(artists.map(a => a.artist))];
                const artistPlays = artistNames.map(artist =>
                    artists
                        .filter(a => a.artist === artist)
                        .reduce((sum, a) => sum + a.plays, 0)
                );

                Plotly.newPlot("top-artists", [{
                    labels: artistNames,
                    values: artistPlays,
                    type: "pie"
                }], {
                    title: "Top Artists"
                });
            }
        })
        .catch(error => console.error("Error fetching data:", error));
}

   
// Render chart for the most popular songs
function renderChart(songs) {
    const ctx = document.getElementById('songs-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: songs.map(song => song.song_name),
            datasets: [{
                label: 'Plays',
                data: songs.map(song => song.plays),
                backgroundColor: 'rgba(0, 123, 255, 0.5)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 1,
            }]
        },
        options: {
            scales: {
                y: { beginAtZero: true },
            },
        },
    });
}
