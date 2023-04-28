$(window).on("load", function () {
    let borderElements = $(".gradient-border");
    console.log({borderElements})
    if (borderElements) {
        setInterval(() => {
            borderElements.each(function (index) {
                borderElements[index].style.setProperty(
                    "--grad",
                    ((parseInt(borderElements[index].style.getPropertyValue("--grad")) || 0) + 2) % 360
                );
            });
        }, 20);
    }
});
