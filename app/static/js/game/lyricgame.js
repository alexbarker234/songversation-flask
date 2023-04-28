let currentPlaylist = null;

let playlistCache = {};
let availableTrackIDs = [];

let loadedTracks = new Map();
/** List of all trackIDs with lyrics */
let loadedLyrics = [];

/** @type Track */
let currentTrack = null;

let rounds = 5;
let roundsLeft = rounds;
let score = 0;

let autocompleteSelected = -1;
let optionCount = 0;

const keyUp = 38,
    keyDown = 40,
    keyEnter = 13;

/* 
    TODO: 
    - ensure only songs with lyrics can get selected
    - ensure playlists have songs on spotify 
    - remove local tracks
    - remove punctuation from autocomplete search
    - try and avoid putting the song title in the lyrics??
    - remove whole lyric lines like "ooh-ooh" and "yeah"
    - keyboard support - arrowkey autocomplete, enter to submit
    - some lyric links return 404 - make sure thats fixed
    - make the autocomplete include artist names 
*/

$(window).on("load", function () {
    if (window.location.pathname.includes("/playlist/")) {
        playlist_id = window.location.pathname.split("/").pop(); // get the last part in the path

        getPlaylist(playlist_id).then((response) => {
            if (response.error === true) {
                displayError(response.message);
            } else {
                loadGameWithPlaylist(response);
            }
        });

        $(document).on("click", ".autocomplete-options li", function (e) {
            selectAutocomplete(e.target.innerHTML);
        });

        // close autocomplete menu
        $(document).on("click", ".autocomplete-options", function (e) {
            e.stopPropagation();
        }); // dont close when clicking this
        $(document).on("click", function (e) {
            setAutocompleteVisibility(
                e.target.id == "guess-input" && e.target.value != ""
            );
        });

        $(document).on("keyup", "#guess-input", manageAutocomplete);

        $(document).on("keydown", autocompleteKeyboard);
    }
});

function displayError(message) {
    let game = $("#lyric-game");
    game.empty();
    game.append($("<h1>", { html: message }));
    game.append($("<a>", { html: "Back", href: "/" }));

    $("#loader-container").remove();
}

function getPlaylist(playlistID) {
    return $.getJSON(`/getplaylist/${playlistID}`);
}

function getPlaylistTracks(playlistID) {
    return $.getJSON(`/getplaylisttracks/${playlistID}`);
}

function loadGameWithPlaylist(playlist) {
    loadedTracks = playlist.tracks.reduce(function (map, obj) {
        map[obj.id] = obj;
        return map;
    }, {});
    availableTrackIDs = playlist.tracks.map(function (obj) {
        return obj.id;
    });
    availableTrackIDs = availableTrackIDs.filter((n) => n).shuffle(); // remove null track ids (local files) and shuffle

    // playlist icon
    selectedPlaylist = createCoverArtBox(playlist);
    selectedPlaylist.css("animation", "fade-in 1s");
    selectedPlaylist.addClass("selected-playlist");
    $("#selected-cover-art").append(selectedPlaylist);

    // register autocomplete options
    const trackList = $("#track-list");
    playlist.tracks.forEach(function (track) {
        trackList.append($("<li>", { html: `${trackListDisplay(track)}` }));
    });

    $("#score-text").html(`0 / ${rounds}`);

    loadLyrics(5, [...availableTrackIDs], true);
}

function finishScreen() {
    /*
        TODO:
        - replay with same playlist
        - back to playlists
    */
    const winScreen = $("<div>", { id: "win-screen" });

    winScreen.append($("<p>", { id: "test", html: "you win" }));

    $("#lyric-game").append(winScreen);

    // remove rest of content after
    setTimeout(function () {
        $("#lyric-game").children("*").not("#win-screen").remove();
    }, 1000);
}

function trackListDisplay(track) {
    return `${track.name} - ${track.artists.join(", ")}`;
}

// AUTOCOMPLETE
function manageAutocomplete(e) {
    if (e.keyCode == keyUp || e.keyCode == keyDown || e.keyCode == keyEnter)
        return;

    setAutocompleteVisibility(e.target.value != "");

    let filter = e.target.value.toUpperCase();
    let trackList = $("#track-list");
    let options = trackList.find("li");

    optionCount = 0;
    autocompleteSelected = -1;

    for (i = 0; i < options.length; i++) {
        txtValue = options[i].textContent || options[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            $(options[i]).css("display", "");
            optionCount++;
        } else {
            $(options[i]).css("display", "none");
        }
        $(options[i]).removeClass("selected");
    }
}
function setAutocompleteVisibility(enabled) {
    $("#track-list").css("display", enabled ? "" : "none");
}
function selectAutocomplete(value) {
    $("#guess-input").val(value);
    setAutocompleteVisibility(false);
}
function autocompleteKeyboard(e) {
    if (
        (e.keyCode != keyUp && e.keyCode != keyDown && e.keyCode != keyEnter) ||
        optionCount == 0
    )
        return;
    e.preventDefault();

    let autocompleteList = $("#track-list");
    let options = autocompleteList.find("li");
    let enabled = options
        .toArray()
        .filter((elem) => elem.style.display != "none");
    let optionHeight = options.first().height() * 2; // TODO: find out why this is 2x

    if (e.keyCode == keyUp || e.keyCode == keyDown) {
        if (autocompleteList.css("display") == "none") return;

        if (e.keyCode == keyUp) {
            if (autocompleteSelected == -1) autocompleteSelected++;
            autocompleteSelected = (autocompleteSelected - 1).mod(optionCount);
        } else if (e.keyCode == keyDown) {
            autocompleteSelected = (autocompleteSelected + 1).mod(optionCount);
        }

        autocompleteList.scrollTop(autocompleteSelected * optionHeight);

        // highlight selected
        for (i = 0; i < enabled.length; i++) {
            if (i == autocompleteSelected) $(enabled[i]).addClass("selected");
            else $(enabled[i]).removeClass("selected");
        }
    } else if (e.keyCode == keyEnter) {
        // submit
        if (autocompleteList.css("display") == "none") checkButton();
        // choose
        else if (autocompleteSelected != -1)
            selectAutocomplete(enabled[autocompleteSelected].innerHTML);
    }
}

// BUTTONS
function skipButton() {
    roundsLeft--;
}
function checkButton() {
    input = $("#guess-input");
    if (input.val() == trackListDisplay(currentTrack)) {
        score++;
        roundsLeft--;
        $("#score-text").html(`${score} / ${rounds}`);
        if (roundsLeft <= 0) {
            finishScreen();
        } else chooseLyrics();
    } else {
        console.log("wrong");
    }
    roundsLeft--;
}
/**
 * Will load all lyrics in order from the availableTrackIDs array into the loadedTracks map
 * First time loads of playlists with large amounts of lyric-less songs could be slow
 * @param {number} numToLoad - The amount of tracks to request lyrics for at once
 * @param {Array} tracksToLoad - A list of trackIDs to get lyrics for
 * @param {boolean} startGame - Whether the game will start when finding suitable lyrics
 * */
function loadLyrics(numToLoad, tracksToLoad, startGame) {
    numToLoad = Math.min(numToLoad, tracksToLoad.length);
    toLoad = tracksToLoad.splice(tracksToLoad.length - numToLoad, numToLoad);

    $.getJSON("/gettracklyrics?track_ids=" + toLoad).done(function (response) {
        for (const track_id in response.track_lyrics) {
            loadedTracks[track_id].lyrics = response.track_lyrics[track_id];
            if (response.track_lyrics[track_id].length > 0)
                loadedLyrics.push(track_id);
        }

        // will only be called on the first load
        if (loadedLyrics.length > 0 && startGame) {
            chooseLyrics();
            loader = $("#loader-container");
            if (loader) loader.remove();
            startGame = false;
        }
        if (tracksToLoad.length != 0) {
            loadLyrics(numToLoad, tracksToLoad, startGame);
        } else {
            console.log("finished loading lyrics");
        }
    });
}

function chooseLyrics(trackID) {
    // choose random song
    if (!trackID) trackID = loadedLyrics.pop();

    if (loadedLyrics.length == 0) {
        console.log("out of songs");
    }

    currentTrack = loadedTracks[trackID];
    displayLyrics(loadedTracks[trackID].lyrics, trackID);
}

function displayLyrics(lyrics, trackID) {
    // clear box from any previous attempts
    $("#lyric-box").empty();

    let startLine = randBetween(0, lyrics.length - 3);
    setTimeout(function () {
        displayLyricLine(lyrics, trackID, startLine, startLine);
    }, 500);
}

function displayLyricLine(lyrics, trackID, startLine, curLine) {
    // stop if the player has already guessed the song correctly
    if (trackID != currentTrack.id) return;

    let lyricBox = $("#lyric-box");
    lyricBox.append(`<div class="lyric-line">${lyrics[curLine]}</div>`);
    curLine++;
    // call next if less than 3 lyrics have been displayed
    if (curLine - startLine < 3)
        setTimeout(function () {
            displayLyricLine(lyrics, trackID, startLine, curLine);
        }, 3000);
}
