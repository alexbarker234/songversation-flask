let playlistCache = {};
let availableTrackIDs = [];

let loadedTracks = new Map();
/** List of all trackIDs with lyrics */
let loadedLyrics = [];

/** @type Track */
let currentTrack = null;

let score = 0;

let playlistID;

const keyUp = 38,
    keyDown = 40,
    keyEnter = 13;

/* 
    TODO: 
    - ensure only songs with lyrics can get selected
    - ensure playlists have songs on spotify 
    - remove local tracks
    - remove punctuation from autocomplete search
    - keyboard support - arrowkey autocomplete, enter to submit
    - some lyric links return 404 - make sure thats fixed
    - make the autocomplete include artist names 
*/

$(window).on("load", function () {
    if (window.location.pathname.includes("/playlist/")) {
        playlistID = window.location.pathname.split("/").pop(); // get the last part in the path

        getPlaylist(playlistID).then((response) => {
            if (response.error === true) {
                displayError(response.message);
            } else {
                loadGameWithPlaylist(response);
            }
        });
    }
});

function displayError(message) {
    let game = $("#lyric-game");
    game.empty();
    game.append(errorMessageComponent(message));
    $("#loader-container").remove();
}

function getPlaylist(playlistID) {
    return $.getJSON(`/api/get-playlist/${playlistID}`);
}

function getPlaylistTracks(playlistID) {
    return $.getJSON(`/api/get-playlist-tracks/${playlistID}`);
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
    selectedPlaylist = coverArtBoxComponent(playlist);
    selectedPlaylist.css("animation", "fade-in 1s");
    selectedPlaylist.addClass("selected-playlist");
    $("#selected-cover-art").append(selectedPlaylist);

    // register autocomplete options
    const trackList = $("#track-list");
    playlist.tracks.forEach(function (track) {
        trackList.append($("<li>", { html: `${trackListDisplay(track)}` }));
    });

    $("#score-text").html(`0`);

    loadLyrics(5, [...availableTrackIDs], true);
}

function finishScreen() {
    /*
        TODO:
        - replay with same playlist
        - back to playlists
    */
    commitStats(score, currentTrack['id']);
    $("#streak-score").html(`Final Streak: ${score}`);
    $("#win-modal").modal("show");
}

function commitStats(score, songFailedOn) {
    $.post("/api/add-game", { score: score, last_song: songFailedOn, game_type: 'playlist', game_object_id: playlistID })
        .done(function () {
            console.log("Stats saved successfully.");
        })
        .fail(function () {
            console.log("Error saving stats.");
        });
}

function trackListDisplay(track) {
    return `${track.name} - ${track.artists.join(", ")}`;
}

// BUTTONS
function skipButton() {
    finishScreen();
}

function checkButton() {
    input = $("#guess-input");
    if (input.val() == trackListDisplay(currentTrack)) {
        score++;
        $("#score-text").html(`${score}`);
        chooseLyrics();
    } else {
        finishScreen();
        console.log("wrong");
    }

    input.val("");
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
    $.getJSON("/api/get-track-lyrics?track_ids=" + toLoad).done(function (response) {
        for (const track_id in response.track_lyrics) {
            loadedTracks[track_id].lyrics = response.track_lyrics[track_id];
            if (response.track_lyrics[track_id].length > 0) loadedLyrics.push(track_id);
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
    initialiseLyricBox(loadedTracks[trackID].lyrics, 3, startLine);
    setTimeout(function () {
        displayLyricLine(trackID, startLine, startLine);
    }, 500);
}

function initialiseLyricBox(lyrics, numLines, startLine) {
    let lyricBox = $("#lyric-box");
    // for adjustment if we add difficulties
    for (let i = 0; i < numLines; i++) {
        lyricBox.append(
            `<div class="lyric-line" style="opacity:0">
                <p>${lyrics[startLine + i]}<p>
            </div>`
        );
    }
}

function displayLyricLine(trackID, startLine, curLine) {
    // stop if the player has already guessed the song correctly
    if (trackID != currentTrack.id) return;

    const lyricNum = curLine - startLine;

    const lyricBox = $("#lyric-box");
    const lyricLines = lyricBox.children(".lyric-line");
    const lyricLine = lyricLines.eq(lyricNum);
    lyricLine.css({
        animation: "fade-in 1s forwards",
    });
    curLine++;
    // call next if less than 3 lyrics have been displayed
    if (lyricNum < lyricLines.length)
        setTimeout(function () {
            displayLyricLine(trackID, startLine, curLine);
        }, 3000);
}

function playAgain() {
    score = 0;
    $("#score-text").html(`${score}`);
    chooseLyrics();
}
