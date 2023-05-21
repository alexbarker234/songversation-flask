/**
 * 
 * @param {*} html - the HTML string to turn into a jQuery object
 * @returns 
 */
function wrapComponent(html){
    return $($.parseHTML(html))
}

function loaderComponent() {
    return wrapComponent(`
    <div id="loader-graphic">
        <div class="loader-bouncer"></div>
        <div class="loader-bouncer"></div>
        <div class="loader-bouncer"></div>
    </div>
    `)
}

function coverArtBoxComponent(coverArtData, index, link) {
    return wrapComponent(`
    <div class='cover-art-box'>
        ${link ? `<a class='cover-art-link' href=${link}>` : ""}
            <img src=${coverArtData.image} draggable=false>
        ${link ? `</a>` : ""}
        ${coverArtData.name}
    </div>
    `)
}

function errorMessageComponent(message) {
    return wrapComponent(`
    <h1>${message}</h1>
    <a href="/">Back to Home</a>
    `)
}

function userResultComponent(user) {
    return wrapComponent(`
    <div class="user-result">
        <div class="user-result-details">
            <img class="profile-pic" src="${user.image}}">
            <div class="username">${user.username}</div>
        </div>
        <div class="add-friend-container">
            ${user.is_self ? '' : user.is_friend ? `<div>Added</div>` : `<button class="button green add-friend">Add Friend</button>`}
        </div>
    </div>
    `)
}