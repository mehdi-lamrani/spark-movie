var host = "http://localhost:5432/"

function addRating() {
    console.log("Get random movie to rate...");

    var xmlhttp = new XMLHttpRequest();
    var url = host + "movies";

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var movie = this.response[0];

                var tableBody = document.getElementById("ratings-table-body");

                var index = tableBody.getElementsByTagName('tr').length;
                var row = tableBody.insertRow(index);
                row.setAttribute("id", index);
            
                var cell1 = row.insertCell(0);
                var cell2 = row.insertCell(1);
            
                var titleInput = document.createElement("input");
                titleInput.setAttribute("type", "text");
                titleInput.setAttribute("class", "form-control");
                titleInput.setAttribute("placeholder", "Movie Identifier");
                titleInput.setAttribute("name", "title_" + index);
                titleInput.setAttribute("value", movie.title);
            
                var idInput = document.createElement("input");
                idInput.setAttribute("type", "hidden");
                idInput.setAttribute("name", "movieId_" + index);
                idInput.setAttribute("value", movie.movieId);

                var select = document.createElement("select");
                select.setAttribute("class", "form-control")
                select.setAttribute("name", "rating_" + index);
            
                var i;
                for (i = 1; i <= 5; i++) {
                    var option = document.createElement("option");
                    option.setAttribute("value", i);
                    var node = document.createTextNode(i);
                    option.appendChild(node);
                    select.appendChild(option);
                }
            
                cell1.appendChild(titleInput);
                cell1.appendChild(idInput);
                cell2.appendChild(select);
            }
        }
    };

    xmlhttp.open("GET", url, true);
    xmlhttp.responseType = 'json';
    xmlhttp.send();
}

function addMovieRecommendation(value, index, array) {
    var table = document.getElementById("movies-table");
    var tableBody = document.getElementById("movies-table-body");
    var row = tableBody.insertRow(index);

    var cell1 = row.insertCell(0);
    var cell2 = row.insertCell(1);

    cell1.innerHTML = index + 1;
    cell2.innerHTML = value.title;
}

function isValidForm(firstParam, secondParam) {
    if (firstParam === "" || isNaN(firstParam)) {
        return false;
    }
    if (secondParam === "" || isNaN(secondParam)) {
        return false;
    }
    return true;
}

function submitRatings(userId) {
    console.log("Add new ratings to the model for user " + userId);

    if (userId.trim() === "" || !isNaN(userId)) {
        var url = host + "newratings";
        if (userId.trim() !== "") {
            url = host + "newratings/" + userId.trim();
        }

        document.getElementById("add-ratings-btn").disabled = true;
        document.getElementById("add-rating-line-btn").disabled = true;
        
        var ratingsForm = document.getElementById("ratings-form");
        var data = new FormData(ratingsForm);

        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var tableBody = document.getElementById("ratings-table-body");
                    while (tableBody.hasChildNodes()) {
                        tableBody.removeChild(tableBody.firstChild);
                    }
                    if (this.responseText) {
                    alert("Model trained successfully with new ratings.\nNew user created with identifier : " + this.responseText);
                    } else {
                        alert("Model trained successfully with new ratings.");
                    }
                    addRating();
                }

                if (this.status == 500) {
                    alert(this.response.substring(this.response.indexOf("<p>") + 3, this.response.indexOf("</p>")))
                }

                document.getElementById("add-ratings-btn").disabled = false;
                document.getElementById("add-rating-line-btn").disabled = false;
            }
        };

        xhr.open("POST", url, true);
        xhr.send(data);
    } else {
        alert("User identifier must be numerical or empty to create new User.");
    }
}

function predictRating(userId, movieId) {
    if (isValidForm(userId, movieId)) {
        console.log("Predict rating for movie " + movieId + " and user " + userId);
        
        document.getElementById("get-prediction-btn").disabled = true;
        document.getElementById("predited-rating-result").innerHTML = "Processing...";

        var xmlhttp = new XMLHttpRequest();
        var url = host + userId + "/ratings/" + movieId;

        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var rating = parseFloat(this.response).toFixed(2);
                    var message = "The prediction failed, movie not found for the given identifier."
                    if (rating != -1) {
                        message = "Predicted rating for movie <br>" + document.getElementById('movieTitlePredictInput').value 
                            + " <br>and user " + userId + " is :<br>" + rating;
                    }
                    document.getElementById("predited-rating-result").innerHTML = message;
                }

                document.getElementById("get-prediction-btn").disabled = false;
            }
        };

        xmlhttp.open("GET", url, true);
        xmlhttp.responseType = 'json';
        xmlhttp.send();
    } else {
        alert("User Identifier and Movie Identifier must be numerical values.");
    }
}

function getRecommendations(userId, nbMovies) {
    if (isValidForm(userId, nbMovies) && nbMovies > 0) {
        console.log("Get top " + nbMovies + " movies for user " + userId);
        document.getElementById("get-recommendations-btn").disabled = true;

        var xmlhttp = new XMLHttpRequest();
        var url = host + userId + "/ratings/top/" + nbMovies;

        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var tableBody = document.getElementById("movies-table-body");
                    while (tableBody.hasChildNodes()) {
                        tableBody.removeChild(tableBody.firstChild);
                    }

                    var result = this.response;
                    result.forEach(addMovieRecommendation);
                }

                document.getElementById("get-recommendations-btn").disabled = false;
            }
        };

        xmlhttp.open("GET", url, true);
        xmlhttp.responseType = 'json';
        xmlhttp.send();
    } else {
        alert("User Identifier and Number of movies must be numerical values.");
    }
}

function getMovie(movieId) {
    if (movieId === "" || isNaN(movieId)) {
        console.log("Movie Identifier is null.");
    } else {
        var xmlhttp = new XMLHttpRequest();
        var url = host + "movies/" + movieId;

        xmlhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    var input = document.getElementById('movieTitlePredictInput');
                    if (this.response == undefined || this.response.length == 0) {
                        input.value = "Movie not found";
                    } else {
                        input.value = this.response[0].title;
                    }
                }
            }
        };

        xmlhttp.open("GET", url, true);
        xmlhttp.responseType = 'json';
        xmlhttp.send();
    }
}