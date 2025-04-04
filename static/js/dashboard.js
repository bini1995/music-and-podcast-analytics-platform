fetch("/spotify/visuals")
  .then((res) => res.json())
  .then((data) => {
    Plotly.newPlot("most-played", JSON.parse(data.most_played_songs));
    Plotly.newPlot("top-artists", JSON.parse(data.top_artists));
  })
  .catch((err) => console.error("Error loading dashboard data:", err));
