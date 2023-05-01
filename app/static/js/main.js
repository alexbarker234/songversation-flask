function createCoverArtBox(coverArtData, index, link) {
    // JSX would be nice

    let box = $($.parseHTML(`
    <div class='cover-art-box'>
        ${link ? `<a class='cover-art-link' href=${link}>` : ""}
            <img src=${coverArtData.image} draggable=false>
        ${link ? `</a>` : ""}
        ${coverArtData.name}
    </div>
    `));
    console.log(box)
    return box

    const coverArtBox = $("<div>", { class: "cover-art-box" });
    coverArtBox.attr("data-id", coverArtData.id);
    if (index) coverArtBox.attr("data-index", index);

    const coverArtLink = $("<a>", href);

    const coverArtImage = $("<img>", {
        src: coverArtData.image,
        draggable: false,
    });

    coverArtBox.append(coverArtImage);
    coverArtBox.append(coverArtData.name);

    return coverArtBox;
}

function createLoader() {
    return $($.parseHTML(`
    <div id="loader-graphic">
        <div class="loader-bouncer"></div>
        <div class="loader-bouncer"></div>
        <div class="loader-bouncer"></div>
    </div>
    `));
}
