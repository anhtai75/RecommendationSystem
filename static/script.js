document.getElementById("get-recommendations").addEventListener("click", function() {
    let userId = document.getElementById("user-id").value;
    let resultDiv = document.getElementById("recommendations");

    fetch(`/recommend?user_id=${userId}`)
    .then(response => response.json())
    .then(data => {
        resultDiv.innerHTML = "<h3>Gợi ý phim:</h3>";
        if (data.recommendations.length > 0) {
            data.recommendations.forEach(movie => {
                let movieName = encodeURIComponent(movie.title);
                let searchUrl = `https://www.google.com/search?q=${movieName} movie`;

                resultDiv.innerHTML += `<p>🎬 <a href="${searchUrl}" target="_blank">${movie.title}</a></p>`;
            });
        } else {
            resultDiv.innerHTML += "<p>No recommendations available.</p>";
        }
    })
    .catch(error => {
        console.error("Error fetching recommendations:", error);
        resultDiv.innerHTML = "<p style='color: red;'>Error fetching recommendations. Check console.</p>";
    });
});